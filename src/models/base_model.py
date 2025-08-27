import pandas as pd
import numpy as np
import xgboost as xgb
from sklearn.model_selection import train_test_split
import yaml
import pickle
import os
from pathlib import Path
import matplotlib.pyplot as plt
import seaborn as sns

# Thử import shap, nếu không thành công thì bỏ qua
try:
    import shap
    SHAP_AVAILABLE = True
except ImportError:
    print("Thư viện SHAP không khả dụng. Một số tính năng giải thích mô hình sẽ bị vô hiệu hóa.")
    SHAP_AVAILABLE = False

from ..features.woe_iv import WoeIvTransformer
from ..utils.metrics import calculate_metrics, plot_roc_curve, plot_ks_curve

class BaseXGBoostModel:
    """
    Lớp cơ sở cho các mô hình XGBoost chấm điểm tín dụng
    """
    def __init__(self, model_type, config_path=None):
        """
        Khởi tạo mô hình
        
        Parameters:
        -----------
        model_type : str
            Loại mô hình ('application_scorecard', 'behavior_scorecard', etc.)
        config_path : str, optional
            Đường dẫn đến file cấu hình
        """
        self.model_type = model_type
        
        if config_path is None:
            config_path = Path(__file__).parents[2] / 'config.yaml'
        
        # Đảm bảo thư mục models tồn tại
        models_dir = Path(__file__).parents[2] / 'models'
        os.makedirs(models_dir, exist_ok=True)
        
        # Đảm bảo thư mục results tồn tại
        results_dir = Path(__file__).parents[2] / 'results' / model_type
        os.makedirs(results_dir, exist_ok=True)
        
        # Đọc cấu hình, tạo file nếu không tồn tại
        if not os.path.exists(config_path):
            # Tạo cấu hình mặc định
            default_config = {
                'data': {
                    'raw_data_path': 'data/raw/',
                    'processed_data_path': 'data/processed/',
                    'train_test_split': 0.7,
                    'random_state': 42,
                    'max_samples': 10000,  # Giới hạn số lượng mẫu để giảm kích thước file
                    'compression': 'gzip',  # Nén dữ liệu khi lưu
                    'float_precision': 2    # Giảm độ chính xác số thập phân
                },
                'feature_engineering': {
                    'max_bins': 10,
                    'min_bin_size': 0.05,
                    'max_features': 50,     # Giới hạn số đặc trưng tối đa
                    'categorical_encoding': 'label',  # Thay vì one-hot để giảm kích thước
                    'drop_low_importance': True       # Loại bỏ đặc trưng ít quan trọng
                },
                'models': {
                    'application_scorecard': {
                        'target': 'default_flag',
                        'perf_window_months': 12,
                        'xgb_params': {
                            'max_depth': 3,
                            'learning_rate': 0.1,
                            'n_estimators': 100,
                            'objective': 'binary:logistic',
                            'eval_metric': 'auc'
                        }
                    },
                    'behavior_scorecard': {
                        'target': 'default_flag',
                        'perf_window_months': 6,
                        'xgb_params': {
                            'max_depth': 4,
                            'learning_rate': 0.05,
                            'n_estimators': 200,
                            'objective': 'binary:logistic',
                            'eval_metric': 'auc'
                        }
                    },
                    'collections_scoring': {
                        'target': 'further_delinquency',
                        'perf_window_months': 1,
                        'xgb_params': {
                            'max_depth': 5,
                            'learning_rate': 0.1,
                            'n_estimators': 150,
                            'objective': 'binary:logistic',
                            'eval_metric': 'auc'
                        }
                    },
                    'desertion_scoring': {
                        'target': 'desertion_flag',
                        'perf_window_months': 3,
                        'xgb_params': {
                            'max_depth': 3,
                            'learning_rate': 0.1,
                            'n_estimators': 100,
                            'objective': 'binary:logistic',
                            'eval_metric': 'auc'
                        }
                    }
                },
                'scorecard': {
                    'pdo': 20,
                    'base_score': 600,
                    'base_odds': 50,
                    'scaling_method': 'standard'
                }
            }
            
            os.makedirs(os.path.dirname(config_path), exist_ok=True)
            with open(config_path, 'w') as f:
                yaml.dump(default_config, f)
            
            self.config = default_config
        else:
            with open(config_path, 'r') as file:
                self.config = yaml.safe_load(file)
        
        self.model_config = self.config['models'][model_type]
        self.target = self.model_config['target']
        self.xgb_params = self.model_config['xgb_params']
        
        self.model = None
        self.woe_transformer = None
        self.feature_importances = None
    
    def prepare_data(self, data):
        """
        Chuẩn bị dữ liệu cho mô hình
        
        Parameters:
        -----------
        data : DataFrame
            Dữ liệu gốc
            
        Returns:
        --------
        X_train, X_test, y_train, y_test
        """
        # Tách đặc trưng và mục tiêu
        y = data[self.target]
        X = data.drop(self.target, axis=1)
        
        # Chia tập train/test
        train_test_split_ratio = self.config['data']['train_test_split']
        random_state = self.config['data']['random_state']
        
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, 
            train_size=train_test_split_ratio, 
            random_state=random_state,
            stratify=y
        )
        
        return X_train, X_test, y_train, y_test
    
    def transform_features(self, X_train, X_test, y_train):
        """
        Chuyển đổi đặc trưng sang WOE
        
        Parameters:
        -----------
        X_train, X_test, y_train : DataFrames
            Dữ liệu đã được chia
            
        Returns:
        --------
        X_train_woe, X_test_woe : DataFrames
            Dữ liệu đã chuyển đổi sang WOE
        """
        self.woe_transformer = WoeIvTransformer()
        X_train_woe = self.woe_transformer.fit_transform(X_train, y_train)
        X_test_woe = self.woe_transformer.transform(X_test)
        
        return X_train_woe, X_test_woe
    
    def train(self, X_train_woe, y_train, X_test_woe=None, y_test=None):
        """
        Huấn luyện mô hình XGBoost
        
        Parameters:
        -----------
        X_train_woe, y_train : DataFrame, Series
            Dữ liệu huấn luyện
        X_test_woe, y_test : DataFrame, Series, optional
            Dữ liệu kiểm tra
        
        Returns:
        --------
        self
        """
        dtrain = xgb.DMatrix(X_train_woe, label=y_train)
        
        eval_list = [(dtrain, 'train')]
        if X_test_woe is not None and y_test is not None:
            dtest = xgb.DMatrix(X_test_woe, label=y_test)
            eval_list.append((dtest, 'test'))
        
        self.model = xgb.train(
            self.xgb_params,
            dtrain,
            num_boost_round=self.xgb_params.get('n_estimators', 100),
            evals=eval_list,
            verbose_eval=True
        )
        
        # Tính feature importance
        self.feature_importances = {
            'weight': self.model.get_score(importance_type='weight'),
            'gain': self.model.get_score(importance_type='gain'),
            'cover': self.model.get_score(importance_type='cover')
        }
        
        return self
    
    def predict(self, X):
        """
        Dự đoán xác suất mặc định
        
        Parameters:
        -----------
        X : DataFrame
            Dữ liệu đặc trưng
            
        Returns:
        --------
        ndarray
            Xác suất mặc định
        """
        if self.model is None:
            raise ValueError("Model hasn't been trained yet!")
        
        # Tạo bản sao để tránh thay đổi dữ liệu gốc
        X_copy = X.copy()
        
        # Loại bỏ cột customer_id nếu có
        if 'customer_id' in X_copy.columns:
            X_copy = X_copy.drop(columns=['customer_id'])
        
        # Chuyển đổi kiểu dữ liệu cho tất cả các cột
        for col in X_copy.columns:
            if X_copy[col].dtype == 'object':
                try:
                    X_copy[col] = pd.to_numeric(X_copy[col])
                except:
                    X_copy[col] = X_copy[col].astype('category')
        
        X_woe = self.woe_transformer.transform(X_copy)
        dmatrix = xgb.DMatrix(X_woe)
        return self.model.predict(dmatrix)
    
    def evaluate(self, X_test, y_test):
        """
        Đánh giá mô hình
        
        Parameters:
        -----------
        X_test, y_test : DataFrame, Series
            Dữ liệu kiểm tra
            
        Returns:
        --------
        dict
            Dictionary chứa các chỉ số hiệu suất
        """
        y_pred_proba = self.predict(X_test)
        metrics = calculate_metrics(y_test, y_pred_proba)
        
        # Vẽ các đường cong
        plt.figure(figsize=(15, 10))
        
        plt.subplot(2, 2, 1)
        plot_roc_curve(y_test, y_pred_proba)
        
        plt.subplot(2, 2, 2)
        plot_ks_curve(y_test, y_pred_proba)
        
        plt.subplot(2, 2, 3)
        # Top feature importance
        importances = pd.DataFrame({'feature': list(self.feature_importances['gain'].keys()),
                                   'importance': list(self.feature_importances['gain'].values())})
        importances.sort_values('importance', ascending=False, inplace=True)
        sns.barplot(x='importance', y='feature', data=importances.head(10))
        plt.title('Feature Importance (Gain)')
        
        # Chỉ vẽ SHAP values nếu thư viện SHAP khả dụng
        if SHAP_AVAILABLE:
            plt.subplot(2, 2, 4)
            # SHAP values for top features
            X_woe = self.woe_transformer.transform(X_test)
            explainer = shap.TreeExplainer(self.model)
            shap_values = explainer.shap_values(X_woe)
            shap.summary_plot(shap_values, X_woe, plot_type='bar', show=False)
        else:
            plt.subplot(2, 2, 4)
            plt.text(0.5, 0.5, "SHAP không khả dụng\nCài đặt thư viện SHAP để xem phân tích giải thích mô hình", 
                     horizontalalignment='center', verticalalignment='center', fontsize=12)
            plt.axis('off')
        
        plt.tight_layout()
        
        # Lưu biểu đồ
        output_dir = Path(__file__).parents[2] / f'results/{self.model_type}'
        output_dir.mkdir(parents=True, exist_ok=True)
        plt.savefig(output_dir / 'model_evaluation.png')
        plt.close()
        
        return metrics
    
    def save_model(self, directory=None):
        """
        Lưu mô hình
        
        Parameters:
        -----------
        directory : str, optional
            Thư mục lưu mô hình
        """
        if directory is None:
            directory = Path(__file__).parents[2] / 'models'
        
        os.makedirs(directory, exist_ok=True)
        
        # Lưu mô hình XGBoost
        model_path = os.path.join(directory, f'{self.model_type}_xgb_model.json')
        self.model.save_model(model_path)
        
        # Lưu WOE transformer
        woe_path = os.path.join(directory, f'{self.model_type}_woe_transformer.pkl')
        self.woe_transformer.save(woe_path)
        
        # Lưu feature importance
        importance_path = os.path.join(directory, f'{self.model_type}_feature_importance.pkl')
        with open(importance_path, 'wb') as f:
            pickle.dump(self.feature_importances, f)
            
        print(f"Model và các thành phần đã được lưu tại {directory}")
    
    def load_model(self, directory=None):
        """
        Tải mô hình
        
        Parameters:
        -----------
        directory : str, optional
            Thư mục chứa mô hình
        """
        if directory is None:
            directory = Path(__file__).parents[2] / 'models'
        
        # Tải mô hình XGBoost
        model_path = os.path.join(directory, f'{self.model_type}_xgb_model.json')
        self.model = xgb.Booster()
        self.model.load_model(model_path)
        
        # Tải WOE transformer
        woe_path = os.path.join(directory, f'{self.model_type}_woe_transformer.pkl')
        with open(woe_path, 'rb') as f:
            self.woe_transformer = pickle.load(f)
        
        # Tải feature importance
        importance_path = os.path.join(directory, f'{self.model_type}_feature_importance.pkl')
        with open(importance_path, 'rb') as f:
            self.feature_importances = pickle.load(f)
            
        print(f"Model và các thành phần đã được tải từ {directory}")
        
        return self

    def evaluate_model_without_shap(self, X_test, y_test, output_dir=None):
        """
        Đánh giá mô hình và tạo các biểu đồ phân tích không sử dụng SHAP
        
        Parameters:
        -----------
        X_test : DataFrame
            Dữ liệu test (features)
        y_test : Series
            Nhãn thực tế
        output_dir : Path, optional
            Thư mục xuất báo cáo đánh giá
            
        Returns:
        --------
        dict
            Các metrics đánh giá
        """
        import matplotlib.pyplot as plt
        import seaborn as sns
        import numpy as np
        from sklearn.metrics import roc_curve, precision_recall_curve, average_precision_score
        from sklearn.metrics import roc_auc_score, confusion_matrix, classification_report
        from sklearn.inspection import permutation_importance
        
        print("Đánh giá mô hình...")
        
        # Tạo thư mục output nếu cần
        if output_dir is not None:
            os.makedirs(output_dir, exist_ok=True)
        
        # Dự đoán
        if self.model is None:
            raise ValueError("Model hasn't been trained yet!")
            
        dtrain = xgb.DMatrix(X_test)
        y_pred_proba = self.model.predict(dtrain)
        y_pred = (y_pred_proba > 0.5).astype(int)
        
        # Tính các metrics
        auc_score = roc_auc_score(y_test, y_pred_proba)
        gini = 2 * auc_score - 1
        
        fpr, tpr, thresholds = roc_curve(y_test, y_pred_proba)
        ks_stat = max(tpr - fpr)
        
        avg_precision = average_precision_score(y_test, y_pred_proba)
        
        # Tạo figure với nhiều subplots
        fig = plt.figure(figsize=(15, 15))
        
        # Cấu hình các subplots
        gs = fig.add_gridspec(3, 2)
        
        # 1. ROC curve
        ax_roc = fig.add_subplot(gs[0, 0])
        ax_roc.plot(fpr, tpr, label=f'AUC = {auc_score:.4f}, Gini = {gini:.4f}')
        ax_roc.plot([0, 1], [0, 1], 'k--', alpha=0.6)
        ax_roc.set_xlabel('False Positive Rate')
        ax_roc.set_ylabel('True Positive Rate')
        ax_roc.set_title('ROC Curve')
        ax_roc.legend()
        ax_roc.grid(alpha=0.3)
        
        # 2. Precision-Recall curve
        ax_pr = fig.add_subplot(gs[0, 1])
        precision, recall, _ = precision_recall_curve(y_test, y_pred_proba)
        ax_pr.plot(recall, precision, label=f'AP = {avg_precision:.4f}')
        ax_pr.set_xlabel('Recall')
        ax_pr.set_ylabel('Precision')
        ax_pr.set_title('Precision-Recall Curve')
        ax_pr.legend()
        ax_pr.grid(alpha=0.3)
        
        # 3. Feature Importance (xgboost built-in)
        ax_fi = fig.add_subplot(gs[1, 0])
        
        # Get feature importance from model
        importance_dict = self.model.get_score(importance_type='gain')
        importance_df = pd.DataFrame({
            'Feature': list(importance_dict.keys()),
            'Importance': list(importance_dict.values())
        })
        importance_df = importance_df.sort_values('Importance', ascending=False).head(10)
        
        # Bar plot for feature importance
        sns.barplot(x='Importance', y='Feature', data=importance_df, ax=ax_fi)
        ax_fi.set_title('Feature Importance (Gain)')
        ax_fi.grid(alpha=0.3)
        
        # 4. Confusion Matrix
        ax_cm = fig.add_subplot(gs[1, 1])
        cm = confusion_matrix(y_test, y_pred)
        sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', ax=ax_cm)
        ax_cm.set_xlabel('Predicted')
        ax_cm.set_ylabel('Actual')
        ax_cm.set_title('Confusion Matrix')
        
        # 5. Permutation Importance
        ax_pi = fig.add_subplot(gs[2, 0])
        
        try:
            # Create pipeline if using sklearn
            from sklearn.pipeline import Pipeline
            from sklearn.preprocessing import StandardScaler
            from sklearn.ensemble import GradientBoostingClassifier
            
            # Create a simplified model for permutation importance
            # This is a workaround since we can't directly use sklearn's permutation_importance with XGBoost Booster
            X_train_sample = X_test.copy()  # Use test data as a sample
            y_train_sample = y_test.copy()
            
            # Create a simplified GBM model
            simple_model = GradientBoostingClassifier(n_estimators=50, random_state=42)
            simple_model.fit(X_train_sample, y_train_sample)
            
            # Calculate permutation importance
            perm_importance = permutation_importance(
                simple_model, X_test, y_test, n_repeats=10, random_state=42
            )
            
            # Create DataFrame for plotting
            perm_imp_df = pd.DataFrame({
                'Feature': X_test.columns,
                'Importance': perm_importance.importances_mean
            }).sort_values('Importance', ascending=False).head(10)
            
            # Bar plot for permutation importance
            sns.barplot(x='Importance', y='Feature', data=perm_imp_df, ax=ax_pi)
            ax_pi.set_title('Permutation Feature Importance (Approximate)')
            ax_pi.grid(alpha=0.3)
        except Exception as e:
            print(f"Warning: Could not calculate permutation importance: {e}")
            ax_pi.text(0.5, 0.5, "Permutation importance calculation failed", 
                       ha='center', va='center', transform=ax_pi.transAxes)
        
        # 6. Score Distribution
        ax_dist = fig.add_subplot(gs[2, 1])
        
        # Create distribution of probability scores by true class
        sns.histplot(
            x=y_pred_proba, 
            hue=y_test,
            bins=30,
            alpha=0.6,
            ax=ax_dist
        )
        ax_dist.set_xlabel('Predicted Probability')
        ax_dist.set_ylabel('Count')
        ax_dist.set_title('Distribution of Predicted Probabilities')
        ax_dist.legend(['Negative', 'Positive'])
        ax_dist.grid(alpha=0.3)
        
        # Adjust layout
        plt.tight_layout()
        
        # Save the figure if output_dir provided
        if output_dir is not None:
            fig_path = os.path.join(output_dir, 'model_evaluation.png')
            plt.savefig(fig_path)
            plt.close()
            
            # Save classification report to text file
            report_path = os.path.join(output_dir, 'classification_report.txt')
            with open(report_path, 'w') as f:
                f.write("Classification Report\n")
                f.write("---------------------\n")
                f.write(classification_report(y_test, y_pred))
                f.write("\n\nAdditional Metrics\n")
                f.write("------------------\n")
                f.write(f"AUC-ROC: {auc_score:.4f}\n")
                f.write(f"Gini: {gini:.4f}\n")
                f.write(f"KS Statistic: {ks_stat:.4f}\n")
                f.write(f"Average Precision: {avg_precision:.4f}\n")
        else:
            plt.show()
        
        # Create detailed feature effect plots if output_dir is provided
        if output_dir is not None:
            self._create_feature_effect_plots(X_test, y_pred_proba, output_dir)
        
        # Return metrics
        metrics = {
            'auc': auc_score,
            'gini': gini,
            'ks_statistic': ks_stat,
            'average_precision': avg_precision
        }
        
        return metrics

    def _create_feature_effect_plots(self, X, y_pred_proba, output_dir):
        """
        Tạo biểu đồ hiển thị ảnh hưởng của từng đặc trưng quan trọng lên dự đoán
        
        Parameters:
        -----------
        X : DataFrame
            Dữ liệu features
        y_pred_proba : array
            Dự đoán xác suất
        output_dir : str
            Thư mục xuất báo cáo
        """
        import matplotlib.pyplot as plt
        import numpy as np
        
        # Get top 6 features by importance
        importance_dict = self.model.get_score(importance_type='gain')
        top_features = sorted(importance_dict.items(), key=lambda x: x[1], reverse=True)[:6]
        top_feature_names = [f[0] for f in top_features]
        
        # Create a directory for feature effects
        feature_dir = os.path.join(output_dir, 'feature_effects')
        os.makedirs(feature_dir, exist_ok=True)
        
        # Create plots for each top feature
        for feature in top_feature_names:
            if feature not in X.columns:
                continue
                
            plt.figure(figsize=(10, 6))
            
            # Sort the data by feature value
            sorted_idx = X[feature].argsort()
            X_sorted = X.iloc[sorted_idx]
            y_pred_sorted = y_pred_proba[sorted_idx]
            
            # Plot feature vs prediction
            plt.subplot(2, 1, 1)
            plt.scatter(X_sorted[feature], y_pred_sorted, alpha=0.5, s=5)
            plt.title(f'Effect of {feature} on Predictions')
            plt.xlabel(feature)
            plt.ylabel('Predicted Probability')
            
            # Add a trend line using moving average
            window_size = min(100, len(X_sorted) // 10)
            if window_size > 0:
                moving_avg = np.convolve(y_pred_sorted, np.ones(window_size)/window_size, mode='valid')
                x_vals = X_sorted[feature].values[window_size-1:]
                if len(x_vals) == len(moving_avg):
                    plt.plot(x_vals, moving_avg, 'r-', lw=2, alpha=0.8)
            
            plt.grid(alpha=0.3)
            
            # Add a histogram to show distribution
            plt.subplot(2, 1, 2)
            plt.hist(X[feature], bins=30, alpha=0.7)
            plt.xlabel(feature)
            plt.ylabel('Count')
            plt.title(f'Distribution of {feature}')
            plt.grid(alpha=0.3)
            
            plt.tight_layout()
            plt.savefig(os.path.join(feature_dir, f'{feature}_effect.png'))
            plt.close()
        
        # Create a summary plot for all top features
        plt.figure(figsize=(12, 10))
        
        for i, feature in enumerate(top_feature_names):
            if feature not in X.columns or i >= 6:  # Limit to 6 features
                continue
                
            plt.subplot(3, 2, i+1)
            
            # Sort the data by feature value
            sorted_idx = X[feature].argsort()
            X_sorted = X.iloc[sorted_idx]
            y_pred_sorted = y_pred_proba[sorted_idx]
            
            # Plot feature vs prediction
            plt.scatter(X_sorted[feature], y_pred_sorted, alpha=0.3, s=3)
            
            # Add a trend line using moving average
            window_size = min(100, len(X_sorted) // 10)
            if window_size > 0:
                moving_avg = np.convolve(y_pred_sorted, np.ones(window_size)/window_size, mode='valid')
                x_vals = X_sorted[feature].values[window_size-1:]
                if len(x_vals) == len(moving_avg):
                    plt.plot(x_vals, moving_avg, 'r-', lw=2, alpha=0.8)
            
            plt.title(feature)
            plt.xlabel('Feature Value')
            plt.ylabel('Prediction')
            plt.grid(alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(os.path.join(output_dir, 'top_features_effect_summary.png'))
        plt.close()

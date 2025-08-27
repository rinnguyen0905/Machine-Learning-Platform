import pandas as pd
import numpy as np
import pickle
import os
import yaml
from pathlib import Path
import matplotlib.pyplot as plt
import seaborn as sns
import json

class ScorecardBuilder:
    """
    Xây dựng và áp dụng bảng điểm tín dụng
    """
    def __init__(self, model_type, config_path=None):
        """
        Khởi tạo builder
        
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
        
        with open(config_path, 'r') as file:
            self.config = yaml.safe_load(file)
        
        # Cấu hình scorecard
        self.scorecard_config = self.config['scorecard']
        self.pdo = self.scorecard_config['pdo']  # Points to Double the Odds
        self.base_score = self.scorecard_config['base_score']  # Điểm cơ sở
        self.base_odds = self.scorecard_config['base_odds']  # Tỷ lệ cơ sở (tốt:xấu)
        
        # Tính hệ số
        self.factor = self.pdo / np.log(2)
        self.offset = self.base_score - self.factor * np.log(self.base_odds)
        
        # Tải mô hình và transformer
        self.load_model_components()
        
        # Thiết lập scorecard
        self.scorecard = None
    
    def load_model_components(self):
        """
        Tải mô hình XGBoost và WOE transformer
        """
        model_dir = Path(__file__).parents[2] / 'models'
        
        # Tải WOE transformer
        woe_path = os.path.join(model_dir, f'{self.model_type}_woe_transformer.pkl')
        with open(woe_path, 'rb') as f:
            self.woe_transformer = pickle.load(f)
        
        # Tải feature importance
        importance_path = os.path.join(model_dir, f'{self.model_type}_feature_importance.pkl')
        with open(importance_path, 'rb') as f:
            self.feature_importances = pickle.load(f)
    
    def build_scorecard_from_model(self, model, feature_bins=None):
        """
        Xây dựng scorecard từ mô hình
        
        Parameters:
        -----------
        model : xgboost.Booster
            Mô hình XGBoost đã được huấn luyện
        feature_bins : dict, optional
            Bảng ánh xạ các đặc trưng sang bin
            
        Returns:
        --------
        dict
            Scorecard dưới dạng dictionary
        """
        try:
            # Lấy thông tin cây từ mô hình
            model_dump = model.get_dump(dump_format='json')
            
            # In thông tin debug
            print(f"Number of trees in model: {len(model_dump)}")
            if len(model_dump) > 0:
                print(f"Sample of first tree: {model_dump[0][:200]}...")
            
            # Kiểm tra xem có thông tin cây nào không
            if not model_dump:
                print("Warning: Model has no trees, scorecard will be empty")
                self.scorecard = {}
                return self.scorecard
            
            # Parse JSON
            trees = []
            for i, tree in enumerate(model_dump):
                try:
                    parsed_tree = json.loads(tree)
                    trees.append(parsed_tree)
                    print(f"Successfully parsed tree {i+1}/{len(model_dump)}")
                except json.JSONDecodeError as e:
                    print(f"Warning: Could not parse tree JSON for tree {i+1}: {e}")
            
            # Tạo trực tiếp một scorecard đơn giản từ model feature importance
            # Đây là giải pháp thay thế khi không thể phân tích cây quyết định
            feature_importance = model.get_score(importance_type='gain')
            print(f"Features found in model: {list(feature_importance.keys())}")
            
            # Initialize scorecard
            self.scorecard = {}
            
            # Xử lý từng cây quyết định
            for tree_idx, tree in enumerate(trees):
                self._process_tree_node(tree, tree_idx, feature_bins)
            
            # Kiểm tra xem scorecard có dữ liệu hay không
            if len(self.scorecard) == 0:
                print("Warning: No features were extracted from the model, using feature importance directly")
                
                # Sử dụng feature importance trực tiếp thay vì cấu trúc cây
                for feature, importance in feature_importance.items():
                    # Chuẩn hóa tầm quan trọng của đặc trưng
                    normalized_importance = importance / sum(feature_importance.values())
                    
                    # Tạo điểm số đơn giản dựa trên tầm quan trọng
                    # Đặc trưng quan trọng hơn có điểm cao hơn
                    self.scorecard[feature] = {
                        "<= median": self.factor * normalized_importance * 0.5,  # Giá trị thấp -> điểm thấp hơn
                        "> median": self.factor * normalized_importance          # Giá trị cao -> điểm cao hơn
                    }
                
                print(f"Created simplified scorecard with {len(self.scorecard)} features based on feature importance")
            
            return self.scorecard
        except Exception as e:
            import traceback
            print(f"Error building scorecard from model: {e}")
            print(traceback.format_exc())
            # Return empty scorecard in case of error
            self.scorecard = {}
            return self.scorecard

    def _process_tree_node(self, node, tree_idx, feature_bins, parent_path=""):
        """
        Xử lý đệ quy từng node trong cây quyết định
        
        Parameters:
        -----------
        node : dict
            JSON node từ mô hình
        tree_idx : int
            Chỉ số của cây
        feature_bins : dict
            Bảng ánh xạ các đặc trưng sang bin
        parent_path : str
            Đường dẫn từ gốc đến node hiện tại
        """
        try:
            # Nếu là node lá
            if 'leaf' in node:
                leaf_value = node['leaf']
                path = parent_path.strip('/')
                
                # Nếu không có path (cây chỉ có một node)
                if not path:
                    return
                
                # Lấy các điều kiện từ path
                conditions = path.split('/')
                for condition in conditions:
                    feature_name, direction, threshold = self._parse_condition(condition)
                    
                    # Bỏ qua nếu không có tên đặc trưng
                    if not feature_name:
                        continue
                    
                    # Tạo bin nếu chưa có thông tin bin
                    if feature_bins is None:
                        bin_value = f"{direction} {threshold}"
                    else:
                        # Đây là vị trí cần được triển khai dựa trên dữ liệu thực tế
                        bin_value = f"{direction} {threshold}"  # Placeholder
                    
                    # Khởi tạo đặc trưng trong scorecard nếu chưa có
                    if feature_name not in self.scorecard:
                        self.scorecard[feature_name] = {}
                    
                    # Cộng dồn điểm cho bin
                    current_score = self.scorecard[feature_name].get(bin_value, 0)
                    # Nhân với factor để chuyển đổi log-odds thành điểm
                    new_score = current_score + self.factor * leaf_value
                    self.scorecard[feature_name][bin_value] = new_score
                    
                    # Debug info
                    if tree_idx < 3:  # Print only for the first few trees to avoid clutter
                        print(f"Tree {tree_idx}: Added score {new_score:.2f} for feature '{feature_name}' bin '{bin_value}'")
            
            # Nếu là node chia
            else:
                feature_name = node.get('split')
                threshold = node.get('split_condition')
                
                if feature_name is None or threshold is None:
                    print(f"Warning: Invalid node structure in tree {tree_idx}: {node}")
                    return
                
                # Xử lý node con trái (giá trị <= ngưỡng)
                left_path = f"{parent_path}/{feature_name}<={threshold}"
                if 'yes' in node and isinstance(node['yes'], dict):
                    self._process_tree_node(node['yes'], tree_idx, feature_bins, left_path)
                elif 'children' in node and len(node['children']) > 0:
                    # Alternative structure for some XGBoost models
                    left_child = node['children'][0]
                    self._process_tree_node(left_child, tree_idx, feature_bins, left_path)
                
                # Xử lý node con phải (giá trị > ngưỡng)
                right_path = f"{parent_path}/{feature_name}>{threshold}"
                if 'no' in node and isinstance(node['no'], dict):
                    self._process_tree_node(node['no'], tree_idx, feature_bins, right_path)
                elif 'children' in node and len(node['children']) > 1:
                    # Alternative structure for some XGBoost models
                    right_child = node['children'][1]
                    self._process_tree_node(right_child, tree_idx, feature_bins, right_path)
        except Exception as e:
            print(f"Error in _process_tree_node: {e} for node: {node}")

    def _parse_condition(self, condition):
        """
        Parse condition string to get feature name, direction and threshold
        
        Parameters:
        -----------
        condition : str
            Condition string (e.g. "feature<=threshold")
            
        Returns:
        --------
        tuple
            (feature_name, direction, threshold)
        """
        if '<=' in condition:
            feature_name, threshold = condition.split('<=')
            return feature_name, '<=', float(threshold)
        elif '>' in condition:
            feature_name, threshold = condition.split('>')
            return feature_name, '>', float(threshold)
        else:
            return None, None, None
    
    def calculate_score(self, customer_data):
        """
        Tính điểm tín dụng cho một khách hàng
        
        Parameters:
        -----------
        customer_data : DataFrame
            Dữ liệu của khách hàng
            
        Returns:
        --------
        int
            Điểm tín dụng
        """
        if self.scorecard is None:
            raise ValueError("Scorecard hasn't been built yet!")
        
        # Bắt đầu với điểm cơ sở
        total_score = self.offset
        
        # Kiểm tra xem scorecard có dữ liệu không
        if not self.scorecard:
            print("Warning: Empty scorecard, returning base score only")
            return round(total_score)
        
        # Nếu scorecard đã được chuyển thành bảng
        if hasattr(self, 'scorecard_table') and self.scorecard_table is not None and 'Feature' in self.scorecard_table.columns:
            for feature in self.scorecard_table['Feature'].unique():
                if feature in customer_data.columns:
                    # Lấy giá trị của biến
                    value = customer_data[feature].iloc[0]
                    
                    # Tìm bin phù hợp dựa trên giá trị và điều kiện trong scorecard
                    feature_points = 0
                    for _, row in self.scorecard_table[self.scorecard_table['Feature'] == feature].iterrows():
                        bin_desc = row['Bin']
                        score = row['Score']
                        
                        # Parse bin description (dạng "<=X" hoặc ">X")
                        if "<=" in bin_desc:
                            _, threshold = bin_desc.split("<=")
                            if value <= float(threshold):
                                feature_points = score
                                break
                        elif ">" in bin_desc:
                            _, threshold = bin_desc.split(">")
                            if value > float(threshold):
                                feature_points = score
                                break
                    
                    total_score += feature_points
        else:
            # Sử dụng cấu trúc scorecard dạng dictionary
            for feature, bins in self.scorecard.items():
                if feature in customer_data.columns:
                    # Lấy giá trị của biến
                    value = customer_data[feature].iloc[0]
                    
                    # Tìm bin phù hợp
                    feature_points = 0
                    for bin_desc, score in bins.items():
                        # Parse bin description (dạng "<=X" hoặc ">X")
                        if "<=" in bin_desc:
                            _, threshold = bin_desc.split("<=")
                            if value <= float(threshold):
                                feature_points = score
                                break
                        elif ">" in bin_desc:
                            _, threshold = bin_desc.split(">")
                            if value > float(threshold):
                                feature_points = score
                                break
                    
                    total_score += feature_points
        
        return round(total_score)
    
    def create_scorecard_table(self, output_path=None):
        """
        Tạo bảng scorecard dưới dạng DataFrame và xuất ra Excel
        
        Parameters:
        -----------
        output_path : Path, optional
            Đường dẫn file Excel xuất ra
        
        Returns:
        --------
        DataFrame
            Bảng scorecard
        """
        if self.scorecard is None:
            raise ValueError("Scorecard chưa được xây dựng")
        
        # Tạo DataFrame cho bảng scorecard
        rows = []
        
        # Kiểm tra xem scorecard có dữ liệu không
        if len(self.scorecard) == 0:
            print("Warning: Scorecard is empty, no features were processed")
            self.scorecard_table = pd.DataFrame(columns=['Feature', 'Bin', 'Score'])
            return self.scorecard_table
        
        for feature, bins in self.scorecard.items():
            for bin_value, points in bins.items():
                row = {
                    'Feature': feature,
                    'Bin': bin_value,
                    'Score': points
                }
                rows.append(row)
        
        # Kiểm tra xem có rows nào được tạo không
        if len(rows) == 0:
            print("Warning: No rows generated for scorecard table")
            self.scorecard_table = pd.DataFrame(columns=['Feature', 'Bin', 'Score'])
            return self.scorecard_table
        
        scorecard_table = pd.DataFrame(rows)
        
        # Làm tròn điểm và chuyển sang số nguyên
        if 'Score' in scorecard_table.columns:
            scorecard_table['Score'] = scorecard_table['Score'].round().astype(int)
        else:
            print("Warning: 'Score' column not found in scorecard table")
        
        # Sắp xếp theo đặc trưng và bin
        if len(scorecard_table) > 0 and 'Feature' in scorecard_table.columns and 'Score' in scorecard_table.columns:
            scorecard_table = scorecard_table.sort_values(['Feature', 'Score'])
        
        # Lưu bảng scorecard ra Excel nếu có đường dẫn
        if output_path is not None and len(scorecard_table) > 0:
            # Đảm bảo thư mục tồn tại
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            # Tạo ExcelWriter
            with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
                # Ghi bảng scorecard
                scorecard_table.to_excel(writer, sheet_name='Scorecard', index=False)
                
                # Ghi thông tin bổ sung
                info = pd.DataFrame([
                    {'Parameter': 'Base Score', 'Value': self.base_score},
                    {'Parameter': 'PDO', 'Value': self.pdo},
                    {'Parameter': 'Base Odds', 'Value': self.base_odds},
                    {'Parameter': 'Factor', 'Value': self.factor},
                    {'Parameter': 'Offset', 'Value': self.offset}
                ])
                info.to_excel(writer, sheet_name='Info', index=False)
        
        self.scorecard_table = scorecard_table
        return scorecard_table

    def visualize_scorecard(self, output_path=None):
        """
        Tạo biểu đồ trực quan cho scorecard
        
        Parameters:
        -----------
        output_path : Path, optional
            Đường dẫn file hình ảnh xuất ra
        """
        if self.scorecard_table is None:
            self.create_scorecard_table()
        
        # Kiểm tra xem scorecard_table có dữ liệu và các cột cần thiết không
        if len(self.scorecard_table) == 0:
            print("Warning: Cannot visualize empty scorecard")
            # Tạo một hình trống với thông báo
            plt.figure(figsize=(8, 6))
            plt.text(0.5, 0.5, "Empty Scorecard - No data to visualize", 
                     horizontalalignment='center', verticalalignment='center', fontsize=14)
            
            # Lưu hình trống nếu có đường dẫn
            if output_path is not None:
                os.makedirs(os.path.dirname(output_path), exist_ok=True)
                plt.savefig(output_path)
                plt.close()
            else:
                plt.show()
            return
        
        # Kiểm tra cột Feature có tồn tại không
        if 'Feature' not in self.scorecard_table.columns:
            print("Warning: 'Feature' column not found in scorecard table")
            # Tạo một hình trống với thông báo
            plt.figure(figsize=(8, 6))
            plt.text(0.5, 0.5, "Cannot visualize: 'Feature' column missing", 
                     horizontalalignment='center', verticalalignment='center', fontsize=14)
            
            # Lưu hình trống nếu có đường dẫn
            if output_path is not None:
                os.makedirs(os.path.dirname(output_path), exist_ok=True)
                plt.savefig(output_path)
                plt.close()
            else:
                plt.show()
            return
        
        # Kiểm tra cột Score có tồn tại không
        if 'Score' not in self.scorecard_table.columns:
            print("Warning: 'Score' column not found in scorecard table")
            # Tạo một hình trống với thông báo
            plt.figure(figsize=(8, 6))
            plt.text(0.5, 0.5, "Cannot visualize: 'Score' column missing", 
                     horizontalalignment='center', verticalalignment='center', fontsize=14)
            
            # Lưu hình trống nếu có đường dẫn
            if output_path is not None:
                os.makedirs(os.path.dirname(output_path), exist_ok=True)
                plt.savefig(output_path)
                plt.close()
            else:
                plt.show()
            return
        
        # Tạo hình với kích thước phù hợp
        plt.figure(figsize=(14, 10))
        
        # Lấy danh sách các đặc trưng duy nhất
        features = self.scorecard_table['Feature'].unique()
        
        # Tính số dòng và cột cho subplots
        n_features = len(features)
        n_cols = min(3, n_features)
        n_rows = max(1, (n_features + n_cols - 1) // n_cols)
        
        # Tạo subplots
        fig, axes = plt.subplots(n_rows, n_cols, figsize=(15, 4 * n_rows))
        
        # Làm phẳng axes nếu cần
        if n_rows == 1 and n_cols == 1:
            axes = np.array([axes])
        elif n_rows == 1 or n_cols == 1:
            axes = axes.flatten()
        
        # Vẽ biểu đồ cho từng đặc trưng
        for i, feature in enumerate(features):
            # Lấy dữ liệu cho đặc trưng
            feature_data = self.scorecard_table[self.scorecard_table['Feature'] == feature]
            
            # Xác định vị trí subplot
            row = i // n_cols
            col = i % n_cols
            
            # Lấy trục tương ứng
            if n_rows == 1:
                ax = axes[col]
            elif n_cols == 1:
                ax = axes[row]
            else:
                ax = axes[row, col]
            
            # Vẽ bar plot
            sns.barplot(x='Bin', y='Score', data=feature_data, ax=ax)
            
            # Đặt tiêu đề và nhãn
            ax.set_title(feature)
            ax.set_xlabel('Bin')
            ax.set_ylabel('Points')
            
            # Xoay nhãn trục x nếu cần
            plt.setp(ax.get_xticklabels(), rotation=45, ha='right')
        
        # Ẩn các subplot không sử dụng
        for i in range(n_features, n_rows * n_cols):
            row = i // n_cols
            col = i % n_cols
            if n_rows == 1:
                axes[col].axis('off')
            elif n_cols == 1:
                axes[row].axis('off')
            else:
                axes[row, col].axis('off')
        
        # Điều chỉnh layout
        plt.tight_layout()
        
        # Lưu hình ảnh nếu có đường dẫn
        if output_path is not None:
            # Đảm bảo thư mục tồn tại
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            plt.savefig(output_path)
            plt.close()
        else:
            plt.show()

    def save_scorecard(self, output_path=None):
        """
        Lưu scorecard
        
        Parameters:
        -----------
        output_path : str, optional
            Đường dẫn để lưu scorecard
        """
        if self.scorecard is None:
            raise ValueError("Scorecard hasn't been built yet!")
            
        if output_path is None:
            output_path = Path(__file__).parents[2] / f'models/{self.model_type}_scorecard.pkl'
        
        # Đảm bảo thư mục tồn tại
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        with open(output_path, 'wb') as f:
            scorecard_data = {
                'scorecard': self.scorecard,
                'base_score': self.base_score,
                'pdo': self.pdo,
                'base_odds': self.base_odds,
                'factor': self.factor,
                'offset': self.offset,  # Sử dụng self.offset thay vì self.scorecard_offset
            }
            pickle.dump(scorecard_data, f)
            print(f"Scorecard saved to {output_path}")

    def load_scorecard(self, input_path=None):
        """
        Tải scorecard
        
        Parameters:
        -----------
        input_path : str, optional
            Đường dẫn để tải scorecard
        """
        if input_path is None:
            input_path = Path(__file__).parents[2] / f'models/{self.model_type}_scorecard.pkl'
        
        if not os.path.exists(input_path):
            raise FileNotFoundError(f"Scorecard file not found at {input_path}")
        
        with open(input_path, 'rb') as f:
            scorecard_data = pickle.load(f)
            self.scorecard = scorecard_data['scorecard']
            self.base_score = scorecard_data['base_score']
            self.pdo = scorecard_data['pdo']
            self.base_odds = scorecard_data['base_odds']
            self.factor = scorecard_data['factor']
            # Kiểm tra xem có offset không, nếu không thì dùng self.offset
            self.offset = scorecard_data.get('offset', self.offset)
            print(f"Scorecard loaded from {input_path}")
        
        return self

    def visualize_feature_importance(self, model, X_sample, output_path=None):
        """
        Tạo biểu đồ tầm quan trọng của đặc trưng không sử dụng SHAP
        
        Parameters:
        -----------
        model : xgboost.Booster
            Mô hình XGBoost đã được huấn luyện
        X_sample : DataFrame
            Mẫu dữ liệu để phân tích
        output_path : Path, optional
            Đường dẫn file hình ảnh xuất ra
        """
        # Tạo figure với nhiều subplot
        fig, axes = plt.subplots(2, 2, figsize=(15, 12))
        fig.suptitle('Feature Importance Analysis', fontsize=16)
        
        # 1. XGBoost built-in feature importance
        try:
            # Lấy feature importance từ model
            importance_gain = model.get_score(importance_type='gain')
            importance_weight = model.get_score(importance_type='weight')
            importance_cover = model.get_score(importance_type='cover')
            
            # Chuyển sang DataFrame để dễ vẽ
            importance_df = pd.DataFrame({
                'Gain': importance_gain,
                'Weight': importance_weight,
                'Cover': importance_cover
            }).fillna(0)
            
            # Sắp xếp theo Gain
            importance_df = importance_df.sort_values('Gain', ascending=False)
            
            # Giới hạn số lượng feature hiển thị
            top_n = min(10, len(importance_df))
            importance_df = importance_df.head(top_n)
            
            # Vẽ barplot cho feature importance
            ax = axes[0, 0]
            importance_df['Gain'].plot(kind='barh', ax=ax, color='skyblue')
            ax.set_title('Feature Importance (Gain)')
            ax.set_xlabel('Gain')
            ax.set_ylabel('Features')
            ax.grid(axis='x', linestyle='--', alpha=0.6)
        except Exception as e:
            print(f"Error plotting feature importance: {e}")
            axes[0, 0].text(0.5, 0.5, "Could not generate\nfeature importance plot", 
                         ha='center', va='center', transform=axes[0, 0].transAxes)
        
        # 2. Score Distribution
        try:
            if hasattr(self, 'scorecard') and self.scorecard:
                # Tạo scorecard table nếu chưa có
                if not hasattr(self, 'scorecard_table') or self.scorecard_table is None:
                    self.create_scorecard_table()
                
                ax = axes[0, 1]
                # Vẽ phân phối điểm theo đặc trưng
                feature_scores = self.scorecard_table.groupby('Feature')['Score'].mean().sort_values(ascending=False)
                feature_scores.plot(kind='barh', ax=ax, color='lightgreen')
                ax.set_title('Average Score by Feature')
                ax.set_xlabel('Average Score')
                ax.set_ylabel('Features')
                ax.grid(axis='x', linestyle='--', alpha=0.6)
            else:
                axes[0, 1].text(0.5, 0.5, "No scorecard data available", 
                             ha='center', va='center', transform=axes[0, 1].transAxes)
        except Exception as e:
            print(f"Error plotting score distribution: {e}")
            axes[0, 1].text(0.5, 0.5, "Could not generate\nscore distribution plot", 
                         ha='center', va='center', transform=axes[0, 1].transAxes)
        
        # 3. Permutation Importance
        try:
            if X_sample is not None and len(X_sample) > 0:
                from sklearn.inspection import permutation_importance
                import xgboost as xgb
                
                # Tạo DMatrix từ dữ liệu mẫu
                dmatrix = xgb.DMatrix(X_sample)
                
                # Dự đoán xác suất trên dữ liệu mẫu
                y_pred = model.predict(dmatrix)
                
                # Calculate permutation importance (using a simplified approach)
                perm_importance = {}
                baseline = y_pred.mean()
                
                # Lặp qua từng đặc trưng
                for feature in X_sample.columns:
                    # Tạo bản sao của dữ liệu
                    X_permuted = X_sample.copy()
                    # Xáo trộn giá trị của đặc trưng
                    X_permuted[feature] = np.random.permutation(X_permuted[feature].values)
                    # Dự đoán trên dữ liệu xáo trộn
                    dmatrix_permuted = xgb.DMatrix(X_permuted)
                    y_pred_permuted = model.predict(dmatrix_permuted)
                    # Tính mức độ thay đổi trong dự đoán
                    impact = abs(y_pred_permuted.mean() - baseline)
                    perm_importance[feature] = impact
                
                # Chuyển sang DataFrame và sắp xếp
                perm_df = pd.DataFrame({'Importance': perm_importance}).sort_values('Importance', ascending=False)
                
                # Giới hạn số lượng feature hiển thị
                top_n = min(10, len(perm_df))
                perm_df = perm_df.head(top_n)
                
                # Vẽ barplot
                ax = axes[1, 0]
                perm_df.plot(kind='barh', ax=ax, color='salmon')
                ax.set_title('Permutation Importance')
                ax.set_xlabel('Importance (prediction change)')
                ax.set_ylabel('Features')
                ax.grid(axis='x', linestyle='--', alpha=0.6)
            else:
                axes[1, 0].text(0.5, 0.5, "No sample data available\nfor permutation importance", 
                             ha='center', va='center', transform=axes[1, 0].transAxes)
        except Exception as e:
            print(f"Error calculating permutation importance: {e}")
            axes[1, 0].text(0.5, 0.5, "Could not generate\npermutation importance plot", 
                         ha='center', va='center', transform=axes[1, 0].transAxes)
        
        # 4. Feature Coverage Analysis
        try:
            # Analyze how many trees use each feature
            ax = axes[1, 1]
            
            if 'Cover' in importance_df.columns:
                importance_df['Cover'].plot(kind='barh', ax=ax, color='mediumpurple')
                ax.set_title('Feature Coverage')
                ax.set_xlabel('Coverage (Weighted # of appearances)')
                ax.set_ylabel('Features')
                ax.grid(axis='x', linestyle='--', alpha=0.6)
            else:
                # Vẽ Weight nếu không có Cover
                importance_df['Weight'].plot(kind='barh', ax=ax, color='mediumpurple')
                ax.set_title('Feature Usage (Weight)')
                ax.set_xlabel('Weight (# of appearances)')
                ax.set_ylabel('Features')
                ax.grid(axis='x', linestyle='--', alpha=0.6)
        except Exception as e:
            print(f"Error plotting feature coverage: {e}")
            axes[1, 1].text(0.5, 0.5, "Could not generate\nfeature coverage plot", 
                         ha='center', va='center', transform=axes[1, 1].transAxes)
        
        # Chỉnh layout
        plt.tight_layout()
        plt.subplots_adjust(top=0.92)
        
        # Lưu hình ảnh nếu có đường dẫn
        if output_path is not None:
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            plt.savefig(output_path)
            plt.close()
        else:
            plt.show()

    def visualize_feature_effects(self, X_sample, output_path=None, n_features=6):
        """
        Tạo biểu đồ hiển thị mối quan hệ giữa giá trị đặc trưng và điểm số
        
        Parameters:
        -----------
        X_sample : DataFrame
            Mẫu dữ liệu để phân tích
        output_path : Path, optional
            Đường dẫn file hình ảnh xuất ra
        n_features : int, optional
            Số đặc trưng quan trọng nhất để hiển thị
        """
        if not hasattr(self, 'scorecard') or not self.scorecard:
            print("Warning: No scorecard available for feature effect visualization")
            
            # Tạo hình trống với thông báo
            plt.figure(figsize=(10, 8))
            plt.text(0.5, 0.5, "No scorecard data available to visualize feature effects", 
                     ha='center', va='center', fontsize=14)
            
            # Lưu hình trống nếu có đường dẫn
            if output_path is not None:
                os.makedirs(os.path.dirname(output_path), exist_ok=True)
                plt.savefig(output_path)
                plt.close()
            else:
                plt.show()
            return
        
        # Tạo scorecard table nếu chưa có
        if not hasattr(self, 'scorecard_table') or self.scorecard_table is None:
            self.create_scorecard_table()
        
        # Chọn các đặc trưng quan trọng nhất để hiển thị
        top_features = self.scorecard_table.groupby('Feature')['Score'].agg(lambda x: max(x) - min(x))\
                                             .sort_values(ascending=False).head(n_features).index.tolist()
        
        # Tính số dòng và cột cho subplots
        n_features = len(top_features)
        n_cols = min(3, n_features)
        n_rows = (n_features + n_cols - 1) // n_cols
        
        # Tạo subplots
        fig, axes = plt.subplots(n_rows, n_cols, figsize=(15, 4 * n_rows))
        fig.suptitle('Feature Effects on Score', fontsize=16)
        
        # Làm phẳng axes nếu cần
        if n_rows == 1 and n_cols == 1:
            axes = np.array([axes])
        elif n_rows == 1 or n_cols == 1:
            axes = axes.flatten()
        
        # Phân tích từng đặc trưng
        for i, feature in enumerate(top_features):
            # Lấy dữ liệu cho đặc trưng
            feature_data = self.scorecard_table[self.scorecard_table['Feature'] == feature]
            
            # Xác định vị trí subplot
            row = i // n_cols
            col = i % n_cols
            
            # Lấy trục tương ứng
            if n_rows == 1:
                ax = axes[col]
            elif n_cols == 1:
                ax = axes[row]
            else:
                ax = axes[row, col]
            
            # Chuẩn bị dữ liệu cho biểu đồ
            bin_values = []
            scores = []
            
            for _, row_data in feature_data.iterrows():
                bin_desc = row_data['Bin']
                score = row_data['Score']
                
                # Parse bin description to get numeric threshold
                if "<=" in bin_desc:
                    _, threshold = bin_desc.split("<=")
                    bin_value = float(threshold)
                    bin_type = "<="
                elif ">" in bin_desc:
                    _, threshold = bin_desc.split(">")
                    bin_value = float(threshold)
                    bin_type = ">"
                else:
                    continue
                
                bin_values.append((bin_value, bin_type))
                scores.append(score)
            
            # Sắp xếp theo giá trị bin
            bin_scores = sorted(zip(bin_values, scores), key=lambda x: x[0][0])
            
            # Vẽ line plot
            x_values = [b[0][0] for b in bin_scores]
            y_values = [b[1] for b in bin_scores]
            
            # Thêm các điểm và đường
            ax.plot(x_values, y_values, 'o-', color='royalblue')
            
            # Hiển thị loại so sánh
            for i, ((bin_val, bin_type), score) in enumerate(bin_scores):
                ax.annotate(f"{bin_type} {bin_val}", 
                           (x_values[i], y_values[i]), 
                           xytext=(0, 10), 
                           textcoords='offset points',
                           ha='center',
                           fontsize=8)
            
            # Thêm giá trị phân phối từ X_sample nếu có
            if X_sample is not None and feature in X_sample.columns:
                # Thêm histogram phân phối dữ liệu
                ax2 = ax.twinx()
                sns.histplot(X_sample[feature], ax=ax2, color='lightgrey', alpha=0.3, bins=20)
                ax2.set_ylabel('Data Frequency', color='grey')
                ax2.tick_params(axis='y', colors='grey')
                ax2.set_yticks([])  # Ẩn giá trị cụ thể trên trục y phụ
            
            # Đặt tiêu đề và nhãn
            ax.set_title(feature)
            ax.set_xlabel('Feature Value')
            ax.set_ylabel('Score')
            ax.grid(linestyle='--', alpha=0.6)
        
        # Ẩn các subplot không sử dụng
        for i in range(n_features, n_rows * n_cols):
            row = i // n_cols
            col = i % n_cols
            if n_rows == 1:
                axes[col].axis('off')
            elif n_cols == 1:
                axes[row].axis('off')
            else:
                axes[row, col].axis('off')
        
        # Chỉnh layout
        plt.tight_layout()
        plt.subplots_adjust(top=0.92)
        
        # Lưu hình ảnh nếu có đường dẫn
        if output_path is not None:
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            plt.savefig(output_path)
            plt.close()
        else:
            plt.show()

if __name__ == "__main__":
    import xgboost as xgb
    
    # Ví dụ sử dụng cho Application Scorecard
    model_type = 'application_scorecard'
    model_path = Path(__file__).parents[2] / f'models/{model_type}_xgb_model.json'
    
    # Tải mô hình
    xgb_model = xgb.Booster()
    xgb_model.load_model(str(model_path))
    
    # Tạo scorecard
    builder = ScorecardBuilder(model_type)
    scorecard = builder.build_scorecard_from_model(xgb_model)
    
    # Lưu và trực quan hóa
    builder.create_scorecard_table(Path(__file__).parents[2] / f'results/{model_type}_scorecard.xlsx')
    builder.visualize_scorecard(Path(__file__).parents[2] / f'results/{model_type}_scorecard_viz.png')
    builder.save_scorecard()
    
    print("Scorecard creation completed!")

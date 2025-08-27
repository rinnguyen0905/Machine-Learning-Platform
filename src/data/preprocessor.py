import pandas as pd
import numpy as np
import yaml
import os
from pathlib import Path
from sklearn.feature_selection import SelectKBest, f_classif

class DataPreprocessor:
    """
    Xử lý dữ liệu thô cho các mô hình chấm điểm tín dụng
    """
    def __init__(self, config_path=None):
        if config_path is None:
            config_path = Path(__file__).parents[2] / 'config.yaml'
        
        with open(config_path, 'r') as file:
            self.config = yaml.safe_load(file)
            
        self.raw_data_path = self.config['data']['raw_data_path']
        self.processed_data_path = self.config['data']['processed_data_path']
        
        # Lấy tham số kiểm soát kích thước dữ liệu
        self.max_samples = self.config['data'].get('max_samples', None)
        self.compression = self.config['data'].get('compression', None)
        self.float_precision = self.config['data'].get('float_precision', None)
        self.max_features = self.config['feature_engineering'].get('max_features', None)
        self.categorical_encoding = self.config['feature_engineering'].get('categorical_encoding', 'one-hot')
        self.drop_low_importance = self.config['feature_engineering'].get('drop_low_importance', False)
        
    def load_data(self, file_name):
        """Tải dữ liệu thô"""
        file_path = Path(self.raw_data_path) / file_name
        df = pd.read_csv(file_path)
        
        # Giới hạn số mẫu nếu cần
        if self.max_samples and len(df) > self.max_samples:
            df = df.sample(self.max_samples, random_state=self.config['data']['random_state'])
            print(f"Đã giới hạn số mẫu xuống {self.max_samples}")
        
        return df
    
    def handle_missing_values(self, df):
        """Xử lý giá trị thiếu"""
        df_copy = df.copy()
        # Xử lý các cột số
        numeric_cols = df_copy.select_dtypes(include=['number']).columns
        for col in numeric_cols:
            df_copy[col] = df_copy[col].fillna(df_copy[col].median())
        
        # Xử lý các cột phân loại
        categorical_cols = df_copy.select_dtypes(include=['object', 'category']).columns
        for col in categorical_cols:
            df_copy[col] = df_copy[col].fillna(df_copy[col].mode()[0])
            
        return df_copy
    
    def handle_outliers(self, df, cols=None, method='clip'):
        """Xử lý giá trị ngoại lai"""
        if cols is None:
            cols = df.select_dtypes(include=['number']).columns
            
        if method == 'clip':
            for col in cols:
                q1 = df[col].quantile(0.01)
                q3 = df[col].quantile(0.99)
                df[col] = df[col].clip(q1, q3)
                
        return df
    
    def encode_categorical(self, df, cols=None, method=None):
        """Mã hóa biến phân loại"""
        if method is None:
            method = self.categorical_encoding
            
        if cols is None:
            cols = df.select_dtypes(include=['object', 'category']).columns
            
        if method == 'one-hot':
            # Giảm số lượng mức trong biến phân loại để hạn chế one-hot explosion
            for col in cols:
                if df[col].nunique() > 10:
                    # Gộp các mức hiếm vào 'Other'
                    value_counts = df[col].value_counts(normalize=True)
                    common_values = value_counts[value_counts >= 0.05].index.tolist()
                    df[col] = df[col].apply(lambda x: x if x in common_values else 'Other')
            
            df = pd.get_dummies(df, columns=cols, drop_first=True)
        elif method == 'label':
            from sklearn.preprocessing import LabelEncoder
            le = LabelEncoder()
            for col in cols:
                df[col] = le.fit_transform(df[col])
                
        return df
    
    def select_features(self, df, target_col):
        """Chọn đặc trưng quan trọng nhất nếu cần"""
        if not self.max_features or self.max_features >= df.shape[1] - 1:
            return df
        
        # Lấy ra target và các đặc trưng
        X = df.drop(target_col, axis=1)
        y = df[target_col]
        
        # Chọn đặc trưng
        selector = SelectKBest(f_classif, k=self.max_features)
        X_new = selector.fit_transform(X, y)
        
        # Lấy ra tên các đặc trưng được chọn
        mask = selector.get_support()
        selected_features = X.columns[mask]
        
        # Tạo DataFrame mới với các đặc trưng đã chọn và target
        selected_df = pd.DataFrame(X_new, columns=selected_features)
        selected_df[target_col] = y.values
        
        print(f"Đã giảm từ {df.shape[1]} xuống {selected_df.shape[1]} đặc trưng")
        return selected_df
    
    def reduce_precision(self, df):
        """Giảm độ chính xác của số thập phân để giảm kích thước dữ liệu"""
        if self.float_precision is None:
            return df
            
        for col in df.select_dtypes(include=['float']).columns:
            df[col] = df[col].round(self.float_precision)
            
        return df
    
    def prepare_data_generic(self, file_name, target_col):
        """
        Phương thức chung để chuẩn bị dữ liệu cho tất cả các loại mô hình
        """
        print(f"Đang xử lý {file_name}...")
        df = self.load_data(file_name)
        print(f"Dữ liệu gốc: {df.shape}")
        
        df = self.handle_missing_values(df)
        df = self.handle_outliers(df)
        df = self.encode_categorical(df)
        df = self.select_features(df, target_col)
        df = self.reduce_precision(df)
        
        # Đảm bảo thư mục tồn tại trước khi lưu
        os.makedirs(Path(self.processed_data_path), exist_ok=True)
        
        # Lưu dữ liệu đã xử lý
        output_name = 'processed_' + file_name
        output_path = Path(self.processed_data_path) / output_name
        
        # Lưu với nén nếu được cấu hình
        if self.compression:
            output_name = output_name + '.gz'  # Thêm phần mở rộng gzip
            output_path = Path(self.processed_data_path) / output_name
            df.to_csv(output_path, index=False, compression=self.compression)
            print(f"Đã lưu dữ liệu đã xử lý (nén {self.compression}) vào {output_path}")
        else:
            df.to_csv(output_path, index=False)
            print(f"Đã lưu dữ liệu đã xử lý vào {output_path}")
        
        print(f"Dữ liệu đã xử lý: {df.shape}, kích thước file: {os.path.getsize(output_path) / (1024 * 1024):.2f} MB")
        return df
    
    def prepare_application_data(self):
        """Chuẩn bị dữ liệu cho Application Scorecard"""
        return self.prepare_data_generic('application_data.csv', 'default_flag')
    
    def prepare_behavior_data(self):
        """Chuẩn bị dữ liệu cho Behavior Scorecard"""
        return self.prepare_data_generic('behavior_data.csv', 'default_flag')
    
    def prepare_collections_data(self):
        """Chuẩn bị dữ liệu cho Collections Scoring"""
        return self.prepare_data_generic('collections_data.csv', 'further_delinquency')
    
    def prepare_desertion_data(self):
        """Chuẩn bị dữ liệu cho Desertion Scoring"""
        return self.prepare_data_generic('desertion_data.csv', 'desertion_flag')

if __name__ == "__main__":
    # Trước khi xử lý, đảm bảo thư mục data/raw tồn tại
    base_dir = Path(__file__).parents[2]
    raw_dir = base_dir / 'data' / 'raw'
    os.makedirs(raw_dir, exist_ok=True)
    
    # Kiểm tra xem đã có dữ liệu trong thư mục raw chưa
    if not any(raw_dir.glob('*.csv')):
        print("Không tìm thấy dữ liệu trong thư mục data/raw!")
        print("Đang tạo dữ liệu mẫu để sử dụng...")
        
        # Nhập mô-đun tạo dữ liệu mẫu và tạo dữ liệu
        from src.data.sample_generator import main as generate_sample_data
        generate_sample_data()
    
    # Tiếp tục với tiền xử lý
    preprocessor = DataPreprocessor()
    try:
        preprocessor.prepare_application_data()
        preprocessor.prepare_behavior_data()
        preprocessor.prepare_collections_data()
        preprocessor.prepare_desertion_data()
        print("Preprocessing completed!")
    except FileNotFoundError as e:
        print(f"Lỗi: {e}")
        print("Vui lòng đảm bảo rằng các file dữ liệu cần thiết đã được đặt trong thư mục data/raw")
        print("Hoặc chạy lệnh python -m src.data.sample_generator để tạo dữ liệu mẫu")

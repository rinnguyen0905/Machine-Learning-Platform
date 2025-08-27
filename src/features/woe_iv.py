import pandas as pd
import numpy as np
from optbinning import OptimalBinning
import yaml
import pickle
from pathlib import Path

class WoeIvTransformer:
    """
    Tính toán Weight of Evidence (WOE) và Information Value (IV) cho các biến
    """
    def __init__(self, config_path=None):
        if config_path is None:
            config_path = Path(__file__).parents[2] / 'config.yaml'
        
        with open(config_path, 'r') as file:
            self.config = yaml.safe_load(file)
        
        self.max_bins = self.config['feature_engineering']['max_bins']
        self.min_bin_size = self.config['feature_engineering']['min_bin_size']
        self.binnings = {}
        self.iv_values = {}
        
    def fit(self, X, y, columns=None):
        """
        Tính WOE và IV cho tất cả các cột được chỉ định
        
        Parameters:
        -----------
        X : DataFrame
            Dữ liệu đặc trưng
        y : Series
            Cột mục tiêu (bad = 1, good = 0)
        columns : list, optional
            Danh sách cột cần tính WOE, IV. Nếu None, sẽ tính toán tất cả các cột.
        """
        if columns is None:
            columns = X.columns
            
        for column in columns:
            variable = X[column]
            
            # Kiểm tra kiểu dữ liệu
            if pd.api.types.is_numeric_dtype(variable):
                binning_type = 'continuous'
            else:
                binning_type = 'categorical'
                
            # Tạo binning tối ưu
            binning = OptimalBinning(
                name=column,
                dtype=binning_type,
                max_n_bins=self.max_bins,
                min_bin_size=self.min_bin_size
            )
            
            try:
                binning.fit(variable, y)
                self.binnings[column] = binning
                self.iv_values[column] = binning.iv
            except Exception as e:
                print(f"Lỗi khi tính WOE cho {column}: {e}")
                
        # Sắp xếp IV theo thứ tự giảm dần
        self.iv_table = pd.DataFrame({
            'Variable': list(self.iv_values.keys()),
            'IV': list(self.iv_values.values())
        }).sort_values('IV', ascending=False).reset_index(drop=True)
        
        return self
    
    def transform(self, X, columns=None):
        """
        Chuyển đổi các biến thành giá trị WOE
        
        Parameters:
        -----------
        X : DataFrame
            Dữ liệu cần chuyển đổi
        columns : list, optional
            Danh sách cột cần chuyển đổi. Nếu None, sẽ chuyển đổi tất cả các cột đã được fit.
        
        Returns:
        --------
        DataFrame
            DataFrame với các cột đã chuyển đổi thành WOE
        """
        X_woe = X.copy()
        
        if columns is None:
            columns = self.binnings.keys()
        
        for column in columns:
            if column in self.binnings:
                X_woe[column] = self.binnings[column].transform(X[column], metric='woe')
            
        return X_woe
    
    def fit_transform(self, X, y, columns=None):
        """
        Fit và chuyển đổi cùng lúc
        """
        self.fit(X, y, columns)
        return self.transform(X, columns)
    
    def get_iv_table(self):
        """
        Trả về bảng Information Value
        """
        return self.iv_table.copy()
    
    def get_binning_table(self, column):
        """
        Trả về bảng binning chi tiết cho một cột
        """
        if column in self.binnings:
            return self.binnings[column].binning_table.build()
        else:
            return None
    
    def save(self, path='models/woe_transformer.pkl'):
        """
        Lưu transformer
        """
        with open(path, 'wb') as f:
            pickle.dump(self, f)
    
    @staticmethod
    def load(path='models/woe_transformer.pkl'):
        """
        Tải transformer đã được lưu
        """
        with open(path, 'rb') as f:
            return pickle.load(f)

if __name__ == "__main__":
    # Ví dụ sử dụng
    import pandas as pd
    from pathlib import Path
    
    # Đọc dữ liệu đã xử lý
    data_path = Path(__file__).parents[2] / 'data/processed/processed_application_data.csv'
    data = pd.read_csv(data_path)
    
    # Tách X và y
    y = data['default_flag']
    X = data.drop('default_flag', axis=1)
    
    # Fit và transform
    woe_transformer = WoeIvTransformer()
    X_woe = woe_transformer.fit_transform(X, y)
    
    # In bảng IV
    print(woe_transformer.get_iv_table())
    
    # Lưu transformer
    output_path = Path(__file__).parents[2] / 'models/woe_transformer.pkl'
    woe_transformer.save(output_path)
    
    print("WOE transformation completed and saved!")

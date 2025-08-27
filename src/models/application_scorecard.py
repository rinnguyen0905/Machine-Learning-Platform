import pandas as pd
import numpy as np
from pathlib import Path
from .base_model import BaseXGBoostModel

class ApplicationScorecard(BaseXGBoostModel):
    """
    Mô hình Application Scorecard cho khách hàng mới
    """
    def __init__(self, config_path=None):
        super().__init__('application_scorecard', config_path)
    
    def process_and_train(self, data_path=None):
        """
        Quy trình đầy đủ từ đọc dữ liệu đến huấn luyện mô hình
        
        Parameters:
        -----------
        data_path : str, optional
            Đường dẫn đến dữ liệu đã xử lý cho application scorecard
            
        Returns:
        --------
        dict
            Từ điển chứa metrics đánh giá
        """
        if data_path is None:
            data_path = Path(__file__).parents[2] / 'data/processed/processed_application_data.csv'
        
        # Đọc dữ liệu
        data = pd.read_csv(data_path)
        
        # Chuẩn bị dữ liệu
        X_train, X_test, y_train, y_test = self.prepare_data(data)
        
        # Chuyển đổi đặc trưng
        X_train_woe, X_test_woe = self.transform_features(X_train, X_test, y_train)
        
        # Huấn luyện mô hình
        self.train(X_train_woe, y_train, X_test_woe, y_test)
        
        # Đánh giá mô hình
        metrics = self.evaluate(X_test, y_test)
        
        # Lưu mô hình
        self.save_model()
        
        return metrics
        
    def get_application_risk_profile(self, customer_data):
        """
        Tạo hồ sơ rủi ro cho một khách hàng mới
        
        Parameters:
        -----------
        customer_data : DataFrame
            Dữ liệu của một khách hàng
            
        Returns:
        --------
        dict
            Thông tin rủi ro và điểm
        """
        proba = self.predict(customer_data)[0]
        
        risk_profile = {
            'probability_of_default': proba,
            'risk_level': 'High' if proba > 0.3 else ('Medium' if proba > 0.1 else 'Low'),
            'recommendation': 'Reject' if proba > 0.3 else ('Review' if proba > 0.1 else 'Approve')
        }
        
        return risk_profile

if __name__ == "__main__":
    # Ví dụ sử dụng
    model = ApplicationScorecard()
    metrics = model.process_and_train()
    print("Application Scorecard Model Metrics:")
    print(metrics)

import pandas as pd
import numpy as np
from pathlib import Path
from .base_model import BaseXGBoostModel

class BehaviorScorecard(BaseXGBoostModel):
    """
    Mô hình Behavior Scorecard cho khách hàng hiện tại
    """
    def __init__(self, config_path=None):
        super().__init__('behavior_scorecard', config_path)
    
    def process_and_train(self, data_path=None):
        """
        Quy trình đầy đủ từ đọc dữ liệu đến huấn luyện mô hình
        
        Parameters:
        -----------
        data_path : str, optional
            Đường dẫn đến dữ liệu đã xử lý cho behavior scorecard
            
        Returns:
        --------
        dict
            Từ điển chứa metrics đánh giá
        """
        if data_path is None:
            data_path = Path(__file__).parents[2] / 'data/processed/processed_behavior_data.csv'
        
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
        
    def recommend_credit_limit(self, customer_data, current_limit):
        """
        Đề xuất giới hạn tín dụng dựa trên mô hình hành vi
        
        Parameters:
        -----------
        customer_data : DataFrame
            Dữ liệu của một khách hàng
        current_limit : float
            Giới hạn tín dụng hiện tại
            
        Returns:
        --------
        dict
            Thông tin điều chỉnh giới hạn tín dụng
        """
        proba = self.predict(customer_data)[0]
        
        if proba < 0.05:  # Rủi ro rất thấp
            new_limit = current_limit * 1.5
            change = "increase"
        elif proba < 0.15:  # Rủi ro thấp
            new_limit = current_limit * 1.2
            change = "increase"
        elif proba < 0.25:  # Rủi ro trung bình
            new_limit = current_limit  # Giữ nguyên
            change = "maintain"
        elif proba < 0.4:  # Rủi ro cao
            new_limit = current_limit * 0.8
            change = "decrease"
        else:  # Rủi ro rất cao
            new_limit = current_limit * 0.5
            change = "decrease"
        
        recommendation = {
            'probability_of_default': proba,
            'current_limit': current_limit,
            'recommended_limit': new_limit,
            'action': change,
            'risk_level': 'Very Low' if proba < 0.05 else 
                          'Low' if proba < 0.15 else 
                          'Medium' if proba < 0.25 else 
                          'High' if proba < 0.4 else 'Very High'
        }
        
        return recommendation

if __name__ == "__main__":
    # Ví dụ sử dụng
    model = BehaviorScorecard()
    metrics = model.process_and_train()
    print("Behavior Scorecard Model Metrics:")
    print(metrics)

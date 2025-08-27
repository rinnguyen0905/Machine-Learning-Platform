import pandas as pd
import numpy as np
from pathlib import Path
from .base_model import BaseXGBoostModel

class DesertionScoring(BaseXGBoostModel):
    """
    Mô hình Desertion Scoring để dự đoán khả năng khách hàng từ bỏ sau khi trả hết nợ
    """
    def __init__(self, config_path=None):
        super().__init__('desertion_scoring', config_path)
    
    def process_and_train(self, data_path=None):
        """
        Quy trình đầy đủ từ đọc dữ liệu đến huấn luyện mô hình
        
        Parameters:
        -----------
        data_path : str, optional
            Đường dẫn đến dữ liệu đã xử lý cho desertion scoring
            
        Returns:
        --------
        dict
            Từ điển chứa metrics đánh giá
        """
        if data_path is None:
            data_path = Path(__file__).parents[2] / 'data/processed/processed_desertion_data.csv'
        
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
    
    def create_retention_strategy(self, customer_data):
        """
        Tạo chiến lược giữ chân cho khách hàng có nguy cơ từ bỏ
        
        Parameters:
        -----------
        customer_data : DataFrame
            Dữ liệu của khách hàng
            
        Returns:
        --------
        DataFrame
            Khách hàng với chiến lược giữ chân
        """
        # Dự đoán xác suất từ bỏ
        customer_data['desertion_probability'] = self.predict(customer_data)
        
        # Phân loại theo mức độ rủi ro
        customer_data['risk_tier'] = pd.cut(
            customer_data['desertion_probability'],
            bins=[0, 0.3, 0.6, 1.0],
            labels=['Low', 'Medium', 'High']
        )
        
        # Chiến lược dựa trên phân loại rủi ro
        strategies = {
            'Low': 'Standard follow-up - Email renewal options',
            'Medium': 'Proactive outreach - Special renewal offer',
            'High': 'Priority retention - Personal call and premium incentives'
        }
        
        customer_data['retention_strategy'] = customer_data['risk_tier'].map(strategies)
        
        # Thêm đề xuất ưu đãi dựa trên xác suất
        customer_data['discount_offer'] = customer_data['desertion_probability'].apply(
            lambda p: '5%' if p < 0.3 else '10%' if p < 0.6 else '15%'
        )
        
        return customer_data

if __name__ == "__main__":
    # Ví dụ sử dụng
    model = DesertionScoring()
    metrics = model.process_and_train()
    print("Desertion Scoring Model Metrics:")
    print(metrics)

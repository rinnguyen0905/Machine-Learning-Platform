import pandas as pd
import numpy as np
from pathlib import Path
from .base_model import BaseXGBoostModel

class CollectionsScoring(BaseXGBoostModel):
    """
    Mô hình Collections Scoring để dự đoán khả năng tiếp tục trễ hạn
    """
    def __init__(self, config_path=None):
        super().__init__('collections_scoring', config_path)
    
    def process_and_train(self, data_path=None):
        """
        Quy trình đầy đủ từ đọc dữ liệu đến huấn luyện mô hình
        
        Parameters:
        -----------
        data_path : str, optional
            Đường dẫn đến dữ liệu đã xử lý cho collections scoring
            
        Returns:
        --------
        dict
            Từ điển chứa metrics đánh giá
        """
        if data_path is None:
            data_path = Path(__file__).parents[2] / 'data/processed/processed_collections_data.csv'
        
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
    
    def prioritize_collections(self, delinquent_accounts, top_n=100):
        """
        Ưu tiên các tài khoản để thu hồi nợ
        
        Parameters:
        -----------
        delinquent_accounts : DataFrame
            Dữ liệu của các tài khoản đang trễ hạn
        top_n : int, optional
            Số lượng tài khoản ưu tiên cao nhất cần trả về
            
        Returns:
        --------
        DataFrame
            Danh sách tài khoản được ưu tiên cho thu hồi nợ
        """
        # Dự đoán xác suất tiếp tục trễ hạn
        delinquent_accounts['probability_further_delinquency'] = self.predict(delinquent_accounts)
        
        # Tính điểm ưu tiên = xác suất * số tiền quá hạn
        if 'outstanding_amount' in delinquent_accounts.columns:
            delinquent_accounts['priority_score'] = (
                delinquent_accounts['probability_further_delinquency'] * 
                delinquent_accounts['outstanding_amount']
            )
        else:
            delinquent_accounts['priority_score'] = delinquent_accounts['probability_further_delinquency']
        
        # Sắp xếp theo điểm ưu tiên giảm dần
        prioritized = delinquent_accounts.sort_values('priority_score', ascending=False).head(top_n)
        
        # Thêm trạng thái hành động
        prioritized['suggested_action'] = prioritized['probability_further_delinquency'].apply(
            lambda p: 'Immediate Contact' if p > 0.7 else 
                      'Phone Call' if p > 0.4 else
                      'Email Reminder'
        )
        
        return prioritized

if __name__ == "__main__":
    # Ví dụ sử dụng
    model = CollectionsScoring()
    metrics = model.process_and_train()
    print("Collections Scoring Model Metrics:")
    print(metrics)

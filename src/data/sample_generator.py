import pandas as pd
import numpy as np
from pathlib import Path
import os

def generate_application_data(n_samples=10000, bad_rate=0.2):
    """
    Tạo dữ liệu mẫu cho Application Scorecard
    
    Parameters:
    -----------
    n_samples : int
        Số lượng mẫu cần tạo
    bad_rate : float
        Tỷ lệ khách hàng xấu (vỡ nợ)
    """
    # Tạo số lượng khách hàng tốt/xấu
    n_bad = int(n_samples * bad_rate)
    n_good = n_samples - n_bad
    
    # Tạo dữ liệu
    np.random.seed(42)
    
    # Khách hàng tốt có xu hướng:
    # - Lớn tuổi hơn
    # - Thu nhập cao hơn
    # - Thời gian làm việc dài hơn
    # - Tỷ lệ nợ/thu nhập thấp hơn
    
    # Tạo dữ liệu khách hàng tốt
    good_data = pd.DataFrame({
        'customer_id': [f'CUS{i:06d}' for i in range(n_good)],
        'age': np.random.normal(40, 10, n_good).clip(18, 80).astype(int),
        'income': np.random.normal(60000, 20000, n_good).clip(10000, 200000),
        'employment_length': np.random.normal(8, 5, n_good).clip(0, 40),
        'debt_to_income': np.random.normal(0.2, 0.1, n_good).clip(0, 0.8),
        'credit_history_length': np.random.normal(10, 5, n_good).clip(0, 30),
        'number_of_debts': np.random.poisson(2, n_good),
        'number_of_delinquent_debts': np.random.poisson(0.2, n_good),
        'homeowner': np.random.choice([0, 1], n_good, p=[0.3, 0.7]),
        'default_flag': 0
    })
    
    # Tạo dữ liệu khách hàng xấu
    bad_data = pd.DataFrame({
        'customer_id': [f'CUS{i:06d}' for i in range(n_good, n_samples)],
        'age': np.random.normal(30, 10, n_bad).clip(18, 80).astype(int),
        'income': np.random.normal(40000, 15000, n_bad).clip(10000, 200000),
        'employment_length': np.random.normal(3, 3, n_bad).clip(0, 40),
        'debt_to_income': np.random.normal(0.5, 0.2, n_bad).clip(0, 1.5),
        'credit_history_length': np.random.normal(3, 3, n_bad).clip(0, 30),
        'number_of_debts': np.random.poisson(4, n_bad),
        'number_of_delinquent_debts': np.random.poisson(2, n_bad),
        'homeowner': np.random.choice([0, 1], n_bad, p=[0.7, 0.3]),
        'default_flag': 1
    })
    
    # Kết hợp và xáo trộn dữ liệu
    data = pd.concat([good_data, bad_data]).sample(frac=1).reset_index(drop=True)
    
    return data

def generate_behavior_data(n_samples=10000, bad_rate=0.15):
    """
    Tạo dữ liệu mẫu cho Behavior Scorecard
    """
    n_bad = int(n_samples * bad_rate)
    n_good = n_samples - n_bad
    
    np.random.seed(42)
    
    # Khách hàng tốt có xu hướng:
    # - Tỷ lệ thanh toán cao hơn
    # - Ít thanh toán trễ
    # - Khoảng thời gian dài hơn từ lần thanh toán trễ cuối cùng
    
    # Tạo dữ liệu khách hàng tốt
    good_data = pd.DataFrame({
        'customer_id': [f'CUS{i:06d}' for i in range(n_good)],
        'current_balance': np.random.normal(5000, 3000, n_good).clip(0, 20000),
        'average_monthly_payment': np.random.normal(1000, 500, n_good).clip(100, 5000),
        'payment_ratio': np.random.normal(0.8, 0.2, n_good).clip(0.1, 1),
        'number_of_late_payments': np.random.poisson(0.5, n_good),
        'months_since_last_late_payment': np.random.poisson(20, n_good),
        'number_of_credit_inquiries': np.random.poisson(1, n_good),
        'current_limit': np.random.normal(10000, 5000, n_good).clip(1000, 50000),
        'average_utilization': np.random.normal(0.3, 0.2, n_good).clip(0, 1),
        'default_flag': 0
    })
    
    # Tạo dữ liệu khách hàng xấu
    bad_data = pd.DataFrame({
        'customer_id': [f'CUS{i:06d}' for i in range(n_good, n_samples)],
        'current_balance': np.random.normal(8000, 4000, n_bad).clip(0, 20000),
        'average_monthly_payment': np.random.normal(500, 300, n_bad).clip(50, 5000),
        'payment_ratio': np.random.normal(0.3, 0.2, n_bad).clip(0, 1),
        'number_of_late_payments': np.random.poisson(3, n_bad),
        'months_since_last_late_payment': np.random.poisson(3, n_bad),
        'number_of_credit_inquiries': np.random.poisson(4, n_bad),
        'current_limit': np.random.normal(8000, 4000, n_bad).clip(1000, 50000),
        'average_utilization': np.random.normal(0.7, 0.2, n_bad).clip(0, 1),
        'default_flag': 1
    })
    
    # Kết hợp và xáo trộn dữ liệu
    data = pd.concat([good_data, bad_data]).sample(frac=1).reset_index(drop=True)
    
    return data

def generate_collections_data(n_samples=10000):
    """
    Tạo dữ liệu mẫu cho Collections Scoring
    """
    np.random.seed(42)
    
    data = pd.DataFrame({
        'customer_id': [f'CUS{i:06d}' for i in range(n_samples)],
        'days_past_due': np.random.randint(1, 180, n_samples),
        'outstanding_amount': np.random.normal(5000, 3000, n_samples).clip(100, 30000),
        'number_of_contacts': np.random.poisson(3, n_samples),
        'previous_late_payments': np.random.poisson(2, n_samples),
        'promised_payment_amount': np.random.normal(1000, 500, n_samples).clip(0, 10000),
        'broken_promises': np.random.poisson(1, n_samples),
        'months_on_book': np.random.randint(1, 60, n_samples),
        'last_payment_amount': np.random.normal(500, 300, n_samples).clip(0, 5000)
    })
    
    # Thêm cột mục tiêu - xác suất tiếp tục trễ hạn cao hơn đối với:
    # - Số ngày quá hạn cao
    # - Số lần bị bỏ lỡ hẹn trả nợ cao
    # - Số tiền quá hạn cao
    
    # Tính xác suất theo hàm logistic
    logodds = (
        0.02 * data['days_past_due'] + 
        0.5 * data['broken_promises'] + 
        0.0001 * data['outstanding_amount'] - 
        0.001 * data['last_payment_amount'] - 2
    )
    
    probability = 1 / (1 + np.exp(-logodds))
    data['further_delinquency'] = np.random.binomial(1, probability)
    
    return data

def generate_desertion_data(n_samples=10000):
    """
    Tạo dữ liệu mẫu cho Desertion Scoring
    """
    np.random.seed(42)
    
    data = pd.DataFrame({
        'customer_id': [f'CUS{i:06d}' for i in range(n_samples)],
        'months_to_maturity': np.random.randint(1, 24, n_samples),
        'total_relationship_value': np.random.normal(50000, 30000, n_samples).clip(1000, 500000),
        'number_of_products': np.random.poisson(2, n_samples) + 1,
        'satisfaction_score': np.random.normal(7, 2, n_samples).clip(1, 10),
        'number_of_complaints': np.random.poisson(0.5, n_samples),
        'months_since_last_interaction': np.random.poisson(2, n_samples),
        'age': np.random.normal(40, 15, n_samples).clip(18, 90).astype(int),
        'tenure_months': np.random.poisson(30, n_samples),
        'monthly_average_balance': np.random.normal(10000, 5000, n_samples).clip(0, 100000)
    })
    
    # Thêm cột mục tiêu - xác suất từ bỏ cao hơn đối với:
    # - Số tháng gần đến kỳ hạn
    # - Mức độ hài lòng thấp
    # - Thời gian kể từ tương tác cuối cùng cao
    # - Số lượng sản phẩm ít
    
    # Tính xác suất theo hàm logistic
    logodds = (
        -0.1 * data['months_to_maturity'] - 
        0.5 * data['satisfaction_score'] + 
        0.2 * data['months_since_last_interaction'] - 
        0.5 * data['number_of_products'] +
        0.5 * data['number_of_complaints'] - 
        0.00001 * data['total_relationship_value'] + 1
    )
    
    probability = 1 / (1 + np.exp(-logodds))
    data['desertion_flag'] = np.random.binomial(1, probability)
    
    return data

def main():
    """
    Tạo và lưu dữ liệu mẫu cho tất cả các loại mô hình
    """
    # Tạo thư mục dữ liệu
    base_dir = Path(__file__).parents[2]
    raw_dir = base_dir / 'data' / 'raw'
    sample_dir = base_dir / 'data' / 'sample'
    
    # Tạo thư mục nếu chưa tồn tại
    os.makedirs(raw_dir, exist_ok=True)
    os.makedirs(sample_dir, exist_ok=True)
    
    # Tạo dữ liệu mẫu
    print("Tạo dữ liệu mẫu Application Scorecard...")
    app_data = generate_application_data()
    
    print("Tạo dữ liệu mẫu Behavior Scorecard...")
    behavior_data = generate_behavior_data()
    
    print("Tạo dữ liệu mẫu Collections Scoring...")
    collections_data = generate_collections_data()
    
    print("Tạo dữ liệu mẫu Desertion Scoring...")
    desertion_data = generate_desertion_data()
    
    # Lưu vào thư mục sample
    app_data.to_csv(sample_dir / 'application_data.csv', index=False)
    behavior_data.to_csv(sample_dir / 'behavior_data.csv', index=False)
    collections_data.to_csv(sample_dir / 'collections_data.csv', index=False)
    desertion_data.to_csv(sample_dir / 'desertion_data.csv', index=False)
    
    # Sao chép vào thư mục raw nếu được yêu cầu
    copy_to_raw = input("Bạn có muốn sao chép dữ liệu mẫu vào thư mục data/raw để sử dụng không? (y/n): ")
    if copy_to_raw.lower() == 'y':
        app_data.to_csv(raw_dir / 'application_data.csv', index=False)
        behavior_data.to_csv(raw_dir / 'behavior_data.csv', index=False)
        collections_data.to_csv(raw_dir / 'collections_data.csv', index=False)
        desertion_data.to_csv(raw_dir / 'desertion_data.csv', index=False)
        print("Đã sao chép dữ liệu mẫu vào thư mục data/raw.")
    
    print("Hoàn thành tạo dữ liệu mẫu! Các tập dữ liệu đã được lưu vào thư mục data/sample.")

if __name__ == "__main__":
    main()

# Hướng dẫn chuẩn bị dữ liệu

## Cấu trúc thư mục

```
data/
├── raw/                 # Dữ liệu thô, chưa xử lý
├── processed/           # Dữ liệu đã được tiền xử lý
└── sample/              # Dữ liệu mẫu để chạy thử
```

## Chuẩn bị dữ liệu

### 1. Sử dụng dữ liệu mẫu

Nếu bạn muốn thử nghiệm hệ thống, hãy sử dụng dữ liệu mẫu được tạo tự động:

```bash
python -m src.data.sample_generator
```

Lệnh này sẽ tạo dữ liệu mẫu trong thư mục `data/sample` và hỏi bạn có muốn sao chép vào thư mục `data/raw` không.

### 2. Sử dụng dữ liệu riêng

Nếu bạn muốn sử dụng dữ liệu riêng, hãy chuẩn bị các tập dữ liệu với định dạng sau:

#### Application Scorecard Data

File: `data/raw/application_data.csv`

Các cột cần thiết:
- `customer_id`: ID khách hàng
- `age`: Tuổi
- `income`: Thu nhập
- `employment_length`: Thời gian làm việc
- `debt_to_income`: Tỷ lệ nợ/thu nhập
- `credit_history_length`: Độ dài lịch sử tín dụng
- `number_of_debts`: Số khoản nợ
- `number_of_delinquent_debts`: Số khoản nợ quá hạn
- `default_flag`: Cột mục tiêu (0: tốt, 1: xấu)

#### Behavior Scorecard Data

File: `data/raw/behavior_data.csv`

Các cột cần thiết:
- `customer_id`: ID khách hàng
- `current_balance`: Số dư hiện tại
- `average_monthly_payment`: Thanh toán trung bình hàng tháng
- `payment_ratio`: Tỷ lệ thanh toán
- `number_of_late_payments`: Số lần thanh toán trễ
- `months_since_last_late_payment`: Số tháng từ lần thanh toán trễ cuối
- `number_of_credit_inquiries`: Số lần kiểm tra tín dụng
- `current_limit`: Hạn mức tín dụng hiện tại
- `default_flag`: Cột mục tiêu (0: tốt, 1: xấu)

#### Collections Scoring Data

File: `data/raw/collections_data.csv`

Các cột cần thiết:
- `customer_id`: ID khách hàng
- `days_past_due`: Số ngày quá hạn
- `outstanding_amount`: Số tiền chưa thanh toán
- `number_of_contacts`: Số lần liên hệ
- `previous_late_payments`: Số lần thanh toán trễ trước đây
- `promised_payment_amount`: Số tiền hứa thanh toán
- `broken_promises`: Số lần không thực hiện được lời hứa
- `further_delinquency`: Cột mục tiêu (0: không tiếp tục trễ hạn, 1: tiếp tục trễ hạn)

#### Desertion Scoring Data

File: `data/raw/desertion_data.csv`

Các cột cần thiết:
- `customer_id`: ID khách hàng
- `months_to_maturity`: Số tháng đến kỳ hạn
- `total_relationship_value`: Tổng giá trị quan hệ
- `number_of_products`: Số sản phẩm
- `satisfaction_score`: Điểm hài lòng
- `number_of_complaints`: Số lần khiếu nại
- `months_since_last_interaction`: Số tháng từ lần tương tác cuối
- `desertion_flag`: Cột mục tiêu (0: không từ bỏ, 1: từ bỏ)

## Lưu ý

- Bạn có thể thêm các cột khác vào dữ liệu, nhưng ít nhất phải có các cột cần thiết liệt kê ở trên
- Đảm bảo tất cả các file có dòng tiêu đề (header)
- Nếu dữ liệu bạn có cấu trúc khác, bạn cần điều chỉnh file cấu hình `config.yaml` phù hợp

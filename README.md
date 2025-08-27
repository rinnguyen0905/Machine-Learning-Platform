# 🚀 Credit Scoring và Scorecard System

[![GitHub Repo](https://img.shields.io/badge/GitHub-Repository-blue)](https://github.com/rinnguyen0905/Machine-Learning-Platform)

> Hệ thống xây dựng các mô hình chấm điểm tín dụng sử dụng XGBoost. Đơn giản, mạnh mẽ và dễ sử dụng! 💡

![ML Platform Icon](data/images/ML_Platform_icon.png)

## ✨ Các loại mô hình được hỗ trợ

- 🎯 **Application Scorecard**: Đánh giá khách hàng mới
- 📊 **Behavior Scorecard**: Đánh giá khách hàng hiện tại
- 🔍 **Collections Scoring**: Dự đoán khả năng tiếp tục trễ hạn
- 🚪 **Desertion Scoring**: Dự đoán khách hàng từ bỏ

## 🛠️ Cài đặt

```bash
pip install -r requirements.txt
```

## 📁 Nguồn dữ liệu

Dự án này cần các tập dữ liệu cho từng loại mô hình. Bạn có thể lấy dữ liệu từ:

### 🌐 Bộ dữ liệu công khai
- **Application Scorecard**: German Credit Dataset, PKDD'99, hoặc Home Credit Default Risk (Kaggle)
- **Behavior Scorecard**: Lending Club Dataset, Credit Card Default (Taiwan)
- **Collections Scoring**: Thường là dữ liệu nội bộ, nhưng có thể mô phỏng từ các tập dữ liệu nợ xấu
- **Desertion Scoring**: Có thể mô phỏng từ dữ liệu khách hàng với thông tin từ bỏ

### 📋 Dữ liệu mẫu
- Dự án đi kèm với dữ liệu mẫu trong thư mục `data/sample` để chạy thử hệ thống
- Dùng lệnh `python -m src.data.sample_generator` để tạo dữ liệu mẫu

### 🗂️ Cấu trúc dữ liệu yêu cầu
- Đặt các file dữ liệu thô trong thư mục `data/raw` với tên:
  - `application_data.csv`: Dữ liệu khách hàng mới
  - `behavior_data.csv`: Dữ liệu hành vi khách hàng
  - `collections_data.csv`: Dữ liệu khách hàng quá hạn
  - `desertion_data.csv`: Dữ liệu khách hàng có khả năng từ bỏ
- Mỗi tập dữ liệu cần có cột mục tiêu tương ứng (được cấu hình trong config.yaml)

## 🚀 Sử dụng

1. Chuẩn bị dữ liệu theo hướng dẫn trong `data/README.md`
2. Chạy tiền xử lý dữ liệu: `python -m src.data.preprocessor`
3. Xây dựng mô hình: `python -m src.models.<model_name>`
4. Tạo scorecard: `python -m src.scorecard.scorecard_builder`
5. Khởi động API: `python -m api.main`

## 📖 Hướng dẫn sử dụng chi tiết

Hệ thống này cung cấp tập lệnh `run.py` để thực hiện các tác vụ khác nhau trong quy trình xây dựng và triển khai mô hình chấm điểm tín dụng.

### 🔄 Tiền xử lý dữ liệu

Để tiền xử lý dữ liệu cho tất cả các mô hình:

```bash
python run.py --action preprocess --model all
```

Hoặc chỉ tiền xử lý dữ liệu cho một mô hình cụ thể (application, behavior, collections, desertion):

```bash
python run.py --action preprocess --model application
```

### 🧠 Huấn luyện mô hình

Để huấn luyện tất cả các mô hình:

```bash
python run.py --action train --model all
```

Để huấn luyện một mô hình cụ thể:

```bash
python run.py --action train --model behavior
```

### 📈 Tạo Scorecard

Để tạo scorecard cho tất cả các mô hình:

```bash
python run.py --action scorecard --model all
```

Để tạo scorecard cho một mô hình cụ thể:

```bash
python run.py --action scorecard --model application
```

### ⚡ Thực hiện tất cả các bước

Để thực hiện tất cả các bước từ tiền xử lý dữ liệu đến tạo scorecard cho tất cả các mô hình:

```bash
python run.py --action all --model all
```

### 🌐 Khởi động API

Để khởi động API phục vụ các mô hình đã huấn luyện:

```bash
python run.py --action api
```

Sau khi khởi động, API sẽ chạy tại địa chỉ `http://localhost:8000` và bạn có thể truy cập tài liệu API tại `http://localhost:8000/docs`.

### 🏗️ Cấu trúc API

- `POST /application-score/`: Tính điểm tín dụng cho khách hàng mới
- `POST /behavior-score/`: Tính điểm hành vi cho khách hàng hiện tại
- `POST /collections-prioritize/`: Ưu tiên các tài khoản thu hồi nợ
- `POST /desertion-strategy/`: Tạo chiến lược giữ chân khách hàng

---

**Liên hệ**: Nếu có câu hỏi, hãy tạo issue trên GitHub! 😊

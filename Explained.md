# Phương pháp luận Credit Scoring Platform

## Giới thiệu

Hệ thống Credit Scoring Platform là một nền tảng toàn diện để xây dựng và triển khai các mô hình chấm điểm tín dụng sử dụng XGBoost. Nền tảng hỗ trợ bốn loại mô hình chính, mỗi mô hình phục vụ một mục đích khác nhau trong vòng đời quản lý rủi ro tín dụng của khách hàng.

## Phương pháp luận chung

### Gradient Boosting với XGBoost

Tất cả các mô hình đều xây dựng trên nền tảng XGBoost (eXtreme Gradient Boosting), một thuật toán máy học dựa trên nguyên lý gradient boosting. Đây là thuật toán hiệu quả cho các bài toán phân loại và hồi quy với những ưu điểm:

- Xử lý tốt dữ liệu có nhiều đặc trưng
- Chống overfitting hiệu quả thông qua regularization
- Xử lý tốt các giá trị thiếu
- Tốc độ và hiệu suất cao
- Hỗ trợ song song hóa

### Biến đổi Weight of Evidence (WOE)

Trước khi đưa vào mô hình, các biến được biến đổi sang giá trị WOE (Weight of Evidence):

```
WOE = ln(% phân phối Good / % phân phối Bad)
```

Điều này mang lại nhiều lợi ích:
- Xử lý biến outlier
- Xử lý mối quan hệ phi tuyến
- Tăng tính giải thích được của mô hình
- Chuẩn hóa các biến khác nhau

### Scorecard Scaling

Sau khi có mô hình dự đoán xác suất, điểm số được tính theo công thức:

```
Score = Offset + Factor × ln(odds)
```

Trong đó:
- Offset: Điểm cơ sở
- Factor: Hệ số chia tỷ lệ, thường tính từ Points to Double the Odds (PDO)
- odds: Tỷ lệ Good/Bad từ mô hình

## Các loại mô hình

### 1. Application Scorecard

**Mục đích**: Đánh giá rủi ro của khách hàng mới khi họ nộp đơn xin vay.

**Đầu vào chính**:
- **Đặc điểm nhân khẩu học**:
  - Tuổi: Biến liên tục, thường có mối quan hệ phi tuyến với rủi ro
  - Thu nhập: Được phân loại theo dải thu nhập hoặc log-transform
  - Nghề nghiệp: Biến phân loại, được mã hóa theo nhóm rủi ro
  - Trình độ học vấn: Được mã hóa thành numeric ordinal
  - Tình trạng hôn nhân: Phân loại theo mức độ ổn định

- **Lịch sử tín dụng**:
  - Điểm tín dụng từ cục tín dụng (nếu có)
  - Số lượng khoản vay hiện tại và đã thanh toán
  - Số lần trả nợ trễ hạn trong quá khứ 
  - Số lượng truy vấn tín dụng gần đây
  - Độ dài lịch sử tín dụng (tháng/năm)

- **Tình trạng tài chính**:
  - Tỷ lệ nợ/thu nhập (DTI): Tổng nợ chia cho thu nhập hàng tháng
  - Khả năng thanh toán: Thu nhập còn lại sau chi phí cần thiết
  - Tỷ lệ khoản vay/giá trị (LTV): Đối với các khoản vay có tài sản đảm bảo
  - Tài sản sở hữu: Nhà, xe và các tài sản giá trị khác

- **Ổn định việc làm**:
  - Thời gian làm việc tại công ty hiện tại (tháng/năm)
  - Loại hình công việc (toàn thời gian, bán thời gian, tự doanh)
  - Mức độ ổn định của ngành nghề 

**Phương pháp chi tiết**:
1. **Phân tích đơn biến**:
   - Tính IV (Information Value) cho từng biến: IV < 0.02 (không dự đoán), 0.02-0.1 (yếu), 0.1-0.3 (trung bình), >0.3 (mạnh)
   - Kiểm tra phân phối và mối tương quan với biến mục tiêu (default_flag)
   - Loại bỏ biến có giá trị IV thấp (< 0.02) hoặc có >95% giá trị giống nhau

2. **Fine & Coarse Classing**:
   - **Fine classing**: Chia biến liên tục thành 10-20 nhóm ban đầu
   - **Coarse classing**: Gộp các nhóm có tỷ lệ bad rate tương tự để có 3-7 nhóm cuối cùng
   - Kiểm tra tính đơn điệu: Đảm bảo mối quan hệ giữa bin và bad rate là đơn điệu
   - Kiểm tra tính phân biệt: Đảm bảo đủ số lượng mẫu và sự khác biệt giữa các bin

3. **Biến đổi WOE**:
   - Tính toán WOE cho mỗi bin: ln(%Good/%Bad)
   - Xử lý các bin trống hoặc toàn good/bad
   - Tạo bảng ánh xạ từ giá trị gốc sang WOE
   - Áp dụng biến đổi WOE cho tất cả các biến đã qua binning

4. **Mô hình XGBoost**:
   - Tham số chính: max_depth=3-5, learning_rate=0.01-0.1, n_estimators=100-500
   - Cross-validation: 5-10 fold để tránh overfitting
   - Regularization: alpha và lambda để kiểm soát phức tạp mô hình
   - Early stopping: Dừng huấn luyện khi hiệu suất không cải thiện

5. **Tạo scorecard**:
   - Chuẩn bị điểm cơ sở (basepoints): Điểm khi tất cả biến là trung bình
   - Tính điểm cho mỗi bin dựa trên công thức: Score = Factor × WOE + Offset/n (n là số biến)
   - Điều chỉnh thang điểm: Thường từ 300-850, với mốc 650-700 là ngưỡng chấp nhận được
   - Rounding: Làm tròn điểm để dễ hiểu và sử dụng

**Kết quả đầu ra chi tiết**:
- **Điểm số tín dụng**:
  - Điểm tổng hợp (300-850), càng cao càng ít rủi ro
  - Phân loại thành các nhóm: Rất tốt (750-850), Tốt (700-749), Trung bình (650-699), Yếu (600-649), Rất yếu (<600)

- **Xác suất vỡ nợ**:
  - Probability of Default (PD) trong khoảng thời gian cụ thể (thường 12 tháng)
  - Khoảng tin cậy của dự báo (95%)
  - So sánh với PD trung bình của phân khúc

- **Hồ sơ rủi ro chi tiết**:
  - Các yếu tố rủi ro chính: Top 3-5 biến đóng góp vào điểm số thấp
  - Các điểm mạnh: Top 3-5 biến đóng góp tích cực
  - Các biện pháp cải thiện cụ thể (nếu điểm thấp)
  - Dự báo hành vi theo phân khúc (dựa trên dữ liệu lịch sử tương tự)

- **Quyết định tín dụng tự động**:
  - Phê duyệt tự động (nếu điểm > ngưỡng cao)
  - Từ chối tự động (nếu điểm < ngưỡng thấp)
  - Đề xuất xem xét thủ công (nếu điểm nằm trong vùng xám)
  - Đề xuất giới hạn tín dụng ban đầu dựa trên điểm số

### 2. Behavior Scorecard

**Mục đích**: Đánh giá rủi ro của khách hàng hiện tại dựa trên hành vi của họ.

**Đầu vào chính chi tiết**:
- **Lịch sử thanh toán**:
  - Tỷ lệ thanh toán đúng hạn trong 6/12/24 tháng gần nhất
  - Số lần trễ hạn và mức độ nghiêm trọng (30+/60+/90+ ngày)
  - Thời gian từ lần trễ hạn gần nhất (recency)
  - Mẫu thanh toán (payment pattern): đúng hạn, thanh toán tối thiểu, thanh toán đầy đủ
  - Biến động trong thanh toán: độ lệch chuẩn của các khoản thanh toán

- **Mức sử dụng tín dụng**:
  - Tỷ lệ sử dụng hiện tại: số dư/hạn mức
  - Tỷ lệ sử dụng trung bình trong 3/6/12 tháng
  - Mức sử dụng tối đa đã đạt được
  - Tần suất vượt hạn mức (nếu được phép)
  - Biến động trong việc sử dụng: tăng/giảm theo thời gian

- **Dữ liệu giao dịch**:
  - Số lượng giao dịch hàng tháng
  - Giá trị trung bình của giao dịch
  - Phân loại chi tiêu (nếu có): thiết yếu vs không thiết yếu
  - Mô hình thời gian: cuối tuần vs ngày thường, đầu tháng vs cuối tháng
  - Thanh toán định kỳ vs không định kỳ

- **Thông tin tài khoản**:
  - Tuổi đời của tài khoản (tháng/năm)
  - Số sản phẩm tài chính đang sử dụng
  - Tổng giá trị quan hệ với tổ chức tài chính
  - Các hoạt động không thanh toán: cập nhật thông tin, yêu cầu tăng hạn mức

**Phương pháp chi tiết**:
1. **Kỹ thuật tạo đặc trưng hành vi**:
   - **Đặc trưng cửa sổ trượt (rolling window)**: Tính toán các chỉ số trong cửa sổ thời gian (3,6,12 tháng)
   - **Đặc trưng xu hướng (trend)**: Phát hiện mô hình tăng/giảm theo thời gian
   - **Đặc trưng tỷ lệ (ratio)**: So sánh hành vi hiện tại với trung bình quá khứ
   - **Đặc trưng độ biến động (volatility)**: Đo lường sự không ổn định trong hành vi
   - **Đặc trưng độ lệch (deviation)**: So sánh với phân khúc khách hàng tương tự

2. **Phân nhóm dữ liệu theo thời gian**:
   - Phân tách dữ liệu theo chu kỳ quan sát và kỳ hiệu suất
   - Áp dụng kỹ thuật "vintage analysis": phân tích theo thời gian đầu vào
   - Xử lý đặc biệt với khách hàng mới (< 6 tháng) vs. khách hàng lâu năm

3. **Kỹ thuật WOE động**:
   - Cập nhật giá trị WOE theo thời gian
   - Tạo WOE riêng cho các phân khúc khách hàng khác nhau
   - Áp dụng smoothing cho WOE để tránh biến động mạnh

4. **XGBoost với đặc trưng thời gian**:
   - Kết hợp model dự đoán và model trend
   - Sử dụng validation dựa trên thời gian (time-based validation)
   - Điều chỉnh trọng số cho dữ liệu gần đây hơn
   - Xử lý concept drift bằng cách cập nhật mô hình theo định kỳ

**Kết quả đầu ra chi tiết**:
- **Điểm số hành vi**:
  - Điểm tổng hợp (300-850) phản ánh rủi ro hiện tại
  - Biến động điểm theo thời gian (tăng/giảm so với kỳ trước)
  - So sánh với điểm trung bình của phân khúc
  - Dự báo điểm trong 3-6 tháng tới (dựa trên xu hướng)

- **Đề xuất giới hạn tín dụng**:
  - Giới hạn được đề xuất dựa trên điểm và thu nhập
  - Phần trăm thay đổi so với giới hạn hiện tại
  - Các mức giới hạn theo ngưỡng: tối thiểu, đề xuất, tối đa
  - Tính toán khả năng thanh toán (affordability) dự báo
  - Các điều kiện kèm theo (nếu có): yêu cầu bổ sung tài liệu, đặt cọc

- **Phân loại hành động**:
  - **Tăng giới hạn**: Mức tăng cụ thể và điều kiện
  - **Giảm giới hạn**: Mức giảm và lý do
  - **Giữ nguyên giới hạn**: Lý do và thời gian đánh giá lại
  - **Đóng tài khoản**: Trong trường hợp rủi ro cao
  - **Cảnh báo sớm**: Phát hiện dấu hiệu rủi ro trước khi xảy ra vỡ nợ
  - **Cross-selling**: Đề xuất sản phẩm phù hợp dựa trên hồ sơ rủi ro

- **Báo cáo chi tiết**:
  - Các yếu tố hành vi chính ảnh hưởng đến điểm số
  - Mẫu hành vi bất thường cần chú ý
  - So sánh với các khách hàng tương tự (peer comparison)
  - Hành vi cần cải thiện để nâng cao điểm số

### 3. Collections Scoring

**Mục đích**: Dự đoán khả năng khách hàng quá hạn sẽ tiếp tục trễ hạn trong tương lai.

**Đầu vào chính chi tiết**:
- **Thông tin quá hạn hiện tại**:
  - Số ngày quá hạn (DPD): Phân nhóm 1-30, 31-60, 61-90, 90+ ngày
  - Số tiền nợ quá hạn: Giá trị tuyệt đối và tỷ lệ trên tổng nợ
  - Giai đoạn chu kỳ nợ (cycle): lần đầu quá hạn hay tái diễn
  - Số lần quá hạn trong 6/12/24 tháng qua
  - Thời gian giữa các lần quá hạn

- **Lịch sử liên hệ và thu hồi**:
  - Số lần liên hệ đã thực hiện: gọi điện, tin nhắn, email, thư
  - Tỷ lệ phản hồi: số lần khách hàng phản hồi / số lần liên hệ
  - Kênh liên hệ hiệu quả nhất với khách hàng
  - Mô hình thời gian phản hồi: thời điểm trong ngày/tuần
  - Kết quả các lần liên hệ trước

- **Lịch sử cam kết thanh toán**:
  - Số lần khách hàng hứa trả nợ
  - Số lần thực hiện được cam kết (kept promises)
  - Số lần thất hứa (broken promises)
  - Tỷ lệ thực hiện cam kết: số cam kết thực hiện / tổng cam kết
  - Thời gian giữa cam kết và thực hiện

- **Đặc điểm tài chính hiện tại**:
  - Thu nhập hiện tại (nếu biết)
  - Tình trạng việc làm (có việc, thất nghiệp, giảm giờ làm)
  - Các khoản nợ khác đang có
  - Lý do khách hàng cung cấp cho việc trễ hạn
  - Khả năng thanh toán ước tính

**Phương pháp chi tiết**:
1. **Phân loại khách hàng theo mức độ rủi ro**:
   - **Phân loại RFM cho nợ**: Recency (thời gian từ lần thanh toán gần nhất), Frequency (tần suất trễ hạn), Monetary (giá trị nợ)
   - **Phân loại theo willingness vs. ability**: Phân biệt khách hàng không muốn trả vs. không có khả năng trả
   - **Phân loại theo mô hình hành vi**: Nhóm các khách hàng có mẫu hành vi tương tự
   - **Phân loại theo cycle**: Early stage (1-30 DPD), Mid stage (31-90 DPD), Late stage (90+ DPD)

2. **Mô hình Survival Analysis**:
   - **Cox Proportional Hazards**: Mô hình hóa thời gian đến khi khách hàng thanh toán
   - **Competing Risk Models**: Xem xét các kết quả cạnh tranh (thanh toán, tiếp tục trễ, tái cơ cấu)
   - **Parametric Survival Models**: Weibull, exponential để mô hình hóa thời gian phục hồi
   - **Time-dependent variables**: Kết hợp các biến thay đổi theo thời gian trong model

3. **XGBoost với tối ưu hóa thu hồi**:
   - **Learning to Rank**: Xếp hạng khách hàng theo khả năng thu hồi thành công
   - **Cost-sensitive learning**: Cân nhắc chi phí thu hồi khác nhau cho các nhóm khách hàng
   - **Optimization for NPV**: Tối ưu hóa giá trị hiện tại ròng của thu hồi
   - **Multi-stage models**: Mô hình riêng cho từng giai đoạn chu kỳ nợ
   - **Ensemble of strategies**: Kết hợp nhiều chiến lược thu hồi

4. **Tối ưu hóa chiến lược thu hồi**:
   - **Champion-challenger testing**: So sánh hiệu quả các chiến lược thu hồi khác nhau
   - **Treatment optimization**: Xác định chiến lược thu hồi tối ưu cho từng phân khúc
   - **Contact strategy optimization**: Tối ưu hóa thời điểm, kênh và tần suất liên hệ
   - **Settlement optimization**: Đề xuất mức giảm nợ tối ưu (nếu áp dụng)
   - **Queue optimization**: Sắp xếp thứ tự xử lý các tài khoản để tối đa hóa thu hồi

**Kết quả đầu ra chi tiết**:
- **Xác suất thanh toán và tiếp tục trễ hạn**:
  - Xác suất khách hàng thanh toán trong 7/15/30 ngày tới
  - Xác suất khách hàng tiếp tục trễ hạn và chuyển sang chu kỳ tiếp theo
  - Xác suất khách hàng sẽ không bao giờ thanh toán (write-off)
  - Các dấu hiệu nhận biết khách hàng có ý định trả nợ

- **Điểm ưu tiên thu hồi**:
  - Điểm số xếp hạng từ 1-1000 cho mức độ ưu tiên
  - Thứ tự ưu tiên trong danh sách thu hồi
  - Giá trị kỳ vọng thu hồi được (expected recovery amount)
  - Chi phí thu hồi ước tính và ROI dự kiến
  - Dự báo thời gian thu hồi

- **Phân nhóm chiến lược thu hồi**:
  - **Champion**: Khả năng thanh toán cao, ưu tiên cao nhất
  - **Negotiable**: Cần đàm phán về kế hoạch thanh toán
  - **Cure**: Khách hàng có khả năng tự khắc phục
  - **Restructure**: Cần tái cấu trúc khoản nợ
  - **Legal**: Cần theo đuổi biện pháp pháp lý
  - **Write-off**: Khả năng thu hồi thấp, không đáng đầu tư nỗ lực

- **Kế hoạch hành động chi tiết**:
  - Kênh liên hệ được đề xuất: điện thoại, SMS, email, thư, thăm nhà
  - Thời điểm tối ưu để liên hệ: ngày trong tuần, thời gian trong ngày
  - Kịch bản đàm phán được đề xuất: mức thanh toán tối thiểu, điều khoản
  - Đề xuất tái cơ cấu (nếu cần): giãn thời hạn, giảm lãi suất, giảm nợ gốc
  - Cảnh báo trường hợp có khả năng gian lận cao

### 4. Desertion Scoring

**Mục đích**: Dự đoán khả năng khách hàng sẽ rời bỏ sản phẩm/dịch vụ.

**Đầu vào chính chi tiết**:
- **Thông tin về kỳ hạn và hợp đồng**:
  - Thời gian còn lại đến kỳ hạn sản phẩm (tháng)
  - Loại hợp đồng: cố định, linh hoạt, tự động gia hạn
  - Điều khoản hợp đồng: phí phạt hủy sớm, điều kiện gia hạn
  - Lịch sử gia hạn trước đây: số lần gia hạn tự động
  - Đã từng cân nhắc hủy trước đây nhưng quyết định ở lại

- **Giá trị khách hàng tổng thể**:
  - Tổng giá trị quantitive: tổng số dư, số phí, lợi nhuận tạo ra
  - Thời gian quan hệ (tenure): số tháng/năm là khách hàng
  - Giá trị vòng đời khách hàng (LTV): giá trị dự kiến trong tương lai
  - Share of wallet: tỷ lệ sản phẩm tài chính của khách hàng tại tổ chức
  - Tăng trưởng giá trị: xu hướng tăng/giảm theo thời gian

- **Đa dạng sản phẩm và mối quan hệ**:
  - Số lượng sản phẩm tài chính đang sử dụng
  - Loại sản phẩm: vay, tiết kiệm, bảo hiểm, đầu tư
  - Sự đa dạng của danh mục sản phẩm
  - Mức độ liên kết giữa các sản phẩm
  - Thời gian kể từ lần mua sản phẩm mới nhất

- **Chỉ số tương tác và hài lòng**:
  - Điểm hài lòng khách hàng (NPS, CSAT)
  - Số lượng và mức độ nghiêm trọng của khiếu nại
  - Tần suất sử dụng dịch vụ: giao dịch, đăng nhập ứng dụng
  - Phản hồi từ khảo sát khách hàng
  - Tương tác với các chiến dịch marketing

- **Thông tin thị trường và cạnh tranh**:
  - Tỷ lệ từ bỏ trung bình của ngành
  - Các ưu đãi cạnh tranh đang diễn ra
  - Mức độ chênh lệch giá/lãi suất với đối thủ
  - Tỷ lệ khách hàng chuyển đến đối thủ cạnh tranh
  - Các yếu tố thị trường vĩ mô ảnh hưởng đến quyết định

**Phương pháp chi tiết**:
1. **Phân tích RFM nâng cao**:
   - **Recency**: Thời gian từ lần tương tác/giao dịch cuối, phân loại chi tiết theo kênh
   - **Frequency**: Tần suất tương tác theo kênh, xu hướng tăng/giảm, so sánh với trung bình
   - **Monetary**: Giá trị giao dịch, số dư, lợi nhuận tạo ra, thay đổi theo thời gian
   - **RFM Segmentation**: Phân khúc khách hàng dựa trên kết hợp các chỉ số RFM
   - **Temporal RFM**: Phân tích sự thay đổi của RFM theo thời gian

2. **Kỹ thuật phân khúc khách hàng nâng cao**:
   - **K-means clustering**: Nhóm khách hàng dựa trên đặc điểm tương tự
   - **Hierarchical clustering**: Tạo cây phân cấp các nhóm khách hàng
   - **Model-based clustering**: Sử dụng mô hình xác suất để phân nhóm
   - **Dynamic segmentation**: Phân khúc thay đổi theo thời gian
   - **Behavioral segmentation**: Phân khúc dựa trên mẫu hành vi
   - **Value-based segmentation**: Phân khúc theo giá trị và khả năng sinh lời

3. **XGBoost với dữ liệu không cân bằng**:
   - **Resampling techniques**: Oversampling (SMOTE), undersampling hoặc kết hợp
   - **Cost-sensitive learning**: Áp dụng trọng số khác nhau cho từng lớp
   - **Threshold optimization**: Tìm ngưỡng tối ưu để cân bằng precision và recall
   - **Focal Loss**: Tập trung vào các trường hợp khó phân loại
   - **Level-wise analysis**: Mô hình riêng cho từng phân khúc giá trị khách hàng
   - **Time-to-event modeling**: Dự đoán thời gian đến khi khách hàng rời bỏ

4. **Tối ưu hóa chi phí-lợi ích giữ chân**:
   - **Customer Lifetime Value (CLV)**: Tính toán chi tiết giá trị vòng đời khách hàng
   - **Churn Cost Calculation**: Chi phí mất khách hàng (thu nhập bị mất, chi phí thu hút khách hàng mới)
   - **Retention ROI Analysis**: Phân tích ROI của các chiến lược giữ chân khác nhau
   - **Optimization models**: Tối ưu hóa ngân sách giữ chân theo phân khúc
   - **A/B testing framework**: Khung thử nghiệm các chiến lược giữ chân
   - **Simulation models**: Mô phỏng tác động của các chiến lược giữ chân khác nhau

**Kết quả đầu ra chi tiết**:
- **Dự báo rủi ro từ bỏ**:
  - Xác suất khách hàng từ bỏ trong 1/3/6 tháng tới
  - Phân loại rủi ro: Rất cao (>70%), Cao (50-70%), Trung bình (30-50%), Thấp (<30%)
  - Xu hướng thay đổi rủi ro theo thời gian
  - Cảnh báo sớm khi rủi ro tăng đột biến
  - Thời gian dự kiến đến khi từ bỏ

- **Phân loại nguyên nhân từ bỏ**:
  - **Giá cả/Lãi suất**: Nguyên nhân liên quan đến chi phí
  - **Dịch vụ**: Vấn đề về chất lượng dịch vụ hoặc hỗ trợ
  - **Sản phẩm**: Thiếu tính năng hoặc không đáp ứng nhu cầu
  - **Cạnh tranh**: Ưu đãi hấp dẫn từ đối thủ
  - **Vòng đời**: Thay đổi nhu cầu tự nhiên của khách hàng
  - **Tài chính**: Khó khăn tài chính cá nhân của khách hàng

- **Chiến lược giữ chân được cá nhân hóa**:
  - **Ưu đãi giá/lãi suất**: Mức giảm giá/lãi suất được đề xuất dựa trên giá trị khách hàng
  - **Nâng cấp sản phẩm**: Đề xuất nâng cấp tính năng hoặc dịch vụ
  - **Tái gia hạn sớm**: Đề xuất gia hạn trước khi đến hạn với ưu đãi
  - **Cross-selling**: Đề xuất sản phẩm bổ sung để củng cố mối quan hệ
  - **Tiếp cận cá nhân**: Lịch trình liên hệ từ quản lý quan hệ khách hàng
  - **Chuyển đổi sản phẩm**: Đề xuất chuyển sang sản phẩm phù hợp hơn

- **Kế hoạch hành động chi tiết**:
  - Thời điểm tối ưu để can thiệp
  - Kênh liên lạc ưu tiên cho từng khách hàng
  - Thông điệp chính cần truyền đạt
  - Ngân sách tối đa cho hoạt động giữ chân
  - Các bước can thiệp theo thứ tự ưu tiên
  - KPI đo lường hiệu quả của chiến lược

- **Phân tích hiệu quả dự báo**:
  - Tỷ lệ chính xác của dự báo từ bỏ
  - ROI của chiến lược giữ chân
  - So sánh hiệu quả của các chiến lược khác nhau
  - Tỷ lệ giảm từ bỏ so với baseline
  - Bài học kinh nghiệm cho các chiến dịch tương lai

## Đánh giá mô hình

### Chỉ số đánh giá hiệu suất

1. **AUC-ROC (Area Under the Receiver Operating Characteristic)**:
   - Đo lường khả năng phân biệt của mô hình
   - Giá trị càng gần 1 càng tốt
   - Thường mong đợi > 0.75 cho mô hình tốt

2. **Gini Coefficient**:
   - Gini = 2 × AUC - 1
   - Đánh giá mức độ bất bình đẳng trong dự đoán
   - Thông dụng trong đánh giá mô hình tín dụng

3. **KS Statistic (Kolmogorov-Smirnov)**:
   - Đo lường sự khác biệt lớn nhất giữa phân phối cumulative của Good và Bad
   - Giá trị cao hơn là tốt hơn
   - Thường mong đợi > 40

4. **PSI (Population Stability Index)**:
   - Đánh giá độ ổn định của mô hình theo thời gian
   - PSI < 0.1: Không có thay đổi đáng kể
   - 0.1 < PSI < 0.25: Thay đổi vừa phải
   - PSI > 0.25: Thay đổi đáng kể, cần xem xét lại mô hình

### Phân tích độ nhạy và SHAP values

SHAP (SHapley Additive exPlanations) được sử dụng để giải thích mô hình và xác định tầm quan trọng của biến:
- Cung cấp hiểu biết cục bộ (local) và toàn cục (global) về mô hình
- Hiển thị tác động của từng biến đối với dự đoán
- Giúp xác định các biến quan trọng nhất trong mô hình

## Triển khai và Giám sát

### API Endpoints

Hệ thống cung cấp 4 API endpoints chính:

1. **/application-score/**: Chấm điểm đơn xin vay của khách hàng mới
2. **/behavior-score/**: Đánh giá hành vi và đề xuất giới hạn tín dụng
3. **/collections-prioritize/**: Xếp hạng ưu tiên thu hồi nợ
4. **/desertion-strategy/**: Tạo chiến lược giữ chân khách hàng

## Triển khai code trong project

Dưới đây là mối liên hệ giữa các phương pháp lý thuyết được mô tả và code thực tế trong project:

### 1. Tiền xử lý dữ liệu

**Mô tả**: Tiền xử lý dữ liệu là bước quan trọng đầu tiên, bao gồm xử lý giá trị thiếu, ngoại lai, và mã hóa biến phân loại.

**Code tương ứng**: 
```python
# src/data/preprocessor.py
class DataPreprocessor:
    # Phương thức xử lý giá trị thiếu
    def handle_missing_values(self, df):
        # ...
        
    # Phương thức xử lý giá trị ngoại lai
    def handle_outliers(self, df, cols=None, method='clip'):
        # ...
        
    # Phương thức mã hóa biến phân loại
    def encode_categorical(self, df, cols=None, method='one-hot'):
        # ...
```

### 2. Biến đổi WOE (Weight of Evidence)

**Mô tả**: Biến đổi các biến thành giá trị WOE để tăng khả năng dự đoán và tính giải thích.

**Code tương ứng**: 
```python
# src/features/woe_iv.py
class WoeIvTransformer:
    def fit(self, X, y):
        # Tính toán WOE và IV cho mỗi biến
        # ...
        
    def transform(self, X):
        # Biến đổi dữ liệu thành WOE
        # ...
        
    def _calculate_woe_iv(self, x, y):
        # Công thức tính WOE: ln(%good/%bad)
        # ...
```

### 3. Mô hình Application Scorecard

**Mô tả**: Xây dựng và huấn luyện mô hình đánh giá khách hàng mới.

**Code tương ứng**: 
```python
# src/models/application_scorecard.py
class ApplicationScorecard(BaseXGBoostModel):
    def process_and_train(self):
        # Tiền xử lý và huấn luyện mô hình
        # ...
        
    def get_application_risk_profile(self, customer_data):
        # Tạo hồ sơ rủi ro chi tiết
        # ...
```

### 4. Mô hình Behavior Scorecard

**Mô tả**: Xây dựng và huấn luyện mô hình đánh giá hành vi khách hàng hiện tại.

**Code tương ứng**: 
```python
# src/models/behavior_scorecard.py
class BehaviorScorecard(BaseXGBoostModel):
    def _create_behavioral_features(self, df):
        # Tạo đặc trưng hành vi từ dữ liệu gốc
        # ...
        
    def recommend_credit_limit(self, customer_data, current_limit):
        # Đề xuất giới hạn tín dụng mới
        # ...
```

### 5. Mô hình Collections Scoring

**Mô tả**: Xây dựng và huấn luyện mô hình đánh giá khả năng tiếp tục trễ hạn.

**Code tương ứng**: 
```python
# src/models/collections_scoring.py
class CollectionsScoring(BaseXGBoostModel):
    def prioritize_collections(self, delinquent_accounts):
        # Xếp hạng ưu tiên các tài khoản trễ hạn
        # Tính toán ROI thu hồi
        # ...
```

### 6. Mô hình Desertion Scoring

**Mô tả**: Xây dựng và huấn luyện mô hình dự đoán khả năng khách hàng từ bỏ.

**Code tương ứng**: 
```python
# src/models/desertion_scoring.py
class DesertionScoring(BaseXGBoostModel):
    def _segment_customers(self, X):
        # Phân khúc khách hàng dựa trên RFM
        # ...
        
    def create_retention_strategy(self, customers_data):
        # Tạo chiến lược giữ chân cá nhân hóa
        # ...
```

### 7. Xây dựng Scorecard

**Mô tả**: Chuyển đổi mô hình machine learning thành bảng điểm dễ hiểu và triển khai.

**Code tương ứng**: 
```python
# src/scorecard/scorecard_builder.py
class ScorecardBuilder:
    def build_scorecard_from_model(self, model, woe_transformer):
        # Tạo bảng điểm từ mô hình và WOE transformer
        # ...
        
    def calculate_score(self, X):
        # Tính điểm từ bảng điểm đã xây dựng
        # ...
```

### 8. Đánh giá mô hình

**Mô tả**: Đánh giá hiệu suất mô hình bằng các chỉ số khác nhau.

**Code tương ứng**: 
```python
# src/utils/metrics.py
def calculate_metrics(y_true, y_pred_proba, threshold=0.5):
    # Tính AUC, Gini, KS, và các chỉ số khác
    # ...
    
def calculate_psi(expected, actual, buckets=10):
    # Tính PSI để đánh giá độ ổn định của mô hình
    # ...
```

### 9. API Endpoints

**Mô tả**: Triển khai các mô hình thông qua REST API.

**Code tương ứng**: 
```python
# api/main.py
@app.post("/application-score/")
def get_application_score(data: ApplicationData):
    # Xử lý yêu cầu API và trả về kết quả đánh giá
    # ...

@app.post("/behavior-score/")
def get_behavior_score(data: BehaviorData):
    # ...

@app.post("/collections-prioritize/")
def prioritize_collection(data_list: list[CollectionsData]):
    # ...

@app.post("/desertion-strategy/")
def get_retention_strategy(data_list: list[DesertionData]):
    # ...
```

### 10. Mô hình cơ sở (Base Model)

**Mô tả**: Lớp cơ sở cho tất cả các loại mô hình, cung cấp các chức năng chung.

**Code tương ứng**: 
```python
# src/models/base_model.py
class BaseXGBoostModel:
    def prepare_data(self, data):
        # Chuẩn bị dữ liệu cho mô hình
        # ...
        
    def transform_features(self, X_train, X_test, y_train):
        # Biến đổi đặc trưng sang WOE
        # ...
        
    def train(self, X_train_woe, y_train, X_test_woe=None, y_test=None):
        # Huấn luyện mô hình XGBoost
        # ...
        
    def evaluate(self, X_test, y_test):
        # Đánh giá mô hình
        # ...
```

Mối liên hệ giữa lý thuyết và code cho thấy cách thức cụ thể để triển khai các phương pháp đánh giá rủi ro tín dụng hiện đại sử dụng XGBoost và phương pháp scorecard. Mỗi component trong hệ thống đều có vai trò riêng biệt nhưng liên kết chặt chẽ với nhau để tạo nên một platform toàn diện.

### Giám sát hiệu suất

Sau khi triển khai, mô hình được giám sát thông qua:
- Theo dõi PSI định kỳ để phát hiện concept drift
- Phân tích backtest để đánh giá hiệu suất trên dữ liệu mới
- Theo dõi phân phối điểm và tỷ lệ lỗi theo thời gian
- Đối chiếu tỷ lệ vỡ nợ thực tế với dự đoán

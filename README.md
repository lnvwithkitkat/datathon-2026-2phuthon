# datathon-2026-2phuthon

Bài làm nhóm Datathon 2026
🚀 Giới thiệu
Dự án tập trung vào việc dự báo doanh thu và giá vốn (Revenue & COGS) cho chuỗi bán lẻ tại Việt Nam. Cách tiếp cận của nhóm kết hợp giữa phân tích kỹ thuật và hiểu biết về đặc thù thị trường nội địa.

📁 Cấu trúc thư mục
reports/: Báo cáo khoa học 4 trang và hình ảnh trực quan.

notebooks/: Lời giải phần trắc nghiệm và phân tích EDA.

scripts/: Mã nguồn mô hình XGBoost V5 (Log-transform, Lễ Tết).

submissions/: File kết quả dự báo 548 ngày.

💡 Điểm nổi bật trong mô hình
Xử lý Lễ Tết: Neo dữ liệu theo ngày Tết Nguyên Đán thay vì ngày dương lịch cố định.

Hiệu ứng tâm lý: Tích hợp biến "Ngày nhận lương" và "Ngày đôi" (Double Days).

Kỹ thuật: Sử dụng Log-transformation để xử lý xu hướng tăng trưởng và mã hóa chu kỳ lượng giác (sin/cos).

🛠 Hướng dẫn chạy code
Cài đặt thư viện: pip install -r requirements.txt

Chạy dự báo: python scripts/3_XGBoost_V5_Model.py

👥 Phân công nhiệm vụ
Thành viên A: Xây dựng Dashboard Power BI và DAX logic.

Thành viên B: Phát triển mô hình Machine Learning và Feature Engineering.

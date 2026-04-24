# 📊 Dự báo Doanh thu Bán lẻ - Datathon 2026

## 🚀 Giới thiệu
Dự án tập trung vào việc dự báo doanh thu và giá vốn (Revenue & COGS) cho chuỗi bán lẻ tại Việt Nam. Cách tiếp cận của nhóm kết hợp giữa phân tích kỹ thuật và hiểu biết về đặc thù thị trường nội địa (Lễ Tết, tâm lý mua sắm).

---

## 📁 Cấu trúc thư mục

```text
datathon-2026-retail-forecasting/
├── README.md               <- Trang giới thiệu tổng quan (Linh hồn dự án)
├── requirements.txt        <- Danh sách các thư viện Python (xgboost, pandas,...)
├── reports/                <- Chứa báo cáo PDF 4 trang và các ảnh Dashboard
│   ├── Final_Report.pdf
│   └── Dashboard_Screenshots/
├── notebooks/              <- Chứa các file phân tích
│   ├── 1_Multiple_Choice.ipynb
│   └── 2_EDA_Analysis.ipynb
├── scripts/                <- Chứa mã nguồn dự báo chính
│   └── 3_XGBoost_V5_Model.py
├── submissions/            <- Chứa file kết quả nộp Kaggle
│   └── xgboost_v5_tet_log.csv
└── data/                   <- (Tùy chọn) Chứa file promotions.csv
```

## Cách làm

1. Install dependencies

```bash
pip install -r requirements.txt
```

2. Train baseline models (Revenue + COGS)

```bash
python -m src.models.train
```

This writes `outputs/models/model_package.joblib`.

3. Generate submission

```bash
python -m src.models.predict
```

This writes `outputs/submissions/submission.csv`.

## 🛫 Phân công công việc

- Thành viên 1: Viết code .ipynb để đọc dữ liệu và trả lời các câu hỏi trắc nghiệm
- Thành viên 2: Xây dựng PowerBI để làm EDA
- Thành viên 3: Đọc insight từ PBI để viết LaTex (phối hợp với thành viên 2)
- Thành viên 4: Xây dựng code dự đoán

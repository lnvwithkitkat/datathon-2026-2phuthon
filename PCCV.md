# Phân công Công việc – DATATHON 2026 Vòng 1

**Đội:** 2phuthon (4 thành viên)

---

## 1. Mục tiêu tổng thể (bám theo đề thi)

| Phần | Nội dung | Điểm | Sản phẩm |
|---|---|---|---|
| 1 | 10 câu trắc nghiệm (Q1–Q10) | 20 | Đáp án trong Form nộp bài |
| 2 | EDA + Visualization, đạt mức **Prescriptive** | 60 | Phần Part 2 trong Report (NeurIPS, ≤4 trang) |
| 3 | Sales Forecasting (Revenue, 2023-01-01 → 2024-07-01) | 20 | `submission.csv` trên Kaggle + mục Part 3 + SHAP/FI |
| — | Checklist nộp bài | — | GitHub repo public + README + ảnh thẻ SV + tick finalist |

**Ràng buộc Part 3 (bắt buộc – loại bài nếu vi phạm):**
1. Không dùng Revenue/COGS từ tập test làm feature.
2. Không dùng dữ liệu ngoài.
3. Có source code, tái lập được (random seed + requirements).

---

## 2. Phân công theo vai trò

### TV1 – Modeling & Pipeline Lead
- Setup repo, môi trường, cấu trúc code.
- Module đọc – làm sạch – merge 15 file CSV.
- Feature engineering (calendar, lag/rolling, promo, traffic, inventory signal).
- Xây, tune, validate mô hình forecasting (time-series CV).
- SHAP / Feature importance / Partial Dependence cho mục Explainability.
- Viết mục **Part 3** trong Report.
- Kaggle submission.

### TV2 – EDA, Visualization & Report Lead
- Descriptive → Diagnostic → Predictive → Prescriptive analyses.
- Bộ biểu đồ (matplotlib/plotly) có tiêu đề, trục, chú thích chuẩn.
- Business insights + actionable recommendations (định lượng).
- Storytelling / mạch trình bày của Part 2.
- Chủ biên Report NeurIPS (≤4 trang, tiếng Anh), tích hợp nội dung hai phần.
- Chuẩn bị Form nộp bài + ảnh thẻ SV.

### Dùng chung
- Cả hai cùng giải 10 câu MCQ (mỗi người 5 câu, rồi cross-check).
- Cross-review code & report trước hạn 1 ngày.

---

## 3. Timeline chi tiết theo ngày (19/04 – 29/04/2026)

| # | Ngày | Thứ | TV1 | TV2 | Milestone |
|---|---|---|---|---|---|
| 1 | 19/04 | CN | Khởi tạo repo, `requirements.txt`, folder structure (`data/`, `notebooks/`, `src/`, `reports/`). Tải & kiểm tra 15 CSV. | Đọc kỹ đề, dựng notebook `00_schema_overview.ipynb`: schema, dtypes, null %, cardinality, foreign keys. | Repo + data ready |
| 2 | 20/04 | T2 | Module `src/data_loader.py` (join products/orders/order_items/promotions/geography). Giải MCQ **Q1, Q5, Q8, Q10**. | Descriptive EDA ban đầu: revenue theo ngày/tháng/năm, top category, top region. Giải MCQ **Q2, Q3, Q6, Q9**. | MCQ xong draft |
| 3 | 21/04 | T3 | Giải MCQ **Q4, Q7**. Baseline forecasting: naive / seasonal naive / Prophet → lưu metric MAE, RMSE, R². | Diagnostic EDA: cohort khách hàng (signup → LTV), return reasons theo category/size, channel hiệu quả. | Baseline model + diagnostic insights |
| 4 | 22/04 | T4 | Feature engineering: calendar (dow, month, holiday VN, EOQ), lag 7/14/28/365, rolling mean/std, promo active flag, web-traffic lag, inventory stockout rate. | Predictive analyses: seasonality decomposition, leading indicators (traffic → revenue lag), forecast simple trend cho category. | FE set v1 |
| 5 | 23/04 | T5 | Time-series CV (expanding window). Train LightGBM / XGBoost / CatBoost. Ghi log experiments. | Prescriptive analyses: gợi ý tồn kho (reorder), ROI khuyến mãi theo channel, segment khách hàng đáng giữ. Định lượng tradeoff. | Ensemble candidate |
| 6 | 24/04 | T6 | Hyperparameter tuning (Optuna). Ensemble / stacking. Kiểm tra leakage (không dùng Revenue/COGS test). | Hoàn thiện bộ figure bản final (≥8 biểu đồ chất lượng xuất bản). Viết caption + key findings. | Model chốt + figures chốt |
| 7 | 25/04 | T7 | SHAP global + local, Feature Importance, PDP cho 3–5 feature quan trọng. Viết business interpretation. | Draft Part 2 trong Report (NeurIPS LaTeX): story arc 4 cấp độ, chèn figure, số liệu. | Explainability + Part 2 draft |
| 8 | 26/04 | CN | Submit Kaggle lần 1–N, điều chỉnh theo public LB. Viết Part 3 draft (method, CV, results, SHAP). | Edit Part 2, đảm bảo mỗi visualization có: mô tả → finding → business implication. | Kaggle có điểm + Report draft đủ phần |
| 9 | 27/04 | T2 | Tích hợp Part 3 vào file LaTeX chính. Tối ưu submission cuối. | Ghép Part 1 (MCQ summary) + Part 2 + Part 3 thành báo cáo liền mạch. Kiểm tra giới hạn 4 trang. | Report v1 hoàn chỉnh |
| 10 | 28/04 | T3 | Reproducibility: đặt seed, đóng `requirements.txt`, viết README (cấu trúc + cách chạy). Cross-review MCQ. | Proofread report (EN), chỉnh figure quality, fix references. Chuẩn bị ảnh thẻ SV. | Release candidate |
| 11 | 29/04 | T4 | Kaggle submission cuối (chọn 2 bản tốt nhất). Push commit final, tag `v1.0`. | Upload PDF, điền Form (MCQ, link GitHub, link Kaggle, ảnh thẻ, tick finalist 23/05). | **NỘP BÀI** |

---

## 4. Tiêu chí hoàn thành (DoD) theo Milestone

- **Data ready (D1):** 15 CSV load không lỗi; có bảng null %/key check.
- **MCQ xong (D3):** 10 đáp án + notebook tính từ dữ liệu, có cross-check chéo giữa 2 TV.
- **FE v1 (D4):** ≥20 feature; không có feature nào leak từ test.
- **Model chốt (D6):** Score CV ổn định, MAE/RMSE/R² log rõ; chênh CV vs LB ≤ 10%.
- **Part 2 draft (D7):** Có đủ 4 cấp độ (Descriptive, Diagnostic, Predictive, Prescriptive) với số liệu.
- **Report v1 (D9):** ≤4 trang, đúng template NeurIPS, link GitHub + Kaggle.
- **Release candidate (D10):** Chạy lại end-to-end từ clone repo → `submission.csv` không lỗi.
- **Nộp bài (D11):** Form submit trước 23:59 ngày 29/04/2026.

---

## 5. Rủi ro & Giảm thiểu

| Rủi ro | Giảm thiểu |
|---|---|
| Leakage từ tập test | Checklist code review D6; chỉ dùng Revenue/COGS cho train; kiểm tra date cutoff |
| Overfit public LB Kaggle | Giữ 2 submission: best CV + best LB; báo cáo CV score |
| Report vượt 4 trang | Viết trực tiếp trên NeurIPS template từ D7; giới hạn figure 4–6 trong body, phần còn lại vào Appendix |
| Không tái lập | Seed + `requirements.txt` + README + chạy thử từ clone D10 |
| Thiếu ảnh thẻ / finalist | TV2 thu thập từ D2, upload D11 |

---

## 6. Liên kết

- **Kaggle:** <https://www.kaggle.com/competitions/datathon-2026-round-1>
- **NeurIPS template:** <https://neurips.cc/Conferences/2025/CallForPapers>
- **GitHub repo:** <https://github.com/nhatvu205/datathon2026-attention-seekers>
- **Finalist (on-site VinUni Hà Nội):** 23/05/2026 – cần ít nhất 1 TV xác nhận tham dự.

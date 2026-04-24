# datathon-2026-2phuthon

Datathon 2026 — **The Gridbreakers**: Revenue Forecasting for an E-commerce Fashion Company in Vietnam.

## Project goal

- Build a robust time-series model to forecast daily **Revenue** and **COGS**.
- Produce a submission file matching `data/raw/sample_submission.csv` format.
- Keep the workflow reproducible and avoid data leakage.

## Structure

## Quickstart

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

## Notes

- In the current dataset snapshot, `sales.csv` ends at **2022-12-31**, while `sample_submission.csv` contains future dates (2023+).
- The provided baseline uses **calendar features + lag/rolling features** and forecasts future dates **autoregressively**.

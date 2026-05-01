# Task 3 Forecasting Pipeline

The pipeline follows the competition diagram: EDA Preprocessed -> Feature Engineering -> Base Models -> Time Series Data Preparing -> Ensemble -> Calibration -> Prediction.

## 1. EDA Preprocessed

`00_pipeline_audit.ipynb` checks the raw CSV files, verifies that `sample_submission.csv` is loaded only with `Date`, and reconciles `sales.csv` against `orders.csv`, `order_items.csv`, and `products.csv`.

`01_eda_preprocessed_feature_engineering.ipynb` writes raw summaries for yearly trend, monthly seasonality, and Covid/recovery regimes. These reports are built only from `Raw Data/*.csv`.

## 2. Feature Engineering

The feature store is rebuilt from raw data:

- Calendar and cyclical features.
- Tet windows, Black Friday, date-equals-month shopping flags, payday windows, and fashion retail seasons.
- Promotion intensity and projected recurring promotions inferred from historical `promotions.csv`.
- Historical seasonal profiles for orders, payments, item mix, returns, web traffic, and inventory. These are profiles, not same-day future operational values.
- Shifted target lags and rolling statistics for Revenue, COGS, and COGS/Revenue ratio.

Same-day `COGS_ratio` is explicitly excluded from model features. Test artifacts do not contain `Revenue`, `COGS`, or `COGS_ratio`.

## 3. Base Models

`02_baseline_models.ipynb` evaluates:

- Seasonal naive.
- Raw-derived recovery seasonal baseline.
- Ridge log baseline.

The recovery baseline uses a raw-only anchor: the average of mature pre-Covid demand and the latest observed recovery year. It does not use public leaderboard constants.

## 4. Time Series Data Preparing

`03_timeseries_models_ensemble_calibration.ipynb` uses rolling-origin folds. For validation/test rows, target-history features are overwritten with profiles fit only on data available before the cutoff. This prevents validation from knowing future target lags that would not exist during the 2023-2024 forecast.

## 5. Advanced Models

The model bench includes Ridge and optional LightGBM, XGBoost, and CatBoost if installed. Model weights are based on out-of-fold MAE. A raw-derived seasonal recovery candidate is always included to prevent the final forecast from collapsing to a flat low scale.

## 6. Ensemble and Calibration

Revenue is forecast first. The final Revenue forecast blends model predictions with the raw-derived recovery seasonal shape and rescales to the raw-derived recovery anchor.

COGS is forecast through a COGS/Revenue ratio model:

- Seasonal ratio from historical raw sales.
- Ridge ratio model using leakage-safe features.
- Final ratio is clipped by historical train quantiles.

## 7. Explainability

Notebook 03 trains compact explanation models after final prediction construction and saves SHAP-style reports:

- Global feature importance for Revenue and COGS/Revenue ratio.
- Forecast-period feature importance for 2023-2024.
- Business-family importance: lag momentum, Tet timing, promotions, fashion seasonality, traffic profile, inventory profile, payment risk, return/refund behavior, and margin history.
- A markdown report with next-improvement suggestions.

If SHAP is unavailable in the local environment, the notebook falls back to native model importance so the pipeline still runs.

## 8. Prediction

The final dataframe is validated before export:

- 548 rows.
- Columns exactly `Date,Revenue,COGS`.
- Date order exactly matches `Raw Data/sample_submission.csv`.
- No missing or negative values.

Export is manual. Set `WRITE_SUBMISSION = True` in the final cell of notebook 03 to write `outputs/submission.csv`.

## Excluded Methods

The final workflow excludes:

- Sample submission Revenue/COGS as features.
- Old submission blending.
- Leaderboard-derived target means or monthly corrections.
- Kaggle API automation or tokens.
- Runtime dependency on helper artifacts.

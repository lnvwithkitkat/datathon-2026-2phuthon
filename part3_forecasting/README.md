# Part 3 - Revenue and COGS Forecasting

The notebook workflow is the source of truth for Task 3.

## Run Order

From the repository root, open Jupyter Lab and run:

```text
part3_forecasting/notebooks/00_pipeline_audit.ipynb
part3_forecasting/notebooks/01_eda_preprocessed_feature_engineering.ipynb
part3_forecasting/notebooks/02_baseline_models.ipynb
part3_forecasting/notebooks/03_timeseries_models_ensemble_calibration.ipynb
```

The notebooks read raw data from:

```text
../Raw Data
```

relative to this folder, and write runtime artifacts to:

```text
part3_forecasting/artifacts/
part3_forecasting/reports/
part3_forecasting/outputs/
```

## Submission

Notebook 03 validates and writes:

```text
part3_forecasting/outputs/submission.csv
```

The included `submission.csv` has 548 rows with exact columns `Date,Revenue,COGS`, matching the row order of `Raw Data/sample_submission.csv`.

## Compliance

- Runtime model inputs come from `Raw Data/*.csv`.
- `sample_submission.csv` is loaded only for dates, order, and schema validation.
- Public calendar features such as Tet, Black Friday, and sale-event flags are feature engineering choices, not external target data.
- No old submission, sample target value, helper output artifact, Kaggle token, or leaderboard-derived target scale is used as model input.

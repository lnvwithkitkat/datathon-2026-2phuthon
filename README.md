# DATATHON 2026 Round 1 Submission

This repository contains the complete source package for all three Round 1 tasks.

## Repository Structure

```text
datathon_2026_round1_github_submission/
  Raw Data/                    # Provided competition data files
  docs/
    de-thi-vong-1.pdf          # Competition statement
  part1_mcq/
    DATATHON_PART_1.ipynb      # MCQ answers computed from raw CSV files
  part2_data_visualization/
    data-visualization-skills/ # EDA, dashboards, scripts, figures, and documentation
  part3_forecasting/
    notebooks/                 # Forecasting notebooks, run 00 -> 03
    outputs/submission.csv     # Final Kaggle submission file
    pipeline.md                # Forecasting pipeline explanation
  requirements.txt
  README.md
```

## Install

From the repository root:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
jupyter lab
```

If you already have a compatible Python environment, installing `requirements.txt` is enough.

## Part 1: Multiple Choice Questions

Open and run:

```text
part1_mcq/DATATHON_PART_1.ipynb
```

The notebook loads CSV files from `../Raw Data` using DuckDB and computes the 10 MCQ answers directly from the provided data.

## Part 2: Data Visualization and Analysis

The EDA and visualization package is in:

```text
part2_data_visualization/data-visualization-skills/
```

This folder contains the cleaned GitHub-safe subset of the visualization work: documentation, scripts, screenshots, PowerBI/Tableau build notes, and figure assets. Large generated exports and dashboard binaries over 100 MB were intentionally excluded so the repository can be pushed to GitHub without Git LFS.

## Part 3: Forecasting

Run the forecasting notebooks in order:

```text
part3_forecasting/notebooks/00_pipeline_audit.ipynb
part3_forecasting/notebooks/01_eda_preprocessed_feature_engineering.ipynb
part3_forecasting/notebooks/02_baseline_models.ipynb
part3_forecasting/notebooks/03_timeseries_models_ensemble_calibration.ipynb
```

Notebook 03 is the final submission generator. It validates the output against `Raw Data/sample_submission.csv` and writes:

```text
part3_forecasting/outputs/submission.csv
```

The included submission file has Kaggle score reference `669191.89991` as reported after the final run.

## Compliance Notes

- All model features are generated from the provided `Raw Data/*.csv` files.
- `sample_submission.csv` is used only for `Date`, row order, and schema validation.
- The forecasting notebooks include rolling-origin validation, leakage checks, model comparison, COGS ratio handling, and SHAP/feature-importance explainability.
- No helper output artifact, old submission blend, Kaggle token, or leaderboard-derived target value is used as model input.

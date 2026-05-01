# File Inventory

This inventory separates files into commit-safe assets, generated reproducible assets, and large local-only assets.

## Project Root

| Path | Purpose | GitHub status |
|---|---|---|
| `README.md` | GitHub-facing project overview | Commit |
| `.gitignore` | Project-local GitHub safety rules | Commit |
| `scripts/` | Reproducible data prep, package, and figure generation scripts | Commit |
| `docs/` | Project documentation and deliverable assets | Commit selected files |

## Scripts

| File | Purpose |
|---|---|
| `scripts/prepare_tableau_data.py` | Builds validated analytical CSV extracts from raw source data |
| `scripts/build_tableau_fileout.py` | Builds the Tableau file-out support package |
| `scripts/generate_preview_exports.py` | Creates non-Tableau preview screenshots and PDF |
| `scripts/generate_latex_figure_pack.py` | Creates the final high-resolution LaTeX-ready rendered figures |

## Core Documentation

| File | Purpose |
|---|---|
| `docs/project-brief.md` | Project context and selected scope |
| `docs/project-plan.md` | Implementation plan |
| `docs/data-preparation.md` | Prepared data contract |
| `docs/data-preparation-validation.md` | Validation checks and row counts |
| `docs/orders-enriched-null-policy.md` | Expected null policy for sparse return/review/shipment fields |
| `docs/order-items-enriched-null-policy.md` | Expected null policy for sparse promotion/return/review/shipment fields |
| `docs/erd.md` | Entity relationship notes |
| `docs/visualization.md` | Dashboard page and interaction design |
| `docs/dashboard-story.md` | CEO narrative and rubric mapping |
| `docs/powerbi-rebuild-guide.md` | Manual Power BI rebuild guide |
| `docs/github-submission.md` | Manual GitHub submission guide |
| `docs/debug-report.md` | Tableau/Power BI/debug findings and final rendered-image path |
| `docs/publish.md` | File-out and export status |
| `docs/document-management.md` | Project documentation index |

## Final Rendered Deliverables

Commit these files. They are small, verified, and useful for LaTeX.

Folder:

```text
docs/assets/figures/latex/
```

| File | Purpose |
|---|---|
| `01_executive_scorecard.png` | Executive overview figure |
| `02_predictive_growth_seasonality.png` | Predictive EDA and seasonality figure |
| `03_profit_promotion_leakage.png` | Promotion margin leakage figure |
| `04_payment_channel_risk.png` | Payment/channel risk figure |
| `05_returns_fulfillment_cx.png` | Return, review, and fulfillment figure |
| `06_inventory_quadrant_actions.png` | Inventory action quadrant figure |
| `07_data_model_validation.png` | Data model and validation proof figure |
| `08_prescriptive_action_roadmap.png` | Prescriptive roadmap figure |
| `VinDatathon_Task2_LaTeX_Figure_Pack.pdf` | 8-page PDF contact sheet |
| `VinDatathon_Task2_LaTeX_Figure_Pack.zip` | Lightweight final figure bundle |
| `figure_manifest.json` | Dimensions, hashes, source files, guardrails |
| `latex_include_figures.tex` | Ready-to-use LaTeX snippets |

Verification status:

- PNG count: 8.
- PNG dimensions: `3200x1800`.
- PNG DPI metadata: approximately `300x300`.
- PDF page count: 8.
- ZIP entries: 11.

## Prepared Extracts

Folder:

```text
docs/assets/exports/tableau/
```

Commit-safe small extracts and metadata:

| File | Size | GitHub status |
|---|---:|---|
| `build_summary.json` | 1 KB | Commit |
| `dashboard_kpis.csv` | 1 KB | Commit |
| `source_manifest.csv` | 1 KB | Commit |
| `seasonality_indices.csv` | 2 KB | Commit |
| `recommendations.csv` | 6 KB | Commit |
| `predictive_signals.csv` | 20 KB | Commit |
| `data_dictionary.csv` | 36 KB | Commit |
| `growth_forecast_monthly.csv` | 40 KB | Commit |
| `orders_enriched_missingness.csv` | 10 KB | Commit |
| `order_items_enriched_missingness.csv` | 11 KB | Commit |
| `daily_kpi.csv` | 1.7 MB | Commit |
| `inventory_monthly.csv` | 15.0 MB | Optional commit |

Ignored large generated extracts:

| File | Size | Reason |
|---|---:|---|
| `orders_enriched.csv` | 280.9 MB | Generated; exceeds GitHub normal file limit |
| `order_items_enriched.csv` | 323.1 MB | Generated; exceeds GitHub normal file limit |

These ignored extracts can be regenerated with:

```powershell
python projects/vindatathon-2026-task2-tableau/scripts/prepare_tableau_data.py
```

Use the bundled Python path in Codex if normal `python` is not available.

## Tableau Assets

Folder:

```text
docs/assets/workbook/
```

Commit these:

- `README_TABLEAU_BUILD.md`
- `tableau_calculated_fields.md`
- `tableau_dashboard_blueprint.json`
- `twbx_package_manifest.json`

Ignored by default:

- `VinDatathon_Task2_Tableau_Fileout_Package.zip` because it is about 141.7 MB.
- Any future `.twbx` file unless you use Git LFS or a GitHub Release.

## Power BI Assets

Folder:

```text
docs/assets/powerbi/
```

This folder is reserved for manually created Power BI files. Its README should be committed. `.pbix` and `.pbit` files are ignored by default because they are binary and can become too large.

## Preview Screenshots

Folder:

```text
docs/assets/screenshots/
```

These are non-Tableau preview exports generated before the final LaTeX pack. They are small and can be committed, but the preferred final figures are in:

```text
docs/assets/figures/latex/
```

## Removed During Cleanup

Removed generated Tableau sample-inspection artifacts:

```text
docs/assets/workbook/_inspect_world_indicators/
```

That folder contained Tableau sample workbook inspection files and was unrelated to VinDatathon.

# Publish Status

## Ready

- Project workspace created.
- Tableau-ready CSV extracts generated.
- Data dictionary generated.
- ERD notes written.
- Dashboard blueprint written.
- Tableau calculated fields written.
- File-out package generated.
- Data validation passed for key integrity and revenue reconciliation.
- LaTeX-ready rendered figure pack generated and verified.
- Power BI rebuild guide generated.
- GitHub submission guide and file inventory generated.
- Project-local `.gitignore` added to protect oversized generated outputs.

## Current Tableau Debug Result

Tableau Desktop 2026.1 launches in the GUI and its logs show a cached free-edition lease. However, automated workbook rendering/export from this environment is still blocked:

```text
tableau.com -h -> Unable to verify license. Please activate the product.
```

The GUI path is available, but the Desktop command-line path is not a supported export automation surface here. No `tabcmd` executable is installed, and there is no Tableau Cloud/Server view URL configured for server-side export.

## Generated Preview Exports

The following files are generated from the prepared data as review previews only; they are not Tableau-rendered exports:

- `docs/assets/screenshots/01_executive_overview.png`
- `docs/assets/screenshots/02_growth_forecast_seasonality.png`
- `docs/assets/screenshots/03_profit_promotion_leakage.png`
- `docs/assets/screenshots/04_customer_channel_payment_risk.png`
- `docs/assets/screenshots/05_returns_reviews_fulfillment.png`
- `docs/assets/screenshots/06_inventory_actions.png`
- `docs/assets/screenshots/VinDatathon_Task2_Dashboard_Preview_NON_TABLEAU.pdf`

## Next Manual Step For Final Tableau File-Out

In Tableau Desktop GUI:

1. Open Tableau Desktop 2026.1.
2. Connect to CSVs from `docs/assets/exports/tableau/`.
3. Build the six dashboards following `docs/assets/workbook/tableau_dashboard_blueprint.json`.
4. Add calculated fields from `docs/assets/workbook/tableau_calculated_fields.md`.
5. Configure dashboard actions from `docs/visualization.md`.
6. Save as `docs/assets/workbook/VinDatathon_Task2_Tableau.twbx`.
7. Export screenshots or PDF into `docs/assets/screenshots/`.

## Current Recommended Submission Path

For the current LaTeX/report workflow, use the rendered figure pack instead of waiting for Tableau or Power BI binary exports:

- `docs/assets/figures/latex/01_executive_scorecard.png`
- `docs/assets/figures/latex/02_predictive_growth_seasonality.png`
- `docs/assets/figures/latex/03_profit_promotion_leakage.png`
- `docs/assets/figures/latex/04_payment_channel_risk.png`
- `docs/assets/figures/latex/05_returns_fulfillment_cx.png`
- `docs/assets/figures/latex/06_inventory_quadrant_actions.png`
- `docs/assets/figures/latex/07_data_model_validation.png`
- `docs/assets/figures/latex/08_prescriptive_action_roadmap.png`
- `docs/assets/figures/latex/VinDatathon_Task2_LaTeX_Figure_Pack.pdf`
- `docs/assets/figures/latex/latex_include_figures.tex`

For GitHub submission, follow `docs/github-submission.md` and check `docs/file-inventory.md` before staging files.

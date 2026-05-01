# Debug Report: Tableau Render / Export Verification

## Summary

The local Tableau account state is improved: Tableau Desktop 2026.1 launches in the GUI and logs show a cached free-edition lease. The requested automated generation/verification of a final rendered `.twbx`, Tableau screenshots, or Tableau PDF export is still blocked because this environment does not expose a usable non-interactive Tableau export path.

## Evidence Collected

- `tableau.com -h` returns:

```text
Unable to verify license. Please activate the product.
```

- `tableau.exe -h` launches Tableau Desktop GUI rather than returning an export/help CLI.
- Running Tableau creates/updates `C:\Users\Admn\OneDrive\Documents\My Tableau Repository\Logs`.
- Logs show Desktop free-edition mode and cached lease activity.
- No `tabcmd.exe` was found under the installed Tableau paths.
- No Tableau Public executable was found.
- No `.twb`, `.twbx`, `.png`, or `.pdf` final Tableau-rendered output existed in the project before this debug pass.

## Root Cause

The blocker is no longer simply "license not verified." The root cause is tool-surface mismatch:

- Tableau Desktop GUI can launch.
- Tableau Desktop export to image/PDF is a GUI workflow.
- Command-line image/PDF exports require Tableau Cloud/Server tooling such as `tabcmd` plus a published view/workbook URL.
- This project is local file-out only and has no Cloud/Server publication target or `tabcmd` session.

## Fix / Mitigation Applied

- Generated non-Tableau preview screenshots and a PDF from the same validated Tableau extract data:
  - `docs/assets/screenshots/01_executive_overview.png`
  - `docs/assets/screenshots/02_growth_forecast_seasonality.png`
  - `docs/assets/screenshots/03_profit_promotion_leakage.png`
  - `docs/assets/screenshots/04_customer_channel_payment_risk.png`
  - `docs/assets/screenshots/05_returns_reviews_fulfillment.png`
  - `docs/assets/screenshots/06_inventory_actions.png`
  - `docs/assets/screenshots/VinDatathon_Task2_Dashboard_Preview_NON_TABLEAU.pdf`
- Added `scripts/generate_preview_exports.py` so those preview assets are reproducible.
- Updated the file-out package builder so preview exports are included in the ZIP.

## Unresolved

Final Tableau-rendered `.twbx`, Tableau screenshots, and Tableau PDF export still require one of:

1. Manual GUI build/export inside Tableau Desktop.
2. A published Tableau Cloud/Server workbook plus `tabcmd` or REST export permissions.
3. A supported Tableau automation tool/API that can create and render workbooks non-interactively.

## Owner Workflow To Resume

Resume `$dv-data-visualize` after the workbook is manually built in Tableau GUI or after a Tableau Cloud/Server publication target is available.

## Power BI / Alternative Tool Assessment

Power BI Desktop is installed locally as the Microsoft Store app (`Microsoft.MicrosoftPowerBIDesktop` version `2.153.910.0`). This makes a Power BI switch feasible for a GUI-built file-out report, but it does not fully remove the automation blocker:

- Power BI Desktop can save reports as `.pbix` and can save text-backed Power BI Project files (`.pbip`) from the GUI.
- Microsoft documents PDF export from Power BI Desktop and Power BI Service, but Desktop export is still a product workflow rather than a reliable local command-line export surface.
- The Power BI REST export API requires a report in a Power BI workspace plus API authorization and model/report IDs.
- No local CLI authoring helpers such as `pbi-tools`, Tabular Editor, or DAX Studio were found in the current environment.

Recommended paths:

1. Use Power BI if a manually finalized `.pbix` is acceptable. Reuse the validated CSV extracts, create a Power BI semantic model, implement the six dashboard pages, then export PDF from Power BI Desktop.
2. Use Evidence.dev or a local web dashboard if the priority is fully automated build, screenshot, and PDF verification from this environment.
3. Keep Tableau only if the grading instructions strictly require Tableau-specific submission.

## Resolved Path: LaTeX-Ready Rendered Figure Pack

The deliverable requirement was narrowed to fully verifiable rendered images for insertion into a LaTeX answer. The safest path is therefore not Tableau/Power BI binary packaging, but scripted high-resolution figure rendering from the validated analytical extracts.

Implemented:

- Added `scripts/generate_latex_figure_pack.py`.
- Generated 8 final PNG figures at `3200x1800` with 300 DPI metadata.
- Generated an 8-page PDF contact sheet.
- Generated a ZIP package containing all rendered figures plus manifest and LaTeX snippets.
- Generated `figure_manifest.json` with file sizes, SHA-256 hashes, source extracts, guardrails, and DPI metadata.
- Generated `latex_include_figures.tex` with ready-to-use `\includegraphics` snippets.

Final outputs:

- `docs/assets/figures/latex/01_executive_scorecard.png`
- `docs/assets/figures/latex/02_predictive_growth_seasonality.png`
- `docs/assets/figures/latex/03_profit_promotion_leakage.png`
- `docs/assets/figures/latex/04_payment_channel_risk.png`
- `docs/assets/figures/latex/05_returns_fulfillment_cx.png`
- `docs/assets/figures/latex/06_inventory_quadrant_actions.png`
- `docs/assets/figures/latex/07_data_model_validation.png`
- `docs/assets/figures/latex/08_prescriptive_action_roadmap.png`
- `docs/assets/figures/latex/VinDatathon_Task2_LaTeX_Figure_Pack.pdf`
- `docs/assets/figures/latex/VinDatathon_Task2_LaTeX_Figure_Pack.zip`
- `docs/assets/figures/latex/figure_manifest.json`
- `docs/assets/figures/latex/latex_include_figures.tex`

Fresh verification:

- PNG count: 8.
- PNG dimensions: `3200x1800`.
- PNG DPI metadata: approximately `300x300`.
- PDF page markers: 8.
- ZIP entries: 11.
- ZIP includes all PNGs, manifest, PDF, and LaTeX snippet file.

# Tableau File-Out Package

This folder contains the prepared CSV extracts, dashboard blueprint, calculated fields, and packaging manifest for the VinDatathon 2026 Task 2 Tableau dashboard.

## Tableau Status

- Detected Tableau Desktop path: `C:\Program Files\Tableau\Tableau 2026.1\bin\tableau.com`
- CLI status: `desktop_gui_available_cli_export_blocked`
- CLI detail: `tableau.com returned: Unable to verify license. Please activate the product.`

    Tableau Desktop GUI is available locally, but the installed Desktop command-line surface is not usable for automated image/PDF export from this local file-out project. The package is therefore a Tableau-ready build package: connect the CSVs, build the listed worksheets/dashboards, then save as `.twbx` and export screenshots/PDF from the GUI.

## Data Connection Order

1. `dashboard_kpis.csv`
2. `daily_kpi.csv`
3. `growth_forecast_monthly.csv`
4. `seasonality_indices.csv`
5. `orders_enriched.csv`
6. `order_items_enriched.csv`
7. `inventory_monthly.csv`
8. `predictive_signals.csv`
9. `recommendations.csv`

Use relationships rather than physical joins unless a worksheet explicitly needs one table:

- `orders_enriched.order_id` -> `order_items_enriched.order_id`
- `daily_kpi.date` -> `growth_forecast_monthly.date` only for trend views; otherwise keep separate.
- `recommendations.dashboard_page` and `predictive_signals.signal_type` support action tables and tooltips.

## Dashboard Actions

Configure the actions in `tableau_dashboard_blueprint.json`:

- Filter action from Executive Overview into all detail dashboards.
- Hover highlight on category, segment, and payment method.
- Category drill from promotion leakage into product/inventory detail.
- Return reason highlight into category-size and refund views.
- Inventory quadrant filter into product recommendation tables.
- Reset behavior by setting all action-clearing behavior to `Show all values` and using Tableau's Revert control.

## Required Export

After activation and final workbook build:

1. Save the workbook as `VinDatathon_Task2_Tableau.twbx`.
2. Export dashboard images or PDF into `docs/assets/screenshots/`.
3. Keep the final packaged workbook under `docs/assets/workbook/`.

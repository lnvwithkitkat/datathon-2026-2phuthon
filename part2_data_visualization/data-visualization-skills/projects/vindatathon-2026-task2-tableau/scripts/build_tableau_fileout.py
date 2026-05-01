from __future__ import annotations

import json
import subprocess
import zipfile
from pathlib import Path


PROJECT_DIR = Path(__file__).resolve().parents[1]
DOCS_DIR = PROJECT_DIR / "docs"
EXPORT_DIR = DOCS_DIR / "assets" / "exports" / "tableau"
WORKBOOK_DIR = DOCS_DIR / "assets" / "workbook"
PACKAGE_PATH = WORKBOOK_DIR / "VinDatathon_Task2_Tableau_Fileout_Package.zip"


DATA_SOURCES = [
    "orders_enriched.csv",
    "order_items_enriched.csv",
    "daily_kpi.csv",
    "inventory_monthly.csv",
    "growth_forecast_monthly.csv",
    "seasonality_indices.csv",
    "predictive_signals.csv",
    "recommendations.csv",
    "dashboard_kpis.csv",
    "data_dictionary.csv",
    "source_manifest.csv",
]


def tableau_license_status() -> dict[str, str]:
    tableau = Path(r"C:\Program Files\Tableau\Tableau 2026.1\bin\tableau.com")
    tableau_gui = Path(r"C:\Program Files\Tableau\Tableau 2026.1\bin\tableau.exe")
    if not tableau.exists():
        return {"status": "not_found", "detail": str(tableau)}
    try:
        result = subprocess.run(
            [str(tableau), "-h"],
            capture_output=True,
            text=True,
            timeout=30,
            check=False,
        )
        combined = (result.stdout + "\n" + result.stderr).strip()
        if result.returncode == 0:
            return {"status": "available", "detail": combined[:500]}
        if tableau_gui.exists():
            return {
                "status": "desktop_gui_available_cli_export_blocked",
                "detail": f"tableau.com returned: {combined[:300]}",
            }
        return {"status": "license_or_cli_blocked", "detail": combined[:500]}
    except Exception as exc:  # pragma: no cover - environment diagnostic only
        return {"status": "error", "detail": str(exc)}


def dashboard_blueprint() -> dict[str, object]:
    return {
        "project": "vindatathon-2026-task2-tableau",
        "title_vi": "VinDatathon 2026 - Task 2: Dashboard CEO cho TMĐT thời trang",
        "visualization_tool": "Tableau Desktop override",
        "deliverable_mode": "File-out",
        "data_sources": DATA_SOURCES,
        "global_filters": [
            "Date range",
            "ship_region",
            "dominant_category / category",
            "dominant_segment / segment",
            "order_source",
            "device_type",
            "payment_method",
            "age_group",
        ],
        "dashboards": [
            {
                "name": "Executive Overview",
                "story_question": "CEO cần hành động ở đâu để tăng trưởng có lợi nhuận?",
                "primary_sources": ["dashboard_kpis.csv", "daily_kpi.csv", "recommendations.csv"],
                "worksheets": [
                    "KPI strip: Revenue, Gross Margin %, Orders, Cancel Rate, Return Rate, Promo Margin Gap",
                    "Monthly revenue and margin trend with forecast overlay",
                    "Revenue and margin by region/category/segment",
                    "Top recommended actions by priority and estimated impact",
                ],
                "rubric_level": ["Descriptive", "Diagnostic", "Predictive", "Prescriptive"],
            },
            {
                "name": "Growth Forecast & Seasonality",
                "story_question": "Điều gì có khả năng xảy ra tiếp theo nếu xu hướng lịch sử tiếp diễn?",
                "primary_sources": ["growth_forecast_monthly.csv", "seasonality_indices.csv", "daily_kpi.csv"],
                "worksheets": [
                    "Historical vs six-month predictive EDA forecast with confidence band",
                    "Month-of-year peak/soft seasonality index",
                    "Weekday revenue index",
                    "Traffic sessions vs revenue leading-indicator scatter",
                ],
                "rubric_level": ["Predictive", "Prescriptive"],
            },
            {
                "name": "Profit & Promotion Leakage",
                "story_question": "Khuyến mãi đang tạo tăng trưởng hay phá biên lợi nhuận?",
                "primary_sources": ["order_items_enriched.csv", "predictive_signals.csv", "recommendations.csv"],
                "worksheets": [
                    "Promo vs no-promo margin % by category and segment",
                    "Discount rate vs margin scatter",
                    "Revenue share vs margin bubble by category/segment",
                    "Promotion margin risk action table",
                ],
                "rubric_level": ["Diagnostic", "Prescriptive"],
            },
            {
                "name": "Customer, Channel & Payment Risk",
                "story_question": "Kênh, thiết bị, và phương thức thanh toán nào tạo doanh thu chất lượng thấp?",
                "primary_sources": ["orders_enriched.csv", "daily_kpi.csv", "predictive_signals.csv", "recommendations.csv"],
                "worksheets": [
                    "Payment risk bar: cancellation + return-record rate",
                    "Channel efficiency: revenue per session vs order risk",
                    "Device/source mix and AOV",
                    "Customer age/acquisition cohort value and risk",
                ],
                "rubric_level": ["Diagnostic", "Predictive", "Prescriptive"],
            },
            {
                "name": "Returns, Reviews & Fulfillment",
                "story_question": "Trải nghiệm khách hàng đang rò rỉ doanh thu ở đâu?",
                "primary_sources": ["order_items_enriched.csv", "orders_enriched.csv", "recommendations.csv"],
                "worksheets": [
                    "Return reason distribution and refund impact",
                    "Wrong-size heatmap by category and size",
                    "Fulfillment days vs rating / return likelihood",
                    "Return-risk product/category detail table",
                ],
                "rubric_level": ["Diagnostic", "Predictive", "Prescriptive"],
            },
            {
                "name": "Inventory Actions",
                "story_question": "Sản phẩm nào cần bổ sung, giảm nhập, hoặc markdown?",
                "primary_sources": ["inventory_monthly.csv", "predictive_signals.csv", "recommendations.csv"],
                "worksheets": [
                    "Stockout vs overstock quadrant",
                    "Product replenishment priority table",
                    "Category trend: stockout days, fill rate, sell-through",
                    "Markdown / reduce receipts action table",
                ],
                "rubric_level": ["Predictive", "Prescriptive"],
            },
        ],
        "dashboard_actions": [
            {
                "action_name": "Global region/category/segment filter",
                "type": "Filter",
                "source_dashboard": "Executive Overview",
                "source_sheets": ["Revenue and margin by region/category/segment"],
                "target_dashboards": [
                    "Profit & Promotion Leakage",
                    "Customer, Channel & Payment Risk",
                    "Returns, Reviews & Fulfillment",
                    "Inventory Actions",
                ],
                "run_action_on": "Select",
                "clearing_selection": "Show all values",
            },
            {
                "action_name": "Cross-dashboard highlight",
                "type": "Highlight",
                "source_dashboards": [
                    "Profit & Promotion Leakage",
                    "Customer, Channel & Payment Risk",
                    "Returns, Reviews & Fulfillment",
                    "Inventory Actions",
                ],
                "fields": ["category", "segment", "payment_method"],
                "run_action_on": "Hover",
            },
            {
                "action_name": "Category drill to product detail",
                "type": "Filter",
                "source_dashboard": "Profit & Promotion Leakage",
                "target_dashboard": "Inventory Actions",
                "target_filters": ["category", "segment"],
                "run_action_on": "Select",
                "clearing_selection": "Show all values",
            },
            {
                "action_name": "Return reason focus",
                "type": "Highlight",
                "source_dashboard": "Returns, Reviews & Fulfillment",
                "source_sheet": "Return reason distribution and refund impact",
                "target_sheets": ["Wrong-size heatmap by category and size", "Return-risk product/category detail table"],
                "fields": ["top_return_reason", "category", "size"],
                "run_action_on": "Select",
            },
            {
                "action_name": "Inventory quadrant filter",
                "type": "Filter",
                "source_dashboard": "Inventory Actions",
                "source_sheet": "Stockout vs overstock quadrant",
                "target_sheets": ["Product replenishment priority table", "Markdown / reduce receipts action table"],
                "fields": ["inventory_quadrant", "category", "segment"],
                "run_action_on": "Select",
                "clearing_selection": "Show all values",
            },
            {
                "action_name": "Reset presentation state",
                "type": "Reset pattern",
                "implementation": "Set every filter/highlight action to 'Clearing the selection: Show all values' and expose Tableau's Revert control during presentation.",
            },
        ],
    }


def calculated_fields_markdown() -> str:
    return """# Tableau Calculated Fields

Use these calculated fields after connecting the prepared CSVs.

## Shared Metrics

```tableau
// Gross Margin
SUM([sales_revenue]) - SUM([sales_cogs])
```

```tableau
// Gross Margin %
IF SUM([sales_revenue]) != 0 THEN (SUM([sales_revenue]) - SUM([sales_cogs])) / SUM([sales_revenue]) END
```

```tableau
// Line Margin %
IF SUM([line_net_revenue]) != 0 THEN SUM([line_margin]) / SUM([line_net_revenue]) END
```

```tableau
// Discount Rate
IF SUM([line_net_revenue]) + SUM([discount_amount]) != 0
THEN SUM([discount_amount]) / (SUM([line_net_revenue]) + SUM([discount_amount]))
END
```

```tableau
// Cancel Rate
SUM(INT([is_cancelled])) / COUNTD([order_id])
```

```tableau
// Return Record Rate
SUM(INT([has_return_record])) / COUNTD([order_id])
```

```tableau
// Payment Risk Rate
[Cancel Rate] + [Return Record Rate]
```

```tableau
// Revenue per Session
IF SUM([sessions]) != 0 THEN SUM([sales_revenue]) / SUM([sessions]) END
```

```tableau
// Conversion Proxy
IF SUM([sessions]) != 0 THEN SUM([order_count]) / SUM([sessions]) END
```

## Predictive EDA

```tableau
// Forecast Display Revenue
IF [is_forecast] THEN [forecast_revenue] ELSE [sales_revenue] END
```

```tableau
// Forecast Band
[forecast_upper_revenue] - [forecast_lower_revenue]
```

```tableau
// Seasonality Label
IF [seasonality_index] >= 1.10 THEN "Peak"
ELSEIF [seasonality_index] <= 0.90 THEN "Soft"
ELSE "Normal"
END
```

```tableau
// Risk Label
STR([priority]) + " | " + STR(ROUND([risk_score], 1))
```

## Prescriptive Actions

```tableau
// Priority Sort
CASE [priority]
WHEN "Critical" THEN 1
WHEN "High" THEN 2
WHEN "Medium" THEN 3
WHEN "Low" THEN 4
ELSE 5
END
```

```tableau
// Impact VND Label
IF ISNULL([estimated_impact_vnd]) THEN "Evidence-based risk"
ELSE STR(ROUND([estimated_impact_vnd] / 1000000, 1)) + "M VND"
END
```
"""


def readme_markdown(status: dict[str, str]) -> str:
    return f"""# Tableau File-Out Package

This folder contains the prepared CSV extracts, dashboard blueprint, calculated fields, and packaging manifest for the VinDatathon 2026 Task 2 Tableau dashboard.

## Tableau Status

- Detected Tableau Desktop path: `C:\\Program Files\\Tableau\\Tableau 2026.1\\bin\\tableau.com`
- CLI status: `{status["status"]}`
- CLI detail: `{status["detail"]}`

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
"""


def write_assets() -> dict[str, str]:
    WORKBOOK_DIR.mkdir(parents=True, exist_ok=True)
    status = tableau_license_status()
    blueprint_path = WORKBOOK_DIR / "tableau_dashboard_blueprint.json"
    calc_path = WORKBOOK_DIR / "tableau_calculated_fields.md"
    readme_path = WORKBOOK_DIR / "README_TABLEAU_BUILD.md"
    manifest_path = WORKBOOK_DIR / "twbx_package_manifest.json"

    blueprint = dashboard_blueprint()
    blueprint["tableau_status"] = status
    blueprint_path.write_text(json.dumps(blueprint, indent=2, ensure_ascii=False), encoding="utf-8")
    calc_path.write_text(calculated_fields_markdown(), encoding="utf-8")
    readme_path.write_text(readme_markdown(status), encoding="utf-8")

    manifest = {
        "package_type": "Tableau file-out build package",
        "twbx_final_expected_name": "VinDatathon_Task2_Tableau.twbx",
        "automated_twbx_verified": False,
        "reason": "Tableau Desktop GUI is available, but local Desktop CLI/export automation is not available for this file-out project.",
        "data_sources": [f"data/{name}" for name in DATA_SOURCES if (EXPORT_DIR / name).exists()],
        "blueprint": blueprint_path.name,
        "calculated_fields": calc_path.name,
        "build_readme": readme_path.name,
    }
    manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")

    if PACKAGE_PATH.exists():
        PACKAGE_PATH.unlink()
    with zipfile.ZipFile(PACKAGE_PATH, "w", compression=zipfile.ZIP_DEFLATED) as package:
        for filename in DATA_SOURCES:
            path = EXPORT_DIR / filename
            if path.exists():
                package.write(path, f"data/{filename}")
        for path in [blueprint_path, calc_path, readme_path, manifest_path]:
            if path.exists():
                package.write(path, path.name)
        for path in DOCS_DIR.glob("*.md"):
            package.write(path, f"docs/{path.name}")
        screenshots_dir = DOCS_DIR / "assets" / "screenshots"
        if screenshots_dir.exists():
            for path in screenshots_dir.glob("*"):
                if path.is_file():
                    package.write(path, f"screenshots/{path.name}")

    return {
        "package": str(PACKAGE_PATH.relative_to(PROJECT_DIR)),
        "blueprint": str(blueprint_path.relative_to(PROJECT_DIR)),
        "calculated_fields": str(calc_path.relative_to(PROJECT_DIR)),
        "readme": str(readme_path.relative_to(PROJECT_DIR)),
        "manifest": str(manifest_path.relative_to(PROJECT_DIR)),
        "tableau_status": status["status"],
    }


def main() -> None:
    missing = [name for name in DATA_SOURCES if not (EXPORT_DIR / name).exists()]
    if missing:
        raise FileNotFoundError(f"Run prepare_tableau_data.py first. Missing exports: {missing}")
    result = write_assets()
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()

# Visualization Specification

## Selected Path

- Tool: Tableau Desktop override
- Delivery: File-out
- Package: `docs/assets/workbook/VinDatathon_Task2_Tableau_Fileout_Package.zip`
- Blueprint: `docs/assets/workbook/tableau_dashboard_blueprint.json`
- Calculated fields: `docs/assets/workbook/tableau_calculated_fields.md`

## Dashboard Pages

Power BI manual rebuild note: use `powerbi-visual-diversity-plan.md` to diversify the visual grammar. The static LaTeX figures are analytical targets, but a graded interactive Power BI build should include decomposition tree, matrix heatmap, scatter/bubble, waterfall, treemap/ribbon, combo charts, KPI cards, and action matrices rather than repeating bar charts.

### 1. Executive Overview

Purpose: CEO-level answer to where the business should act first.

Charts:

- KPI strip: revenue, margin %, orders, customers, cancel rate, return-record rate, promo margin gap.
- Monthly revenue and margin trend with forecast overlay.
- Region/category/segment contribution.
- Top recommendation table.

### 2. Growth Forecast & Seasonality

Purpose: make the Predictive rubric explicit.

Charts:

- Historical vs six-month predictive EDA forecast.
- Month-of-year seasonality index.
- Weekday seasonality index.
- Traffic vs revenue leading-indicator view.

### 3. Profit & Promotion Leakage

Purpose: identify where discounting destroys margin.

Charts:

- Promo vs no-promo margin % by category/segment.
- Discount rate vs line margin.
- Revenue share vs margin bubble.
- Promotion margin recommendation table.

### 4. Customer, Channel & Payment Risk

Purpose: show low-quality revenue pockets.

Charts:

- Payment risk rate, especially COD.
- Revenue per session by channel.
- Device/source mix and AOV.
- Customer age/acquisition cohort value and risk.

### 5. Returns, Reviews & Fulfillment

Purpose: quantify customer-experience leakage.

Charts:

- Return reason and refund impact.
- Wrong-size heatmap by category and size.
- Fulfillment days vs rating/return likelihood.
- Product/category return detail.

### 6. Inventory Actions

Purpose: turn stockout/overstock signals into actions.

Charts:

- Stockout vs overstock quadrant.
- Product replenishment priority.
- Category stockout days, fill rate, sell-through trend.
- Markdown or reduce-receipts action table.

## Dashboard Actions

- Filter action: selecting region/category/segment on Executive Overview filters all detail dashboards.
- Highlight action: hovering on category, segment, or payment method highlights related marks across risk dashboards.
- Drill action: selecting a category on Promotion Leakage opens product-level inventory and margin detail.
- Return reason action: selecting a return reason highlights affected categories, sizes, and refund impact.
- Inventory quadrant action: selecting stockout/overstock quadrant filters product action tables.
- Reset behavior: configure every action with `Clearing the selection: Show all values`; expose Tableau Revert during presentation.

## Current Validation Status

- Data extracts generated and validated.
- Tableau build package generated.
- Rendered Tableau `.twbx` and screenshots are blocked until Tableau Desktop activation is available locally.
- Power BI rebuild guide updated with a visual-diversity plan to avoid overusing bar charts.
- Power BI rebuild guide updated with explicit Dashboard 3 waterfall helper-table DAX and build steps.
- Power BI rebuild guide updated with explicit Dashboard 5 decomposition tree measures, field wells, manual drill path, and troubleshooting.
- Power BI rebuild guide updated with non-technical reproduction steps for Page 5 remaining visuals, Page 6 inventory visuals, and optional appendix Pages 7-8.
- Power BI rebuild guide clarified that `11+ days` is an unused fulfillment fallback bucket in the current prepared data, and order-level fulfillment buckets now handle `No shipment` explicitly.
- Power BI `.pbix` structural review completed for `docs/assets/powerbi/VinDatathon_Task2_PowerBI.pbix`; fix and improvement instructions are in `docs/powerbi-pbix-review-fix-list.md`.

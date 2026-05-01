# Power BI Visual Diversity Plan

This plan revises the manual Power BI build so the dashboard does not overuse bar charts. Diversity should improve the analytical story, not just add visual variety.

## Principle

Use each visual type for a distinct analytical job:

| Analytical job | Better visual choices |
|---|---|
| Single-number executive status | KPI card, card with sparkline, gauge only when target exists |
| Time movement | Line chart, area chart, combo line/column chart |
| Forecast uncertainty | Line chart with shaded band, area range, error bars |
| Contribution / composition | Treemap, ribbon chart, stacked column, matrix |
| Ranking | Bar chart, lollipop-style bar, sorted table |
| Driver diagnosis | Decomposition tree, scatter/bubble, matrix heatmap |
| Leakage bridge | Waterfall chart |
| Two-risk tradeoff | Scatter plot / quadrant |
| Operational action list | Matrix/table with conditional formatting |
| Deep dive | Drillthrough page, tooltip page |

## Page-Level Visual Mix

### Page 1: Executive Overview

Use:

- KPI cards for revenue, margin, COD risk, and promo gap.
- Combo chart for monthly revenue columns plus margin-rate line.
- Decomposition tree for revenue/margin drivers by region, category, payment method, source, and segment.
- Compact action matrix with conditional formatting by priority.

Avoid:

- A second generic risk bar chart if the decomposition tree already explains drivers.

### Page 2: Growth Forecast & Seasonality

Use:

- Forecast line chart with historical actuals, forecast, and confidence band.
- Matrix heatmap for month-of-year and weekday seasonality.
- Ribbon chart or small multiples to show changing source/channel contribution over time.
- KPI cards for strongest month, softest month, and next forecast high.

Avoid:

- Separate month and weekday bar charts unless the heatmap is unreadable.

### Page 3: Profit & Promotion Leakage

Use:

- Waterfall chart for margin bridge: no-promo margin baseline, promo margin loss, estimated recoverable opportunity.
- Scatter/bubble chart: discount rate vs margin %, bubble size revenue, legend category or segment.
- Matrix heatmap: category x segment, colored by promo margin gap.
- Action table filtered to promotion risks.

Avoid:

- Two bar charts showing nearly the same promotion gap.

### Page 4: Customer, Channel & Payment Risk

Use:

- Donut chart for payment-method order share, used only as context.
- Scatter chart: channel margin % vs risk rate, bubble size revenue.
- Treemap for channel revenue contribution.
- Matrix with payment method x order source risk rates.
- Action table for controls and spend shift.

Avoid:

- Ranking every payment/channel field with bars.

### Page 5: Returns, Reviews & Fulfillment

Use:

- Sankey-style flow if available: category -> return reason -> refund impact. If not available, use decomposition tree.
- Matrix heatmap for category x size return pressure.
- Combo chart for fulfillment bucket: order count columns plus return-rate line.
- Tooltip/drillthrough page for product/category detail.

Avoid:

- A plain return-reason bar as the main visual unless custom visuals are not allowed.

### Page 6: Inventory Actions

Use:

- Scatter/quadrant chart: stockout pressure vs overstock pressure.
- Filled matrix heatmap by category and segment for stockout/overstock share.
- Treemap for overstock working-capital exposure.
- Action table with replenishment vs markdown recommendations.

Avoid:

- Clustered bars for category stockout/overstock if the heatmap communicates imbalance better.

### Optional Page 7: Data Model & Validation

Use:

- Shape-based relationship diagram or imported ERD image.
- KPI cards for 13 CSVs, 100% FK coverage, 0 VND revenue gap, EDA-only forecast.
- Small table of row counts.

### Optional Page 8: Prescriptive Roadmap

Use:

- Swimlane-style matrix by business owner and action theme.
- Impact/risk bubble chart for prioritization.
- Action table for exact wording.

## Minimum Diversity Target

Across the six main pages, include at least these visual families:

- KPI cards.
- Line or area chart.
- Combo chart.
- Matrix heatmap.
- Scatter/bubble chart.
- Decomposition tree or drillthrough.
- Waterfall chart.
- Treemap or ribbon chart.
- Action matrix/table.

This gives enough variety for grading while keeping the dashboard coherent.

## Power BI Interaction Notes

- Use slicers for global filters.
- Use `Edit interactions` so decomposition trees and scatter points filter the detail table.
- Use drillthrough pages for product/category detail.
- Use tooltip pages for product-level return/margin/inventory context.
- Use a reset bookmark button on each page.

## When To Still Use Bar Charts

Bar charts are still appropriate for simple ranked comparisons. Use them sparingly:

- Top 10 products by risk.
- Top return reasons when a decomposition tree or flow visual is not available.
- Small category ranking when labels must be readable.

Limit each page to at most one primary bar chart.

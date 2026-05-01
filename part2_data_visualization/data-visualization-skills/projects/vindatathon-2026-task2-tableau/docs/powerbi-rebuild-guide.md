# Power BI Rebuild Guide

This guide explains how to recreate the VinDatathon 2026 Task 2 dashboard manually in Power BI Desktop from the validated extracts already produced in this project.

Use this as the Power BI build recipe. The existing LaTeX figure pack is the visual target:

```text
projects/vindatathon-2026-task2-tableau/docs/assets/figures/latex/
```

## Goal

Rebuild the dashboard as a Power BI report that supports the same CEO story:

- Descriptive: revenue, margin, orders, customers, returns, inventory state.
- Diagnostic: promotion leakage, COD risk, channel quality, return reasons, fulfillment issues.
- Predictive: historical trend extrapolation, monthly seasonality, stockout/overstock risk, return risk.
- Prescriptive: action queue with owners, risk scores, impact, tradeoffs, and recommended next steps.

Keep the Part 2 guardrails:

- Use historical Part 2 business data only.
- Do not use `sales_test.csv`.
- Do not use `sample_submission.csv`.
- Do not use `baseline.ipynb`.
- Treat predictive outputs as EDA signals, not Kaggle forecasting submission outputs.

## Recommended Source Files

Use the prepared extracts rather than rebuilding joins inside Power BI. They are validated and already reconcile revenue.

Source folder:

```text
D:\Code\Coding\data-visualization-skills\projects\vindatathon-2026-task2-tableau\docs\assets\exports\tableau
```

Import these CSVs:

| File | Purpose | Rows |
|---|---:|---:|
| `dashboard_kpis.csv` | Final KPI values and definitions | 13 |
| `daily_kpi.csv` | Daily revenue, margin, traffic, rolling averages | 3,833 |
| `growth_forecast_monthly.csv` | Monthly actuals plus six-month EDA forecast | 132 |
| `seasonality_indices.csv` | Month and weekday seasonal indices | 19 |
| `recommendations.csv` | Prescriptive action queue | 16 |
| `orders_enriched.csv` | Order-level customer, payment, channel, fulfillment, risk | 646,945 |
| `order_items_enriched.csv` | Line-level product, promo, margin, return, review | 714,669 |
| `inventory_monthly.csv` | Product-month stockout, overstock, sell-through, action scores | 60,247 |
| `predictive_signals.csv` | Optional signal table for tooltips and appendix views | 62 |

Power BI can load the full model, but the two enriched fact files are large. If Desktop becomes slow, use Power Query reference queries to create smaller aggregate tables, then disable load on the full fact tables after the aggregates are built.

## Power BI Setup

1. Open Power BI Desktop.
2. Select `Get data > Text/CSV`.
3. Import each CSV from the source folder above.
4. In Power Query, confirm data types before loading.
5. Use `Import` mode.
6. Turn off `Auto date/time` to keep the model controlled:
   - `File > Options and settings > Options > Current File > Data Load`
   - Disable `Auto date/time`.
7. Save the report as:

```text
D:\Code\Coding\data-visualization-skills\projects\vindatathon-2026-task2-tableau\docs\assets\powerbi\VinDatathon_Task2_PowerBI.pbix
```

Create the `docs/assets/powerbi/` folder if it does not exist.

## Data Type Checklist

Set these types in Power Query:

| Table | Columns | Type |
|---|---|---|
| `daily_kpi` | `date` | Date |
| `growth_forecast_monthly` | `date` | Date |
| `inventory_monthly` | `snapshot_date` | Date |
| `orders_enriched` | `order_date`, `ship_date`, `delivery_date`, `first_return_date` | Date |
| `order_items_enriched` | `order_date`, `start_date`, `end_date`, `first_return_date`, `first_review_date` | Date |
| All revenue, COGS, margin, fee, discount, risk, rating columns | numeric fields | Decimal number |
| `stockout_flag`, `overstock_flag`, `reorder_flag` | inventory flags | Whole number |
| `is_cancelled`, `has_return_record`, `is_cod`, `has_promo`, `returned_flag`, `reviewed_flag`, `late_fulfillment_flag`, `is_forecast` | boolean fields | True/False |

If Power BI imports boolean fields as text, convert them in Power Query before writing DAX. Avoid mixing text `"True"` with boolean `TRUE()` in measures.

## Null Policy For Orders Enriched

Power BI may show high empty percentages for a few `orders_enriched.csv` columns. That is expected for optional event fields, not a failed join.

Measured file-wide blank-cell rate is only `7.24%`. The high-empty columns are:

| Column | Blank rate | Meaning |
|---|---:|---|
| `top_return_reason` | 94.43% | Order has no return record |
| `first_return_date` | 94.43% | Order has no return record |
| `avg_rating` | 82.79% | Order has no review |
| `order_avg_rating` | 82.79% | Order has no review |
| Shipment fields | 12.50% | Order has no shipment row, mostly cancelled/created/paid |

Do not globally replace all blanks. Keep date and numeric fields null, and create display labels only where useful. See `docs/orders-enriched-null-policy.md` for the detailed profile.

## Null Policy For Order Items Enriched

Power BI may also show some `order_items_enriched.csv` columns as `100%` empty if column profiling is based on only the first 1,000 preview rows. The full file has no columns that are actually 100% blank.

Measured full-file profile:

| Column / group | Blank rate | Meaning |
|---|---:|---|
| `promo_id_2` | 99.97% | Second stacked promotions are extremely rare |
| `applicable_category` | 95.82% | Most promotions are global, so source category is blank |
| Return fields | 94.41% | Line item has no return record |
| Review fields | 84.11% | Line item has no review |
| Primary promotion metadata | 61.34% | Line item has no promotion |
| Shipment fields | 12.49% | Parent order has no shipment row |

Before making cleanup decisions in Power Query, change profiling to `Column profiling based on entire dataset`. See `docs/order-items-enriched-null-policy.md` for the detailed profile.

## Model Design

Use a simple star-ish model. The enriched tables are already denormalized, so do not physically merge everything again.

Create a calculated date table:

```DAX
DimDate =
CALENDAR (
    MIN ( daily_kpi[date] ),
    MAX ( growth_forecast_monthly[date] )
)
```

Add date columns:

```DAX
Year = YEAR ( DimDate[Date] )
Month Number = MONTH ( DimDate[Date] )
Month Name = FORMAT ( DimDate[Date], "MMMM" )
Year Month = FORMAT ( DimDate[Date], "YYYY-MM" )
Quarter = "Q" & FORMAT ( DimDate[Date], "Q" )
```

Optional product dimension:

```DAX
DimProduct =
DISTINCT (
    UNION (
        SELECTCOLUMNS (
            order_items_enriched,
            "product_id", order_items_enriched[product_id],
            "product_name", order_items_enriched[product_name],
            "category", order_items_enriched[category],
            "segment", order_items_enriched[segment]
        ),
        SELECTCOLUMNS (
            inventory_monthly,
            "product_id", inventory_monthly[product_id],
            "product_name", inventory_monthly[product_name],
            "category", inventory_monthly[category],
            "segment", inventory_monthly[segment]
        )
    )
)
```

Recommended active relationships:

| From | To | Cardinality | Cross-filter |
|---|---|---:|---|
| `DimDate[Date]` | `daily_kpi[date]` | 1:* | Single |
| `DimDate[Date]` | `orders_enriched[order_date]` | 1:* | Single |
| `DimDate[Date]` | `growth_forecast_monthly[date]` | 1:* | Single |
| `DimDate[Date]` | `inventory_monthly[snapshot_date]` | 1:* | Single |
| `orders_enriched[order_id]` | `order_items_enriched[order_id]` | 1:* | Single |
| `DimProduct[product_id]` | `order_items_enriched[product_id]` | 1:* | Single |
| `DimProduct[product_id]` | `inventory_monthly[product_id]` | 1:* | Single |

Do not also create an active `DimDate[Date] -> order_items_enriched[order_date]` relationship while `orders_enriched[order_id] -> order_items_enriched[order_id]` is active. That creates two filter paths from `DimDate` to line items:

```text
DimDate -> order_items_enriched
DimDate -> orders_enriched -> order_items_enriched
```

Power BI correctly reports this as an ambiguous path.

Preferred fix for this model:

1. Keep `DimDate[Date] -> orders_enriched[order_date]` active.
2. Keep `orders_enriched[order_id] -> order_items_enriched[order_id]` active.
3. Delete the active `DimDate[Date] -> order_items_enriched[order_date]` relationship.
4. If you need line-item date analysis independent of `orders_enriched`, create the `DimDate -> order_items_enriched` relationship as inactive and use `USERELATIONSHIP` in specific measures, or temporarily remove the order-to-items relationship for a pure line-item model.

Leave `dashboard_kpis`, `seasonality_indices`, `recommendations`, and `predictive_signals` disconnected unless you need a specific visual interaction. They are summary/action tables.

## Core Measures

Create a measure table named `Measures`, then add these DAX measures.

```DAX
Official Revenue =
SUM ( daily_kpi[sales_revenue] )

Gross Margin =
SUM ( daily_kpi[sales_margin] )

Gross Margin % =
DIVIDE ( [Gross Margin], [Official Revenue] )

Orders =
DISTINCTCOUNT ( orders_enriched[order_id] )

Customers =
DISTINCTCOUNT ( orders_enriched[customer_id] )

AOV =
DIVIDE ( [Official Revenue], [Orders] )
```

Order risk:

```DAX
Cancelled Orders =
CALCULATE (
    DISTINCTCOUNT ( orders_enriched[order_id] ),
    orders_enriched[is_cancelled] = TRUE ()
)

Returned Orders =
CALCULATE (
    DISTINCTCOUNT ( orders_enriched[order_id] ),
    orders_enriched[has_return_record] = TRUE ()
)

Cancel Rate =
DIVIDE ( [Cancelled Orders], [Orders] )

Return Record Rate =
DIVIDE ( [Returned Orders], [Orders] )

Payment Risk Rate =
[Cancel Rate] + [Return Record Rate]

COD Orders =
CALCULATE (
    DISTINCTCOUNT ( orders_enriched[order_id] ),
    orders_enriched[payment_method] = "cod"
)

COD Risk Orders =
CALCULATE (
    DISTINCTCOUNT ( orders_enriched[order_id] ),
    orders_enriched[payment_method] = "cod",
    FILTER (
        orders_enriched,
        orders_enriched[is_cancelled] = TRUE ()
            || orders_enriched[has_return_record] = TRUE ()
    )
)

COD Risk Rate =
DIVIDE ( [COD Risk Orders], [COD Orders] )
```

Line-level return and refund measures for Page 5:

Use these for the Dashboard 5 decomposition tree because `category`, `size`, `segment`, `top_return_reason`, `payment_method`, and fulfillment fields all exist in `order_items_enriched`. Keeping the analyzed measure and the explanation fields on the same table avoids weak or missing filtering in the decomposition tree.

```DAX
Line Items =
COUNTROWS ( order_items_enriched )

Return Line Items =
CALCULATE (
    [Line Items],
    order_items_enriched[return_records] > 0
)

Return Line Rate =
DIVIDE ( [Return Line Items], [Line Items] )

Returned Units =
SUM ( order_items_enriched[returned_units] )

Refund Amount =
SUM ( order_items_enriched[refund_amount] )

Avg Line Rating =
AVERAGE ( order_items_enriched[avg_rating] )

Wrong Size Return Lines =
CALCULATE (
    [Return Line Items],
    order_items_enriched[top_return_reason] = "wrong_size"
)

Wrong Size Refund Amount =
CALCULATE (
    [Refund Amount],
    order_items_enriched[top_return_reason] = "wrong_size"
)
```

Line and promotion margin:

```DAX
Line Revenue =
SUM ( order_items_enriched[line_net_revenue] )

Line Margin =
SUM ( order_items_enriched[line_margin] )

Line Margin % =
DIVIDE ( [Line Margin], [Line Revenue] )

Promo Margin % =
CALCULATE (
    [Line Margin %],
    order_items_enriched[has_promo] = TRUE ()
)

No Promo Margin % =
CALCULATE (
    [Line Margin %],
    order_items_enriched[has_promo] = FALSE ()
)

Promo Margin Gap pp =
100 * ( [No Promo Margin %] - [Promo Margin %] )

Discount Rate =
DIVIDE (
    SUM ( order_items_enriched[discount_amount] ),
    SUM ( order_items_enriched[line_list_revenue] )
)
```

Promotion leakage waterfall helper:

Create this disconnected helper table with `Modeling > New table`. Do not create any relationship from this table to the rest of the model.

```DAX
Promo Leakage Waterfall =
DATATABLE (
    "Step Order", INTEGER,
    "Step", STRING,
    {
        { 1, "No-promo margin baseline" },
        { 2, "Promotion leakage" }
    }
)
```

Select `Promo Leakage Waterfall[Step]`, then set `Column tools > Sort by column` to `Promo Leakage Waterfall[Step Order]`.

Create this measure:

```DAX
Promo Leakage Waterfall Value pp =
VAR NoPromoMarginPP = [No Promo Margin %] * 100
VAR PromoMarginPP = [Promo Margin %] * 100
RETURN
    SWITCH (
        SELECTEDVALUE ( 'Promo Leakage Waterfall'[Step] ),
        "No-promo margin baseline", NoPromoMarginPP,
        "Promotion leakage", PromoMarginPP - NoPromoMarginPP,
        BLANK ()
    )
```

Why this uses only two rows: Power BI waterfall charts show a running total. The first bar is the no-promo baseline, the second bar is the negative margin leakage, and Power BI's final total column becomes the promo margin result. Do not add a third helper row for `Promo margin result`, because Power BI will treat it as another change unless your visual supports setting that point as a total.

Traffic, fulfillment, and inventory:

```DAX
Web Sessions =
SUM ( daily_kpi[sessions] )

Revenue per Session =
DIVIDE ( [Official Revenue], [Web Sessions] )

Orders per Session =
DIVIDE ( SUM ( daily_kpi[order_count] ), [Web Sessions] )

Avg Fulfillment Days =
AVERAGE ( orders_enriched[fulfillment_days] )

Avg Rating =
AVERAGE ( orders_enriched[order_avg_rating] )

Inventory Stockout Share =
AVERAGE ( inventory_monthly[stockout_flag] )

Inventory Overstock Share =
AVERAGE ( inventory_monthly[overstock_flag] )

Avg Stockout Pressure =
AVERAGE ( inventory_monthly[stockout_pressure_score] )

Avg Overstock Pressure =
AVERAGE ( inventory_monthly[overstock_pressure_score] )

Inventory Products =
DISTINCTCOUNT ( inventory_monthly[product_id] )

Stock On Hand =
SUM ( inventory_monthly[stock_on_hand] )

Inventory Units Sold =
SUM ( inventory_monthly[units_sold] )

Inventory Units Sold 3M Avg =
SUM ( inventory_monthly[units_sold_3m_avg] )

Stockout Products =
CALCULATE (
    [Inventory Products],
    inventory_monthly[stockout_flag] = 1
)

Overstock Products =
CALCULATE (
    [Inventory Products],
    inventory_monthly[overstock_flag] = 1
)

Stockout Product Share =
DIVIDE ( [Stockout Products], [Inventory Products] )

Overstock Product Share =
DIVIDE ( [Overstock Products], [Inventory Products] )

Avg Fill Rate =
AVERAGE ( inventory_monthly[fill_rate] )

Avg Days of Supply =
AVERAGE ( inventory_monthly[days_of_supply] )

Avg Sell Through Rate =
AVERAGE ( inventory_monthly[sell_through_rate] )
```

Forecast and recommendation measures:

```DAX
Forecast Revenue =
SUM ( growth_forecast_monthly[forecast_revenue] )

Forecast Lower Revenue =
SUM ( growth_forecast_monthly[forecast_lower_revenue] )

Forecast Upper Revenue =
SUM ( growth_forecast_monthly[forecast_upper_revenue] )

Seasonality Index =
AVERAGE ( seasonality_indices[seasonality_index] )

Risk Score =
AVERAGE ( recommendations[risk_score] )

Estimated Impact VND =
SUM ( recommendations[estimated_impact_vnd] )

Action Count =
COUNTROWS ( recommendations )
```

## Helpful Calculated Columns

Category and segment label:

```DAX
Category Segment =
order_items_enriched[category] & " / " & order_items_enriched[segment]
```

Forecast label:

```DAX
Forecast Type =
IF ( growth_forecast_monthly[is_forecast] = TRUE (), "Forecast", "Historical" )
```

Seasonality label:

```DAX
Seasonality Label =
SWITCH (
    TRUE (),
    seasonality_indices[seasonality_index] >= 1.10, "Peak",
    seasonality_indices[seasonality_index] <= 0.90, "Soft",
    "Normal"
)
```

Priority sort:

```DAX
Priority Sort =
SWITCH (
    recommendations[priority],
    "Critical", 1,
    "High", 2,
    "Medium", 3,
    "Low", 4,
    5
)
```

Fulfillment buckets:

Create `Fulfillment Bucket` as a calculated column on `orders_enriched`. Use it for order-level visuals.

```DAX
Fulfillment Bucket =
SWITCH (
    TRUE (),
    ISBLANK ( orders_enriched[fulfillment_days] ), "No shipment",
    orders_enriched[fulfillment_days] <= 3, "0-3 days",
    orders_enriched[fulfillment_days] <= 5, "4-5 days",
    orders_enriched[fulfillment_days] <= 7, "6-7 days",
    orders_enriched[fulfillment_days] <= 10, "8-10 days",
    "11+ days"
)
```

Create this calculated column on `orders_enriched`, then select `Fulfillment Bucket` and set `Column tools > Sort by column` to `Fulfillment Bucket Sort`.

```DAX
Fulfillment Bucket Sort =
SWITCH (
    orders_enriched[Fulfillment Bucket],
    "No shipment", 0,
    "0-3 days", 1,
    "4-5 days", 2,
    "6-7 days", 3,
    "8-10 days", 4,
    "11+ days", 5,
    99
)
```

Current data note: in the prepared extracts, nonblank `fulfillment_days` ranges from `2` to `10`, so the `11+ days` bucket has no rows right now. Keep the `11+ days` branch as a safe fallback for future refreshes or manual changes. It is normal if Power BI only shows `0-3 days`, `4-5 days`, `6-7 days`, and `8-10 days` after you filter out `No shipment`.

Create `Line Fulfillment Bucket` as a calculated column on `order_items_enriched`. Use it for Page 5 line-item return visuals.

```DAX
Line Fulfillment Bucket =
SWITCH (
    TRUE (),
    ISBLANK ( order_items_enriched[fulfillment_days] ), "No shipment",
    order_items_enriched[fulfillment_days] <= 3, "0-3 days",
    order_items_enriched[fulfillment_days] <= 5, "4-5 days",
    order_items_enriched[fulfillment_days] <= 7, "6-7 days",
    order_items_enriched[fulfillment_days] <= 10, "8-10 days",
    "11+ days"
)
```

Create this calculated column on `order_items_enriched`, then select `Line Fulfillment Bucket` and set `Column tools > Sort by column` to `Line Fulfillment Bucket Sort`.

```DAX
Line Fulfillment Bucket Sort =
SWITCH (
    order_items_enriched[Line Fulfillment Bucket],
    "No shipment", 0,
    "0-3 days", 1,
    "4-5 days", 2,
    "6-7 days", 3,
    "8-10 days", 4,
    "11+ days", 5,
    99
)
```

## Report Theme

Use a restrained business palette:

| Purpose | Hex |
|---|---|
| Background | `#F7F8F4` |
| Panel | `#FFFFFF` |
| Text | `#152018` |
| Muted text | `#617067` |
| Positive / revenue | `#2F7D4B` |
| Margin / secondary | `#178F91` |
| Forecast / channel | `#3F6FA6` |
| Inventory / seasonality | `#7654A7` |
| Warning / promo | `#D9842E` |
| Risk / returns | `#B84848` |
| Grid / borders | `#D9DFD6` |

Canvas settings:

- Page size: `16:9`.
- Suggested canvas: `1920 x 1080` or default 16:9.
- Use page background `#F7F8F4`.
- Keep cards and panels simple. Avoid decorative backgrounds.

## Global Slicers

Create a slicer band on the main pages:

- Date range: `DimDate[Date]`
- Region: `orders_enriched[ship_region]`
- Category: `DimProduct[category]` or `order_items_enriched[category]`
- Segment: `DimProduct[segment]` or `order_items_enriched[segment]`
- Order source: `orders_enriched[order_source]`
- Device type: `orders_enriched[device_type]`
- Payment method: `orders_enriched[payment_method]`
- Customer age group: `orders_enriched[age_group]`

Use `View > Sync slicers` if you want the same slicers to apply across pages.

## Dashboard Pages

Build six main pages. Add two optional appendix pages if your written submission needs visual proof of validation and prescriptive roadmap.

Use the diversified visual plan in `docs/powerbi-visual-diversity-plan.md`. The PNGs in `docs/assets/figures/latex/` are analytical targets, not a requirement to copy every chart type exactly. For Power BI, prefer the visual mix below to avoid a bar-chart-heavy dashboard.

### Page 1: Executive Overview

Target figure:

```text
docs/assets/figures/latex/01_executive_scorecard.png
```

Purpose: show the CEO where to act first.

Visuals:

| Visual | Fields / measures | Notes |
|---|---|---|
| KPI cards | `[Official Revenue]`, `[Gross Margin %]`, `[COD Risk Rate]`, `[Promo Margin %]`, `[No Promo Margin %]` | Expected values: 16.4B VND, 13.8%, 24.9%, 1.3% vs 20.0% |
| Combo chart | Axis `daily_kpi[date]`; columns `sales_revenue`; line `[Gross Margin %]` or `sales_margin_rolling_30d` | Shows scale and profitability together |
| Decomposition tree | Analyze `[Official Revenue]` or `[Line Margin %]`; explain by region, category, payment method, order source, segment | Stronger diagnostic visual than another ranked bar |
| Action matrix | `priority`, `signal_type`, `entity`, `recommended_action`, `risk_score` | Conditional-format priority and risk score |

Business takeaway:

```text
Growth exists, but revenue quality is constrained by low promo margin, COD risk, returns, and inventory imbalance.
```

### Page 2: Growth Forecast & Seasonality

Target figure:

```text
docs/assets/figures/latex/02_predictive_growth_seasonality.png
```

Purpose: make the Predictive EDA rubric explicit.

Visuals:

| Visual | Fields / measures | Notes |
|---|---|---|
| Line chart | Axis `growth_forecast_monthly[date]`; values `sales_revenue`, `forecast_revenue` | Use green for actual and blue dashed style for forecast if available |
| Forecast band | `forecast_lower_revenue`, `forecast_upper_revenue` | Use area chart, error bars, or a light blue range visual |
| Matrix heatmap | Rows `grain`, columns `period_name`, values `seasonality_index` | Conditional formatting makes peak/soft periods obvious |
| Ribbon chart or small multiples | Axis date/month; legend `order_source` or channel; value revenue/orders | Shows changing channel contribution over time |
| KPI cards | max forecast revenue, strongest month, softest month | Expected: May is strongest; December is softest |

Business takeaway:

```text
March-June are likely stronger demand windows; inventory and return controls should be ready before the seasonal peak.
```

### Page 3: Profit & Promotion Leakage

Target figure:

```text
docs/assets/figures/latex/03_profit_promotion_leakage.png
```

Purpose: show where promotions create low-quality revenue.

Visuals:

| Visual | Fields / measures | Notes |
|---|---|---|
| Waterfall chart | Category `Promo Leakage Waterfall[Step]`; Y-axis `[Promo Leakage Waterfall Value pp]`; total column on | Shows no-promo margin baseline, negative promo leakage, and final promo margin result |
| Scatter/bubble chart | X `line_discount_rate`; Y `line_margin_pct`; size `line_net_revenue`; legend category/segment | Shows where discount depth destroys margin |
| Matrix heatmap | Rows category, columns segment, values `[Promo Margin Gap pp]` | Finds the worst promotion leakage pockets |
| KPI cards | `[Promo Margin %]`, `[No Promo Margin %]` | Expected: 1.3% vs 20.0% |
| Action table | Recommendations filtered to `signal_type = Promotion margin risk` | Use owner/action/tradeoff columns |

Waterfall build steps:

1. Confirm the helper table and measure from the `Line and promotion margin` section exist.
2. Insert the native `Waterfall chart` visual.
3. Put `Promo Leakage Waterfall[Step]` in `Category`.
4. Put `[Promo Leakage Waterfall Value pp]` in `Y-axis`.
5. Leave `Breakdown` empty for the main bridge. Use the matrix heatmap and scatter chart for category/segment detail.
6. Sort the visual by `Promo Leakage Waterfall[Step Order]` ascending. If the menu only shows `Step`, first confirm `Step` is sorted by `Step Order` in the table view.
7. In the formatting pane, turn the total column on. The total should equal `[Promo Margin %] * 100`.
8. Format the value as percentage points, not percent of total: data labels on, 1 decimal place, display units `None`, Y-axis title `Margin percentage points`.
9. Use colors consistently: baseline/total in a neutral or blue tone, negative leakage in red/orange.
10. Add a short text annotation: `Promo margin falls from ~20.0pp to ~1.3pp, implying ~18.7pp leakage under promoted orders.`

Expected visual check:

| Bar | Expected value | Meaning |
|---|---:|---|
| No-promo margin baseline | about `20.0` | Margin percentage points on non-promoted items |
| Promotion leakage | about `-18.7` | Lost margin percentage points from promoted items |
| Total | about `1.3` | Promo margin percentage points after leakage |

If Power BI does not show a total column in your version, keep the two-step waterfall and place a KPI card for `[Promo Margin %]` immediately to the right of it. Do not add a third bar unless you are using a custom waterfall visual that supports marking the final bar as a total.

Business takeaway:

```text
Promotion spend should be tightened in low-margin Streetwear segments, with minimum order thresholds and SKU exclusions.
```

### Page 4: Customer, Channel & Payment Risk

Target figure:

```text
docs/assets/figures/latex/04_payment_channel_risk.png
```

Purpose: separate high-volume revenue from high-quality revenue.

Visuals:

| Visual | Fields / measures | Notes |
|---|---|---|
| Donut chart | Legend `payment_method`; values `[Orders]` | Context only: show how large COD/prepaid workflows are |
| Scatter/bubble chart | X `[Payment Risk Rate]`; Y margin %; size revenue/orders; detail `order_source` | Separates volume from revenue quality |
| Treemap | Group `order_source`; value revenue; color by risk or margin if available | Shows channel contribution without another bar chart |
| Risk matrix | Rows payment method, columns order source, values risk rate | Conditional formatting identifies bad combinations |
| Action table | Recommendations filtered to payment/channel signals | Show risk score and recommended action |

Business takeaway:

```text
COD needs stricter workflow controls or prepaid incentives; marketing should shift toward channels with stronger revenue quality.
```

### Page 5: Returns, Reviews & Fulfillment

Target figure:

```text
docs/assets/figures/latex/05_returns_fulfillment_cx.png
```

Purpose: quantify customer-experience leakage.

Problem to avoid:

- Do not build Page 5 by mixing `orders_enriched` measures with `order_items_enriched` fields. The return reason, product category, size, refund amount, and item rating live at line-item grain.
- For Page 5 visuals, use `order_items_enriched` unless the guide explicitly says otherwise.
- Blank `top_return_reason` means the line item did not have a return record. For return-focused visuals, filter blank return reasons out.

Visuals:

| Visual | Fields / measures | Notes |
|---|---|---|
| Decomposition tree | Analyze `[Return Line Items]` or `[Refund Amount]`; explain by `top_return_reason`, `category`, `size`, `segment`, `payment_method`, `Line Fulfillment Bucket`, `ship_region`, `order_source` | Root-cause visual for return pressure |
| Matrix heatmap | Rows `category`; columns `size`; values `[Wrong Size Return Lines]` | Best view for sizing issue diagnosis |
| Combo chart | X-axis `Line Fulfillment Bucket`; column y-axis `[Line Items]`; line y-axis `[Return Line Rate]` | Shows operational volume and return risk together |
| Drillthrough detail page | Drill by `product_name` or `category`; show return, rating, refund, and fulfillment detail | Adds interaction depth for grading |
| Action table | Recommendations filtered to `Wrong-size return risk` | Converts the diagnosis into action |

Decomposition tree build steps:

1. Confirm the measures in `Line-level return and refund measures for Page 5` exist.
2. Insert the native `Decomposition tree` visual.
3. Put `[Return Line Items]` in `Analyze`.
4. Put these fields in `Explain by`, all from `order_items_enriched`: `top_return_reason`, `category`, `size`, `segment`, `payment_method`, `Line Fulfillment Bucket`, `ship_region`, `order_source`.
5. Add a visual-level filter: `top_return_reason is not blank`. This keeps the root cause tree focused on actual return records instead of all non-returned line items.
6. Click the `+` next to the root node and choose `top_return_reason`.
7. Select the `wrong_size` node. In the current prepared extract this should be the largest return-reason branch, about 14K returned line items.
8. Click the `+` next to `wrong_size` and choose `category`.
9. Click the largest category node, then choose `size`.
10. For a fourth level, choose either `Line Fulfillment Bucket` if you want an operations story, or `payment_method` if you want a refund/payment-risk story.

Recommended manual path for the CEO slide:

```text
Return Line Items
> top_return_reason = wrong_size
> category = largest affected category
> size = largest affected size
> Line Fulfillment Bucket or payment_method
```

Use manual splits for the final submission screenshot. Power BI also offers `High value` and `Low value` AI splits from the `+` menu, but manual splits are easier to reproduce and explain in grading.

Formatting:

1. Title: `Cây phân rã: Vì sao phát sinh trả hàng?`
2. Subtitle or annotation: `Wrong-size là nhánh trả hàng lớn nhất; ưu tiên xử lý theo category-size.`
3. Data label display units: `None`.
4. Values: whole number for `[Return Line Items]`; VND format if you switch `Analyze` to `[Refund Amount]`.
5. Turn on the tree connector lines and keep the visual wide enough for at least four levels.
6. Use this visual as the interactive driver: selecting a return reason or size should filter/highlight the heatmap and action table on the same page.

Troubleshooting:

| Problem | Fix |
|---|---|
| The tree is blank | Put a numeric measure in `Analyze`; do not put `top_return_reason`, `category`, or other text fields there. |
| `[Return Line Items]` errors or counts every row | In `Data view`, set `order_items_enriched[return_records]` to `Whole number`, then use the measure condition `return_records > 0`. |
| The `+` button does not show useful fields | Add fields to `Explain by`; the `+` menu only shows fields already placed there. |
| Return reason is mostly blank | Add the visual-level filter `top_return_reason is not blank`. Blank means the line item was not returned. |
| Category or size does not change the numbers | Use `order_items_enriched` fields for both the measure and `Explain by`; avoid mixing an `orders_enriched` measure with item-level explanation fields for this visual. |
| The visual only shows top categories | This is normal. Power BI decomposition trees show a limited top-N set per level; use the `wrong_size` branch plus the matrix heatmap for the detailed long tail. |
| AI split gives a different path from the guide | Use manual splits for the submitted screenshot; AI split can change after slicers or cross-filtering. |

#### Chart 5B: Wrong-Size Category x Size Heatmap

This is the chart that shows exactly which category-size combinations create the wrong-size return problem.

1. Click a blank area on Page 5.
2. In `Visualizations`, choose `Matrix`.
3. Drag `order_items_enriched[category]` into `Rows`.
4. Drag `order_items_enriched[size]` into `Columns`.
5. Drag `[Wrong Size Return Lines]` into `Values`.
6. In the `Filters on this visual` pane, add `order_items_enriched[top_return_reason]`.
7. Select only `wrong_size`.
8. Optional but useful: add `order_items_enriched[category]` and `order_items_enriched[size]` to the same visual filter area and remove blank values if Power BI shows any.
9. Sort by the value total descending so the biggest wrong-size problem appears first.
10. Format it as a heatmap: open the down-arrow next to `[Wrong Size Return Lines]` in the Values well, choose `Conditional formatting > Background color`, choose a light-to-dark color scale, with light for low values and red/orange for high values.
11. Turn `Column subtotals` and `Row subtotals` on if you want the CEO to see the total pressure by category and by size.
12. Title: `Wrong-size returns by category and size`.

Expected check: the strongest cells should align with the recommendation table. You should see `Streetwear / XL` as one of the high-priority combinations.

Common mistakes:

| Problem | Fix |
|---|---|
| The matrix shows all returns, not wrong-size returns | Make sure the visual-level filter selects only `top_return_reason = wrong_size`. |
| Conditional formatting option is missing | Click the down-arrow next to the measure inside `Values`; conditional formatting applies to values, not row/column labels. |
| The matrix is too wide | Keep only one measure in `Values`; use `[Wrong Size Return Lines]` first, not both lines and refund amount. |
| Sizes sort in a strange order | This is acceptable for the submission. If needed, manually order sizes in the visual or use a small size sort table later. |

#### Chart 5C: Fulfillment Delay vs Return Rate Combo Chart

This chart answers whether slower fulfillment is associated with higher return pressure. It is easier to reproduce if you keep it line-item based.

1. Click a blank area on Page 5.
2. Choose `Line and clustered column chart`.
3. Drag `order_items_enriched[Line Fulfillment Bucket]` into `X-axis`.
4. Drag `[Line Items]` into `Column y-axis`.
5. Drag `[Return Line Rate]` into `Line y-axis`.
6. In visual filters, add `order_items_enriched[Line Fulfillment Bucket]` and uncheck `No shipment`. This keeps the chart about delivered or fulfilled workflows.
7. Sort the X-axis by `Line Fulfillment Bucket Sort`, ascending. If it sorts as `0-3`, `11+`, `4-5`, go to `Data view`, select `Line Fulfillment Bucket`, and set `Sort by column` to `Line Fulfillment Bucket Sort`.
8. Format the line axis as a percentage: `Format visual > Secondary y-axis > Display units None`; set the title to `Return line rate`.
9. Format the column axis title as `Line items`.
10. Title: `Fulfillment delay and return pressure`.

Expected check: the columns show volume by fulfillment bucket, while the line shows the return rate. Do not use `[Orders]` here, because `[Orders]` comes from `orders_enriched` and can confuse the line-item filter context.

Common mistakes:

| Problem | Fix |
|---|---|
| The chart only shows one bucket | Add `Line Fulfillment Bucket` to `X-axis`, not to Legend. |
| The line is flat at 100% or 0% | Check that `[Return Line Rate] = [Return Line Items] / [Line Items]` and that `return_records` is Whole number. |
| Buckets are out of order | Set `Line Fulfillment Bucket` to sort by `Line Fulfillment Bucket Sort`. |
| Power BI asks for a column y-axis and line y-axis | Use `Line and clustered column chart`, not a normal column chart. |

#### Chart 5D: Product/Category Drillthrough Detail

This is not a normal chart. It is a hidden detail page you open by right-clicking a product or category in another visual.

1. Add a new report page.
2. Rename it `Return Detail`.
3. On the `Visualizations` pane, find the `Drill-through` field well.
4. Drag `order_items_enriched[product_name]` into `Drill-through`.
5. Also drag `order_items_enriched[category]` into `Drill-through`.
6. Keep the automatically added Back button. If Power BI does not add one, insert `Button > Back`.
7. Add four Card visuals:
   - `[Return Line Items]`
   - `[Refund Amount]`
   - `[Return Line Rate]`
   - `[Avg Line Rating]`
8. Add one Table visual with these fields:
   - `order_items_enriched[product_name]`
   - `order_items_enriched[category]`
   - `order_items_enriched[size]`
   - `order_items_enriched[top_return_reason]`
   - `order_items_enriched[payment_method]`
   - `order_items_enriched[Line Fulfillment Bucket]`
   - `[Return Line Items]`
   - `[Refund Amount]`
9. In the table visual filter, remove blank `top_return_reason`.
10. To use it, go back to Page 5, right-click a category or product mark, choose `Drill through`, then choose `Return Detail`.

If this feels too hard, keep the drillthrough page simple. The grading value comes from showing that a return-risk mark can open a deeper product/category explanation.

#### Chart 5E: Wrong-Size Action Table

1. Click a blank area on Page 5.
2. Choose `Table`.
3. Use fields from `recommendations`:
   - `priority`
   - `decision_owner`
   - `entity`
   - `risk_score`
   - `estimated_impact_vnd`
   - `recommended_action`
   - `tradeoff`
4. In visual filters, add `recommendations[signal_type]`.
5. Select only `Wrong-size return risk`.
6. Sort the table by `risk_score`, descending.
7. Turn on `Text wrap` for values and headers.
8. Format `risk_score` with conditional formatting or data bars so the highest-risk rows stand out.
9. Title: `Recommended actions for wrong-size returns`.

Business takeaway:

```text
Wrong-size returns are a measurable CX issue; category-size sizing guidance can reduce refund pressure.
```

### Page 6: Inventory Actions

Target figure:

```text
docs/assets/figures/latex/06_inventory_quadrant_actions.png
```

Purpose: distinguish stockout actions from overstock actions.

Problem to avoid:

- `inventory_monthly` has one row per product per month. If you do not filter to one month, product-level visuals combine many months and become hard to interpret.
- For the main inventory action page, filter all Page 6 visuals to the latest snapshot month: `snapshot_year_month = 2022-12`.
- If your scatter chart becomes one dot, you forgot the `Details` field.

Visuals:

| Visual | Fields / measures | Notes |
|---|---|---|
| Scatter | X `stockout_pressure_score`; Y `overstock_pressure_score`; Details `product_name`; Size `units_sold_3m_avg` | Add constant lines at 50/50 |
| Matrix heatmap | Rows category, columns segment, values `[Avg Stockout Pressure]` or `[Avg Overstock Pressure]` | Use conditional formatting or two small matrices |
| Treemap | Group product/category; value stock on hand or overstock exposure | Shows working capital concentration |
| KPI cards | `[Stockout Product Share]`, `[Overstock Product Share]` | Snapshot-based Page 6 KPIs |
| Action table | Recommendations filtered to stockout/overstock signals | Split replenish vs markdown/reduce receipts |

Before building Page 6:

1. Add a slicer or page-level filter using `inventory_monthly[snapshot_year_month]`.
2. Select only `2022-12`.
3. Keep this filter on every Page 6 inventory visual.

#### Chart 6A: Inventory Risk KPI Cards

Use these cards to anchor the page before the detailed visuals.

1. Add five Card visuals.
2. Put one measure in each card:
   - `[Inventory Products]`
   - `[Stockout Products]`
   - `[Overstock Products]`
   - `[Stockout Product Share]`
   - `[Overstock Product Share]`
3. Make sure the page filter is `snapshot_year_month = 2022-12`.
4. Format the share cards as percentages with one decimal place.
5. Suggested card titles:
   - `Products in snapshot`
   - `Stockout-risk products`
   - `Overstock-risk products`
   - `Stockout-risk share`
   - `Overstock-risk share`

Do not compare these directly to the older all-history KPI cards in `dashboard_kpis.csv`. Page 6 is intentionally snapshot-based for product action.

#### Chart 6B: Stockout vs Overstock Scatter Quadrant

This chart is the main inventory decision surface.

1. Click a blank area on Page 6.
2. Choose `Scatter chart`.
3. Drag `inventory_monthly[stockout_pressure_score]` into `X-axis`. Set aggregation to `Average`.
4. Drag `inventory_monthly[overstock_pressure_score]` into `Y-axis`. Set aggregation to `Average`.
5. Drag `inventory_monthly[product_name]` into `Values` or `Details`, depending on your Power BI field-well name. This creates one dot per product.
6. Drag `inventory_monthly[inventory_quadrant]` into `Legend`.
7. Drag `inventory_monthly[units_sold_3m_avg]` into `Size`. Set aggregation to `Sum` or `Average`; either is acceptable after filtering to one month.
8. Drag these into `Tooltips`:
   - `inventory_monthly[category]`
   - `inventory_monthly[segment]`
   - `inventory_monthly[stock_on_hand]`
   - `inventory_monthly[days_of_supply]`
   - `inventory_monthly[replenishment_priority]`
9. In visual filters, confirm `snapshot_year_month = 2022-12`.
10. Add quadrant guide lines if available: open the Analytics pane and add a constant line at `50` on the X-axis and another at `50` on the Y-axis.
11. Title: `Inventory action quadrant: stockout vs overstock pressure`.

Expected check for `2022-12`: the visual should show many `Overstock risk` products, fewer `Balanced/watch` products, and a small number of `Stockout risk` products. If there is only one dot, add `product_name` to `Details` or `Values`.

#### Chart 6C: Category x Segment Inventory Heatmap

This heatmap shows which merchandise groups carry the inventory risk.

Build the stockout version first:

1. Click a blank area on Page 6.
2. Choose `Matrix`.
3. Drag `inventory_monthly[category]` into `Rows`.
4. Drag `inventory_monthly[segment]` into `Columns`.
5. Drag `[Avg Stockout Pressure]` into `Values`.
6. Confirm the visual filter is `snapshot_year_month = 2022-12`.
7. Apply conditional formatting to `[Avg Stockout Pressure]`: `Values dropdown > Conditional formatting > Background color`.
8. Use a light-to-red scale, with darker red for higher pressure.
9. Title: `Stockout pressure by category and segment`.

Then duplicate it for overstock:

1. Copy and paste the matrix.
2. Replace `[Avg Stockout Pressure]` with `[Avg Overstock Pressure]`.
3. Change the title to `Overstock pressure by category and segment`.
4. Use a light-to-orange or light-to-purple scale.

If the page feels crowded, keep only one matrix and choose the one that supports your story. For this dataset, overstock pressure is usually more widespread, while stockout risk is more targeted.

#### Chart 6D: Overstock Working-Capital Treemap

This chart shows where stock is concentrated. It is useful for markdown or reduce-receipts decisions.

1. Click a blank area on Page 6.
2. Choose `Treemap`.
3. Drag `inventory_monthly[category]` into `Category`.
4. Drag `inventory_monthly[product_name]` into `Details`.
5. Drag `[Stock On Hand]` into `Values`.
6. In visual filters, set:
   - `snapshot_year_month = 2022-12`
   - `inventory_quadrant = Overstock risk`
7. Add `inventory_monthly[replenishment_priority]` to `Tooltips`.
8. Title: `Overstock concentration by category and product`.

If the treemap has too many tiny rectangles, remove `product_name` from `Details`. The chart will then show category-level concentration only, which is still acceptable.

#### Chart 6E: Inventory Action Table

1. Click a blank area on Page 6.
2. Choose `Table`.
3. Use fields from `recommendations`:
   - `priority`
   - `decision_owner`
   - `signal_type`
   - `entity`
   - `risk_score`
   - `estimated_impact_vnd`
   - `recommended_action`
   - `tradeoff`
4. In visual filters, add `recommendations[dashboard_page]`.
5. Select only `Inventory Actions`.
6. Sort by `risk_score`, descending.
7. Turn on text wrap.
8. Use conditional formatting or data bars on `risk_score`.
9. Title: `Inventory actions: replenish, monitor, markdown`.

Business takeaway:

```text
High-risk products need differentiated action: replenish stockout-prone demand, but reduce receipts or markdown slow movers.
```

## Optional Appendix Pages

### Page 7: Data Model & Validation

Target figure:

```text
docs/assets/figures/latex/07_data_model_validation.png
```

Use this page if your answer needs proof that the analysis is valid.

Problem to avoid:

- Do not try to make this page visually complex. It is an evidence page.
- Use tables, cards, and text boxes. The goal is to prove scope, relationships, and validation.

#### Chart 7A: Source File Scope Table

1. Add a Table visual.
2. Use fields from `source_manifest`:
   - `source_name`
   - `filename`
   - `status`
3. Sort by `status`, then `source_name`.
4. Title: `Source files used and excluded`.
5. Use conditional formatting on `status` if desired:
   - `used` = green
   - `excluded_by_scope` = gray

Expected check: 13 files should be marked `used`; `sample_submission.csv`, `baseline.ipynb`, and `sales_test.csv` should be excluded.

#### Chart 7B: Prepared Extract Row Count Table

1. Add a Table visual.
2. Use fields from `data_dictionary`:
   - `table_name`
   - `row_count`
3. In the visual, remove duplicates by changing the view if needed:
   - Easiest method: use a Matrix instead of a Table.
   - Rows: `table_name`
   - Values: `row_count`
   - Aggregation: `Maximum`
4. Title: `Prepared analytical extracts`.

Expected row counts include:

| Extract | Expected rows |
|---|---:|
| `orders_enriched` | `646,945` |
| `order_items_enriched` | `714,669` |
| `daily_kpi` | `3,833` |
| `inventory_monthly` | `60,247` |
| `recommendations` | `16` |

#### Chart 7C: Data Model Sketch

Use Power BI shapes and text boxes. This does not need to be data-driven.

1. Insert text boxes for:
   - `DimDate`
   - `orders_enriched`
   - `order_items_enriched`
   - `inventory_monthly`
   - `daily_kpi`
   - `recommendations`
2. Draw arrows or lines:
   - `DimDate -> orders_enriched`
   - `orders_enriched -> order_items_enriched`
   - `DimDate -> daily_kpi`
   - `DimDate -> inventory_monthly`
3. Add a warning note: `Do not keep an active DimDate -> order_items_enriched relationship when orders_enriched already connects to DimDate.`

#### Chart 7D: Validation Guardrail Cards

Use text boxes or Card visuals:

- `13 business CSVs used`
- `Excluded sample_submission, baseline, sales_test`
- `Revenue reconciliation gap: 0 VND`
- `Predictive signals use historical Part 2 data only`

If using Card visuals from `dashboard_kpis`, use a visual-level filter on `kpi_name` for each card. If that is too slow, use text boxes. For an appendix proof page, text boxes are acceptable because the values are validated in the preparation report.

### Page 8: Prescriptive Action Roadmap

Target figure:

```text
docs/assets/figures/latex/08_prescriptive_action_roadmap.png
```

Use this as a final CEO recommendation page.

Problem to avoid:

- Do not create this page from the raw transaction tables. Use `recommendations.csv`.
- This page should answer "what should the CEO do next?", not re-explain every analysis.

Recommended visuals:

| Visual | Fields / measures | Notes |
|---|---|---|
| Swimlane matrix | Rows `decision_owner`; columns `signal_type`; values `[Action Count]` or `[Estimated Impact VND]` | Shows who owns each action theme |
| Bubble chart | X `risk_score`; Y `estimated_impact_vnd`; details `entity`; legend `priority`; size `estimated_impact_vnd` | Prioritizes action by risk and impact |
| Action table | `priority`, `dashboard_page`, `entity`, `recommended_action`, `tradeoff`, `evidence` | Final CEO action list |

#### Chart 8A: Owner x Action Theme Matrix

1. Add a Matrix visual.
2. Drag `recommendations[decision_owner]` into `Rows`.
3. Drag `recommendations[signal_type]` into `Columns`.
4. Drag `[Action Count]` into `Values`.
5. Optional: replace `[Action Count]` with `[Estimated Impact VND]` if you want an impact-weighted matrix.
6. Sort rows by total descending.
7. Apply background-color conditional formatting to the value.
8. Title: `Action ownership by risk theme`.

#### Chart 8B: Risk vs Impact Bubble Chart

1. Add a Scatter chart.
2. Drag `recommendations[risk_score]` into `X-axis`. Set aggregation to `Average`.
3. Drag `recommendations[estimated_impact_vnd]` into `Y-axis`. Set aggregation to `Sum` or `Average`; with one row per action, either gives the same point.
4. Drag `recommendations[entity]` into `Values` or `Details`. This creates one dot per recommendation entity.
5. Drag `recommendations[priority]` into `Legend`.
6. Drag `recommendations[estimated_impact_vnd]` into `Size`.
7. Drag these into `Tooltips`:
   - `recommendations[dashboard_page]`
   - `recommendations[signal_type]`
   - `recommendations[recommended_action]`
   - `recommendations[tradeoff]`
8. Title: `Prioritize actions by risk and estimated impact`.

If the chart becomes one dot, add `recommendations[entity]` to `Details` or `Values`.

#### Chart 8C: CEO Action Table

1. Add a Table visual.
2. Use fields from `recommendations`:
   - `priority`
   - `dashboard_page`
   - `decision_owner`
   - `entity`
   - `risk_score`
   - `estimated_impact_vnd`
   - `recommended_action`
   - `tradeoff`
   - `evidence`
3. Sort by `priority` and then by `risk_score` descending.
4. If priority does not sort correctly, select `recommendations[priority]` and sort it by `Priority Sort`.
5. Turn on text wrap.
6. Use conditional formatting or data bars on `risk_score` and `estimated_impact_vnd`.
7. Title: `CEO action roadmap`.

Recommended grouping language for your presentation:

- Protect margin.
- Reduce failed demand.
- Fix customer leakage.
- Balance inventory.
- Release capital.
- Shift marketing spend.

## Interactions

Power BI defaults to cross-filtering or cross-highlighting many visuals on the same page. Configure this deliberately.

Recommended setup:

| Interaction | Power BI implementation |
|---|---|
| Overview filter action | Use slicers synced across pages; set visual interactions to filter relevant charts |
| Highlight action | Use default visual selection behavior for category, segment, payment, and channel charts |
| Drill action | Create drillthrough pages for `category`, `product_name`, and `payment_method` |
| Return reason action | Use the Page 5 decomposition tree or wrong-size heatmap to filter category-size and refund visuals |
| Inventory quadrant action | Select scatter points or quadrant categories to filter inventory action table |
| Reset control | Add a button linked to a reset bookmark with default slicer state |

To configure visual interactions:

1. Select a visual.
2. Go to `Format > Edit interactions`.
3. For each other visual, choose filter, highlight, or none.

To create drillthrough:

1. Add a new detail page, for example `Product Detail`.
2. Drag `order_items_enriched[product_name]` or `order_items_enriched[category]` into the Drill-through well.
3. Add product-level margin, return, and inventory visuals.
4. Keep the automatically added Back button.

To create reset behavior:

1. Clear filters to the intended default state.
2. Open `View > Bookmarks`.
3. Add a bookmark named `Reset`.
4. Insert a button, set Action to Bookmark, and select `Reset`.

## Validation Checklist

Before exporting, verify these numbers:

| Metric | Expected |
|---|---:|
| Revenue | 16.43B VND |
| Gross margin | 2.27B VND |
| Gross margin % | 13.8% |
| Orders | 646,945 |
| Customers | 90,246 |
| Cancel rate | 9.2% |
| Return-record rate | 5.6% |
| COD risk rate | 24.9% |
| Promo margin % | 1.3% |
| No-promo margin % | 20.0% |
| Inventory stockout share | 67.3% |
| Inventory overstock share | 76.3% |

Also verify:

- `sales.csv` revenue equals item-level estimated revenue: gap `0.00`.
- The report does not import `sample_submission.csv`, `baseline.ipynb`, or `sales_test.csv`.
- Predictive pages use `growth_forecast_monthly.csv`, `seasonality_indices.csv`, `predictive_signals.csv`, and historical facts only.
- Page filters do not accidentally remove rows from KPI cards unless the page is intentionally interactive.

## Export for LaTeX

Power BI Desktop PDF export:

1. Open the `.pbix`.
2. Go to `File > Export > Export to PDF`.
3. Confirm every page is visible before export. Hidden pages are not exported from Desktop.
4. Use the PDF in LaTeX directly, or convert individual pages to PNG if your answer template requires images.

If you only need the already verified rendered figures, use:

```text
D:\Code\Coding\data-visualization-skills\projects\vindatathon-2026-task2-tableau\docs\assets\figures\latex
```

Ready-to-use LaTeX snippets:

```text
D:\Code\Coding\data-visualization-skills\projects\vindatathon-2026-task2-tableau\docs\assets\figures\latex\latex_include_figures.tex
```

## Suggested Written Narrative

Use this short structure in the report:

1. Business health: 16.43B VND revenue, 13.8% margin, meaningful scale.
2. Leakage diagnosis: promo margin collapses to 1.3%, COD risk is 24.9%, returns and inventory pressure are material.
3. Predictive signal: March-June are stronger seasonal demand months, with May as the strongest seasonality index.
4. CEO actions: tighten promotions, reduce COD risk, fix wrong-size returns, replenish stockout-risk SKUs, markdown overstock, and shift spend to high-quality channels.

## Official Power BI References

- Get data from files: <https://learn.microsoft.com/en-us/power-bi/connect-data/service-get-data-from-files>
- Create and manage relationships: <https://learn.microsoft.com/en-us/power-bi/transform-model/desktop-create-and-manage-relationships>
- Create measures: <https://learn.microsoft.com/en-us/power-bi/transform-model/desktop-measures>
- Visual interactions: <https://learn.microsoft.com/en-us/power-bi/create-reports/service-reports-visual-interactions>
- Filters and highlighting: <https://learn.microsoft.com/en-us/power-bi/create-reports/power-bi-reports-filters-and-highlighting>
- Decomposition tree visual: <https://learn.microsoft.com/en-us/power-bi/visuals/power-bi-visualization-decomposition-tree>
- Matrix and table conditional formatting: <https://learn.microsoft.com/en-us/power-bi/create-reports/desktop-conditional-table-formatting>
- Combo chart: <https://learn.microsoft.com/en-us/power-bi/visuals/power-bi-visualization-combo-chart>
- Scatter and bubble chart: <https://learn.microsoft.com/en-us/power-bi/visuals/power-bi-visualization-scatter>
- Treemap: <https://learn.microsoft.com/en-us/power-bi/visuals/power-bi-visualization-treemaps>
- Drillthrough: <https://learn.microsoft.com/en-us/power-bi/create-reports/desktop-drillthrough>
- Export to PDF: <https://learn.microsoft.com/en-us/power-bi/consumer/end-user-pdf>

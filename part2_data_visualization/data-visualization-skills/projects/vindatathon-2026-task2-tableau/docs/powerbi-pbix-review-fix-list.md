# Power BI PBIX Review And Fix List

Reviewed file:

```text
docs/assets/powerbi/VinDatathon_Task2_PowerBI.pbix
```

Review method:

- Inspected the readable `Report/Layout` metadata inside the `.pbix`.
- Checked page names, visual types, field bindings, visual filters, page filters, slicer state, and drillthrough filters.
- Compared the report structure against `powerbi-rebuild-guide.md`, the prepared-data contract, and the scoring goal: descriptive, diagnostic, predictive, and prescriptive analysis.

Important limitation:

- This review did not visually render the report canvas in Power BI Desktop. It checks report structure and likely semantic mistakes. After applying the fixes, export screenshots/PDF and visually inspect spacing, labels, and readability.

## Overall Assessment

The report is a strong first build. It contains most required main dashboards:

| Page found in PBIX | Status |
|---|---|
| Executive Scorecard | Present |
| Predictive growth and seasonality | Present |
| Profit and promotion leakage | Present |
| Customer, Channel & Payment Risk | Present |
| Returns, Reviews & Fulfillment | Present |
| Return Detail | Present as visible drillthrough/detail page |
| Inventory Actions | Present |

Main score risks:

1. Several date slicers appear to be copied from the inventory page and are set around December 2022.
2. The Return Detail page has a saved drillthrough filter for `GenZ`, so it may show one tested category instead of behaving as a clean drillthrough page.
3. The channel-risk scatter uses an official gross margin measure that may not slice correctly by channel.
4. Inventory slicer/filter fields should be inventory or dimension fields, not `order_items_enriched` fields.
5. High-score appendix pages are missing: data validation/model proof and final CEO action roadmap.

Fix the P0 items first. They are the most likely to create wrong numbers or confusing screenshots.

## P0 Fixes: Must Fix Before Final Export

### P0-1. Clear Wrong Date Slicer State On Pages 1-5

Evidence found:

- Pages 1, 2, 3, 4, and 5 have a `DimDate[Date]` slicer.
- The slicer metadata contains a December 2022 state and an `inventory_monthly[snapshot_year_month]` filter.
- That is appropriate for the inventory page only, not for revenue, forecast, promotion, payment, or returns pages.

Why this matters:

- It can accidentally make the report look like it is analyzing only one month.
- It can weaken the CEO story because the dashboard should mostly explain the full historical Part 2 period, while only the inventory action page should focus on the latest snapshot month.

How to fix in Power BI Desktop:

1. Open the report.
2. Go to Page 1: `Executive Scorecard`.
3. Click the date slicer.
4. In the slicer itself, click the clear/eraser icon.
5. In the `Filters on this visual` pane, remove any filter from `inventory_monthly[snapshot_year_month]`.
6. Repeat steps 3-5 on:
   - `Predictive growth and seasonality`
   - `Profit and promotion leakage`
   - `Customer, Channel & Payment Risk`
   - `Returns, Reviews & Fulfillment`
7. Go to `View > Sync slicers`.
8. Make sure the inventory month slicer is not synced into Pages 1-5.
9. Keep `snapshot_year_month = 2022-12` only on the `Inventory Actions` page.

Expected result:

- Pages 1, 3, 4, and 5 should show full historical business behavior unless you manually choose a date filter.
- Page 2 should show historical trend plus forecast period.
- Page 6 or Inventory Actions should keep the `2022-12` inventory snapshot filter.

### P0-2. Fix Return Detail Page Saved Filter

Evidence found:

- `Return Detail` has page-level filters:
  - `order_items_enriched[category] = GenZ`
  - `order_items_enriched[product_name]` as a drillthrough field

Why this matters:

- If you export the page, it may show only `GenZ` because that was the last tested drillthrough context.
- A drillthrough page should wait for the selected product/category from the source page.

How to fix:

1. Go to the `Return Detail` page.
2. Open the `Filters` pane.
3. Find the page-level filter for `order_items_enriched[category]`.
4. Clear the selected value `GenZ`.
5. Keep `order_items_enriched[category]` in the drillthrough field well if you want category drillthrough.
6. Keep `order_items_enriched[product_name]` in the drillthrough field well if you want product drillthrough.
7. Turn `Keep all filters` on for the drillthrough section.
8. Test it:
   - Go to Page 5.
   - Right-click a category or product mark.
   - Choose `Drill through > Return Detail`.
   - Confirm the detail page changes based on the selected item.

Recommendation:

- If the page is for interaction only, right-click the `Return Detail` tab and choose `Hide page`.
- If you want it included in the PDF/LaTeX screenshots, keep it visible but rename it `Appendix - Return Detail` and move it after `Inventory Actions`.

### P0-3. Fix Channel Quality Scatter Margin Measure

Evidence found:

- Page 4 scatter chart `Channel Quality: Margin vs. Risk` uses:
  - X-axis: `Payment Risk Rate`
  - Y-axis: `Gross Margin %`
  - Detail: `orders_enriched[order_source]`

Why this matters:

- `Gross Margin %` is an official overall sales/daily KPI. It may not slice correctly by `order_source`.
- If it does not slice by channel, every source can appear to have the same margin, which weakens the diagnostic insight.

How to fix:

1. Go to `Customer, Channel & Payment Risk`.
2. Click the scatter chart `Channel Quality: Margin vs. Risk`.
3. Remove `[Gross Margin %]` from the Y-axis.
4. Add `[Line Margin %]` to the Y-axis.
5. Use `[Line Revenue]` or `[Orders]` as bubble size.
6. Keep `orders_enriched[order_source]` or `order_items_enriched[order_source]` as Details.
7. If the chart collapses into one dot, put `order_source` into `Details`.
8. Rename the Y-axis to `Line margin %`.

Expected result:

- Different channels should show different margin/risk positions.
- The visual should separate high-volume channels from high-quality channels.

### P0-4. Replace Inventory Page Category Slicer

Evidence found:

- `Inventory Actions` has a category slicer using `order_items_enriched[category]`.
- The page visuals are built from `inventory_monthly`.

Why this matters:

- A slicer from one fact table may not filter another fact table if relationships are single-direction or disconnected.
- The inventory page should use `inventory_monthly[category]` or `DimProduct[category]`.

How to fix:

1. Go to `Inventory Actions`.
2. Click the category slicer.
3. Remove `order_items_enriched[category]`.
4. Add one of these instead:
   - Recommended simple choice: `inventory_monthly[category]`
   - Model-clean choice: `DimProduct[category]`
5. Test by selecting `Streetwear`.
6. Confirm the scatter, heatmap, treemap, and KPI cards all change.

Expected result:

- Category selections should visibly filter the inventory visuals.

## P1 Fixes: High-Score Improvements

### P1-1. Add Missing Promotion Heatmap On Page 3

Evidence found:

- Page 3 has cards, waterfall, scatter, action table, and slicers.
- It does not appear to have the recommended category x segment promotion leakage heatmap.

Why this helps scoring:

- It adds diagnostic depth and visual diversity.
- It shows exactly where promotion leakage is concentrated.

How to add:

1. Go to `Profit and promotion leakage`.
2. Add a `Matrix` visual.
3. Rows: `DimProduct[category]` or `order_items_enriched[category]`.
4. Columns: `DimProduct[segment]` or `order_items_enriched[segment]`.
5. Values: `[Promo Margin Gap pp]`.
6. Apply conditional formatting to the value background.
7. Use red/orange for larger leakage.
8. Title: `Promotion leakage by category and segment`.

### P1-2. Add Stockout Heatmap Or Toggle On Inventory Page

Evidence found:

- `Inventory Actions` has an overstock pressure matrix.
- It does not appear to include a separate stockout pressure matrix.

Why this helps scoring:

- The inventory story should cover both failed demand and excess working capital.
- Overstock is widespread, but stockout is more urgent for high-demand products.

Simple fix:

1. Copy the existing overstock pressure matrix.
2. Replace `[Avg Overstock Pressure]` with `[Avg Stockout Pressure]`.
3. Change the title to `Stockout pressure by category and segment`.
4. Use a red color scale.
5. Keep the page filter `snapshot_year_month = 2022-12`.

If the page is crowded:

- Keep both matrices smaller side by side.
- Or use only the stockout matrix and explain overstock through the scatter and treemap.

### P1-3. Fix Inventory Treemap Title Or Add Product Detail

Evidence found:

- The treemap title is `Overstock concentration by category and product`.
- The detected fields include category and stock on hand, but product detail was not detected in the treemap field bindings.

Choose one fix:

Option A, keep category-only treemap:

1. Rename the title to `Overstock concentration by category`.
2. Keep `inventory_monthly[category]` and `[Stock On Hand]`.

Option B, show product detail:

1. Add `inventory_monthly[product_name]` to `Details`.
2. Keep `inventory_monthly[category]` in `Category`.
3. Keep `[Stock On Hand]` in `Values`.
4. If the treemap becomes too busy, switch back to Option A.

### P1-4. Add A Final CEO Action Roadmap Page

Evidence found:

- The report has action tables on individual pages.
- It does not have a final combined action roadmap page.

Why this helps scoring:

- It strengthens the Prescriptive part of the rubric.
- It gives the CEO one final decision page.

How to add:

1. Add a new page after `Inventory Actions`.
2. Name it `CEO Action Roadmap`.
3. Add a Matrix:
   - Rows: `recommendations[decision_owner]`
   - Columns: `recommendations[signal_type]`
   - Values: `[Action Count]` or `[Estimated Impact VND]`
4. Add a Scatter chart:
   - X-axis: `recommendations[risk_score]`
   - Y-axis: `recommendations[estimated_impact_vnd]`
   - Details: `recommendations[entity]`
   - Legend: `recommendations[priority]`
   - Size: `recommendations[estimated_impact_vnd]`
5. Add a Table:
   - `priority`
   - `dashboard_page`
   - `decision_owner`
   - `entity`
   - `risk_score`
   - `estimated_impact_vnd`
   - `recommended_action`
   - `tradeoff`
6. Add a text box with the final message:
   - Tighten margin-destructive promotions.
   - Reduce COD risk.
   - Fix wrong-size returns.
   - Replenish stockout-risk SKUs.
   - Markdown or reduce receipts for overstock.
   - Shift spend to higher-quality channels.

### P1-5. Add Data Model And Validation Appendix Page

Evidence found:

- No separate data validation/model proof page was found.

Why this helps scoring:

- The task rubric rewards technical correctness and credible data handling.
- This page proves that you used the correct files and ignored excluded files.

How to add:

1. Add a new page named `Data Model & Validation`.
2. Add a source manifest table:
   - `source_manifest[source_name]`
   - `source_manifest[filename]`
   - `source_manifest[status]`
3. Add an extract row-count matrix:
   - Rows: `data_dictionary[table_name]`
   - Values: `Max(data_dictionary[row_count])`
4. Add text boxes:
   - `13 business CSVs used`
   - `sample_submission.csv, baseline.ipynb, and sales_test.csv excluded`
   - `Revenue reconciliation gap: 0 VND`
   - `Predictive signals use historical Part 2 data only`
5. Add a simple relationship sketch using text boxes and lines:
   - `DimDate -> orders_enriched`
   - `orders_enriched -> order_items_enriched`
   - `DimDate -> daily_kpi`
   - `DimDate -> inventory_monthly`

### P1-6. Add Reset Buttons

Evidence found:

- Only one action button was found, on `Return Detail`.
- Main report pages do not appear to have reset buttons.

Why this helps scoring:

- Reset/revert behavior was part of the interaction plan.
- It prevents presentation mistakes when slicers are changed.

How to add a reset button:

1. Clear slicers and filters to the default state on a page.
2. Open `View > Bookmarks`.
3. Add a bookmark named `Reset - Page Name`.
4. Insert `Button > Reset` or `Button > Blank`.
5. Set Button action to `Bookmark`.
6. Choose the matching reset bookmark.
7. Repeat for each main page.

## P2 Polish: Improve Readability And Grading Impression

### P2-1. Standardize Page Names

Current detected names:

- `Executive Scorecard`
- `Predictive growth and seasonality`
- `Profit and promotion leakage`
- `Customer, Channel & Payment Risk`
- `Returns, Reviews & Fulfillment`
- `Return Detail`
- `Inventory Actions`

Recommended names:

1. `Executive Overview`
2. `Growth Forecast & Seasonality`
3. `Profit & Promotion Leakage`
4. `Customer, Channel & Payment Risk`
5. `Returns, Reviews & Fulfillment`
6. `Inventory Actions`
7. `Appendix - Return Detail` or hidden drillthrough page
8. `Data Model & Validation`
9. `CEO Action Roadmap`

### P2-2. Add Vietnamese Business Takeaways

Most page titles detected in the PBIX are English. That is acceptable for internal work, but the original task is Vietnamese and asks for persuasive dashboard storytelling.

Add one short Vietnamese takeaway text box per main page. Keep it business-focused, not technical.

Examples without accents if your font setup is unstable:

- `Tang truong co that, nhung loi nhuan bi ro ri qua khuyen mai, COD, return va ton kho.`
- `Khuyen mai can duoc gioi han o cac nhom co bien loi nhuan thap.`
- `Wrong-size la nhanh return lon nhat; can uu tien huong dan size theo category-size.`
- `Ton kho can tach thanh hai hanh dong: bo sung hang stockout-risk va markdown overstock.`

### P2-3. Standardize Slicers

Recommended slicer fields:

| Page | Recommended slicers |
|---|---|
| Executive / Growth / Promotion / Payment | `DimDate[Date]`, `DimProduct[category]`, optional `orders_enriched[ship_region]` |
| Returns | `order_items_enriched[category]`, `order_items_enriched[top_return_reason]`, optional `order_items_enriched[payment_method]` |
| Inventory | `inventory_monthly[snapshot_year_month]`, `inventory_monthly[category]`, `inventory_monthly[inventory_quadrant]` |
| Action Roadmap | `recommendations[priority]`, `recommendations[signal_type]`, `recommendations[decision_owner]` |

Avoid using a slicer from one fact table to filter another fact table unless you have tested it.

## Final Pre-Export Checklist

Before exporting the PDF or screenshots:

1. Clear the wrong December 2022 slicer state from Pages 1-5.
2. Confirm only `Inventory Actions` is locked to `snapshot_year_month = 2022-12`.
3. Confirm Page 4 channel scatter uses `[Line Margin %]`, not `[Gross Margin %]`.
4. Confirm `Inventory Actions` category slicer filters the scatter and treemap.
5. Confirm `Return Detail` is either hidden or clearly labeled as an appendix.
6. Add the Page 3 promo leakage heatmap.
7. Add a stockout pressure view on the inventory page.
8. Add reset buttons or at least a clear reset bookmark.
9. Add the `Data Model & Validation` appendix page.
10. Add the `CEO Action Roadmap` final page.
11. Export to PDF and inspect every page visually for overlapping text and unreadable legends.


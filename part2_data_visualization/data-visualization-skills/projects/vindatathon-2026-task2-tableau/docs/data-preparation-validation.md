# Tableau Data Preparation Validation

## Scope

- Part 2 only.
- Used the 13 approved business CSVs from `projects/data/`.
- Excluded `sample_submission.csv`, `baseline.ipynb`, and unavailable `sales_test.csv`.

## Output Row Counts

- `orders_enriched`: 646,945 rows
- `order_items_enriched`: 714,669 rows
- `daily_kpi`: 3,833 rows
- `inventory_monthly`: 60,247 rows
- `growth_forecast_monthly`: 132 rows
- `seasonality_indices`: 19 rows
- `predictive_signals`: 62 rows
- `recommendations`: 16 rows
- `dashboard_kpis`: 13 rows

## Key Integrity Checks

- orders.order_id unique: PASS
- payments.order_id unique: PASS
- products.product_id unique: PASS
- customers.customer_id unique: PASS
- geography.zip unique: PASS
- order_items order_id coverage: 100.00%
- payments order_id coverage: 100.00%
- shipments order_id coverage: 100.00%
- returns order_id coverage: 100.00%
- reviews order_id coverage: 100.00%
- orders customer coverage: 100.00%
- orders shipping zip coverage: 100.00%
- inventory product coverage: 100.00%

Coverage note: the source `shipments.csv` contains 566,067 distinct order IDs, while `orders.csv` contains 646,945 orders. The shipment coverage check above means all shipment records map back to valid orders; it does not mean every order has a shipment row.

## Orders Enriched Missingness Note

`orders_enriched.csv` is not broadly empty:

- Rows: 646,945
- Columns: 61
- File-wide blank-cell rate: 7.24%
- Columns with no blanks: 50 / 61
- Columns above 80% blank: 4 / 61

Expected sparse event columns:

- `top_return_reason` and `first_return_date`: 94.43% blank because only 36,062 orders have return records.
- `avg_rating` and `order_avg_rating`: 82.79% blank because only 111,369 orders have reviews.
- Shipment fields: 12.50% blank because 80,878 orders have no shipment row, mostly cancelled/created/paid orders.

See `orders-enriched-null-policy.md` and `docs/assets/exports/tableau/orders_enriched_missingness.csv`.

## Order Items Enriched Missingness Note

`order_items_enriched.csv` has no columns that are 100% blank across the full file:

- Rows: 714,669
- Columns: 65
- File-wide blank-cell rate: 20.35%
- Columns with no blanks: 44 / 65
- Columns at 100% blank: 0 / 65

Expected sparse fields:

- `promo_id_2`: 99.97% blank because only 206 line items have a second stacked promotion.
- `applicable_category`: 95.82% blank because most promotion definitions are global, with blank category in `promotions.csv`.
- Return fields: 94.41% blank because only 39,939 line items have return records.
- Review fields: 84.11% blank because only 113,553 line items have reviews.
- Promotion metadata fields: 61.34% blank because 38.66% of line items have a primary promotion.
- Shipment fields: 12.49% blank because the parent order has no shipment row.

If Power BI shows some of these as 100% empty, switch Power Query column profiling from the first 1,000 rows to the entire dataset. The first 1,000 line items are early rows before promotion activity appears.

See `order-items-enriched-null-policy.md` and `docs/assets/exports/tableau/order_items_enriched_missingness.csv`.

## Revenue Reconciliation Note

- `sales.csv` total revenue: 16,430,476,585.53
- item-level estimated revenue: 16,430,476,585.53
- item minus sales gap: 0.00

`sales.csv` remains the official daily revenue/COGS source for executive totals and forecasting signals. Item-level revenue is used for diagnostic slicing where product, promotion, customer, and fulfillment fields are required.

## Predictive EDA Guardrail

Forecast, seasonality, stockout, return, promotion, and channel signals are historical EDA indicators only. They do not use `sales_test.csv`, `sample_submission.csv`, or external data.

# Order Items Enriched Null Policy

`order_items_enriched.csv` is a line-item grain table. It intentionally combines every order item with optional promotion, return, review, and order-shipment context. Some columns are therefore sparse by business design.

## Short Answer

There are no columns that are actually `100%` empty across the full `order_items_enriched.csv`.

Measured directly from the file:

- Rows: `714,669`
- Columns: `65`
- Total cells: `46,453,485`
- Blank cells: `9,455,526`
- File-wide blank-cell rate: `20.35%`
- Columns with no blanks: `44 / 65`
- Columns at `100%` blank: `0 / 65`

If Power BI shows some columns as `100%` empty, it is likely using the default Power Query profile based on the first 1,000 preview rows. Microsoft documents that Power Query profiling defaults to the first 1,000 rows unless you switch it to the entire dataset.

## Highest-Sparsity Columns

| Column | Blank rate | Meaning |
|---|---:|---|
| `promo_id_2` | 99.97% | A second stacked promotion is extremely rare |
| `applicable_category` | 95.82% | Most promotions are global; source `promotions.csv` has blank category for global promos |
| `top_return_reason` | 94.41% | Line item has no return record |
| `first_return_date` | 94.41% | Line item has no return record |
| `avg_rating` | 84.11% | Line item has no review |
| `min_rating` | 84.11% | Line item has no review |
| `top_review_title` | 84.11% | Line item has no review |
| `first_review_date` | 84.11% | Line item has no review |
| Promotion metadata fields | 61.34% | Line item has no promotion |
| Shipment fields | 12.49% | Parent order has no shipment row |

## Source Consistency Checks

The sparse fields match the raw source data:

| Source / field | Nonblank count | Share |
|---|---:|---:|
| `order_items.promo_id` | 276,316 | 38.66% |
| `order_items.promo_id_2` | 206 | 0.03% |
| `promotions.applicable_category` | 10 of 50 promotions | 20.00% of promo definitions |
| line items with return reason | 39,939 | 5.59% |
| line items with review rating | 113,553 | 15.89% |
| line items with shipment fee | 625,382 | 87.51% |

The first 1,000 rows have no promotion IDs because they are early historical rows before the first promotion period in the source data. In Power Query's default preview profile, that can make promotion columns look `100%` empty even though the full dataset contains 276,316 promoted line items.

## Should We Change The Data?

Do not globally fill all blanks.

Recommended handling:

| Column group | Action |
|---|---|
| `promo_id_2` | Hide or drop in Power BI unless analyzing stacked promotions |
| Promotion metadata | Keep null for non-promoted line items; use `has_promo` for filtering |
| `applicable_category` | Keep null; blank means global promotion in the source data |
| Return fields | Keep null for no-return lines; create display label only for charts |
| Review fields | Keep numeric ratings null; create `No review` label only for charts |
| Shipment fields | Keep null for no-shipment orders; exclude nulls from duration averages |

## Power BI Display Columns

Use calculated columns or Power Query custom columns for labels. Keep numeric/date columns null for calculations.

```DAX
Promotion Status =
IF ( order_items_enriched[has_promo] = TRUE (), "Promoted", "No promotion" )
```

```DAX
Second Promotion Status =
IF ( order_items_enriched[has_second_promo] = TRUE (), "Stacked promo", "No second promo" )
```

```DAX
Applicable Category Label =
COALESCE ( order_items_enriched[applicable_category], "Global / all categories" )
```

```DAX
Return Reason Label =
COALESCE ( order_items_enriched[top_return_reason], "No return record" )
```

```DAX
Review Status =
IF ( ISBLANK ( order_items_enriched[avg_rating] ), "No review", "Reviewed" )
```

## Optional Power BI Cleanup

For a cleaner model, hide these fields from report view:

- `promo_id_2`
- `top_review_title`
- `first_review_date`
- `first_return_date`

Keep them in the model only if you need drillthrough details or auditability.

## Generated Profile

Column-level missingness is recorded here:

```text
docs/assets/exports/tableau/order_items_enriched_missingness.csv
```

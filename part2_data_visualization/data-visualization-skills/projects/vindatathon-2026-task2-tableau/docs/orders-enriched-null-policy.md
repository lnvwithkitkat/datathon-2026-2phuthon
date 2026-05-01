# Orders Enriched Null Policy

`orders_enriched.csv` has expected sparse columns because it combines the base order table with optional event tables: returns, reviews, and shipments.

## Short Answer

There is no evidence that `orders_enriched.csv` is 82% empty overall.

Measured directly from the file:

- Rows: `646,945`
- Columns: `61`
- Total cells: `39,463,645`
- Blank cells: `2,859,064`
- File-wide blank-cell rate: `7.24%`
- Columns with no blanks: `50 / 61`
- Columns above 80% blank: `4 / 61`

The `82%` value likely comes from Power BI's column quality view for rating fields:

| Column | Blank rate | Interpretation |
|---|---:|---|
| `avg_rating` | 82.79% | Expected: most orders have no review |
| `order_avg_rating` | 82.79% | Expected: most orders have no review |
| `top_return_reason` | 94.43% | Expected: most orders have no return |
| `first_return_date` | 94.43% | Expected: most orders have no return |

## Why These Nulls Are Expected

The source data confirms the sparse event pattern:

| Source table / event | Count |
|---|---:|
| Orders | 646,945 |
| Orders with review count greater than 0 | 111,369 |
| Orders with return record | 36,062 |
| Orders with shipment row | 566,067 |

Consistency checks:

- `review_count > 0` exactly matches nonblank `avg_rating` and `order_avg_rating`.
- `has_return_record = TRUE` exactly matches nonblank `top_return_reason` and `first_return_date`.
- Shipping fields are blank where no shipment row exists.

## Shipping Nulls

Shipment-related fields are blank for `80,878` orders (`12.50%`):

- `ship_date`
- `delivery_date`
- `shipping_fee`
- `ship_delay_days`
- `delivery_days`
- `fulfillment_days`
- `late_fulfillment_flag`

Breakdown by `order_status` for blank `ship_date`:

| Order status | Blank `ship_date` count |
|---|---:|
| cancelled | 59,462 |
| paid | 13,577 |
| created | 7,275 |
| delivered | 524 |
| returned | 29 |
| shipped | 11 |

Most shipment nulls are expected for cancelled or not-yet-shipped orders. The `564` delivered/returned/shipped rows without shipment fields are a small source data anomaly, about `0.09%` of all orders. Keep them as nulls and exclude null `fulfillment_days` from fulfillment-duration averages.

## Power BI Handling

Do not fill all blanks globally. Handle them by semantic type:

| Column type | Recommended handling |
|---|---|
| Return reason | Create a display label such as `No return record` |
| Return date | Keep as null date |
| Rating | Keep as numeric null; create `No review` label only for display |
| Shipment dates | Keep as null dates |
| Fulfillment duration | Keep as numeric null and filter non-null for averages |
| `late_fulfillment_flag` | Create a display label such as `No shipment / not applicable` |

Suggested Power BI calculated columns:

```DAX
Return Reason Label =
COALESCE ( orders_enriched[top_return_reason], "No return record" )
```

```DAX
Review Status =
IF ( ISBLANK ( orders_enriched[order_avg_rating] ), "No review", "Reviewed" )
```

```DAX
Shipment Status Label =
IF ( ISBLANK ( orders_enriched[ship_date] ), "No shipment / not applicable", "Shipment recorded" )
```

Suggested measure:

```DAX
Avg Fulfillment Days - Shipped Only =
CALCULATE (
    AVERAGE ( orders_enriched[fulfillment_days] ),
    NOT ISBLANK ( orders_enriched[fulfillment_days] )
)
```

## Generated Profile

Column-level missingness is recorded here:

```text
docs/assets/exports/tableau/orders_enriched_missingness.csv
```

Use that file when explaining Power BI column-quality warnings.

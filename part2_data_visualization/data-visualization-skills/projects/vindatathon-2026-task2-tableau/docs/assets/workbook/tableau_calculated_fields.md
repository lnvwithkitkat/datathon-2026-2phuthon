# Tableau Calculated Fields

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

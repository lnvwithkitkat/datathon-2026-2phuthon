# Dashboard Story Notes

## Executive Thesis

The business has meaningful revenue scale, but the CEO story should focus on profitable growth leakage:

- Total historical revenue: 16.43B VND.
- Gross margin: 2.27B VND.
- Gross margin rate: 13.8%.
- Cancel rate: 9.2%.
- Return-record rate: 5.6%.
- Promo item margin is about 1.3%, while no-promo item margin is about 20.0%.
- COD cancel-plus-return risk is about 24.9%.
- Inventory has simultaneous stockout and overstock pressure.

## Predictive EDA Story

Use `growth_forecast_monthly.csv` and `seasonality_indices.csv` to show what is likely to happen if historical patterns continue:

- March to June are historically stronger revenue months, with April to June especially high.
- The six-month EDA forecast estimates continued monthly revenue from roughly 53M to 131M VND in early 2023.
- May is the strongest month-of-year signal in the prepared seasonality index.
- Stockout, overstock, wrong-size returns, and channel quality are modeled as forward-looking risk signals, not Kaggle forecasts.

## Prescriptive Story

Recommended CEO actions:

- Tighten Streetwear promotions where promo margins collapse versus no-promo margins.
- Treat COD as a high-risk payment workflow and test prepaid incentives or stricter COD controls.
- Reduce wrong-size refunds, especially in Streetwear size combinations.
- Prioritize replenishment for high-demand stockout-risk products.
- Markdown or reduce receipts for products with excessive days of supply.
- Reallocate marketing toward channels with stronger revenue quality, not only high sessions.

## Rubric Mapping

- Visualization quality: six focused Tableau dashboards, clear titles, labels, filters, and actions.
- Analysis depth: each page includes Descriptive, Diagnostic, Predictive, and/or Prescriptive components.
- Business insight: action tables include owner, tradeoff, risk score, and impact where quantifiable.
- Creativity/storytelling: connects promotions, payment, returns, reviews, logistics, web traffic, and inventory into one CEO decision flow.

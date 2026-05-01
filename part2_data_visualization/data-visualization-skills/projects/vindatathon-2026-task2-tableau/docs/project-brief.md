# Project Brief

## Context

VinDatathon 2026 Task 2 asks teams to build a Tableau dashboard and analysis story from a multi-table Vietnamese fashion e-commerce dataset. The goal is to persuade a CEO to act using high-quality visual storytelling, not just descriptive EDA.

## Confirmed Decisions

- Framework: CRISP-DM
- Goal tier: Advanced
- Visualization path: Tableau override
- Deployment target: File-out
- Active scope: Part 2 only

## Source Scope

Use the 13 business CSVs in `projects/data/`:

- `customers.csv`
- `geography.csv`
- `inventory.csv`
- `order_items.csv`
- `orders.csv`
- `payments.csv`
- `products.csv`
- `promotions.csv`
- `returns.csv`
- `reviews.csv`
- `sales.csv`
- `shipments.csv`
- `web_traffic.csv`

Excluded:

- `sample_submission.csv`
- `baseline.ipynb`
- `sales_test.csv` because it is not provided and belongs to Part 3 forecasting, not Part 2.

## Success Criteria

- Cover all four rubric levels: Descriptive, Diagnostic, Predictive, Prescriptive.
- Make the Predictive layer explicit through trend, seasonality, leading-indicator, stockout, return, promotion, and channel risk signals.
- Produce a CEO-facing Tableau dashboard with dashboard actions: filter, highlight, drill, return-reason focus, inventory quadrant focus, and reset behavior.
- Use quantified recommendations tied to business tradeoffs.

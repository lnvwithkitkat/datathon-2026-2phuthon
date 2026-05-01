# Project Plan

## Confirmed Planning Gate

- Framework: CRISP-DM
- Goal tier: Advanced
- Visualization tool: Tableau override
- Deploy target: File-out

## Goal

Build a Part 2-only Tableau dashboard package for the VinDatathon 2026 e-commerce fashion dataset, optimized for the 60-point visualization and analysis rubric.

## Dashboard Narrative

The dashboard answers one executive question:

> Where should a Vietnamese fashion e-commerce CEO act next to grow profitably while reducing operational and customer-experience leakage?

The story is split into six dashboards:

1. Executive Overview
2. Growth Forecast & Seasonality
3. Profit & Promotion Leakage
4. Customer, Channel & Payment Risk
5. Returns, Reviews & Fulfillment
6. Inventory Actions

## Analytical Approach

- Descriptive: establish revenue, margin, orders, customers, traffic, returns, and inventory baseline.
- Diagnostic: explain margin leakage, COD risk, wrong-size returns, fulfillment friction, and inventory imbalance by segment.
- Predictive: use historical trend, seasonality, leading indicators, and risk scoring to show what is likely to happen if patterns continue.
- Prescriptive: convert risk signals into action recommendations with owner, tradeoff, and impact notes.

## Implementation Outputs

- Prepared CSV extracts under `docs/assets/exports/tableau/`.
- Tableau file-out build package under `docs/assets/workbook/`.
- Data dictionary, ERD, validation report, calculated fields, and dashboard blueprint.

## Current Constraint

Tableau Desktop 2026.1 exists locally, but `tableau.com -h` reports that product activation is required. The data, blueprint, and package are ready; final rendered `.twbx` verification and screenshot/PDF export require Tableau activation.

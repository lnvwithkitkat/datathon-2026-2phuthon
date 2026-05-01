from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd


PROJECT_DIR = Path(__file__).resolve().parents[1]
REPO_ROOT = Path(__file__).resolve().parents[3]
SOURCE_DIR = REPO_ROOT / "projects" / "data"
DOCS_DIR = PROJECT_DIR / "docs"
EXPORT_DIR = DOCS_DIR / "assets" / "exports" / "tableau"

SOURCE_FILES = {
    "customers": "customers.csv",
    "geography": "geography.csv",
    "inventory": "inventory.csv",
    "order_items": "order_items.csv",
    "orders": "orders.csv",
    "payments": "payments.csv",
    "products": "products.csv",
    "promotions": "promotions.csv",
    "returns": "returns.csv",
    "reviews": "reviews.csv",
    "sales": "sales.csv",
    "shipments": "shipments.csv",
    "web_traffic": "web_traffic.csv",
}

EXCLUDED_FILES = ["sample_submission.csv", "baseline.ipynb", "sales_test.csv"]


def pct(numerator: pd.Series | np.ndarray, denominator: pd.Series | np.ndarray) -> np.ndarray:
    numerator = np.asarray(numerator, dtype="float64")
    denominator = np.asarray(denominator, dtype="float64")
    out = np.full_like(numerator, np.nan, dtype="float64")
    np.divide(numerator, denominator, out=out, where=denominator != 0)
    return out


def read_csv(name: str, **kwargs) -> pd.DataFrame:
    path = SOURCE_DIR / SOURCE_FILES[name]
    if not path.exists():
        raise FileNotFoundError(f"Required source file is missing: {path}")
    return pd.read_csv(path, low_memory=False, **kwargs)


def mode_or_blank(values: pd.Series) -> str:
    values = values.dropna()
    if values.empty:
        return ""
    modes = values.mode()
    return str(modes.iloc[0]) if not modes.empty else str(values.iloc[0])


def add_date_parts(df: pd.DataFrame, date_col: str, prefix: str = "") -> pd.DataFrame:
    out = df.copy()
    d = pd.to_datetime(out[date_col], errors="coerce")
    key = f"{prefix}_" if prefix else ""
    out[f"{key}year"] = d.dt.year
    out[f"{key}quarter"] = d.dt.quarter
    out[f"{key}month"] = d.dt.month
    out[f"{key}month_name"] = d.dt.month_name()
    out[f"{key}year_month"] = d.dt.to_period("M").astype(str)
    out[f"{key}weekday"] = d.dt.day_name()
    out[f"{key}day_of_week"] = d.dt.dayofweek + 1
    return out


def write_csv(df: pd.DataFrame, name: str) -> Path:
    EXPORT_DIR.mkdir(parents=True, exist_ok=True)
    path = EXPORT_DIR / name
    df.to_csv(path, index=False, encoding="utf-8-sig")
    return path


def safe_margin_pct(df: pd.DataFrame, margin_col: str, revenue_col: str) -> pd.Series:
    return pd.Series(pct(df[margin_col], df[revenue_col]), index=df.index).replace([np.inf, -np.inf], np.nan)


def build_outputs() -> dict[str, pd.DataFrame]:
    customers = read_csv("customers", parse_dates=["signup_date"])
    geography = read_csv("geography")
    inventory = read_csv("inventory", parse_dates=["snapshot_date"])
    order_items = read_csv("order_items", dtype={"promo_id": "string", "promo_id_2": "string"})
    orders = read_csv("orders", parse_dates=["order_date"])
    payments = read_csv("payments")
    products = read_csv("products")
    promotions = read_csv("promotions", parse_dates=["start_date", "end_date"])
    returns = read_csv("returns", parse_dates=["return_date"])
    reviews = read_csv("reviews", parse_dates=["review_date"])
    sales = read_csv("sales", parse_dates=["Date"])
    shipments = read_csv("shipments", parse_dates=["ship_date", "delivery_date"])
    web_traffic = read_csv("web_traffic", parse_dates=["date"])

    products_small = products[
        ["product_id", "product_name", "category", "segment", "size", "color", "price", "cogs"]
    ]
    items = order_items.merge(products_small, on="product_id", how="left")
    items["line_net_revenue"] = items["quantity"] * items["unit_price"]
    items["line_list_revenue"] = items["quantity"] * items["price"]
    items["line_cogs"] = items["quantity"] * items["cogs"]
    items["line_margin"] = items["line_net_revenue"] - items["line_cogs"]
    items["line_margin_pct"] = safe_margin_pct(items, "line_margin", "line_net_revenue")
    items["line_discount_rate"] = pct(items["discount_amount"], items["line_net_revenue"] + items["discount_amount"])
    items["has_promo"] = items["promo_id"].notna()
    items["has_second_promo"] = items["promo_id_2"].notna()

    promo_cols = [
        "promo_id",
        "promo_name",
        "promo_type",
        "discount_value",
        "start_date",
        "end_date",
        "applicable_category",
        "promo_channel",
        "stackable_flag",
        "min_order_value",
    ]
    items = items.merge(promotions[promo_cols], on="promo_id", how="left")

    return_item = (
        returns.groupby(["order_id", "product_id"], as_index=False)
        .agg(
            return_records=("return_id", "count"),
            returned_units=("return_quantity", "sum"),
            refund_amount=("refund_amount", "sum"),
            top_return_reason=("return_reason", mode_or_blank),
            first_return_date=("return_date", "min"),
        )
    )
    review_item = (
        reviews.groupby(["order_id", "product_id"], as_index=False)
        .agg(
            review_count=("review_id", "count"),
            avg_rating=("rating", "mean"),
            min_rating=("rating", "min"),
            top_review_title=("review_title", mode_or_blank),
            first_review_date=("review_date", "min"),
        )
    )

    items = items.merge(return_item, on=["order_id", "product_id"], how="left")
    items = items.merge(review_item, on=["order_id", "product_id"], how="left")
    for col in ["return_records", "returned_units", "refund_amount", "review_count"]:
        items[col] = items[col].fillna(0)
    items["returned_flag"] = items["return_records"] > 0
    items["reviewed_flag"] = items["review_count"] > 0
    items["return_rate_units"] = pct(items["returned_units"], items["quantity"])

    order_item_rollup = (
        items.groupby("order_id", as_index=False)
        .agg(
            order_lines=("product_id", "count"),
            unique_products=("product_id", "nunique"),
            units=("quantity", "sum"),
            item_net_revenue=("line_net_revenue", "sum"),
            item_list_revenue=("line_list_revenue", "sum"),
            item_cogs=("line_cogs", "sum"),
            item_margin=("line_margin", "sum"),
            total_discount=("discount_amount", "sum"),
            promo_line_count=("has_promo", "sum"),
            returned_units=("returned_units", "sum"),
            refund_amount=("refund_amount", "sum"),
            return_records=("return_records", "sum"),
            avg_rating=("avg_rating", "mean"),
            review_count=("review_count", "sum"),
        )
    )
    order_item_rollup["has_promo"] = order_item_rollup["promo_line_count"] > 0
    order_item_rollup["order_margin_pct"] = safe_margin_pct(order_item_rollup, "item_margin", "item_net_revenue")
    order_item_rollup["order_discount_rate"] = pct(
        order_item_rollup["total_discount"], order_item_rollup["item_net_revenue"] + order_item_rollup["total_discount"]
    )

    dominant_category = (
        items.groupby(["order_id", "category"], as_index=False)["line_net_revenue"]
        .sum()
        .sort_values(["order_id", "line_net_revenue"], ascending=[True, False])
        .drop_duplicates("order_id")
        .rename(columns={"category": "dominant_category"})
        [["order_id", "dominant_category"]]
    )
    dominant_segment = (
        items.groupby(["order_id", "segment"], as_index=False)["line_net_revenue"]
        .sum()
        .sort_values(["order_id", "line_net_revenue"], ascending=[True, False])
        .drop_duplicates("order_id")
        .rename(columns={"segment": "dominant_segment"})
        [["order_id", "dominant_segment"]]
    )
    return_order = (
        returns.groupby("order_id", as_index=False)
        .agg(top_return_reason=("return_reason", mode_or_blank), first_return_date=("return_date", "min"))
    )
    review_order = reviews.groupby("order_id", as_index=False).agg(order_avg_rating=("rating", "mean"))

    shipments = shipments.merge(orders[["order_id", "order_date"]], on="order_id", how="left")
    shipments["ship_delay_days"] = (shipments["ship_date"] - shipments["order_date"]).dt.days
    shipments["delivery_days"] = (shipments["delivery_date"] - shipments["ship_date"]).dt.days
    shipments["fulfillment_days"] = (shipments["delivery_date"] - shipments["order_date"]).dt.days
    fulfillment_p90 = shipments["fulfillment_days"].quantile(0.90)
    shipments["late_fulfillment_flag"] = shipments["fulfillment_days"] > fulfillment_p90

    customer_cols = [
        "customer_id",
        "zip",
        "city",
        "signup_date",
        "gender",
        "age_group",
        "acquisition_channel",
    ]
    customers_renamed = customers[customer_cols].rename(
        columns={"zip": "customer_zip", "city": "customer_city", "signup_date": "customer_signup_date"}
    )
    geography_ship = geography.rename(columns={"city": "ship_city", "region": "ship_region", "district": "ship_district"})

    orders_enriched = (
        orders.merge(order_item_rollup, on="order_id", how="left")
        .merge(dominant_category, on="order_id", how="left")
        .merge(dominant_segment, on="order_id", how="left")
        .merge(customers_renamed, on="customer_id", how="left")
        .merge(geography_ship, on="zip", how="left")
        .merge(payments[["order_id", "payment_value", "installments"]], on="order_id", how="left")
        .merge(
            shipments[
                [
                    "order_id",
                    "ship_date",
                    "delivery_date",
                    "shipping_fee",
                    "ship_delay_days",
                    "delivery_days",
                    "fulfillment_days",
                    "late_fulfillment_flag",
                ]
            ],
            on="order_id",
            how="left",
        )
        .merge(return_order, on="order_id", how="left")
        .merge(review_order, on="order_id", how="left")
    )
    orders_enriched = add_date_parts(orders_enriched, "order_date", "order")
    orders_enriched["customer_tenure_days"] = (
        orders_enriched["order_date"] - orders_enriched["customer_signup_date"]
    ).dt.days
    orders_enriched["is_cancelled"] = orders_enriched["order_status"].eq("cancelled")
    orders_enriched["is_returned_status"] = orders_enriched["order_status"].eq("returned")
    orders_enriched["has_return_record"] = orders_enriched["return_records"].fillna(0) > 0
    orders_enriched["is_cod"] = orders_enriched["payment_method"].eq("cod")
    late_fulfillment = orders_enriched["late_fulfillment_flag"].fillna(False).astype(bool)
    orders_enriched["risk_status"] = np.select(
        [
            orders_enriched["is_cancelled"],
            orders_enriched["has_return_record"] | orders_enriched["is_returned_status"],
            late_fulfillment,
        ],
        ["Cancelled", "Returned/refunded", "Late fulfillment"],
        default="Completed/open",
    )

    order_context = orders_enriched[
        [
            "order_id",
            "order_date",
            "order_year",
            "order_quarter",
            "order_month",
            "order_year_month",
            "order_weekday",
            "customer_id",
            "ship_region",
            "ship_city",
            "ship_district",
            "order_status",
            "payment_method",
            "device_type",
            "order_source",
            "gender",
            "age_group",
            "acquisition_channel",
            "fulfillment_days",
            "delivery_days",
            "shipping_fee",
            "late_fulfillment_flag",
        ]
    ]
    order_items_enriched = items.merge(order_context, on="order_id", how="left")

    sales = add_date_parts(sales.rename(columns={"Date": "date", "Revenue": "sales_revenue", "COGS": "sales_cogs"}), "date")
    sales["sales_margin"] = sales["sales_revenue"] - sales["sales_cogs"]
    sales["sales_margin_pct"] = safe_margin_pct(sales, "sales_margin", "sales_revenue")

    daily_orders = (
        orders_enriched.groupby("order_date", as_index=False)
        .agg(
            order_count=("order_id", "count"),
            cancelled_orders=("is_cancelled", "sum"),
            returned_orders=("has_return_record", "sum"),
            item_net_revenue=("item_net_revenue", "sum"),
            item_margin=("item_margin", "sum"),
            avg_order_value=("item_net_revenue", "mean"),
            promo_order_share=("has_promo", "mean"),
            cod_order_share=("is_cod", "mean"),
            avg_fulfillment_days=("fulfillment_days", "mean"),
        )
        .rename(columns={"order_date": "date"})
    )
    daily_orders["cancel_rate"] = pct(daily_orders["cancelled_orders"], daily_orders["order_count"])
    daily_orders["return_order_rate"] = pct(daily_orders["returned_orders"], daily_orders["order_count"])

    web = web_traffic.copy()
    web["bounce_x_sessions"] = web["bounce_rate"] * web["sessions"]
    web["duration_x_sessions"] = web["avg_session_duration_sec"] * web["sessions"]
    web_daily = (
        web.groupby("date", as_index=False)
        .agg(
            sessions=("sessions", "sum"),
            unique_visitors=("unique_visitors", "sum"),
            page_views=("page_views", "sum"),
            bounce_x_sessions=("bounce_x_sessions", "sum"),
            duration_x_sessions=("duration_x_sessions", "sum"),
        )
    )
    web_daily["weighted_bounce_rate"] = pct(web_daily["bounce_x_sessions"], web_daily["sessions"])
    web_daily["weighted_avg_session_duration_sec"] = pct(web_daily["duration_x_sessions"], web_daily["sessions"])
    web_daily = web_daily.drop(columns=["bounce_x_sessions", "duration_x_sessions"])

    daily_kpi = sales.merge(daily_orders, on="date", how="left").merge(web_daily, on="date", how="left")
    for col in ["order_count", "cancelled_orders", "returned_orders", "sessions", "unique_visitors", "page_views"]:
        daily_kpi[col] = daily_kpi[col].fillna(0)
    daily_kpi = daily_kpi.sort_values("date")
    for window in [7, 30, 90]:
        daily_kpi[f"sales_revenue_rolling_{window}d"] = daily_kpi["sales_revenue"].rolling(window, min_periods=1).mean()
        daily_kpi[f"sales_margin_rolling_{window}d"] = daily_kpi["sales_margin"].rolling(window, min_periods=1).mean()
    daily_kpi["orders_per_session"] = pct(daily_kpi["order_count"], daily_kpi["sessions"])
    daily_kpi["revenue_per_session"] = pct(daily_kpi["sales_revenue"], daily_kpi["sessions"])
    daily_kpi["page_views_per_session"] = pct(daily_kpi["page_views"], daily_kpi["sessions"])

    inventory_monthly = inventory.sort_values(["product_id", "snapshot_date"]).copy()
    inventory_monthly = add_date_parts(inventory_monthly, "snapshot_date", "snapshot")
    inventory_monthly["units_sold_3m_avg"] = (
        inventory_monthly.groupby("product_id")["units_sold"]
        .transform(lambda s: s.rolling(3, min_periods=1).mean())
        .astype(float)
    )
    inventory_monthly["stockout_days_3m_avg"] = (
        inventory_monthly.groupby("product_id")["stockout_days"]
        .transform(lambda s: s.rolling(3, min_periods=1).mean())
        .astype(float)
    )
    category_medians = inventory_monthly.groupby("category").agg(
        median_days_supply=("days_of_supply", "median"),
        median_sell_through=("sell_through_rate", "median"),
        median_units_3m=("units_sold_3m_avg", "median"),
    )
    inventory_monthly = inventory_monthly.merge(category_medians, on="category", how="left")
    inventory_monthly["stockout_pressure_score"] = (
        inventory_monthly["stockout_days"].clip(0, 30) / 30 * 40
        + (1 - inventory_monthly["fill_rate"]).clip(0, 1) * 35
        + inventory_monthly["sell_through_rate"].clip(0, 1) * 25
    )
    inventory_monthly["overstock_pressure_score"] = (
        pct(inventory_monthly["days_of_supply"], inventory_monthly["median_days_supply"]).clip(0, 3) / 3 * 45
        + (1 - pct(inventory_monthly["sell_through_rate"], inventory_monthly["median_sell_through"]).clip(0, 1)) * 35
        + inventory_monthly["overstock_flag"].clip(0, 1) * 20
    )
    stockout_risk = (
        (inventory_monthly["stockout_days_3m_avg"] >= 5)
        & (inventory_monthly["units_sold_3m_avg"] >= inventory_monthly["median_units_3m"])
    )
    overstock_risk = (
        (inventory_monthly["days_of_supply"] > inventory_monthly["median_days_supply"])
        & (inventory_monthly["sell_through_rate"] < inventory_monthly["median_sell_through"])
        & inventory_monthly["overstock_flag"].eq(1)
    )
    inventory_monthly["inventory_quadrant"] = np.select(
        [stockout_risk & overstock_risk, stockout_risk, overstock_risk],
        ["Mixed risk", "Stockout risk", "Overstock risk"],
        default="Balanced/watch",
    )
    inventory_monthly["replenishment_priority"] = np.select(
        [
            inventory_monthly["inventory_quadrant"].eq("Stockout risk")
            & (inventory_monthly["stockout_pressure_score"] >= inventory_monthly["stockout_pressure_score"].quantile(0.80)),
            inventory_monthly["inventory_quadrant"].eq("Mixed risk"),
            inventory_monthly["inventory_quadrant"].eq("Overstock risk"),
        ],
        ["High replenishment priority", "Investigate allocation", "Markdown / reduce receipts"],
        default="Monitor",
    )

    monthly_forecast = build_monthly_forecast(sales)
    seasonality_indices = build_seasonality_indices(sales, daily_kpi)
    risk_signals = build_risk_signals(
        orders_enriched=orders_enriched,
        order_items_enriched=order_items_enriched,
        inventory_monthly=inventory_monthly,
        web_traffic=web_traffic,
    )
    recommendations = build_recommendations(risk_signals)
    dashboard_kpis = build_dashboard_kpis(sales, orders_enriched, order_items_enriched, inventory_monthly, web_traffic)

    return {
        "orders_enriched": orders_enriched,
        "order_items_enriched": order_items_enriched,
        "daily_kpi": daily_kpi,
        "inventory_monthly": inventory_monthly,
        "growth_forecast_monthly": monthly_forecast,
        "seasonality_indices": seasonality_indices,
        "predictive_signals": risk_signals,
        "recommendations": recommendations,
        "dashboard_kpis": dashboard_kpis,
    }


def build_monthly_forecast(sales: pd.DataFrame) -> pd.DataFrame:
    monthly = (
        sales.set_index("date")[["sales_revenue", "sales_cogs"]]
        .resample("MS")
        .sum()
        .reset_index()
        .sort_values("date")
    )
    monthly["sales_margin"] = monthly["sales_revenue"] - monthly["sales_cogs"]
    monthly["sales_margin_pct"] = safe_margin_pct(monthly, "sales_margin", "sales_revenue")
    monthly["month"] = monthly["date"].dt.month
    monthly["month_name"] = monthly["date"].dt.month_name()
    monthly["period_index"] = np.arange(len(monthly))

    seasonal_revenue = monthly.groupby("month")["sales_revenue"].mean() / monthly["sales_revenue"].mean()
    seasonal_cogs = monthly.groupby("month")["sales_cogs"].mean() / monthly["sales_cogs"].mean()
    deseasonal_revenue = monthly["sales_revenue"] / monthly["month"].map(seasonal_revenue)
    deseasonal_cogs = monthly["sales_cogs"] / monthly["month"].map(seasonal_cogs)
    revenue_coef = np.polyfit(monthly["period_index"], deseasonal_revenue, deg=1)
    cogs_coef = np.polyfit(monthly["period_index"], deseasonal_cogs, deg=1)

    monthly["forecast_revenue"] = np.polyval(revenue_coef, monthly["period_index"]) * monthly["month"].map(seasonal_revenue)
    monthly["forecast_cogs"] = np.polyval(cogs_coef, monthly["period_index"]) * monthly["month"].map(seasonal_cogs)
    residual = monthly["sales_revenue"] - monthly["forecast_revenue"]
    residual_std = residual.std()

    future_dates = pd.date_range(monthly["date"].max() + pd.offsets.MonthBegin(1), periods=6, freq="MS")
    future = pd.DataFrame({"date": future_dates})
    future["month"] = future["date"].dt.month
    future["month_name"] = future["date"].dt.month_name()
    future["period_index"] = np.arange(len(monthly), len(monthly) + len(future))
    future["forecast_revenue"] = np.polyval(revenue_coef, future["period_index"]) * future["month"].map(seasonal_revenue)
    future["forecast_cogs"] = np.polyval(cogs_coef, future["period_index"]) * future["month"].map(seasonal_cogs)
    future["forecast_revenue"] = future["forecast_revenue"].clip(lower=0)
    future["forecast_cogs"] = future["forecast_cogs"].clip(lower=0)
    future["sales_revenue"] = np.nan
    future["sales_cogs"] = np.nan
    future["sales_margin"] = np.nan
    future["sales_margin_pct"] = np.nan

    combined = pd.concat([monthly, future], ignore_index=True)
    combined["forecast_margin"] = combined["forecast_revenue"] - combined["forecast_cogs"]
    combined["forecast_margin_pct"] = pct(combined["forecast_margin"], combined["forecast_revenue"])
    combined["forecast_lower_revenue"] = (combined["forecast_revenue"] - 1.28 * residual_std).clip(lower=0)
    combined["forecast_upper_revenue"] = (combined["forecast_revenue"] + 1.28 * residual_std).clip(lower=0)
    combined["is_forecast"] = combined["sales_revenue"].isna()
    combined["signal_type"] = np.where(combined["is_forecast"], "Predictive EDA forecast", "Historical actual")
    combined["forecast_method"] = "Linear trend on deseasonalized monthly revenue/COGS plus month-of-year index"
    return combined


def build_seasonality_indices(sales: pd.DataFrame, daily_kpi: pd.DataFrame) -> pd.DataFrame:
    month = (
        sales.groupby(["month", "month_name"], as_index=False)
        .agg(avg_daily_revenue=("sales_revenue", "mean"), avg_daily_margin_pct=("sales_margin_pct", "mean"))
    )
    month["seasonality_index"] = month["avg_daily_revenue"] / sales["sales_revenue"].mean()
    month["season_type"] = np.select(
        [month["seasonality_index"] >= 1.10, month["seasonality_index"] <= 0.90],
        ["Likely peak month", "Likely soft month"],
        default="Normal month",
    )
    month["grain"] = "month_of_year"
    month = month.rename(columns={"month": "period_number", "month_name": "period_name"})

    weekday = (
        daily_kpi.groupby(["day_of_week", "weekday"], as_index=False)
        .agg(avg_daily_revenue=("sales_revenue", "mean"), avg_order_count=("order_count", "mean"))
    )
    weekday["seasonality_index"] = weekday["avg_daily_revenue"] / daily_kpi["sales_revenue"].mean()
    weekday["avg_daily_margin_pct"] = np.nan
    weekday["season_type"] = np.select(
        [weekday["seasonality_index"] >= 1.05, weekday["seasonality_index"] <= 0.95],
        ["Likely high weekday", "Likely low weekday"],
        default="Normal weekday",
    )
    weekday["grain"] = "weekday"
    weekday = weekday.rename(columns={"day_of_week": "period_number", "weekday": "period_name"})

    cols = [
        "grain",
        "period_number",
        "period_name",
        "seasonality_index",
        "season_type",
        "avg_daily_revenue",
        "avg_daily_margin_pct",
    ]
    return pd.concat([month[cols], weekday[cols]], ignore_index=True)


def build_risk_signals(
    orders_enriched: pd.DataFrame,
    order_items_enriched: pd.DataFrame,
    inventory_monthly: pd.DataFrame,
    web_traffic: pd.DataFrame,
) -> pd.DataFrame:
    signals: list[dict[str, object]] = []

    promo = (
        order_items_enriched.groupby(["category", "segment", "has_promo"], as_index=False)
        .agg(revenue=("line_net_revenue", "sum"), margin=("line_margin", "sum"), lines=("order_id", "count"))
    )
    promo["margin_pct"] = pct(promo["margin"], promo["revenue"])
    pivot = promo.pivot_table(index=["category", "segment"], columns="has_promo", values=["revenue", "margin_pct"], fill_value=0)
    pivot.columns = [f"{metric}_{'promo' if flag else 'no_promo'}" for metric, flag in pivot.columns]
    pivot = pivot.reset_index()
    for _, row in pivot.sort_values("revenue_promo", ascending=False).head(12).iterrows():
        gap = float(row.get("margin_pct_no_promo", 0) - row.get("margin_pct_promo", 0))
        leakage = max(gap, 0) * float(row.get("revenue_promo", 0))
        signals.append(
            {
                "signal_type": "Promotion margin risk",
                "entity_grain": "category_segment",
                "entity": f"{row['category']} / {row['segment']}",
                "current_value": row.get("margin_pct_promo", np.nan),
                "baseline_value": row.get("margin_pct_no_promo", np.nan),
                "expected_direction": "Margin pressure if current promo mix continues",
                "risk_score": min(100, leakage / 10_000_000),
                "estimated_impact_vnd": leakage,
                "recommended_action": "Tighten discount depth, exclude low-margin SKUs, or require higher minimum order value.",
                "evidence": "Promo margin compared with no-promo margin at category/segment grain.",
            }
        )

    payment = (
        orders_enriched.groupby("payment_method", as_index=False)
        .agg(
            orders=("order_id", "count"),
            revenue=("item_net_revenue", "sum"),
            cancel_rate=("is_cancelled", "mean"),
            return_rate=("has_return_record", "mean"),
        )
    )
    payment["risk_rate"] = payment["cancel_rate"] + payment["return_rate"]
    baseline = (orders_enriched["is_cancelled"].mean() + orders_enriched["has_return_record"].mean())
    for _, row in payment.iterrows():
        excess = max(float(row["risk_rate"] - baseline), 0)
        signals.append(
            {
                "signal_type": "Payment risk",
                "entity_grain": "payment_method",
                "entity": row["payment_method"],
                "current_value": row["risk_rate"],
                "baseline_value": baseline,
                "expected_direction": "Higher cancellation/return pressure when risk rate is above baseline",
                "risk_score": min(100, excess * 500),
                "estimated_impact_vnd": excess * float(row["revenue"]),
                "recommended_action": "Use payment-specific incentives and controls; prioritize prepaid methods where risk is lower.",
                "evidence": "Cancellation plus return-record rate by payment method.",
            }
        )

    size_base = (
        order_items_enriched.groupby(["category", "size"], as_index=False)
        .agg(lines=("order_id", "count"), revenue=("line_net_revenue", "sum"), refunds=("refund_amount", "sum"))
    )
    wrong_size = (
        order_items_enriched[order_items_enriched["top_return_reason"].eq("wrong_size")]
        .groupby(["category", "size"], as_index=False)
        .agg(wrong_size_returns=("return_records", "sum"), wrong_size_refunds=("refund_amount", "sum"))
    )
    size_risk = size_base.merge(wrong_size, on=["category", "size"], how="left").fillna(0)
    size_risk["wrong_size_rate"] = pct(size_risk["wrong_size_returns"], size_risk["lines"])
    for _, row in size_risk.sort_values("wrong_size_refunds", ascending=False).head(12).iterrows():
        signals.append(
            {
                "signal_type": "Wrong-size return risk",
                "entity_grain": "category_size",
                "entity": f"{row['category']} / {row['size']}",
                "current_value": row["wrong_size_rate"],
                "baseline_value": size_risk["wrong_size_rate"].mean(),
                "expected_direction": "Refund pressure likely remains high without size guidance or SKU changes",
                "risk_score": min(100, row["wrong_size_refunds"] / 1_000_000),
                "estimated_impact_vnd": row["wrong_size_refunds"],
                "recommended_action": "Improve size guidance and target the worst category-size combinations first.",
                "evidence": "Wrong-size return records and refunds by category/size.",
            }
        )

    recent_cutoff = inventory_monthly["snapshot_date"].max() - pd.DateOffset(months=6)
    inv_recent = inventory_monthly[inventory_monthly["snapshot_date"] >= recent_cutoff]
    inv_product = (
        inv_recent.groupby(["product_id", "product_name", "category", "segment"], as_index=False)
        .agg(
            units_sold=("units_sold", "sum"),
            stockout_days=("stockout_days", "sum"),
            avg_fill_rate=("fill_rate", "mean"),
            avg_days_supply=("days_of_supply", "mean"),
            max_stockout_score=("stockout_pressure_score", "max"),
            max_overstock_score=("overstock_pressure_score", "max"),
        )
    )
    inv_product["stockout_risk_score"] = inv_product["max_stockout_score"] * (1 - inv_product["avg_fill_rate"]).clip(0, 1)
    inv_product["overstock_risk_score"] = inv_product["max_overstock_score"]
    for _, row in inv_product.sort_values("stockout_risk_score", ascending=False).head(15).iterrows():
        signals.append(
            {
                "signal_type": "Stockout risk",
                "entity_grain": "product",
                "entity": f"{row['product_name']} ({int(row['product_id'])})",
                "current_value": row["stockout_days"],
                "baseline_value": inv_product["stockout_days"].median(),
                "expected_direction": "Likely lost demand if recent stockout pattern continues",
                "risk_score": row["stockout_risk_score"],
                "estimated_impact_vnd": np.nan,
                "recommended_action": "Prioritize replenishment and allocation review for high-demand products with low fill rate.",
                "evidence": "Recent six-month stockout days, fill rate, and units sold.",
            }
        )
    for _, row in inv_product.sort_values("overstock_risk_score", ascending=False).head(15).iterrows():
        signals.append(
            {
                "signal_type": "Overstock risk",
                "entity_grain": "product",
                "entity": f"{row['product_name']} ({int(row['product_id'])})",
                "current_value": row["avg_days_supply"],
                "baseline_value": inv_product["avg_days_supply"].median(),
                "expected_direction": "Working capital remains tied up if sell-through does not improve",
                "risk_score": row["overstock_risk_score"],
                "estimated_impact_vnd": np.nan,
                "recommended_action": "Reduce receipts, bundle, or markdown products with excessive days of supply.",
                "evidence": "Recent six-month days of supply and overstock score.",
            }
        )

    source_orders = (
        orders_enriched.groupby("order_source", as_index=False)
        .agg(
            revenue=("item_net_revenue", "sum"),
            orders=("order_id", "count"),
            cancel_rate=("is_cancelled", "mean"),
            return_rate=("has_return_record", "mean"),
        )
        .rename(columns={"order_source": "traffic_source"})
    )
    source_traffic = web_traffic.groupby("traffic_source", as_index=False).agg(sessions=("sessions", "sum"))
    channel = source_orders.merge(source_traffic, on="traffic_source", how="left")
    channel["revenue_per_session"] = pct(channel["revenue"], channel["sessions"])
    channel_baseline = np.nanmedian(channel["revenue_per_session"])
    for _, row in channel.iterrows():
        quality_gap = max(channel_baseline - float(row["revenue_per_session"]), 0)
        signals.append(
            {
                "signal_type": "Channel quality risk",
                "entity_grain": "traffic_source",
                "entity": row["traffic_source"],
                "current_value": row["revenue_per_session"],
                "baseline_value": channel_baseline,
                "expected_direction": "Budget efficiency risk when revenue per session trails channel baseline",
                "risk_score": min(100, quality_gap / max(channel_baseline, 1) * 100),
                "estimated_impact_vnd": quality_gap * float(row.get("sessions", 0)),
                "recommended_action": "Shift spend toward channels with stronger revenue quality and lower order risk.",
                "evidence": "Order revenue by source divided by traffic sessions from the matching source.",
            }
        )

    out = pd.DataFrame(signals)
    out["priority"] = pd.qcut(out["risk_score"].rank(method="first"), 4, labels=["Low", "Medium", "High", "Critical"])
    return out.sort_values(["priority", "risk_score"], ascending=[False, False])


def build_recommendations(risk_signals: pd.DataFrame) -> pd.DataFrame:
    signal_order = [
        "Promotion margin risk",
        "Payment risk",
        "Wrong-size return risk",
        "Stockout risk",
        "Overstock risk",
        "Channel quality risk",
    ]
    candidate_signals = risk_signals[risk_signals["risk_score"].fillna(0) > 0].copy()
    top = (
        candidate_signals.assign(signal_rank=lambda d: d["signal_type"].map({v: i for i, v in enumerate(signal_order)}))
        .sort_values(["signal_rank", "risk_score", "estimated_impact_vnd"], ascending=[True, False, False])
        .groupby("signal_type", as_index=False)
        .head(3)
        .sort_values(["signal_rank", "risk_score"], ascending=[True, False])
        .head(20)
        .copy()
    )
    top.insert(0, "action_id", [f"A{i:02d}" for i in range(1, len(top) + 1)])
    top["dashboard_page"] = top["signal_type"].map(
        {
            "Promotion margin risk": "Profit & Promotion Leakage",
            "Payment risk": "Customer, Channel & Payment Risk",
            "Wrong-size return risk": "Returns, Reviews & Fulfillment",
            "Stockout risk": "Inventory Actions",
            "Overstock risk": "Inventory Actions",
            "Channel quality risk": "Customer, Channel & Payment Risk",
        }
    )
    top["decision_owner"] = top["signal_type"].map(
        {
            "Promotion margin risk": "Commercial / Pricing",
            "Payment risk": "Finance / Operations",
            "Wrong-size return risk": "Merchandising / CX",
            "Stockout risk": "Supply Chain",
            "Overstock risk": "Supply Chain / Merchandising",
            "Channel quality risk": "Marketing",
        }
    )
    top["tradeoff"] = top["signal_type"].map(
        {
            "Promotion margin risk": "May reduce order volume but protects gross margin.",
            "Payment risk": "May lower COD convenience but reduces failed or refunded demand.",
            "Wrong-size return risk": "Requires UX/content work but reduces refund leakage.",
            "Stockout risk": "Higher inventory commitment but reduces lost sales risk.",
            "Overstock risk": "Markdowns reduce unit margin but free working capital.",
            "Channel quality risk": "Lower traffic volume is acceptable if revenue quality improves.",
        }
    )
    return top[
        [
            "action_id",
            "dashboard_page",
            "decision_owner",
            "signal_type",
            "entity_grain",
            "entity",
            "priority",
            "risk_score",
            "estimated_impact_vnd",
            "recommended_action",
            "tradeoff",
            "evidence",
        ]
    ]


def build_dashboard_kpis(
    sales: pd.DataFrame,
    orders_enriched: pd.DataFrame,
    order_items_enriched: pd.DataFrame,
    inventory_monthly: pd.DataFrame,
    web_traffic: pd.DataFrame,
) -> pd.DataFrame:
    total_revenue = sales["sales_revenue"].sum()
    total_cogs = sales["sales_cogs"].sum()
    total_margin = total_revenue - total_cogs
    promo_items = order_items_enriched[order_items_enriched["has_promo"]]
    no_promo_items = order_items_enriched[~order_items_enriched["has_promo"]]
    rows = [
        ("Revenue", total_revenue, "Historical sales.csv revenue"),
        ("Gross margin", total_margin, "Revenue minus COGS from sales.csv"),
        ("Gross margin %", total_margin / total_revenue, "Gross margin divided by revenue"),
        ("Orders", orders_enriched["order_id"].nunique(), "Total orders"),
        ("Customers", orders_enriched["customer_id"].nunique(), "Customers with at least one order"),
        ("Cancel rate", orders_enriched["is_cancelled"].mean(), "Cancelled orders divided by all orders"),
        ("Return-record rate", orders_enriched["has_return_record"].mean(), "Orders with at least one return record"),
        ("COD risk rate", orders_enriched.loc[orders_enriched["payment_method"].eq("cod"), "is_cancelled"].mean()
         + orders_enriched.loc[orders_enriched["payment_method"].eq("cod"), "has_return_record"].mean(), "COD cancel plus return rate"),
        ("Promo margin %", promo_items["line_margin"].sum() / promo_items["line_net_revenue"].sum(), "Line margin percent for promoted items"),
        ("No-promo margin %", no_promo_items["line_margin"].sum() / no_promo_items["line_net_revenue"].sum(), "Line margin percent for non-promoted items"),
        ("Inventory stockout share", inventory_monthly["stockout_flag"].mean(), "Share of product-month rows with stockout flag"),
        ("Inventory overstock share", inventory_monthly["overstock_flag"].mean(), "Share of product-month rows with overstock flag"),
        ("Web sessions", web_traffic["sessions"].sum(), "Total web sessions"),
    ]
    return pd.DataFrame(rows, columns=["kpi_name", "kpi_value", "metric_definition"])


def write_data_dictionary(outputs: dict[str, pd.DataFrame]) -> pd.DataFrame:
    descriptions = {
        "orders_enriched": "Order-grain table with customer, geography, payment, fulfillment, revenue, margin, promotion, return, and review context.",
        "order_items_enriched": "Line-item grain table with product, promotion, margin, return, review, and order context.",
        "daily_kpi": "Daily official sales, order, web traffic, rolling trend, and conversion-proxy metrics.",
        "inventory_monthly": "Product-month inventory table with risk quadrants and replenishment/markdown signals.",
        "growth_forecast_monthly": "Historical and six-month predictive EDA forecast using trend plus seasonality from sales.csv only.",
        "seasonality_indices": "Month-of-year and weekday indices for likely peak/soft periods.",
        "predictive_signals": "Risk and opportunity signals for promotion, payment, returns, inventory, and channels.",
        "recommendations": "CEO-facing action table linking risk signals to owners, tradeoffs, and recommended actions.",
        "dashboard_kpis": "Small metric-definition table for dashboard KPI strips.",
    }
    records = []
    for table, df in outputs.items():
        for col in df.columns:
            records.append(
                {
                    "table_name": table,
                    "table_description": descriptions.get(table, ""),
                    "column_name": col,
                    "dtype": str(df[col].dtype),
                    "null_count": int(df[col].isna().sum()),
                    "row_count": int(len(df)),
                }
            )
    dictionary = pd.DataFrame(records)
    write_csv(dictionary, "data_dictionary.csv")
    return dictionary


def write_source_manifest() -> pd.DataFrame:
    rows = []
    for name, filename in SOURCE_FILES.items():
        path = SOURCE_DIR / filename
        rows.append(
            {
                "source_name": name,
                "filename": filename,
                "status": "used",
                "bytes": path.stat().st_size if path.exists() else None,
            }
        )
    for filename in EXCLUDED_FILES:
        path = SOURCE_DIR / filename
        if not path.exists() and filename == "baseline.ipynb":
            path = REPO_ROOT / "projects" / "notebook" / filename
        rows.append(
            {
                "source_name": Path(filename).stem,
                "filename": filename,
                "status": "excluded_by_scope",
                "bytes": path.stat().st_size if path.exists() else None,
            }
        )
    manifest = pd.DataFrame(rows)
    write_csv(manifest, "source_manifest.csv")
    return manifest


def write_validation_report(outputs: dict[str, pd.DataFrame]) -> Path:
    orders = read_csv("orders")
    order_items = read_csv("order_items")
    payments = read_csv("payments")
    products = read_csv("products")
    customers = read_csv("customers")
    geography = read_csv("geography")
    shipments = read_csv("shipments")
    returns = read_csv("returns")
    reviews = read_csv("reviews")
    inventory = read_csv("inventory")
    sales = read_csv("sales")

    checks = [
        ("orders.order_id unique", orders["order_id"].is_unique),
        ("payments.order_id unique", payments["order_id"].is_unique),
        ("products.product_id unique", products["product_id"].is_unique),
        ("customers.customer_id unique", customers["customer_id"].is_unique),
        ("geography.zip unique", geography["zip"].is_unique),
        ("order_items order_id coverage", order_items["order_id"].isin(orders["order_id"]).mean()),
        ("payments order_id coverage", payments["order_id"].isin(orders["order_id"]).mean()),
        ("shipments order_id coverage", shipments["order_id"].isin(orders["order_id"]).mean()),
        ("returns order_id coverage", returns["order_id"].isin(orders["order_id"]).mean()),
        ("reviews order_id coverage", reviews["order_id"].isin(orders["order_id"]).mean()),
        ("orders customer coverage", orders["customer_id"].isin(customers["customer_id"]).mean()),
        ("orders shipping zip coverage", orders["zip"].isin(geography["zip"]).mean()),
        ("inventory product coverage", inventory["product_id"].isin(products["product_id"]).mean()),
    ]
    row_counts = {name: len(df) for name, df in outputs.items()}
    sales_revenue = sales["Revenue"].sum()
    item_revenue = outputs["order_items_enriched"]["line_net_revenue"].sum()
    reconciliation_gap = item_revenue - sales_revenue

    lines = [
        "# Tableau Data Preparation Validation",
        "",
        "## Scope",
        "",
        "- Part 2 only.",
        "- Used the 13 approved business CSVs from `projects/data/`.",
        "- Excluded `sample_submission.csv`, `baseline.ipynb`, and unavailable `sales_test.csv`.",
        "",
        "## Output Row Counts",
        "",
    ]
    for table, count in row_counts.items():
        lines.append(f"- `{table}`: {count:,} rows")

    lines += ["", "## Key Integrity Checks", ""]
    for name, value in checks:
        if isinstance(value, (bool, np.bool_)):
            display = "PASS" if value else "FAIL"
        else:
            display = f"{value:.2%}"
        lines.append(f"- {name}: {display}")

    lines += [
        "",
        "## Revenue Reconciliation Note",
        "",
        f"- `sales.csv` total revenue: {sales_revenue:,.2f}",
        f"- item-level estimated revenue: {item_revenue:,.2f}",
        f"- item minus sales gap: {reconciliation_gap:,.2f}",
        "",
        "`sales.csv` remains the official daily revenue/COGS source for executive totals and forecasting signals. "
        "Item-level revenue is used for diagnostic slicing where product, promotion, customer, and fulfillment fields are required.",
        "",
        "## Predictive EDA Guardrail",
        "",
        "Forecast, seasonality, stockout, return, promotion, and channel signals are historical EDA indicators only. "
        "They do not use `sales_test.csv`, `sample_submission.csv`, or external data.",
        "",
    ]
    path = DOCS_DIR / "data-preparation-validation.md"
    path.write_text("\n".join(lines), encoding="utf-8")
    return path


def main() -> None:
    outputs = build_outputs()
    written = {}
    for name, df in outputs.items():
        written[name] = str(write_csv(df, f"{name}.csv").relative_to(PROJECT_DIR))
    dictionary = write_data_dictionary(outputs)
    manifest = write_source_manifest()
    validation_path = write_validation_report(outputs)
    summary = {
        "project": PROJECT_DIR.name,
        "source_dir": str(SOURCE_DIR),
        "export_dir": str(EXPORT_DIR),
        "outputs": written,
        "data_dictionary_rows": int(len(dictionary)),
        "source_manifest_rows": int(len(manifest)),
        "validation_report": str(validation_path.relative_to(PROJECT_DIR)),
    }
    (EXPORT_DIR / "build_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()

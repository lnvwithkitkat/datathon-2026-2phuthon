from __future__ import annotations

from pathlib import Path

import pandas as pd
from PIL import Image, ImageDraw, ImageFont
from reportlab.lib.pagesizes import landscape
from reportlab.pdfgen import canvas


PROJECT_DIR = Path(__file__).resolve().parents[1]
EXPORT_DIR = PROJECT_DIR / "docs" / "assets" / "exports" / "tableau"
SCREENSHOT_DIR = PROJECT_DIR / "docs" / "assets" / "screenshots"
PDF_PATH = SCREENSHOT_DIR / "VinDatathon_Task2_Dashboard_Preview_NON_TABLEAU.pdf"

W, H = 1600, 900
BG = "#f8faf7"
INK = "#17211a"
MUTED = "#647067"
GREEN = "#2f7d4b"
TEAL = "#178f91"
ORANGE = "#d9802e"
RED = "#b64747"
BLUE = "#3f6fa6"
PURPLE = "#7756a8"
LIGHT = "#ffffff"
GRID = "#d8ded7"


def font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    name = "arialbd.ttf" if bold else "arial.ttf"
    path = Path("C:/Windows/Fonts") / name
    return ImageFont.truetype(str(path), size=size)


def money(v: float) -> str:
    if abs(v) >= 1_000_000_000:
        return f"{v / 1_000_000_000:.1f}B"
    if abs(v) >= 1_000_000:
        return f"{v / 1_000_000:.1f}M"
    return f"{v:,.0f}"


def pct(v: float) -> str:
    return f"{v * 100:.1f}%"


def new_page(title: str, subtitle: str) -> tuple[Image.Image, ImageDraw.ImageDraw]:
    img = Image.new("RGB", (W, H), BG)
    draw = ImageDraw.Draw(img)
    draw.rectangle([0, 0, W, 86], fill="#ffffff")
    draw.text((44, 22), title, fill=INK, font=font(28, True))
    draw.text((44, 58), subtitle, fill=MUTED, font=font(16))
    draw.text((1260, 28), "NON-TABLEAU PREVIEW", fill=RED, font=font(16, True))
    return img, draw


def card(draw: ImageDraw.ImageDraw, box: tuple[int, int, int, int], title: str, value: str, note: str, color: str = GREEN) -> None:
    x1, y1, x2, y2 = box
    draw.rounded_rectangle(box, radius=8, fill=LIGHT, outline=GRID, width=2)
    draw.text((x1 + 18, y1 + 14), title, fill=MUTED, font=font(14, True))
    draw.text((x1 + 18, y1 + 42), value, fill=color, font=font(30, True))
    draw.text((x1 + 18, y1 + 82), note, fill=MUTED, font=font(13))


def panel(draw: ImageDraw.ImageDraw, box: tuple[int, int, int, int], title: str) -> None:
    draw.rounded_rectangle(box, radius=8, fill=LIGHT, outline=GRID, width=2)
    draw.text((box[0] + 18, box[1] + 14), title, fill=INK, font=font(18, True))


def line_chart(draw: ImageDraw.ImageDraw, box: tuple[int, int, int, int], values: list[float], color: str, label: str) -> None:
    x1, y1, x2, y2 = box
    panel(draw, box, label)
    px1, py1, px2, py2 = x1 + 54, y1 + 62, x2 - 24, y2 - 42
    draw.line([px1, py2, px2, py2], fill=GRID, width=2)
    draw.line([px1, py1, px1, py2], fill=GRID, width=2)
    if not values:
        return
    lo, hi = min(values), max(values)
    span = hi - lo if hi != lo else 1
    pts = []
    for i, v in enumerate(values):
        x = px1 + (px2 - px1) * i / max(1, len(values) - 1)
        y = py2 - (py2 - py1) * (v - lo) / span
        pts.append((x, y))
    draw.line(pts, fill=color, width=4)
    for x, y in pts[:: max(1, len(pts) // 8)]:
        draw.ellipse([x - 4, y - 4, x + 4, y + 4], fill=color)
    draw.text((px1, py2 + 10), f"min {money(lo)}", fill=MUTED, font=font(12))
    draw.text((px2 - 120, py1 - 24), f"max {money(hi)}", fill=MUTED, font=font(12))


def bar_chart(draw: ImageDraw.ImageDraw, box: tuple[int, int, int, int], rows: list[tuple[str, float]], color: str, title: str) -> None:
    x1, y1, x2, y2 = box
    panel(draw, box, title)
    px1, py1, px2 = x1 + 230, y1 + 62, x2 - 32
    bar_h, gap = 28, 14
    max_v = max([abs(v) for _, v in rows] or [1])
    for i, (name, value) in enumerate(rows[:8]):
        y = py1 + i * (bar_h + gap)
        draw.text((x1 + 18, y + 4), name[:24], fill=INK, font=font(14))
        w = int((px2 - px1) * abs(value) / max_v)
        fill = color if value >= 0 else RED
        draw.rounded_rectangle([px1, y, px1 + w, y + bar_h], radius=4, fill=fill)
        val = pct(value) if abs(value) <= 1.5 else money(value)
        draw.text((px1 + w + 8, y + 4), val, fill=MUTED, font=font(13))


def table(draw: ImageDraw.ImageDraw, box: tuple[int, int, int, int], rows: pd.DataFrame, title: str) -> None:
    panel(draw, box, title)
    x1, y1, x2, _ = box
    y = y1 + 58
    for _, row in rows.head(7).iterrows():
        action = str(row.get("recommended_action", ""))[:45]
        entity = str(row.get("entity", ""))[:34]
        priority = str(row.get("priority", ""))
        draw.text((x1 + 18, y), priority, fill=RED if priority == "Critical" else ORANGE, font=font(13, True))
        draw.text((x1 + 110, y), entity, fill=INK, font=font(13, True))
        draw.text((x1 + 420, y), action, fill=MUTED, font=font(13))
        y += 36
        draw.line([x1 + 18, y - 8, x2 - 18, y - 8], fill="#edf0ec", width=1)


def load() -> dict[str, pd.DataFrame]:
    return {
        "kpi": pd.read_csv(EXPORT_DIR / "dashboard_kpis.csv"),
        "daily": pd.read_csv(EXPORT_DIR / "daily_kpi.csv", parse_dates=["date"]),
        "forecast": pd.read_csv(EXPORT_DIR / "growth_forecast_monthly.csv", parse_dates=["date"]),
        "season": pd.read_csv(EXPORT_DIR / "seasonality_indices.csv"),
        "signals": pd.read_csv(EXPORT_DIR / "predictive_signals.csv"),
        "rec": pd.read_csv(EXPORT_DIR / "recommendations.csv"),
    }


def kpi_value(kpi: pd.DataFrame, name: str) -> float:
    return float(kpi.loc[kpi["kpi_name"].eq(name), "kpi_value"].iloc[0])


def make_pages() -> list[Path]:
    data = load()
    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)
    paths: list[Path] = []

    kpi = data["kpi"]
    daily = data["daily"].tail(365)
    forecast = data["forecast"]
    season = data["season"]
    signals = data["signals"]
    rec = data["rec"]

    pages = []

    img, d = new_page("Executive Overview", "Tổng quan tăng trưởng, biên lợi nhuận và hành động ưu tiên")
    cards = [
        ("Revenue", money(kpi_value(kpi, "Revenue")), "sales.csv official", GREEN),
        ("Gross Margin %", pct(kpi_value(kpi, "Gross margin %")), "margin / revenue", TEAL),
        ("Cancel Rate", pct(kpi_value(kpi, "Cancel rate")), "order status", ORANGE),
        ("COD Risk", pct(kpi_value(kpi, "COD risk rate")), "cancel + return", RED),
    ]
    for i, c in enumerate(cards):
        card(d, (44 + i * 380, 112, 390 + i * 380, 226), *c)
    line_chart(d, (44, 260, 760, 620), daily["sales_revenue_rolling_30d"].tolist(), GREEN, "30-day Rolling Revenue")
    table(d, (800, 260, 1556, 620), rec, "Prescriptive Action Queue")
    d.text((54, 690), "CEO message: growth exists, but margin leakage, COD risk, returns, and inventory imbalance decide the next actions.", fill=INK, font=font(22, True))
    pages.append(("01_executive_overview.png", img))

    img, d = new_page("Growth Forecast & Seasonality", "Predictive EDA: xu hướng, mùa vụ và tín hiệu dẫn dắt")
    line_chart(d, (44, 122, 920, 620), forecast["forecast_revenue"].tail(36).tolist(), BLUE, "Monthly Trend + Six-month Forecast")
    month_rows = season[season["grain"].eq("month_of_year")].sort_values("seasonality_index", ascending=False)
    bar_chart(d, (960, 122, 1556, 620), list(zip(month_rows["period_name"], month_rows["seasonality_index"])), PURPLE, "Month Seasonality Index")
    d.text((54, 690), "Predictive statement: March-June carry stronger historical revenue seasonality; inventory and return risks should be addressed before these peaks.", fill=INK, font=font(22, True))
    pages.append(("02_growth_forecast_seasonality.png", img))

    img, d = new_page("Profit & Promotion Leakage", "Khuyến mãi tạo doanh thu nhưng phá biên lợi nhuận ở một số phân khúc")
    promo_rows = rec[rec["signal_type"].eq("Promotion margin risk")]
    bar_chart(d, (44, 122, 760, 570), list(zip(promo_rows["entity"], promo_rows["risk_score"])), ORANGE, "Promotion Margin Risk")
    card(d, (820, 142, 1150, 270), "Promo Margin %", pct(kpi_value(kpi, "Promo margin %")), "promoted items", RED)
    card(d, (1190, 142, 1520, 270), "No-promo Margin %", pct(kpi_value(kpi, "No-promo margin %")), "non-promoted items", GREEN)
    table(d, (820, 310, 1556, 650), promo_rows, "Pricing Actions")
    pages.append(("03_profit_promotion_leakage.png", img))

    img, d = new_page("Customer, Channel & Payment Risk", "Doanh thu chất lượng thấp theo payment, source và traffic efficiency")
    pay_channel = rec[rec["signal_type"].isin(["Payment risk", "Channel quality risk"])]
    bar_chart(d, (44, 122, 760, 570), list(zip(pay_channel["entity"], pay_channel["risk_score"])), RED, "Payment / Channel Risk")
    table(d, (820, 122, 1556, 570), pay_channel, "Risk Controls and Spend Shift")
    d.text((54, 650), "COD is the main payment risk signal; channel quality should be judged by revenue quality, not sessions alone.", fill=INK, font=font(22, True))
    pages.append(("04_customer_channel_payment_risk.png", img))

    img, d = new_page("Returns, Reviews & Fulfillment", "Return/refund leakage and customer-experience signals")
    wrong_size = rec[rec["signal_type"].eq("Wrong-size return risk")]
    bar_chart(d, (44, 122, 760, 570), list(zip(wrong_size["entity"], wrong_size["risk_score"])), RED, "Wrong-size Return Risk")
    table(d, (820, 122, 1556, 570), wrong_size, "CX / Merchandising Actions")
    d.text((54, 650), "Wrong-size return pressure concentrates in specific Streetwear size combinations; size guidance is a quantified CX intervention.", fill=INK, font=font(22, True))
    pages.append(("05_returns_reviews_fulfillment.png", img))

    img, d = new_page("Inventory Actions", "Stockout và overstock cùng tồn tại, cần quyết định theo quadrant")
    inv = rec[rec["signal_type"].isin(["Stockout risk", "Overstock risk"])]
    bar_chart(d, (44, 122, 760, 650), list(zip(inv["entity"], inv["risk_score"])), PURPLE, "Inventory Risk Score")
    table(d, (820, 122, 1556, 650), inv, "Supply Chain Actions")
    pages.append(("06_inventory_actions.png", img))

    for filename, img in pages:
        path = SCREENSHOT_DIR / filename
        img.save(path, "PNG")
        paths.append(path)

    c = canvas.Canvas(str(PDF_PATH), pagesize=landscape((W, H)))
    for path in paths:
        c.drawImage(str(path), 0, 0, width=W, height=H)
        c.showPage()
    c.save()
    paths.append(PDF_PATH)
    return paths


def main() -> None:
    paths = make_pages()
    for path in paths:
        print(path.relative_to(PROJECT_DIR))


if __name__ == "__main__":
    main()

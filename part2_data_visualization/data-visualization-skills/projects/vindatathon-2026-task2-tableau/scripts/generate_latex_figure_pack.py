from __future__ import annotations

import hashlib
import json
import math
import textwrap
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable, Iterable

import numpy as np
import pandas as pd
from PIL import Image, ImageDraw, ImageFont
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas


PROJECT_DIR = Path(__file__).resolve().parents[1]
EXPORT_DIR = PROJECT_DIR / "docs" / "assets" / "exports" / "tableau"
FIGURE_DIR = PROJECT_DIR / "docs" / "assets" / "figures" / "latex"
PDF_PATH = FIGURE_DIR / "VinDatathon_Task2_LaTeX_Figure_Pack.pdf"
ZIP_PATH = FIGURE_DIR / "VinDatathon_Task2_LaTeX_Figure_Pack.zip"
MANIFEST_PATH = FIGURE_DIR / "figure_manifest.json"
LATEX_SNIPPET_PATH = FIGURE_DIR / "latex_include_figures.tex"

W, H = 3200, 1800
DPI = 300
MARGIN = 88

COLORS = {
    "bg": "#f7f8f4",
    "panel": "#ffffff",
    "ink": "#152018",
    "muted": "#617067",
    "grid": "#d9dfd6",
    "green": "#2f7d4b",
    "teal": "#178f91",
    "blue": "#3f6fa6",
    "purple": "#7654a7",
    "orange": "#d9842e",
    "red": "#b84848",
    "yellow": "#e3b23c",
    "soft_green": "#e9f3ec",
    "soft_red": "#f7e9e8",
    "soft_blue": "#eaf0f7",
    "soft_orange": "#faefe3",
}


def font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    candidates = [
        Path("C:/Windows/Fonts/arialbd.ttf" if bold else "C:/Windows/Fonts/arial.ttf"),
        Path("C:/Windows/Fonts/segoeuib.ttf" if bold else "C:/Windows/Fonts/segoeui.ttf"),
        Path("C:/Windows/Fonts/calibrib.ttf" if bold else "C:/Windows/Fonts/calibri.ttf"),
    ]
    for path in candidates:
        if path.exists():
            return ImageFont.truetype(str(path), size=size)
    return ImageFont.load_default()


F = {
    "title": font(54, True),
    "subtitle": font(29),
    "section": font(32, True),
    "label": font(24, True),
    "body": font(23),
    "small": font(19),
    "tiny": font(16),
    "number": font(50, True),
    "big": font(68, True),
}


def clean_text(value: object) -> str:
    if pd.isna(value):
        return ""
    return str(value).replace("_", " ").replace("/", " / ").strip()


def fmt_money(value: float) -> str:
    if value is None or pd.isna(value):
        return "n/a"
    sign = "-" if value < 0 else ""
    value = abs(float(value))
    if value >= 1_000_000_000:
        return f"{sign}{value / 1_000_000_000:.1f}B VND"
    if value >= 1_000_000:
        return f"{sign}{value / 1_000_000:.1f}M VND"
    if value >= 1_000:
        return f"{sign}{value / 1_000:.1f}K VND"
    return f"{sign}{value:,.0f} VND"


def fmt_plain_money(value: float) -> str:
    if value is None or pd.isna(value):
        return "n/a"
    sign = "-" if value < 0 else ""
    value = abs(float(value))
    if value >= 1_000_000_000:
        return f"{sign}{value / 1_000_000_000:.1f}B"
    if value >= 1_000_000:
        return f"{sign}{value / 1_000_000:.1f}M"
    if value >= 1_000:
        return f"{sign}{value / 1_000:.1f}K"
    return f"{sign}{value:,.0f}"


def fmt_pct(value: float, already_percent: bool = False) -> str:
    if value is None or pd.isna(value):
        return "n/a"
    v = float(value)
    if not already_percent:
        v *= 100
    return f"{v:.1f}%"


def fmt_num(value: float) -> str:
    if value is None or pd.isna(value):
        return "n/a"
    return f"{float(value):,.0f}"


def bool_series(series: pd.Series) -> pd.Series:
    return series.astype(str).str.lower().isin(["true", "1", "yes"])


def color_for_pct(value: float) -> str:
    if value >= 0.5:
        return COLORS["red"]
    if value >= 0.2:
        return COLORS["orange"]
    return COLORS["green"]


def text_size(draw: ImageDraw.ImageDraw, text: str, fnt: ImageFont.FreeTypeFont) -> tuple[int, int]:
    box = draw.textbbox((0, 0), text, font=fnt)
    return box[2] - box[0], box[3] - box[1]


def wrap_lines(draw: ImageDraw.ImageDraw, text: str, fnt: ImageFont.FreeTypeFont, max_width: int) -> list[str]:
    words = clean_text(text).split()
    if not words:
        return [""]
    lines: list[str] = []
    current = words[0]
    for word in words[1:]:
        candidate = f"{current} {word}"
        if text_size(draw, candidate, fnt)[0] <= max_width:
            current = candidate
        else:
            lines.append(current)
            current = word
    lines.append(current)
    return lines


def draw_wrapped(
    draw: ImageDraw.ImageDraw,
    xy: tuple[int, int],
    text: str,
    fnt: ImageFont.FreeTypeFont,
    fill: str,
    max_width: int,
    line_gap: int = 7,
    max_lines: int | None = None,
) -> int:
    lines = wrap_lines(draw, text, fnt, max_width)
    if max_lines is not None and len(lines) > max_lines:
        lines = lines[:max_lines]
        lines[-1] = lines[-1].rstrip(".") + "..."
    x, y = xy
    line_height = text_size(draw, "Ag", fnt)[1] + line_gap
    for line in lines:
        draw.text((x, y), line, fill=fill, font=fnt)
        y += line_height
    return y


def new_canvas(title: str, subtitle: str) -> tuple[Image.Image, ImageDraw.ImageDraw]:
    img = Image.new("RGB", (W, H), COLORS["bg"])
    draw = ImageDraw.Draw(img)
    draw.rectangle([0, 0, W, 150], fill=COLORS["panel"])
    draw.text((MARGIN, 35), title, fill=COLORS["ink"], font=F["title"])
    draw.text((MARGIN, 101), subtitle, fill=COLORS["muted"], font=F["subtitle"])
    draw.text((W - 575, 48), "VinDatathon 2026 Task 2", fill=COLORS["green"], font=F["label"])
    draw.text((W - 575, 86), "Scripted, reproducible figure", fill=COLORS["muted"], font=F["small"])
    draw.line([MARGIN, 150, W - MARGIN, 150], fill=COLORS["grid"], width=3)
    return img, draw


def rounded_panel(draw: ImageDraw.ImageDraw, box: tuple[int, int, int, int], title: str | None = None) -> tuple[int, int, int, int]:
    draw.rounded_rectangle(box, radius=18, fill=COLORS["panel"], outline=COLORS["grid"], width=3)
    x1, y1, x2, y2 = box
    if title:
        draw.text((x1 + 34, y1 + 26), title, fill=COLORS["ink"], font=F["section"])
        return x1 + 34, y1 + 86, x2 - 34, y2 - 34
    return x1 + 28, y1 + 28, x2 - 28, y2 - 28


def kpi_card(
    draw: ImageDraw.ImageDraw,
    box: tuple[int, int, int, int],
    label: str,
    value: str,
    note: str,
    color: str,
) -> None:
    draw.rounded_rectangle(box, radius=18, fill=COLORS["panel"], outline=COLORS["grid"], width=3)
    x1, y1, x2, _ = box
    draw.text((x1 + 26, y1 + 25), label, fill=COLORS["muted"], font=F["label"])
    draw.text((x1 + 26, y1 + 72), value, fill=color, font=F["number"])
    draw_wrapped(draw, (x1 + 26, y1 + 142), note, F["small"], COLORS["muted"], x2 - x1 - 52, max_lines=2)


def draw_axis_grid(
    draw: ImageDraw.ImageDraw,
    plot: tuple[int, int, int, int],
    y_min: float,
    y_max: float,
    formatter: Callable[[float], str],
    ticks: int = 5,
) -> None:
    x1, y1, x2, y2 = plot
    draw.line([x1, y2, x2, y2], fill=COLORS["grid"], width=3)
    draw.line([x1, y1, x1, y2], fill=COLORS["grid"], width=3)
    for i in range(ticks + 1):
        v = y_min + (y_max - y_min) * i / ticks
        y = y2 - (y2 - y1) * i / ticks
        draw.line([x1, y, x2, y], fill="#edf0ea", width=2)
        draw.text((x1 - 86, y - 12), formatter(v), fill=COLORS["muted"], font=F["tiny"])


def nice_y_bounds(y_min: float, y_max: float, max_ticks: int = 7) -> tuple[float, float, int]:
    if y_min == y_max:
        y_max = y_min + 1
    span = abs(y_max - y_min)
    raw_step = span / max_ticks
    magnitude = 10 ** math.floor(math.log10(raw_step)) if raw_step > 0 else 1
    normalized = raw_step / magnitude
    if normalized <= 1:
        step = 1 * magnitude
    elif normalized <= 2:
        step = 2 * magnitude
    elif normalized <= 2.5:
        step = 2.5 * magnitude
    elif normalized <= 5:
        step = 5 * magnitude
    elif normalized <= 7.5:
        step = 7.5 * magnitude
    else:
        step = 10 * magnitude
    nice_min = math.floor(y_min / step) * step
    nice_max = math.ceil(y_max / step) * step
    intervals = max(1, int(round((nice_max - nice_min) / step)))
    return nice_min, nice_max, intervals


def scale_points(
    values: Iterable[float],
    plot: tuple[int, int, int, int],
    y_min: float,
    y_max: float,
) -> list[tuple[float, float] | None]:
    x1, y1, x2, y2 = plot
    vals = list(values)
    pts: list[tuple[float, float] | None] = []
    denom = max(1, len(vals) - 1)
    span = y_max - y_min if y_max != y_min else 1
    for i, v in enumerate(vals):
        x = x1 + (x2 - x1) * i / denom
        if v is None or pd.isna(v):
            pts.append(None)
            continue
        y = y2 - (y2 - y1) * (float(v) - y_min) / span
        pts.append((x, y))
    return pts


def draw_polyline(
    draw: ImageDraw.ImageDraw,
    points: list[tuple[float, float] | None],
    color: str,
    width: int = 7,
    dashed: bool = False,
) -> None:
    prev: tuple[float, float] | None = None
    for point in points:
        if point is None:
            prev = None
            continue
        if prev is not None:
            if dashed:
                draw_dashed_line(draw, prev, point, color, width=width)
            else:
                draw.line([prev, point], fill=color, width=width)
        prev = point
    for point in points:
        if point is not None:
            x, y = point
            draw.ellipse([x - 6, y - 6, x + 6, y + 6], fill=color)


def draw_dashed_line(
    draw: ImageDraw.ImageDraw,
    p1: tuple[float, float],
    p2: tuple[float, float],
    color: str,
    width: int = 5,
    dash: int = 22,
    gap: int = 14,
) -> None:
    x1, y1 = p1
    x2, y2 = p2
    length = math.hypot(x2 - x1, y2 - y1)
    if length == 0:
        return
    dx = (x2 - x1) / length
    dy = (y2 - y1) / length
    pos = 0.0
    while pos < length:
        end = min(pos + dash, length)
        draw.line(
            [(x1 + dx * pos, y1 + dy * pos), (x1 + dx * end, y1 + dy * end)],
            fill=color,
            width=width,
        )
        pos += dash + gap


def draw_line_chart(
    draw: ImageDraw.ImageDraw,
    box: tuple[int, int, int, int],
    title: str,
    labels: list[str],
    series: list[tuple[str, list[float], str]],
    y_formatter: Callable[[float], str] = fmt_plain_money,
    y_floor_zero: bool = True,
) -> None:
    ix1, iy1, ix2, iy2 = rounded_panel(draw, box, title)
    plot = (ix1 + 112, iy1 + 12, ix2 - 16, iy2 - 72)
    all_values = [float(v) for _, vals, _ in series for v in vals if v is not None and not pd.isna(v)]
    if not all_values:
        return
    raw_min = min(all_values)
    raw_max = max(all_values)
    if y_floor_zero:
        y_min = min(0, raw_min)
        y_max = max(0, raw_max)
    else:
        y_min = raw_min
        y_max = raw_max
    pad = (y_max - y_min) * 0.08 if y_max != y_min else 1
    if y_min < 0:
        y_min -= pad
    y_max += pad
    y_min, y_max, tick_count = nice_y_bounds(y_min, y_max)
    draw_axis_grid(draw, plot, y_min, y_max, y_formatter, ticks=tick_count)
    for _, vals, color in series:
        draw_polyline(draw, scale_points(vals, plot, y_min, y_max), color)
    if labels:
        x1, _, x2, y2 = plot
        for idx in sorted(set([0, len(labels) // 2, len(labels) - 1])):
            x = x1 + (x2 - x1) * idx / max(1, len(labels) - 1)
            draw.text((x - 52, y2 + 24), labels[idx], fill=COLORS["muted"], font=F["tiny"])
    lx = ix1 + 112
    for name, _, color in series:
        draw.rounded_rectangle([lx, iy2 - 36, lx + 34, iy2 - 14], radius=5, fill=color)
        draw.text((lx + 46, iy2 - 42), name, fill=COLORS["muted"], font=F["small"])
        lx += text_size(draw, name, F["small"])[0] + 118


def draw_forecast_chart(
    draw: ImageDraw.ImageDraw,
    box: tuple[int, int, int, int],
    forecast: pd.DataFrame,
) -> None:
    ix1, iy1, ix2, iy2 = rounded_panel(draw, box, "Revenue trend and six-month predictive signal")
    plot = (ix1 + 118, iy1 + 16, ix2 - 24, iy2 - 86)
    df = forecast.copy()
    df["is_forecast_bool"] = bool_series(df["is_forecast"])
    labels = pd.to_datetime(df["date"]).dt.strftime("%Y-%m").tolist()
    actual = df["sales_revenue"].where(~df["is_forecast_bool"]).tolist()
    pred = df["forecast_revenue"].tolist()
    lower = df["forecast_lower_revenue"].tolist()
    upper = df["forecast_upper_revenue"].tolist()
    all_values = [v for v in lower + upper + pred if not pd.isna(v)]
    y_min = 0
    y_max = max(all_values) * 1.08
    y_min, y_max, tick_count = nice_y_bounds(y_min, y_max)
    draw_axis_grid(draw, plot, y_min, y_max, fmt_plain_money, ticks=tick_count)
    lower_pts = scale_points(lower, plot, y_min, y_max)
    upper_pts = scale_points(upper, plot, y_min, y_max)
    band_pts = [p for p in upper_pts if p is not None] + [p for p in reversed(lower_pts) if p is not None]
    if len(band_pts) >= 3:
        draw.polygon(band_pts, fill="#d9e7f5")
    draw_polyline(draw, scale_points(actual, plot, y_min, y_max), COLORS["green"], width=7)
    draw_polyline(draw, scale_points(pred, plot, y_min, y_max), COLORS["blue"], width=7, dashed=True)
    x1, _, x2, y2 = plot
    for idx in sorted(set([0, len(labels) // 3, 2 * len(labels) // 3, len(labels) - 1])):
        x = x1 + (x2 - x1) * idx / max(1, len(labels) - 1)
        draw.text((x - 58, y2 + 24), labels[idx], fill=COLORS["muted"], font=F["tiny"])
    legend = [("Actual revenue", COLORS["green"]), ("Trend + seasonality", COLORS["blue"]), ("Forecast band", "#8fb3d9")]
    lx = ix1 + 118
    for name, color in legend:
        draw.rounded_rectangle([lx, iy2 - 43, lx + 34, iy2 - 21], radius=5, fill=color)
        draw.text((lx + 46, iy2 - 49), name, fill=COLORS["muted"], font=F["small"])
        lx += text_size(draw, name, F["small"])[0] + 118


def draw_horizontal_bars(
    draw: ImageDraw.ImageDraw,
    box: tuple[int, int, int, int],
    title: str,
    rows: list[tuple[str, float]],
    value_formatter: Callable[[float], str],
    color: str = COLORS["blue"],
    max_rows: int = 8,
    zero_based: bool = True,
) -> None:
    ix1, iy1, ix2, iy2 = rounded_panel(draw, box, title)
    rows = [(clean_text(n), float(v)) for n, v in rows if v is not None and not pd.isna(v)][:max_rows]
    if not rows:
        return
    max_abs = max(abs(v) for _, v in rows)
    min_v = 0 if zero_based else min(v for _, v in rows)
    max_v = max(v for _, v in rows)
    if zero_based:
        scale_max = max_abs if max_abs else 1
    else:
        scale_max = max(abs(min_v), abs(max_v), 1)
    bar_area_x1 = ix1 + 430
    bar_area_x2 = ix2 - 160
    row_h = max(48, int((iy2 - iy1 - 20) / max(1, len(rows))))
    for i, (name, value) in enumerate(rows):
        y = iy1 + i * row_h + 8
        draw_wrapped(draw, (ix1, y + 2), name, F["small"], COLORS["ink"], 390, max_lines=2)
        width = int((bar_area_x2 - bar_area_x1) * abs(value) / scale_max)
        bar_color = color if value >= 0 else COLORS["red"]
        if not zero_based:
            mid = bar_area_x1 + (bar_area_x2 - bar_area_x1) // 2
            if value >= 0:
                rect = [mid, y, mid + width // 2, y + 30]
            else:
                rect = [mid - width // 2, y, mid, y + 30]
        else:
            rect = [bar_area_x1, y, bar_area_x1 + width, y + 30]
        draw.rounded_rectangle(rect, radius=8, fill=bar_color)
        draw.text((bar_area_x2 + 24, y - 1), value_formatter(value), fill=COLORS["muted"], font=F["small"])


def draw_grouped_bars(
    draw: ImageDraw.ImageDraw,
    box: tuple[int, int, int, int],
    title: str,
    rows: list[tuple[str, float, float]],
    labels: tuple[str, str],
    formatter: Callable[[float], str] = fmt_pct,
    colors: tuple[str, str] = (COLORS["orange"], COLORS["green"]),
) -> None:
    ix1, iy1, ix2, iy2 = rounded_panel(draw, box, title)
    rows = rows[:7]
    max_v = max([abs(a) for _, a, _ in rows] + [abs(b) for _, _, b in rows] + [0.01])
    bar_area_x1 = ix1 + 480
    bar_area_x2 = ix2 - 180
    row_h = max(80, int((iy2 - iy1 - 20) / max(1, len(rows))))
    for i, (name, v1, v2) in enumerate(rows):
        y = iy1 + i * row_h + 10
        draw_wrapped(draw, (ix1, y), name, F["small"], COLORS["ink"], 430, max_lines=2)
        w1 = int((bar_area_x2 - bar_area_x1) * abs(v1) / max_v)
        w2 = int((bar_area_x2 - bar_area_x1) * abs(v2) / max_v)
        draw.rounded_rectangle([bar_area_x1, y, bar_area_x1 + w1, y + 27], radius=7, fill=colors[0])
        draw.rounded_rectangle([bar_area_x1, y + 34, bar_area_x1 + w2, y + 61], radius=7, fill=colors[1])
        draw.text((bar_area_x2 + 22, y - 1), formatter(v1), fill=COLORS["muted"], font=F["tiny"])
        draw.text((bar_area_x2 + 22, y + 33), formatter(v2), fill=COLORS["muted"], font=F["tiny"])
    lx = ix1
    for label, c in zip(labels, colors):
        draw.rounded_rectangle([lx, iy2 - 26, lx + 30, iy2 - 8], radius=5, fill=c)
        draw.text((lx + 42, iy2 - 32), label, fill=COLORS["muted"], font=F["tiny"])
        lx += text_size(draw, label, F["tiny"])[0] + 110


def draw_recommendation_table(
    draw: ImageDraw.ImageDraw,
    box: tuple[int, int, int, int],
    title: str,
    rec: pd.DataFrame,
    max_rows: int = 6,
) -> None:
    ix1, iy1, ix2, iy2 = rounded_panel(draw, box, title)
    cols = [("Priority", 130), ("Signal / Entity", 520), ("Recommended action", ix2 - ix1 - 690)]
    x = ix1
    for label, width in cols:
        draw.text((x, iy1), label, fill=COLORS["muted"], font=F["small"])
        x += width
    y = iy1 + 44
    row_h = int((iy2 - y) / max_rows)
    for _, row in rec.head(max_rows).iterrows():
        priority = clean_text(row.get("priority", ""))
        signal = f"{clean_text(row.get('signal_type', ''))}: {clean_text(row.get('entity', ''))}"
        action = clean_text(row.get("recommended_action", ""))
        color = COLORS["red"] if priority.lower() == "critical" else COLORS["orange"]
        draw.rounded_rectangle([ix1, y, ix1 + 104, y + 34], radius=8, fill=color)
        draw.text((ix1 + 14, y + 5), priority[:8], fill="white", font=F["tiny"])
        draw_wrapped(draw, (ix1 + 130, y), signal, F["small"], COLORS["ink"], 485, max_lines=2)
        draw_wrapped(draw, (ix1 + 650, y), action, F["small"], COLORS["muted"], ix2 - ix1 - 670, max_lines=2)
        draw.line([ix1, y + row_h - 12, ix2, y + row_h - 12], fill="#edf0ea", width=2)
        y += row_h


def draw_scatter_inventory(
    draw: ImageDraw.ImageDraw,
    box: tuple[int, int, int, int],
    prod: pd.DataFrame,
) -> None:
    ix1, iy1, ix2, iy2 = rounded_panel(draw, box, "Inventory quadrant: stockout pressure vs overstock pressure")
    plot = (ix1 + 96, iy1 + 30, ix2 - 40, iy2 - 95)
    x1, y1, x2, y2 = plot
    draw.line([x1, y2, x2, y2], fill=COLORS["grid"], width=3)
    draw.line([x1, y1, x1, y2], fill=COLORS["grid"], width=3)
    for tick in range(0, 101, 25):
        x = x1 + (x2 - x1) * tick / 100
        y = y2 - (y2 - y1) * tick / 100
        draw.line([x, y1, x, y2], fill="#edf0ea", width=2)
        draw.line([x1, y, x2, y], fill="#edf0ea", width=2)
        draw.text((x - 14, y2 + 22), str(tick), fill=COLORS["muted"], font=F["tiny"])
        draw.text((x1 - 48, y - 10), str(tick), fill=COLORS["muted"], font=F["tiny"])
    draw.line([x1 + (x2 - x1) * 50 / 100, y1, x1 + (x2 - x1) * 50 / 100, y2], fill=COLORS["orange"], width=3)
    draw.line([x1, y2 - (y2 - y1) * 50 / 100, x2, y2 - (y2 - y1) * 50 / 100], fill=COLORS["orange"], width=3)
    for _, row in prod.iterrows():
        sx = max(0, min(100, float(row["stockout_pressure_score"])))
        oy = max(0, min(100, float(row["overstock_pressure_score"])))
        x = x1 + (x2 - x1) * sx / 100
        y = y2 - (y2 - y1) * oy / 100
        color = COLORS["red"] if sx >= 50 and oy >= 50 else COLORS["purple"] if oy >= 50 else COLORS["orange"] if sx >= 50 else COLORS["teal"]
        draw.ellipse([x - 5, y - 5, x + 5, y + 5], fill=color)
    top = prod.assign(max_risk=prod[["stockout_pressure_score", "overstock_pressure_score"]].max(axis=1)).nlargest(5, "max_risk")
    for _, row in top.iterrows():
        sx = max(0, min(100, float(row["stockout_pressure_score"])))
        oy = max(0, min(100, float(row["overstock_pressure_score"])))
        x = x1 + (x2 - x1) * sx / 100
        y = y2 - (y2 - y1) * oy / 100
        label = clean_text(row["product_name"])[:24]
        draw.line([x, y, min(x + 120, x2 - 220), max(y - 36, y1 + 6)], fill=COLORS["muted"], width=2)
        draw.text((min(x + 126, x2 - 220), max(y - 49, y1 + 6)), label, fill=COLORS["ink"], font=F["tiny"])
    draw.text((x1 + (x2 - x1) // 2 - 130, y2 + 55), "Stockout pressure", fill=COLORS["muted"], font=F["small"])
    draw.text((x1 - 56, y1 - 24), "Overstock pressure", fill=COLORS["muted"], font=F["small"])


def draw_validation_erd(draw: ImageDraw.ImageDraw, box: tuple[int, int, int, int], data: dict[str, pd.DataFrame]) -> None:
    ix1, iy1, ix2, iy2 = rounded_panel(draw, box, "Data model and validation proof")
    source_x = ix1
    source_y = iy1 + 20
    mid_x = ix1 + 760
    out_x = ix1 + 1540
    box_w = 540
    box_h = 90
    sources = ["orders", "order_items", "products", "customers", "payments", "shipments", "returns", "reviews", "traffic", "inventory"]
    outputs = ["orders_enriched", "order_items_enriched", "daily_kpi", "inventory_monthly", "predictive_signals", "recommendations"]
    draw.text((source_x, iy1), "Approved business CSVs", fill=COLORS["muted"], font=F["small"])
    for i, name in enumerate(sources):
        y = source_y + i * 58
        draw.rounded_rectangle([source_x, y, source_x + 340, y + 42], radius=9, fill=COLORS["soft_blue"], outline=COLORS["grid"], width=2)
        draw.text((source_x + 18, y + 8), name, fill=COLORS["ink"], font=F["tiny"])
    center_boxes = [
        ("Order grain", "customer, geography, payment, fulfillment"),
        ("Line grain", "product, promotion, return, review"),
        ("Time grain", "daily/monthly KPI and seasonality"),
        ("Risk grain", "forecast, stockout, return, COD, promo"),
    ]
    for i, (name, note) in enumerate(center_boxes):
        y = iy1 + 72 + i * 138
        draw.rounded_rectangle([mid_x, y, mid_x + box_w, y + box_h], radius=13, fill=COLORS["panel"], outline=COLORS["green"], width=3)
        draw.text((mid_x + 24, y + 14), name, fill=COLORS["green"], font=F["label"])
        draw.text((mid_x + 24, y + 52), note, fill=COLORS["muted"], font=F["tiny"])
    for i, name in enumerate(outputs):
        y = iy1 + 35 + i * 82
        draw.rounded_rectangle([out_x, y, out_x + 470, y + 56], radius=12, fill=COLORS["soft_green"], outline=COLORS["grid"], width=2)
        draw.text((out_x + 20, y + 15), name, fill=COLORS["ink"], font=F["small"])
    for y in [iy1 + 128, iy1 + 266, iy1 + 404, iy1 + 542]:
        draw.line([source_x + 360, y, mid_x - 20, y], fill=COLORS["muted"], width=3)
        draw.polygon([(mid_x - 20, y), (mid_x - 42, y - 10), (mid_x - 42, y + 10)], fill=COLORS["muted"])
    for y in [iy1 + 128, iy1 + 266, iy1 + 404, iy1 + 542]:
        draw.line([mid_x + box_w, y, out_x - 20, y], fill=COLORS["muted"], width=3)
        draw.polygon([(out_x - 20, y), (out_x - 42, y - 10), (out_x - 42, y + 10)], fill=COLORS["muted"])
    count_y = iy1 + 720
    draw.text((ix1, count_y), "Rendered extract row counts", fill=COLORS["muted"], font=F["small"])
    row_counts = [
        ("orders_enriched", len(data["orders"])),
        ("order_items_enriched", len(data["items"])),
        ("daily_kpi", len(data["daily"])),
        ("inventory_monthly", len(data["inv"])),
        ("recommendations", len(data["rec"])),
        ("seasonality_indices", len(data["season"])),
    ]
    count_w = 585
    count_h = 86
    for i, (name, count) in enumerate(row_counts):
        x = ix1 + (i % 3) * (count_w + 70)
        y = count_y + 54 + (i // 3) * 112
        draw.rounded_rectangle([x, y, x + count_w, y + count_h], radius=14, fill=COLORS["soft_green"], outline=COLORS["grid"], width=2)
        draw.text((x + 22, y + 14), name, fill=COLORS["ink"], font=F["small"])
        draw.text((x + 22, y + 45), f"{count:,} rows", fill=COLORS["green"], font=F["label"])
    proof_x = ix1
    proof_y = iy2 - 210
    proof_cards = [
        ("13 CSVs", "sample_submission, baseline, sales_test excluded"),
        ("100% FK", "orders, payments, shipments, returns, reviews coverage"),
        ("0 VND gap", "sales.csv revenue reconciles to item-level revenue"),
        ("EDA only", "predictive signals use historical Part 2 data"),
    ]
    for i, (value, note) in enumerate(proof_cards):
        x = proof_x + i * 680
        card = (x, proof_y, x + 620, proof_y + 150)
        draw.rounded_rectangle(card, radius=18, fill=COLORS["panel"], outline=COLORS["grid"], width=3)
        draw.text((x + 26, proof_y + 24), value, fill=COLORS["green"], font=F["label"])
        draw_wrapped(draw, (x + 26, proof_y + 70), note, F["small"], COLORS["ink"], 568, max_lines=2)
        draw.text((x + 26, proof_y + 122), "validation guardrail", fill=COLORS["muted"], font=F["tiny"])


def kpi_value(kpi: pd.DataFrame, name: str) -> float:
    match = kpi.loc[kpi["kpi_name"].eq(name), "kpi_value"]
    return float(match.iloc[0]) if not match.empty else float("nan")


def load_data() -> dict[str, pd.DataFrame]:
    kpi = pd.read_csv(EXPORT_DIR / "dashboard_kpis.csv")
    daily = pd.read_csv(EXPORT_DIR / "daily_kpi.csv", parse_dates=["date"])
    forecast = pd.read_csv(EXPORT_DIR / "growth_forecast_monthly.csv", parse_dates=["date"])
    season = pd.read_csv(EXPORT_DIR / "seasonality_indices.csv")
    rec = pd.read_csv(EXPORT_DIR / "recommendations.csv")

    orders_cols = [
        "order_id",
        "order_date",
        "payment_method",
        "order_source",
        "device_type",
        "age_group",
        "ship_region",
        "dominant_category",
        "item_net_revenue",
        "item_margin",
        "total_discount",
        "is_cancelled",
        "has_return_record",
        "fulfillment_days",
        "top_return_reason",
        "review_count",
        "order_avg_rating",
    ]
    item_cols = [
        "category",
        "segment",
        "size",
        "line_net_revenue",
        "line_margin",
        "line_discount_rate",
        "has_promo",
        "returned_flag",
        "return_rate_units",
        "top_return_reason",
        "avg_rating",
    ]
    inv_cols = [
        "snapshot_date",
        "product_id",
        "product_name",
        "category",
        "segment",
        "stock_on_hand",
        "units_sold",
        "stockout_flag",
        "overstock_flag",
        "days_of_supply",
        "sell_through_rate",
        "stockout_pressure_score",
        "overstock_pressure_score",
    ]
    orders = pd.read_csv(EXPORT_DIR / "orders_enriched.csv", usecols=orders_cols, parse_dates=["order_date"])
    items = pd.read_csv(EXPORT_DIR / "order_items_enriched.csv", usecols=item_cols)
    inv = pd.read_csv(EXPORT_DIR / "inventory_monthly.csv", usecols=inv_cols, parse_dates=["snapshot_date"])
    return {"kpi": kpi, "daily": daily, "forecast": forecast, "season": season, "rec": rec, "orders": orders, "items": items, "inv": inv}


def aggregate_data(data: dict[str, pd.DataFrame]) -> dict[str, pd.DataFrame]:
    orders = data["orders"].copy()
    items = data["items"].copy()
    inv = data["inv"].copy()

    for col in ["item_net_revenue", "item_margin", "total_discount", "fulfillment_days", "order_avg_rating"]:
        orders[col] = pd.to_numeric(orders[col], errors="coerce")
    orders["is_cancelled_bool"] = bool_series(orders["is_cancelled"])
    orders["has_return_record_bool"] = bool_series(orders["has_return_record"])

    for col in ["line_net_revenue", "line_margin", "line_discount_rate", "return_rate_units", "avg_rating"]:
        items[col] = pd.to_numeric(items[col], errors="coerce")
    items["has_promo_bool"] = bool_series(items["has_promo"])
    items["returned_flag_bool"] = bool_series(items["returned_flag"])

    payment = (
        orders.groupby("payment_method", dropna=False)
        .agg(
            orders=("order_id", "count"),
            revenue=("item_net_revenue", "sum"),
            margin=("item_margin", "sum"),
            cancel_rate=("is_cancelled_bool", "mean"),
            return_rate=("has_return_record_bool", "mean"),
        )
        .reset_index()
    )
    payment["risk_rate"] = payment["cancel_rate"] + payment["return_rate"]
    payment["margin_pct"] = payment["margin"] / payment["revenue"].replace(0, np.nan)
    payment = payment.sort_values("risk_rate", ascending=False)

    channel = (
        orders.groupby("order_source", dropna=False)
        .agg(
            orders=("order_id", "count"),
            revenue=("item_net_revenue", "sum"),
            margin=("item_margin", "sum"),
            cancel_rate=("is_cancelled_bool", "mean"),
            return_rate=("has_return_record_bool", "mean"),
        )
        .reset_index()
    )
    channel["risk_rate"] = channel["cancel_rate"] + channel["return_rate"]
    channel["margin_pct"] = channel["margin"] / channel["revenue"].replace(0, np.nan)
    channel["revenue_per_order"] = channel["revenue"] / channel["orders"].replace(0, np.nan)
    channel = channel.sort_values("margin_pct")

    promo = (
        items.groupby(["category", "segment", "has_promo_bool"], dropna=False)
        .agg(revenue=("line_net_revenue", "sum"), margin=("line_margin", "sum"), rows=("line_net_revenue", "count"))
        .reset_index()
    )
    promo["margin_pct"] = promo["margin"] / promo["revenue"].replace(0, np.nan)
    promo_wide = promo.pivot_table(
        index=["category", "segment"],
        columns="has_promo_bool",
        values=["margin_pct", "revenue"],
        aggfunc="first",
    )
    promo_wide.columns = [f"{metric}_{'promo' if flag else 'no_promo'}" for metric, flag in promo_wide.columns]
    promo_wide = promo_wide.reset_index().fillna(0)
    if "margin_pct_no_promo" not in promo_wide:
        promo_wide["margin_pct_no_promo"] = 0
    if "margin_pct_promo" not in promo_wide:
        promo_wide["margin_pct_promo"] = 0
    if "revenue_promo" not in promo_wide:
        promo_wide["revenue_promo"] = 0
    promo_wide["leakage_pp"] = promo_wide["margin_pct_no_promo"] - promo_wide["margin_pct_promo"]
    promo_wide["entity"] = promo_wide["category"].astype(str) + " / " + promo_wide["segment"].astype(str)
    promo_wide = promo_wide.sort_values("leakage_pp", ascending=False)

    returns_reason = (
        orders.loc[orders["has_return_record_bool"]]
        .groupby("top_return_reason", dropna=True)
        .agg(orders=("order_id", "count"), revenue=("item_net_revenue", "sum"))
        .reset_index()
        .sort_values("orders", ascending=False)
    )
    returns_reason["top_return_reason"] = returns_reason["top_return_reason"].map(clean_text)

    fulfillment = orders.copy()
    fulfillment["fulfillment_bucket"] = pd.cut(
        fulfillment["fulfillment_days"],
        bins=[-1, 3, 5, 7, 10, 999],
        labels=["0-3 days", "4-5 days", "6-7 days", "8-10 days", "11+ days"],
    )
    fulfillment = (
        fulfillment.groupby("fulfillment_bucket", observed=False)
        .agg(orders=("order_id", "count"), return_rate=("has_return_record_bool", "mean"), cancel_rate=("is_cancelled_bool", "mean"))
        .reset_index()
    )

    size_return = (
        items.groupby(["category", "size"], dropna=False)
        .agg(lines=("line_net_revenue", "count"), returned=("returned_flag_bool", "mean"), revenue=("line_net_revenue", "sum"))
        .reset_index()
    )
    size_return = size_return[size_return["lines"] >= 100].sort_values("returned", ascending=False)
    size_return["entity"] = size_return["category"].astype(str) + " / size " + size_return["size"].astype(str)

    inv["stockout_pressure_score"] = pd.to_numeric(inv["stockout_pressure_score"], errors="coerce").fillna(0)
    inv["overstock_pressure_score"] = pd.to_numeric(inv["overstock_pressure_score"], errors="coerce").fillna(0)
    inv["stockout_flag"] = pd.to_numeric(inv["stockout_flag"], errors="coerce").fillna(0)
    inv["overstock_flag"] = pd.to_numeric(inv["overstock_flag"], errors="coerce").fillna(0)
    max_date = inv["snapshot_date"].max()
    recent = inv[inv["snapshot_date"] >= max_date - pd.DateOffset(months=6)]
    inv_prod = (
        recent.groupby(["product_id", "product_name", "category", "segment"], dropna=False)
        .agg(
            stockout_pressure_score=("stockout_pressure_score", "mean"),
            overstock_pressure_score=("overstock_pressure_score", "mean"),
            days_of_supply=("days_of_supply", "mean"),
            units_sold=("units_sold", "sum"),
        )
        .reset_index()
    )
    inv_category = (
        recent.groupby("category", dropna=False)
        .agg(stockout_share=("stockout_flag", "mean"), overstock_share=("overstock_flag", "mean"), rows=("product_id", "count"))
        .reset_index()
        .sort_values("stockout_share", ascending=False)
    )

    return {
        "payment": payment,
        "channel": channel,
        "promo": promo_wide,
        "returns_reason": returns_reason,
        "fulfillment": fulfillment,
        "size_return": size_return,
        "inv_prod": inv_prod,
        "inv_category": inv_category,
    }


def render_executive(data: dict[str, pd.DataFrame], agg: dict[str, pd.DataFrame]) -> Image.Image:
    img, draw = new_canvas("01 Executive scorecard", "CEO-level view of growth, margin, risk, and action urgency")
    kpi = data["kpi"]
    cards = [
        ("Revenue", fmt_money(kpi_value(kpi, "Revenue")), "Official sales.csv total; reconciled to item grain.", COLORS["green"]),
        ("Gross margin", fmt_pct(kpi_value(kpi, "Gross margin %")), "Margin is positive but thin for a fashion marketplace.", COLORS["teal"]),
        ("COD risk", fmt_pct(kpi_value(kpi, "COD risk rate")), "Cancellation plus return pressure in COD workflow.", COLORS["red"]),
        ("Promo gap", f"{fmt_pct(kpi_value(kpi, 'Promo margin %'))} vs {fmt_pct(kpi_value(kpi, 'No-promo margin %'))}", "Promotions protect volume but can destroy margin.", COLORS["orange"]),
    ]
    for i, card in enumerate(cards):
        x = MARGIN + i * 760
        kpi_card(draw, (x, 205, x + 700, 400), *card)

    daily = data["daily"].tail(1095).copy()
    labels = pd.to_datetime(daily["date"]).dt.strftime("%Y-%m").tolist()
    draw_line_chart(
        draw,
        (MARGIN, 455, 1960, 1190),
        "Last three years: rolling revenue and margin",
        labels,
        [
            ("30-day revenue", daily["sales_revenue_rolling_30d"].tolist(), COLORS["green"]),
            ("30-day margin", daily["sales_margin_rolling_30d"].tolist(), COLORS["teal"]),
        ],
        fmt_plain_money,
    )
    risks = [
        ("Cancel rate", kpi_value(kpi, "Cancel rate")),
        ("Return-record rate", kpi_value(kpi, "Return-record rate")),
        ("COD risk rate", kpi_value(kpi, "COD risk rate")),
        ("Inventory stockout share", kpi_value(kpi, "Inventory stockout share")),
        ("Inventory overstock share", kpi_value(kpi, "Inventory overstock share")),
    ]
    draw_horizontal_bars(draw, (2025, 455, W - MARGIN, 1190), "Risk signals that require management action", risks, fmt_pct, COLORS["red"], max_rows=5)
    rec = data["rec"].sort_values(["priority", "risk_score"], ascending=[True, False])
    draw_recommendation_table(draw, (MARGIN, 1245, W - MARGIN, H - 92), "Highest-value action queue", rec, max_rows=4)
    return img


def render_predictive(data: dict[str, pd.DataFrame]) -> Image.Image:
    img, draw = new_canvas("02 Predictive growth and seasonality", "Historical EDA forecast, likely peak months, and planning lead indicators")
    forecast = data["forecast"]
    season = data["season"]
    draw_forecast_chart(draw, (MARGIN, 205, 2105, 1165), forecast)
    month = season[season["grain"].eq("month_of_year")].copy()
    month = month.sort_values("seasonality_index", ascending=False)
    weekday = season[season["grain"].eq("weekday")].copy().sort_values("period_number")
    draw_horizontal_bars(
        draw,
        (2170, 205, W - MARGIN, 910),
        "Likely peak and soft months",
        list(zip(month["period_name"], month["seasonality_index"])),
        lambda v: f"{v:.2f}x",
        COLORS["purple"],
        max_rows=12,
    )
    draw_horizontal_bars(
        draw,
        (2170, 955, W - MARGIN, 1450),
        "Weekday demand index",
        list(zip(weekday["period_name"], weekday["seasonality_index"])),
        lambda v: f"{v:.2f}x",
        COLORS["blue"],
        max_rows=7,
    )
    future = forecast[bool_series(forecast["is_forecast"])].copy()
    peak = month.iloc[0]
    cards = [
        ("Next forecast high", fmt_money(future["forecast_revenue"].max()), "Use as demand-planning pressure, not Kaggle forecast.", COLORS["blue"]),
        ("Peak month", f"{peak['period_name']} {float(peak['seasonality_index']):.2f}x", "Replenish before peak demand windows.", COLORS["purple"]),
        ("Softest month", f"{month.iloc[-1]['period_name']} {float(month.iloc[-1]['seasonality_index']):.2f}x", "Use markdowns and working-capital cleanup.", COLORS["orange"]),
    ]
    for i, card in enumerate(cards):
        x = MARGIN + i * 980
        kpi_card(draw, (x, 1490, x + 905, H - 92), *card)
    return img


def render_profit_promo(data: dict[str, pd.DataFrame], agg: dict[str, pd.DataFrame]) -> Image.Image:
    img, draw = new_canvas("03 Profit and promotion leakage", "Diagnostic view of where revenue growth stops converting into gross margin")
    kpi = data["kpi"]
    promo = agg["promo"].head(9)
    margin_rows = [(row["entity"], row["margin_pct_promo"], row["margin_pct_no_promo"]) for _, row in promo.iterrows()]
    draw_grouped_bars(
        draw,
        (MARGIN, 205, 1845, 1050),
        "Promo margin vs non-promo margin by category / segment",
        margin_rows,
        ("Promo margin", "No-promo margin"),
    )
    leakage_rows = list(zip(promo["entity"], promo["leakage_pp"]))
    draw_horizontal_bars(
        draw,
        (1910, 205, W - MARGIN, 1050),
        "Margin leakage opportunity",
        leakage_rows,
        lambda v: f"{v * 100:.1f} pp",
        COLORS["orange"],
        max_rows=9,
    )
    cards = [
        ("Promoted margin", fmt_pct(kpi_value(kpi, "Promo margin %")), "Low margin means discounts need SKU and threshold controls.", COLORS["red"]),
        ("Non-promo margin", fmt_pct(kpi_value(kpi, "No-promo margin %")), "Baseline proves the business can sell with healthier margin.", COLORS["green"]),
        ("Primary action", "Tighten discount depth", "Exclude low-margin SKUs and require minimum order value.", COLORS["orange"]),
    ]
    for i, card in enumerate(cards):
        x = MARGIN + i * 980
        kpi_card(draw, (x, 1115, x + 905, 1348), *card)
    rec = data["rec"][data["rec"]["signal_type"].eq("Promotion margin risk")]
    draw_recommendation_table(draw, (MARGIN, 1395, W - MARGIN, H - 92), "Recommended pricing controls", rec, max_rows=3)
    return img


def render_payment_channel(data: dict[str, pd.DataFrame], agg: dict[str, pd.DataFrame]) -> Image.Image:
    img, draw = new_canvas("04 Customer, channel, and payment risk", "Revenue quality depends on payment workflow and channel mix, not only order volume")
    payment = agg["payment"]
    channel = agg["channel"]
    draw_horizontal_bars(
        draw,
        (MARGIN, 205, 1520, 970),
        "Payment-method risk rate",
        list(zip(payment["payment_method"], payment["risk_rate"])),
        fmt_pct,
        COLORS["red"],
        max_rows=8,
    )
    draw_grouped_bars(
        draw,
        (1585, 205, W - MARGIN, 970),
        "Channel margin and risk",
        [(row["order_source"], row["risk_rate"], row["margin_pct"]) for _, row in channel.iterrows()],
        ("Risk rate", "Margin %"),
        fmt_pct,
        colors=(COLORS["red"], COLORS["green"]),
    )
    rec = data["rec"][data["rec"]["signal_type"].isin(["Payment risk", "Channel quality risk"])]
    draw_recommendation_table(draw, (MARGIN, 1035, W - MARGIN, 1460), "Controls and budget-shift recommendations", rec, max_rows=5)
    cod = payment[payment["payment_method"].astype(str).str.lower().eq("cod")]
    cod_risk = float(cod["risk_rate"].iloc[0]) if not cod.empty else np.nan
    cards = [
        ("COD workflow", fmt_pct(cod_risk), "Treat as higher-risk demand: verify, incentivize prepaid, and monitor refunds.", COLORS["red"]),
        ("Quality metric", "Margin + risk", "Do not rank channels by sessions or order volume alone.", COLORS["blue"]),
        ("CEO decision", "Spend shift", "Move budget toward channels with stronger revenue quality.", COLORS["green"]),
    ]
    for i, card in enumerate(cards):
        x = MARGIN + i * 980
        kpi_card(draw, (x, 1500, x + 905, H - 92), *card)
    return img


def render_returns(data: dict[str, pd.DataFrame], agg: dict[str, pd.DataFrame]) -> Image.Image:
    img, draw = new_canvas("05 Returns, reviews, and fulfillment", "Customer-experience leakage concentrates in return reasons, size fit, and service timing")
    reasons = agg["returns_reason"].head(8)
    draw_horizontal_bars(
        draw,
        (MARGIN, 205, 1485, 980),
        "Top return reasons by returned orders",
        list(zip(reasons["top_return_reason"], reasons["orders"])),
        fmt_num,
        COLORS["red"],
        max_rows=8,
    )
    size_return = agg["size_return"].head(8)
    draw_horizontal_bars(
        draw,
        (1550, 205, W - MARGIN, 980),
        "Category / size return pressure",
        list(zip(size_return["entity"], size_return["returned"])),
        fmt_pct,
        COLORS["orange"],
        max_rows=8,
    )
    fulfillment = agg["fulfillment"]
    labels = fulfillment["fulfillment_bucket"].astype(str).tolist()
    draw_line_chart(
        draw,
        (MARGIN, 1045, 2040, H - 92),
        "Fulfillment timing vs return / cancellation rate",
        labels,
        [
            ("Return rate", fulfillment["return_rate"].tolist(), COLORS["red"]),
            ("Cancel rate", fulfillment["cancel_rate"].tolist(), COLORS["orange"]),
        ],
        lambda v: fmt_pct(v),
        y_floor_zero=True,
    )
    rec = data["rec"][data["rec"]["signal_type"].eq("Wrong-size return risk")]
    draw_recommendation_table(draw, (2105, 1045, W - MARGIN, H - 92), "CX interventions", rec, max_rows=5)
    return img


def render_inventory(data: dict[str, pd.DataFrame], agg: dict[str, pd.DataFrame]) -> Image.Image:
    img, draw = new_canvas("06 Inventory quadrant actions", "Stockout and overstock can coexist; the action must depend on product-level risk")
    inv_prod = agg["inv_prod"]
    draw_scatter_inventory(draw, (MARGIN, 205, 1970, 1305), inv_prod)
    inv_cat = agg["inv_category"].head(8)
    draw_grouped_bars(
        draw,
        (2035, 205, W - MARGIN, 950),
        "Category stockout / overstock share",
        [(row["category"], row["stockout_share"], row["overstock_share"]) for _, row in inv_cat.iterrows()],
        ("Stockout", "Overstock"),
        fmt_pct,
        colors=(COLORS["red"], COLORS["purple"]),
    )
    rec = data["rec"][data["rec"]["signal_type"].isin(["Stockout risk", "Overstock risk"])]
    draw_recommendation_table(draw, (2035, 1005, W - MARGIN, H - 92), "Supply-chain action list", rec, max_rows=7)
    cards = [
        ("Stockout share", fmt_pct(kpi_value(data["kpi"], "Inventory stockout share")), "Lost demand risk in product-month rows.", COLORS["red"]),
        ("Overstock share", fmt_pct(kpi_value(data["kpi"], "Inventory overstock share")), "Working capital tied up in slow movers.", COLORS["purple"]),
    ]
    for i, card in enumerate(cards):
        x = MARGIN + i * 905
        kpi_card(draw, (x, 1365, x + 840, H - 92), *card)
    return img


def render_model_validation(data: dict[str, pd.DataFrame]) -> Image.Image:
    img, draw = new_canvas("07 Data model and validation", "Proof that the analysis uses the required Part 2 business data and reconciles core totals")
    draw_validation_erd(draw, (MARGIN, 205, W - MARGIN, H - 92), data)
    return img


def render_action_roadmap(data: dict[str, pd.DataFrame]) -> Image.Image:
    img, draw = new_canvas("08 Prescriptive roadmap", "CEO-ready action plan tied directly to descriptive, diagnostic, and predictive signals")
    rec = data["rec"].copy()
    rec["impact"] = pd.to_numeric(rec["estimated_impact_vnd"], errors="coerce").fillna(0)
    rec["risk_score"] = pd.to_numeric(rec["risk_score"], errors="coerce").fillna(0)
    rec = rec.sort_values(["priority", "risk_score"], ascending=[True, False])
    sections = [
        ("Protect margin", "Promotion margin risk", COLORS["orange"]),
        ("Reduce failed demand", "Payment risk", COLORS["red"]),
        ("Fix customer leakage", "Wrong-size return risk", COLORS["purple"]),
        ("Balance inventory", "Stockout risk", COLORS["blue"]),
        ("Release capital", "Overstock risk", COLORS["teal"]),
        ("Shift spend", "Channel quality risk", COLORS["green"]),
    ]
    card_w = 965
    card_h = 405
    for i, (title, signal, color) in enumerate(sections):
        x = MARGIN + (i % 3) * (card_w + 60)
        y = 225 + (i // 3) * (card_h + 72)
        draw.rounded_rectangle([x, y, x + card_w, y + card_h], radius=18, fill=COLORS["panel"], outline=COLORS["grid"], width=3)
        draw.rounded_rectangle([x, y, x + card_w, y + 78], radius=18, fill=color)
        draw.text((x + 28, y + 21), title, fill="white", font=F["section"])
        sub = rec[rec["signal_type"].eq(signal)].head(2)
        if sub.empty:
            draw.text((x + 28, y + 118), "No recommendation generated.", fill=COLORS["muted"], font=F["body"])
            continue
        yy = y + 112
        for _, row in sub.iterrows():
            entity = clean_text(row.get("entity", ""))
            action = clean_text(row.get("recommended_action", ""))
            risk = float(row.get("risk_score", 0))
            impact = float(row.get("impact", 0))
            draw.text((x + 28, yy), entity[:42], fill=COLORS["ink"], font=F["label"])
            draw.text((x + card_w - 190, yy), f"Risk {risk:.1f}", fill=color, font=F["small"])
            yy = draw_wrapped(draw, (x + 28, yy + 42), action, F["small"], COLORS["muted"], card_w - 56, max_lines=2)
            if impact > 0:
                draw.text((x + 28, yy + 8), f"Estimated impact: {fmt_money(impact)}", fill=COLORS["green"], font=F["tiny"])
                yy += 42
            draw.line([x + 28, yy + 8, x + card_w - 28, yy + 8], fill="#edf0ea", width=2)
            yy += 34
    bottom = (MARGIN, 1540, W - MARGIN, H - 92)
    ix1, iy1, ix2, iy2 = rounded_panel(draw, bottom, "Storytelling thesis for the written answer")
    thesis = (
        "The business has real demand but needs CEO action on revenue quality: forecasted peak months increase the cost of "
        "stockouts, promotion leakage weakens margin, COD creates failed-demand risk, wrong-size returns damage customer "
        "experience, and slow movers tie up capital. The recommendation is to protect margin, shift spend by revenue quality, "
        "prepay-incentivize risky payment flows, fix sizing, and rebalance replenishment before the seasonal peak."
    )
    draw_wrapped(draw, (ix1, iy1 + 8), thesis, F["body"], COLORS["ink"], ix2 - ix1, max_lines=4)
    return img


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def save_pdf(paths: list[Path]) -> None:
    page_w = W / DPI * inch
    page_h = H / DPI * inch
    c = canvas.Canvas(str(PDF_PATH), pagesize=(page_w, page_h))
    for path in paths:
        c.drawImage(str(path), 0, 0, width=page_w, height=page_h)
        c.showPage()
    c.save()


def write_latex_snippets(paths: list[Path]) -> None:
    captions = {
        "01_executive_scorecard.png": "Executive scorecard: growth, margin, risk, and recommended actions.",
        "02_predictive_growth_seasonality.png": "Predictive EDA: trend forecast and seasonal demand signals.",
        "03_profit_promotion_leakage.png": "Diagnostic EDA: promotion margin leakage by category and segment.",
        "04_payment_channel_risk.png": "Payment and channel risk: revenue quality by workflow and source.",
        "05_returns_fulfillment_cx.png": "Returns, reviews, and fulfillment: customer-experience leakage.",
        "06_inventory_quadrant_actions.png": "Inventory action quadrant: stockout and overstock pressure.",
        "07_data_model_validation.png": "Data model and validation proof for the Part 2 analysis.",
        "08_prescriptive_action_roadmap.png": "Prescriptive roadmap connecting insights to CEO actions.",
    }
    lines = [
        "% Generated by scripts/generate_latex_figure_pack.py",
        "% Paths are relative to this figure directory.",
        "",
    ]
    for path in paths:
        label = path.stem.replace("_", "-")
        caption = captions.get(path.name, path.stem)
        lines.extend(
            [
                "\\begin{figure}[H]",
                "    \\centering",
                f"    \\includegraphics[width=0.98\\textwidth]{{{path.name}}}",
                f"    \\caption{{{caption}}}",
                f"    \\label{{fig:{label}}}",
                "\\end{figure}",
                "",
            ]
        )
    LATEX_SNIPPET_PATH.write_text("\n".join(lines), encoding="utf-8")


def build_zip(paths: list[Path]) -> None:
    with zipfile.ZipFile(ZIP_PATH, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for path in paths + [PDF_PATH, MANIFEST_PATH, LATEX_SNIPPET_PATH]:
            zf.write(path, path.relative_to(FIGURE_DIR))


def write_manifest(paths: list[Path]) -> None:
    files = []
    for path in paths + [PDF_PATH, LATEX_SNIPPET_PATH]:
        stat = path.stat()
        item = {
            "file": path.name,
            "bytes": stat.st_size,
            "sha256": sha256(path),
        }
        if path.suffix.lower() == ".png":
            with Image.open(path) as img:
                item.update({"width": img.width, "height": img.height, "dpi": img.info.get("dpi")})
        files.append(item)
    manifest = {
        "project": "vindatathon-2026-task2-tableau",
        "deliverable": "LaTeX-ready fully rendered figure pack",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "rendering_engine": "Python + Pillow + ReportLab",
        "figure_size_px": [W, H],
        "dpi": DPI,
        "source_extract_dir": str(EXPORT_DIR),
        "source_files": [
            "dashboard_kpis.csv",
            "daily_kpi.csv",
            "growth_forecast_monthly.csv",
            "seasonality_indices.csv",
            "recommendations.csv",
            "orders_enriched.csv",
            "order_items_enriched.csv",
            "inventory_monthly.csv",
        ],
        "guardrails": [
            "Part 2 historical data only",
            "No sales_test.csv",
            "No sample_submission.csv",
            "No baseline.ipynb",
            "Predictive charts are EDA signals, not Kaggle submission forecasts",
        ],
        "files": files,
    }
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2), encoding="utf-8")


def main() -> None:
    FIGURE_DIR.mkdir(parents=True, exist_ok=True)
    data = load_data()
    agg = aggregate_data(data)
    figures = [
        ("01_executive_scorecard.png", render_executive(data, agg)),
        ("02_predictive_growth_seasonality.png", render_predictive(data)),
        ("03_profit_promotion_leakage.png", render_profit_promo(data, agg)),
        ("04_payment_channel_risk.png", render_payment_channel(data, agg)),
        ("05_returns_fulfillment_cx.png", render_returns(data, agg)),
        ("06_inventory_quadrant_actions.png", render_inventory(data, agg)),
        ("07_data_model_validation.png", render_model_validation(data)),
        ("08_prescriptive_action_roadmap.png", render_action_roadmap(data)),
    ]
    paths: list[Path] = []
    for filename, image in figures:
        path = FIGURE_DIR / filename
        image.save(path, "PNG", dpi=(DPI, DPI), optimize=True)
        paths.append(path)
    save_pdf(paths)
    write_latex_snippets(paths)
    write_manifest(paths)
    build_zip(paths)
    for path in paths + [PDF_PATH, MANIFEST_PATH, LATEX_SNIPPET_PATH, ZIP_PATH]:
        print(path.relative_to(PROJECT_DIR))


if __name__ == "__main__":
    main()

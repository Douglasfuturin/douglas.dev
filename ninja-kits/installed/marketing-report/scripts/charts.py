"""
charts.py — inline SVG chart primitives for the marketing-report skill.

All functions return an SVG string ready to be embedded into the HTML template.
No JS required at view time; charts are rendered fully server-side.

Design tokens come from visual-design.md and are duplicated here as constants so
the module is self-contained.
"""

from __future__ import annotations
from typing import Iterable, Sequence
from html import escape

BRAND = "#ff8c42"
BRAND_FAINT = "rgba(255, 140, 66, 0.08)"
GRID = "rgba(255, 255, 255, 0.04)"
AXIS = "rgba(255, 255, 255, 0.2)"
TEXT_DIM = "#5a5a5a"
TEXT_MUTED = "#8a8a8a"
TEXT = "#ededed"
SURFACE_2 = "#1a1a1a"
UP = "#4ade80"
DOWN = "#f87171"
NEUTRALS = ("#94a3b8", "#64748b", "#475569", "#334155")


def _safe_id(prefix: str) -> str:
    """Stable-ish unique-enough id for SVG defs."""
    import os, binascii
    return f"{prefix}-{binascii.hexlify(os.urandom(4)).decode()}"


def _scale(values: Sequence[float], lo: float, hi: float, out_lo: float, out_hi: float) -> list[float]:
    if hi == lo:
        return [(out_lo + out_hi) / 2] * len(values)
    return [out_lo + (v - lo) * (out_hi - out_lo) / (hi - lo) for v in values]


def sparkline(values: Sequence[float], width: int = 200, height: int = 32, stroke: str = BRAND) -> str:
    """Tiny inline sparkline for KPI tiles. No axes, no labels."""
    if not values:
        return f'<svg width="{width}" height="{height}" viewBox="0 0 {width} {height}"></svg>'
    if len(values) == 1:
        values = [values[0], values[0]]

    pad = 2
    lo, hi = min(values), max(values)
    xs = _scale(list(range(len(values))), 0, len(values) - 1, pad, width - pad)
    ys = _scale(values, lo, hi, height - pad, pad)

    path = "M " + " L ".join(f"{x:.2f} {y:.2f}" for x, y in zip(xs, ys))
    area = path + f" L {xs[-1]:.2f} {height - pad} L {xs[0]:.2f} {height - pad} Z"

    gid = _safe_id("spark")
    return f'''<svg width="{width}" height="{height}" viewBox="0 0 {width} {height}" xmlns="http://www.w3.org/2000/svg" preserveAspectRatio="none">
  <defs><linearGradient id="{gid}" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="{stroke}" stop-opacity="0.18"/>
    <stop offset="1" stop-color="{stroke}" stop-opacity="0"/>
  </linearGradient></defs>
  <path d="{area}" fill="url(#{gid})"/>
  <path d="{path}" fill="none" stroke="{stroke}" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
  <circle cx="{xs[-1]:.2f}" cy="{ys[-1]:.2f}" r="2.5" fill="{stroke}"/>
</svg>'''


def line_chart(series: list[dict], x_labels: list[str], width: int = 1000, height: int = 280,
               y_format: str = "{:,.0f}", title: str | None = None) -> str:
    """
    Larger trend line chart. series = [{name, values, color?}, ...] (up to 4).
    Primary series (index 0) gets the brand color + area fill below.
    """
    if not series or not series[0].get("values"):
        return f'<svg width="{width}" height="{height}" viewBox="0 0 {width} {height}"></svg>'

    pad_l, pad_r, pad_t, pad_b = 56, 16, 16, 36

    all_vals: list[float] = []
    for s in series:
        all_vals.extend(s["values"])
    lo, hi = min(all_vals), max(all_vals)
    # Pad y range so the top line isn't flush against the top edge.
    span = (hi - lo) or hi or 1
    lo, hi = lo - span * 0.08, hi + span * 0.12

    n = len(series[0]["values"])
    xs = _scale(list(range(n)), 0, max(n - 1, 1), pad_l, width - pad_r)

    # Y gridlines (4 ticks)
    grid_lines = []
    y_ticks_count = 4
    for i in range(y_ticks_count + 1):
        frac = i / y_ticks_count
        y = pad_t + (height - pad_t - pad_b) * frac
        val = hi - (hi - lo) * frac
        grid_lines.append(
            f'<line x1="{pad_l}" y1="{y:.1f}" x2="{width - pad_r}" y2="{y:.1f}" stroke="{GRID}" stroke-width="1"/>'
            f'<text x="{pad_l - 8}" y="{y + 4:.1f}" font-family="JetBrains Mono, monospace" font-size="11" fill="{TEXT_DIM}" text-anchor="end">{y_format.format(val)}</text>'
        )

    # X-axis labels — show only ~5-7 across to avoid crowding
    every = max(1, n // 6)
    x_label_els = []
    for i, lab in enumerate(x_labels):
        if i % every == 0 or i == n - 1:
            x_label_els.append(
                f'<text x="{xs[i]:.1f}" y="{height - 14}" font-family="JetBrains Mono, monospace" font-size="11" fill="{TEXT_DIM}" text-anchor="middle">{escape(str(lab))}</text>'
            )

    series_paths = []
    series_areas = []
    palette = [BRAND, *NEUTRALS]
    for idx, s in enumerate(series):
        color = s.get("color") or palette[idx % len(palette)]
        ys = _scale(s["values"], lo, hi, height - pad_b, pad_t)
        path = "M " + " L ".join(f"{x:.2f} {y:.2f}" for x, y in zip(xs, ys))
        series_paths.append(
            f'<path d="{path}" fill="none" stroke="{color}" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round"/>'
        )
        if idx == 0:
            gid = _safe_id("area")
            area = path + f" L {xs[-1]:.2f} {height - pad_b} L {xs[0]:.2f} {height - pad_b} Z"
            series_areas.append(
                f'<defs><linearGradient id="{gid}" x1="0" y1="0" x2="0" y2="1">'
                f'<stop offset="0" stop-color="{color}" stop-opacity="0.18"/>'
                f'<stop offset="1" stop-color="{color}" stop-opacity="0"/>'
                f'</linearGradient></defs>'
                f'<path d="{area}" fill="url(#{gid})"/>'
            )

    title_el = ""
    if title:
        title_el = f'<text x="{pad_l}" y="14" font-family="Plus Jakarta Sans, system-ui, sans-serif" font-size="12" fill="{TEXT_MUTED}" font-weight="600">{escape(title)}</text>'

    return f'''<svg width="100%" viewBox="0 0 {width} {height}" xmlns="http://www.w3.org/2000/svg" role="img">
  {title_el}
  {''.join(grid_lines)}
  {''.join(series_areas)}
  {''.join(series_paths)}
  {''.join(x_label_els)}
</svg>'''


def bar_chart(labels: list[str], values: list[float], compare: list[float] | None = None,
              width: int = 1000, height: int = 280, y_format: str = "{:,.0f}",
              show_value_labels: bool = True) -> str:
    """Horizontal bar chart for channel/source comparisons."""
    if not values:
        return f'<svg width="{width}" height="{height}" viewBox="0 0 {width} {height}"></svg>'

    pad_l, pad_r, pad_t, pad_b = 16, 16, 16, 40

    all_vals = list(values) + (list(compare) if compare else [])
    hi = max(all_vals) * 1.18
    lo = 0

    n = len(values)
    band = (width - pad_l - pad_r) / n
    bar_w = band * 0.42 if compare else band * 0.6

    grid_lines = []
    for i in range(5):
        frac = i / 4
        y = pad_t + (height - pad_t - pad_b) * frac
        val = hi - (hi - lo) * frac
        grid_lines.append(
            f'<line x1="{pad_l}" y1="{y:.1f}" x2="{width - pad_r}" y2="{y:.1f}" stroke="{GRID}" stroke-width="1"/>'
        )

    bars = []
    value_labels = []
    x_labels = []
    base_y = height - pad_b

    for i, v in enumerate(values):
        center = pad_l + band * (i + 0.5)
        # primary bar
        bx = center - (bar_w + (band * 0.06 if compare else 0)) if compare else center - bar_w / 2
        bh = (v - lo) / (hi - lo) * (height - pad_t - pad_b) if hi > lo else 0
        bars.append(
            f'<rect x="{bx:.1f}" y="{base_y - bh:.1f}" width="{bar_w:.1f}" height="{bh:.1f}" fill="{BRAND}" rx="3" ry="3"/>'
        )
        if show_value_labels:
            value_labels.append(
                f'<text x="{(bx + bar_w/2):.1f}" y="{base_y - bh - 8:.1f}" font-family="JetBrains Mono, monospace" font-size="11" fill="{TEXT}" text-anchor="middle">{y_format.format(v)}</text>'
            )

        # compare bar
        if compare:
            cx = center + band * 0.06
            cv = compare[i]
            ch = (cv - lo) / (hi - lo) * (height - pad_t - pad_b) if hi > lo else 0
            bars.append(
                f'<rect x="{cx:.1f}" y="{base_y - ch:.1f}" width="{bar_w:.1f}" height="{ch:.1f}" fill="{NEUTRALS[1]}" rx="3" ry="3"/>'
            )

        x_labels.append(
            f'<text x="{center:.1f}" y="{base_y + 22:.1f}" font-family="Plus Jakarta Sans, system-ui, sans-serif" font-size="12" fill="{TEXT_MUTED}" text-anchor="middle">{escape(str(labels[i]))}</text>'
        )

    return f'''<svg width="100%" viewBox="0 0 {width} {height}" xmlns="http://www.w3.org/2000/svg" role="img">
  {''.join(grid_lines)}
  {''.join(bars)}
  {''.join(value_labels)}
  {''.join(x_labels)}
</svg>'''


def donut(slices: list[dict], size: int = 240, label: str | None = None,
          sublabel: str | None = None) -> str:
    """slices = [{name, value, color?}]. Renders a donut + center label."""
    if not slices:
        return f'<svg width="{size}" height="{size}"></svg>'

    total = sum(s["value"] for s in slices) or 1
    cx = cy = size / 2
    r_outer = size * 0.42
    r_inner = r_outer * 0.62

    palette = [BRAND, *NEUTRALS]
    paths = []
    angle = -90.0  # start at top
    for i, s in enumerate(slices):
        frac = s["value"] / total
        sweep = frac * 360
        a0 = angle
        a1 = angle + sweep
        angle = a1

        import math
        def pt(r, a_deg):
            a = math.radians(a_deg)
            return cx + r * math.cos(a), cy + r * math.sin(a)

        large = 1 if sweep > 180 else 0
        x0o, y0o = pt(r_outer, a0)
        x1o, y1o = pt(r_outer, a1)
        x0i, y0i = pt(r_inner, a0)
        x1i, y1i = pt(r_inner, a1)

        color = s.get("color") or palette[i % len(palette)]
        d = (f"M {x0o:.2f} {y0o:.2f} A {r_outer:.2f} {r_outer:.2f} 0 {large} 1 {x1o:.2f} {y1o:.2f} "
             f"L {x1i:.2f} {y1i:.2f} A {r_inner:.2f} {r_inner:.2f} 0 {large} 0 {x0i:.2f} {y0i:.2f} Z")
        paths.append(f'<path d="{d}" fill="{color}"/>')

    label_el = ""
    if label:
        label_el = f'<text x="{cx}" y="{cy - 4}" font-family="JetBrains Mono, monospace" font-size="22" font-weight="700" fill="{TEXT}" text-anchor="middle">{escape(label)}</text>'
    if sublabel:
        label_el += f'<text x="{cx}" y="{cy + 18}" font-family="Plus Jakarta Sans, system-ui, sans-serif" font-size="11" fill="{TEXT_MUTED}" text-anchor="middle">{escape(sublabel)}</text>'

    return f'''<svg width="{size}" height="{size}" viewBox="0 0 {size} {size}" xmlns="http://www.w3.org/2000/svg" role="img">
  {''.join(paths)}
  {label_el}
</svg>'''


def heatmap(grid: list[list[float]], row_labels: list[str], col_labels: list[str],
            width: int = 1000, height: int = 240) -> str:
    """7×24-ish heatmap. grid[row][col] = value (0..max)."""
    if not grid or not grid[0]:
        return f'<svg width="{width}" height="{height}" viewBox="0 0 {width} {height}"></svg>'

    pad_l, pad_r, pad_t, pad_b = 56, 16, 24, 28
    rows, cols = len(grid), len(grid[0])
    cell_w = (width - pad_l - pad_r) / cols
    cell_h = (height - pad_t - pad_b) / rows

    flat = [v for row in grid for v in row]
    max_v = max(flat) if flat else 1

    cells = []
    for r in range(rows):
        for c in range(cols):
            v = grid[r][c]
            t = v / max_v if max_v else 0
            # Lerp from surface-2 -> brand
            # Surface-2 is #1a1a1a; brand is BRAND. We blend in linear sRGB-ish.
            from_rgb = (0x1a, 0x1a, 0x1a)
            to_rgb = (0xff, 0x8c, 0x42)
            blend = tuple(int(from_rgb[i] + (to_rgb[i] - from_rgb[i]) * t) for i in range(3))
            fill = f"rgb({blend[0]},{blend[1]},{blend[2]})"
            x = pad_l + c * cell_w
            y = pad_t + r * cell_h
            cells.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{cell_w - 1.5:.1f}" height="{cell_h - 1.5:.1f}" fill="{fill}" rx="2"/>')

    row_label_els = []
    for r, lab in enumerate(row_labels):
        y = pad_t + cell_h * (r + 0.6)
        row_label_els.append(
            f'<text x="{pad_l - 8:.1f}" y="{y:.1f}" font-family="JetBrains Mono, monospace" font-size="11" fill="{TEXT_DIM}" text-anchor="end">{escape(lab)}</text>'
        )

    col_label_els = []
    every = max(1, cols // 8)
    for c, lab in enumerate(col_labels):
        if c % every == 0 or c == cols - 1:
            x = pad_l + cell_w * (c + 0.5)
            col_label_els.append(
                f'<text x="{x:.1f}" y="{height - 12:.1f}" font-family="JetBrains Mono, monospace" font-size="11" fill="{TEXT_DIM}" text-anchor="middle">{escape(lab)}</text>'
            )

    return f'''<svg width="100%" viewBox="0 0 {width} {height}" xmlns="http://www.w3.org/2000/svg" role="img">
  {''.join(cells)}
  {''.join(row_label_els)}
  {''.join(col_label_els)}
</svg>'''


def delta_pill(pct: float, *, decimals: int = 0, flat_threshold: float = 0.5) -> str:
    """Render the standard delta pill markup (matches the CSS in the report template)."""
    if abs(pct) < flat_threshold:
        return f'<span class="delta delta--flat">— flat</span>'
    arrow = "↑" if pct > 0 else "↓"
    cls = "delta--up" if pct > 0 else "delta--down"
    return f'<span class="delta {cls}">{arrow} {abs(pct):.{decimals}f}%</span>'


def kpi_tile(label: str, value: str, delta_pct: float | None, spark_values: Sequence[float],
             sub: str | None = None) -> str:
    """A self-contained KPI tile HTML block (with embedded SVG sparkline)."""
    pill = delta_pill(delta_pct) if delta_pct is not None else ''
    sub_el = f'<div class="kpi__sub">{escape(sub)}</div>' if sub else ''
    return f'''<div class="kpi">
  <div class="kpi__label">{escape(label)}</div>
  <div class="kpi__value">{escape(value)}</div>
  <div class="kpi__delta">{pill}{sub_el}</div>
  <div class="kpi__spark">{sparkline(list(spark_values), width=240, height=36)}</div>
</div>'''

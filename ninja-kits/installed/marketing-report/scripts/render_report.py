#!/usr/bin/env python3
"""
render_report.py — render a marketing-report HTML from collected data + analysis JSON.

Inputs:
  --data PATH        Path to data JSON (pulled from sources)
  --analysis PATH    Path to analysis JSON (insights + focus, written by Claude)
  --period weekly|monthly
  --output PATH      Where to write the HTML

Both JSONs follow the schemas in references/report-anatomy.md.

Usage:
  python3 render_report.py --data data.json --analysis analysis.json \
      --period weekly --output report.html
"""

from __future__ import annotations
import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

try:
    from jinja2 import Environment, FileSystemLoader, select_autoescape
except ImportError:
    print("jinja2 not installed — run: pip install jinja2", file=sys.stderr)
    sys.exit(1)

import charts


# ---------- helpers ----------

def fmt_int(n: float) -> str:
    return f"{int(round(n)):,}"

def fmt_money(n: float, *, decimals: int = 0) -> str:
    return f"${n:,.{decimals}f}"

def fmt_pct(n: float, *, decimals: int = 1) -> str:
    return f"{n:.{decimals}f}%"


def delta(curr: float, prev: float) -> float:
    if prev == 0:
        return 0.0
    return (curr - prev) / prev * 100.0


# ---------- builders ----------

def build_kpi_tile(tile_spec: dict) -> str:
    """tile_spec keys: label, value, sub, delta_pct, spark"""
    return charts.kpi_tile(
        label=tile_spec["label"],
        value=tile_spec["value"],
        delta_pct=tile_spec.get("delta_pct"),
        spark_values=tile_spec.get("spark") or [],
        sub=tile_spec.get("sub"),
    )


def build_web_chart(web: dict) -> dict:
    """web = { x_labels, series: [{name, values, color?}] }"""
    series = web["series"]
    palette = [charts.BRAND] + list(charts.NEUTRALS)
    for i, s in enumerate(series):
        s.setdefault("color", palette[i % len(palette)])
    svg = charts.line_chart(series, web["x_labels"], width=1000, height=240)
    return {
        "title": web.get("title", "Sessions by source"),
        "meta": web.get("meta", ""),
        "series": series,
        "svg": svg,
    }


def build_ads_chart(ads: dict) -> dict:
    svg = charts.bar_chart(ads["labels"], ads["values"], compare=ads.get("compare"),
                           y_format=ads.get("y_format", "{:,.0f}"), width=520, height=240)
    return {
        "title": ads.get("title", "Ad performance by channel"),
        "meta": ads.get("meta", ""),
        "svg": svg,
    }


def build_spend_donut(spend: dict) -> dict:
    total = sum(s["value"] for s in spend["slices"])
    palette = [charts.BRAND] + list(charts.NEUTRALS)
    legend = []
    for i, s in enumerate(spend["slices"]):
        color = s.get("color") or palette[i % len(palette)]
        s["color"] = color
        pct = s["value"] / total * 100 if total else 0
        legend.append({
            "name": s["name"],
            "color": color,
            "label": f'{fmt_money(s["value"])} · {pct:.0f}%',
        })
    svg = charts.donut(spend["slices"], size=220,
                       label=fmt_money(total),
                       sublabel=spend.get("sublabel", "Total spend"))
    return {
        "title": spend.get("title", "Spend distribution"),
        "meta": spend.get("meta", ""),
        "svg": svg,
        "legend": legend,
    }


def build_heatmap(h: dict) -> dict:
    svg = charts.heatmap(h["grid"], h["row_labels"], h["col_labels"], width=1000, height=240)
    return {
        "title": h.get("title", "Engagement by day × hour"),
        "meta": h.get("meta", ""),
        "svg": svg,
    }


def build_headline(headline_in: dict) -> dict:
    """Render delta HTML for each hero KPI."""
    out = {
        "title": headline_in["title"],
        "lede": headline_in.get("lede", ""),
        "kpis": [],
    }
    for k in headline_in["kpis"]:
        out["kpis"].append({
            "label": k["label"],
            "value": k["value"],
            "delta_html": charts.delta_pill(k["delta_pct"]) if k.get("delta_pct") is not None else "",
        })
    return out


# ---------- main ----------

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", required=True, type=Path)
    ap.add_argument("--analysis", required=True, type=Path)
    ap.add_argument("--period", choices=["weekly", "monthly"], default="weekly")
    ap.add_argument("--output", required=True, type=Path)
    ap.add_argument("--brand-name", default=None,
                    help="Override the brand name displayed in the report top bar.")
    ap.add_argument("--brand-color", default=None,
                    help="Override the report accent color (hex).")
    args = ap.parse_args()

    data = json.loads(args.data.read_text())
    analysis = json.loads(args.analysis.read_text())

    period_tag = "WEEK OF" if args.period == "weekly" else "MONTH OF"
    period_label = "Weekly" if args.period == "weekly" else "Monthly"

    meta = data.get("meta", {})
    meta["period_tag"] = period_tag
    meta["period_label"] = period_label
    meta["generated_at"] = datetime.now().strftime("%Y-%m-%d %H:%M")
    if args.brand_name:
        meta["brand_name"] = args.brand_name
    if args.brand_color:
        meta["brand_color"] = args.brand_color
    meta.setdefault("brand_name", "Friday Labs")
    meta.setdefault("sources", [])

    # Build the rendered pieces.
    headline = build_headline(analysis["headline"])

    kpi_tiles_html = [build_kpi_tile(t) for t in data.get("kpis", [])]

    channels = None
    if "channels" in data:
        c = data["channels"]
        channels = {
            "title": c.get("title", "Where the traffic and spend went."),
            "lede": c.get("lede", "Web sessions, ad performance, and spend distribution across the active paid channels."),
            "web": build_web_chart(c["web"]),
            "ads": build_ads_chart(c["ads"]),
            "spend": build_spend_donut(c["spend"]),
        }

    content_block = None
    if "content" in data:
        cb = data["content"]
        content_block = {
            "title": cb.get("title", "Content & social performance."),
            "lede": cb.get("lede", "Top and bottom posts across Instagram, TikTok, YouTube, and LinkedIn for the period, plus posting-time heatmap."),
            "heatmap": build_heatmap(cb["heatmap"]),
            "top_posts": cb.get("top_posts", []),
            "bottom_posts": cb.get("bottom_posts", []),
        }

    env = Environment(
        loader=FileSystemLoader(str(SCRIPT_DIR / "templates")),
        autoescape=select_autoescape(["html"]),
    )
    tpl = env.get_template("report.html.j2")

    html = tpl.render(
        meta=meta,
        headline=headline,
        kpi_section_lede=data.get("kpi_section_lede",
                                  "Core marketing KPIs for the period, with delta vs prior period and a 14-point trend sparkline."),
        kpis=kpi_tiles_html,
        channels=channels,
        content=content_block,
        insights=analysis.get("insights", []),
        insights_title=analysis.get("insights_title"),
        insights_lede=analysis.get("insights_lede"),
        focus=analysis.get("focus"),
    )

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(html)
    print(f"Wrote: {args.output}")


if __name__ == "__main__":
    main()

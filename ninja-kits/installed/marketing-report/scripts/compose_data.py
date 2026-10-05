#!/usr/bin/env python3
"""
compose_data.py — merge per-source JSONs into the unified report-data.json that
render_report.py expects.

Reads:
  data/ga4.json
  data/meta_ads.json
  data/hyros.json
  data/metricool.json
  data/email.json          (optional placeholder; ignored if missing)

Writes:
  report-data.json

Each per-source JSON is either {"status": "ok", ...} or {"status": "missing", "reason": "..."}.
Missing sources are tracked in meta.sources so the footer shows them, and any derived
metric / section that needed them is skipped.

Usage:
  python3 compose_data.py --in-dir workspace/{slug}/data --out workspace/{slug}/report-data.json \
      --period weekly --brand-name "Friday Labs" --brand-color "#ff8c42"
"""

from __future__ import annotations
import argparse
import json
import math
import sys
from datetime import datetime, timedelta
from pathlib import Path


def _load(in_dir: Path, name: str) -> dict | None:
    p = in_dir / f"{name}.json"
    if not p.exists():
        return None
    try:
        return json.loads(p.read_text())
    except Exception:
        return None


def _ok(src: dict | None) -> bool:
    return bool(src) and src.get("status") == "ok"


def _delta_pct(curr: float, prev: float) -> float | None:
    if not prev:
        return None
    return (curr - prev) / prev * 100.0


def _spark_from_daily(daily: list[dict], key: str, n: int = 14) -> list[float]:
    if not daily:
        return []
    values = [float(d.get(key, 0) or 0) for d in daily]
    return values[-n:] if len(values) >= n else values


def _fmt_money(n: float, decimals: int = 0) -> str:
    return f"${n:,.{decimals}f}"


def _fmt_int(n: float) -> str:
    return f"{int(round(n)):,}"


def _fmt_pct(n: float, decimals: int = 1) -> str:
    return f"{n:.{decimals}f}%"


def _fmt_multiple(n: float, decimals: int = 2) -> str:
    return f"{n:.{decimals}f}x"


def build_kpis(ga4: dict | None, meta: dict | None, hyros: dict | None) -> list[dict]:
    """Build the 6-8 KPI tiles based on which sources are available."""
    kpis: list[dict] = []

    # Booked calls (Hyros)
    if _ok(hyros):
        cur = hyros["totals"].get("calls_booked", 0)
        prev = hyros.get("prior_window", {}).get("calls_booked", 0)
        kpis.append({
            "label": "Booked calls",
            "value": _fmt_int(cur),
            "sub": "Hyros-attributed, all sources",
            "delta_pct": _delta_pct(cur, prev),
            "spark": [],  # Hyros doesn't always return daily; left empty if not
        })

    # Qualified leads (Hyros)
    if _ok(hyros):
        cur = hyros["totals"].get("leads", 0)
        prev = hyros.get("prior_window", {}).get("leads", 0)
        kpis.append({
            "label": "Qualified leads",
            "value": _fmt_int(cur),
            "sub": "Per Hyros lead events",
            "delta_pct": _delta_pct(cur, prev),
            "spark": [],
        })

    # Web visitors (GA4 sessions)
    if _ok(ga4):
        cur = ga4["totals"].get("sessions", 0)
        prev = ga4.get("prior_window", {}).get("sessions", 0)
        kpis.append({
            "label": "Web visitors",
            "value": _fmt_int(cur),
            "sub": "GA4 sessions",
            "delta_pct": _delta_pct(cur, prev),
            "spark": _spark_from_daily(ga4.get("daily", []), "sessions"),
        })

    # Blended CAC — Hyros + Meta
    if _ok(hyros) and _ok(meta):
        ad_spend = meta["totals"].get("spend", 0)
        calls = hyros["totals"].get("calls_booked", 0) or 0
        cac = (ad_spend / calls) if calls else 0
        prev_spend = meta.get("prior_window", {}).get("spend", 0)
        prev_calls = hyros.get("prior_window", {}).get("calls_booked", 0) or 0
        prev_cac = (prev_spend / prev_calls) if prev_calls else 0
        kpis.append({
            "label": "Blended CAC",
            "value": _fmt_money(cac),
            "sub": "Total spend ÷ booked calls",
            "delta_pct": _delta_pct(cac, prev_cac),
            "spark": [],
        })

    # Conversion rate (sessions → calls, blended)
    if _ok(ga4) and _ok(hyros):
        s = ga4["totals"].get("sessions", 0) or 1
        c = hyros["totals"].get("calls_booked", 0)
        cr = c / s * 100
        ps = ga4.get("prior_window", {}).get("sessions", 0) or 1
        pc = hyros.get("prior_window", {}).get("calls_booked", 0)
        pcr = pc / ps * 100
        kpis.append({
            "label": "Conversion rate",
            "value": _fmt_pct(cr, 2),
            "sub": "Visitor → call booked",
            "delta_pct": _delta_pct(cr, pcr),
            "spark": [],
        })

    # MER — Hyros revenue / Meta spend
    if _ok(hyros) and _ok(meta):
        spend = meta["totals"].get("spend", 0) or 0
        rev = hyros["totals"].get("revenue", 0) or 0
        mer = (rev / spend) if spend else 0
        ps = meta.get("prior_window", {}).get("spend", 0) or 0
        pr = hyros.get("prior_window", {}).get("revenue", 0) or 0
        pmer = (pr / ps) if ps else 0
        kpis.append({
            "label": "MER",
            "value": _fmt_multiple(mer),
            "sub": "Revenue ÷ ad spend",
            "delta_pct": _delta_pct(mer, pmer),
            "spark": [],
        })

    # Ad spend (Meta)
    if _ok(meta):
        cur = meta["totals"].get("spend", 0)
        prev = meta.get("prior_window", {}).get("spend", 0)
        kpis.append({
            "label": "Ad spend",
            "value": _fmt_money(cur),
            "sub": "Meta Ads",
            "delta_pct": _delta_pct(cur, prev),
            "spark": _spark_from_daily(meta.get("daily", []), "spend"),
        })

    # New revenue (Hyros)
    if _ok(hyros):
        cur = hyros["totals"].get("revenue", 0)
        prev = hyros.get("prior_window", {}).get("revenue", 0)
        kpis.append({
            "label": "New revenue",
            "value": _fmt_money(cur),
            "sub": "Hyros-attributed",
            "delta_pct": _delta_pct(cur, prev),
            "spark": [],
        })

    return kpis[:8]


def build_channels(ga4: dict | None, meta: dict | None, hyros: dict | None) -> dict | None:
    if not (_ok(ga4) or _ok(meta)):
        return None

    out: dict = {
        "title": "Where the traffic and spend went.",
        "lede": "Sessions by source from GA4, ROAS by channel from Hyros, and spend distribution across paid channels.",
    }

    # Web — GA4 sessions by source, daily
    if _ok(ga4) and ga4.get("daily"):
        daily = ga4["daily"]
        x_labels = [d["date"][-5:].replace("-", "/") for d in daily]
        # Single "sessions" series (no source breakdown by day from the standard report)
        # If you want multi-series, the pull would need to fetch by date × source dimensions.
        out["web"] = {
            "title": "Daily sessions",
            "meta": f"Source: GA4 · {daily[0]['date']} → {daily[-1]['date']}",
            "x_labels": x_labels,
            "series": [{"name": "Sessions", "values": [d.get("sessions", 0) for d in daily]}],
        }

    # Ads — ROAS by channel (Hyros preferred)
    if _ok(hyros) and hyros.get("by_channel"):
        rows = hyros["by_channel"][:6]
        labels = [r["channel"].title() for r in rows]
        # Hyros doesn't return spend directly via /sales; we can fall back to Meta-derived ROAS:
        values = [round((r.get("revenue", 0) / max(r.get("spend", 1), 1)) if r.get("spend") else 0, 2) for r in rows]
        if not any(values) and _ok(meta):
            # Fallback: just show Meta-reported ROAS as a single bar
            values = [meta["totals"].get("roas", 0)]
            labels = ["Meta (platform-reported)"]
        out["ads"] = {
            "title": "ROAS by channel",
            "meta": "Hyros-attributed where available, platform-reported otherwise",
            "labels": labels,
            "values": values,
            "y_format": "{:.1f}x",
        }
    elif _ok(meta):
        out["ads"] = {
            "title": "Meta ROAS",
            "meta": "Meta-reported only — connect Hyros for true cross-channel attribution",
            "labels": ["Meta"],
            "values": [meta["totals"].get("roas", 0)],
            "y_format": "{:.1f}x",
        }

    # Spend donut (Meta-only by default; can be extended if more ad sources added)
    if _ok(meta):
        slices = []
        if meta.get("by_campaign"):
            for c in meta["by_campaign"][:5]:
                slices.append({"name": c["name"][:40], "value": round(c["spend"], 2)})
        if slices:
            out["spend"] = {
                "title": "Spend distribution",
                "meta": "Top 5 campaigns by spend (Meta)",
                "sublabel": "Total Meta spend",
                "slices": slices,
            }

    return out


def build_content(metricool: dict | None) -> dict | None:
    if not _ok(metricool):
        return None

    # Heatmap
    heatmap = None
    bt = metricool.get("best_times") or {}
    day_order = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
    if all(d in bt for d in day_order):
        heatmap = {
            "title": "Engagement by day × hour (all platforms, normalized)",
            "meta": "Source: Metricool",
            "row_labels": ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"],
            "col_labels": ["12a", "2a", "4a", "6a", "8a", "10a", "12p", "2p", "4p", "6p", "8p", "10p"],
            "grid": [bt[d] for d in day_order],
        }

    # Top + bottom posts
    posts = metricool.get("all_posts") or []
    def _score(p):
        return (p.get("engagement_rate", 0) or 0) * (math.log10(max(p.get("reach", 0) or 0, 10)))
    posts_sorted = sorted(posts, key=_score, reverse=True)

    def _row(p):
        return {
            "title": (p.get("title") or "")[:80],
            "platform": p.get("network", "").title(),
            "reach": f"{int(p.get('reach', 0) or 0):,}",
            "engagement": f"{(p.get('engagement_rate', 0) or 0) * 100:.1f}%",
        }

    top_posts = [_row(p) for p in posts_sorted[:5]]
    bottom_posts = [_row(p) for p in posts_sorted[-5:][::-1]]

    if not heatmap and not top_posts:
        return None

    out = {
        "title": "Content & social performance.",
        "lede": "Organic post performance across connected networks, with the engagement heatmap showing optimal posting windows.",
    }
    if heatmap:
        out["heatmap"] = heatmap
    if top_posts:
        out["top_posts"] = top_posts
        out["bottom_posts"] = bottom_posts
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--in-dir", required=True, type=Path)
    ap.add_argument("--out", required=True, type=Path)
    ap.add_argument("--period", choices=["weekly", "monthly"], default="weekly")
    ap.add_argument("--brand-name", default="Friday Labs")
    ap.add_argument("--brand-color", default="#ff8c42")
    args = ap.parse_args()

    ga4 = _load(args.in_dir, "ga4")
    meta = _load(args.in_dir, "meta_ads")
    hyros = _load(args.in_dir, "hyros")
    metricool = _load(args.in_dir, "metricool")
    email = _load(args.in_dir, "email")

    # Determine window from whichever source has it
    window_start = window_end = None
    for src in (ga4, meta, hyros, metricool):
        if _ok(src) and src.get("window"):
            window_start = src["window"]["start"]
            window_end = src["window"]["end"]
            break
    if not window_start:
        # Fallback to today
        today = datetime.now().date()
        window_end = today.isoformat()
        days = 7 if args.period == "weekly" else 30
        window_start = (today - timedelta(days=days - 1)).isoformat()

    sources_status = [
        ("Google Analytics 4", ga4),
        ("Meta Ads", meta),
        ("Hyros", hyros),
        ("Metricool (social)", metricool),
        ("ActiveCampaign (email)", email),
    ]
    sources_meta = []
    for name, src in sources_status:
        if not src:
            sources_meta.append({"name": name, "status": "missing"})
        elif src.get("status") == "ok":
            sources_meta.append({"name": name, "status": "ok"})
        else:
            sources_meta.append({"name": name, "status": "missing"})

    report = {
        "meta": {
            "brand_name": args.brand_name,
            "brand_color": args.brand_color,
            "brand_glow": "rgba(255, 140, 66, 0.25)",
            "window_start": window_start,
            "window_end": window_end,
            "sources": sources_meta,
        },
        "kpi_section_lede": (
            "Core marketing KPIs for the period, with a delta against the prior window. "
            "Sparklines show the 14-point trajectory entering this period where daily data is available."
        ),
        "kpis": build_kpis(ga4, meta, hyros),
    }
    ch = build_channels(ga4, meta, hyros)
    if ch:
        report["channels"] = ch
    co = build_content(metricool)
    if co:
        report["content"] = co

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(report, indent=2))
    print(f"composed: wrote {args.out} (sources ok: {sum(1 for s in sources_meta if s['status']=='ok')}/{len(sources_meta)})")
    return 0


if __name__ == "__main__":
    sys.exit(main())

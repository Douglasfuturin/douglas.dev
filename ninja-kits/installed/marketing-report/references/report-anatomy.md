# Report Anatomy

The report renders in this order, top to bottom. Each section earns its place — if a section has nothing meaningful to say in a given period, it's dropped (not stubbed with "no data this week").

## Sequence

1. **Top bar** — Brand mark, "Marketing Report" label, period chip, generated timestamp.
2. **Hero card** — Eyebrow pill (e.g. "WEEK OF MAY 13"), one-sentence headline finding, 1-3 sentence lede, three highest-signal KPIs with deltas.
3. **Core metrics tile grid** — 6-8 KPI tiles with delta + 14-point sparkline.
4. **Channel performance** — Line chart (sessions by source), bar chart (ROAS by channel), donut (spend distribution).
5. **Content & social** — Day×hour engagement heatmap, top posts table, underperformers table.
6. **Investigator insights** — 3-6 observation cards, each with title, body, and a single recommended action.
7. **Recommended focus** — Start / Stop / Test list for the upcoming period.
8. **Footer** — Source connection status + window + delta basis.

The hero, KPI grid, investigator insights, and focus list are mandatory. Channels and content are conditional — if their underlying data sources are all missing, the section is dropped.

---

## The unified `report-data.json` schema

This is the contract between the data-pulling layer and the renderer. The composer produces it; the renderer consumes it.

```json
{
  "meta": {
    "brand_name": "Friday Labs",
    "brand_color": "#ff8c42",
    "brand_glow": "rgba(255, 140, 66, 0.25)",
    "window_start": "2026-05-13",
    "window_end": "2026-05-19",
    "sources": [
      {"name": "Google Analytics 4", "status": "ok"},
      {"name": "Meta Ads", "status": "ok"},
      {"name": "Metricool (social)", "status": "ok"},
      {"name": "Hyros", "status": "ok"},
      {"name": "ActiveCampaign (email)", "status": "missing"}
    ]
  },

  "kpi_section_lede": "One-sentence framing of what the tile grid covers.",

  "kpis": [
    {
      "label": "Booked calls",
      "value": "47",
      "sub": "Hyros-attributed, all sources",
      "delta_pct": 23.7,
      "spark": [22, 19, 25, ...]
    }
  ],

  "channels": {
    "title": "Where the traffic and spend went.",
    "lede": "1-2 sentences framing the channel section.",
    "web": {
      "title": "Sessions by source — daily",
      "meta": "Source: GA4 · window 2026-05-06 → 2026-05-19",
      "x_labels": ["5/6", "5/7", ...],
      "series": [
        {"name": "Organic", "values": [820, 870, ...], "color": "#ff8c42"},
        {"name": "Paid",    "values": [410, 420, ...]}
      ]
    },
    "ads": {
      "title": "Ad ROAS by channel",
      "meta": "Last 7d vs prior 7d · Hyros-attributed revenue",
      "labels": ["Meta", "Google", "YouTube", "TikTok", "LinkedIn"],
      "values": [4.8, 5.2, 3.9, 2.1, 1.4],
      "compare": [4.1, 5.0, 3.2, 2.4, 1.7],
      "y_format": "{:.1f}x"
    },
    "spend": {
      "title": "Spend distribution",
      "meta": "Last 7d · all paid channels",
      "sublabel": "Total ad spend",
      "slices": [
        {"name": "Meta Ads", "value": 4820},
        {"name": "Google Ads", "value": 2740}
      ]
    }
  },

  "content": {
    "title": "Content & social performance.",
    "lede": "1-2 sentences framing the content section.",
    "heatmap": {
      "title": "Engagement by day × hour (all platforms, normalized)",
      "meta": "Source: Metricool · last 28 days",
      "row_labels": ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"],
      "col_labels": ["12a", "2a", "4a", "6a", "8a", "10a", "12p", "2p", "4p", "6p", "8p", "10p"],
      "grid": [[0.1, 0.05, ...], ...]
    },
    "top_posts": [
      {"title": "...", "platform": "TikTok", "reach": "184,300", "engagement": "9.4%"}
    ],
    "bottom_posts": [
      {"title": "...", "platform": "Instagram", "reach": "1,840", "engagement": "0.8%"}
    ]
  }
}
```

## The `analysis.json` schema (Claude's output)

This is the *intelligence* layer Claude writes after reading `report-data.json`. It is the highest-leverage artifact in the skill — it's where the model's pattern-recognition adds real value.

```json
{
  "headline": {
    "title": "One sentence with a single <span class=\"accent\">highlighted number</span>.",
    "lede": "1-3 sentences framing why that headline matters.",
    "kpis": [
      {"label": "...", "value": "...", "delta_pct": 12.3}
    ]
  },

  "insights_title": "Patterns worth your attention.",
  "insights_lede": "One sentence introducing the section.",

  "insights": [
    {
      "tag": "SHORT UPPERCASE TAG",
      "title": "One-sentence observation that names a real pattern.",
      "body": "2-4 sentences with the specific evidence — quote numbers from report-data.json.",
      "action": "One specific verb-led next step. Not 'consider'. Not a list."
    }
  ],

  "focus": {
    "title": "Where to spend the next week.",
    "lede": "One sentence framing the choice.",
    "start": ["3 specific moves"],
    "stop": ["1-2 things to drop"],
    "test": ["1 hypothesis to test"]
  }
}
```

## Section-by-section rules

### Hero card
- **Headline title**: ONE sentence. Use the `<span class="accent">…</span>` markup to highlight ONE number — never more than one. Two highlights split the eye.
- **Lede**: 1-3 sentences. Frames WHY the headline matters. Should mention the composition of the win/loss, not just restate it.
- **Hero KPIs**: exactly 3 tiles. These are the *most-important* 3 metrics this period — not necessarily the same 3 every period. Curated, not templated.

### Core metrics tile grid
- 6-8 tiles, fixed list per brand (or per source-availability). Order: revenue → leads → traffic → CAC → conv rate → MER → spend → top-of-funnel volume.
- Each tile gets a 14-point sparkline showing the trajectory entering the period.
- Delta pill is mandatory — no "—" unless the prior-period value is literally unavailable.

### Channel performance
- Three charts side by side: web (line, full-width), ads (bar, half-width), spend (donut, half-width).
- The line chart prefers GA4 data; falls back to Hyros if GA4 is missing.
- The bar chart prefers Hyros ROAS; falls back to Meta-reported ROAS.
- The donut always uses ad-platform-reported spend (it's the ground truth for that one).

### Content & social
- Heatmap covers 28-day trailing posting engagement (smoother than 7-day).
- Top posts: 5 rows max, ranked by engagement_rate × log(reach) so a viral 5%-engagement post outranks a niche 12%-engagement post with 200 reach.
- Bottom posts: 5 rows of posts that consumed production time but didn't earn it. Visitors will scan this as the "stop doing" list before they read the actual Stop section.

### Investigator insights
- **3-6 cards max.** Fewer is better. If you can't credibly find 3 patterns, the period was too quiet — say so in the lede and ship 1 or 2.
- Each insight has a SINGLE recommended action — never a list of "and also consider…".
- Don't restate the dashboard. The insight earns its slot by surfacing a CAUSE, a CROSS-CHANNEL pattern, or an ANOMALY.

See [analysis-framework.md](analysis-framework.md) for how to find the patterns.

### Recommended focus
- 3 starts max, 1-2 stops, 1 test. Hard limit.
- Every item is verb-led ("Publish four new long-form posts…" not "More long-form").
- Each item should be doable inside the next period — no "redo the brand" 6-month projects.

### Footer
- Lists all data sources with green/red dot.
- Always includes the window dates and the comparison basis ("vs prior 7d").

## Conditional rendering

- If `data.channels` is absent → channel section is dropped.
- If `data.content` is absent → content section is dropped.
- If `analysis.insights` has fewer than 3 items → still render, but adjust the lede to acknowledge the quiet period.
- If `analysis.focus` is absent → drop the focus section (rare; should always have at least 1 start).

## Mobile rendering

The report is dark editorial and primarily a desktop artifact. But it must not break on mobile:
- KPI grid collapses 4-col → 2-col → 1-col
- Channel charts stack vertically below 880px
- Heatmap remains horizontally scrollable rather than squashed

Tested down to 375px. Don't ship if the headline wraps to 4+ lines at 375px — shorten the headline.

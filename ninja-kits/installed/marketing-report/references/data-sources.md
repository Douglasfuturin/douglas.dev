# Data Sources

Every source the marketing-report skill can pull from. Each entry lists: the environment variables / credentials required, the pull method (Python script vs MCP), and the JSON schema it writes.

The skill works with whatever subset is available. Missing sources are flagged in the report footer; insights that depend on them are suppressed.

## 1. Google Analytics 4 — Web traffic

**Purpose**: Web sessions, pageviews, source/medium breakdown, top landing pages, conversions (events).

**Connection requirements**:
- A GA4 service account JSON file (Google Cloud → IAM → Service Accounts → create + download key)
- The service account email added as a Viewer in GA4 Property → Admin → Property Access Management
- The GA4 Property ID (numeric, found in GA4 → Admin → Property Settings)

**Environment variables**:
```
GA4_SERVICE_ACCOUNT_PATH=/path/to/service-account.json
GA4_PROPERTY_ID=123456789
```

**Pull command**:
```bash
python3 scripts/pull_ga4.py --start 2026-05-13 --end 2026-05-19 --out workspace/{slug}/data/ga4.json
```

**Python dependencies**: `google-analytics-data`

**Schema written**:
```json
{
  "status": "ok",
  "source": "ga4",
  "window": {"start": "2026-05-13", "end": "2026-05-19"},
  "totals": {
    "sessions": 12847,
    "users": 9234,
    "pageviews": 38201,
    "engaged_sessions": 7891,
    "conversions": 183,
    "engagement_rate": 0.614
  },
  "by_source": [
    {"source": "google / organic", "sessions": 6821, "conversions": 97},
    {"source": "facebook / cpc", "sessions": 2104, "conversions": 41}
  ],
  "daily": [
    {"date": "2026-05-13", "sessions": 1640, "conversions": 22},
    ...
  ],
  "top_pages": [
    {"path": "/", "sessions": 4210, "engagement_rate": 0.67},
    ...
  ],
  "prior_window": {
    "sessions": 11848,
    "users": 8517,
    "conversions": 161
  }
}
```

---

## 2. Meta Ads — Paid social (Facebook + Instagram)

**Purpose**: Spend, impressions, clicks, CTR, CPC, conversions, ROAS by campaign/adset/ad. Creative performance breakdown.

**Connection requirements**:
- Meta Business Manager → System Users → grant access to an app
- Long-lived access token (use Graph API Explorer to generate, or System User token)
- Ad Account ID (the `act_1234567890` form)

**Environment variables**:
```
META_ADS_ACCESS_TOKEN=EAAB...
META_ADS_ACCOUNT_ID=act_1234567890
META_ADS_API_VERSION=v22.0
```

**Pull command**:
```bash
python3 scripts/pull_meta_ads.py --start 2026-05-13 --end 2026-05-19 --out workspace/{slug}/data/meta_ads.json
```

**Python dependencies**: `requests` (no SDK needed — direct Graph API HTTP)

**Schema written**:
```json
{
  "status": "ok",
  "source": "meta_ads",
  "window": {"start": "2026-05-13", "end": "2026-05-19"},
  "totals": {
    "spend": 4820.41,
    "impressions": 1242109,
    "clicks": 18420,
    "ctr": 0.0148,
    "cpc": 0.262,
    "conversions": 41,
    "roas": 4.8
  },
  "by_campaign": [
    {"name": "Q2 - VSL - Cold", "spend": 2104.10, "conversions": 21, "roas": 5.2},
    ...
  ],
  "by_creative": [
    {"id": "120203...", "name": "Hook A - Founder POV", "spend": 410.20, "ctr": 0.021, "conversions": 8}
  ],
  "daily": [
    {"date": "2026-05-13", "spend": 689.10, "conversions": 6, "roas": 4.4},
    ...
  ],
  "prior_window": {
    "spend": 4623.10,
    "conversions": 38,
    "roas": 4.1
  }
}
```

---

## 3. Hyros — Cross-channel attribution

**Purpose**: True ROAS across channels (Meta, Google, YouTube, organic, email, etc.), CAC, LTV signals, multi-touch attribution.

**Connection requirements**:
- Hyros Account → Integrations → API Keys → create one
- The Account/Workspace ID

**Environment variables**:
```
HYROS_API_KEY=hyk_...
HYROS_WORKSPACE_ID=...
```

**Pull command**:
```bash
python3 scripts/pull_hyros.py --start 2026-05-13 --end 2026-05-19 --out workspace/{slug}/data/hyros.json
```

**Python dependencies**: `requests`

**Schema written**:
```json
{
  "status": "ok",
  "source": "hyros",
  "window": {"start": "2026-05-13", "end": "2026-05-19"},
  "totals": {
    "revenue": 42344.18,
    "leads": 183,
    "calls_booked": 47,
    "blended_cac": 214.07,
    "blended_roas": 4.21
  },
  "by_channel": [
    {"channel": "meta", "spend": 4820, "revenue": 23136, "leads": 78, "calls": 21, "roas": 4.8},
    {"channel": "google", "spend": 2740, "revenue": 14248, "leads": 42, "calls": 13, "roas": 5.2},
    {"channel": "linkedin", "spend": 428, "revenue": 599, "leads": 14, "calls": 11, "roas": 1.4},
    ...
  ],
  "first_touch_view": [
    {"channel": "meta", "revenue": 12120},
    {"channel": "linkedin", "revenue": 18420}
  ],
  "prior_window": {
    "revenue": 33210,
    "calls_booked": 38,
    "blended_cac": 241.40
  }
}
```

The Hyros pull is the highest-leverage source — it produces the true CAC / ROAS / MER picture and joins paid spend (Meta/Google) to actual revenue. Without Hyros, the report falls back to Meta-reported ROAS (which inflates against organic credit).

---

## 4. Metricool — Organic social (IG/TT/YT/LinkedIn/X)

**Purpose**: Organic post performance across all connected social accounts. Followers / reach / engagement / saves / shares. Best-time-to-post heatmap.

**Connection requirements**:
- The Metricool MCP server connected in Claude. Available tools (deferred — load via ToolSearch if not present):
  - `getAnalyticsAvailableMetrics`
  - `getAnalyticsDataByMetrics`
  - `getBestTimeToPostByNetwork`
  - `getScheduledPosts`
  - `getBrandSettings`

**Pull method**: not a Python script — Claude calls the MCP tools directly. See `scripts/pull_metricool.md` for the exact tool-call sequence.

**Schema written** to `workspace/{slug}/data/metricool.json`:
```json
{
  "status": "ok",
  "source": "metricool",
  "window": {"start": "2026-05-13", "end": "2026-05-19"},
  "by_network": {
    "instagram": {
      "followers": 8421,
      "follower_delta": 142,
      "reach": 184300,
      "engagement_rate": 0.058,
      "top_posts": [
        {"id": "...", "title": "POV: every AI tool…", "reach": 62400, "engagement_rate": 0.078, "format": "reel"}
      ]
    },
    "tiktok": { ... },
    "youtube": { ... },
    "linkedin": { ... }
  },
  "best_times": {
    "monday":    [0.10, 0.05, 0.05, 0.15, 0.40, ...],   // 12 hour buckets, normalized 0..1
    "tuesday":   [0.10, 0.05, 0.05, 0.20, 0.50, ...],
    ...
  },
  "all_posts": [
    {"id": "...", "network": "tiktok", "title": "...", "published_at": "2026-05-15T14:23:00Z", "reach": 184300, "engagement_rate": 0.094, "format": "short_video"}
  ]
}
```

---

## 5. ActiveCampaign / Email (placeholder — not yet implemented)

**Purpose**: List growth, open rates, click rates, top-performing sends, segment performance.

**Status**: Stub. The skill knows email is a source but doesn't have a pull script yet. If the user has email metrics they want included, they can manually drop a JSON at `workspace/{slug}/data/email.json` following the schema below; the composer will pick it up.

**Future implementation notes**: ActiveCampaign has a v3 REST API (`api-us1.api.com/3/`). Pull last-7d campaign reports + list-growth metric.

---

## How sources combine in the composer

`compose_data.py` reads each `data/*.json` file and builds the unified `report-data.json` the renderer expects.

Key derivations:
- **Blended CAC** = (Meta spend + Google spend + paid channel spend from Hyros) ÷ Hyros calls_booked
- **MER (marketing efficiency ratio)** = Hyros total revenue ÷ total ad spend
- **Channel ROAS bar chart** = `hyros.by_channel` (preferred) or `meta_ads.totals.roas` (fallback if Hyros missing)
- **Best-time heatmap** = `metricool.best_times` (preferred) or computed from `metricool.all_posts` engagement rates grouped by day×hour (fallback)

If a source is missing, the composer emits `null` for any derived metric that needed it, and the renderer skips the corresponding tile/chart silently.

## Adding a new source

To add a new data source:

1. Create `scripts/pull_{source}.py` (or `scripts/pull_{source}.md` if it's MCP-based)
2. Make it write a `data/{source}.json` matching one of the schemas above (status / window / totals / breakdowns / prior_window)
3. Update `scripts/compose_data.py` to merge it into the unified `report-data.json`
4. Add an entry to `meta.sources` so the footer shows the connection status
5. Document the env vars + schema here

Don't bake a new source into the renderer — keep it data-source-agnostic so the report continues to work even if sources change.

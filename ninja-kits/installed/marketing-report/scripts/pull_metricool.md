# Metricool MCP Pull — Instructions for Claude

Unlike GA4/Meta/Hyros, the Metricool data pull is done by Claude calling the Metricool MCP tools directly. This document tells the model exactly what to call and how to shape the output JSON.

The MCP server is registered with deferred tools. Load them via ToolSearch if not already available:

```
ToolSearch({ query: "metricool", max_results: 12 })
```

You should see (tool names may differ slightly; match by suffix):
- `getBrandSettings` — list connected accounts/networks for the workspace
- `getAnalyticsAvailableMetrics` — list metrics available per network
- `getAnalyticsDataByMetrics` — pull metric values for a metric × network × date range
- `getBestTimeToPostByNetwork` — engagement heatmap (day × hour)
- `getScheduledPosts` — recent + scheduled posts with engagement per post (optional)

## Step 1 — Identify connected networks

Call `getBrandSettings`. Filter to networks the user has connected (instagram, tiktok, youtube, linkedin, x, facebook). Keep that list — every subsequent call iterates over it.

## Step 2 — For each network, pull totals

Call `getAnalyticsDataByMetrics` for each network with:
- `dateFrom = window_start`, `dateTo = window_end`
- Metrics to request (per network, fall back to whatever the network exposes):

| Network | Metrics |
|---------|---------|
| instagram | `followers, follower_growth, reach, impressions, engagement, profile_visits` |
| tiktok | `followers, follower_growth, views, likes, comments, shares, engagement` |
| youtube | `subscribers, views, watch_time, engagement, impressions` |
| linkedin | `followers, follower_growth, impressions, engagement, clicks` |
| x | `followers, follower_growth, impressions, engagement` |
| facebook | `followers, follower_growth, reach, engagement, impressions` |

Some metrics won't be available on every account tier — silently skip ones that error.

## Step 3 — Pull recent posts

For each connected network, call `getScheduledPosts` (or equivalent posts-listing tool) with the window dates and `status=published`. Capture per-post:
- `id`, `published_at`, `network`, `format` (reel/carousel/static/short_video/long_video), `title` or first 80 chars of caption, `reach`, `engagement_rate`

Rank top 8 by `engagement_rate × log10(max(reach, 10))` for the "Top posts" table.
Rank bottom 5 by the same score (ascending) for the "Underperformers" table.

## Step 4 — Pull the best-time heatmap

Call `getBestTimeToPostByNetwork` (or compute manually if the tool isn't available).

If the tool returns a per-network heatmap, average across networks (weighted by follower count) to produce ONE blended 7-row × 12-col grid normalized 0..1.

If the tool isn't available, compute manually from Step 3's post list:
- Bucket each post into (day_of_week, hour_bucket) where hour_bucket = floor(hour/2)
- For each cell, average the post engagement_rates
- Normalize the grid so the highest cell is 1.0

## Step 5 — Write the unified output JSON

Write to `workspace/{slug}/data/metricool.json`:

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
    "monday":    [0.10, 0.05, 0.05, 0.15, 0.40, 0.65, 0.85, 0.95, 0.90, 0.75, 0.45, 0.20],
    "tuesday":   [...],
    "wednesday": [...],
    "thursday":  [...],
    "friday":    [...],
    "saturday":  [...],
    "sunday":    [...]
  },
  "all_posts": [
    {"id": "...", "network": "tiktok", "title": "...", "published_at": "2026-05-15T14:23:00Z", "reach": 184300, "engagement_rate": 0.094, "format": "short_video"}
  ]
}
```

Keys for arrays under `by_network` use the lowercase network name. If a network isn't connected, omit it entirely (don't write `"instagram": null`).

## Error handling

If `getBrandSettings` fails or returns no connected networks, write:
```json
{"status": "missing", "source": "metricool", "reason": "no connected networks"}
```

If individual network calls fail, exclude that network from `by_network` and continue. Don't abort the whole pull.

## Rate-limit etiquette

Metricool MCP calls are bursty-friendly but not free. Cap network iteration to ≤6 networks and ≤30 total tool calls per report. If approaching the cap, prioritize: top 3 networks by follower count, then heatmap, then post lists, then per-network metrics last.

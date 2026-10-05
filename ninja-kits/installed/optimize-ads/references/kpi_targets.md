# KPI Targets

**This file is yours to edit.** The skill reads these as the benchmarks for what "good" looks like. Add per-account or per-campaign overrides as you learn what's realistic for your business.

---

## Defaults (used when no per-campaign target is set)

| Objective | Target ROAS | Target CPA | Target CTR (link) | Notes |
|---|---|---|---|---|
| Sales / Conversions | **2.5×** | derived from AOV ÷ target ROAS | **1.5%** | Below 1.5× ROAS = drainer territory. |
| Lead Gen (form fills) | n/a | **$15** | **1.2%** | Adjust CPA based on lead-to-customer rate. |
| App Install | n/a | **$3.50** | **1.0%** | Highly category-dependent. |
| Awareness / Reach | n/a | CPM **< $12** | n/a | Use frequency cap as the discipline. |
| Engagement | n/a | CPE **< $0.10** | **2.0%** | Mostly a top-of-funnel signal. |

---

## Per-campaign overrides

Add entries here when you've validated a tighter or looser target for a specific campaign. Format:

```
- campaign: <campaign_name or id>
  objective: sales
  target_roas: 3.0
  target_cpa: $42
  note: "Hero product line — higher margin, can absorb a lower ROAS than core."
```

### Active overrides

_(none yet — add as you learn)_

---

## What counts as "missing target"

- **Drainer threshold:** running at < 60% of target (e.g., target ROAS 2.5 → drainer at < 1.5).
- **Winner threshold:** running at > 130% of target (e.g., target ROAS 2.5 → winner at > 3.25).
- **Healthy band:** 60-130% of target — keep an eye on, don't actively change.

The skill uses these thresholds in framework calculations. Tune them here, not in `frameworks.md` or scripts.

---

## CTR floors (link CTR specifically — not all CTR)

CTR on its own is a weak signal, but link CTR is decent. If link CTR is < 50% of the target above and CPM is normal, the creative isn't earning attention. Refresh.

If CTR is fine but conversion rate on the landing page is low, the problem is downstream of ads — say so in the recommendation and don't try to fix it with ad changes alone.

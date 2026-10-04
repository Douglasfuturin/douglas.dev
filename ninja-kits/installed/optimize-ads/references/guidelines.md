# Guidelines & Guardrails

**This file is yours to edit.** These are the rules the skill never breaks. Frameworks propose; guardrails veto.

---

## Hard guardrails (skill must respect these)

1. **Recommend-only.** The skill never calls update/pause/PATCH endpoints. It writes recommendations to the session log. The human applies them in Ads Manager.

2. **Don't touch ads with < $50 lifetime spend.** Not enough data to draw conclusions. Mention them in the snapshot if anything looks off, but no recommendations.

3. **Don't touch campaigns in learning phase.** If a campaign has < 50 conversions in the last 7 days AND its status shows learning, do not recommend pausing or major budget changes. A creative swap is OK if creative is clearly failing.

4. **Don't recommend budget changes > 20% in either direction.** Meta resets the learning phase on swings larger than that. If you want to "double the budget on a winner," recommend it as a staged plan: +20% now, check in 3-4 days, +20% again.

5. **Don't recommend pausing always-on campaigns.** Campaigns listed under `always_on_campaign_ids` in `config/config.json` are off-limits for pause recommendations. Budget tweaks within bounds are fine.

6. **Don't recommend the same change twice within 7 days unless evidence changed.** Check the last 2-3 sessions before recommending. If you already suggested it and the user deferred or rejected, ask why before re-recommending — or skip and note it under "Considered and skipped."

7. **Statistical sanity.** Don't make decisions on < 100 impressions or < 10 link clicks at the ad level. Roll up to the adset or campaign level instead.

---

## Soft guardrails (defaults the user can override per-session)

- **Default lookback window:** 7 days, unless the last session is more recent (then use last-session → now).
- **Min spend for "winner" classification:** $200 lifetime in the lookback window.
- **Min conversions for "winner" classification:** 10 conversions in the lookback window.
- **Frequency ceiling before flagging fatigue:** 3.0 (CTR-confirmed) / 4.0 (audience saturation).
- **Default ROAS target if not specified per-campaign:** see `kpi_targets.md`.

If a session is run with a non-default window (e.g., user says "look at the last 30 days"), use that and note it explicitly in the session log.

---

## Reporting and tone

- Lead with the **"What we learned"** preamble from past sessions. Show your work.
- Snapshots are short. Numbers and deltas, not paragraphs.
- Every recommendation cites a framework by name. If no framework fits, don't make the recommendation.
- If a framework keeps producing rejections, say so in the preamble and suggest editing `frameworks.md`.
- If the user repeatedly rejects a specific type of change (e.g., always rejects "consolidation"), bias against that framework in future sessions and tell them you're doing so.

---

## When to refuse to recommend

- Account spent < $50 in lookback → no recommendations, just observations.
- Account has 0 conversions and 0 link clicks across the window → something is broken upstream (pixel, payment, landing page). Recommend the user check those, not the ads.
- Pull script returned errors on > 50% of campaigns → don't recommend on partial data. Ask the user to re-auth or check token scopes.

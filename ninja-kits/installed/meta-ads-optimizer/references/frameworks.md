# Optimization Frameworks

**This file is yours to edit.** The skill reads it every session. Add frameworks you trust, remove ones you don't, tune the thresholds. The skill will only reach for frameworks defined here.

Each framework has a **name**, a **signal** (what to look for), an **action** (what to recommend), and **confidence notes** (when this framework lies). The skill cites the framework name in every recommendation, so if a framework keeps producing bad calls you'll see it in the session logs and can sharpen or delete it.

---

## 1. Kill the Drainers

**Signal:** Campaign or adset has spent ≥ 2× its target CPA without a single conversion, OR has spent ≥ 3× target CPA with CPA running > 2× target over the lookback window.

**Action:** Pause it. Don't try to "fix" a drainer with budget cuts or audience tweaks — the creative or offer isn't working. If the creative tested well elsewhere, the audience is wrong; if the audience is proven, the creative is wrong. Either way, the live ad is bleeding money.

**Confidence notes:** High confidence when spend > 3× target CPA. Lower confidence in the first 48 hours after launch (learning phase). Never apply to a campaign with < $50 lifetime spend.

---

## 2. Scale the Winners

**Signal:** Campaign has been ROAS-positive (> target ROAS) for ≥ 4 consecutive days, with daily spend stable or rising, and frequency < 2.5.

**Action:** Increase daily budget by 15-20%. **Not** 50%, not 2x — Meta's learning resets if you change budget by more than ~20% on a CBO/ABO campaign, and you lose the momentum you're trying to scale.

**Confidence notes:** High confidence on Advantage+ Shopping campaigns (they handle budget changes more gracefully). Medium on standard CBO. Low if conversions per day < 10 (small numbers swing wildly).

---

## 3. Creative Fatigue Refresh

**Signal:** An ad has frequency > 3.0 AND CTR has declined > 25% from its first-week CTR, OR CPM has risen > 30% with no audience change.

**Action:** Duplicate the adset and swap in 2-3 fresh creative variants. Pause the fatigued ad. Don't kill the adset — the audience is still proven.

**Confidence notes:** Frequency alone is a weak signal — some audiences tolerate frequency 5+. The CTR-decline-from-baseline is the strong signal. Skip if total spend < 5× target CPA (not enough data to call fatigue).

---

## 4. Audience Saturation

**Signal:** Frequency > 4.0 across an audience over a rolling 7-day window AND ROAS is declining week-over-week.

**Action:** Expand the audience (add lookalikes, broaden interests, or test broad targeting), OR move budget to a fresh audience adset. Don't just refresh creative — the audience itself is tapped.

**Confidence notes:** This is distinct from creative fatigue: there, CTR drops; here, ROAS drops even when CTR holds. If both are true at once, audience saturation is the heavier issue.

---

## 5. CPM Spike Investigation

**Signal:** CPM rose > 40% week-over-week on a campaign whose budget didn't change.

**Action:** Don't reflexively act — investigate first. Common causes:
- Auction got more competitive (seasonal, competitor launch) → may need to accept it or push to less competitive audiences
- Quality / engagement / conversion ranking dropped → creative is being penalized, refresh
- Audience was narrowed accidentally → check recent changes

Recommend the diagnostic step + one concrete next move based on what you find. This framework rarely produces a "pause" or "scale" recommendation directly.

**Confidence notes:** Always medium confidence — CPM spikes have many causes and the right action depends on which one.

---

## 6. Consolidation

**Signal:** Account has > 3 active campaigns with the same objective AND average daily conversions per campaign < 10.

**Action:** Consolidate into 1-2 campaigns. Meta's algorithm needs ~50 conversions/week per ad set to exit learning. Splitting budget across many small adsets keeps them all stuck in learning forever.

**Confidence notes:** High confidence if the account has chronic learning-phase issues. Lower if the campaigns are intentionally segmented for reporting reasons the user cares about.

---

## 7. Creative Winner Cross-Pollination

**Signal:** A specific ad (creative) is significantly outperforming siblings in its adset (e.g., 2× the CTR or ROAS of the next-best ad in the same adset) with ≥ 50 conversions or ≥ $500 spend.

**Action:** Test that winning creative in other adsets / audiences. The creative has signal — find out how broadly it travels.

**Confidence notes:** High confidence on the creative itself. Lower on whether it'll work in a new audience — be explicit that this is a test, not a guaranteed win.

---

## How the skill picks among these

When multiple frameworks fire on the same target, prefer:
1. **Kill the Drainers** (stop bleeding first)
2. **Audience Saturation** (structural issue)
3. **Creative Fatigue** (tactical refresh)
4. **Scale the Winners** (compounding)
5. **CPM Spike Investigation** (diagnostic)
6. **Consolidation** (account hygiene)
7. **Creative Winner Cross-Pollination** (opportunistic)

Each recommendation in a session must name exactly one framework. If you find yourself wanting to invent a new framework on the fly, **suggest adding it to this file** instead of silently using it.

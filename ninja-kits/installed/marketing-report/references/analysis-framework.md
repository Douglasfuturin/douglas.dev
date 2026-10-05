# Analysis Framework

How Claude writes the `analysis.json` from the unified `report-data.json`. This is the highest-leverage layer of the skill — it's where the model's pattern-recognition turns a dashboard into intelligence.

The deliverables Claude writes:
1. **Headline finding** — the one sentence the operator could quote in a board update.
2. **Investigator insights** — 3-6 observations that surface causes, cross-channel patterns, or anomalies the operator wouldn't see by skimming dashboards.
3. **Recommended focus** — 3 starts, 1-2 stops, 1 test for the next period.

## The bar to clear

An insight earns its slot ONLY if it answers at least one of these questions better than the operator could answer by looking at the raw dashboard:

1. **Why did this happen?** (cause behind a number)
2. **What's about to break / compound?** (forward-looking signal)
3. **What does the cross-channel data say that no single channel knows?** (joining attribution, content, and web data)
4. **What pattern is hidden inside the average?** (segment-level finding the topline obscures)
5. **What disagreement exists between two metrics that should agree?** (data quality / attribution gap)

If the proposed insight is just "X went up Y%" or "Channel Z is performing well" — it's a dashboard restatement, not an insight. Drop it.

## Pattern-detection playbook

The framework below is what to run through when looking at the unified data JSON. Not every period will have all patterns; pick the 3-6 most leverageable.

### A. Source-mix shift
Look at `ga4.by_source` percentages this period vs prior. Has organic gone from 41% to 53% of total sessions? Has paid contribution shrunk despite increased spend? If yes — the growth engine is shifting, and the budget allocation may be lagging.

Insight template: "Organic compounded harder than paid this period — but you're still spending like paid is the growth engine."

### B. Channel ROAS divergence
Compare `hyros.by_channel` ROAS to `meta_ads.totals.roas` (the platform-reported ROAS). If they disagree by >40%, Meta is over-counting (or Hyros is under-counting). Either way, the operator is making decisions on wrong data.

Insight template: "Meta reports 6.2x but Hyros sees 4.1x — the platform is double-counting purchases that organic warmed up."

### C. Content format vs cadence mismatch
Look at `metricool.all_posts` and group by `format` (reel / carousel / static / short_video / long_video). Compute average engagement_rate per format. Compare to actual *count* of posts per format published.

If the operator published 10 carousels at 1.4% engagement and 3 reels at 5.8% engagement, the publishing schedule is misaligned with what's working.

Insight template: "Short-form is your highest-engagement format by 4x, but your schedule still skews carousel-heavy."

### D. Best-time-to-post miss
`metricool.best_times` shows engagement-peak by day×hour. Compare to actual posting timestamps in `metricool.all_posts`. If posts are landing OUTSIDE peak windows >60% of the time, the operator is leaving organic reach on the table.

Insight template: "Your peak posting window is Thursday 2pm — and you've published exactly zero posts in that slot for the last 21 days."

### E. Funnel-step regression / improvement
Compare conversion rates between funnel steps (visitor → lead → call → close where data allows). If a step's rate changes >20% with no deployed change, the *traffic quality* shifted, not the page.

Insight template: "The application step-2 dropoff fixed itself — but you didn't change anything on the page. The new completers are 71% organic, which is bringing more-qualified visitors."

### F. Spend-quality mismatch
Cross-reference `meta_ads.by_campaign` spend with `hyros.by_channel` revenue at the campaign-level. A campaign can have high spend + good Meta-reported ROAS but bad Hyros true-ROAS (it's claiming credit for conversions other channels closed). Surface this.

Insight template: "Campaign X has the highest spend and Meta's best ROAS — but Hyros says it's last-clicking conversions other channels closed. The true ROAS is 1.8x, not 5.6x."

### G. Lookalike opportunity
Look at top-performing creatives in `meta_ads.by_creative`. If 1-2 creatives are doing 5-10x the average, the operator should be making more like them.

Insight template: "Two ads are doing 8x the average ROAS — they share the same hook style (founder POV with a specific dollar number)."

### H. Underleveraged channel
Find channels in `hyros.by_channel` where spend is small (<$500) but ROAS is high (>4x). That's an underweight channel — more budget would likely scale.

Insight template: "LinkedIn is spending $428 at 7.4x ROAS — the smallest channel by spend, the highest by quality. It's underweight."

### I. First-touch vs last-touch divergence
Hyros gives you both. If a channel looks weak by last-touch but is the top first-touch source, it's WARMING traffic the other channels CLOSE. Cutting it would crater the whole funnel.

Insight template: "LinkedIn looks like your worst channel by ROAS — but it's your #1 first-touch source. Cut it and watch Meta's numbers crater too."

### J. Anomaly: unexpected spike
Look at `ga4.daily` and `hyros.daily` for any single day where a metric is >3 standard deviations from the trailing 14-day average. Surface it WITH a possible cause if you can find one (a tweet, an email send, a press mention).

Insight template: "Tuesday spiked 4x normal traffic — the LinkedIn post you published Monday afternoon is still driving sessions 36 hours later."

## Writing the insight cards

Each insight card has four parts:

### Tag (short uppercase)
A category label, max 4-5 words. Examples: "WHERE GROWTH ACTUALLY CAME FROM", "ATTRIBUTION GAP", "CONTENT FORMAT INSIGHT", "FUNNEL ANOMALY". This is the eyebrow of the card.

### Title (one sentence)
The observation, named. Must contain at least one number or one specific entity (channel, campaign, post). Bad: "Organic is doing well." Good: "Organic sessions grew 84% week-over-week and now drive 53% of total traffic."

### Body (2-4 sentences)
The evidence. Quote specific numbers from the data JSON. Include the secondary observation that turns the headline into a *finding* (e.g. "*despite this*, paid spend rose"). Tell the operator something they couldn't see by glancing.

### Action (one sentence)
The recommended move. Verb-led, specific, doable inside the next period. Never "consider". Never a list. Never "monitor closely". Always a real change to make.

Bad: "Consider re-evaluating the content strategy."
Good: "Hold paid spend flat for two weeks and redirect that attention to publishing four more long-form pieces on the same three topic clusters that drove the April win."

## Writing the headline finding

The hero headline is the single highest-leverage sentence in the report. It's what the operator quotes when their CEO/co-founder asks "how was the week?"

Constraints:
- **ONE sentence.** No exceptions. If it's two, you're hedging.
- **ONE highlighted number**, wrapped in `<span class="accent">…</span>`. Two highlights split focus.
- **Specific.** Use real numbers, not "significant" or "strong".
- **Causal or compositional**, not just declarative. "Booked calls up 23.7%" is a number; "Booked calls up 23.7% — the cheapest week of the quarter at $214 CAC" tells you why it matters.
- **No hype words.** Banned: "incredible", "massive", "amazing", "huge", "killer", "fire". Operators don't talk like this.

### Headline templates that work

- "{KPI} up {X%} to {value}, {secondary metric} {context} — {qualifier}."
- "{X} of your {Y} came from {single source} — {implication}."
- "{Metric} broke {threshold} for the first time, driven by {single cause}."
- "Despite {visible win}, {hidden problem} got worse."
- "{Channel} is now {fraction} of the total, up from {prior fraction} — {what it means for budget}."

## Writing the Start / Stop / Test focus list

The focus list is the *forward* part of the report. Everything else is rearview.

### Constraints
- **3 starts maximum.** If you have 5 starts, you have zero priorities.
- **1-2 stops.** Every operator has too much in motion; naming what to drop is harder and more valuable than naming what to add.
- **1 test.** A specific hypothesis with a measurable outcome inside the next period.

### Selection rubric (which moves go on the list)
1. Highest leverage per hour spent (prefer compounding moves over one-time moves)
2. Doable inside the next period (no "rebrand the company")
3. Directly tied to an insight earlier in the report (the focus should feel like the logical consequence of the analysis, not a separate brainstorm)
4. Concrete enough that the operator could brief a team member tomorrow morning

### Writing style
- Verb-led, present tense imperative.
- Includes a number or specific entity where possible ("Publish four new long-form posts on the three topic clusters from the April win" not "More long-form content").
- One line each. If it needs more than 25 words, it's not crisp enough.

## Voice for the analysis copy

This is a Tyler-style voice rule that applies across the analysis layer. The voice should be:

- **Operator-to-operator.** Not consultant-y. Not academic. "Hold spend flat for two weeks" not "It may be advisable to consider holding spend constant during the upcoming period."
- **Flowing prose with commas and em-dashes** in the body sections. Not staccato. (See the landing-page skill's `copy-patterns.md` for the anti-staccato rule — same applies here.)
- **Oxford commas** in every list.
- **No hedging.** "The picture flips" not "the picture may flip". The operator can override your recommendation; your job is to be definitive, not to cover yourself.
- **No corporate-speak.** Banned: "synergies", "low-hanging fruit", "leverage" as a verb, "best practices", "going forward".

## What to do when data is missing

If a key source is missing (Hyros down, Meta token expired, etc.):

1. **Mark the affected insights as suppressed** — don't fabricate around the missing data.
2. **Note in the report's lede that the analysis is partial** — the operator should know to weight the recommendations accordingly.
3. **Don't generate insights that would have needed the missing source** — better to ship 3 strong insights than 5 with one fabricated.

A short report with high-conviction insights beats a long report with hedge-laden filler. Every time.

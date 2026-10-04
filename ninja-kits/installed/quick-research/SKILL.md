---
name: quick-research
description: Research any topic — product, person, company, technology, decision — and return a clean, source-backed report calibrated to the depth the user needs. Trigger when the user says "research X," "look into Y," "what's the deal with Z," "give me a breakdown of," "investigate this," "find out about," "should I use [tool]," "compare [A] vs [B]," or any variant of needing a working summary they can act on.
---

# Topic Deep Dive

A research request can mean three completely different things. Saying "I'll research it" without knowing which one wastes the user's time and yours. This skill picks the right depth, gathers from real sources, and writes a report the user can act on without re-researching.

## Three depth tiers

Pick one based on the user's request. Default to **Brief** unless the wording signals something else.

| Tier | Trigger | Output | Time |
|---|---|---|---|
| **Sketch** | "Quick take on…", "TL;DR…", "Just the gist of…" | 3–4 paragraphs, 2–3 sources, no formal sections | ~1 min |
| **Brief** | "Research X," "What's the deal with…," "Look into…" | Structured report, 4–6 sources, recommendation | ~3–5 min |
| **Report** | "Deep dive on…," "Full investigation," "I'm making a real decision about…" | Long-form report, 8–12 sources, alternatives, risk analysis | ~10+ min |

If the request is ambiguous and the stakes feel high (a buying decision, a hiring choice, a public claim the user will make), ask once: "Quick sketch, working brief, or full report?" If it feels low-stakes, just deliver a Brief.

## Source discipline

This is the part most research gets wrong. The internet in 2026 is heavily SEO-optimized and AI-generated; surface-skimming returns plausible-sounding garbage. Apply this filter:

**Tier 1 sources (always check):**
- Primary documents — official product pages, GitHub repos, regulatory filings, court records, academic papers, original interviews.
- The thing or person itself — actually read the README, the docs, the policy text, the contract, the changelog.

**Tier 2 sources (use with care):**
- Recent news from outlets with named editors and a corrections policy (Reuters, AP, the FT, the major trades for the field).
- Practitioner-written content — engineers writing about the tools they use, lawyers writing about cases they argued, founders writing about their own companies (with awareness that they're selling).
- Forum discussion where people post under stable identities (Hacker News, niche subreddits, professional Discords).

**Tier 3 sources (cross-reference only, never load-bearing):**
- AI-generated summary content (Wikipedia is fine for orientation; AI-spam content farms are not).
- Listicle/SEO articles ("Top 10 X for 2026") — fine for surfacing candidates, useless for evaluating them.
- Vendor marketing pages without independent verification.

For a Brief, get at least 4 sources, with at least 2 from Tier 1. For a Report, 8+ sources, with at least 4 from Tier 1. Cross-reference any specific claim — pricing, dates, counts, capabilities — against a second source before stating it as fact.

If sources disagree, say so. "Sources disagree on X — [Source A] says Y, [Source B] says Z, the divergence is unresolved" is more useful than picking one and pretending.

## What to investigate

Adjust by topic type. Use this as a checklist, not a script.

**Product / tool / service:** what does it actually do, what does it cost, who uses it, what do they say a year in (not at launch), what's the alternative, who owns the company, is it actively maintained.

**Person:** what have they actually shipped, who funds or employs them, what do peers say (not their own marketing), what is their specific track record on the question that matters here.

**Company:** business model, funding history, headcount trajectory, lawsuits and regulatory actions, leadership turnover, recent press, customer reviews on Glassdoor / G2 / Trustpilot — read for patterns, not stars.

**Technology / framework:** maintainer activity (commits, releases, issue response), production users, performance vs alternatives, common failure modes, how it ages (is the 2-year-old version still supported?).

**Decision** ("should I do X"): the case for, the case against, who has done it and what happened, what the user would lose if they skip, what they would lose if they commit and it doesn't work.

**Comparison ("X vs Y"):** the dimensions that actually matter to *this* user (not a generic feature matrix), the breakpoint where one beats the other, the wrong reasons people pick each.

## Output formats

### Sketch

No headers, no table of contents. Three or four paragraphs.

```
[Topic] in plain terms: [what it is, who made it, why it exists].

[The shape of the thing — pricing/scale/posture, one paragraph].

[The honest take — what it's good at, where it falls short, who it's for].

Sources: [Source 1 with URL] · [Source 2 with URL] · [Source 3 with URL]
```

### Brief

```markdown
# [Topic]

**One-line:** [The most useful 15-word summary you can write].

**Verdict:** [Worth using / Worth watching / Skip / It depends — and one sentence on why].

## What it is

[2–3 sentences. What it does, who made it, when it appeared, current state].

## How it works / what it costs

[Pricing, scale, distribution, the mechanical facts].

## What's good

- [Specific strength, with the source or evidence inline]
- [Specific strength]
- [Specific strength]

## What's not

- [Specific weakness, with evidence]
- [Specific weakness]

## Who it's for / who should skip

[2–3 sentences. Concrete. "Best for [specific user] doing [specific job]. Skip if [specific situation]."]

## Open questions

[Things the research couldn't answer. Naming them is the honest thing — and helpful.]

## Sources

- [Title](URL) — [tier, one-line note on what it covered]
- [Title](URL) — [tier, note]
- [Title](URL) — [tier, note]
```

### Report

Same shape as Brief, but with these added sections after **What's not**:

- **Alternatives** — table comparing 2–4 substitutes on the dimensions that matter
- **Track record** — what's happened with this thing over the last 1–3 years (releases, incidents, leadership changes, customer wins/losses)
- **Risks** — the realistic failure modes; what you'd be exposed to by committing
- **Recommendation** — direct, named, with a specific path forward (e.g., "Run a 30-day pilot with [scope]; if [metric] hits [threshold], commit")

## Fact-checking pass

Before delivering any report, run this final pass:

1. **Every number.** Pricing, dates, counts, percentages — re-verify against a source. Numbers are where credibility lives or dies.
2. **Every name.** People, products, companies — confirm spelling and role. Misnaming a CTO is more damaging than missing a feature.
3. **Every claim that begins "X said" or "X reported."** Hyperlink to the actual source; never paraphrase a paraphrase.
4. **Every recommendation against a competitor.** Make sure the user has the criticism in context — naming a flaw without scope ("It's slow") is unhelpful and possibly unfair.

If a claim doesn't survive the pass, drop it from the report or label it explicitly as "unverified."

## Hard rules

- **Sources or it didn't happen.** Every non-trivial factual claim needs a source link inline. A report without sources is an opinion in formal clothing.
- **Date everything that decays.** Pricing, headcount, version numbers, "supported until X" — note the date observed. Research goes stale fast in 2026.
- **Disagree with the source if the source is wrong.** If marketing copy says "fastest in class" and your investigation finds otherwise, write the truth — not a both-sides hedge.
- **Honest takes win.** If a product is mediocre, write that it's mediocre. The user is paying for judgment, not promotion. The default tone is direct, not laudatory.
- **Skip the dead.** If a product has not shipped a release in 18 months, the issue tracker is graveyard, or the maintainer is gone — say so up front. Saved hours.
- **Quote, don't paraphrase, when accuracy matters.** For policy text, contract language, or a specific claim someone made publicly — use the exact words and link them.
- **Open questions are a feature.** Saying "I couldn't determine X" is more useful than guessing. Name what you don't know.

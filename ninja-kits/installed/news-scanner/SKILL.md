---
name: news-scanner
description: Given a company / topic / person, return the most material news from the last 7-30 days. Filters out fluff (re-published press releases, PR-driven coverage, irrelevant mentions); surfaces what actually moved or changed. Agent-triggered primitive composed by /competitor-deep-dive, /competitor-scan, /partner-research, /risk-scan, /opportunity-scan. User-invocable when [FOUNDER NAME] asks "what's the latest on X", "any news on X", "what's happened recently with X".
---

# /scan-news-on — Recent News Sweep

A focused web search primitive: given a subject, find what's *actually* new and material. Not a Google News dump — a filtered, materiality-ranked summary.

## Input
- **Subject** — company name, person name, topic, product, industry segment
- **(Optional) Window** — default 30 days; pass 7 / 14 / 90 for narrower / wider
- **(Optional) Lens** — competitor / partner / regulatory / market — narrows what counts as material

## Tools — search infrastructure options

The skill works with Claude Code's built-in **WebSearch** by default, but if available, prefer dedicated MCP search servers — they're better-tuned for citation-heavy AI workflows.

### Recommended MCP search servers (in order of fit for this primitive)

| MCP | Best for | Notes |
|---|---|---|
| **[Tavily MCP](https://github.com/tavily-ai/tavily-mcp)** | Citation-heavy news research | Built for AI agents; 1,000 free queries/mo on free tier; returns clean snippets + sources |
| **[Perplexity MCP](https://docs.perplexity.ai/)** | Conversational answers with sources | Sonar API; great when "summarize what's happening with X" is the task |
| **[Brave Search MCP](https://brave.com/search/api/)** | Zero-cost, general purpose | Includes dedicated news/image/video search endpoints and AI summarization; the "sweet spot" for most use |
| **[mcp-omnisearch](https://github.com/spences10/mcp-omnisearch)** | Unified access | One MCP, multiple providers (Tavily + Brave + Kagi + Exa); good if [CLIENT NAME] wants provider redundancy |

If none of these MCPs are configured, fall back to Claude Code's built-in WebSearch — it's fine, just less optimized for the citation/snippet pattern this primitive needs.

### When to escalate beyond search MCPs
- **Earnings/financial filings** — pair with the SEC EDGAR API or a finance-data MCP for public-company news
- **PR/press releases** — Cision/Meltwater APIs if [CLIENT NAME] has subscriptions
- **Social media posts** — X/LinkedIn data is paywalled; use WebFetch on public profile URLs only

## Method — three-pass search

### Pass 1 — Direct news search
Query: `<subject> news` filtered to the window. Use WebSearch with recency-biased phrasing ("latest", "recent", "this month", or include the current month/year).

### Pass 2 — Surface beyond press-release filler
Most news on a company is amplified press releases. The signal lives in:
- Earnings / financial reports (for public companies)
- Job postings (signals direction; check careers page)
- Product/feature launches with real customer-visible changes
- Leadership changes (departures > arrivals usually more informative)
- Lawsuits / regulatory actions
- Acquisitions or fundraising

### Pass 3 — Materiality filter
For each surfaced item, ask: *does this change anything actionable for [CLIENT NAME]?*
- **Material** — affects positioning, pricing, market, competitive dynamic, regulatory landscape
- **Background** — happened, but doesn't change anything for us. Drop.

## Output

```
# News on <subject> — last <N> days

## Material moves
- **<YYYY-MM-DD> — <headline>** ([source](url))
  <one-sentence summary of what actually changed>
  *So what for [CLIENT NAME]:* <one sentence on the implication>

- **<YYYY-MM-DD> — <headline>** ([source](url))
  <…>

## Background (FYI, not actionable)
- <YYYY-MM-DD>: <one-line headline + source>

## Nothing material found
<If the search returns nothing material in the window — say so explicitly. A quiet period is a real signal.>
```

## Query patterns by subject type

| Subject type | Query patterns |
|---|---|
| **Public company** | `<name> earnings`, `<name> Q<quarter> results`, `<name> announces`, `<name> press release` |
| **Private company** | `<name> raised`, `<name> launches`, `<name> CEO`, `<name> news` |
| **Person** | `<name> joins`, `<name> announces`, `<name> interview` |
| **Industry / topic** | `<topic> trend`, `<topic> 2026`, `<topic> regulation`, `<topic> shutdown` |
| **Product** | `<product> review`, `<product> launch`, `<product> vs`, `<product> alternatives` |

Cap at **5 search queries** total. More usually returns the same hits via different framings.

## When to call this primitive

- Inside `/competitor-scan` — refresh news per tracked competitor
- Inside `/competitor-deep-dive` — populate the "recent moves" section
- Inside `/partner-research` — recent news context on a potential partner
- Inside `/risk-scan` — regulatory / market-shift signals
- Inside `/opportunity-scan` — market-shift signals indicating new windows

## Anti-patterns

- **Don't paste a Google News dump.** Filter by materiality.
- **Don't repeat press releases as news.** A company announcing they're great isn't news; a customer leaving them is.
- **Don't fabricate dates.** Every item must have a verifiable source URL.
- **Don't expand the window without being asked.** If the default 30 days is empty, that's information — don't widen to "find something."
- **Don't search more than 5 queries.** Diminishing returns; the model should know when to stop.

## Related primitives
- `/find-comparable-cases` — when looking for *historical* cases rather than recent news
- `/find-counterevidence` — news search is often where counterevidence lives

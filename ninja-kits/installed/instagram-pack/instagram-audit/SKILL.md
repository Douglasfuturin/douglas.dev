---
name: instagram-audit
description: Use when the user wants to audit their Instagram account, set up their CLAUDE.md, onboard for the first time, or get a comprehensive analysis of their account's content, performance, engagement, and voice. This is the first skill new users should run.
---

# Instagram Account Audit

Run a comprehensive audit of an Instagram account. Analyzes post formats, captions, content strategy, performance trends, voice/brand, and competitive landscape. Produces a detailed audit report and auto-generates a customized `CLAUDE.md` tailored to the creator's style.

This is the **onboarding skill** — the first thing a new user runs. It turns a blank `CLAUDE.md` template into a fully personalized account config that powers every other skill.

---

## Process

### Step 1: Gather Account Info

Read `CLAUDE.md` for any existing info (name, Instagram handle, Metricool details).

Ask the user for anything missing:
1. **Name** — What should Claude call them?
2. **Instagram handle** — e.g., `@username`
3. **Metricool blog ID and timezone** (optional) — needed for deep analytics. If they don't use Metricool, the audit still works using web search and public data.
4. **Anything else they want Claude to know** — business context, goals, what they're building toward.

### Step 2: Account Discovery

Before launching the deep dives, gather the baseline data that all agents need. Use Metricool MCP tools as the primary data source for Instagram analytics, post data, and engagement metrics.

#### Data gathering steps:

1. **Pull account analytics** via Metricool `get_analytics` with `network: "instagram"` — followers, reach, impressions, engagement over the last 6 months.
2. **Pull all recent posts** via Metricool Instagram endpoints — full post list with captions, reach, engagement, saves, shares, dates, post types.
3. **Pull competitor data** if configured via `get_network_competitors` with `network: "instagram"`.
4. **If Metricool is not connected:** Fall back to web search and public data.

Save all discovered data as context for the sub-agents.

### Step 3: Parallel Deep Dives

Launch **5 sub-agents in parallel** using the Task tool (`subagent_type: "general-purpose"`). Each agent gets the account data from Step 2 plus a focused analysis brief. Each agent returns a structured findings report.

All agents should use the Metricool MCP tools when available, and fall back to web search when not.

---

#### Agent 1: Content Format Analyst

**Brief:** Analyze the content formats — how the account's posts look and perform by type.

**Tasks:**
- Categorize all posts by format: carousel, Reel, single image, Story highlight, etc.
- For each format, calculate: average reach, engagement rate, saves, shares
- Identify which formats consistently outperform others
- Analyze carousel-specific patterns:
  - Average slide count for top performers
  - Slide 1 (cover) style — text-heavy, image-only, bold statement, etc.
  - CTA placement (last slide, caption, both)
- Analyze Reels patterns:
  - Average length for top performers
  - Hook style in first 3 seconds
  - Use of text overlays, music, transitions
- Identify the **3 best-performing posts** and explain why they worked
- Identify **3 content format mistakes** the account makes repeatedly

**Return:** Structured findings with specific examples and recommendations.

---

#### Agent 2: Content Strategist

**Brief:** Analyze what the account posts — topics, themes, pillars, and gaps.

**Tasks:**
- Categorize every post by topic/content pillar (group similar posts together)
- Identify the account's **3-5 natural content pillars** based on what they've actually posted
- For each pillar: count posts, average reach, average engagement, and whether it's growing or shrinking
- Track posting frequency over time — how consistent are they? Any gaps?
- Identify the **single most successful content theme** on the account
- Look for **missed opportunities** — topics the audience clearly wants (high engagement on some posts) that the creator hasn't explored further
- Analyze caption patterns — length, CTA style, hook effectiveness
- Note any content pivots or shifts in direction

**Return:** Content pillar breakdown, format analysis, frequency report, and strategic recommendations.

---

#### Agent 3: Performance Analyst

**Brief:** Analyze the numbers — what's working, what's not, and where the account stands.

**Tasks:**
- Pull `get_analytics` for Instagram over the last 6 months — followers, reach, engagement metrics
- Calculate account benchmarks:
  - Median reach per post (more useful than average — avoids outlier skew)
  - Average engagement rate (likes + comments + saves + shares / reach)
  - Follower growth rate
  - Save rate and share rate (key distribution metrics)
- Identify the **top 5 posts** by reach and analyze what they have in common
- Identify **underperformers** — posts that got significantly less reach than the account average. What went wrong?
- Look for **growth trends** — is the account growing, flat, or declining? Any inflection points?
- Analyze if there's a **best day/time** pattern for high-performing posts
- Calculate how the account compares to typical benchmarks for its size

**Return:** Performance dashboard summary, benchmarks, top/bottom performers, growth trajectory, and data-driven recommendations.

---

#### Agent 4: Voice & Brand Analyst

**Brief:** Extract the creator's authentic voice, tone, and brand identity from their **Instagram content only**.

**Tasks:**
- Read the captions of all recent posts — note language patterns, recurring phrases, tone
- Read the account bio and highlights
- Identify **voice characteristics:**
  - Formal vs. casual spectrum
  - Use of humor, sarcasm, or irreverence
  - First person vs. second person vs. third person
  - Sentence length — short and punchy vs. long and detailed
  - Vocabulary level — technical jargon vs. accessible language
  - Emotional tone — excited, calm, authoritative, friendly, contrarian
  - Emoji usage — which ones, how often
  - CTA patterns — "comment X", "save this", "share with..."
- Identify **anti-patterns** — things the creator clearly avoids
- Note their **unique angle** — what makes this creator different from others in the same niche?
- Extract any **catchphrases, signature lines, or recurring themes**
- Describe the creator's **brand in 2-3 sentences** — who they are, what they stand for, why someone would follow

**Return:** Voice profile with specific examples from Instagram content, brand summary, anti-patterns list, and unique differentiators.

---

#### Agent 5: Competitive Landscape

**Brief:** Map the competitive landscape — who else creates similar content, and what can we learn?

**Tasks:**
- Identify **5-8 competitors or similar accounts** in the same niche
- If Metricool competitors are configured: Pull `get_network_competitors` for Instagram
- For each competitor, note:
  - Handle, follower count, recent posting frequency
  - Their content focus — what do they post?
  - What's working for them — their top-performing recent posts
  - Their visual style and caption style — how does it compare?
  - Carousel vs. Reel vs. single image mix
- Identify **gaps in the competitive landscape** — topics or formats that competitors aren't covering well
- Identify **proven formats** from competitors that this account could adapt
- Note any competitors who are **growing fast** and what's driving it

**Return:** Competitor overview table, gap analysis, format opportunities, and strategic positioning recommendations.

---

### Step 4: Synthesize the Audit Report

Once all 5 agents return, combine their findings into a comprehensive audit report. Save this to:

```
audit/{date}-account-audit.md
```

**Audit report structure:**

```markdown
# Instagram Account Audit — {Account Name}
**Date:** {date}
**Audited by:** Claude Instagram

## Executive Summary
3-5 bullet points: the most important findings and #1 recommendation.

## Account Overview
Basic stats, current state, trajectory.

## Content Format Analysis
Post format performance, carousel patterns, Reel patterns, best/worst examples, recommendations.

## Content Strategy
Content pillars, theme analysis, posting frequency, missed opportunities.

## Performance Deep Dive
Benchmarks, top performers, underperformers, growth trends.

## Voice & Brand
Voice profile, brand identity, unique angle.

## Competitive Landscape
Competitor overview, gaps, opportunities.

## Top 10 Recommendations
Prioritized, actionable list. Most impactful first.
```

### Step 5: Generate the Customized CLAUDE.md

Using everything from the audit, **rewrite `CLAUDE.md`** with a fully personalized config. Follow this structure:

```markdown
# CLAUDE.md

## Role

You are {Name}'s Instagram assistant. Your primary job is helping {Name} write captions, design carousel concepts, plan Reels, optimize posting strategy, analyze Instagram performance, study competitors, and grow their Instagram following. Everything you do should be focused on making their Instagram content better and their account bigger.

## About {Name}

- **Name:** {Name} ({handle})
- **Company/Brand:** {if applicable}
- **Location:** {if known}
- **Niche:** {niche extracted from content analysis}
- **Background:** {brief bio from research}

## Instagram Account

- **Handle:** {handle}
- **Followers:** {count} (as of {date})
- **Status:** {active/dormant/growing — from performance analysis}
- **Content mix:** {carousel, Reels, single image breakdown}
- **Content direction:** {current and recommended direction}

## {Name}'s Voice & Tone

This applies to captions, carousel text, Reels scripts, Stories — everything.

### Core traits
{Extracted from Voice & Brand Analyst — specific, with examples}

### Never do this
{Anti-patterns extracted from their content}

## Instagram Strategy

### Content pillars
{From Content Strategist — the natural pillars identified}

### What's worked before
{From Performance Analyst — top performers and why}

### Opportunities
{From Competitive Landscape + Content Strategist — gaps and ideas}

## Carousel Design Style

{From Content Format Analyst — what their carousels look like, what works}

## Metricool Integration

- **Blog ID:** {if available}
- **Timezone:** {timezone}
- Always load preferences from `.claude/skills/instagram-analysis/preferences.md` before making Metricool API calls

## Working Preferences

- When writing captions, draft first and iterate. Don't over-ask upfront — get something on paper and refine.
- When planning content, validate with real data (engagement patterns, competitor analysis, audience signals).
- When analyzing performance, always compare against historical benchmarks.
- When suggesting post ideas, ground them in what's actually worked (data-driven) combined with current trends.
- Keep recommendations actionable. Data without "here's what to do" is useless.
```

**Important:** The voice section is the most critical part. Every other skill uses it to write in the creator's voice. Be specific — use real examples from their content, not generic descriptions.

### Step 6: Present to the User

Show the user:
1. **Executive summary** — the 5 most important findings
2. **Where files were saved** — audit report path and confirmation that CLAUDE.md was updated
3. **Top 3 quick wins** — things they can do immediately to improve
4. **The voice profile** — read it back so they can confirm it sounds right

Ask if they want to adjust anything in the CLAUDE.md — especially the voice section. This is their chance to correct anything that doesn't feel right.

### Step 7: Update Analysis Preferences

If Metricool is connected, also update `.claude/skills/instagram-analysis/preferences.md` with:
- Brand info (blog ID, timezone)
- Connected platforms
- Audience sizes
- Content performance benchmarks from the audit
- Session log entry

---

## Re-Running the Audit

The audit can be run again anytime. When re-running:
- Compare new findings against the previous audit report
- Highlight what's changed (growth, new content pillars, improved formats)
- Update CLAUDE.md with any new information
- Keep the previous audit report — rename it to `{date}-account-audit.md` so there's a history

---

## Output Files

```
CLAUDE.md                              — Customized account config (rewritten)
audit/{date}-account-audit.md          — Full audit report
.claude/skills/instagram-analysis/preferences.md — Updated Metricool preferences (if applicable)
```

---

## Notes

- **Metricool** is the primary data source for Instagram analytics, post data, and engagement metrics.
- The voice extraction is the hardest part to get right. Always ask the creator to review and correct the voice section.
- The audit should take 3-5 minutes depending on how much data is available.

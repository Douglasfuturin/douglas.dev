---
name: youtube-audit
description: Use when the user wants to audit their YouTube channel, set up their CLAUDE.md, onboard for the first time, or get a comprehensive analysis of their channel's packaging, content, performance, and voice. This is the first skill new users should run.
---

# YouTube Channel Audit

Run a comprehensive audit of a YouTube channel. Analyzes thumbnails, titles, content strategy, performance trends, voice/brand, and competitive landscape. Produces a detailed audit report and auto-generates a customized `CLAUDE.md` tailored to the creator's style.

This is the **onboarding skill** — the first thing a new user runs. It turns a blank `CLAUDE.md` template into a fully personalized channel config that powers every other skill.

---

## Process

### Step 1: Gather Channel Info

Read `CLAUDE.md` for any existing info (name, YouTube URL, Metricool details).

Ask the user for anything missing:
1. **Name** — What should Claude call them?
2. **YouTube channel URL or handle** — e.g., `@channelname` or a full URL
3. **Metricool blog ID and timezone** (optional) — needed for deep analytics. If they don't use Metricool, the audit still works using web search and public data.
4. **Anything else they want Claude to know** — business context, goals, what they're building toward.

### Step 2: Channel Discovery

Before launching the deep dives, gather the baseline data that all agents need. Use the **ScrapeCreators YouTube API** as the primary data source — it provides channel details, video lists, transcripts, and comments without rate limits or auth complexity.

#### ScrapeCreators API Reference

All endpoints use `GET` requests with header `x-api-key: $SCRAPECREATORS_API_KEY` (from `.env`).

| Endpoint | URL | Key Params |
|----------|-----|------------|
| **Channel Details** | `https://api.scrapecreators.com/v1/youtube/channel` | `handle` or `channelId` |
| **Channel Videos** | `https://api.scrapecreators.com/v1/youtube/channel-videos` | `handle`, `includeExtras=true` |
| **Channel Shorts** | `https://api.scrapecreators.com/v1/youtube/channel/shorts/simple` | `handle` |
| **Video Details + Transcript** | `https://api.scrapecreators.com/v1/youtube/video/transcript` | `url` (full YouTube URL) |
| **Video Comments** | `https://api.scrapecreators.com/v1/youtube/video/comments` | `url` |
| **Search** | `https://api.scrapecreators.com/v1/youtube/search` | `query`, `includeExtras=true` |

#### Data gathering steps:

1. **Pull channel details** via ScrapeCreators `/v1/youtube/channel` — subscribers, description, video count, join date, tags.
2. **Pull all channel videos** via `/v1/youtube/channel-videos?handle={handle}&includeExtras=true` — full video list with titles, views, likes, comments, dates, durations.
3. **Pull transcripts** for the top 5-10 videos via `/v1/youtube/video/transcript` — needed for voice analysis.
4. **If Metricool is connected:** Also call `get_youtube_videos` and `get_analytics` for deeper metrics (watch time, impressions, CTR) that ScrapeCreators doesn't provide.
5. **If no ScrapeCreators API key:** Fall back to Metricool data + web search.

**Important:** This is a YouTube-only audit. Do not research the creator's other social media platforms (Instagram, LinkedIn, X, etc.). The voice and brand analysis should be extracted entirely from YouTube content — titles, descriptions, transcripts, and the channel's about page. Other platforms are only relevant for competitor/niche research in rare cases.

Save all discovered data as context for the sub-agents.

### Step 3: Parallel Deep Dives

Launch **5 sub-agents in parallel** using the Task tool (`subagent_type: "general-purpose"`). Each agent gets the channel data from Step 2 plus a focused analysis brief. Each agent returns a structured findings report.

All agents should use the Metricool MCP tools when available, and fall back to web search when not.

---

#### Agent 1: Packaging Analyst (Thumbnails & Titles)

**Brief:** Analyze the visual packaging — how the channel's videos look in the feed.

**Tasks:**
- Pull the last 30 video thumbnails (download via the YouTube thumbnail URL pattern: `https://i.ytimg.com/vi/{VIDEO_ID}/maxresdefault.jpg`)
- Sort videos by view count. Compare thumbnails of the **top 10 performers** vs the **bottom 10**. What's different?
- Analyze thumbnail patterns:
  - Do they use faces? How prominently?
  - Text on thumbnails — how much, what font style, what colors?
  - Color palette — bright, dark, muted, saturated?
  - Composition — centered, rule of thirds, split layout?
  - Consistency — is there a recognizable visual brand?
- Analyze title patterns across all videos:
  - Average title length (characters)
  - Formats used (how-to, listicle, question, statement, challenge)
  - Power words and emotional triggers
  - Use of numbers, brackets, capitalization
  - Titles that over/under-performed relative to the channel average
- Identify the **3 best-packaged videos** (thumbnail + title combo) and explain why they work
- Identify **3 packaging mistakes** the channel makes repeatedly

**Return:** Structured findings with specific examples and recommendations.

---

#### Agent 2: Content Strategist

**Brief:** Analyze what the channel makes — topics, formats, pillars, and gaps.

**Tasks:**
- Categorize every video by topic/content pillar (group similar videos together)
- Identify the channel's **3-5 natural content pillars** based on what they've actually made
- For each pillar: count videos, average views, and whether it's growing or shrinking
- Analyze video lengths — what's the typical length? Do longer or shorter videos perform better?
- Track posting frequency over time — how consistent are they? Any gaps?
- Identify the **single most successful content format** on the channel
- Look for **missed opportunities** — topics the audience clearly wants (high engagement on some videos) that the creator hasn't explored further
- Note any content pivots or shifts in direction

**Return:** Content pillar breakdown, format analysis, frequency report, and strategic recommendations.

---

#### Agent 3: Performance Analyst

**Brief:** Analyze the numbers — what's working, what's not, and where the channel stands.

**Tasks:**
- If Metricool is available: Pull `get_analytics` for YouTube over the last 6 months — subscribers, views, engagement metrics
- Calculate channel benchmarks:
  - Median views per video (more useful than average — avoids outlier skew)
  - Average engagement rate (likes + comments / views)
  - Subscriber-to-view ratio
  - Views per subscriber (measures audience activation)
- Identify the **top 5 videos** by total views and analyze what they have in common
- Identify **underperformers** — videos that got significantly fewer views than the channel average. What went wrong?
- Look for **growth trends** — is the channel growing, flat, or declining? Any inflection points?
- Analyze if there's a **best day/time** pattern for high-performing uploads
- Calculate how the channel compares to typical benchmarks for its size (views/sub ratio, engagement rate, etc.)

**Return:** Performance dashboard summary, benchmarks, top/bottom performers, growth trajectory, and data-driven recommendations.

---

#### Agent 4: Voice & Brand Analyst

**Brief:** Extract the creator's authentic voice, tone, and brand identity from their **YouTube content only**.

**Tasks:**
- Read the titles and descriptions of all videos — note language patterns, recurring phrases, tone
- Read the channel's about page / description
- Analyze **transcripts** of the top 5-10 videos (from Step 2 data) — this is the richest source of voice data. Look at how they open videos, explain concepts, transition between topics, and close.
- Identify **voice characteristics:**
  - Formal vs. casual spectrum
  - Use of humor, sarcasm, or irreverence
  - First person vs. second person vs. third person
  - Sentence length — short and punchy vs. long and detailed
  - Vocabulary level — technical jargon vs. accessible language
  - Emotional tone — excited, calm, authoritative, friendly, contrarian
- Identify **anti-patterns** — things the creator clearly avoids (e.g., never uses emojis, never says "guys", never does clickbait)
- Note their **unique angle** — what makes this creator different from others in the same niche?
- Extract any **catchphrases, signature lines, or recurring themes**
- Describe the creator's **brand in 2-3 sentences** — who they are, what they stand for, why someone would subscribe

**Important:** Do NOT research other platforms (Instagram, LinkedIn, X, personal website). Extract voice entirely from YouTube content — titles, descriptions, transcripts, and channel about page. This keeps the analysis focused and avoids cross-platform noise.

**Return:** Voice profile with specific examples from YouTube content, brand summary, anti-patterns list, and unique differentiators.

---

#### Agent 5: Competitive Landscape

**Brief:** Map the competitive landscape — who else makes similar content, and what can we learn?

**Tasks:**
- Identify **5-8 competitors or similar channels** in the same niche. Search for: `"[niche/topic]" youtube channel`, look at related channels, check who appears in similar search results.
- If Metricool competitors are configured: Pull `get_network_competitors` for YouTube
- For each competitor, note:
  - Channel name, subscriber count, recent upload frequency
  - Their content focus — what do they make?
  - What's working for them — their top-performing recent videos
  - Their thumbnail/title style — how does it compare?
- Identify **gaps in the competitive landscape** — topics or formats that competitors aren't covering well
- Identify **proven formats** from competitors that this channel could adapt
- Note any competitors who are **growing fast** and what's driving it

**Return:** Competitor overview table, gap analysis, format opportunities, and strategic positioning recommendations.

---

### Step 4: Synthesize the Audit Report

Once all 5 agents return, combine their findings into a comprehensive audit report. Save this to:

```
workspace/{today}/audit/{channel-name}-audit.md
```

**Audit report structure:**

```markdown
# YouTube Channel Audit — {Channel Name}
**Date:** {date}
**Audited by:** Claude YouTube

## Executive Summary
3-5 bullet points: the most important findings and #1 recommendation.

## Channel Overview
Basic stats, current state, trajectory.

## Packaging Analysis
Thumbnail patterns, title analysis, best/worst examples, recommendations.

## Content Strategy
Content pillars, format analysis, posting frequency, missed opportunities.

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

You are {Name}'s YouTube assistant. Your primary job is helping {Name} research video topics, write scripts, optimize titles and thumbnails, analyze YouTube performance, study competitors, and grow their YouTube channel. Everything you do should be focused on making their YouTube content better and their channel bigger.

## About {Name}

- **Name:** {Name} ({handle})
- **Company/Brand:** {if applicable}
- **Location:** {if known}
- **Niche:** {niche extracted from content analysis}
- **Background:** {brief bio from web research}

## YouTube Channel

- **Channel ID:** {channel ID}
- **Subscribers:** {count} (as of {date})
- **Status:** {active/dormant/growing — from performance analysis}
- **Back catalog:** {summary of existing content library}
- **Content direction:** {current and recommended direction}

## {Name}'s Voice & Tone

This applies to scripts, titles, descriptions, community posts — everything.

### Core traits
{Extracted from Voice & Brand Analyst — specific, with examples}

### Never do this
{Anti-patterns extracted from their content}

## YouTube Strategy

### Content pillars
{From Content Strategist — the natural pillars identified}

### What's worked before
{From Performance Analyst — top performers and why}

### Opportunities
{From Competitive Landscape + Content Strategist — gaps and ideas}

## Thumbnail Style

{From Packaging Analyst — what their thumbnails look like, what works}

## Presentation Style

- **Accent Color:** {Primary brand color as hex, e.g., #00CB5A — extracted from thumbnail/brand analysis. Used for headings, emphasis, underlines, and circles in presentations.}

## Metricool Integration

- **Blog ID:** {if available}
- **Timezone:** {timezone}
- Always load preferences from `.claude/skills/youtube-analysis/preferences.md` before making Metricool API calls

## Working Preferences

- When writing scripts, draft first and iterate. Don't over-ask upfront — get something on paper and refine.
- When researching video topics, validate with real data (search volume, competitor analysis, audience signals).
- When analyzing performance, always compare against historical benchmarks.
- When suggesting video ideas, ground them in what's actually worked (data-driven) combined with current trends.
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

If Metricool is connected, also update `.claude/skills/youtube-analysis/preferences.md` with:
- Brand info (blog ID, timezone)
- Connected platforms
- Audience sizes
- Content performance benchmarks from the audit
- Session log entry

---

## Re-Running the Audit

The audit can be run again anytime. When re-running:
- Compare new findings against the previous audit report
- Highlight what's changed (growth, new content pillars, improved packaging)
- Update CLAUDE.md with any new information
- Keep the previous audit report — previous reports stay in their dated `workspace/{date}/audit/` folder so there's a history

---

## Output Files

```
CLAUDE.md                                           — Customized channel config (rewritten)
workspace/{today}/audit/{channel-name}-audit.md     — Full audit report
.claude/skills/youtube-analysis/preferences.md      — Updated Metricool preferences (if applicable)
```

---

## Notes

- **ScrapeCreators API** is the primary data source for YouTube channel/video data, transcripts, and comments. Requires `SCRAPECREATORS_API_KEY` in `.env`. Falls back to Metricool + web search if unavailable.
- **Metricool** provides deeper analytics (watch time, impressions, CTR, subscriber trends) that ScrapeCreators doesn't. Best results come from using both.
- **YouTube-only audit.** Do not crawl other platforms for voice/brand analysis. Extract everything from YouTube titles, descriptions, transcripts, and the channel about page.
- The voice extraction is the hardest part to get right. Always ask the creator to review and correct the voice section.
- Thumbnails from YouTube are served in AVIF format. The agents should convert to JPEG for analysis using Pillow with `pillow_avif`.
- The audit should take 3-5 minutes depending on how much data is available.

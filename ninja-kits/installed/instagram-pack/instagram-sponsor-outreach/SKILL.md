---
name: instagram-sponsor-outreach
description: Use when the user wants to find AI companies to pitch for sponsored Instagram posts. Researches trending AI startups across Reddit, Hacker News, YouTube, Instagram, and Product Hunt, builds a prospect list for user review, then drafts personalized outreach emails for approved companies.
---

# Sponsor Outreach — Find & Pitch AI Companies

Research trending AI companies, build a curated prospect list, and draft personalized sponsorship outreach emails. The user reviews and approves prospects before any emails are drafted.

---

## Process Overview

```
Step 1: Research  →  Find trending AI companies from multiple sources
Step 2: Prospect List  →  Compile into a structured document for user review
Step 3: User Review  →  User marks YES / NO / MAYBE on each prospect
Step 4: Draft Emails  →  Write personalized outreach for every approved company
Step 5: Send (future)  →  When email integration is available, send directly
```

---

## Step 1: Research — Find Companies

Search across multiple sources to find AI companies that are:
- **Trending right now** — being talked about, just launched, or recently funded
- **Relevant to the user's audience** — founders, developers, AI builders
- **Likely to sponsor creators** — have marketing budget, active on social, B2B or devtool focus

### Sources to Search (use as many as possible)

**Reddit** (via web search):
- Search `site:reddit.com` for recent posts in subreddits like r/artificial, r/machinelearning, r/LocalLLaMA, r/SaaS, r/startups, r/singularity
- Look for: "just launched", "built this", "Show HN"-style posts, product recommendations
- Search queries: `site:reddit.com AI tool launch 2026`, `site:reddit.com "just launched" AI`, `site:reddit.com best AI tools`

**Hacker News** (via web search):
- Search `site:news.ycombinator.com` for recent Show HN posts and trending AI companies
- Search queries: `site:news.ycombinator.com "Show HN" AI`, `site:news.ycombinator.com AI startup`

**Product Hunt** (via web search):
- Search `site:producthunt.com` for recently launched AI products
- Search queries: `site:producthunt.com AI tool 2026`, `site:producthunt.com AI launch`

**YouTube** (via web search):
- Look for AI tools being reviewed by tech YouTubers (Matt Wolfe, AI Jason, All About AI, etc.)
- Search queries: `AI tool review 2026 youtube`, `best AI tools youtube`

**Instagram / Creator Space** (via web search):
- Search for AI companies already doing sponsored content with creators
- Search queries: `AI company sponsored instagram post`, `AI startup influencer marketing`

**Crunchbase / Funding News** (via web search):
- Recently funded AI startups have marketing budget to spend
- Search queries: `AI startup funding 2026 seed series A`, `site:techcrunch.com AI startup funding`

**Tavily** (if TAVILY_API_KEY is set):
- Use Tavily for deeper web research if available
- Good for finding recent articles and mentions

### What to Collect for Each Company

For every potential prospect, gather:

| Field | Description |
|-------|-------------|
| **Company Name** | Full company name |
| **Website** | Homepage URL |
| **One-Liner** | What they do in 1 sentence |
| **Why They Fit** | Why this company's product matches the user's audience |
| **Funding / Stage** | Recent funding or company stage if known |
| **Buzz Source** | Where you found them (Reddit, HN, PH, YouTube, etc.) |
| **Contact** | Best contact — email from website, founder LinkedIn, or info@ |
| **Already Sponsoring?** | Any evidence they work with creators already |
| **Notes** | Anything else relevant (hot take angle, competitor comparison, etc.) |

### Research Tips

- **Prioritize companies with marketing budget.** Seed+ funded startups with a website that looks polished are more likely to pay for content.
- **Look for companies already doing creator marketing.** If they've sponsored other creators, they understand the value and are easier to close.
- **DevTools and B2B AI products are the sweet spot.** They need to reach exactly the audience the user has.
- **Skip giant companies** (OpenAI, Google, etc.) — they have agency relationships, not creator DM deals.
- **Skip pre-product companies.** If there's no website or product to try, skip them.

---

## Step 2: Build the Prospect List

Save the prospect list to `workspace/outreach/prospects.md`. Use this exact format so the user can easily scan and mark decisions:

```markdown
# Sponsor Prospects — [Date]

> Research sources: Reddit, Hacker News, Product Hunt, YouTube, Crunchbase
> Found: X companies | Researched on: [date]

---

## How to Review
Mark each company with your decision:
- ✅ **YES** — Draft an outreach email
- ❌ **NO** — Skip
- 🤔 **MAYBE** — Interested but not sure yet

---

## 1. [Company Name] — [one-liner]
**Website:** [url]
**Why they fit:** [1-2 sentences on audience match]
**Funding:** [stage/amount if known]
**Found on:** [source]
**Contact:** [email or LinkedIn]
**Already sponsoring creators?** [Yes/No/Unknown]
**Notes:** [angle ideas, hot takes, what makes this interesting]

**Decision:** ⬜ YES / NO / MAYBE

---

## 2. [Company Name] — [one-liner]
...
```

### List Guidelines

- **Aim for 10-20 prospects per batch.** Enough variety without overwhelming.
- **Rank by fit.** Put the strongest matches first.
- **Include angle ideas.** For each company, suggest what the carousel/post angle could be — this helps the user evaluate faster.
- **Be honest about fit.** If a company is borderline, say so in the notes.

---

## Step 3: User Review

After presenting the prospect list, wait for the user to review and mark their decisions. They'll come back with their YES/NO/MAYBE choices.

- **YES companies** → proceed to Step 4 (draft emails)
- **MAYBE companies** → ask if the user wants more research on these
- **NO companies** → skip entirely

If the user wants more prospects, repeat Step 1 with different search queries or sources.

---

## Step 4: Draft Outreach Emails

For each approved company, draft a personalized outreach email. Save all emails to `workspace/outreach/emails/[company-name].md`.

### Email Template Structure

Every email follows this structure but gets personalized per company:

```
Subject: [Short, specific — mention their product or what caught your attention]

Hey [Name/Team],

[1 sentence: who you are and your audience]

[1-2 sentences: what caught your attention about THEIR product specifically — show you actually know what they do]

[1 sentence: why your audience is a fit for them]

Would you be open to a sponsored carousel post?

What I'm thinking:
- Tweet-style carousel (X slides) breaking down [their product], [specific angle]
- Caption written in my voice with a CTA to [their site]
- Story set driving to the post (3-5 frames)

Rate: $[rate]

Quick stats:
- [follower count] followers — [audience description]
- [engagement rate]% avg engagement rate
- Top carousel: [top carousel stats]

Happy to send my media kit or hop on a quick call.

[signature]
```

### Personalization Rules

- **NEVER send a generic email.** Every email must reference something specific about the company's product.
- **Suggest a specific angle.** Don't just say "I'll make a carousel about you." Say "I'd break down your real-time voice API and show devs how to integrate it in 5 minutes."
- **Match the contact's level.** If emailing a founder, keep it casual and direct. If emailing a marketing team, be slightly more structured.
- **Use the stats from CLAUDE.md.** Pull the user's actual follower count, engagement rate, and top carousel stats.
- **Keep the rate consistent** unless the user specifies different rates for different companies.

### Email File Format

Each email file should include:

```markdown
# [Company Name] — Outreach Email

**To:** [email]
**Subject:** [subject line]
**Status:** Draft

---

[email body]

---

**Notes:** [any context — best time to send, follow-up strategy, etc.]
```

---

## Step 5: Present & Iterate

After drafting all emails:

1. **Show the user a summary** of all drafted emails with subject lines
2. **Let them review each one** — read the files inline so they can see them
3. **Make edits** as requested — tone, rate, angle, etc.
4. **Mark as ready to send** when approved

### Follow-Up Strategy

If the user asks about follow-ups:
- Wait 3-5 business days after initial send
- Follow-up should be short: "Hey [name], just bumping this — would love to create something for [product]. Let me know if you're open to it."
- Max 2 follow-ups. After that, move on.
- Save follow-up drafts in the same email file under a `## Follow-Up` section.

---

## Folder Structure

```
workspace/outreach/
├── prospects.md              # The master prospect list
├── emails/
│   ├── anam-ai.md           # Individual outreach emails
│   ├── company-two.md
│   └── ...
└── sent/                     # Move emails here after sending (future)
```

---

## Pulling User Stats for Emails

When drafting emails, pull the user's Instagram stats from:

1. **CLAUDE.md** — name, handle, audience description, niche
2. **Metricool API** (if configured) — real engagement rate, reach, impressions
3. **User-provided stats** — the user may provide specific numbers (follower count, top post stats)

If Metricool is configured, fetch fresh stats using:
- Blog ID and User Token from the MCP config or `.env`
- Hit the Instagram posts endpoint for recent performance data
- Calculate average engagement rate across recent posts

If Metricool is NOT configured, ask the user for their key stats:
- Follower count
- Average engagement rate
- Top carousel/post stats (views, interactions, saves)

Cache these in the prospect file header so you don't have to re-ask every time.

---

## General Guidelines

- **Quality over quantity.** 10 well-researched, high-fit prospects beat 50 random companies.
- **The user always reviews before emails are drafted.** Never skip the approval step.
- **Never send emails without explicit user approval.** Even when email integration is added, always confirm before sending.
- **Update the prospect list as outreach progresses.** Mark companies as contacted, responded, closed, etc.
- **Learn from responses.** If certain types of companies respond better, note that pattern for future batches.
- **Keep emails short.** Nobody reads long cold emails. The Anam email that was actually sent is the gold standard — study its structure and tone.

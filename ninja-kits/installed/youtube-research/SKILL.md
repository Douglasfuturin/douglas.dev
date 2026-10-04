---
name: youtube-research
description: Use when the user wants to research a YouTube video topic, plan video content, analyze competitors, understand their audience, or validate a video idea before production. Performs deep web research across all 4 phases of YouTube research.
---

# YouTube Video Research

Conduct thorough research for a YouTube video idea across 4 phases: Audience Understanding, Competitor Analysis, Gathering Content, and Validation. Each phase uses web search to gather real data and produce actionable insights.

## Process

1. **Get the video topic** from the user. Ask clarifying questions:
   - What's the video topic or working title?
   - Who is this for? (beginner, intermediate, advanced audience)
   - What's the channel niche? (tech, business, education, etc.)
   - Is there a specific angle or argument you want to make?
2. **Run all 4 research phases** below, presenting findings after each phase.
3. **Deliver a final research brief** that synthesizes everything into a clear, actionable document the user can use to script their video.

---

## Phase 1: Audience Understanding

**Goal:** Know exactly who you're making the video for, what they care about, and what language they use.

### Actions
- **Search for audience discussions** around the topic on Reddit, forums, and Q&A sites. Use queries like:
  - `"[topic]" site:reddit.com` — find real conversations
  - `"[topic]" questions beginners ask` — surface common pain points
  - `"[topic]" frustrating OR confusing OR "I don't understand"` — find emotional friction
- **Identify audience segments.** Who searches for this? What's their experience level? What adjacent topics do they care about?
- **Map the language they use.** Note exact phrases, slang, and terminology the audience uses (not industry jargon they wouldn't know).
- **Find the burning questions.** What are the top 5-10 questions people ask about this topic? Check:
  - Google's "People Also Ask" boxes
  - Reddit threads
  - Quora
  - YouTube comments on existing videos about this topic

### Deliverable
A summary containing:
- **Target viewer profile** — who they are, what they know, what they want
- **Top questions/pain points** — ranked by frequency and intensity
- **Language map** — exact phrases and terms the audience uses
- **Emotional drivers** — what frustrates, excites, or confuses them about this topic

---

## Phase 2: Competitor Analysis

**Goal:** Understand what already exists on YouTube for this topic so you can differentiate.

### Actions
- **Search YouTube for existing videos** on the topic. Use queries like:
  - `"[topic]" site:youtube.com` — find top-ranking videos
  - `[topic] YouTube video analysis` — find commentary and reviews
- **Analyze the top 5-10 results.** For each, note:
  - Title and thumbnail approach
  - View count and engagement (likes, comments)
  - Video length
  - Channel size (subscriber count)
  - Hook / first 30 seconds approach (if discernible from description or comments)
- **Identify content gaps.** What are commenters asking for that the video didn't cover? What angles are missing?
- **Search for related blog posts and articles** to see how written content covers the topic differently.
- **Check Google Trends** for the topic to understand search interest and seasonality.

### Deliverable
A summary containing:
- **Competitor landscape** — top videos, their performance, and their approach
- **Title patterns that work** — common structures in high-performing titles
- **Content gaps** — what's missing or underserved
- **Differentiation opportunities** — angles no one else is taking
- **Trend data** — is interest growing, stable, or declining?

---

## Phase 3: Gathering Content

**Goal:** Collect the raw material — facts, data, stories, examples, and expert opinions — that will make the video valuable.

### Actions
- **Search for authoritative sources** on the topic:
  - Recent studies, reports, or statistics
  - Expert opinions and quotes
  - Case studies and real-world examples
  - Historical context or origin stories
- **Find compelling stories and anecdotes.** Search for:
  - `"[topic]" case study OR example OR story` — real-world applications
  - `"[topic]" before and after OR results OR transformation` — proof of concept
- **Collect data points and statistics.** Numbers make videos more credible and shareable.
  - `"[topic]" statistics [current year]` — fresh data
  - `"[topic]" research study OR survey` — academic or industry research
- **Find counterarguments and nuance.** Every good video acknowledges the other side:
  - `"[topic]" criticism OR downside OR problem` — honest limitations
  - `"[topic]" myth OR misconception` — common misunderstandings to debunk
- **Identify quotable experts or creators** in this space who add credibility.

### Deliverable
A summary containing:
- **Key facts and statistics** — sourced and cited
- **Stories and examples** — 3-5 compelling narratives
- **Expert perspectives** — notable opinions from credible sources
- **Counterarguments** — honest limitations or alternative viewpoints
- **Unique insights** — anything surprising or non-obvious discovered during research

---

## Phase 4: Validation

**Goal:** Pressure-test the video idea before committing to production.

### Actions
- **Validate search demand.** Check if people are actively searching for this:
  - Search for the topic + "how to" / "what is" / "best" / "vs" variations
  - Look at Google Trends data and related queries
  - Check YouTube autocomplete suggestions for the topic
- **Assess competition level.** Can you realistically rank?
  - How many views do competing videos have?
  - Are they from huge channels or smaller creators?
  - Is there room for a new perspective?
- **Test title and angle options.** Based on all research, propose 3-5 title options and evaluate each:
  - Does it contain a clear benefit or curiosity gap?
  - Does it match the language the audience actually uses?
  - Is it differentiated from existing videos?
- **Score the video idea** on:
  - **Search demand** (1-10): Are people looking for this?
  - **Competition** (1-10): Can you stand out? (10 = low competition, easy to rank)
  - **Expertise fit** (1-10): Can the creator credibly speak on this?
  - **Evergreen potential** (1-10): Will this video get views for months/years?
  - **Shareability** (1-10): Would someone send this to a friend?

### Deliverable
A summary containing:
- **Search demand assessment** with supporting evidence
- **Competition analysis** — realistic ranking potential
- **3-5 title options** ranked by potential
- **Video idea scorecard** — the 5 scores above with brief justifications
- **Go / Iterate / Kill recommendation** — honest assessment of whether to proceed, refine the angle, or move on

---

## Final Research Brief

After all 4 phases, compile a single document with:

1. **Video Concept** — one-sentence summary of the video
2. **Target Viewer** — who this is for and why they'll click
3. **Recommended Title** — top pick from validation phase
4. **Key Talking Points** — the 5-7 most important points to cover, in order
5. **Supporting Evidence** — stats, stories, and examples to include
6. **Differentiation** — what makes this video different from what exists
7. **Risks and Mitigations** — potential issues and how to address them
8. **Recommended Video Length** — based on competitor analysis and content depth
9. **Suggested Hook** — a compelling opening based on audience pain points

## Output: Save Research Document

After completing all 4 phases and the final research brief, **always save the complete research to a markdown file**.

### File Location & Naming
- Save to: `workspace/{today}/research/{topic-slug}.md` (use today's date in YYYY-MM-DD format for `{today}`. For example, if today is 2026-02-18, save to `workspace/2026-02-18/research/{topic-slug}.md`)
- Create the `workspace/{today}/research/` directory in the project root if it doesn't exist
- Use a descriptive kebab-case slug (e.g., `claude-code-for-marketing.md`, `react-vs-nextjs-2026.md`)

### Document Structure
The saved file should contain the **complete research** in this order:

1. **Header** — Title, date, status (Go/Iterate/Kill), overall score
2. **Executive Summary** (the Final Research Brief) — Video concept, target viewer, recommended titles, suggested hook, recommended length, key talking points, supporting evidence, differentiation, scorecard, risks & mitigations
3. **Full Research** — All 4 phases with complete findings:
   - Phase 1: Audience Understanding (profile, questions, language map, emotional drivers)
   - Phase 2: Competitor Analysis (landscape table, title patterns, content gaps, differentiation, trends)
   - Phase 3: Content Gathering (stats, stories, use cases, counterarguments, expert perspectives)
   - Phase 4: Validation (demand, competition, title options, scorecard)
4. **Key Sources** — All URLs referenced throughout the research, collected at the bottom

### Formatting Rules
- Use proper markdown with headers, tables, bullet points, and bold text
- All statistics and claims must include source URLs as markdown hyperlinks
- Include the competitor landscape as a markdown table
- Include the video idea scorecard as a markdown table
- The document should be self-contained — someone reading it without context should understand everything

After saving, tell the user where the file was saved and offer to proceed to scripting.

---

## Guidelines

- Always cite sources with URLs when presenting research findings.
- Prioritize recency — favor data and examples from the last 12 months when possible.
- Be honest. If the research reveals the idea is weak, say so. A killed idea saves hours of production time.
- Present findings in a scannable format — bullet points, bold key phrases, clear headers.
- If the user has a specific channel or brand, tailor recommendations to their existing audience and style.
- Always run web searches directly (not via sub-agents) to avoid permission issues with delegated tools.

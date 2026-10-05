---
name: youtube-description
description: Use when the user wants to write a YouTube video description, generate a description for a video they're uploading, or optimize an existing description. Produces SEO-rich, structured descriptions with timestamps, links, and keyword coverage.
---

# YouTube Description Writer

Generate structured, SEO-optimized YouTube descriptions that drive clicks, surface in search, and give viewers everything they need. Every description follows a consistent template tuned for your channel.

## Process

### Step 1: Gather Context

You need these inputs. Pull from what's available — script, title, topic — and only ask for what's missing:

1. **Video title** (required) — the final title being used
2. **Video topic / summary** — what the video covers. If a script exists in `workspace/`, read it instead of asking.
3. **Timestamps** — either provided by the user, pulled from the script's section headers, or ask the user to provide them after editing
4. **Links** — any specific tools, repos, products, or resources mentioned in the video
5. **CTA** — what should the viewer do? (subscribe, comment, check a link, join a community)

**Don't ask for things you can figure out.** If there's a script, extract the summary, key points, and section structure from it. If there's a title, match the description's tone and angle to it.

### Step 2: Write the Description

Follow the **Description Template** below. Write in the creator's voice from CLAUDE.md — direct, conversational, no fluff.

### Step 3: Present to User

Show the full description formatted and ready to copy-paste into YouTube Studio. Call out:
- Total character count (YouTube cap is 5,000 characters)
- Number of timestamps
- Keywords included
- Any placeholder links that need to be filled in

### Step 4: Iterate

If the user wants changes, edit and re-present. Common adjustments:
- Add/remove timestamps after final edit
- Swap links
- Adjust keyword density
- Change the hook paragraph

---

## Description Template

Every description follows this structure. All sections are required. The description should feel **dense and complete** — like a mini landing page for the video. Aim for 2,500-4,000 characters total.

```
[HOOK PARAGRAPH — 2-3 sentences, result-first, specific numbers]

[DETAIL PARAGRAPH — 3-5 sentences, what they'll see, key features/reveals, real examples]

[VALUE PROP + CTA LINE — punchy contrast + "let me show you how it works"]

⏱️ TIMESTAMPS:
[timestamps — 8-15 entries, starting at 00:00]

🛠️ [TOPIC-SPECIFIC HEADER]:
[links directly related to the main subject of the video — repos, tools built, resources shown]

💻 INSTALL / GET STARTED:
[how to get the tools mentioned — Claude Code, VS Code, etc.]

🔗 TOOLS MENTIONED IN THIS VIDEO:
[every tool, platform, or product referenced]

🎯 [CONTENT-SPECIFIC SECTION — optional but encouraged]:
[bullet list of key concepts, features, or takeaways — gives the description density and SEO value]

👨‍💻 ABOUT ME:
[2-3 sentence bio in the creator's voice + social links from links.md]

[SEO PARAGRAPH — "This video covers:" format, comma-separated keyword phrases]

[HASHTAGS — 5-8 hashtags]
```

### Section-by-Section Rules

#### 1. Hook Paragraph (2-3 sentences)

The first 2-3 lines are **critical** — they show up in search results and above the "Show more" fold on YouTube. Front-load the value.

Rules:
- First sentence = what you built / did / discovered, with specific numbers. Lead with the result.
- Second sentence = specific details that prove it's real (features, outcomes, metrics)
- Third sentence (optional) = the "all from one ___" or "one install command" punchy closer
- No generic openers ("In this video I show you..."). Start with the thing itself.
- Include the primary keyword naturally in the first sentence

**Good example:**
> I built a Claude Code skill that generates 4 professional YouTube thumbnails in under 2 minutes — from just the video topic. 465 lines of thumbnail psychology, an 11-step automated pipeline, headshot compositing via Gemini, and parallel generation. All from a single markdown file.

#### 2. Detail Paragraph (3-5 sentences)

Expand on the specifics. What does the viewer actually see? Mention key features, real results, and honest assessments. This paragraph should be **longer and more detailed** than the hook — it's the meat.

Rules:
- Cover the 3-4 most interesting things in the video
- Include a real example or result ("It told me LinkedIn was too expensive at $1K/month")
- Be specific — names, numbers, frameworks, tools
- Mention what makes this different from what's already out there
- Include 1-2 secondary keywords naturally
- End with something honest — not everything has to be hype ("Honest, no fluff.")

#### 3. Value Prop + CTA Line (1-2 sentences)

Close the above-the-fold section with a punchy line. Use the **contrast pattern**: list what you DON'T need, then state what you DO need.

Rules:
- Format: "No X. No Y. No Z. One [simple thing]. Let me show you how it works."
- This line should make someone who's on the fence click play
- Always end with a forward-looking CTA ("Let me show you how it works." / "Full walkthrough below.")

#### 4. Timestamps

Format: `00:00 — Section name`

Rules:
- Start at `00:00` — YouTube requires this to enable chapters
- Use an em dash ` — ` (not a hyphen) between time and label
- Keep labels short (3-8 words) and descriptive
- Aim for 8-15 timestamps for a 10+ minute video
- If timestamps aren't available yet (video not edited), write `[TIMESTAMPS — add after final edit]` as a placeholder

#### 5. Link Sections (multiple, with emoji headers)

This is where descriptions get their density. Each link section gets its own **emoji + descriptive header**. Don't lump everything under one generic "Links" section.

**Required sections:**

- **🛠️ [TOPIC-SPECIFIC]:** — The main thing from the video. Name it specifically: "🛠️ THE THUMBNAIL SKILL:", "🛠️ INSTALL CLAUDE ADS:", "🛠️ GET THE TEMPLATE:". This is the #1 link people are looking for.
- **💻 INSTALL / GET STARTED:** — How to get the underlying tools. Claude Code install link, VS Code, docs.
- **🔗 TOOLS MENTIONED IN THIS VIDEO:** — Every tool, API, platform, or product shown or referenced. Even if it's a competitor or "what I used to use."

**Optional sections (use when relevant):**

- **🎯 KEY CONCEPTS / WHAT'S INSIDE:** — Bullet list of frameworks, features, or takeaways. Great for SEO density and for viewers scanning the description. Use `►` bullets.
- **🔗 RELATED PROJECTS:** — Other repos, skills, or companion tools.
- **🌐 WEBSITES / DEMOS:** — Sites shown in the video.

Format for all link sections:
```
► Label: https://...
► Label: https://...
```

#### 6. About Me Section

A **👨‍💻 ABOUT ME:** section appears in every description. 2-3 sentences in the creator's voice (from CLAUDE.md), followed by social links with emoji bullets (from `links.md`).

Read the bio from CLAUDE.md and the social links from `links.md`. Update `links.md` if links change.

#### 7. SEO Paragraph

A single paragraph starting with **"This video covers:"** followed by a comma-separated list of keyword phrases.

Rules:
- Start with "This video covers:" — this is the format that works
- List 15-25 keyword phrases, comma-separated
- Each phrase should be a real search term someone might type
- Include the main topic, related tools, the format, the audience, the year
- End with a period after the last phrase
- Place after the About Me section (deep below the fold — purely for the algorithm)

**Example:**
> This video covers: Claude Code skills, Claude Code tutorial, AI thumbnail generator, YouTube thumbnail design, thumbnail psychology, Gemini API image generation, headshot compositing, parallel AI agent execution, Claude Code markdown skills, AI tools for YouTube creators, thumbnail automation, desire loop framework, visual stun gun elements, competitive thumbnail research, AI-powered creative workflow, YouTube production automation 2026, how to build Claude Code skills, and solo creator AI tools.

#### 8. Hashtags (5-8)

Rules:
- 5-8 hashtags. YouTube shows the first 3 above the title — choose those carefully.
- First 3 hashtags = highest-value, most searchable terms for this video
- Mix broad terms (#AITools) with specific ones (#ClaudeCodeSkills)
- Include tool-specific hashtags when relevant (e.g., `#ClaudeCode` if the video involves Claude Code)
- Format: `#PrimaryTopic #ToolName #BroadNiche #SpecificTopic #YouTubeCreator`

---

## Voice Rules for Descriptions

- **Direct.** No throat-clearing. First sentence = the thing.
- **Specific.** Numbers, names, tools. Not "a cool AI tool" — "Gemini 3 Pro generating 4 concepts in parallel."
- **No hype words.** Don't say "insane," "game-changing," "revolutionary." Let the specifics speak.
- **Short paragraphs.** 2-4 sentences max per block. YouTube descriptions are scanned, not read.
- **Match the creator's voice from CLAUDE.md** — use their natural language patterns and style
- **Sentence fragments are fine.** "No subscriptions. No dashboards. One markdown file." reads better than a full sentence.

---

## Character Limits

- **YouTube description max:** 5,000 characters
- **Above the fold (visible before "Show more"):** ~200 characters on mobile, ~300 on desktop
- **Target total length:** 2,500-4,000 characters. The description should feel dense and complete — like a mini landing page. More is better here as long as every section earns its place.
- **Timestamps and link sections don't count** against the "too long" feel — viewers expect and appreciate structure

---

## Standing Links File

Store the creator's recurring links in `.claude/skills/youtube-description/links.md`. Read this file before every description. Update it when links change.

If `links.md` doesn't exist, create it by asking the creator for:
- Social media links (YouTube, Instagram, X/Twitter, LinkedIn)
- Website / company link
- Community link (if any)
- Standard tools they use and want to promote

---

## Quality Checklist

Before presenting the description:

- [ ] **Hook paragraph front-loads value** — first sentence is the result, not the setup
- [ ] **Primary keyword in first sentence** — critical for YouTube search
- [ ] **Above the fold is compelling** — would you click "Show more" after reading the first 2 lines?
- [ ] **Timestamps start at 00:00** — required for YouTube chapters
- [ ] **Multiple link sections with emoji headers** — not one generic "Links" dump
- [ ] **About Me section present** — 2-3 sentences + social links
- [ ] **All links are present** — no broken or missing URLs (placeholders flagged)
- [ ] **SEO paragraph uses "This video covers:" format** — comma-separated keyword phrases, 15-25 terms
- [ ] **Description is 2,500-4,000 characters** — dense and complete, not thin
- [ ] **5-8 hashtags** — first 3 are the most searchable terms
- [ ] **Under 5,000 characters** — YouTube's hard limit
- [ ] **No hype words** — no "insane," "game-changing," "revolutionary"
- [ ] **Matches the creator's voice** — consistent with CLAUDE.md voice profile

---

## Output Format

Save completed descriptions to: `workspace/{today}/descriptions/{video-slug}.md`

Present the raw text (ready to copy-paste) AND the formatted version with notes.

---

## Examples

### Strong Description (competitor reference — note what works)

```
I built 12 Claude Code skills that replace your ad agency - a free AI ad
audit tool with 190 PPC checks across 6 platforms.

6 Claude Code agents run your paid advertising audit in parallel. Google Ads,
Meta Ads, LinkedIn, TikTok, Microsoft - all at once. You get an Ads Health
Score, a PDF report with charts you can send to clients, strategic ad
planning with 11 industry templates, and budget-aware recommendations. It
told me LinkedIn was too expensive at $1K/month and went Meta-only instead.
Honest, no fluff.

No subscriptions. No dashboards. No agency retainer. One install command.
Let me show you how it works.
```

**Why this works:**
- First sentence = the result (12 skills, 190 checks, 6 platforms)
- Specific numbers throughout (not "a bunch of checks" — "190 PPC checks")
- Real example baked in ("told me LinkedIn was too expensive at $1K/month")
- Punchy value prop closing ("No subscriptions. No dashboards. One install command.")
- Primary keyword ("Claude Code skills") in the first sentence

### Weak Description (what to avoid)

```
Hey guys! In today's video I'm going to show you something really cool that
I've been working on. I think you're going to love it. Make sure to like and
subscribe and hit that notification bell!

In this video we cover how to use AI for marketing. It's a really powerful
tool and I think everyone should check it out. Link in the description below.
```

**Why this fails:**
- Generic opener ("Hey guys!")
- No specifics — what is the thing? What does it do?
- "Really cool" and "really powerful" say nothing
- CTA before any value is delivered
- "Link in the description below" — you ARE the description

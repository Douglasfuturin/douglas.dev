---
name: youtube-init
description: Use when setting up Claude YouTube for the first time. Gathers channel info, runs a full audit, generates all personalized config files, then removes itself.
---

# YouTube Init

One-time onboarding command for new Claude YouTube users. Gathers channel info, runs the full audit, generates every personalized file the skills need, and then self-destructs.

**This skill should only run once.** After it completes, it deletes itself.

---

## Process

### Step 1: Welcome & Gather Info

Print a welcome message:

```
Welcome to Claude YouTube! Let's get your channel set up.

This will take about 5 minutes. I'll analyze your channel, extract your voice,
and generate all the config files so every skill knows who you are.
```

Ask the user for:

1. **Name** — What should Claude call you?
2. **YouTube channel URL or handle** — e.g., `@channelname` or a full URL
3. **Social links** — YouTube, Instagram, X/Twitter, LinkedIn, website (whatever they have)
4. **Tools they use and want to promote** — e.g., Claude Code, Cursor, specific frameworks
5. **Community link** (optional) — Discord, Skool, newsletter, etc.
6. **Metricool blog ID and timezone** (optional) — needed for deep analytics. Skip if they don't use Metricool.
7. **Brief background** — what they do, what their channel is about, any goals

### Step 2: Run the Full Audit

Invoke the `/youtube-audit` skill. Pass it all the info gathered in Step 1.

The audit handles:
- Channel discovery via ScrapeCreators API
- 5 parallel deep-dive agents (packaging, content, performance, voice, competitive)
- Generating the audit report
- Writing the personalized `CLAUDE.md`
- Updating `preferences.md` (if Metricool is connected)

Wait for the audit to complete before continuing.

### Step 3: Generate Personalized Skill Files

After the audit finishes, generate the remaining personalized files that the audit doesn't cover.

#### 3a: Standing Links (`links.md`)

Create `.claude/skills/youtube-description/links.md` using the social links and tools gathered in Step 1.

Follow this format:

```markdown
# Standing Links

> Used in every YouTube description. Update here when links change.

## Tools I Use
► {Tool}: {URL}
► {Tool}: {URL}

## Connect
► YouTube: {URL}
► Instagram: {URL}
► X/Twitter: {URL}
► LinkedIn: {URL}
► Website: {URL}

## Community
► {Community platform}: {URL}

## Notes
- Update this file whenever links change — every description reads from it
- Add new tools as they become part of the standard stack
- Remove anything you stop using
```

Only include sections and links the user actually provided. Don't add placeholder lines — if they didn't give a LinkedIn URL, omit it entirely.

#### 3b: Brand Style Guide (`brand-style.md`)

Check if `.claude/skills/youtube-thumbnail/brand-style.md` was already populated by the audit. If it's still a stub ("auto-populated by the YouTube audit skill"), generate it now using the packaging analysis from the audit report. Include:

- Primary colors identified from their thumbnails
- Typography style (if detectable)
- Composition patterns
- Face/expression style
- Any consistent visual brand elements

#### 3c: Presentation Accent Color

Ensure the generated `CLAUDE.md` includes a **Presentation Accent Color** field. This is the hex color used for headings, emphasis, underlines, and circles in the presentation skill.

Pick the accent color from the brand's primary color (identified from thumbnails in the packaging analysis). Add it under a `## Presentation Style` section in CLAUDE.md:

```markdown
## Presentation Style

- **Accent Color:** #00CB5A (or whatever the brand's primary color is)
```

If no clear brand color exists, ask the user what accent color they'd like for their presentations. Default to `#00CB5A` (green) if they don't have a preference.

#### 3d: Description Bio

Verify the About Me section in the CLAUDE.md matches what the description skill needs. The youtube-description skill reads from `links.md` for standing links and from CLAUDE.md for the bio. Make sure both are consistent.

### Step 4: Present Summary

Show the user everything that was created:

```
Setup complete! Here's what was generated:

  CLAUDE.md                                          — Your personalized channel config
  workspace/{today}/audit/{channel-name}-audit.md    — Full audit report
  .claude/skills/youtube-description/links.md        — Standing links for descriptions
  .claude/skills/youtube-thumbnail/brand-style.md    — Visual brand guide for thumbnails
  .claude/skills/youtube-analysis/preferences.md     — Analytics preferences (if Metricool connected)

You're ready to go. Try any skill:

  /youtube-research   — Research a video topic
  /youtube-script     — Write a video script
  /youtube-title      — Generate title options
  /youtube-thumbnail  — Create thumbnail concepts
  /youtube-description — Write a video description
  /youtube-presentation — Build a slide deck
  /youtube-preview    — Preview thumbnail + title combos
  /youtube-analysis   — Pull analytics data
```

Ask if they want to adjust anything — especially the voice section in CLAUDE.md and the links in links.md.

### Step 5: Self-Destruct

Once the user confirms everything looks good:

1. Delete the entire `.claude/skills/youtube-init/` directory
2. Confirm: "Init skill removed. Your channel is set up — just use the other skills from now on."

**Important:** Do NOT delete until the user has confirmed they're happy with the setup. If they want changes, make them first, then delete.

---

## Failure Handling

- **No ScrapeCreators API key:** The audit will fall back to Metricool + web search. Warn the user that results will be less detailed but still functional.
- **No API keys at all:** The audit can still run using web search for public YouTube data. Voice extraction from transcripts won't be available, so the voice section will be thinner.
- **User wants to skip the audit:** Don't allow it. The audit is what makes everything else work. Explain that it only takes 5 minutes and it's a one-time setup.

---

## Output Files

```
CLAUDE.md                                           — Personalized channel config
workspace/{today}/audit/{channel-name}-audit.md     — Full audit report
.claude/skills/youtube-description/links.md         — Standing links for descriptions
.claude/skills/youtube-thumbnail/brand-style.md     — Visual brand guide
.claude/skills/youtube-analysis/preferences.md      — Analytics preferences (if Metricool)
```

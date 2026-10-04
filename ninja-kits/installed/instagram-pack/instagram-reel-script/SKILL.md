---
name: instagram-reel-script
description: Use when the user wants to write a reel script, generate Instagram reel content, script a talking head video, create reel hooks, plan reel content, or write a script for a short-form video. Generates multiple script variations with hooks, body beats, CTAs, on-screen text suggestions, and visual notes.
---

# Reel Script Generator

Generate ready-to-film Instagram reel scripts with proven hook frameworks, beat-by-beat structure, on-screen text suggestions, and visual notes. Produces 3 different script variations per topic so the user can pick their favorite direction. Can write in the user's own voice, a cloned competitor voice, or a blend of both.

---

## Process Overview

```
Step 1: Get the Topic          →  What's the reel about?
Step 2: Select Voice Source     →  Own voice / cloned voice / blend
Step 3: Load Context            →  Pull voice + strategy + examples
Step 4: Generate 3 Scripts      →  Different hooks, structures, lengths
Step 5: Present & Iterate       →  User picks and refines
Step 6: Save                    →  Save final script to workspace
```

---

## Step 1: Get the Topic

All you need from the user is the **reel topic or idea**. They may provide:

- A specific topic: "How I use Claude Code to write Instagram carousels"
- A general area: "Something about AI agents"
- A trending angle: "React to this news about OpenAI"
- A content pillar: "Productivity tip"

If the topic is vague, check `CLAUDE.md` for the user's content pillars and suggest 3-5 specific angles within that pillar. Let them pick.

Don't ask a bunch of follow-up questions. Figure out the angle, hook, and structure yourself — that's what the 3 variations are for.

## Step 2: Select Voice Source

Present the user with their options:

**(a) Your voice (default)** — Uses the voice profile from `CLAUDE.md`. This is the default if the audit has been run. If CLAUDE.md hasn't been personalized yet, tell the user to run `/instagram-audit` first for best results, but still proceed with a neutral, engaging tone.

**(b) Cloned voice** — Uses a saved voice profile from `workspace/voices/`. List available profiles:
```bash
ls workspace/voices/
```
If no profiles exist, tell the user to run `/voice-cloner` first to create one.

**(c) Blend** — Uses the user's personal context (audience, content pillars, brand) from `CLAUDE.md` but adopts the style patterns (hooks, pacing, tone) from a cloned voice profile. This is the most powerful option — it sounds like the user but with a proven creator's structural patterns.

If the user doesn't specify, default to **(a) Your voice**.

## Step 3: Load Context

Pull together all the context needed to write great scripts:

1. **Voice profile** — From CLAUDE.md (option a/c) or `workspace/voices/{profile}.md` (option b/c)
2. **Personal context from CLAUDE.md:**
   - Content pillars and topics
   - Audience description
   - Brand identity and unique angle
   - Performance benchmarks (what's working)
   - Any reel-specific patterns noted in the audit
3. **Example scripts** — Check `workspace/reel-scripts/` for previously saved scripts. Use these as style references if they exist.
4. **Topic research** — If the topic is about a specific tool, product, or news item, do a quick web search to get accurate details.

## Step 4: Generate 3 Script Variations

Create **3 entirely different reel scripts** for the same topic. Vary across these dimensions:

| Dimension | Script A | Script B | Script C |
|-----------|----------|----------|----------|
| **Hook** | Different framework | Different framework | Different framework |
| **Structure** | Talking head | B-roll guided | On-screen text heavy |
| **Length** | ~30s (short & punchy) | ~45s (medium depth) | ~60s (full breakdown) |
| **Angle** | Hot take / opinion | Educational / tutorial | Story / personal experience |

### Hook Frameworks (Adapted for Spoken Video)

Use a different hook framework for each script. These are the proven frameworks adapted from carousel hooks to spoken/video format:

**1. Borrowed Authority**
Open by naming a well-known person, company, or product. The name grabs attention; the take holds it.
> "Sam Altman just said something that should scare every developer..."
> "This one feature in Claude Code changed how I build everything."

**2. Surprising Statistic**
Lead with a specific, hard-to-ignore number. Say it with emphasis — let it land.
> "90% of Instagram reels get less than 500 views. Here's what the other 10% do differently."
> "I spent 47 hours last month on content. This tool cut it to 6."

**3. Direct Listicle**
State exactly what the list is about. No cleverness — the format does the work.
> "3 AI tools I use every single day."
> "5 mistakes killing your Instagram engagement."

**4. Pattern Interrupt**
Start with something unexpected — a visual, a sound, an odd statement. Break the scroll pattern.
> [Looking confused at camera] "Why is nobody talking about this?"
> "Stop. Whatever you're doing right now — watch this first."

**5. Bold Claim / Hot Take**
Make a strong, opinionated statement that people will either love or want to argue with.
> "Posting every day is destroying your account."
> "AI won't replace you. But someone using AI will."

**6. Direct "You" Challenge**
Point directly at the viewer. Make them feel called out.
> "If you're still editing reels manually, you're wasting hours every week."
> "You're sitting on a goldmine and you don't even know it."

**What kills a hook (same rules as carousels):**
- Desensitized claims ("I make $10K/month")
- Disconnected first and second lines
- Clichés that anyone could say
- Wide net, narrow delivery

### Script Structure

Every script must include these sections:

#### HOOK (0-3 seconds)
- The opening line that stops the scroll
- Label which hook framework is being used
- Include on-screen text suggestion (the text that appears over the video)
- Describe the visual setup (where to look, expression, setting)

#### BODY (main content)
Break into numbered **beats** — each beat is one idea or point.
- `[Say]:` — The spoken script (conversational, not robotic)
- `[On-screen text]:` — Key words/phrases shown on screen (shorter than what's said)
- `[Visual]:` — What the viewer sees (talking head, b-roll, screenshot, etc.)

**Body structure options:**
- **List format** — "First... Second... Third..." (clean, scannable)
- **Story format** — "So I was doing X when Y happened..." (engaging, personal)
- **Tutorial format** — "Here's how: Step 1..." (actionable, saveable)
- **Contrast format** — "Most people do X. But the top 1% do Y." (tension-building)
- **Rant format** — Stream of consciousness hot take (authentic, shareable)

Keep each beat tight. One idea per beat. If a beat has more than 2-3 sentences, split it.

#### CTA (last 3-5 seconds)
- Clear call to action that matches the content
- Don't always default to "follow for more" — match the CTA to the value:
  - Educational content → "Save this for later"
  - Hot take → "Drop your take in the comments"
  - Tutorial → "Try it and DM me your results"
  - Story → "Have you experienced this? Comment below"
  - Tool review → "Link in bio / comment [keyword] and I'll send it"

### Pacing Guidelines

- **15-30s reels:** 1 hook + 2-3 beats + CTA. Rapid-fire. No wasted words.
- **30-45s reels:** 1 hook + 3-5 beats + CTA. Room for one short example or story.
- **45-60s reels:** 1 hook + 5-7 beats + CTA. Can go deeper, add a mini-story, or do a full walkthrough.
- **60s+ reels:** Only if the topic demands it. Every second must earn its place.

When in doubt, go shorter. A tight 30s reel outperforms a bloated 60s reel.

### Voice Matching

When using a cloned voice (option b or c):
- Match their sentence length patterns
- Use their hook framework preferences
- Mirror their energy level and formality
- Incorporate their catchphrases naturally (don't force them)
- Follow their CTA style
- Respect their anti-patterns (things they avoid)

When blending (option c):
- Use the competitor's structural patterns (hook type, pacing, beat structure)
- But keep the user's personal context (audience, brand, content pillars)
- Use the user's natural vocabulary and catchphrases, not the competitor's
- Think of it as: "How would I say this if I had their delivery style?"

## Step 5: Present & Iterate

Show all 3 scripts clearly labeled. For each, highlight:
- Hook framework used
- Estimated duration
- Structure type
- Why this angle works

Ask the user which direction they like best. Then:
- **Refine** — Adjust the tone, length, hook, or specific beats
- **Combine** — Take the hook from A, body from B, CTA from C
- **Regenerate** — Try 3 completely new approaches
- **Save** — Lock in the final version

## Step 6: Save

Save the final script to `workspace/reel-scripts/{topic-slug}.md`.

```
workspace/reel-scripts/
├── ai-tools-daily-workflow.md
├── claude-code-carousel-trick.md
├── posting-every-day-myth.md
└── examples/            ← user can drop example scripts here for reference
```

Create the directory if it doesn't exist. Use a short, descriptive slug for the filename.

### Final Script Format

```markdown
# Reel Script: {Topic Title}

**Voice:** {Your voice / @competitor / Blend (@competitor style + your context)}
**Estimated Duration:** {Xs}
**Hook Type:** {Framework name}
**Style:** {Talking head / B-roll guided / On-screen text heavy / Mixed}

---

## HOOK (0-3s)

**[On-screen text]:** "{big bold text for the screen}"
**[Say]:** "{what to actually say — conversational}"
**[Visual]:** {camera setup, expression, setting}

---

## BODY ({start}s-{end}s)

### Beat 1
**[On-screen text]:** "{key phrase}"
**[Say]:** "{spoken script}"
**[Visual]:** {what the viewer sees}

### Beat 2
**[On-screen text]:** "{key phrase}"
**[Say]:** "{spoken script}"
**[Visual]:** {what the viewer sees}

### Beat 3
**[On-screen text]:** "{key phrase}"
**[Say]:** "{spoken script}"
**[Visual]:** {what the viewer sees}

---

## CTA ({start}s-{end}s)

**[On-screen text]:** "{CTA text}"
**[Say]:** "{spoken CTA}"
**[Visual]:** {final visual}

---

## Caption

{Draft Instagram caption — matches the user's voice from CLAUDE.md. Include relevant hashtags.}

## Cover Text Ideas

1. {Option A — 2-4 words for the reel cover/thumbnail}
2. {Option B}
3. {Option C}
```

---

## Tips for Better Scripts

- **Write for the ear, not the eye.** Read every line out loud. If it sounds stiff, rewrite it.
- **Front-load value.** The best content hits before the viewer thinks about swiping.
- **Use contrast.** "Most people do X. But here's what actually works." Tension keeps attention.
- **Be specific.** "3 tools" beats "some tools." "$47/month" beats "affordable."
- **One reel = one idea.** Don't cram two topics into one reel. Split them.
- **End strong.** A weak CTA kills an otherwise great reel. Make the ask clear and relevant.

---

## Troubleshooting

| Issue | Fix |
|-------|-----|
| Scripts sound generic | Make sure CLAUDE.md has been personalized via `/instagram-audit`. The voice profile makes the scripts sound like the user. |
| No voice profiles available | Run `/voice-cloner` first to create competitor voice profiles. Or use option (a) with your own voice. |
| Scripts are too long | Ask for a specific target length. Use the 15-30s format for punchy content. |
| User wants a different style | Ask them to point to a reel they like. Analyze its structure and use that as a template. |
| Topic is too broad | Check CLAUDE.md for content pillars. Suggest specific angles within the topic area. |

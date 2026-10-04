---
name: youtube-presentation
description: Use when the user wants to create a presentation, slide deck, or PowerPoint. Generates .pptx files in a dark visual style with big text, images, and funny GIFs. Supports normal and camera modes for recording.
---

# Presentation Generator

Generate polished PowerPoint presentations in a signature dark style. Content-dense slides with structured text, bullet points, GIFs alongside text, professional section dividers, and impactful stats slides. 80-200 slides total. Outputs as .pptx.

## First-Time Setup

Before first use, verify these are in place:

1. **pptxgenjs:** Run `npm install pptxgenjs` in the project root if not already installed.
2. **GIPHY_API_KEY:** Check `.env` for this key. If missing, tell the user to get a free key at https://developers.giphy.com/ and add `GIPHY_API_KEY=your_key` to `.env`.
3. **TAVILY_API_KEY:** Check `.env` for this key. Required for image search. Get a key at https://tavily.com/.
4. **Fonts:** Heading Now Trial is installed. IBM Plex Serif and Steel City Comic may not be — see `.claude/skills/youtube-presentation/fonts/README.md` for install instructions. Presentations will still generate without them (PowerPoint uses fallback fonts).

## Process

### Step 1: Get the Topic and Mode

Ask the user:
1. **What is the presentation about?** Topic, audience, context.
2. **Which mode?** Normal (full-width) or camera mode (content on one side for camera overlay — left or right).

That's it. Don't ask about individual slide content, colors, fonts, or GIF preferences. Figure all of that out yourself.

**Accent color:** Check CLAUDE.md for a `Presentation Accent Color` or brand color. If one is defined, use it as `accent_color` in the outline JSON. If not, use the default (#00CB5A). The accent color drives headings, bullets, dividers, and all accent elements.

### Step 2: Create the Outline

Start by reading `templates.md` in this skill directory — it's a layout catalog showing every slide type with visual blueprints, properties, and examples. Use it as reference when building the outline. This is the creative step — take your time here.

**Structure rules:**
- **80-200 slides total.** Each slide = ~3 seconds of presentation time. Aim for the length that fits the topic.
- **Content-dense slides are fine.** Slides can have 1-3 sentences or a heading + 3-5 bullet points. Keep it scannable — if you can't read it in 5 seconds, split it up.
- **Use bullet points when listing 3+ related items.** Use multiple slides for pacing/emphasis on important single points. Don't default to bullets for everything — mix it up.
- **Every image needs explanatory text.** Use `content_media` to pair images/GIFs WITH text. Never put images on standalone slides without context — the only exception is self-explanatory charts or diagrams. Standalone `gif` type is for rare full-bleed reaction moments only.
- **Real images on 20-40% of slides.** Every presentation MUST include real images — screenshots, product shots, UI images, diagrams — not just GIFs. When creating the outline, proactively add `image_query` fields to `content_media` slides that would benefit from a real screenshot or visual. Think: "What would a screenshot of this look like?" If the topic mentions a tool, product, UI, dashboard, workflow, or concept that can be visualized — add an `image_query`. Mix of GIF slides and image slides keeps it visually rich.
- **Use `stats` slides for impactful numbers** — one stat per slide, big and bold.
- **Use `two_column` for comparisons** — before/after, pros/cons, old way/new way.
- **Section dividers** break up the content into logical parts (every 15-25 slides). Include `section_number` for numbered sections and `subtitle` for context.
- **GIFs every 7-12 slides** — prefer `content_media` type (GIF alongside text). Funny, contextually relevant. Not random.
- **`image` type is rare** — only for self-explanatory charts/diagrams needing full width. For everything else, use `content_media` so there's always text with the visual.
- **Quote slides** for powerful external quotes. Uses a clean vertical accent bar.
- **Accent slides** (Steel City Comic font) sparingly for playful moments.
- **Blank slides** for breathing room or camera-only moments.
- **Speaker notes on every slide** — what the presenter should say while this slide is showing.

**Visual emphasis rules:**
- **`==text==` for inline emphasis.** Wrap key words in `==double equals==` to render them in a contrasting accent color. In white text → accent. In accent text → white. Use sparingly — 1-3 emphasized words per slide max. Don't emphasize everything.
- **`heading_underline: true` for hand-drawn underlines.** Adds a wavy accent-colored SVG line under the heading. Use on 10-20% of slides to draw attention to key headings. Works on: `title`, `content`, `content_media`, `section_divider`, `two_column`.
- **`value_circle: true` for hand-drawn circles.** Adds an irregular accent-colored SVG circle around the stat value. Use on `stats` slides when the number is the most important takeaway.

**Voice rules:**
- Write in the creator's voice from CLAUDE.md. If CLAUDE.md has voice/tone rules, follow them.
- Default: direct and conversational, not corporate. Short, punchy language. No filler.

**GIF search terms:** For each slide with a `gif_query` field, include 2-4 word Giphy search terms. Think about what reaction or emotion fits the moment: "mind blown", "confused math", "this is fine", "mic drop", "excited celebration", etc.

### Step 3: Fetch GIFs

For each slide with a `gif_query` field (both `gif` and `content_media` types), run `fetch_giphy.py` **in parallel**:

```bash
export $(grep GIPHY_API_KEY .env) && python3 .claude/skills/youtube-presentation/scripts/fetch_giphy.py \
  --query "{gif_query}" \
  --output "workspace/{today}/presentations/{slug}-assets/gif-{index}-{query-slug}.gif"
```

Run all GIF fetches simultaneously for speed.

### Step 4: Search & Download Images

Use `search_images.py` to find relevant images via Google Image Search (Tavily API). Search for images **in parallel** for all slides that need them:

```bash
export $(grep TAVILY_API_KEY .env) && python3 .claude/skills/youtube-presentation/scripts/search_images.py \
  --query "{image_query}" \
  --output "workspace/{today}/presentations/{slug}-assets/img-{index}-{query-slug}.jpg"
```

**When to search for images:**
- **Image slides** — full-bleed visuals (screenshots, diagrams, product shots)
- **Content_media slides** — images alongside text (when not using a GIF)

**Search query tips:**
- Be specific: "marketing automation dashboard dark UI" > "dashboard"
- Add "screenshot" for product/UI images, "illustration" for conceptual art
- Add "dark background" or "dark theme" for better visual fit with the dark slide theme
- Never use images as slide backgrounds — images should be their own slides or alongside text

If an image can't be sourced, leave `image_path` empty — the generator will show a placeholder.

### Step 5: Save the Outline

Write the completed outline JSON (with all local paths filled in) to:
```
workspace/{today}/presentations/{slug}-assets/outline.json
```

### Step 6: Generate the PPTX

```bash
node .claude/skills/youtube-presentation/scripts/generate_presentation.js \
  --outline "workspace/{today}/presentations/{slug}-assets/outline.json" \
  --output "workspace/{today}/presentations/{slug}.pptx" \
  --mode "{normal|camera-left|camera-right}"
```

### Step 7: Present to User

Tell the user:
- Where the .pptx file was saved
- Total slide count
- Section breakdown (how many sections, their topics)
- Number of GIFs and images included
- Any slides where images were missing (placeholders)

### Step 8: Iterate

If the user wants changes:
- **Small changes** (fix text on a few slides, swap a GIF): Edit the outline JSON directly and regenerate.
- **Structural changes** (reorder sections, add/remove topics): Regenerate the outline from scratch.
- **Style tweaks**: These require editing `generate_presentation.js` — flag this to the user.

---

## Design System

### Colors
| Name | Hex | Usage |
|------|-----|-------|
| Background | #0A0B12 | Every slide background |
| Primary Accent | Set via `accent_color` in outline JSON (default: #00CB5A) | Section dividers, headings, bullets, accent elements |
| White | #FFFFFF | Body text, title text |
| Light Gray | #A0A0A0 | Captions, subtitles, attributions |
| Dark Gray | #1A1B26 | Card backgrounds behind media |
| Card Border | #2A2B36 | Subtle card outlines |

### Fonts
| Font | Usage | Style |
|------|-------|-------|
| Heading Now Trial 04 (Bold) | Main headings, titles, section dividers | Sans-serif, bold, large |
| Heading Now Trial 04 (Regular) | Body text, bullets | Sans-serif, regular weight |
| IBM Plex Serif (Medium Italic) | Subtitles, quotes, context lines | Serif, italic |
| Steel City Comic | Playful/funny accent moments | Comic style, sparingly |

### Slide Types
| Type | Description | When to use |
|------|-------------|-------------|
| `title` | Big centered heading + subtitle | Opening slide, major section opens |
| `content` | Accent heading + body text with optional bullet points | The default — most slides are this |
| `content_media` | Text + GIF/image side by side (55/45 split) with card background | GIFs alongside text, visual + explanation combos |
| `image` | Full-bleed image with optional caption | Screenshots, diagrams that need full width |
| `gif` | Full-bleed embedded GIF | Rare — only for big reaction moments. Prefer `content_media` |
| `section_divider` | Numbered circle + accent line + heading + subtitle | Signal topic transitions |
| `quote` | Vertical accent bar + serif italic text + attribution | Powerful external quotes |
| `stats` | Big number (96pt) + label + context | Impactful statistics, one per slide |
| `two_column` | Side-by-side columns with vertical divider | Before/after, pros/cons, comparisons |
| `accent` | Steel City Comic font, centered | Playful one-liner moments |
| `blank` | Just dark background | Breathing room, camera-only pauses |

### Camera Mode
- **Normal:** Content uses full slide width.
- **Camera-left:** Left 40% is empty (camera zone), content on right 60%.
- **Camera-right:** Right 40% is empty, content on left 60%.

Camera mode is set globally for the entire presentation — don't mix modes.

---

## JSON Outline Schema

```json
{
    "title": "Presentation Title",
    "slug": "presentation-topic-slug",
    "author": "Your Name",
    "date": "2026-02-18",
    "mode": "normal",
    "accent_color": "#00CB5A",
    "slides": [
        {
            "type": "title",
            "heading": "The ==Big== Title",
            "subtitle": "Optional subtitle in serif italic",
            "heading_underline": true,
            "notes": "Speaker notes for what to say"
        },
        {
            "type": "content",
            "heading": "Key Point",
            "body": "One to three sentences. Can be longer now.",
            "notes": "Speaker notes"
        },
        {
            "type": "content",
            "heading": "Key Point with Bullets",
            "bullets": [
                "First important point",
                "Second important point",
                "Third important point"
            ],
            "notes": "Speaker notes"
        },
        {
            "type": "content",
            "heading": "Auto-Detected Bullets",
            "body": "- Lines starting with dash become bullets\n- Like this\n- And this",
            "notes": "Body text with - prefix auto-renders as bullets"
        },
        {
            "type": "content_media",
            "heading": "Point with Visual",
            "body": "Explanation alongside the image or GIF.",
            "bullets": ["Can also use bullets here"],
            "image_path": "workspace/{today}/presentations/slug-assets/gif-0-reaction.gif",
            "gif_query": "mind blown",
            "media_side": "right",
            "caption": "optional caption under media",
            "notes": "Speaker notes"
        },
        {
            "type": "section_divider",
            "heading": "Part 2: The Good Stuff",
            "subtitle": "Optional context line under the heading",
            "section_number": 2,
            "notes": "Speaker notes"
        },
        {
            "type": "stats",
            "value": "81%",
            "value_circle": true,
            "label": "reduction in audit time",
            "context": "Anthropic's marketing team",
            "notes": "Speaker notes"
        },
        {
            "type": "two_column",
            "heading": "Before vs After",
            "left_heading": "Before",
            "left_bullets": ["Manual process", "8 hours per audit", "Spreadsheet chaos"],
            "right_heading": "After",
            "right_bullets": ["One command", "90 minutes", "Interactive report"],
            "notes": "Speaker notes"
        },
        {
            "type": "image",
            "image_query": "marketing analytics dashboard dark",
            "image_path": "workspace/{today}/presentations/slug-assets/img-0-name.jpg",
            "caption": "Optional caption",
            "notes": "Speaker notes"
        },
        {
            "type": "gif",
            "image_path": "workspace/{today}/presentations/slug-assets/gif-0-mind-blown.gif",
            "gif_query": "mind blown",
            "caption": "optional funny caption",
            "notes": "Speaker notes"
        },
        {
            "type": "quote",
            "text": "The best way to predict the future is to build it.",
            "attribution": "Alan Kay",
            "notes": "Speaker notes"
        },
        {
            "type": "accent",
            "text": "wait what?!",
            "notes": "Speaker notes"
        },
        {
            "type": "blank",
            "notes": "Pause for effect"
        }
    ]
}
```

**Required fields per type:**
- `title`: heading (required), subtitle (optional)
- `content`: heading (optional), body (optional), bullets (optional) — at least one required
- `content_media`: image_path (required after fetch), gif_query (for GIF fetching) OR image_query (for image search), heading/body/bullets (at least one text element), media_side (optional, default "right"), caption (optional)
- `section_divider`: heading (required), subtitle (optional), section_number (optional)
- `stats`: value (required), label (required), context (optional)
- `two_column`: heading (optional), left_heading/left_body/left_bullets, right_heading/right_body/right_bullets — at least one column must have content
- `image`: image_path (required), image_query (for image search), caption (optional)
- `gif`: image_path (filled after fetch), gif_query (for fetching), caption (optional)
- `quote`: text (required), attribution (optional)
- `accent`: text (required)
- `blank`: nothing required

Every slide type supports `notes` for speaker notes (embedded in the PPTX via PptxGenJS).

**Visual features available on all text fields:**
- `==text==` → inline emphasis (contrasting accent color)

**Visual features by slide type:**
- `title`, `content`, `content_media`, `section_divider`, `two_column`: `heading_underline` (boolean) → hand-drawn accent wavy underline
- `stats`: `value_circle` (boolean) → hand-drawn accent circle around the stat value

---

## Quality Checklist

- [ ] **80-200 slides total** — appropriate length for the topic
- [ ] **Content-dense slides use bullets or multi-paragraph body where appropriate**
- [ ] **Real images (screenshots, product shots, diagrams) on 20-40% of slides** via `content_media` with `image_query`
- [ ] **GIFs appear alongside text via `content_media`**, not on blank standalone slides (except intentional full-bleed moments)
- [ ] **Section dividers include numbers and/or subtitles** for context
- [ ] **Stats slides used for impactful data points** — big number, clear label
- [ ] **GIFs every 7-12 slides** — contextually funny, not random
- [ ] **Speaker notes on every slide** — what the presenter should say
- [ ] **All image/GIF paths are valid** local files in the assets directory
- [ ] **Text is in the creator's voice** — direct, no-BS, conversational
- [ ] **Presentation tells a story** — coherent arc from start to finish
- [ ] **Mode is consistent** — camera zone is on the correct side throughout
- [ ] **Mix of slide types** — don't overuse any single type. Variety keeps it engaging.
- [ ] **`==emphasis==` used sparingly** — 1-3 highlighted words per slide max. Not every slide needs it.
- [ ] **`heading_underline` on 10-20% of slides** — adds visual interest without overuse.
- [ ] **`value_circle` on standout stats** — use on the most impactful 1-2 stats, not every stats slide.

---

## Troubleshooting

| Issue | Fix |
|-------|-----|
| `Cannot find module 'pptxgenjs'` | Run `npm install pptxgenjs` in the project root |
| No GIPHY_API_KEY | Add `GIPHY_API_KEY=your_key` to `.env`. Free key at developers.giphy.com |
| GIPHY_API_KEY not found by script | Use `export $(grep GIPHY_API_KEY .env) && python3 ...` to load it |
| Fonts look wrong | Install IBM Plex Serif and Steel City Comic. Heading Now Trial should already be installed. |
| GIF doesn't animate in Keynote | Keynote has limited GIF support. Open in PowerPoint for full GIF animation. |
| Image not found | Ensure images are downloaded to the assets directory before generating |
| Slides too many / too few | Adjust the outline. Each slide ~3 seconds. 100 slides = ~5 min presentation. |
| No TAVILY_API_KEY | Add `TAVILY_API_KEY=your_key` to `.env`. Get a key at tavily.com |
| Image search returns no results | Try broader/different search terms. Add "photo" or "screenshot" to the query. |
| Downloaded image is too small | Script auto-skips images < 640px wide. Try more specific search terms. |

---

## Output Format

Use today's date (YYYY-MM-DD format) for the date folder. For example, if today is 2026-02-18, the output goes in `workspace/2026-02-18/presentations/`.

```
workspace/{today}/presentations/{topic-slug}.pptx
workspace/{today}/presentations/{topic-slug}-assets/
    outline.json
    gif-0-{description}.gif
    gif-1-{description}.gif
    img-0-{description}.jpg
    img-1-{description}.jpg
    ...
```

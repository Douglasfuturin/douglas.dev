---
name: instagram-thumbnail
description: Use when the user wants to create an Instagram reel cover, design an Instagram post thumbnail, or generate cover art for Instagram reels/posts. Uses Gemini 3 Pro Image Preview (Nano Banana Pro) to generate professional, vertical-format cover images composited with the user's headshot photos.
---

# Instagram Thumbnail Generator

Generate professional Instagram reel covers and post thumbnails using Gemini Nano Banana Pro. Produces 4 entirely different cover variations at once, saves them individually, and creates a comparison grid so you can quickly pick the direction you like best.

---

## Cover Strategy

Instagram covers compete for attention in a vertical, mobile-first feed. Every cover needs to stop the scroll in under 1 second.

### How Instagram Differs from YouTube

- **Vertical format (9:16)** — Phone-native. Person can fill the frame. Text stacks vertically.
- **No title pairing** — Unlike YouTube, there's no separate title below the thumbnail. The cover IS the entire pitch. Caption text is secondary and often hidden behind "...more".
- **Feed context** — Reels appear in the Reels tab (grid of covers), Explore page (mixed grid), and main feed (full-screen autoplay). The cover matters most in the grid views.
- **Sound-on culture** — Many viewers watch with sound, so the cover doesn't carry as much weight as YouTube thumbnails. But for the Reels grid and Explore, it's everything.
- **Smaller grid display** — In the Reels tab, covers display at roughly 1/3 screen width. Text must be HUGE to be readable.

### The 2-Step Instagram Decision Loop

1. **Grid Scan** — Viewer sees the cover in a grid (Reels tab, Explore, profile). They're scanning fast. The cover needs to visually pop AND communicate what the reel is about in one glance.
2. **Tap or Skip** — Unlike YouTube's thumbnail→title→thumbnail flow, Instagram is simpler: the cover either makes them tap or they keep scrolling. There's no title to read — it's all visual.

### Desire Loop (Same Framework)

Before designing, define:
- **What is the core desire?** (money, growth, speed, capability)
- **What is the specific pain point?**
- **What is the solution/transformation?**
- **What is the curiosity loop?**

### Visual Stun Gun Elements (Adapted for Vertical)

Use a maximum of 3 per cover:

1. **Color contrast** — Bold, saturated colors that pop in a grid of competing covers
2. **Large face with emotion** — Faces work even better vertically — they can fill the frame
3. **Visually compelling graphic** — Product shots, screenshots, UI elements
4. **Big text, numbers, or dollars** — Even more critical on Instagram since there's no title to read
5. **Before/After split** — Top/bottom split works naturally in vertical
6. **Aesthetic imagery** — Instagram rewards beautiful, aspirational visuals more than YouTube
7. **Design collage** — Words and icons surrounding the subject

### Composition Types (Vertical)

- **Full-frame face** — Person fills the frame, text overlaid. Most engaging for personality-driven content.
- **Top text / Bottom person** — Text in the upper third, person in the lower two-thirds. Clean and readable.
- **Top/Bottom split** — Before/after or contrast. Top half vs bottom half.
- **Centered symmetric** — Subject centered, balanced composition. Works for aesthetic/cinematic content.
- **Text-heavy poster** — Bold text dominates, minimal imagery. Works for educational/tip content.

---

## Process

### Step 1: Get the Topic & Set Up

All you need from the user is the **reel topic or caption**. Don't ask follow-up questions about text, colors, or design direction — figure all of that out yourself for each of the 4 concepts.

**However, do ask about specific visual elements.** Before designing, ask if there are specific logos, products, tools, or screenshots that should appear.

Pick the first available headshot from `.claude/skills/instagram-thumbnail/headshots/`. If empty, check `.claude/skills/youtube-thumbnail/headshots/` as a fallback. If both are empty, tell the user to add a headshot photo first.

### Step 1b: Search for High-Performing Example Covers (Optional)

Search Instagram for reels on the same topic and download their cover images as style inspiration. This step is optional — skip it if the topic is niche or you don't expect great results.

```bash
python3 .claude/skills/instagram-thumbnail/scripts/search_examples.py \
  --query "{reel topic}" \
  --top 5 \
  --min-views 10000
```

This will:
1. Search Instagram reels via the Scrape Creators API
2. Sort results by view count (highest first)
3. Download the top 5 reel covers to `workspace/examples/instagram/`
4. Print a JSON manifest to stdout with metadata

**Review the downloaded examples** if available, but don't over-index on them. Instagram reel covers vary wildly in quality. Take note of what stands out and skip anything low-effort.

**Notes:**
- Requires `SCRAPECREATORS_API_KEY` in `.env`
- Instagram CDN URLs can expire — download promptly
- If the API fails or returns poor results, skip this step entirely. It's nice-to-have, not essential.

### Step 2: Define the Desire Loop, Then Craft 4 Different Prompts

Work through the desire loop, then craft **4 entirely different cover concepts** using the Style Guide and Prompt Template below. Vary across these dimensions:

- **Visual elements:** Different objects, icons, screenshots, props
- **Text treatment:** Different words, or no text at all
- **Color direction:** Different palettes — try at least one bold/bright approach
- **Person pose/expression:** Different emotions and framing (close-up vs wider shot)
- **Composition style:** Different layouts from the vertical composition types above

Label each concept A, B, C, D. Briefly describe each to the user before generating.

Key rules for every prompt:
- Always specify **9:16 vertical composition** (phone format)
- Always describe person placement explicitly
- Always specify the reference photo
- Describe text with font style, color, and position
- **Keep text in the center 70% vertically** — Instagram crops the top and bottom edges in some views
- **Keep elements LARGE** — imagine the cover at 1/3 phone screen width in a grid

### Step 2b: Gather Reference Images for Concepts

Same process as the YouTube skill — fetch logos, icons, screenshots needed by the concepts. Save to `workspace/refs/`.

### Step 3: Generate All 4 Covers

Run the generation script **4 times in parallel**:

```bash
python3 .claude/skills/instagram-thumbnail/scripts/generate_thumbnail.py \
  --headshot ".claude/skills/instagram-thumbnail/headshots/{selected-headshot}" \
  --reference "workspace/refs/{ref1}.png" \
  --examples "workspace/examples/instagram/{slug}-1.jpg" \
  --prompt "{concept A prompt}" \
  --output "workspace/{today}/instagram/{reel-slug}/a.png"
```

Repeat for B, C, D. **Run all 4 in parallel.**

### Step 4: Create Comparison Grid

```bash
python3 .claude/skills/instagram-thumbnail/scripts/combine_thumbnails.py \
  --images "workspace/{today}/instagram/{reel-slug}/a.png" \
           "workspace/{today}/instagram/{reel-slug}/b.png" \
           "workspace/{today}/instagram/{reel-slug}/c.png" \
           "workspace/{today}/instagram/{reel-slug}/d.png" \
  --output "workspace/{today}/instagram/{reel-slug}/comparison.png" \
  --labels "A" "B" "C" "D"
```

### Step 5: Present to User

Show the comparison grid and describe each concept. Ask which direction they like best.

### Step 6: Iterate

Same iteration flow as the YouTube skill — pass the chosen cover as a reference and generate refined versions (v2, v3, etc.).

```bash
python3 .claude/skills/instagram-thumbnail/scripts/generate_thumbnail.py \
  --headshot ".claude/skills/instagram-thumbnail/headshots/{selected-headshot}" \
  --reference "workspace/{today}/instagram/{reel-slug}/b.png" \
  --prompt "{edit prompt with user feedback}" \
  --output "workspace/{today}/instagram/{reel-slug}/v2.png"
```

---

## Style Guide

**IMPORTANT:** Always read `brand-style.md` in the youtube-thumbnail skill directory if it exists — the same brand identity applies here.

### Composition (Vertical 9:16)

- **Person:** Can be positioned more flexibly than YouTube thumbnails:
  - **Full-frame:** Person fills the entire frame, text overlaid on top
  - **Lower two-thirds:** Person in the bottom portion, text/graphics in the upper third
  - **Centered:** Person centered with elements around them
- **Face emotion:** Even more important on Instagram — faces drive engagement. Exaggerated expressions work.
- **Visual elements:** Can be placed above, below, or alongside the person. Layer for depth.
- **Icons/logos:** Upper area, floating with subtle shadows.
- **Text:** Bold, large, stacked vertically. Usually upper third or center. Must be readable at grid size (~130px wide).

### Background

- Same rules as YouTube: **never a solid black void.** Use darkened real-world scenes with texture and depth.
- Dark and moody works, but Instagram also rewards **brighter, more saturated** approaches. Don't be afraid to go bold.
- Consider the topic — lifestyle/travel content can be brighter; tech/business content stays darker.

### Color Palette

- More flexibility than YouTube. Instagram feeds are more visually diverse.
- **Dark + neon accent** works great for tech content
- **Bold, saturated colors** can stand out in the grid
- **White text on dark** is the safest for readability
- Explore at least one concept with a non-dark approach

### Typography

- **Headlines:** Bold, heavy sans-serif. Even larger than YouTube since there's no separate title.
- **Stacked text:** Works well vertically — one word per line for maximum impact.
- **Maximum 4-5 words.** Fewer is better. Some of the best covers have just 1-2 words.
- Must be readable when the cover is ~130px wide (Reels grid size).

### Technical Specs

- **Aspect ratio:** 9:16 (vertical, phone-native)
- **Resolution:** 1080x1920 (standard Instagram)
- **Output format:** PNG

---

## Prompt Template

```
A professional Instagram reel cover image in 9:16 vertical aspect ratio (phone format).

ATTACHED IMAGES:
- Image 1 (headshot): Reference photo of the person to include. Use their exact likeness.
{reference_image_descriptions}

PERSON:
Use the likeness from the headshot (Image 1). {person_placement_description}. They should have dramatic, natural lighting on their face. Their expression is [confident / excited / curious / serious / shocked].

BACKGROUND:
Dark, moody, cinematic background — NOT a solid black void. Use a darkened real-world scene or environment relevant to the topic. The scene should feel like dramatic night photography or heavy cinematic color grading — dark overall but with real environmental detail, texture, and depth. {color_direction} color tones. No glow effects.

VISUAL ELEMENTS:
{visual_elements_description}

TEXT:
"{cover_text}" in bold, large, white text. {text_position}. Clean, heavy, modern sans-serif font. High contrast against the dark background. Must be clearly readable even at small sizes. Stack words vertically for maximum impact — one or two words per line.

STYLE:
Professional, high-contrast, clean design. Designed for Instagram's vertical format. Dramatic lighting on the person. Polished and modern — not cluttered. Must look great both full-screen and in a small grid view.
```

### Ideas for Varying the 4 Concepts

| Dimension | Concept A | Concept B | Concept C | Concept D |
|-----------|-----------|-----------|-----------|-----------|
| **Layout** | Full-frame face + overlay text | Top text / bottom person | Text-heavy poster, minimal imagery | Top/bottom split (before/after) |
| **Text** | Punchy 1-2 word feeling | Big number or dollar amount | 3-4 word hook | No text (visual only) |
| **Colors** | Dark + neon accent (cyan, magenta) | Dark + warm accent (orange, gold) | Bold saturated background (non-dark) | Dark + white/minimal |
| **Person** | Extreme close-up, big emotion | Waist-up, gesturing | Small in frame, environment dominates | Side profile or looking away |
| **Stun gun** | Face + big text | Face + number + graphic | Compelling graphic + text | Aesthetic imagery + face |

---

## Quality Checklist

### Technical Quality
- [ ] **9:16 vertical format** — correct phone-native proportions
- [ ] **Person is recognizable** — face clear, well-lit, not distorted
- [ ] **Face has clear emotion** — exaggerated enough to read at grid size
- [ ] **Background has depth** — not a flat solid color
- [ ] **Text is readable at grid size** — would it be legible at ~130px wide?
- [ ] **3 elements max** — not overcrowded
- [ ] **High contrast** — pops in a grid of competing covers
- [ ] **Content in safe zone** — important elements in center 70% vertically (Instagram crops edges in some views)

### Engagement Check
- [ ] **Scroll-stopping** — would this make you tap in the Reels grid?
- [ ] **Clear topic** — can you tell what the reel is about in 1 second?
- [ ] **Emotion is clear** — face expression readable at small size?
- [ ] **Stands out** — would this catch your eye in Explore?

---

## Troubleshooting

| Issue | Fix |
|-------|-----|
| "Could not process image" on reference | File is HTML, not image. Run `file <path>` to confirm. Re-download from different source. |
| search_examples.py fails or returns junk | Instagram search is less reliable than YouTube. Skip Step 1b and generate without `--examples`. |
| No image returned | Simplify the prompt. Try again. |
| Person doesn't look like headshot | Add "Use the exact likeness from the attached reference photo." Try a different headshot. |
| Text is garbled | Gemini's text rendering isn't perfect. Consider adding text in post-production. |
| Wrong aspect ratio | The script sets 9:16 automatically. Check saved file dimensions. |

---

## Output Format

Use today's date for the date folder:

```
workspace/{today}/instagram/{reel-slug}/
  a.png
  b.png
  c.png
  d.png
  comparison.png
  v2.png
  v3.png
```

Scripts create directories automatically via `mkdir -p`.

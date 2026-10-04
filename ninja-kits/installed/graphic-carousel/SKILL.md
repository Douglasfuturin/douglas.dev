---
name: graphic-carousel
description: Use when the user wants to create a LinkedIn carousel, design carousel slides, or generate infographic slides for LinkedIn posts. Uses Gemini 3 Pro Image Preview to generate professional, dark-themed carousel slides with clean diagrams, comparisons, and flow charts. No headshots — purely diagrammatic/infographic.
---

# LinkedIn Carousel Generator

Generate professional LinkedIn carousel slides using Gemini 3 Pro Image Preview. Plans a narrative arc across slides, generates each slide individually, and creates a preview strip so the user can review the full carousel at a glance.

---

## Carousel Strategy

LinkedIn carousels are educational infographics broken into a swipeable sequence. Each slide must work as a standalone visual AND as part of a larger story. The goal is to teach a concept, compare approaches, or walk through a system — one slide at a time.

### The Carousel Psychology

LinkedIn carousels work because of three psychological hooks:

1. **Hook Slide** — The first slide stops the scroll. It poses a compelling question, states a bold claim, or names a framework. The viewer swipes because they want the answer.
2. **Progressive Reveal** — Each subsequent slide reveals one piece of the puzzle. The viewer keeps swiping because each slide delivers value AND sets up the next one.
3. **Takeaway Slide** — The final slide summarizes the key insight or provides a call to action. This is what the viewer screenshots or shares.

**The flow is: Hook → Build → Build → Build → Takeaway.** This means:
- If the first slide doesn't stop the scroll → nobody sees slide 2 (fails at step 1)
- If middle slides don't deliver value → they stop swiping (fails at step 2)
- If the final slide doesn't land → they don't share or engage (fails at step 3)

### Slide Count Guidelines

- **3-5 slides** for a single concept or comparison
- **5-8 slides** for a walkthrough, tutorial, or multi-step framework
- **8-10 slides** for comprehensive deep dives (use sparingly)
- **Never more than 10 slides** — attention drops off sharply

### Slide Type Vocabulary

Every carousel is composed from these slide types. Mix them to build the narrative:

| Slide Type | When to Use | Key Elements |
|-----------|-------------|-------------|
| **Title/Hook** | Always slide 1 | Bold headline, minimal visual, curiosity trigger |
| **Architecture** | Showing systems, data flow, or structure | Connected boxes, arrows, component labels |
| **Comparison (A vs B)** | Contrasting approaches, old vs new | Two-column split, vertical divider, "VS" label, bottom metrics |
| **Flow/Cycle** | Showing loops, processes, or feedback systems | Circular or linear flow, 3-5 connected elements, arrows |
| **List/Features** | Enumerating capabilities, tools, or benefits | Bordered container, bulleted items, bold key terms |
| **Before → After** | Showing transformation | Split layout with clear visual contrast between states |
| **Takeaway** | Always the final slide | Bold summary statement, optional CTA |

---

## Process

### Step 0: Choose the Visual Theme

The carousel system supports two themes (see `carousel-style.md` for full details):

- **Theme A: Dark Diagram** — Dark navy background, coral/golden accents, architectural diagrams, flow charts, comparisons. Best for technical/architectural content.
- **Theme B: Grid Paper** — White grid paper background, green accents, hand-drawn circles/underlines, device mockups, star ratings. Best for listicles, tool showcases, social engagement.

Pick the theme based on the content type. If the carousel explains a system or architecture → Theme A. If it's a numbered list, tool showcase, or social CTA → Theme B. Default to Theme A if ambiguous.

### Step 1: Get the Topic & Plan the Narrative

All you need from the user is the **topic, concept, or post idea**. Don't ask follow-up questions about layout, colors, or slide count — figure all of that out yourself. The whole point is to deliver a complete carousel the user can react to.

**However, do ask about specific visual elements.** Before gathering reference images, ask the user: "Should I include any specific logos, product icons, or brand visuals?" This takes 5 seconds and avoids wasting a generation on the wrong references.

**Then, plan the narrative arc.** Before designing any slides, outline the carousel's story:

1. **What's the hook?** — What question, claim, or framework name will stop the scroll?
2. **What's the build?** — What are the 2-6 key points/steps/comparisons that form the middle?
3. **What's the takeaway?** — What single insight should the viewer walk away with?

Present this outline to the user before generating. Format it as:

```
Carousel outline: "{topic}"
- Slide 1 (Hook): {description}
- Slide 2 ({type}): {description}
- Slide 3 ({type}): {description}
- ...
- Slide N (Takeaway): {description}
```

### Step 2: Gather Reference Images

Before fetching anything from the web, **check the asset library first.** The `library/` directory at the project root contains pre-made assets:

```
library/
├── content-assets/
│   ├── backgrounds/
│   │   ├── black paper.png          # Dark textured paper background
│   │   └── white-grid-paper.png     # White grid paper (Theme B background)
│   ├── logos/
│   │   └── instagram-logo.png       # Instagram logo
│   └── svgs/
│       ├── circle-1.png             # Green hand-drawn circle (emphasis)
│       ├── circle-2.png             # Green hand-drawn oval (emphasis)
│       └── underline.png            # Green hand-drawn underline (emphasis)
└── tyler-example-content/
    └── carousels/
        ├── 9 Claude Code Skills/    # 11 frames — Theme B (grid paper) example
        └── Claude Code for Youtubers/ # 8 frames — Theme B (grid paper) example
```

**Use library assets as reference images.** Pass them via `--reference` so Gemini can incorporate them:
- **Theme B slides:** Always pass `library/content-assets/backgrounds/white-grid-paper.png` as a reference and instruct Gemini to use it as the background texture
- **Green accent elements:** Pass `circle-1.png`, `circle-2.png`, or `underline.png` when the slide needs hand-drawn emphasis marks
- **Instagram branding:** Pass `instagram-logo.png` if the carousel will also be posted to Instagram

**For additional example slides,** pass frames from the library's example carousels via `--examples` alongside the ones in the `examples/` directory. For Theme B carousels, use frames from `library/tyler-example-content/carousels/` as style examples instead of (or in addition to) the dark-themed examples.

**Then, fetch any remaining assets from the web.** Based on the topic, identify visual assets not in the library:

**What to fetch:**
- **Tool/product logos** — If the carousel discusses Claude Code, Cursor, React, etc., fetch their official logos
- **Mascots or brand visuals** — e.g., the Anthropic Claude logo, pixel art mascots, app icons
- **UI screenshots** — If a slide shows a specific tool or interface
- **Relevant icons or symbols** — API symbols, framework logos, etc.

**How to fetch:**
1. Use `WebSearch` to find the best image URL (e.g., search for "Claude Code logo PNG transparent")
2. Use `Bash` with `curl` to download AND validate:
   ```bash
   mkdir -p workspace/refs && \
   curl -sL "https://example.com/logo.png" -o "workspace/refs/claude-logo.png" && \
   file workspace/refs/claude-logo.png
   ```
3. **CHECK the `file` output.** Good: `PNG image data`, `JPEG image data`. Bad: `HTML document text` — delete and try a different source.
4. Only after `file` confirms it's a real image, verify it visually with the `Read` tool.

**CRITICAL: Many image hosting sites block direct downloads.** They return an HTML page instead of the image. The `file` command catches this instantly.

**If a download returns HTML:**
- Try a different source URL entirely
- Prefer: **Wikipedia/Wikimedia Commons**, **GitHub raw content**, **official press pages**
- Add `-H "User-Agent: Mozilla/5.0"` if needed
- As a last resort, skip it — Gemini can approximate common logos from description alone

**Tips:**
- Prefer PNG with transparent backgrounds
- Save all fetched references in `workspace/refs/` for reuse across slides
- Fetch 2-5 reference images max
- **Always validate with `file` before using**

### Step 3: Craft Prompts for Each Slide

For each slide in the outline, craft a detailed generation prompt. Each prompt should specify:

1. **Slide type** — What kind of layout (architecture, comparison, flow, etc.)
2. **Content** — Exact text, labels, and descriptions to appear on the slide
3. **Layout** — Where elements go (top, center, left/right columns, bottom tagline)
4. **Visual elements** — What diagrams, icons, arrows, or containers to include
5. **Reference images** — Which attached images to use and where

**Always include in every prompt:**
- "A professional LinkedIn carousel slide in 3:4 portrait aspect ratio (1080x1440px)."
- Explicit element positioning ("upper-left", "center", "bottom 15% of the slide")
- "No photos or headshots. Purely diagrammatic with geometric shapes, icons, and text."
- "No title bar or header strip at the top — jump straight into the headline."

**For Theme A, also include:**
- "Deep navy background #0D1520 with a radial vignette gradient — slightly lighter #162035 at center, darker #07101A at corners."
- "All card/node fills: gradient from #1E2D42 (top-left) to #111826 (bottom-right)."
- "All card borders: 2px gradient stroke from coral #E07856 (top) to golden #D4A55C (bottom), 12px radius."
- "Arrows: coral-to-golden gradient along their length. Soft coral ambient glow (15% opacity) behind the primary hero element."
- "Font: Inter Bold. Letter spacing: -4%. Line height: 85%."
- "Key headline word: left-to-right text gradient from coral #F08060 to golden #D4A55C."
- "1-2 hand-drawn emphasis elements (rough wobbly marker underline or sketchy oval circle in coral) on the single most important element per slide."

**For Theme B, also include:**
- "White grid paper background texture (use the attached grid paper reference image). Black text. Green (#00C853) accent elements."
- "Extra bold Inter sans-serif headlines with key words in green. Casual, friendly body text."
- "Hand-drawn green circles and underlines for emphasis (use the attached SVG overlays)."
- "Dark device mockups or dark cards floating on the white background."
- "'@itstylergermain' in bottom-left, 'save for later ↓' in bottom-right italic."

Describe each concept to the user before generating — include the slide type and what content it shows.

### Step 4: Generate All Slides

Run the generation script for each slide. **Generate slides in parallel** (batch 4 at a time if more than 4 slides).

Pass example carousel images via `--examples` so Gemini matches the established style. **Choose examples that match the selected theme.**

**Theme A (Dark Diagram) example:**
```bash
python3 .claude/skills/graphics-carousel/scripts/generate_slide.py \
  --reference "workspace/refs/{ref1}.png" "workspace/refs/{ref2}.png" \
  --examples ".claude/skills/linkedin-carousel/examples/1.jpeg" \
             ".claude/skills/linkedin-carousel/examples/2.jpeg" \
             ".claude/skills/linkedin-carousel/examples/3.jpeg" \
  --prompt "{slide prompt}" \
  --output "workspace/{today}/carousels/{topic-slug}/slide-1.png"
```

**Theme B (Grid Paper) example:**
```bash
python3 .claude/skills/graphics-carousel/scripts/generate_slide.py \
  --reference "library/content-assets/backgrounds/white-grid-paper.png" \
              "library/content-assets/svgs/circle-1.png" \
              "library/content-assets/svgs/underline.png" \
              "workspace/refs/{ref1}.png" \
  --examples "library/tyler-example-content/carousels/9 Claude Code Skills/Frame 1.png" \
             "library/tyler-example-content/carousels/9 Claude Code Skills/Frame 2.png" \
             "library/tyler-example-content/carousels/Claude Code for Youtubers/Frame 1.png" \
  --prompt "{slide prompt}" \
  --output "workspace/{today}/carousels/{topic-slug}/slide-1.png"
```

Repeat for each slide. Run up to 4 in parallel for speed.

**Reference image notes:**
- Only pass `--reference` images relevant to that specific slide's visual elements
- In the prompt, explicitly tell Gemini which attached image is which: "The first attached image is the grid paper background texture — use this as the slide background", "The second attached image is a green hand-drawn circle — use it to circle the key element"
- If a slide doesn't need any reference images (e.g., a pure text or abstract diagram), omit `--reference` entirely
- **Theme B always needs** the grid paper background and at least one green SVG accent as references

**Example image notes:**
- Always pass 2-3 example slides via `--examples` that match the chosen theme
- **Theme A:** Use the dark diagram examples from `.claude/skills/linkedin-carousel/examples/`
- **Theme B:** Use frames from `library/tyler-example-content/carousels/` (the grid paper ones)
- The script automatically appends a "STYLE EXAMPLES" instruction telling Gemini to study but not copy them
- Mix examples from different carousels for variety (e.g., a hook slide + a content slide + a CTA slide)

### Step 4.5: Visual QA — Inspect Every Slide

**ALWAYS do this. Never skip.** After generating slides, visually inspect every single one using the Read tool before showing anything to the user.

Check each slide for:
1. **Centering** — Is text and content centered where intended? Is the visual weight balanced?
2. **Spacing** — Even margins on all sides? No content crammed against edges? No wasted dead zones?
3. **Text readability** — All text legible at phone size? Nothing cut off or overlapping?
4. **Element collisions** — Any boxes, arrows, or labels stacking on each other?
5. **Compositing alignment** — If a diagram was composited onto a slide background, is it centered in the content zone (between title and footer), not just centered on the full slide?

**If anything looks off, fix it before moving on:**
- Re-generate the slide with adjusted prompt instructions
- For composited diagrams: adjust `--width`, `--position`, `--y-offset` in composite_diagram.py
- Keep iterating until every slide looks intentionally designed

The user should never have to point out centering or spacing issues — catch them yourself.

### Step 5: Create Preview

After all slides are generated, combine them into a preview image:

```bash
python3 .claude/skills/linkedin-carousel/scripts/combine_slides.py \
  --images "workspace/{today}/carousels/{topic-slug}/slide-1.png" \
           "workspace/{today}/carousels/{topic-slug}/slide-2.png" \
           "workspace/{today}/carousels/{topic-slug}/slide-3.png" \
  --output "workspace/{today}/carousels/{topic-slug}/preview.png"
```

For 6+ slides, add `--grid` to use a 2-column grid layout instead of a horizontal strip (which gets too wide to view).

### Step 6: Present to User

Show the user the preview image and describe each slide:
- **Slide 1 (Hook):** {description}
- **Slide 2 ({type}):** {description}
- **Slide 3 ({type}):** {description}
- ...

Ask which slides they like and which need changes.

### Step 7: Iterate

Once the user gives feedback, regenerate specific slides by passing the current version as a reference:

```bash
python3 .claude/skills/graphics-carousel/scripts/generate_slide.py \
  --reference "workspace/{today}/carousels/{topic-slug}/slide-2.png" \
  --examples ".claude/skills/linkedin-carousel/examples/1.jpeg" \
             ".claude/skills/linkedin-carousel/examples/2.jpeg" \
             ".claude/skills/linkedin-carousel/examples/3.jpeg" \
  --prompt "Edit this LinkedIn carousel slide. Keep the same overall layout and style.
The first attached image is the current slide to modify.
Please make the following changes: {user's feedback}" \
  --output "workspace/{today}/carousels/{topic-slug}/slide-2-v2.png"
```

After regenerating edited slides, rebuild the preview strip so the user can see the updated carousel in context.

Continue iterating until the user is happy with all slides.

---

## Style Guide

**IMPORTANT:** Always read `carousel-style.md` (in this skill directory) before crafting prompts. It contains the full visual identity rules for both themes — colors, typography, layout patterns, and constraints.

The carousel system supports two themes:
- **Theme A: Dark Diagram** — professional, dark-themed, technical. Default for architectural/explainer content.
- **Theme B: Grid Paper** — clean, white, social-friendly. Default for listicles, showcases, CTAs.

### Shared Specs (Both Themes)
- **Aspect ratio:** 3:4 portrait (1080x1440) — default. Use `--aspect-ratio 3:4` in the generation script.
- **Output format:** PNG
- **No headshots or photos of people**
- **Generous padding** — minimum 70px from all edges
- **Maximum ~40 words per slide**
- **Font:** Inter Bold throughout — tight letter spacing (-4%), tight line height (85%)

---

## Prompt Templates

### Theme A: Dark Diagram Template

```
A professional LinkedIn carousel slide in 3:4 portrait aspect ratio (1080x1440px).

ATTACHED IMAGES:
{reference_image_descriptions}

BACKGROUND:
Deep navy #0D1520 with a subtle radial vignette gradient — slightly lighter warm navy #162035 at center, deeper #07101A at corners. Never flat. Feels like depth and focus.

NO TITLE BAR. No header strip, no series label, no slide counter at the top. Start straight with the headline.

LAYOUT TYPE: {Title/Hook | Architecture | Comparison | Flow/Cycle | List | Takeaway}

FONT: Inter Bold throughout. Letter spacing: -4% (tight). Line height: 85% (tight). These specs apply to every text element on the slide.

HEADLINE:
"{headline_text}" in Inter Bold, very large, at the top of the content area with generous top padding. Mixed case. The single most important word uses a left-to-right gradient: coral #F08060 → golden #D4A55C. The rest of the headline is white.

CONTENT:
{detailed description of diagrams, boxes, arrows, labels, and their positions}

VISUAL STYLE (apply to all elements):
- Card/node fills: gradient from #1E2D42 (top-left) to #111826 (bottom-right)
- Card/node borders: 2px gradient stroke from coral #E07856 (top) to golden #D4A55C (bottom), 12px corner radius
- Arrows: coral-to-golden gradient along their length showing flow direction
- Soft coral ambient glow (15% opacity) behind the main hero element or central visual
- Icons: flat line-art, white or coral fill
- No flat solid card fills — every surface has a gradient
- No flat solid accent colors — coral and golden always appear as gradients

HAND-DRAWN EMPHASIS:
Add 1 rough hand-drawn element on the single most important item — either a wobbly brush-stroke underline in coral beneath the key headline word, or a sketchy imperfect oval/circle around the key metric or node. Keep it marker-style and slightly irregular, not perfectly smooth.

BOTTOM BRANDING BAR:
Thin separator line (#1E2D40) above the bar.
Bottom-left: "@itstylergermain" in small Inter Bold, color #7A8A9E
Bottom-right: "save for later ↓" in small Inter Bold italic, color #7A8A9E
```

### Theme B: Grid Paper Template

```
A professional LinkedIn/Instagram carousel slide in 1:1 square aspect ratio (1080x1080).

ATTACHED IMAGES:
- Image 1: White grid paper background texture — use this as the full slide background
- Image 2: Green hand-drawn circle — use this to circle/highlight the key visual element
- Image 3: Green hand-drawn underline — use this under the most important word in the headline
{additional_reference_image_descriptions}

BACKGROUND:
White grid paper texture (use the attached grid paper image as the background). Clean, bright, with subtle grid lines visible.

LAYOUT TYPE: {Title/Hook | Feature/Skill | Showcase | CTA/Takeaway}

HEADLINE:
"{headline_text}" in extra bold, heavy, black sans-serif text filling the top 30-40% of the slide. Key word "{emphasized_word}" in bright green (#00C853). Very large, impactful.

CONTENT:
{detailed description of device mockups, screenshots, cards, and their positions}

VISUAL STYLE:
- White grid paper background — clean and bright
- Black text for headlines, dark gray for body text
- Green (#00C853) for emphasis: key words, arrows, circles, underlines
- Dark charcoal cards/screenshots floating on the white background with subtle shadows
- Hand-drawn green circles around key elements (use attached SVG)
- Hand-drawn green underlines under important words (use attached SVG)
- Thick green arrows pointing to CTAs or key elements
- Casual, friendly serif for body text — approachable and readable
- Monospace text in dark rounded pills for code/commands

BRANDING:
- Bottom-left: "@itstylergermain" in small dark text
- Bottom-right: "save for later" in small italic text with bookmark icon
```

### Slide-Specific Prompt Additions

**For Architecture slides (Theme A):**
```
Show a left-to-right data flow with connected components:
- {Component A} on the left inside a rounded rectangle
- Arrow pointing right to {Component B}
- Arrow pointing right to {Component C} inside a larger bordered container
- Labels below or inside each component
- Feedback loop arrow curving back from right to left (if applicable)
```

**For Comparison (A vs B) slides (Theme A):**
```
Two-column comparison layout:
- Left column: "{Approach A title}" with {elements stacked below}
- Vertical coral divider line in the center with "VS" label
- Right column: "{Approach B title}" with {elements}
- Bottom-left: "{negative metric}" with X mark
- Bottom-right: "{positive metric}" with checkmark
```

**For Flow/Cycle slides (Theme A):**
```
Circular flow diagram with {N} elements arranged in a circle/loop:
- Center: {central element or label}
- Position 1 (top): "{label}" with {icon} — "{description}"
- Position 2 (right): "{label}" with {icon} — "{description}"
- Position 3 (bottom): "{label}" with {icon} — "{description}"
- Position 4 (left): "{label}" with {icon} — "{description}"
- White curved arrows connecting each element to the next in a clockwise loop
```

**For Feature/Skill slides (Theme B):**
```
Tool/skill showcase slide:
- Top: decorative green line + "Skill #{number}" header with pixel mascot icon
- Green star rating row (e.g., 5 green stars)
- Dark charcoal card showing: tool icon, tool name in bold white, author/org below, category tag, star count
- Below the card: description text in casual serif font explaining what the tool does
- Bottom: dark rounded pill containing monospace install command text
```

**For CTA/Takeaway slides:**
```
Theme A: Centered, bold white statement on dark background. Clean and impactful — let the words breathe.
Theme B: Bold call-to-action. "COMMENT" in huge black bold text, "{keyword}" in green with quotes, "{instruction}" below. Green arrow pointing down toward comment area. @handle bottom-left, save for later bottom-right.
```

---

## Quality Checklist

Run through this after every generation:

### Visual Quality
- [ ] **Background matches theme** — Theme A: dark navy `#1A2332`. Theme B: white grid paper
- [ ] **Text is readable** — would it be legible on a phone screen?
- [ ] **Accent colors are correct** — Theme A: coral/golden. Theme B: green `#00C853`
- [ ] **Containers and elements are styled** — Theme A: bordered rounded rects. Theme B: dark cards on white
- [ ] **Padding is generous** — content doesn't crowd the edges
- [ ] **No headshots or photos** — purely diagrammatic
- [ ] **Square aspect ratio** — 1:1, not rectangular
- [ ] **Typography is bold** — no thin or light-weight fonts
- [ ] **Consistent style across slides** — same theme, colors, fonts, and spacing throughout
- [ ] **Theme B branding** — @handle bottom-left, "save for later" bottom-right (if Theme B)

### Content Quality
- [ ] **Hook slide is compelling** — would this stop someone scrolling LinkedIn?
- [ ] **Each slide delivers one idea** — not overloaded with information
- [ ] **Narrative flows logically** — each slide builds on the previous one
- [ ] **Takeaway slide is strong** — clear, memorable summary statement
- [ ] **Text is concise** — ~40 words max per slide
- [ ] **Diagrams are clear** — arrows and connections are easy to follow
- [ ] **Labels are descriptive** — each box/element is clearly labeled

### Technical Quality
- [ ] **All slides generated** — no missing slides in the sequence
- [ ] **Preview strip looks cohesive** — slides feel like they belong together
- [ ] **Files are organized** — saved in the correct date/topic directory

---

## Troubleshooting

| Issue | Fix |
|-------|-----|
| "Could not process image" for reference | The file is HTML, not an image. Run `file <path>` to confirm. Delete and download from a different source. |
| Slides look inconsistent in style | Always pass the 3 example slides via `--examples`. They anchor the visual style. |
| Text is too small or unreadable | Add explicit sizing instructions in the prompt: "Large, bold text that fills the top 20% of the slide." |
| Wrong aspect ratio | The script sets 1:1 automatically. If output looks wrong, check dimensions. |
| Colors don't match the style | Be explicit in every prompt: "#1A2332 background, #E07856 coral accents, white text." |
| Too many elements on one slide | Break the content across more slides. Each slide = one idea. |
| Arrows or flow is confusing | Simplify. Use fewer connections. Label everything. |
| No image returned | Simplify the prompt. Remove potentially flagged content. Retry. |
| API error or timeout | Check GEMINI_API_KEY is set. Check internet. Retry. |
| One slide fails | Others still save. Re-run just the failed one. |

---

## Output Format

Use today's date (YYYY-MM-DD format) for the date folder. Each carousel topic gets its own folder:

```
workspace/{today}/carousels/{topic-slug}/
  slide-1.png
  slide-2.png
  slide-3.png
  slide-4.png
  slide-5.png
  preview.png
  slide-2-v2.png    (iteration)
  preview-v2.png    (updated preview)
```

The scripts create directories automatically via `mkdir -p`.

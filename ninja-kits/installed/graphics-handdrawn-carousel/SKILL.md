---
name: handdrawn-carousel
description: "Generate hand-drawn style LinkedIn carousel slides using SVG blueprints rendered by Nano Banana Pro. Combines precise layout control from SVG with the sketchy PaperBanana whiteboard aesthetic. Two styles: color (warm cream, colored accents, doodles) and mono (black ink on white). Use when user says hand drawn carousel, sketchy carousel, whiteboard carousel, handdrawn slides, or wants carousels in the PaperBanana / gemini-diagram visual style."
---

# Hand-Drawn Carousel Generator

Generate LinkedIn carousel slides in the PaperBanana hand-drawn illustration style. Each slide is built as an SVG blueprint, critiqued for layout quality, then rendered through Nano Banana Pro for the sketchy whiteboard aesthetic.

This is the fusion of **gemini-diagram** (SVG blueprint + Nano Banana Pro rendering) with **linkedin-carousel** (narrative arc + slide sequencing + signature branding).

---

## When to Use This vs. linkedin-carousel

| Use **handdrawn-carousel** when | Use **linkedin-carousel** when |
|------|------|
| Content is educational, conceptual, or framework-based | Content needs polished dark cinematic or grid paper look |
| You want the warm, approachable PaperBanana style | You need device mockups, screenshots, or realistic visuals |
| Diagrams, flows, and comparisons are the core content | Photo backgrounds or dark themed slides are needed |
| The carousel should feel personal and human | The carousel should feel corporate/premium |

Default to **handdrawn-carousel** for educational content, frameworks, teardowns, and anything where the hand-drawn feel adds warmth and approachability.

---

## Visual Styles

### Color (Default)

Warm, playful, magazine-quality editorial illustration.

| Element | Value |
|---------|-------|
| Background | Warm cream `#FDF6E3` |
| Ink/outlines | Dark charcoal `#2D2D2D`, 2-3px strokes |
| Primary accent | Coral red `#EF6351` |
| Secondary accent | Sky blue `#4BA3D4` |
| Tertiary accent | Soft green `#6BBF6A` |
| Warm accent | Golden yellow `#F4C542` |
| Cool accent | Lavender `#9B7ED8` |
| Badge text | White `#FFFFFF` on colored pills |
| Font stack | `'Comic Neue', 'Segoe Print', 'Patrick Hand', system-ui, sans-serif` |

Visual elements: colored pill badges, bezier curve arrows, stick figures, doodle icons (lightbulbs, gears, stars), sparkles, confetti, squiggly underlines, speech bubbles.

### Mono

Clean, technical, authoritative. Black ink on cream.

| Element | Value |
|---------|-------|
| Ink | `currentColor` (works on light & dark backgrounds) |
| Background | Transparent or light cream |
| Emphasis | Opacity variations (0.08 to 1.0) and stroke-width (1.5 to 3.5) |

Visual elements: crosshatch fills, dashed connectors, bracket groups, bold weight shifts, panel grids. No color ever.

---

## Process

### Step 1: Plan the Narrative Arc

Same carousel psychology as linkedin-carousel — **Hook → Build → Takeaway.**

1. **What's the hook?** — Bold claim, question, or framework name that stops the scroll
2. **What's the build?** — 2-6 key points, each getting its own slide
3. **What's the takeaway?** — Summary statement or CTA on the final slide

Present the outline before building:
```
Carousel outline: "{topic}"
Style: color / mono
- Slide 1 (Hook): {description}
- Slide 2 ({type}): {description}
- Slide 3 ({type}): {description}
- ...
- Slide N (Takeaway): {description}
```

### Slide Count
- **3-5 slides** for single concepts
- **5-8 slides** for walkthroughs or frameworks
- **8-10 slides** max for deep dives
- Never more than 10

### Step 2: Build SVG Blueprints

For each slide, construct an SVG blueprint following the gemini-diagram construction rules adapted for 1:1 square format.

**SVG shell template (square carousel slide):**
```xml
<svg xmlns="http://www.w3.org/2000/svg"
  viewBox="0 0 800 800"
  style="max-width: 100%; height: auto; font-family: 'Comic Neue', 'Segoe Print', 'Patrick Hand', system-ui, sans-serif"
  role="img"
  aria-label="[Slide description]">
  <title>[Slide Title]</title>
  <desc>[Full description]</desc>

  <!-- Background (color style) -->
  <rect width="800" height="800" fill="#FDF6E3" rx="0" />

  <!-- Slide content -->

  <!-- ==================== SIGNATURE (every slide except last) ==================== -->
  <text x="70" y="782" font-size="11" font-weight="600" fill="#2D2D2D" opacity="0.35">@itstylergermain</text>
  <text x="730" y="782" text-anchor="end" font-size="11" font-weight="600" fill="#2D2D2D" opacity="0.35">save for later ↗</text>

  <!-- OR for last slide: full CREDITS BAR (see Credits Bar section) -->

</svg>
```

**Key differences from gemini-diagram SVG blueprints:**
- ViewBox is always `0 0 800 800` (square)
- More generous margins — 60px+ on all sides (content area: ~680x680)
- Maximum ~40 words per slide — keep text large and scannable
- One idea per slide — don't overload
- Headlines should be 28-36px font-size, readable at phone scale
- Signature branding is embedded directly in every SVG (not added as a post-render overlay)
- Slides 1 through N-1: subtle signature at bottom (`@itstylergermain` left, `save for later ↗` right)
- Last slide: full credits bar with IG + LinkedIn handles

**SVG construction rules carry over from gemini-diagram:**
- Hand-drawn path technique: 1-3px wobble in coordinates
- Bezier curves for arrows, never straight lines between distant elements
- Colored pill badges with `rx="15"`, filled accent color, white bold text
- Decorative elements (stars, sparkles, squiggles) scattered in empty space
- Stick figures for people, doodle icons for concepts
- Each list item gets a DIFFERENT accent color

### Slide Type SVG Patterns

#### Hook/Title Slide
```xml
<!-- Big bold headline centered -->
<text x="400" y="280" text-anchor="middle" font-size="42" font-weight="900" fill="#2D2D2D">
  BOLD CLAIM HERE
</text>
<!-- Subtitle or tease -->
<text x="400" y="340" text-anchor="middle" font-size="18" font-weight="600" fill="#2D2D2D" opacity="0.6">
  What you'll learn in this carousel
</text>
<!-- Central doodle illustration related to the topic -->
<!-- Decorative elements: stars, sparkles around headline -->
```

#### Architecture/Flow Slide
```xml
<!-- Left-to-right or top-to-bottom flow -->
<!-- Connected boxes with pill badges -->
<!-- Bezier curve arrows between elements -->
<!-- Small doodle icons inside or beside boxes -->
<!-- Bold section label at top -->
```

#### Comparison (A vs B) Slide
```xml
<!-- Two-column layout with center divider -->
<!-- Left column: old way / problem -->
<!-- Right column: new way / solution -->
<!-- "VS" label or zigzag divider in center -->
<!-- Red X marks on left, green checks on right -->
<!-- Bottom summary metric -->
```

#### List/Numbered Slide
```xml
<!-- 3-5 items, each with a different colored pill badge number -->
<!-- Bold key term + short description per item -->
<!-- Consistent vertical spacing -->
<!-- Optional small doodle icon per item -->
```

#### Takeaway/CTA Slide
```xml
<!-- Big bold summary statement centered -->
<!-- Optional "Comment [WORD]" CTA with arrow pointing down -->
<!-- Credits bar at bottom (IG + LinkedIn handles) -->
<!-- Decorative celebration elements: confetti, stars -->
```

### Step 3: SVG Critique (Sub-Agent)

**ALWAYS run this step for EVERY slide.** After writing each SVG, launch a sub-agent to critique and fix the blueprint.

Batch all slide SVGs into one critique pass when possible. Use the Task tool with `subagent_type="general-purpose"`:

```
Read the SVG files at:
- workspace/{date}/handdrawn-carousel/{slug}/slide-1-blueprint.svg
- workspace/{date}/handdrawn-carousel/{slug}/slide-2-blueprint.svg
- ...

These are carousel slide blueprints. Critique each for:
- Overlapping text or elements
- Text alignment (miscentered labels, text overflowing containers)
- Spacing problems (too close, too far, unbalanced)
- Arrow/connector clarity
- Badge/pill sizing (text clipped or too small?)
- Visual balance within the 800x800 viewBox
- Text readability at phone size (font-size >= 14 for body, >= 28 for headlines)
- Content fits within 60px margin zone

Fix any issues by editing each SVG directly. Do NOT rewrite entire files.
Keep all IMAGE placeholder comments intact.
```

### Step 4: Render with Nano Banana Pro (Parallel Sub-Agents)

**Render ALL slides in parallel** using the Task tool. Launch one sub-agent per slide — they all run concurrently, so an 8-slide carousel renders in the same time as a single slide (~30s).

Use the Task tool with `subagent_type="general-purpose"` for each slide. Send ALL Task calls in a single message so they run in parallel:

```
For each slide (1 through N), launch a sub-agent with this prompt:

"Run this command and report the result:
cd '/Users/tyler/Developer/Claude Code/gemini-diagram' && python3 .claude/skills/handdrawn-carousel/scripts/generate_handdrawn_slide.py \
  --svg 'workspace/{date}/handdrawn-carousel/{slug}/slide-{N}-blueprint.svg' \
  --output 'workspace/{date}/handdrawn-carousel/{slug}/slide-{N}.png' \
  --no-images"
```

**IMPORTANT:** Send all Task tool calls in ONE message block. Do NOT wait for one slide to finish before starting the next. The whole point is full parallelism.

**With reference images (logos, icons):** Add `--reference "path/to/image.png"` to the command.

**Mono style:** Add `--style mono` to the command.

**Script options:**

| Flag | Description |
|------|-------------|
| `--svg FILE` | SVG blueprint path (primary mode) |
| `--prompt TEXT` | Text prompt (alone = text-only, with --svg = extra instructions) |
| `-o, --output FILE` | Output PNG path — required |
| `--style` | `color` (default) or `mono` |
| `--reference` | Additional image files (logos, icons) |
| `--no-images` | Skip Tavily search for IMAGE placeholders |
| `--ref-dir` | Style reference directory (default: `ref/`) |
| `--env` | .env file path (default: `.env`) |

### Step 4.5: Visual QA — Inspect Every Rendered Slide

**ALWAYS run this step. Never skip it.** After rendering, visually inspect every slide PNG using the Read tool. Check for:

1. **Centering** — Is the main content block centered horizontally? Is it vertically balanced in the available space (accounting for any title at top and footer at bottom)?
2. **Spacing** — Are there even margins on all sides? Does content feel cramped against any edge? Is there dead/wasted space that could be filled by repositioning?
3. **Text readability** — Can you read all text at the rendered size? Are labels cut off or overlapping?
4. **Element overlap** — Are any elements colliding or stacking on top of each other?
5. **Visual balance** — Does the slide feel lopsided? Is one side heavier than the other?

**If anything is off, fix it before moving on:**
- Go back to the SVG blueprint, adjust positions/sizes, re-run the critique sub-agent, and re-render
- For composited slides (diagram on background), adjust `--width`, `--position`, and `--y-offset` in composite_diagram.py until the diagram sits centered in the content zone between title and footer
- Keep iterating until the output looks polished — the user should never have to ask "can you center this"

**Compositing centering formula:**
When compositing a diagram onto a slide background with a title and footer, the diagram should be centered in the **content zone** (the space between title bottom and footer top), not the full slide. Calculate:
```
content_zone_top = title_bottom_y + padding
content_zone_bottom = footer_top_y - padding
content_zone_center = (content_zone_top + content_zone_bottom) / 2
y_offset = content_zone_center - (slide_height / 2)
```
Then pass `--y-offset {value}` to composite_diagram.py.

**This step is what separates good output from great output.** Every slide should look intentionally designed, not just generated.

### Step 5: Signature Branding (Embedded in SVGs — No Post-Render Overlay)

Signatures are embedded directly in every SVG blueprint during Step 2. **Do NOT use add_signature.py** — it adds an external strip that overlaps with bottom content on hand-drawn slides.

**Slides 1 through N-1** get a subtle embedded signature:
```xml
<!-- ==================== SIGNATURE ==================== -->
<text x="70" y="782" font-size="11" font-weight="600" fill="#2D2D2D" opacity="0.35">@itstylergermain</text>
<text x="730" y="782" text-anchor="end" font-size="11" font-weight="600" fill="#2D2D2D" opacity="0.35">save for later ↗</text>
```

**Last slide** gets the full credits bar (IG + LinkedIn handles) — see the Credits Bar section.

This approach renders the branding as part of the hand-drawn image, maintaining visual consistency and avoiding overlapping strips.

### Step 6: Create Preview

Combine all slides into a preview strip:

```bash
python3 linkedin-carousel/scripts/combine_slides.py \
  --images workspace/{date}/handdrawn-carousel/{slug}/slide-1.png \
           workspace/{date}/handdrawn-carousel/{slug}/slide-2.png \
           workspace/{date}/handdrawn-carousel/{slug}/slide-3.png \
  --output workspace/{date}/handdrawn-carousel/{slug}/preview.png
```

For 6+ slides, add `--grid` for a 2-column layout.

### Step 7: Present & Iterate

Show the preview and describe each slide. For revisions, re-edit the SVG blueprint for the specific slide, re-run critique, and re-render just that slide.

When iterating, pass the current rendered slide as a `--reference` so Nano Banana Pro can refine it:

```bash
python3 .claude/skills/handdrawn-carousel/scripts/generate_handdrawn_slide.py \
  --svg "workspace/{date}/handdrawn-carousel/{slug}/slide-3-blueprint.svg" \
  --reference "workspace/{date}/handdrawn-carousel/{slug}/slide-3.png" \
  --prompt "Keep same layout but make the arrows more prominent" \
  --output "workspace/{date}/handdrawn-carousel/{slug}/slide-3-v2.png"
```

---

## SVG Construction Reference

### Hand-Drawn Path Technique

Avoid mechanical straight lines. Add 1-3px of wobble:

```xml
<!-- Mechanical (avoid) -->
<line x1="100" y1="200" x2="400" y2="200" />

<!-- Hand-drawn (use this) -->
<path d="M 100 200 Q 250 197 400 201" />
```

For rectangles, use wobbly `<path>` instead of `<rect>`:
```xml
<path d="M 108 100 L 348 102 Q 352 102 352 108 L 350 248 Q 350 252 346 252 L 106 250 Q 102 250 102 246 L 104 106 Q 104 102 108 102 Z"
      stroke="#2D2D2D" stroke-width="2.5" fill="none" />
```

### Badge / Pill Construction
```xml
<g transform="translate(50, 100)">
  <rect width="120" height="30" rx="15" fill="#EF6351" stroke="#2D2D2D" stroke-width="1.5" />
  <text x="60" y="20" text-anchor="middle" font-size="13" font-weight="800" fill="#FFFFFF">Label</text>
</g>
```

### Curved Arrow
```xml
<path d="M 100 300 C 200 310, 300 180, 390 200"
      stroke="#4BA3D4" stroke-width="4" fill="none" />
<polygon points="390,200 378,192 380,206" fill="#4BA3D4" />
```

### Decorative Elements
```xml
<!-- 4-point star -->
<path d="M 0 -8 L 2 -2 L 8 0 L 2 2 L 0 8 L -2 2 L -8 0 L -2 -2 Z"
      fill="#F4C542" transform="translate(X, Y)" />

<!-- Sparkle -->
<g transform="translate(X, Y)" stroke="#F4C542" stroke-width="1.5" stroke-linecap="round">
  <line x1="0" y1="-5" x2="0" y2="5" />
  <line x1="-5" y1="0" x2="5" y2="0" />
</g>

<!-- Squiggly underline -->
<path d="M X Y q 5 -4 10 0 q 5 4 10 0 q 5 -4 10 0" stroke="#EF6351" stroke-width="2" fill="none" />
```

### Stick Figure
```xml
<g transform="translate(200, 150)">
  <circle cx="0" cy="0" r="12" stroke="#2D2D2D" stroke-width="2" fill="#4BA3D4" />
  <line x1="0" y1="12" x2="0" y2="45" stroke="#2D2D2D" stroke-width="2.5" />
  <line x1="0" y1="22" x2="-18" y2="10" stroke="#2D2D2D" stroke-width="2" />
  <line x1="0" y1="22" x2="18" y2="10" stroke="#2D2D2D" stroke-width="2" />
  <line x1="0" y1="45" x2="-12" y2="65" stroke="#2D2D2D" stroke-width="2" />
  <line x1="0" y1="45" x2="12" y2="65" stroke="#2D2D2D" stroke-width="2" />
</g>
```

### Image Placeholders

Add `<!-- IMAGE: description -->` comments near SVG elements where a real reference photo helps Nano Banana Pro understand what to draw:

```xml
<!-- IMAGE: Claude Code terminal with dark theme -->
<!-- IMAGE: robot mascot friendly illustration -->
```

Use 0-3 per slide (fewer than full diagrams — slides are simpler).

---

## Branding Zones

### Signature (Slides 1 through N-1)

Every slide except the last gets a subtle embedded signature at the very bottom of the SVG (y=782, below the 60px margin content zone). This renders as part of the hand-drawn image:

```xml
<!-- ==================== SIGNATURE ==================== -->
<text x="70" y="782" font-size="11" font-weight="600" fill="#2D2D2D" opacity="0.35">@itstylergermain</text>
<text x="730" y="782" text-anchor="end" font-size="11" font-weight="600" fill="#2D2D2D" opacity="0.35">save for later ↗</text>
```

### Credits Bar (Last Slide Only)

The last slide gets a full credits bar with both social handles. Include this in the SVG:

```xml
<!-- ==================== CREDITS BAR ==================== -->
<g transform="translate(400, 760)">
  <path d="M -320 -18 Q -160 -21 0 -18 Q 160 -15 320 -18"
        stroke="#2D2D2D" stroke-width="0.8" opacity="0.15" fill="none" />

  <!-- Instagram -->
  <rect x="-180" y="-7" width="16" height="16" rx="4" fill="#E1306C"
        stroke="#2D2D2D" stroke-width="1" />
  <circle cx="-172" cy="1" r="4" stroke="#FFFFFF" stroke-width="1.2" fill="none" />
  <circle cx="-172" cy="1" r="1.2" fill="#FFFFFF" />
  <text x="-158" y="5" text-anchor="start" font-size="13" font-weight="700"
        fill="#E1306C">@itstylergermain</text>

  <circle cx="0" cy="1" r="2.5" fill="#2D2D2D" opacity="0.3" />

  <!-- LinkedIn -->
  <text x="158" y="5" text-anchor="end" font-size="13" font-weight="700"
        fill="#0A66C2">@tylergermain</text>
  <rect x="164" y="-7" width="16" height="16" rx="3" fill="#0A66C2"
        stroke="#2D2D2D" stroke-width="1" />
  <text x="168" y="7" font-size="11" font-weight="900" fill="#FFFFFF">in</text>
</g>
```

---

## Quality Checklist

### Per-Slide SVG Quality
- [ ] ViewBox is `0 0 800 800` (square)
- [ ] Content within 60px margin zone (content area ~680x680)
- [ ] Maximum ~40 words on the slide
- [ ] Headline font-size >= 28, body >= 14
- [ ] Hand-drawn feel: wobbly paths, bezier arrows, no mechanical lines
- [ ] Style correct: color palette OR mono (not mixed)
- [ ] One main idea per slide
- [ ] No overlapping text or elements
- [ ] Image placeholders where reference photos help (0-3 per slide)

### Carousel Quality
- [ ] Hook slide stops the scroll
- [ ] Each slide builds on the previous
- [ ] Narrative flows: Hook → Build → Takeaway
- [ ] Takeaway slide has clear summary or CTA
- [ ] Consistent style across all slides (same palette, fonts, element styles)
- [ ] Slide count within range (3-10)
- [ ] Credits bar on last slide SVG
- [ ] Embedded signatures on all other slides (in SVG, not post-render overlay)
- [ ] Preview strip generated for review

### Rendering Quality (Visually Inspect Every Slide)
- [ ] All Nano Banana Pro renders successful
- [ ] **Every slide visually inspected** via Read tool after rendering
- [ ] Content is **centered** — horizontally and vertically balanced in available space
- [ ] **Even spacing** on all sides — no content cramped against edges, no large dead zones
- [ ] Text is readable in final PNGs at phone size — no cut-off or overlapping labels
- [ ] No elements colliding or stacking on each other
- [ ] Diagrams and arrows clear in rendered output
- [ ] Consistent hand-drawn aesthetic across all rendered slides
- [ ] If composited: diagram centered in content zone between title and footer, not just slide center
- [ ] **If anything looks off: fixed before presenting to user** — re-edit SVG, re-render, re-check

---

## Troubleshooting

| Issue | Fix |
|-------|-----|
| Text overlaps in rendered slide | Edit SVG to increase spacing, re-run critique sub-agent |
| Nano Banana Pro ignores SVG layout | Simplify SVG — fewer elements, clearer structure |
| Text too small in rendered output | Increase font-size in SVG blueprint (min 14 for body) |
| Arrows unclear | Use thicker strokes (4-6px) and larger arrowheads |
| Style inconsistent between slides | Ensure all SVGs use same color palette and element patterns |
| Slide looks too crowded | Remove elements — one idea per slide, max 40 words |
| Render fails | Simplify SVG, check GEMINI_API_KEY, retry |
| Tavily search fails | Add `--no-images` flag, or check TAVILY_API_KEY |

---

## Output Format

```
workspace/{date}/handdrawn-carousel/{topic-slug}/
  slide-1-blueprint.svg     # SVG blueprints (intermediate)
  slide-2-blueprint.svg
  slide-3-blueprint.svg
  slide-1.png               # Rendered hand-drawn slides
  slide-2.png
  slide-3.png
  preview.png               # Combined preview strip
  slide-2-v2.png            # Iterations
  preview-v2.png            # Updated preview
```

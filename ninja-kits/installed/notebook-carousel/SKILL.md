---
name: notebook-carousel
description: "Generate LinkedIn carousel slides that look like pages from a spiral-bound dotted notebook. Features hand-drawn marker text, colorful doodle icons, speech bubbles, highlighter accents, and black spiral binding on the left edge. Rendered via Nano Banana Pro from SVG blueprints. Use when user says notebook carousel, notebook slides, spiral notebook, dotted notebook, journal carousel, or wants the notebook/journal visual style for carousel slides."
---

# Notebook Carousel Generator

Generate LinkedIn carousel slides that look like pages from a spiral-bound dotted notebook — hand-drawn marker text, colorful doodle icons, speech bubbles, highlighter accents, and black spiral coil binding on the left edge.

Built on the same SVG blueprint → Nano Banana Pro pipeline as gemini-diagram and handdrawn-carousel, but with a distinct notebook/journal aesthetic.

---

## The Notebook Style

Every slide looks like a page torn from someone's dotted notebook where they drew out a concept with markers and highlighters.

### Defining Visual Elements

| Element | Description |
|---------|-------------|
| **Spiral binding** | Black oval coils running down the LEFT edge (~12-15 coils). This is the #1 signature element — mandatory on every slide |
| **Dotted paper** | Warm cream/off-white background with evenly spaced small dots |
| **Marker text** | Bold, hand-drawn lettering — like thick felt-tip marker. Slightly imperfect, never perfectly aligned |
| **Doodle icons** | Simple, colorful hand-drawn icons — gears, folders, files, lightning bolts, checkmarks, stars |
| **Speech bubbles** | Light blue fill with hand-drawn dark outline — for quotes, commands, user input |
| **Highlighter strips** | Yellow or green rectangles behind key takeaway text at bottom of slides |
| **Comparison boxes** | Red-bordered (with X) vs green-bordered (with checkmark) for A/B comparisons |

### Color Palette

| Element | Color | Hex | Usage |
|---------|-------|-----|-------|
| Paper | Warm cream | `#F5F0E8` | Background fill |
| Ink | Rich black | `#1A1A1A` | Primary text, outlines |
| Blue | Bright blue | `#3B82F6` | Titles, speech bubbles, download icons, arrows |
| Green | Vibrant green | `#22C55E` | Checkmarks, success boxes, highlight strips |
| Red | Coral red | `#EF4444` | X marks, warning/wrong boxes |
| Orange | Warm orange | `#F97316` | Gear icons, settings, asterisk/star shapes |
| Purple | Rich purple | `#8B5CF6` | Special titles, plugin icons, accent text |
| Yellow | Bright yellow | `#FDE047` | Highlighter strips behind text |
| Teal | Mint teal | `#2DD4BF` | Document/file icons |
| Gold | Deep gold | `#EAB308` | Star decorations |

### Slide Type Patterns

#### Cover/Hook Slide
- Large bold black headline at top ("How to Set Up Claude")
- Central colorful illustration/icon cluster related to the topic
- Subtitle in blue text below illustration
- Author credit at bottom in smaller text
- Colorful doodle icons scattered around the central element

#### Comparison (A vs B) Slide
- Bold title centered at top ("Prompts vs Skills")
- Two boxes side by side:
  - LEFT: Red border, red X mark above → the wrong/old way
  - RIGHT: Green border, green checkmark above → the right/new way
- Brief label inside each box + description below
- Yellow/green highlighter strip at bottom with the key insight

#### Steps/How-To Slide
- Bold title at top (can be in color — blue or purple)
- Speech bubble with user intent/command
- Numbered or arrowed list of steps below
- Each step gets a brief one-line description
- Green highlighter strip at bottom with the key principle

#### Numbered List Slide
- Bold colored title at top (purple works well)
- 3-5 numbered items with colorful icons beside each:
  - Step 1: Blue download icon + description
  - Step 2: Orange gear icon + description
  - Step 3: Green checkmark icon + description
- Clean vertical spacing between items

#### Takeaway/CTA Slide
- Bold summary statement or call to action
- Optional celebratory doodles (stars, checkmarks)
- Credits/handles at bottom
- Can include "Comment [KEYWORD]" CTA with arrow

---

## Process

### Step 1: Plan the Narrative Arc

Same carousel psychology — **Hook → Build → Takeaway.**

1. **Hook** — Cover slide that stops the scroll. Bold title + central illustration.
2. **Build** — 3-6 content slides, each one concept. Mix slide types for variety.
3. **Takeaway** — Summary or CTA slide.

Present the outline before building:
```
Notebook carousel: "{topic}"
- Slide 1 (Cover): {title} + {central illustration concept}
- Slide 2 ({type}): {concept}
- Slide 3 ({type}): {concept}
- ...
- Slide N (Takeaway): {summary/CTA}
```

### Slide Count
- **4-6 slides** for single concepts (sweet spot)
- **6-8 slides** for tutorials or walkthroughs
- **8-10 slides** max for comprehensive guides

### Step 2: Build SVG Blueprints

For each slide, construct an SVG blueprint at `0 0 800 800` (square).

**SVG shell template:**
```xml
<svg xmlns="http://www.w3.org/2000/svg"
  viewBox="0 0 800 800"
  style="max-width: 100%; height: auto; font-family: 'Comic Neue', 'Segoe Print', 'Patrick Hand', system-ui, sans-serif"
  role="img"
  aria-label="[Slide description]">
  <title>[Slide Title]</title>
  <desc>[Full description]</desc>

  <!-- Background: dotted paper -->
  <rect width="800" height="800" fill="#F5F0E8" />

  <!-- Dot pattern -->
  <pattern id="dots" x="0" y="0" width="24" height="24" patternUnits="userSpaceOnUse">
    <circle cx="12" cy="12" r="1" fill="#C4B8A8" opacity="0.5" />
  </pattern>
  <rect width="800" height="800" fill="url(#dots)" />

  <!-- Spiral binding (left edge) -->
  <g id="spiral-binding">
    <rect x="0" y="0" width="45" height="800" fill="#E8E0D4" />
    <line x1="45" y1="0" x2="45" y2="800" stroke="#C4B8A8" stroke-width="1" />
    <!-- Coils (12-15 evenly spaced) -->
    <ellipse cx="35" cy="55" rx="18" ry="10" fill="none" stroke="#2D2D2D" stroke-width="3.5" />
    <ellipse cx="35" cy="115" rx="18" ry="10" fill="none" stroke="#2D2D2D" stroke-width="3.5" />
    <ellipse cx="35" cy="175" rx="18" ry="10" fill="none" stroke="#2D2D2D" stroke-width="3.5" />
    <ellipse cx="35" cy="235" rx="18" ry="10" fill="none" stroke="#2D2D2D" stroke-width="3.5" />
    <ellipse cx="35" cy="295" rx="18" ry="10" fill="none" stroke="#2D2D2D" stroke-width="3.5" />
    <ellipse cx="35" cy="355" rx="18" ry="10" fill="none" stroke="#2D2D2D" stroke-width="3.5" />
    <ellipse cx="35" cy="415" rx="18" ry="10" fill="none" stroke="#2D2D2D" stroke-width="3.5" />
    <ellipse cx="35" cy="475" rx="18" ry="10" fill="none" stroke="#2D2D2D" stroke-width="3.5" />
    <ellipse cx="35" cy="535" rx="18" ry="10" fill="none" stroke="#2D2D2D" stroke-width="3.5" />
    <ellipse cx="35" cy="595" rx="18" ry="10" fill="none" stroke="#2D2D2D" stroke-width="3.5" />
    <ellipse cx="35" cy="655" rx="18" ry="10" fill="none" stroke="#2D2D2D" stroke-width="3.5" />
    <ellipse cx="35" cy="715" rx="18" ry="10" fill="none" stroke="#2D2D2D" stroke-width="3.5" />
  </g>

  <!-- Content area starts at x=70, giving room after the binding -->
  <!-- Content -->

</svg>
```

**Key layout rules:**
- Content area: x=70 to x=760 (after spiral binding, with right margin)
- Content center: x=415 (centered in the content area, not the full slide)
- Top margin: y=60+
- Bottom margin: y=740-
- Max ~30 words per slide
- Headlines: font-size 36-48, font-weight 900
- Body: font-size 18-24, font-weight 600
- All text hand-drawn style — use the Comic Neue / Patrick Hand font stack

### SVG Element Patterns

#### Speech Bubble
```xml
<g transform="translate(120, 200)">
  <!-- Bubble body -->
  <rect x="0" y="0" width="560" height="100" rx="20" fill="#DBEAFE" stroke="#3B82F6" stroke-width="2.5" />
  <!-- Tail -->
  <path d="M 60 100 L 40 130 L 90 100" fill="#DBEAFE" stroke="#3B82F6" stroke-width="2.5" />
  <!-- Text inside -->
  <text x="280" y="55" text-anchor="middle" font-size="20" font-weight="600" fill="#1A1A1A">
    I want to create a Skill for
  </text>
  <text x="280" y="80" text-anchor="middle" font-size="20" font-weight="600" fill="#1A1A1A">
    writing weekly client updates.
  </text>
</g>
```

#### Highlighter Strip
```xml
<g transform="translate(100, 680)">
  <!-- Yellow/green highlight background -->
  <rect x="-10" y="-8" width="580" height="36" rx="4" fill="#FDE047" opacity="0.7" />
  <!-- Text on top -->
  <text x="0" y="18" font-size="20" font-weight="700" fill="#1A1A1A">
    Write it once. Claude follows it every time.
  </text>
</g>
```

#### Comparison Boxes
```xml
<!-- Red (wrong) box -->
<g transform="translate(80, 250)">
  <rect x="0" y="0" width="280" height="180" rx="12" fill="none" stroke="#EF4444" stroke-width="3" />
  <!-- Red X above -->
  <g transform="translate(140, -20)">
    <line x1="-12" y1="-12" x2="12" y2="12" stroke="#EF4444" stroke-width="5" stroke-linecap="round" />
    <line x1="12" y1="-12" x2="-12" y2="12" stroke="#EF4444" stroke-width="5" stroke-linecap="round" />
  </g>
  <text x="140" y="70" text-anchor="middle" font-size="28" font-weight="800" fill="#1A1A1A">A Prompt</text>
  <text x="140" y="120" text-anchor="middle" font-size="18" font-weight="600" fill="#555">Dies when the</text>
  <text x="140" y="145" text-anchor="middle" font-size="18" font-weight="600" fill="#555">chat ends.</text>
</g>

<!-- Green (right) box -->
<g transform="translate(420, 250)">
  <rect x="0" y="0" width="280" height="180" rx="12" fill="none" stroke="#22C55E" stroke-width="3" />
  <!-- Green checkmark above -->
  <g transform="translate(140, -15)">
    <path d="M -12 0 L -3 10 L 14 -10" stroke="#22C55E" stroke-width="5" fill="none" stroke-linecap="round" stroke-linejoin="round" />
  </g>
  <text x="140" y="70" text-anchor="middle" font-size="28" font-weight="800" fill="#1A1A1A">A Skill</text>
  <text x="140" y="120" text-anchor="middle" font-size="18" font-weight="600" fill="#555">Persists forever.</text>
</g>
```

#### Numbered Step with Icon
```xml
<g transform="translate(80, 250)">
  <!-- Number -->
  <text x="0" y="40" font-size="32" font-weight="900" fill="#1A1A1A">1.</text>
  <!-- Icon (blue download arrow) -->
  <g transform="translate(60, 10)">
    <rect x="0" y="20" width="40" height="6" rx="2" fill="#3B82F6" />
    <path d="M 20 0 L 20 25 M 8 15 L 20 28 L 32 15" stroke="#3B82F6" stroke-width="4" fill="none" stroke-linecap="round" stroke-linejoin="round" />
  </g>
  <!-- Label -->
  <text x="120" y="38" font-size="24" font-weight="700" fill="#1A1A1A">Download the file</text>
</g>
```

#### Doodle Icon Library
```xml
<!-- Gear (orange) -->
<g transform="translate(X, Y)">
  <circle cx="0" cy="0" r="16" fill="#F97316" stroke="#1A1A1A" stroke-width="2" />
  <circle cx="0" cy="0" r="6" fill="#F5F0E8" stroke="#1A1A1A" stroke-width="2" />
  <!-- Teeth -->
  <rect x="-4" y="-22" width="8" height="10" rx="2" fill="#F97316" stroke="#1A1A1A" stroke-width="1.5" />
  <rect x="-4" y="12" width="8" height="10" rx="2" fill="#F97316" stroke="#1A1A1A" stroke-width="1.5" />
  <rect x="-22" y="-4" width="10" height="8" rx="2" fill="#F97316" stroke="#1A1A1A" stroke-width="1.5" />
  <rect x="12" y="-4" width="10" height="8" rx="2" fill="#F97316" stroke="#1A1A1A" stroke-width="1.5" />
</g>

<!-- Folder (yellow) -->
<g transform="translate(X, Y)">
  <path d="M 0 8 L 0 32 L 40 32 L 40 8 L 22 8 L 18 0 L 0 0 Z" fill="#FDE047" stroke="#1A1A1A" stroke-width="2" rx="3" />
</g>

<!-- Document (teal) -->
<g transform="translate(X, Y)">
  <rect x="0" y="0" width="28" height="36" rx="3" fill="#99F6E4" stroke="#1A1A1A" stroke-width="2" />
  <line x1="6" y1="10" x2="22" y2="10" stroke="#1A1A1A" stroke-width="1.5" />
  <line x1="6" y1="18" x2="22" y2="18" stroke="#1A1A1A" stroke-width="1.5" />
  <line x1="6" y1="26" x2="16" y2="26" stroke="#1A1A1A" stroke-width="1.5" />
</g>

<!-- Lightning bolt (blue) -->
<g transform="translate(X, Y)">
  <path d="M 12 0 L 0 18 L 10 18 L 6 32 L 22 12 L 12 12 Z" fill="#3B82F6" stroke="#1A1A1A" stroke-width="1.5" />
</g>

<!-- Checkmark circle (green) -->
<g transform="translate(X, Y)">
  <circle cx="16" cy="16" r="16" fill="#22C55E" stroke="#1A1A1A" stroke-width="2" />
  <path d="M 8 16 L 14 22 L 26 10" stroke="white" stroke-width="3" fill="none" stroke-linecap="round" stroke-linejoin="round" />
</g>

<!-- Star/asterisk (orange) -->
<g transform="translate(X, Y)">
  <path d="M 0 -14 L 3 -4 L 13 -4 L 5 3 L 8 13 L 0 7 L -8 13 L -5 3 L -13 -4 L -3 -4 Z"
        fill="#F97316" stroke="#1A1A1A" stroke-width="1.5" />
</g>

<!-- Plug (purple) -->
<g transform="translate(X, Y)">
  <circle cx="14" cy="20" r="14" fill="#8B5CF6" stroke="#1A1A1A" stroke-width="2" />
  <rect x="8" y="0" width="4" height="12" rx="2" fill="#1A1A1A" />
  <rect x="18" y="0" width="4" height="12" rx="2" fill="#1A1A1A" />
</g>
```

### Step 3: SVG Critique (Sub-Agent)

**ALWAYS run this step.** After writing SVG blueprints, launch a sub-agent to critique and fix them.

```
Read the SVG files at:
- workspace/{date}/notebook-carousel/{slug}/slide-1-blueprint.svg
- workspace/{date}/notebook-carousel/{slug}/slide-2-blueprint.svg
- ...

These are notebook-style carousel slide blueprints. Critique each for:
- Spiral binding present on left edge with 12+ coils
- Dotted paper background pattern present
- Content starts at x=70+ (after binding)
- Text alignment and centering within content area (centered at x=415, not x=400)
- Overlapping elements or text
- Spacing and visual balance
- Text readability (headlines >= 28px, body >= 18px)
- Max ~30 words per slide
- Highlighter strips behind key text properly sized
- Speech bubbles properly closed with tail
- Icons colorful and appropriately sized

Fix any issues by editing each SVG directly. Do NOT rewrite entire files.
Keep all IMAGE placeholder comments intact.
```

### Step 4: Render with Nano Banana Pro

Generate each slide in parallel (batch 4 at a time).

**With example images (best results — strongly recommended):**
```bash
python3 .claude/skills/notebook-carousel/scripts/generate_notebook_slide.py \
  --svg "workspace/{date}/notebook-carousel/{slug}/slide-1-blueprint.svg" \
  --examples ".claude/skills/notebook-carousel/examples/cover.png" \
             ".claude/skills/notebook-carousel/examples/comparison.png" \
  --output "workspace/{date}/notebook-carousel/{slug}/slide-1.png"
```

**Without examples:**
```bash
python3 .claude/skills/notebook-carousel/scripts/generate_notebook_slide.py \
  --svg "workspace/{date}/notebook-carousel/{slug}/slide-1-blueprint.svg" \
  --output "workspace/{date}/notebook-carousel/{slug}/slide-1.png"
```

**Script options:**

| Flag | Description |
|------|-------------|
| `--svg FILE` | SVG blueprint path (primary mode) |
| `--prompt TEXT` | Text prompt (alone = text-only, with --svg = extra instructions) |
| `-o, --output FILE` | Output PNG path — required |
| `--examples` | Example notebook slides for style matching (strongly recommended) |
| `--reference` | Additional images (logos, icons) |
| `--no-images` | Skip Tavily search for IMAGE placeholders |
| `--ref-dir` | Style reference directory (default: `ref/`) |
| `--env` | .env file path (default: `.env`) |

### Step 4.5: Visual QA — Inspect Every Slide

**ALWAYS do this. Never skip.** After rendering, visually inspect every slide PNG using the Read tool.

Check each slide for:
1. **Spiral binding** — Present on left edge? Black coils clearly visible?
2. **Dotted paper** — Cream background with dot pattern?
3. **Centering** — Content centered in the content area (x=70 to x=760), not the full slide?
4. **Spacing** — Even margins? Nothing crammed? No wasted dead zones?
5. **Text readability** — All text legible at phone size? Nothing cut off or overlapping?
6. **Icon quality** — Doodle icons colorful and recognizable?
7. **Highlighter strips** — Properly behind text, not covering it?
8. **Consistency** — Does this slide match the notebook style of other slides in the set?

**If anything looks off, fix it before moving on.** Re-edit the SVG, re-critique, re-render. The user should never have to point out centering or spacing issues.

### Step 5: Signature Branding

Signatures are embedded directly in the SVG blueprints as subtle text near the bottom. Do NOT use add_signature.py — the notebook aesthetic requires the branding to look hand-drawn like everything else.

```xml
<!-- Embedded signature (all slides except last) -->
<text x="80" y="782" font-size="11" font-weight="600" fill="#888" opacity="0.6">@itstylergermain</text>
<text x="720" y="782" text-anchor="end" font-size="11" font-weight="600" fill="#888" font-style="italic" opacity="0.6">save for later</text>
```

**First slide (hook):** Use "swipe →" instead of "save for later" on the right side. Optionally include handles if they fit.

**Last slide:** Include full credits bar with both handles:
```xml
<text x="80" y="775" font-size="13" font-weight="700" fill="#888">IG @itstylergermain</text>
<text x="720" y="775" text-anchor="end" font-size="13" font-weight="700" fill="#888">LI @tylergermain</text>
```

### Step 6: Create Preview

```bash
python3 linkedin-carousel/scripts/combine_slides.py \
  --images workspace/{date}/notebook-carousel/{slug}/slide-1.png \
           workspace/{date}/notebook-carousel/{slug}/slide-2.png \
           workspace/{date}/notebook-carousel/{slug}/slide-3.png \
  --output workspace/{date}/notebook-carousel/{slug}/preview.png
```

For 6+ slides, add `--grid`.

### Step 7: Present & Iterate

Show the preview. For revisions, edit the specific SVG blueprint, re-critique, re-render just that slide.

---

## Quality Checklist

### Per-Slide Quality
- [ ] Spiral binding on left edge with 12+ black coils
- [ ] Dotted paper background
- [ ] Content in the x=70 to x=760 zone (after binding, before right edge)
- [ ] Content centered at x=415 (center of content area)
- [ ] Max ~30 words
- [ ] Headlines bold and large (>= 28px)
- [ ] Hand-drawn feel — wobbly lines, imperfect shapes
- [ ] Colorful doodle icons where appropriate
- [ ] No overlapping text or elements
- [ ] Embedded signature text at bottom

### Carousel Quality
- [ ] Hook slide stops the scroll — bold title + colorful illustration
- [ ] Each slide = one concept
- [ ] Narrative flows: Hook → Build → Takeaway
- [ ] Mix of slide types (comparison, steps, list, etc.)
- [ ] Consistent notebook style across all slides
- [ ] Slide count 4-10
- [ ] Full credits on last slide

### Rendering Quality (Visual QA)
- [ ] **Every slide visually inspected** via Read tool
- [ ] Spiral binding visible and consistent across all slides
- [ ] Dotted paper texture present
- [ ] Content properly centered and spaced
- [ ] Text readable at phone size
- [ ] Colors vibrant and matching palette
- [ ] **Any issues fixed before presenting to user**

---

## Troubleshooting

| Issue | Fix |
|-------|-----|
| No spiral binding in render | Make it more prominent in SVG — thicker strokes, more contrast. Add explicit instruction in --prompt |
| Dots not visible | Increase dot size or opacity in SVG pattern |
| Content overlaps binding | Move content start to x=80+ |
| Text too small | Increase font-size (min 18 for body, 28+ for headlines) |
| Icons not colorful | Use explicit fill colors in SVG, not just stroke |
| Highlighter covers text | Ensure highlight rect is BEFORE text in SVG draw order |
| Style inconsistent between slides | Pass same examples via --examples for every slide |

---

## Output Format

```
workspace/{date}/notebook-carousel/{topic-slug}/
  slide-1-blueprint.svg
  slide-2-blueprint.svg
  slide-3-blueprint.svg
  slide-1.png
  slide-2.png
  slide-3.png
  preview.png
  slide-2-v2.png        # iterations
  preview-v2.png
```

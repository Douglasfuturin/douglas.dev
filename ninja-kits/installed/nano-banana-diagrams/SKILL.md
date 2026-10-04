---
name: nano-banana-diagrams
description: "Generate hand-drawn style conceptual diagrams as inline SVG inspired by PaperBanana / Gemini Nano Banana Pro visual language. Two styles: color (warm pastel palette with colored arrows, badges, mascots, confetti) and mono (pure black-and-white sketchy ink with thick outlines, dashed connectors, crosshatch fills). Use when user says diagram, gemini diagram, sketch diagram, hand drawn diagram, concept diagram, architecture diagram, flow diagram, visual explainer, or infographic."
---

# Gemini Diagram -- Hand-Drawn Conceptual Diagrams

Two-phase pipeline: Claude Code generates an SVG blueprint with image
placeholders, then Nano Banana Pro renders it as a gorgeous hand-drawn
illustration.

**Reference images:** `ref/` directory in this skill's project.
**Generation script:** `generate.py` in the project root.

---

## Workflow

There are two generation modes. **SVG mode is the default.**

### Mode 1: SVG Blueprint → Nano Banana Pro (Default)

This is the primary workflow. It produces the best results because Claude Code
controls the layout/content precisely, and Nano Banana Pro handles the artistic
rendering.

```
1. Claude Code generates SVG blueprint
   - Detailed layout with all elements, labels, arrows
   - Includes <!-- IMAGE: description --> placeholders where reference
     photos would enhance the final illustration
   - Uses the SVG construction rules below for structure

2. generate.py pipeline runs:
   a. Parses SVG for <!-- IMAGE: ... --> placeholders
   b. Searches Tavily for matching reference images
   c. Downloads best image for each placeholder
   d. Sends SVG + style refs + found images to Nano Banana Pro
   e. Saves final hand-drawn PNG

3. Output: Beautiful hand-drawn diagram as PNG
```

**Run command:**
```bash
python generate.py --svg blueprint.svg -o output.png
```

### Mode 2: Text-Only → Nano Banana Pro

Skip the SVG phase. Send a detailed text prompt directly to Nano Banana Pro.
Use when quick/experimental generation is preferred, or when you want Nano
Banana Pro to freely design the layout.

**Run command:**
```bash
python generate.py --prompt "A diagram explaining how microservices work" -o output.png
```

### generate.py Options

| Flag | Description |
|------|-------------|
| `--svg FILE` | Path to SVG blueprint (default mode) |
| `--prompt TEXT` | Text prompt (alone = text-only mode, with --svg = extra instructions) |
| `-o, --output FILE` | Output image path (.png) — **required** |
| `--no-images` | Skip Tavily image search for placeholders |
| `--aspect-ratio` | Output aspect ratio: `1:1`, `16:9`, `4:3`, `3:4` (default: model decides) |
| `--ref-dir DIR` | Style reference images directory (default: `ref/`) |
| `--env FILE` | Path to .env file (default: `.env`) |

### Image Placeholders

When building the SVG blueprint, add `<!-- IMAGE: ... -->` comments to mark
areas where a real reference photo would help Nano Banana Pro understand what
to draw. The generate.py script will search Tavily for each placeholder and
pass the found images to the model.

**Syntax:**
```xml
<!-- IMAGE: description of what to search for -->
```

**Examples:**
```xml
<!-- IMAGE: developer typing at a dark terminal with code on screen -->
<!-- IMAGE: cloud computing server infrastructure diagram -->
<!-- IMAGE: git branching workflow visualization -->
<!-- IMAGE: robot mascot friendly cute illustration -->
<!-- IMAGE: lock and shield cybersecurity icon -->
```

**Guidelines for placeholders:**
- Use 2-6 image placeholders per diagram (more than 6 slows generation)
- Write descriptive search queries — be specific about what you want
- Place the comment near the SVG element it relates to
- Focus on elements that benefit from visual reference: people, objects,
  scenes, logos, UI screenshots — not abstract shapes or arrows
- If the diagram is purely abstract/conceptual, skip placeholders entirely

## Style Selection

Two styles available. User can specify, or auto-select based on context:

| Style | When to use |
|-------|-------------|
| **color** | Blog posts, social media, presentations, marketing — anything that benefits from visual energy and warmth |
| **mono** | Technical docs, research papers, README files, dark-mode-first contexts, minimalist aesthetic |

If the user doesn't specify, default to **color**.

---

## STYLE 1: COLOR (Warm Illustrated)

The color style is playful, warm, and magazine-quality. It feels like an
editorial illustration from a tech blog — approachable but information-dense.

### Color Palette

| Role | Color | Hex | Usage |
|------|-------|-----|-------|
| Background | Warm cream | `#FDF6E3` | Full SVG background fill |
| Ink / outlines | Dark charcoal | `#2D2D2D` | All strokes, text, outlines |
| Primary accent | Coral red | `#EF6351` | Main element, central box, primary badge |
| Secondary accent | Sky blue | `#4BA3D4` | Arrows, secondary badges, figures |
| Tertiary accent | Soft green | `#6BBF6A` | Tertiary badges, success indicators |
| Warm accent | Golden yellow | `#F4C542` | Highlights, lightbulbs, stars |
| Cool accent | Lavender purple | `#9B7ED8` | Quaternary badges, special callouts |
| Soft accent | Salmon pink | `#F2918C` | Fifth-level badges, gentle emphasis |
| Badge text | White | `#FFFFFF` | Text inside colored badges/pills |
| Callout bg | Pale yellow | `#FFF9DB` | Sticky-note callout boxes |

### Visual Elements

#### Backgrounds and Containers
- Full SVG background: `fill="#FDF6E3"` (warm cream)
- Rounded rectangle containers with `rx="12"` and 2-3px strokes in `#2D2D2D`
- Drop shadow effect via offset darker rect or subtle `<filter>` blur
- Speech bubbles: rounded rect + triangle tail, stroke `#2D2D2D`
- Sticky-note callouts: `fill="#FFF9DB"` with slightly rotated angle (2-3deg transform)
- Notebook/checklist: white fill with spiral binding circles at top

#### Badges and Labels
- Colored pill shapes: `rx="10"`, filled with accent color, white bold text
- Min width 80px, height 28-32px, centered text
- Each item in a list gets a DIFFERENT color from the palette
- Bold name + smaller subtitle below if needed

#### Arrows and Connectors
- Thick colored arrows (stroke-width 4-6) curving between elements
- Each arrow a DIFFERENT color when fanning out from a source
- Arrowheads: filled triangles matching arrow color
- Use quadratic bezier curves (`Q`) for organic feel — never straight lines between distant elements
- Dashed lines (`stroke-dasharray="8,6"`) for secondary/optional connections

#### Decorative Elements (sprinkle liberally)
- Stars: 4-point or 5-point, small (8-12px), scattered, filled `#F4C542` or `#2D2D2D`
- Sparkles: 4-line cross pattern, `stroke="#F4C542" stroke-width="2"`
- Confetti: small rotated rectangles (4x10px) in assorted colors near celebration zones
- Squiggly underlines: wavy path under important text
- Small gear icons: circles with teeth, `stroke="#2D2D2D" fill="none"`
- Tiny doodles: exclamation marks, question marks, `...` dots, hearts

#### Typography
- Titles: `font-size="28-36"`, `font-weight="900"`, `fill="#2D2D2D"`
- Subtitles: `font-size="14-16"`, `font-weight="600"`, `fill="#2D2D2D"`, `opacity="0.7"`
- Body text: `font-size="12-14"`, `font-weight="400"`, `fill="#2D2D2D"`
- Badge text: `font-size="13-15"`, `font-weight="800"`, `fill="#FFFFFF"`
- Source/caption: `font-size="10"`, `fill="#2D2D2D"`, `opacity="0.4"`
- Font stack: `'Comic Neue', 'Segoe Print', 'Patrick Hand', system-ui, sans-serif`

#### Character / Mascot Elements
- Simple stick figures with colored bodies (circle head, line body, line limbs)
- Color each figure differently to represent different stakeholders
- Expressive poses: arms up (celebration), pushing against something (struggle), pointing
- Optional: simple robot mascot (rounded rect body, circle eyes, antenna)
- Speech bubbles from characters with short punchy text

#### Emphasis Techniques
- Red X marks (`stroke="#EF6351" stroke-width="3"`) for rejection/negation
- Green checkmarks for success
- Lightbulb icon (circle + filament lines) filled `#F4C542` for ideas
- Glowing effect: duplicate shape behind with larger size, same color, `opacity="0.2"`
- Banner/ribbon at bottom for taglines: rect with notched ends

### Color Style Composition Rules

1. **Warm ground:** Always start with the cream background — never transparent
2. **Color variety:** When showing a list or fan-out, each item gets a unique accent color
3. **Ink outlines on everything:** Every shape has a `#2D2D2D` stroke (2-3px)
4. **Organic curves:** Connectors, arrows, and decorative elements should feel hand-drawn — use bezier curves with slight irregularity
5. **Celebrate the output:** The final/result element should have sparkles, confetti, and a glow effect
6. **Fill the margins:** Scatter small decorative elements (stars, sparkles, squiggles) in empty space — but not so many it feels cluttered (8-15 decorative elements per diagram)

---

## STYLE 2: MONO (Sketchy Black & White)

The mono style is clean, technical, and authoritative. It feels like a
well-crafted whiteboard sketch or a diagram from an academic paper — clear
information hierarchy with no color distraction.

### Color Palette

| Role | Value | Usage |
|------|-------|-------|
| Ink | `currentColor` | All strokes, text, fills |
| Background | transparent | No background fill |
| Emphasis fill | `currentColor` with `opacity="0.08"` | Subtle container fills |
| Strong fill | `currentColor` with `opacity="0.15"` | Emphasized container fills |
| Border | `currentColor` with `opacity="0.6"` | Container strokes |
| Subtle text | `currentColor` with `opacity="0.5"` | Secondary text, captions |

Using `currentColor` ensures the diagram works on both light and dark backgrounds.

### Visual Elements

#### Backgrounds and Containers
- SVG background: transparent (no fill)
- Rounded rectangles: `stroke="currentColor" stroke-width="2.5" fill="none"` with `rx="8"`
- Emphasized containers: add `fill="currentColor" opacity="0.06"` inside
- Cloud/thought bubbles: bumpy path outline, no fill
- Bracket groups: square bracket paths to group related items
- Panel grids: divide space into sections with `stroke="currentColor" stroke-width="1.5"`

#### Sketchy Line Effect
To achieve the hand-drawn feel, offset paths slightly:
- Main stroke: `stroke-width="2.5"`, slight imperfection via bezier control points
- For straight lines: add 1-2px of bezier wobble at midpoints
- Corner rounding on all rectangles: `rx="6-10"`
- Vary stroke-width subtly (2-3px range) between different elements

#### Arrows and Connectors
- Solid arrows: `stroke="currentColor" stroke-width="2" fill="none"`
- Dashed connectors: `stroke-dasharray="6,4"` for secondary flows
- Arrowheads: simple open chevron or filled triangle in `currentColor`
- Flow direction: generally left-to-right or top-to-bottom

#### Icons (All Ink-Drawn)
- Lightbulb: circle + 3 radiating lines, all `stroke="currentColor"`
- Magnifying glass: circle + angled line handle
- Document: rectangle + horizontal lines inside
- Gear: circle + teeth pattern
- Star: 5-point path, `stroke="currentColor" fill="none"` (or filled for emphasis)
- Checkmark: simple path `M 0 5 L 4 9 L 12 0`
- X mark: two crossing lines
- Person: circle head + body lines (stick figure)
- Lock: rounded rect body + shackle arc
- Maze: nested rectangular spiral path
- Beaker: trapezoid + bubbles

#### Typography
- Titles: `font-size="22-28"`, `font-weight="900"`, `fill="currentColor"`
- Section heads: `font-size="16-20"`, `font-weight="800"`, `fill="currentColor"`, UPPERCASE
- Body text: `font-size="12-14"`, `font-weight="400"`, `fill="currentColor"`
- Annotations: `font-size="11"`, `font-weight="400"`, `fill="currentColor"`, `opacity="0.6"`
- Font stack: `'Comic Neue', 'Segoe Print', 'Patrick Hand', system-ui, sans-serif`

#### Emphasis Techniques
- Thick underline below key text: `stroke-width="3"` path
- Crosshatch/scribble fill: tight parallel diagonal lines inside a container for emphasis
- Circle-around-text for callouts: hand-drawn ellipse
- Bold weight shift: key words in `font-weight="900"` vs normal `400`
- Size hierarchy: important concepts get larger containers and text

### Mono Style Composition Rules

1. **No color ever:** Everything is `currentColor` or transparent
2. **Contrast via weight and opacity:** Use stroke-width (1.5 to 3.5) and opacity (0.3 to 1.0) for hierarchy
3. **Generous whitespace:** Let elements breathe — mono needs more space than color to avoid feeling cluttered
4. **Strong section labels:** UPPERCASE, bold, larger font for section divisions
5. **Ink economy:** Every line should communicate — no purely decorative elements except occasional dashes or dots as separators
6. **Panel composition:** Use panel grids (2x2, 1x3, etc.) when showing multiple related concepts

---

## Layout Patterns

Choose a layout pattern based on the concept being communicated:

### Flow / Pipeline
Left-to-right or top-to-bottom sequence of steps.
```
[Input] ---> [Process 1] ---> [Process 2] ---> [Output]
```
- Best for: architectures, pipelines, workflows, build processes
- Use arrows between each stage
- Optional: iterative loop arrows returning from later to earlier stages

### Fan-Out / Divergence
One source element with multiple outputs branching away.
```
              /--> [Option A]
[Source] ----/--> [Option B]
              \--> [Option C]
```
- Best for: framework comparisons, forks, one-to-many relationships
- In color: each branch gets a different colored arrow
- In mono: vary dash patterns or arrow styles

### Convergence / Funnel
Multiple inputs flowing into one output.
```
[Input A] --\
[Input B] ---\---> [Result]
[Input C] --/
```
- Best for: aggregation, "best of" synthesis, merging concepts

### Panel Grid
Multiple independent scenes in a grid layout.
```
[Scene 1] | [Scene 2]
----------|----------
[Scene 3] | [Scene 4]
```
- Best for: use cases, pattern categories, comparison of scenarios
- Each panel gets its own mini-illustration
- Central connecting text between panels

### Central Hub
One dominant central element with satellites around it.
```
        [A]
         |
  [B] -- [HUB] -- [C]
         |
        [D]
```
- Best for: ecosystem diagrams, feature maps, stakeholder views

### Before / After
Two-panel comparison with a transformation in between.
```
[Before State] ==transform==> [After State]
```
- Best for: improvement stories, refactoring, migration narratives

---

## SVG Construction

### Standard Shell

```xml
<svg
  viewBox="0 0 900 550"
  style="max-width: 100%; height: auto; font-family: 'Comic Neue', 'Segoe Print', 'Patrick Hand', system-ui, sans-serif"
  role="img"
  aria-label="[Descriptive alt text of the diagram]"
>
  <title>[Diagram Title]</title>
  <desc>[Full description for screen readers including all key concepts shown]</desc>

  <!-- Background (color style only) -->
  <rect width="900" height="550" fill="#FDF6E3" rx="0" />

  <!-- Diagram content -->

</svg>
```

### ViewBox Guidelines

Match the viewBox to the user's requested aspect ratio:

| Aspect | ViewBox (simple) | ViewBox (complex) | generate.py flag |
|--------|------------------|-------------------|------------------|
| **wide** (default) | `0 0 900 550` | `0 0 1100 500` | `--aspect-ratio 16:9` |
| **square** | `0 0 800 800` | `0 0 900 900` | `--aspect-ratio 1:1` |
| **tall** | `0 0 500 800` | `0 0 600 1000` | `--aspect-ratio 3:4` |
| **standard** | `0 0 900 650` | `0 0 1000 750` | `--aspect-ratio 4:3` |

Always use `style="max-width: 100%; height: auto"` for responsive scaling.

**Aspect ratio flag in generate.py:** Pass `--aspect-ratio 1:1` (or `16:9`, `4:3`, `3:4`) to constrain the output image aspect ratio. This ensures Nano Banana Pro renders at the correct proportions.

### Square Diagrams for Carousel Slides

When generating diagrams intended for LinkedIn/Instagram carousel slides, use a **square viewBox** (`0 0 800 800`) and pass `--aspect-ratio 1:1` to generate.py.

**Usage with carousel skill:**
```bash
# 1. Generate the square diagram
python generate.py --svg blueprint.svg --aspect-ratio 1:1 -o diagram.png

# 2. Add rounded corners for carousel embedding
python .claude/skills/linkedin-carousel/scripts/round_corners.py \
  --input diagram.png \
  --output diagram-rounded.png \
  --radius 24

# 3. Pass as --reference to the carousel slide generator
python .claude/skills/linkedin-carousel/scripts/generate_slide.py \
  --reference diagram-rounded.png "library/content-assets/backgrounds/black paper.png" \
  --prompt "Place Image 1 (the diagram) centered on the slide with the dark background..." \
  --output slide.png
```

The diagram becomes a visual element floating on the carousel slide background — the rounded corners give it a card-like feel that integrates naturally.

### Hand-Drawn Path Technique

To make paths feel sketchy rather than mechanical, add slight control point offsets:

**Mechanical (avoid):**
```xml
<line x1="100" y1="200" x2="400" y2="200" />
```

**Hand-drawn (prefer):**
```xml
<path d="M 100 200 Q 250 197 400 201" />
```

For rectangles, instead of `<rect>`, use `<path>` with slightly wobbly corners:
```xml
<!-- Sketchy rectangle at x=50, y=50, w=200, h=100 -->
<path d="M 58 50 L 248 52 Q 252 52 252 58 L 250 148 Q 250 152 246 152 L 52 150 Q 48 150 48 146 L 50 56 Q 50 52 54 52 Z"
      stroke="currentColor" stroke-width="2.5" fill="none" />
```

The key is 1-3px of imperfection in coordinates — enough to read as "hand-drawn"
but not so much that it looks broken.

### Curved Arrow Construction

```xml
<!-- Organic curved arrow from (100,300) to (400,200) -->
<path d="M 100 300 C 200 310, 300 180, 390 200"
      stroke="#4BA3D4" stroke-width="4" fill="none" />
<!-- Arrowhead -->
<polygon points="390,200 378,192 380,206" fill="#4BA3D4" />
```

### Badge / Pill Construction

```xml
<!-- Colored badge -->
<g transform="translate(50, 100)">
  <rect width="120" height="30" rx="15" fill="#EF6351" stroke="#2D2D2D" stroke-width="1.5" />
  <text x="60" y="20" text-anchor="middle" font-size="13" font-weight="800" fill="#FFFFFF">Label</text>
</g>
```

### Stick Figure Construction

```xml
<!-- Basic stick figure (centered at cx, cy=head center) -->
<g transform="translate(200, 150)">
  <!-- Head -->
  <circle cx="0" cy="0" r="12" stroke="#2D2D2D" stroke-width="2" fill="#4BA3D4" />
  <!-- Body -->
  <line x1="0" y1="12" x2="0" y2="45" stroke="#2D2D2D" stroke-width="2.5" />
  <!-- Arms (raised = celebration) -->
  <line x1="0" y1="22" x2="-18" y2="10" stroke="#2D2D2D" stroke-width="2" />
  <line x1="0" y1="22" x2="18" y2="10" stroke="#2D2D2D" stroke-width="2" />
  <!-- Legs -->
  <line x1="0" y1="45" x2="-12" y2="65" stroke="#2D2D2D" stroke-width="2" />
  <line x1="0" y1="45" x2="12" y2="65" stroke="#2D2D2D" stroke-width="2" />
</g>
```

### Decorative Elements Library

```xml
<!-- 4-point star -->
<path d="M 0 -8 L 2 -2 L 8 0 L 2 2 L 0 8 L -2 2 L -8 0 L -2 -2 Z"
      fill="#F4C542" transform="translate(X, Y)" />

<!-- Sparkle (cross) -->
<g transform="translate(X, Y)" stroke="#F4C542" stroke-width="1.5" stroke-linecap="round">
  <line x1="0" y1="-5" x2="0" y2="5" />
  <line x1="-5" y1="0" x2="5" y2="0" />
</g>

<!-- Confetti piece -->
<rect x="0" y="0" width="4" height="10" rx="1" fill="#9B7ED8"
      transform="translate(X, Y) rotate(35)" />

<!-- Lightbulb icon -->
<g transform="translate(X, Y)">
  <circle cx="0" cy="0" r="10" stroke="currentColor" stroke-width="2" fill="#F4C542" opacity="0.3" />
  <circle cx="0" cy="0" r="10" stroke="currentColor" stroke-width="2" fill="none" />
  <line x1="-3" y1="10" x2="3" y2="10" stroke="currentColor" stroke-width="1.5" />
  <line x1="0" y1="-14" x2="0" y2="-18" stroke="currentColor" stroke-width="1.5" />
  <line x1="10" y1="-8" x2="14" y2="-11" stroke="currentColor" stroke-width="1.5" />
  <line x1="-10" y1="-8" x2="-14" y2="-11" stroke="currentColor" stroke-width="1.5" />
</g>

<!-- Squiggly underline -->
<path d="M X Y q 5 -4 10 0 q 5 4 10 0 q 5 -4 10 0 q 5 4 10 0"
      stroke="currentColor" stroke-width="2" fill="none" />

<!-- Small gear -->
<g transform="translate(X, Y) scale(0.6)">
  <circle cx="0" cy="0" r="8" stroke="currentColor" stroke-width="2" fill="none" />
  <circle cx="0" cy="0" r="3" stroke="currentColor" stroke-width="1.5" fill="none" />
  <!-- Teeth (6 evenly spaced) -->
  <line x1="0" y1="-8" x2="0" y2="-12" stroke="currentColor" stroke-width="2.5" />
  <line x1="7" y1="-4" x2="10" y2="-6" stroke="currentColor" stroke-width="2.5" />
  <line x1="7" y1="4" x2="10" y2="6" stroke="currentColor" stroke-width="2.5" />
  <line x1="0" y1="8" x2="0" y2="12" stroke="currentColor" stroke-width="2.5" />
  <line x1="-7" y1="4" x2="-10" y2="6" stroke="currentColor" stroke-width="2.5" />
  <line x1="-7" y1="-4" x2="-10" y2="-6" stroke="currentColor" stroke-width="2.5" />
</g>
```

---

## Input Format

The user provides a concept to diagram. They may specify:

```
Diagram: [concept or topic to visualize]
Style: color | mono        (default: color)
Aspect: wide | square | tall | auto  (default: auto)
Layout: flow | fan-out | convergence | panel | hub | before-after  (auto-detect)
Elements: [optional specific items to include]
```

Or they may simply describe what they want in natural language. Infer the best
layout, style, and aspect ratio from context.

### Aspect Ratio

| Aspect | Ratio | ViewBox Examples | Best For |
|--------|-------|------------------|----------|
| **wide** | ~16:9 to 2:1 | `0 0 1000 550`, `0 0 1100 500` | Pipelines, flows, timelines, presentations |
| **square** | 1:1 | `0 0 800 800`, `0 0 900 900` | Social media posts, balanced hub diagrams, Instagram |
| **tall** | ~9:16 to 1:2 | `0 0 500 900`, `0 0 600 1000` | Vertical flows, mobile-first, stories format |
| **auto** | varies | Based on content | Default — choose what fits the content best |

When **auto** (default), select based on the layout pattern:
- Flow/pipeline → wide
- Central hub → square
- Fan-out → wide
- Panel grid → square or wide depending on grid shape
- Vertical flow → tall
- Before/after → wide

User can also say "square diagram", "tall format", "landscape", "portrait", etc.
and the aspect should be inferred accordingly.

## Process

### Phase 1: SVG Blueprint

1. **Understand the concept:** What are the key entities, relationships, and flow?
2. **Choose layout:** Pick the pattern that best represents the information structure
3. **Choose style:** Use specified style, or default to color
4. **Sketch mentally:** Plan element positions on the viewBox grid before writing SVG
5. **Build SVG:** Construct from background layer up: bg → containers → connectors → icons → text → decorations
6. **Hand-drawn feel:** Apply the wobble technique to ALL paths and rectangles
7. **Add image placeholders:** Insert `<!-- IMAGE: ... -->` comments where reference photos would enhance the diagram (2-6 per diagram, or none for purely abstract diagrams)
8. **Verify SVG:** Check all text is readable, arrows point correctly, no overlapping elements

### Phase 1.5: SVG Critique (Sub-Agent)

**ALWAYS run this step.** After writing the SVG, launch a sub-agent to critique
and fix the blueprint before rendering. Use the Task tool with
`subagent_type="general-purpose"` and a prompt like:

```
Read the SVG file at <path>. Critique it for:
- Overlapping text or elements
- Text alignment issues (miscentered labels, text overflowing containers)
- Spacing problems (elements too close or too far apart)
- Arrow/connector clarity (do they clearly show flow direction?)
- Badge/pill sizing (is text clipped or too small to read?)
- Visual balance (is the layout lopsided or cramped in one area?)
- Missing labels or unclear abbreviations

Fix any issues you find by editing the SVG directly. Do NOT rewrite the
entire file — only make targeted fixes. Keep all existing IMAGE placeholder
comments intact.
```

This sub-agent catches layout bugs that are easy to miss when constructing
complex SVGs from scratch — misaligned text anchors, overlapping groups,
cramped spacing, etc.

### Phase 2: Nano Banana Pro Rendering

10. **Run generate.py:** Execute `python generate.py --svg <file> -o <output>.png` to render the hand-drawn version

### Phase 2.5: Visual QA — Inspect the Output

**ALWAYS do this. Never skip.** After rendering, visually inspect the final PNG using the Read tool before showing it to the user.

Check for:
1. **Centering** — Is the content centered within the canvas? Is text balanced?
2. **Spacing** — Even margins, no content crammed against edges, no large dead zones?
3. **Text readability** — All labels readable? Nothing cut off, overlapping, or too small?
4. **Credits bar** — Present and properly spaced at the bottom?
5. **Element alignment** — Arrows pointing correctly? Boxes aligned? Visual weight balanced?

**If anything looks off, fix it:**
- Edit the SVG blueprint to adjust positions/sizes
- Re-run the critique sub-agent on the edited SVG
- Re-render and re-inspect until the output is polished
- For carousel-embedded diagrams: adjust compositing parameters (`--width`, `--y-offset`) until centered in the content zone

The final output should always look as good as it can. The user should never have to ask for centering or spacing fixes.

11. **Show the result:** Display the generated PNG to the user

### Alternative: Text-Only Mode

If the user requests text-only mode, or for quick experimental generation:

1. Craft a detailed text prompt describing all diagram elements, layout, and relationships
2. Run `python generate.py --prompt "..." -o <output>.png`
3. Show the result

## Output Format

The pipeline produces two files:

1. **SVG blueprint** (intermediate) — written by Claude Code, used as input to generate.py
2. **PNG diagram** (final output) — hand-drawn illustration generated by Nano Banana Pro

Save the SVG blueprint as `<name>-blueprint.svg` and the final output as `<name>.png`.

**SVG blueprint file (intermediate):**
```xml
<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 900 550"
     style="max-width: 100%; height: auto; font-family: 'Comic Neue', 'Segoe Print', 'Patrick Hand', system-ui, sans-serif"
     role="img" aria-label="[description]">
  <title>[Title]</title>
  <desc>[Full description]</desc>

  <!-- IMAGE: description of a reference photo for this area -->
  <!-- Diagram content -->

</svg>
```

**SVG-only output (when user specifically requests SVG):**

If the user explicitly asks for SVG output (not PNG), skip Phase 2 and deliver
the SVG directly. Use the same construction rules below. SVG can be:

- Standalone `.svg` file
- Inline in HTML: wrapped in `<figure>` tag
- Inline in MDX: camelCase attributes, wrapped in JSX `<figure>`

## Quality Checklist

### SVG Blueprint Quality
- [ ] Style matches user request (color vs mono)
- [ ] Hand-drawn feel: wobbly paths, rounded corners, bezier curves
- [ ] No mechanical straight lines between distant elements
- [ ] Text hierarchy is clear: titles > section heads > body > annotations
- [ ] All arrows have visible arrowheads and point correctly
- [ ] No overlapping text or elements
- [ ] Layout uses space well (no huge empty zones, no cramped areas)
- [ ] `role="img"` and `aria-label` present on `<svg>`
- [ ] `<title>` and `<desc>` present inside `<svg>`
- [ ] Color style: warm cream background, decorative elements scattered
- [ ] Color style: each list/fan item uses a different accent color
- [ ] Mono style: only `currentColor` and `transparent` — zero hex colors
- [ ] Font family set to handwritten stack
- [ ] ViewBox appropriate for diagram complexity
- [ ] Image placeholders added where reference photos would help (2-6)

### Pipeline Quality
- [ ] generate.py executed successfully
- [ ] Tavily found images for all (or most) placeholders
- [ ] **Final PNG visually inspected** via Read tool before showing to user
- [ ] Content centered and balanced — no lopsided layouts or wasted space
- [ ] Even spacing on all sides — nothing crammed against edges
- [ ] All text readable — no cut-off, overlapping, or illegibly small labels
- [ ] Credits bar included and properly spaced at bottom
- [ ] **If anything looks off: fixed before presenting** — edit SVG, re-critique, re-render

---

## Credits Bar

**ALWAYS include a credits bar at the bottom of every diagram.** This shows the
creator's headshot, platform usernames, and platform icons.

### Creator Info

| Platform | Username | Icon Color |
|----------|--------|------------|
| Instagram | `@itstylergermain` | `#E1306C` (IG pink) |
| LinkedIn | `@tylergermain` | `#0A66C2` (LinkedIn blue) |

### Credits Bar SVG Template

Place this at the very bottom of the SVG, centered horizontally. Reserve ~50px
of vertical space for the credits (adjust viewBox height if needed).

```xml
<!-- ==================== CREDITS BAR ==================== -->
<g transform="translate(CENTER_X, BOTTOM_Y)">
  <!-- Subtle separator line -->
  <path d="M -320 -18 Q -160 -21 0 -18 Q 160 -15 320 -18"
        stroke="#2D2D2D" stroke-width="0.8" opacity="0.15" fill="none" />

  <!-- Instagram (left side) -->
  <rect x="-180" y="-7" width="16" height="16" rx="4" fill="#E1306C"
        stroke="#2D2D2D" stroke-width="1" />
  <circle cx="-172" cy="1" r="4" stroke="#FFFFFF" stroke-width="1.2" fill="none" />
  <circle cx="-172" cy="1" r="1.2" fill="#FFFFFF" />
  <text x="-158" y="5" text-anchor="start" font-size="13" font-weight="700"
        fill="#E1306C">@itstylergermain</text>

  <!-- Dot separator -->
  <circle cx="0" cy="1" r="2.5" fill="#2D2D2D" opacity="0.3" />

  <!-- LinkedIn (right side) -->
  <text x="158" y="5" text-anchor="end" font-size="13" font-weight="700"
        fill="#0A66C2">@tylergermain</text>
  <rect x="164" y="-7" width="16" height="16" rx="3" fill="#0A66C2"
        stroke="#2D2D2D" stroke-width="1" />
  <text x="168" y="7" font-size="11" font-weight="900" fill="#FFFFFF">in</text>
</g>
```

### Mono Style Credits Variant

For mono diagrams, use `currentColor` instead of brand colors:
```xml
<!-- Instagram icon: fill="currentColor" opacity="0.6" -->
<!-- LinkedIn icon: fill="currentColor" opacity="0.6" -->
<!-- All text: fill="currentColor" -->
```

### Credits Placement Rules

1. **Center horizontally** at `x = viewBox_width / 2`
2. **Place at bottom** — about 40px from the bottom edge of the viewBox
3. **Separator line** above credits using a subtle wavy path
4. **Instagram** on the left, dot separator in center, **LinkedIn** on the right
5. Reserve 50px of viewBox height for credits when planning layout

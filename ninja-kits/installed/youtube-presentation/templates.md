# Slide Layout Templates

Visual blueprints for every slide type. Each template shows where elements are positioned, what properties control the layout, and an example JSON snippet.

---

## title

Big centered heading with optional subtitle. Opening and closing slides.

```
┌─────────────────────────────────────────┐
│                                         │
│                                         │
│      HEADING (white, 54pt, bold)        │
│      ~~~~ underline (optional) ~~~~     │
│                                         │
│      subtitle (gray, serif, italic)     │
│                                         │
│                                         │
└─────────────────────────────────────────┘
```

**Properties:**
| Field | Required | Notes |
|-------|----------|-------|
| `heading` | yes | Main title text. Use `==word==` for accent emphasis. |
| `subtitle` | no | Serif italic line below heading |
| `heading_underline` | no | `true` → accent hand-drawn wavy line under heading |

**Example:**
```json
{
  "type": "title",
  "heading": "AI Agents Are ==Not== What You Think",
  "subtitle": "A contrarian take on the agent hype cycle",
  "heading_underline": true,
  "notes": "Open strong — pause after title appears"
}
```

---

## content

The default slide. Accent heading + white body text or bullet points.

### Layout A: Heading + Body Text
```
┌─────────────────────────────────────────┐
│                                         │
│  HEADING (accent, 36pt, bold)            │
│  ~~~~ underline (optional) ~~~~         │
│                                         │
│  Body text goes here. One to three      │
│  sentences. Can contain ==emphasis==.   │
│                                         │
│                                         │
└─────────────────────────────────────────┘
```

### Layout B: Heading + Bullets
```
┌─────────────────────────────────────────┐
│                                         │
│  HEADING (accent, 36pt, bold)            │
│                                         │
│  • First important point                │
│  • Second point with ==emphasis==       │
│  • Third point                          │
│  • Fourth point                         │
│                                         │
└─────────────────────────────────────────┘
```

### Layout C: Body Only (no heading)
```
┌─────────────────────────────────────────┐
│                                         │
│  Body text fills more of the slide      │
│  when there's no heading. Good for      │
│  continuation or emphasis on a single   │
│  thought that needs room to breathe.    │
│                                         │
│                                         │
│                                         │
└─────────────────────────────────────────┘
```

**Properties:**
| Field | Required | Notes |
|-------|----------|-------|
| `heading` | no | Accent-colored heading. Supports `==emphasis==` (renders white). |
| `body` | no | White body text. Lines starting with `- ` auto-render as bullets. Supports `==emphasis==` (renders accent). |
| `bullets` | no | Array of bullet point strings. Supports `==emphasis==`. |
| `heading_underline` | no | `true` → hand-drawn accent underline below heading |

At least one of `heading`, `body`, or `bullets` required.

**Example:**
```json
{
  "type": "content",
  "heading": "Why ==Claude Code== Changes Everything",
  "body": "It's not just a coding assistant — it's an ==autonomous agent== that understands your entire codebase.",
  "heading_underline": true,
  "notes": "Emphasize the word autonomous"
}
```

---

## content_media

Text + image/GIF side by side. The workhorse layout for visual slides.

### Layout A: Text Left, Media Right (default)
```
┌─────────────────────────────────────────┐
│                                         │
│  HEADING (accent)   │ ┌───────────────┐ │
│  ~~~~ underline ~~  │ │               │ │
│                     │ │   image/GIF   │ │
│  Body text or       │ │   in card     │ │
│  bullet points      │ │   background  │ │
│  go here            │ │               │ │
│                     │ │  caption       │ │
│                     │ └───────────────┘ │
└─────────────────────────────────────────┘
         55%                   45%
```

### Layout B: Media Left, Text Right
```
┌─────────────────────────────────────────┐
│                                         │
│ ┌───────────────┐  │  HEADING (accent)  │
│ │               │  │                    │
│ │   image/GIF   │  │  Body text or      │
│ │   in card     │  │  bullet points     │
│ │   background  │  │  go here           │
│ │               │  │                    │
│ │  caption       │  │                    │
│ └───────────────┘  │                    │
└─────────────────────────────────────────┘
         45%                   55%
```

**Properties:**
| Field | Required | Notes |
|-------|----------|-------|
| `heading` | no | Accent-colored heading. Supports `==emphasis==`. |
| `body` | no | White body text. Supports `==emphasis==` and auto-bullets. |
| `bullets` | no | Array of bullet points. Supports `==emphasis==`. |
| `image_path` | yes (after fetch) | Local path to GIF or image |
| `gif_query` | no | Giphy search terms (for GIF fetch) |
| `image_query` | no | Image search terms (for image fetch) |
| `media_side` | no | `"right"` (default) or `"left"` |
| `caption` | no | Small gray text under the media |
| `heading_underline` | no | `true` → hand-drawn underline |

**Example:**
```json
{
  "type": "content_media",
  "heading": "The ==Agent Loop==",
  "body": "Every AI agent follows the same pattern:\n- Observe the environment\n- Decide on an action\n- Execute and evaluate",
  "gif_query": "robot thinking",
  "media_side": "right",
  "caption": "basically this",
  "notes": "Walk through the three steps"
}
```

---

## section_divider

Visual break between major sections. Numbered circle + accent line + heading.

### Layout A: With Section Number
```
┌─────────────────────────────────────────┐
│                                         │
│                 ┌──┐                    │
│                 │02│  (accent circle)   │
│                 └──┘                    │
│            ────────────                 │
│                                         │
│         HEADING (accent, 54pt)          │
│         ~~~~ underline (opt) ~~~~       │
│         subtitle (gray, italic)         │
│                                         │
└─────────────────────────────────────────┘
```

### Layout B: Without Number
```
┌─────────────────────────────────────────┐
│                                         │
│                                         │
│            ────────────                 │
│                                         │
│         HEADING (accent, 54pt)          │
│         subtitle (gray, italic)         │
│                                         │
│                                         │
└─────────────────────────────────────────┘
```

**Properties:**
| Field | Required | Notes |
|-------|----------|-------|
| `heading` | yes | Large accent heading. Supports `==emphasis==` (renders white). |
| `subtitle` | no | Gray serif italic context line |
| `section_number` | no | Number shown in accent circle (renders as 01, 02, etc.) |
| `heading_underline` | no | `true` → hand-drawn underline under heading |

**Example:**
```json
{
  "type": "section_divider",
  "heading": "The ==Real== Problem",
  "subtitle": "Why most AI implementations fail",
  "section_number": 2,
  "notes": "Transition — slow down here"
}
```

---

## stats

One big impactful number. Used for data points that deserve their own moment.

### Layout A: Standard
```
┌─────────────────────────────────────────┐
│                                         │
│                                         │
│              81% (accent, 96pt)         │
│            ────────────                 │
│         reduction in audit time         │
│         (white, 28pt)                   │
│                                         │
│         Anthropic's marketing team      │
│         (gray, serif italic)            │
└─────────────────────────────────────────┘
```

### Layout B: With Hand-Drawn Circle
```
┌─────────────────────────────────────────┐
│                                         │
│                                         │
│           ╭─── 81% ───╮ (accent, 96pt) │
│           ╰────────────╯ (hand-drawn)   │
│            ────────────                 │
│         reduction in audit time         │
│                                         │
│         Anthropic's marketing team      │
│                                         │
└─────────────────────────────────────────┘
```

**Properties:**
| Field | Required | Notes |
|-------|----------|-------|
| `value` | yes | The big number/stat (e.g., "81%", "$2.4M", "10x") |
| `label` | yes | What the number means. Supports `==emphasis==`. |
| `context` | no | Attribution or source (gray serif italic) |
| `value_circle` | no | `true` → hand-drawn accent circle around the value |

**Example:**
```json
{
  "type": "stats",
  "value": "10x",
  "label": "faster than ==manual== code review",
  "context": "Internal client data, Q4 2025",
  "value_circle": true,
  "notes": "Let this sink in — pause after"
}
```

---

## two_column

Side-by-side comparison with vertical accent divider.

```
┌─────────────────────────────────────────┐
│                                         │
│  HEADING (accent, optional)             │
│  ~~~~ underline (optional) ~~~~         │
│                                         │
│  Left Heading     │  Right Heading      │
│  (white, bold)    │  (white, bold)      │
│                   │                     │
│  • Bullet one     │  • Bullet one       │
│  • Bullet two     │  • Bullet two       │
│  • Bullet three   │  • Bullet three     │
│                   │                     │
└─────────────────────────────────────────┘
        47%         │         47%
              accent divider
```

**Properties:**
| Field | Required | Notes |
|-------|----------|-------|
| `heading` | no | Accent heading spanning both columns. Supports `==emphasis==`. |
| `left_heading` | no | White bold heading for left column |
| `left_body` | no | Body text for left column |
| `left_bullets` | no | Bullet array for left column |
| `right_heading` | no | White bold heading for right column |
| `right_body` | no | Body text for right column |
| `right_bullets` | no | Bullet array for right column |
| `heading_underline` | no | `true` → hand-drawn underline under main heading |

Column headings and bullets support `==emphasis==`.

**Example:**
```json
{
  "type": "two_column",
  "heading": "Before vs ==After==",
  "left_heading": "Manual Process",
  "left_bullets": ["8 hours per audit", "Spreadsheet chaos", "3 people involved"],
  "right_heading": "With AI Agent",
  "right_bullets": ["==90 minutes==", "Interactive report", "1 command"],
  "heading_underline": true,
  "notes": "Point at each column as you describe it"
}
```

---

## quote

Vertical accent bar + serif italic quote text + attribution.

```
┌─────────────────────────────────────────┐
│                                         │
│                                         │
│  █  "The best way to predict the        │
│  █   future is to ==build it==."        │
│  █                                      │
│     — Alan Kay                          │
│                                         │
│                                         │
└─────────────────────────────────────────┘
  accent bar
```

**Properties:**
| Field | Required | Notes |
|-------|----------|-------|
| `text` | yes | The quote. Serif italic. Supports `==emphasis==` (renders accent). |
| `attribution` | no | Who said it (gray, preceded by em dash) |

**Example:**
```json
{
  "type": "quote",
  "text": "The companies that win will be the ones that ==build agents==, not the ones that talk about them.",
  "attribution": "Your Name",
  "notes": "Let the quote land — don't rush"
}
```

---

## image

Full-bleed image with optional caption. Rare — use `content_media` for most image slides.

```
┌─────────────────────────────────────────┐
│                                         │
│                                         │
│          [ full-bleed image ]           │
│          [ maintains aspect ratio ]     │
│          [ centered in slide ]          │
│                                         │
│              caption (gray)             │
│                                         │
└─────────────────────────────────────────┘
```

**Properties:**
| Field | Required | Notes |
|-------|----------|-------|
| `image_path` | yes (after fetch) | Local path to image |
| `image_query` | no | Search terms for image fetch |
| `caption` | no | Gray centered caption |

---

## gif

Full-bleed GIF. Only for big reaction moments. Prefer `content_media` for GIFs with context.

Same layout as `image`. Same properties plus `gif_query` for Giphy search.

---

## accent

Playful one-liner in Steel City Comic font. Accent color, centered, bold.

```
┌─────────────────────────────────────────┐
│                                         │
│                                         │
│                                         │
│          wait what?!                    │
│          (comic font, accent, 48pt)     │
│                                         │
│                                         │
│                                         │
└─────────────────────────────────────────┘
```

**Properties:**
| Field | Required | Notes |
|-------|----------|-------|
| `text` | yes | The playful one-liner |

---

## blank

Just the dark background. Breathing room or camera-only pauses.

```
┌─────────────────────────────────────────┐
│                                         │
│                                         │
│              (nothing)                  │
│                                         │
│                                         │
└─────────────────────────────────────────┘
```

No required properties.

---

## Visual Features Reference

### Inline Emphasis: `==text==`
Wrapping text in `==double equals==` renders it in a contrasting accent color:
- In **white text** (body, title headings, column headings): emphasis renders in the **accent color**
- In **accent text** (content headings, section dividers): emphasis renders **white**

Works in: headings, body text, bullets, labels, quotes, subtitles.

### Hand-Drawn Underline: `heading_underline: true`
Adds a wavy accent-colored SVG line below the heading. Each one is slightly different (randomized curves). Supported on: `title`, `content`, `content_media`, `section_divider`, `two_column`.

### Hand-Drawn Circle: `value_circle: true`
Adds an irregular accent-colored SVG circle around the stat value. Only supported on `stats` slides.

### Camera Modes
Set globally on the presentation, not per-slide:
- **normal** — content uses full slide width
- **camera-left** — left 40% empty for camera, content on right 60%
- **camera-right** — right 40% empty, content on left 60%
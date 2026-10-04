---
name: screen-demo
description: Use when the user wants to browse a website in a cloud browser and record a polished demo video. Records browsing sessions with Steel.dev, then edits the recording with Remotion — adding screen zooms, smooth cursor, and clip transitions for a Screen Studio-like result.
---

# Screen Demo — Browse, Record & Edit

Record polished product/website demo videos for Instagram content. Uses **Steel.dev** to browse in a cloud browser (with a large smooth cursor baked in), then **Remotion** to trim, zoom, and transition the recording into a clean final video with a gradient canvas background.

---

## Assets

Bundled gradient backgrounds for Remotion renders:

| File | Use |
|------|-----|
| `.claude/skills/screen-demo/assets/gradient-dark.jpg` | Dark blue gradient. Default for most demos. |
| `.claude/skills/screen-demo/assets/gradient-light.jpg` | Warm orange/teal gradient. Use for lighter/playful demos. |

Before rendering, copy the chosen gradient to `remotion/public/gradient.jpg`. The Remotion `ZoomClip` component reads it from there.

---

## Process

### Step 1: Gather the Browsing Plan

Ask the user what they want to demo. You need:

1. **URL(s)** — What website or product to show
2. **Interactions** — What to click, scroll to, hover over, type into
3. **Key moments** — What parts matter most (these become zoom targets)
4. **Label** (optional) — Short name for the demo (used for folder naming)

If the user gives a vague description like "show off Acme's landing page", translate that into specific actions:
- Navigate to the homepage
- Wait a moment for it to load
- Scroll down to the features section
- Hover over a feature card
- Click the CTA button
- etc.

### Step 2: Build the Browse Plan JSON

Create a folder at `workspace/screen-demos/{slug}/` and write the browsing plan:

```json
{
  "viewport": { "width": 1920, "height": 1080 },
  "actions": [
    { "action": "navigate", "url": "https://example.com", "wait": 3000, "label": "Homepage" },
    { "action": "scroll", "y": 600, "wait": 2000, "label": "Scroll to features" },
    { "action": "hover", "selector": ".feature-card:first-child", "wait": 1500, "label": "Hover feature 1" },
    { "action": "click", "selector": ".cta-button", "wait": 2000, "label": "Click CTA" },
    { "action": "type", "selector": "input[name=email]", "text": "demo@example.com", "wait": 1000, "label": "Fill email" }
  ]
}
```

**Action types:**

| Action | Required Fields | Description |
|--------|----------------|-------------|
| `navigate` | `url` | Go to a URL. Cursor overlay is auto-injected after each navigation. |
| `click` | `selector` | Move cursor smoothly to element, then click. Cursor pulses on click. |
| `click_at` | `x`, `y` | Move cursor to exact pixel coordinates and click. Use when selectors don't work (SPAs, shadow DOM, custom components). |
| `scroll` | `y` | Smooth scroll by Y pixels. Use negative for scrolling up. |
| `hover` | `selector` | Move cursor smoothly to element and pause. |
| `type` | `selector`, `text` | Click element, then type text character by character (80ms delay). |
| `keyboard_type` | `text` | Type text directly via keyboard without targeting a selector. Use after `click_at` to type into focused elements. Optional `delay` field (default 80ms). |
| `keyboard_press` | `key` | Press a keyboard key (e.g., `Enter`, `Tab`, `Escape`, `ArrowDown`). |
| `wait` | — | Just pause. Only uses the `wait` field. |

Every action has an optional `wait` field (milliseconds to pause after the action, default 1000) and an optional `label` for the moments log.

**Tips:**
- Add generous `wait` times (2-3s) after navigations to let pages load
- The cursor overlay auto-injects on every `navigate` action
- For hover effects (tooltips, dropdowns), use `hover` + a long `wait`
- The cursor moves smoothly to click/hover targets with realistic motion (20-25 steps)
- **When selectors fail** (SPAs like Perplexity, Notion, etc.), use `click_at` with pixel coordinates + `keyboard_type` instead of `click`/`type`. Find the input location visually and click at those coordinates.

### Step 3: Run the Recording

```bash
python3 scripts/steel-browse.py workspace/screen-demos/{slug}/browse-plan.json workspace/screen-demos/{slug}
```

This will:
1. Create a Steel cloud browser session
2. Print the **viewer URL** (share with user so they can watch live)
3. Execute all actions with the custom large cursor
4. Release the session
5. Download the recording as `recording.mp4` (via HLS -> ffmpeg)
6. Save `moments.json` with timestamped action log

**Output files:**
```
workspace/screen-demos/{slug}/
├── browse-plan.json    # The input plan
├── recording.mp4       # Raw session recording
└── moments.json        # Timestamped action log
```

The script outputs JSON to stdout with `viewer_url`, `recording`, and `moments` paths.

### Step 4: Present the Recording

Tell the user:
1. The **viewer URL** — they can replay the session in their browser
2. The **recording path** — the raw MP4 file
3. The **moments** — summarize the timestamped actions

Do NOT try to read the recording MP4 in chat (it's too large). Just tell the user the file path.

### Step 5: Build the Edit Config

Based on `moments.json`, build the edit config. **Always add zooms to key moments.** Do not ask the user whether they want zooms — always include them. Good zoom targets:

- **Clicks** — Zoom 1.5x into the button/link area right before the click
- **Typing** — Zoom 2.0x into the input field while text is being entered
- **Hover reveals** — Zoom 1.5x into the element showing a tooltip/dropdown
- **Key UI changes** — Zoom 1.5x into results, loading states, or important content

For flat/overview moments (page loads, scrolling), use `zoom: null`.

**Always present the edit plan to the user before rendering:**

```
Clip 1: 0s -> 5s — Homepage hero (no zoom)
Clip 2: 5s -> 9s — Click CTA button (zoom 1.5x into button area, ~65% right, 35% down)
Clip 3: 10s -> 15s — Results page (no zoom)
```

### Step 6: Set Up Gradient Background

**Always copy a gradient to Remotion before rendering.** Default to the dark gradient unless the user requests light:

```bash
cp .claude/skills/screen-demo/assets/gradient-dark.jpg remotion/public/gradient.jpg
```

For a lighter/warmer look:
```bash
cp .claude/skills/screen-demo/assets/gradient-light.jpg remotion/public/gradient.jpg
```

The user can also provide their own gradient image — just copy it to `remotion/public/gradient.jpg`.

The Remotion ZoomClip component renders each clip with:
- The gradient image as a full-bleed background
- 64px padding around the video
- 24px rounded corners on the video
- A subtle box shadow and light grey border (`2px solid rgba(180, 180, 180, 0.6)`)
- Spring-animated zoom in/out (damping: 28, stiffness: 60, mass: 0.8) for Screen Studio feel

### Step 7: Build the Edit Config JSON

Create `edit-config.json`:

```json
{
  "fps": 30,
  "width": 1920,
  "height": 1080,
  "source": "recording.mp4",
  "clips": [
    {
      "startMs": 0,
      "endMs": 5000,
      "zoom": null
    },
    {
      "startMs": 5000,
      "endMs": 9000,
      "zoom": { "scale": 1.5, "originX": 65, "originY": 35 }
    },
    {
      "startMs": 10000,
      "endMs": 15000,
      "zoom": null
    }
  ],
  "transitionDurationMs": 500
}
```

**Zoom config:**
- `scale` — Zoom level. Default 1.5 (150%) for most moments, 2.0 (200%) for typing text.
- `originX` — Horizontal zoom center as percentage (0 = left edge, 100 = right edge)
- `originY` — Vertical zoom center as percentage (0 = top, 100 = bottom)
- Zooms use spring easing (0.8s ease in, hold, 0.8s ease out) for Screen Studio feel

**Transitions:**
- All clips are connected with crossfade transitions
- `transitionDurationMs: 500` = 0.5s crossfade (good default)

**Clip trimming tips:**
- Cut out long wait times (loading screens, generation delays)
- Keep clips tight — 3-8 seconds each
- Total video should be 15-60 seconds for Instagram

### Step 8: Render the Final Video

```bash
node remotion/render.mjs workspace/screen-demos/{slug}/edit-config.json workspace/screen-demos/{slug}/recording.mp4 workspace/screen-demos/{slug}/demo.mp4
```

This:
1. Copies the recording into Remotion's public/ directory
2. Bundles the Remotion project
3. Renders the composition with gradient background, zoom effects, and transitions
4. Outputs the final video as `demo.mp4`

Progress is printed to stderr. Rendering takes 1-5 minutes depending on video length.

**Important:** The `node` command must be able to find the Remotion dependencies. If it fails with module errors, run `cd remotion && npm install` first.

### Step 9: Extract GIF for Carousel (Optional)

If the demo will be embedded in a carousel slide, extract a sped-up GIF:

```bash
ffmpeg -ss 0 -t {duration}s -i workspace/screen-demos/{slug}/demo.mp4 \
  -vf "setpts=0.25*PTS,fps=12,scale=920:-1:flags=lanczos" \
  -loop 0 workspace/screen-demos/{slug}/demo-4x.gif
```

- `setpts=0.25*PTS` = 4x speed (adjust multiplier as needed)
- `fps=12` = good balance of smoothness vs file size for GIF
- `scale=920:-1` = fits well inside carousel slides
- Aim for 8-15 seconds of GIF playback after speedup
- To get 12s of GIF at 4x, you need ~48s of source video

### Step 10: Present the Output

Tell the user:
1. The **output path** — `workspace/screen-demos/{slug}/demo.mp4`
2. The **file size**
3. Offer to adjust — change clips, zoom targets, re-render

**Final output structure:**
```
workspace/screen-demos/{slug}/
├── browse-plan.json    # Input browsing plan
├── recording.mp4       # Raw recording
├── moments.json        # Action timestamps
├── edit-config.json    # Clip & zoom config
├── demo.mp4            # Final polished video (gradient + zooms)
└── demo-4x.gif         # Optional sped-up GIF for carousels
```

---

## Defaults (Always Apply)

These are always applied to every screen demo render. Do not skip them unless the user explicitly asks:

1. **Gradient background** — Copy a gradient from `assets/` to `remotion/public/gradient.jpg` before every render
2. **Zooms on key moments** — Always add zoom effects to clicks, typing, and UI reveals
3. **Tight clip trimming** — Cut out dead time, loading waits, and boring stretches
4. **Crossfade transitions** — 500ms fades between all clips
5. **Spring animation** — Zooms use `{ damping: 28, stiffness: 60, mass: 0.8 }` for buttery Screen Studio feel
6. **GIF extraction** — When the demo is for a carousel, always extract a 4x sped-up GIF

---

## Requirements

| Dependency | Install |
|-----------|---------|
| `STEEL_API_KEY` | Add to `.env` — get from [app.steel.dev](https://app.steel.dev/settings/api-keys) |
| `steel-sdk` | `pip install steel-sdk` |
| `playwright` | `pip install playwright && playwright install chromium` |
| `ffmpeg` | `brew install ffmpeg` |
| Node.js | Required for Remotion — install from [nodejs.org](https://nodejs.org/) |
| Remotion | `cd remotion && npm install` |

---

## Troubleshooting

**Steel session fails to connect:** Check your `STEEL_API_KEY` in `.env`. Free tier allows 5 concurrent sessions and 500 daily requests.

**Recording download fails (HLS not ready):** Steel recordings take 5-30 seconds to process after session release. The script retries automatically with backoff (up to 300s timeout). If all retries fail, the viewer URL still works — user can screen-record it manually.

**Remotion render fails with module errors:** Run `cd remotion && npm install` to install dependencies. All `@remotion/*` packages must be at the exact same version.

**Cursor not visible in recording:** The cursor is injected via JavaScript after each `navigate` action. If a page blocks JS injection (CSP), the native browser cursor will still be recorded but at default size.

**Video too long / too short:** Adjust the `wait` values in the browsing plan. More wait = longer recording = more to work with when clipping.

**Disk space errors (ENOSPC):** Remotion renders can be large. Run `brew cleanup --prune=all` and clear old recordings if disk is tight. Need at least 2-3GB free.

**Gradient not showing:** Make sure `remotion/public/gradient.jpg` exists before rendering. Copy from `.claude/skills/screen-demo/assets/`.

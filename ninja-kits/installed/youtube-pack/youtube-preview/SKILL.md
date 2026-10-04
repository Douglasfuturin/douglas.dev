---
name: youtube-preview
description: Use when the user wants to preview how a YouTube thumbnail and title will look on the platform. Generates realistic YouTube card mockups in dark or light mode, compares multiple title options side by side, and shows how videos appear in the feed.
---

# YouTube Preview Generator

Generate realistic YouTube preview mockups showing exactly how a thumbnail + title combination will appear on the platform. Supports single card previews, side-by-side title comparisons, and simulated feed context.

---

## When to Use

- After generating thumbnails (youtube-thumbnail skill) — see how they look with actual titles
- After brainstorming titles (youtube-title skill) — compare title options visually
- Before publishing — final gut-check on the thumbnail+title package
- During iteration — quickly see how changes affect the overall look

---

## Process

### Step 1: Gather Inputs

You need at minimum:
- **A thumbnail image** — path to an existing thumbnail PNG (usually in `workspace/{today}/thumbnails/`)
- **A title** — one or more title strings to preview

Optional:
- Duration text (e.g., "12:34")
- Views/time-ago text for realism
- Channel avatar path (default: branded green "T" avatar)
- Theme preference (dark/light — default: dark)

If the user already has thumbnails generated from the youtube-thumbnail skill, use those paths. If they have title options from the youtube-title skill, use those strings.

### Step 2: Choose the Right Mode

| Scenario | Mode | What it does |
|----------|------|-------------|
| Preview one thumbnail+title | `card` | Single YouTube card with padding |
| Compare title options | `compare` | Side-by-side cards (same thumbnail, different titles), labeled A/B/C |
| Compare different thumbnails | `compare` | Side-by-side cards (different thumbnails paired with different titles) |
| See it in context | `feed` | Card placed between placeholder videos in a 3-column feed |

The script auto-detects: 1 title = `card`, multiple titles = `compare`. Override with `--mode`.

### Step 3: Generate the Preview

**Single card:**
```bash
python3 .claude/skills/youtube-preview/scripts/generate_preview.py \
  --thumbnail "workspace/{today}/thumbnails/{slug}-a.png" \
  --title "How I Built an AI Agent That Replaced My Entire Workflow" \
  --duration "12:34" \
  --output "workspace/{today}/previews/{slug}-preview.png"
```

**Compare multiple titles (same thumbnail):**
```bash
python3 .claude/skills/youtube-preview/scripts/generate_preview.py \
  --thumbnail "workspace/{today}/thumbnails/{slug}-a.png" \
  --title "How I Built an AI Agent That Replaced My Entire Workflow" \
         "This AI Agent Does What 5 Employees Can't" \
         "I Automated My Entire Business With One AI Agent" \
  --duration "12:34" \
  --output "workspace/{today}/previews/{slug}-titles-compare.png"
```

**Compare different thumbnail+title packages:**
```bash
python3 .claude/skills/youtube-preview/scripts/generate_preview.py \
  --thumbnail "workspace/{today}/thumbnails/{slug}-a.png" "workspace/{today}/thumbnails/{slug}-b.png" \
  --title "Title for Thumbnail A" "Title for Thumbnail B" \
  --duration "12:34" \
  --output "workspace/{today}/previews/{slug}-package-compare.png"
```

**Feed context (see it surrounded by other videos):**
```bash
python3 .claude/skills/youtube-preview/scripts/generate_preview.py \
  --thumbnail "workspace/{today}/thumbnails/{slug}-a.png" \
  --title "How I Built an AI Agent That Replaced My Entire Workflow" \
  --duration "12:34" \
  --mode feed \
  --output "workspace/{today}/previews/{slug}-feed.png"
```

**Light mode:**
Add `--theme light` to any command.

### Step 4: Present and Iterate

Show the preview image to the user. If in compare mode, reference the labels:
- **A:** "How I Built an AI Agent That Replaced My Entire Workflow"
- **B:** "This AI Agent Does What 5 Employees Can't"
- **C:** "I Automated My Entire Business With One AI Agent"

Ask which title (or combination) works best. Re-generate with refinements as needed.

---

## Full CLI Reference

```
Arguments:
  --thumbnail    Path(s) to thumbnail image(s) [required]
  --title        Video title(s) to preview [required]
  --output       Output file path [required]
  --mode         auto | card | compare | feed (default: auto)
  --channel-name Channel name (default: "Your Channel")
  --channel-avatar Path to avatar image (default: branded green avatar)
  --views        View count text (e.g., "1.2K views")
  --time-ago     Time text (e.g., "2 hours ago")
  --duration     Duration badge text (e.g., "12:34")
  --theme        dark | light (default: dark)
```

**Thumbnail/title pairing rules:**
- 1 thumbnail + N titles = thumbnail reused for each title card
- N thumbnails + N titles = paired 1:1 (thumb A with title A, thumb B with title B)
- Mismatched counts (other than 1:N) = error

---

## Output

Use today's date (YYYY-MM-DD format) for the date folder. For example, if today is 2026-02-18, the output goes in `workspace/2026-02-18/previews/`.

Previews save to `workspace/{today}/previews/` at the project root:
```
workspace/{today}/previews/{slug}-preview.png         (single card)
workspace/{today}/previews/{slug}-titles-compare.png  (title comparison)
workspace/{today}/previews/{slug}-package-compare.png (thumbnail+title comparison)
workspace/{today}/previews/{slug}-feed.png            (feed context)
```

Create the `workspace/{today}/previews/` directory if it doesn't exist (the script handles this automatically).

---

## Tips

- **Always use the duration badge** — it makes the preview look significantly more realistic
- **Compare 3-4 title options max** — more than that gets hard to evaluate at a glance
- **Use feed mode for the final check** — seeing the card next to placeholders is the closest simulation to the real YouTube experience
- **Check both dark and light themes** — most viewers use dark mode, but light mode is worth checking too
- **Title length matters visually** — a title that looks great in text might wrap awkwardly on the card. The preview catches this instantly

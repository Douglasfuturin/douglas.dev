---
name: instagram-carousel-preview
description: Use when the user wants to generate a carousel preview image, create a social media preview of a carousel, stitch carousel slides into one image, or share a carousel as a single wide image.
---

# Carousel Preview Generator

Takes a carousel directory and stitches all slides into a single wide horizontal image with a dark background — ready to share on social media.

## Process

### Step 1: Find the Carousel

The user provides either:
- A full path: `workspace/carousel/Claude Code Skills 101/`
- A carousel name: `Claude Code Skills 101`

If they give just a name, look in `workspace/carousel/{name}/`.

### Step 2: Generate the Preview

```bash
python3 .claude/skills/instagram-carousel-preview/scripts/carousel_preview.py "workspace/carousel/{name}/"
```

**Options:**
- `--height N` — Target slide height in pixels (default: 600). Use 400 for a smaller preview, 800 for higher quality.
- `--output path.png` — Custom output path (default: `preview.png` in the carousel directory).

### Step 3: Show the Result

Read the generated `preview.png` and display it to the user.

If the user wants adjustments, re-run with different options:
- **Bigger/smaller:** Adjust `--height`
- **Different output location:** Use `--output`

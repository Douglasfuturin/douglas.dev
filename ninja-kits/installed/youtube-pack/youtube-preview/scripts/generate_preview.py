#!/usr/bin/env python3
"""
Generate YouTube preview mockups showing how a thumbnail + title
combination will appear on the YouTube platform.

Usage:
    Single card preview:
    python3 generate_preview.py \
        --thumbnail path/to/thumbnail.png \
        --title "My Video Title Here" \
        --output path/to/preview.png

    Compare multiple titles (same thumbnail):
    python3 generate_preview.py \
        --thumbnail path/to/thumbnail.png \
        --title "Title Option A" "Title Option B" "Title Option C" \
        --output path/to/preview.png

    Compare different thumbnail+title packages:
    python3 generate_preview.py \
        --thumbnail thumb-a.png thumb-b.png \
        --title "Title A" "Title B" \
        --output path/to/preview.png

    Show in simulated feed:
    python3 generate_preview.py \
        --thumbnail path/to/thumbnail.png \
        --title "My Video Title" \
        --mode feed \
        --output path/to/preview.png

Environment:
    Requires Pillow: pip install Pillow
"""

import argparse
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


# ── Scale & Dimensions ─────────────────────────────────────────

SCALE = 2  # Render at 2x for crisp output

# Card dimensions (base values, multiplied by SCALE)
CARD_W = 360 * SCALE
THUMB_H = int(CARD_W * 9 / 16)  # 16:9
CORNER_R = 12 * SCALE

# Metadata area
PAD_TOP = 12 * SCALE
PAD_BOTTOM = 12 * SCALE
AVATAR_SIZE = 36 * SCALE
AVATAR_GAP = 12 * SCALE
TITLE_META_GAP = 2 * SCALE

# Typography
TITLE_FONT_SIZE = 14 * SCALE
META_FONT_SIZE = 12 * SCALE
TITLE_LINE_HEIGHT = 20 * SCALE
META_LINE_HEIGHT = 18 * SCALE
MAX_TITLE_LINES = 2

# Duration badge
DURATION_FONT_SIZE = 12 * SCALE
DURATION_PAD_X = 4 * SCALE
DURATION_PAD_Y = 3 * SCALE
DURATION_MARGIN = 8 * SCALE
DURATION_RADIUS = 4 * SCALE

# Layout spacing
CARD_MARGIN = 32 * SCALE
CARD_GAP = 16 * SCALE
LABEL_FONT_SIZE = 13 * SCALE
LABEL_GAP = 10 * SCALE


# ── Themes ─────────────────────────────────────────────────────

THEMES = {
    "dark": {
        "bg": (15, 15, 15),
        "title": (241, 241, 241),
        "meta": (170, 170, 170),
        "duration_bg": (0, 0, 0, 204),
        "duration_text": (255, 255, 255),
        "placeholder_thumb": (38, 38, 38),
        "placeholder_line": (55, 55, 55),
        "placeholder_circle": (55, 55, 55),
        "label": (170, 170, 170),
    },
    "light": {
        "bg": (255, 255, 255),
        "title": (15, 15, 15),
        "meta": (96, 96, 96),
        "duration_bg": (0, 0, 0, 204),
        "duration_text": (255, 255, 255),
        "placeholder_thumb": (229, 229, 229),
        "placeholder_line": (210, 210, 210),
        "placeholder_circle": (210, 210, 210),
        "label": (96, 96, 96),
    },
}


# ── Font Loading ───────────────────────────────────────────────

_font_cache = {}


def load_font(size, bold=False):
    """Load the best available font for YouTube-like rendering."""
    key = (size, bold)
    if key in _font_cache:
        return _font_cache[key]

    if bold:
        paths = [
            "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
            "/System/Library/Fonts/Helvetica.ttc",
        ]
    else:
        paths = [
            "/System/Library/Fonts/Supplemental/Arial.ttf",
            "/System/Library/Fonts/Helvetica.ttc",
        ]

    for path in paths:
        try:
            font = ImageFont.truetype(path, size)
            _font_cache[key] = font
            return font
        except (OSError, IOError):
            continue

    font = ImageFont.load_default()
    _font_cache[key] = font
    return font


# ── Image Helpers ──────────────────────────────────────────────


def round_corners(img, radius):
    """Apply rounded corners to an image."""
    mask = Image.new("L", img.size, 0)
    draw = ImageDraw.Draw(mask)
    draw.rounded_rectangle(
        [0, 0, img.width - 1, img.height - 1], radius=radius, fill=255
    )

    if img.mode != "RGBA":
        img = img.convert("RGBA")

    result = Image.new("RGBA", img.size, (0, 0, 0, 0))
    result.paste(img, mask=mask)
    return result


def create_circle_mask(size):
    """Create a circular mask."""
    mask = Image.new("L", (size, size), 0)
    draw = ImageDraw.Draw(mask)
    draw.ellipse([0, 0, size - 1, size - 1], fill=255)
    return mask


def create_default_avatar(size):
    """Create a default channel avatar (green circle with 'T')."""
    avatar = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(avatar)

    # Green circle (brand color #00CB5A)
    draw.ellipse([0, 0, size - 1, size - 1], fill=(0, 203, 90))

    # "T" letter centered
    font = load_font(int(size * 0.5), bold=True)
    bbox = font.getbbox("T")
    text_w = bbox[2] - bbox[0]
    text_h = bbox[3] - bbox[1]
    x = (size - text_w) // 2 - bbox[0]
    y = (size - text_h) // 2 - bbox[1]
    draw.text((x, y), "T", fill=(255, 255, 255), font=font)

    return avatar


def wrap_text(text, font, max_width, max_lines=2):
    """Word-wrap text, truncating with ellipsis if it exceeds max_lines."""
    words = text.split()
    if not words:
        return [""]

    lines = []
    current = words[0]

    for word in words[1:]:
        test = f"{current} {word}"
        w = font.getbbox(test)[2] - font.getbbox(test)[0]

        if w <= max_width:
            current = test
        else:
            lines.append(current)
            current = word

            if len(lines) >= max_lines:
                # Truncate last line with ellipsis
                _truncate_line(lines, max_lines - 1, font, max_width)
                return lines[:max_lines]

    lines.append(current)

    if len(lines) > max_lines:
        lines = lines[:max_lines]
        _truncate_line(lines, max_lines - 1, font, max_width)

    return lines


def _truncate_line(lines, idx, font, max_width):
    """Truncate a line with ellipsis to fit within max_width."""
    last = lines[idx]
    test_w = font.getbbox(last + "...")[2] - font.getbbox(last + "...")[0]
    if test_w <= max_width:
        lines[idx] = last + "..."
        return

    while last:
        if " " in last:
            last = last.rsplit(" ", 1)[0]
        else:
            last = last[:-1]
        test_w = font.getbbox(last + "...")[2] - font.getbbox(last + "...")[0]
        if test_w <= max_width:
            break

    lines[idx] = last + "..."


# ── Card Rendering ─────────────────────────────────────────────


def render_card(
    thumbnail_path, title, channel_name, avatar_img,
    views=None, time_ago=None, duration=None, theme_name="dark",
):
    """Render a single YouTube video card. Returns PIL Image (RGBA)."""
    theme = THEMES[theme_name]

    # Load and resize thumbnail
    thumb = Image.open(thumbnail_path).convert("RGBA")
    thumb = thumb.resize((CARD_W, THUMB_H), Image.LANCZOS)
    thumb = round_corners(thumb, CORNER_R)

    # Fonts
    title_font = load_font(TITLE_FONT_SIZE, bold=True)
    meta_font = load_font(META_FONT_SIZE, bold=False)

    # Compute text layout
    text_area_w = CARD_W - AVATAR_SIZE - AVATAR_GAP
    title_lines = wrap_text(title, title_font, text_area_w, MAX_TITLE_LINES)
    title_block_h = len(title_lines) * TITLE_LINE_HEIGHT

    meta_parts = [channel_name]
    if views or time_ago:
        sub = " \u00b7 ".join(filter(None, [views, time_ago]))
        meta_parts.append(sub)
    meta_block_h = len(meta_parts) * META_LINE_HEIGHT

    info_h = PAD_TOP + title_block_h + TITLE_META_GAP + meta_block_h + PAD_BOTTOM
    card_h = THUMB_H + info_h

    # Canvas
    card = Image.new("RGBA", (CARD_W, int(card_h)), (*theme["bg"], 255))

    # Thumbnail
    card.paste(thumb, (0, 0), thumb)

    # Duration badge
    if duration:
        _draw_duration_badge(card, duration, theme)

    # Avatar
    avatar_y = int(THUMB_H + PAD_TOP)
    if avatar_img:
        av = avatar_img.resize((AVATAR_SIZE, AVATAR_SIZE), Image.LANCZOS).convert("RGBA")
    else:
        av = create_default_avatar(AVATAR_SIZE)

    circ_mask = create_circle_mask(AVATAR_SIZE)
    av_composite = Image.new("RGBA", (AVATAR_SIZE, AVATAR_SIZE), (0, 0, 0, 0))
    av_composite.paste(av, (0, 0), circ_mask)
    card.paste(av_composite, (0, avatar_y), av_composite)

    # Text
    draw = ImageDraw.Draw(card)
    text_x = AVATAR_SIZE + AVATAR_GAP
    text_y = THUMB_H + PAD_TOP

    for line in title_lines:
        draw.text((text_x, text_y), line, fill=theme["title"], font=title_font)
        text_y += TITLE_LINE_HEIGHT

    text_y += TITLE_META_GAP
    for line in meta_parts:
        draw.text((text_x, text_y), line, fill=theme["meta"], font=meta_font)
        text_y += META_LINE_HEIGHT

    return card


def _draw_duration_badge(card, duration, theme):
    """Draw a duration badge on the bottom-right of the thumbnail."""
    dur_font = load_font(DURATION_FONT_SIZE, bold=True)
    bbox = dur_font.getbbox(duration)
    dur_w = int(bbox[2] - bbox[0] + DURATION_PAD_X * 2)
    dur_h = int(bbox[3] - bbox[1] + DURATION_PAD_Y * 2)

    dur_x = int(CARD_W - dur_w - DURATION_MARGIN)
    dur_y = int(THUMB_H - dur_h - DURATION_MARGIN)

    badge = Image.new("RGBA", (dur_w, dur_h), (0, 0, 0, 0))
    badge_draw = ImageDraw.Draw(badge)
    badge_draw.rounded_rectangle(
        [0, 0, dur_w - 1, dur_h - 1],
        radius=DURATION_RADIUS,
        fill=theme["duration_bg"],
    )
    badge_draw.text(
        (DURATION_PAD_X - bbox[0], DURATION_PAD_Y - bbox[1]),
        duration,
        fill=theme["duration_text"],
        font=dur_font,
    )
    card.paste(badge, (dur_x, dur_y), badge)


def render_placeholder_card(theme_name="dark"):
    """Render a placeholder YouTube card for feed context."""
    theme = THEMES[theme_name]

    info_h = PAD_TOP + 2 * TITLE_LINE_HEIGHT + TITLE_META_GAP + 2 * META_LINE_HEIGHT + PAD_BOTTOM
    card_h = int(THUMB_H + info_h)

    card = Image.new("RGBA", (CARD_W, card_h), (*theme["bg"], 255))
    draw = ImageDraw.Draw(card)

    # Placeholder thumbnail
    ph_thumb = Image.new("RGBA", (CARD_W, THUMB_H), (*theme["placeholder_thumb"], 255))
    ph_thumb = round_corners(ph_thumb, CORNER_R)
    card.paste(ph_thumb, (0, 0), ph_thumb)

    # Placeholder avatar
    av_y = THUMB_H + PAD_TOP
    draw.ellipse(
        [0, int(av_y), AVATAR_SIZE, int(av_y) + AVATAR_SIZE],
        fill=theme["placeholder_circle"],
    )

    # Placeholder text lines
    text_x = AVATAR_SIZE + AVATAR_GAP
    line_h = int(10 * SCALE)
    line_gap = int(8 * SCALE)
    r = int(4 * SCALE)

    y = int(THUMB_H + PAD_TOP)
    draw.rounded_rectangle(
        [text_x, y, text_x + int(CARD_W * 0.72), y + line_h], radius=r,
        fill=theme["placeholder_line"],
    )
    y += line_h + line_gap
    draw.rounded_rectangle(
        [text_x, y, text_x + int(CARD_W * 0.48), y + line_h], radius=r,
        fill=theme["placeholder_line"],
    )

    y += line_h + line_gap + TITLE_META_GAP
    draw.rounded_rectangle(
        [text_x, y, text_x + int(CARD_W * 0.32), y + line_h], radius=r,
        fill=theme["placeholder_line"],
    )

    return card


# ── Layout Modes ───────────────────────────────────────────────


def layout_single(card, theme_name="dark"):
    """Single card centered with padding."""
    theme = THEMES[theme_name]
    m = CARD_MARGIN

    w = card.width + m * 2
    h = card.height + m * 2

    canvas = Image.new("RGBA", (w, h), (*theme["bg"], 255))
    canvas.paste(card, (m, m), card)
    return canvas


def layout_compare(cards, labels, theme_name="dark"):
    """Multiple cards side by side with letter labels."""
    theme = THEMES[theme_name]
    m = CARD_MARGIN
    gap = CARD_GAP

    n = len(cards)
    max_h = max(c.height for c in cards)

    label_font = load_font(LABEL_FONT_SIZE, bold=True)
    label_h = LABEL_GAP + LABEL_FONT_SIZE + LABEL_GAP

    w = m + n * CARD_W + (n - 1) * gap + m
    h = m + int(label_h) + max_h + m

    canvas = Image.new("RGBA", (w, h), (*theme["bg"], 255))
    draw = ImageDraw.Draw(canvas)

    x = m
    for i, card in enumerate(cards):
        # Label
        label = labels[i] if i < len(labels) else chr(65 + i)
        lbl_bbox = label_font.getbbox(label)
        lbl_w = lbl_bbox[2] - lbl_bbox[0]
        lbl_x = x + (CARD_W - lbl_w) // 2 - lbl_bbox[0]
        lbl_y = m + LABEL_GAP
        draw.text((lbl_x, lbl_y), label, fill=theme["label"], font=label_font)

        # Card
        card_y = m + int(label_h)
        canvas.paste(card, (x, card_y), card)
        x += CARD_W + gap

    return canvas


def layout_feed(card, theme_name="dark"):
    """Card placed in a simulated 3-column YouTube feed."""
    theme = THEMES[theme_name]
    m = CARD_MARGIN
    gap = CARD_GAP

    placeholder = render_placeholder_card(theme_name)
    max_h = max(card.height, placeholder.height)

    w = m + 3 * CARD_W + 2 * gap + m
    h = m + max_h + m

    canvas = Image.new("RGBA", (w, h), (*theme["bg"], 255))

    # Left placeholder
    canvas.paste(placeholder, (m, m), placeholder)

    # Center: user's video
    cx = m + CARD_W + gap
    canvas.paste(card, (cx, m), card)

    # Right placeholder
    rx = m + 2 * (CARD_W + gap)
    canvas.paste(placeholder, (rx, m), placeholder)

    return canvas


# ── Main ───────────────────────────────────────────────────────


def parse_args():
    parser = argparse.ArgumentParser(
        description="Generate YouTube preview mockups"
    )
    parser.add_argument(
        "--thumbnail", required=True, nargs="+",
        help="Path(s) to thumbnail image(s)",
    )
    parser.add_argument(
        "--title", required=True, nargs="+",
        help="Video title(s) to preview",
    )
    parser.add_argument(
        "--output", required=True,
        help="Output file path",
    )
    parser.add_argument(
        "--mode", default="auto",
        choices=["auto", "card", "compare", "feed"],
        help="Layout mode (default: auto — card for 1 title, compare for multiple)",
    )
    parser.add_argument(
        "--channel-name", default="Your Channel",
        help="Channel name (default: Your Channel)",
    )
    # Default avatar: use headshot from the thumbnail skill
    default_avatar = None
    headshot_dir = Path(__file__).resolve().parents[2] / "youtube-thumbnail" / "headshots"
    if headshot_dir.exists():
        pngs = sorted(headshot_dir.glob("*.png"))
        if pngs:
            default_avatar = str(pngs[0])

    parser.add_argument(
        "--channel-avatar", default=default_avatar,
        help="Path to channel avatar image (default: headshot from thumbnail skill)",
    )
    parser.add_argument(
        "--views", default=None,
        help='View count text (e.g., "1.2K views")',
    )
    parser.add_argument(
        "--time-ago", default=None,
        help='Time text (e.g., "2 hours ago")',
    )
    parser.add_argument(
        "--duration", default=None,
        help='Video duration badge (e.g., "12:34")',
    )
    parser.add_argument(
        "--theme", default="dark", choices=["dark", "light"],
        help="YouTube theme (default: dark)",
    )
    return parser.parse_args()


def main():
    args = parse_args()

    # Validate thumbnail paths
    for t in args.thumbnail:
        if not Path(t).exists():
            print(f"Error: Thumbnail not found: {t}", file=sys.stderr)
            sys.exit(1)

    # Load avatar
    avatar = None
    if args.channel_avatar and Path(args.channel_avatar).exists():
        avatar = Image.open(args.channel_avatar).convert("RGBA")

    # Match thumbnails to titles
    n_thumbs = len(args.thumbnail)
    n_titles = len(args.title)

    if n_thumbs == 1 and n_titles >= 1:
        # One thumbnail, one or more titles: reuse thumbnail for each
        pairs = [(args.thumbnail[0], t) for t in args.title]
    elif n_thumbs == n_titles:
        # Matched pairs
        pairs = list(zip(args.thumbnail, args.title))
    else:
        print(
            f"Error: Got {n_thumbs} thumbnail(s) and {n_titles} title(s). "
            "Provide either 1 thumbnail (reused for all titles) or equal counts.",
            file=sys.stderr,
        )
        sys.exit(1)

    # Determine mode
    mode = args.mode
    if mode == "auto":
        mode = "compare" if len(pairs) > 1 else "card"

    # Render cards
    cards = []
    for thumb_path, title in pairs:
        card = render_card(
            thumb_path, title, args.channel_name, avatar,
            args.views, args.time_ago, args.duration, args.theme,
        )
        cards.append(card)

    # Generate labels
    labels = [chr(65 + i) for i in range(len(cards))]

    # Layout
    if mode == "card":
        result = layout_single(cards[0], args.theme)
    elif mode == "compare":
        result = layout_compare(cards, labels, args.theme)
    elif mode == "feed":
        result = layout_feed(cards[0], args.theme)
    else:
        result = layout_single(cards[0], args.theme)

    # Save
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    result.convert("RGB").save(str(output_path), quality=95)

    print(f"Preview saved to: {output_path}")
    print(f"Mode: {mode} | Theme: {args.theme} | Cards: {len(cards)}")


if __name__ == "__main__":
    main()

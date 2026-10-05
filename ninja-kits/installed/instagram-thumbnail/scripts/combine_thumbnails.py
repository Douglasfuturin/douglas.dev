#!/usr/bin/env python3
"""
Combine multiple vertical cover images into a comparison grid.

For 4 images: creates a 4-across horizontal row (best for comparing vertical images).
For 2 images: side by side.

Usage:
    python3 combine_thumbnails.py \
        --images cover1.png cover2.png cover3.png cover4.png \
        --output comparison.png \
        --labels "A" "B" "C" "D"
"""

import argparse
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


def parse_args():
    parser = argparse.ArgumentParser(description="Combine vertical covers into comparison grid")
    parser.add_argument(
        "--images", required=True, nargs="+",
        help="Paths to cover images (expects 4 for a 4-across grid)"
    )
    parser.add_argument(
        "--output", required=True,
        help="Output file path for the combined grid image"
    )
    parser.add_argument(
        "--labels", nargs="*", default=["A", "B", "C", "D"],
        help="Labels for each cover (default: A B C D)"
    )
    return parser.parse_args()


def add_label(img, label):
    """Add a label badge to the top-left corner of an image."""
    draw = ImageDraw.Draw(img)
    font_size = max(28, img.width // 12)

    try:
        font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", font_size)
    except (OSError, IOError):
        try:
            font = ImageFont.truetype("/System/Library/Fonts/SFNSMono.ttf", font_size)
        except (OSError, IOError):
            font = ImageFont.load_default()

    padding = 12
    bbox = draw.textbbox((0, 0), label, font=font)
    text_w = bbox[2] - bbox[0]
    text_h = bbox[3] - bbox[1]

    badge_w = text_w + padding * 2
    badge_h = text_h + padding * 2
    margin = 16

    draw.rounded_rectangle(
        [margin, margin, margin + badge_w, margin + badge_h],
        radius=8,
        fill=(0, 0, 0, 200),
    )
    draw.text(
        (margin + padding, margin + padding - bbox[1]),
        label, fill="white", font=font,
    )
    return img


def main():
    args = parse_args()

    images = []
    for path in args.images:
        if not Path(path).exists():
            print(f"Error: Image not found: {path}", file=sys.stderr)
            sys.exit(1)
        images.append(Image.open(path).convert("RGBA"))

    # Normalize all images to the same size (use the first image's dimensions)
    target_w, target_h = images[0].size
    resized = []
    for img in images:
        if img.size != (target_w, target_h):
            img = img.resize((target_w, target_h), Image.LANCZOS)
        resized.append(img)

    # Add labels
    labels = args.labels[:len(resized)]
    for i, (img, label) in enumerate(zip(resized, labels)):
        resized[i] = add_label(img, label)

    # Build grid: 4 across in a single row for vertical images
    # This gives a wide comparison that's easy to view
    n = len(resized)
    gap = 8

    if n <= 2:
        # Side by side
        cols, rows = n, 1
    elif n <= 4:
        # All in one row
        cols, rows = n, 1
    else:
        # 2 rows
        cols = (n + 1) // 2
        rows = 2

    grid_w = target_w * cols + gap * (cols - 1)
    grid_h = target_h * rows + gap * (rows - 1)
    grid = Image.new("RGBA", (grid_w, grid_h), (20, 20, 20, 255))

    for i, img in enumerate(resized):
        col = i % cols
        row = i // cols
        x = col * (target_w + gap)
        y = row * (target_h + gap)
        grid.paste(img, (x, y))

    # Save
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    grid.convert("RGB").save(str(output_path), quality=95)
    print(f"Comparison grid saved to: {output_path}")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Carousel Preview Generator

Stitches all slide images from a carousel directory into a single wide
horizontal strip with a dark background — ready to share on social media.

Supports animated slides: if any slide has an MP4 alongside its PNG,
the output is a video (MP4) with the animated slide playing in place.

Usage:
    python3 carousel_preview.py <carousel_dir> [--output preview.png] [--height 600]
"""

import argparse
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter

try:
    import cv2
    HAS_CV2 = True
except ImportError:
    HAS_CV2 = False


# --- Config ---
BG_COLOR = (20, 20, 20)
GAP = 20
PADDING = 40
CORNER_RADIUS = 16
SHADOW_OFFSET = 6
SHADOW_BLUR = 12
DEFAULT_HEIGHT = 600


def natural_sort_key(path):
    """Sort filenames naturally (slide-2 before slide-10)."""
    return [
        int(c) if c.isdigit() else c.lower()
        for c in re.split(r'(\d+)', path.name)
    ]


def round_corners(img, radius):
    """Add rounded corners to an image."""
    mask = Image.new("L", img.size, 0)
    draw = ImageDraw.Draw(mask)
    draw.rounded_rectangle([0, 0, img.width, img.height], radius=radius, fill=255)
    result = img.copy()
    result.putalpha(mask)
    return result


def make_shadow(w, h, radius, offset, blur):
    """Create a drop shadow image."""
    shadow = Image.new("RGBA", (w + blur * 2, h + blur * 2), (0, 0, 0, 0))
    draw = ImageDraw.Draw(shadow)
    draw.rounded_rectangle(
        [blur, blur, blur + w, blur + h],
        radius=radius,
        fill=(0, 0, 0, 80),
    )
    shadow = shadow.filter(ImageFilter.GaussianBlur(blur))
    return shadow


def parse_args():
    parser = argparse.ArgumentParser(description="Generate carousel preview strip")
    parser.add_argument("carousel_dir", help="Path to carousel directory containing slide images")
    parser.add_argument("--output", default=None, help="Output filename (default: auto-detected)")
    parser.add_argument("--height", type=int, default=DEFAULT_HEIGHT, help=f"Target slide height in pixels (default: {DEFAULT_HEIGHT})")
    parser.add_argument("--exclude", nargs="*", default=[], help="Filenames to exclude")
    return parser.parse_args()


def build_layout(slides_png, target_h):
    """Load and scale slides, compute layout positions. Returns (scaled_images, positions, canvas_size)."""
    scaled = []
    for path in slides_png:
        img = Image.open(path).convert("RGBA")
        s = target_h / img.height
        new_w = int(img.width * s)
        img = img.resize((new_w, target_h), Image.LANCZOS)
        img = round_corners(img, CORNER_RADIUS)
        scaled.append(img)

    # Single row layout
    row_w = sum(img.width for img in scaled) + GAP * (len(scaled) - 1)
    total_w = row_w + PADDING * 2
    total_h = target_h + PADDING * 2

    # Compute positions
    positions = []
    x = PADDING
    y = PADDING
    for img in scaled:
        positions.append((x, y))
        x += img.width + GAP

    return scaled, positions, (total_w, total_h)


def render_base_canvas(scaled, positions, canvas_size):
    """Render the static base canvas with shadows and all static slides."""
    canvas = Image.new("RGBA", canvas_size, (*BG_COLOR, 255))

    for img, (x, y) in zip(scaled, positions):
        shadow = make_shadow(img.width, img.height, CORNER_RADIUS, SHADOW_OFFSET, SHADOW_BLUR)
        shadow_x = x - SHADOW_BLUR + SHADOW_OFFSET
        shadow_y = y - SHADOW_BLUR + SHADOW_OFFSET
        canvas.paste(shadow, (shadow_x, shadow_y), shadow)
        canvas.paste(img, (x, y), img)

    return canvas


def generate_static_preview(carousel_dir, slides_png, target_h, output_path):
    """Generate a static PNG preview."""
    scaled, positions, canvas_size = build_layout(slides_png, target_h)
    canvas = render_base_canvas(scaled, positions, canvas_size)

    canvas.convert("RGB").save(str(output_path), quality=95)
    print(f"\nPreview saved to: {output_path}")
    print(f"Dimensions: {canvas_size[0]} x {canvas_size[1]}px")


def generate_video_preview(carousel_dir, slides_png, video_slides, target_h, output_path):
    """Generate a video preview with animated slides composited in."""
    scaled, positions, canvas_size = build_layout(slides_png, target_h)

    # Render the base canvas (with static slides)
    base_canvas = render_base_canvas(scaled, positions, canvas_size)

    # For each video slide, load frames with cv2
    # video_slides: dict of slide_index -> mp4_path
    if not HAS_CV2:
        print("Error: opencv-python (cv2) is required for video previews.", file=sys.stderr)
        print("Install with: pip install opencv-python", file=sys.stderr)
        sys.exit(1)

    # Find the longest video to determine output duration
    video_caps = {}
    video_fps = 30
    max_frames = 0
    for idx, mp4_path in video_slides.items():
        cap = cv2.VideoCapture(str(mp4_path))
        fps = cap.get(cv2.CAP_PROP_FPS) or 30
        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        video_caps[idx] = (cap, frame_count)
        video_fps = fps
        max_frames = max(max_frames, frame_count)

    if max_frames == 0:
        print("Error: Could not read video frames", file=sys.stderr)
        sys.exit(1)

    # Determine target size for video slides
    video_targets = {}
    for idx in video_slides:
        img = scaled[idx]
        video_targets[idx] = (img.width, img.height, positions[idx])

    # Make canvas_size even for h264
    cw = canvas_size[0] if canvas_size[0] % 2 == 0 else canvas_size[0] + 1
    ch = canvas_size[1] if canvas_size[1] % 2 == 0 else canvas_size[1] + 1

    # Start ffmpeg pipe
    ffmpeg_bin = shutil.which("ffmpeg") or "/opt/homebrew/bin/ffmpeg"
    proc = subprocess.Popen(
        [
            ffmpeg_bin, "-y",
            "-f", "rawvideo",
            "-pix_fmt", "rgb24",
            "-s", f"{cw}x{ch}",
            "-r", str(video_fps),
            "-i", "pipe:0",
            "-vcodec", "libx264",
            "-pix_fmt", "yuv420p",
            "-crf", "18",
            "-preset", "fast",
            "-movflags", "+faststart",
            str(output_path),
        ],
        stdin=subprocess.PIPE,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.PIPE,
    )

    # Prepare the rounded corner mask for video frames
    masks = {}
    for idx, (tw, th, _) in video_targets.items():
        mask = Image.new("L", (tw, th), 0)
        ImageDraw.Draw(mask).rounded_rectangle([0, 0, tw, th], radius=CORNER_RADIUS, fill=255)
        masks[idx] = mask

    print(f"Rendering {max_frames} frames at {video_fps}fps...")

    for frame_num in range(max_frames):
        # Start with base canvas
        frame = base_canvas.copy()

        # Composite each video slide's current frame
        for idx, (cap, frame_count) in video_caps.items():
            tw, th, (px, py) = video_targets[idx]

            # Loop video if shorter than max
            actual_frame = frame_num % frame_count
            cap.set(cv2.CAP_PROP_POS_FRAMES, actual_frame)
            ret, bgr = cap.read()
            if not ret:
                cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                ret, bgr = cap.read()
                if not ret:
                    continue

            # Convert BGR -> RGB -> PIL
            rgb = cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB)
            vid_frame = Image.fromarray(rgb).resize((tw, th), Image.LANCZOS)
            vid_frame.putalpha(masks[idx])
            frame.paste(vid_frame, (px, py), vid_frame)

        # Convert to RGB and resize to even dimensions
        rgb_frame = frame.convert("RGB")
        if rgb_frame.size != (cw, ch):
            rgb_frame = rgb_frame.crop((0, 0, cw, ch))

        proc.stdin.write(rgb_frame.tobytes())

        if frame_num % 30 == 0:
            pct = int(frame_num / max_frames * 100)
            print(f"  {pct}%...", end="\r")

    proc.stdin.close()
    proc.wait()

    # Clean up
    for cap, _ in video_caps.values():
        cap.release()

    print(f"\nVideo preview saved to: {output_path}")
    print(f"Dimensions: {cw} x {ch}px, {max_frames} frames @ {video_fps}fps")

    # Also save a static PNG preview (first frame)
    png_path = output_path.with_suffix(".png")
    base_canvas.convert("RGB").save(str(png_path), quality=95)
    print(f"Static preview saved to: {png_path}")


def main():
    args = parse_args()
    carousel_dir = Path(args.carousel_dir)

    if not carousel_dir.is_dir():
        print(f"Error: Not a directory: {carousel_dir}", file=sys.stderr)
        sys.exit(1)

    # Find all PNG slide images, exclude preview files
    exclude = set(args.exclude + ["preview.png"])
    slides_png = sorted(
        [p for p in carousel_dir.glob("slide-*.png") if p.name not in exclude],
        key=natural_sort_key,
    )

    if not slides_png:
        # Fallback: any PNG that's not preview
        slides_png = sorted(
            [p for p in carousel_dir.glob("*.png") if p.name not in exclude],
            key=natural_sort_key,
        )

    if not slides_png:
        print(f"Error: No slide images found in {carousel_dir}", file=sys.stderr)
        sys.exit(1)

    print(f"Found {len(slides_png)} slides:")
    for s in slides_png:
        print(f"  {s.name}")

    # Check for MP4 versions of any slide
    video_slides = {}
    for i, png_path in enumerate(slides_png):
        mp4_path = png_path.with_suffix(".mp4")
        if mp4_path.exists():
            video_slides[i] = mp4_path
            print(f"  -> {mp4_path.name} (animated)")

    has_video = len(video_slides) > 0

    if has_video:
        output_path = Path(args.output) if args.output else carousel_dir / "preview.mp4"
        generate_video_preview(carousel_dir, slides_png, video_slides, args.height, output_path)
    else:
        output_path = Path(args.output) if args.output else carousel_dir / "preview.png"
        generate_static_preview(carousel_dir, slides_png, args.height, output_path)


if __name__ == "__main__":
    main()

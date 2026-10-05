#!/usr/bin/env python3
"""
Generate a LinkedIn carousel slide using Gemini 3 Pro Image Preview.

Usage:
    python3 generate_slide.py \
        --prompt "detailed prompt text" \
        --output path/to/output.png

    With reference images (logos, icons, previous slides):
    python3 generate_slide.py \
        --reference path/to/logo.png path/to/icon.png \
        --prompt "detailed prompt text" \
        --output path/to/output.png

    With example slides for style inspiration:
    python3 generate_slide.py \
        --examples path/to/example1.jpg path/to/example2.jpg \
        --prompt "detailed prompt text" \
        --output path/to/output.png

Environment:
    GEMINI_API_KEY must be set.
"""

import argparse
import os
import sys
from pathlib import Path

from google import genai
from google.genai import types
from PIL import Image

# Enable AVIF support
try:
    import pillow_avif  # noqa: F401
except ImportError:
    pass


def parse_args():
    parser = argparse.ArgumentParser(description="Generate LinkedIn carousel slide via Gemini")
    parser.add_argument(
        "--reference", nargs="*", default=[],
        help="Path(s) to reference images (logos, icons, previous slides for iteration)"
    )
    parser.add_argument(
        "--examples", nargs="*", default=[],
        help="Path(s) to example carousel slides (style inspiration)"
    )
    parser.add_argument(
        "--prompt", required=True,
        help="Detailed prompt for slide generation"
    )
    parser.add_argument(
        "--output", required=True,
        help="Output file path for the generated slide"
    )
    parser.add_argument(
        "--no-style", action="store_true",
        help="Skip appending the carousel style guide to the prompt"
    )
    parser.add_argument(
        "--aspect-ratio", default="1:1",
        choices=["1:1", "3:4", "4:3", "16:9", "9:16"],
        help="Image aspect ratio (default: 1:1)"
    )
    return parser.parse_args()


def validate_image_file(path):
    """Check that a file is actually an image, not HTML or other junk from a failed download."""
    p = Path(path)
    if not p.exists():
        print(f"Error: File not found: {path}", file=sys.stderr)
        sys.exit(1)
    with open(p, "rb") as f:
        header = f.read(256)
    if b"<!DOCTYPE" in header or b"<html" in header or b"<HTML" in header:
        print(
            f"Error: '{path}' is an HTML file, not an image. "
            f"The download URL likely returned a web page instead of the actual image. "
            f"Try downloading from a different source.",
            file=sys.stderr,
        )
        sys.exit(1)
    if len(header) < 8:
        print(f"Error: '{path}' is too small to be a valid image ({len(header)} bytes).", file=sys.stderr)
        sys.exit(1)


def resize_if_needed(img, max_edge=2048):
    """Resize image if larger than max_edge on any side."""
    w, h = img.size
    if max(w, h) > max_edge:
        ratio = max_edge / max(w, h)
        new_size = (int(w * ratio), int(h * ratio))
        return img.resize(new_size, Image.LANCZOS)
    return img


def load_dotenv():
    """Load .env file from project root if it exists."""
    env_path = Path(__file__).resolve().parents[3] / ".env"
    if not env_path.exists():
        env_path = Path.cwd() / ".env"
    if env_path.exists():
        with open(env_path) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, _, value = line.partition("=")
                    os.environ.setdefault(key.strip(), value.strip())


def main():
    args = parse_args()

    load_dotenv()

    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("Error: GEMINI_API_KEY environment variable not set", file=sys.stderr)
        sys.exit(1)

    client = genai.Client(api_key=api_key)

    # Build contents: prompt text + reference images + examples
    #
    # Image order in contents:
    #   1. Reference images (logos, icons, previous slides)
    #   2. Example slides (style inspiration from existing carousels)
    #
    # The prompt should reference these by position (Image 1, Image 2, etc.)
    # Examples are appended last and prefixed with a system note so Gemini
    # knows they're style references, not elements to reproduce exactly.

    prompt = args.prompt

    # Append carousel style guide unless --no-style is set
    if not args.no_style:
        style_path = Path(__file__).resolve().parent.parent / "carousel-style.md"
        if style_path.exists():
            style_text = style_path.read_text().strip()
            prompt += (
                "\n\nCAROUSEL STYLE GUIDE (follow these rules strictly):\n"
                f"{style_text}"
            )

    if args.examples:
        prompt += (
            "\n\nSTYLE EXAMPLES:\n"
            "The final attached images are slides from high-performing LinkedIn carousels. "
            "Study their composition, color usage, typography, diagram layouts, and visual "
            "hierarchy — then apply those patterns to create an ORIGINAL slide. "
            "Do NOT copy these slides. Use them as inspiration for the visual style."
        )

    contents = [prompt]

    for ref_path in args.reference:
        validate_image_file(ref_path)
        img = resize_if_needed(Image.open(ref_path))
        contents.append(img)

    for ex_path in args.examples:
        validate_image_file(ex_path)
        img = resize_if_needed(Image.open(ex_path))
        contents.append(img)

    # Generate
    response = client.models.generate_content(
        model="gemini-3-pro-image-preview",
        contents=contents,
        config=types.GenerateContentConfig(
            response_modalities=["TEXT", "IMAGE"],
            image_config=types.ImageConfig(
                aspect_ratio=args.aspect_ratio,
            ),
        ),
    )

    # Process response
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    image_saved = False
    text_response = ""

    for part in response.candidates[0].content.parts:
        if hasattr(part, "inline_data") and part.inline_data is not None:
            img = part.as_image()
            img.save(str(output_path))
            image_saved = True
            print(f"Slide saved to: {output_path}")
        elif hasattr(part, "text") and part.text is not None:
            text_response += part.text

    if text_response:
        print(f"\nModel notes: {text_response}")

    if not image_saved:
        print("Error: No image was generated in the response.", file=sys.stderr)
        if text_response:
            print(f"Response text: {text_response}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
brand-image generator — on-brand imagery via Gemini Nano Banana Pro or
OpenAI GPT Image (gpt-image-2).

Importable:
    from generate_image import generate_image
    generate_image("a moody atmospheric background", "out.png", aspect_ratio="16:9")
    generate_image("...", "out.png", provider="openai")

CLI:
    python3 generate_image.py --prompt "..." --output out.png --aspect 16:9
    python3 generate_image.py --prompt "..." --output out.png --provider openai
    python3 generate_image.py --prompt "..." --output out.png --reference ref1.png

Environment:
    GEMINI_API_KEY  — for provider "gemini" (default)
    OPENAI_API_KEY  — for provider "openai" (gpt-image-2)
    (either may live in a .env walking up from this script)
"""

import argparse
import base64
import io
import os
import sys
import time
from pathlib import Path

try:
    from PIL import Image
    _HAS_PIL = True
except ImportError:
    _HAS_PIL = False

try:
    from google import genai
    from google.genai import types
    _HAS_GEMINI = True
except ImportError:
    _HAS_GEMINI = False

try:
    from openai import OpenAI
    _HAS_OPENAI = True
except ImportError:
    _HAS_OPENAI = False

# Appended to every prompt — generated text is garbled across all providers.
NO_TEXT_SUFFIX = (
    " IMPORTANT: Do not render any text, words, letters, numbers, symbols, "
    "logos, watermarks, or signatures anywhere in the image. The image must be "
    "purely visual."
)

VALID_ASPECTS = {"16:9", "9:16", "1:1", "4:3", "3:4", "21:9", "3:2", "2:3"}

# gpt-image-2 takes pixel sizes — edges multiple of 16, max edge 3840,
# long:short ratio <= 3:1, total pixels 655,360 - 8,294,400.
_OPENAI_SIZES = {
    "1:1":  "1024x1024",
    "3:2":  "1536x1024",
    "2:3":  "1024x1536",
    "4:3":  "1536x1152",
    "3:4":  "1152x1536",
    "16:9": "2048x1152",
    "9:16": "1152x2048",
    "21:9": "2048x880",
}


def load_dotenv():
    """Load .env by walking up from this script, then the cwd."""
    here = Path(__file__).resolve()
    for parent in [*here.parents, Path.cwd()]:
        env_path = parent / ".env"
        if env_path.exists():
            for line in env_path.read_text().splitlines():
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, _, val = line.partition("=")
                    val = val.strip().strip('"').strip("'")
                    if val:
                        os.environ.setdefault(key.strip(), val)
            return


def _resize_for_upload(img, max_edge=2048):
    w, h = img.size
    if max(w, h) > max_edge:
        ratio = max_edge / max(w, h)
        img = img.resize((int(w * ratio), int(h * ratio)), Image.LANCZOS)
    return img


def _save_image_bytes(data, output_path):
    """Route raw image bytes through PIL so the saved format matches the
    extension (the providers return JPEG/PNG bytes; we want a real PNG)."""
    img = Image.open(io.BytesIO(data))
    if img.mode not in ("RGB", "RGBA"):
        img = img.convert("RGB")
    img.save(str(output_path))


# ---- provider: Gemini Nano Banana Pro --------------------------------------
def _generate_gemini(prompt, output_path, aspect_ratio, references):
    if not _HAS_GEMINI:
        raise RuntimeError("google-genai not installed. pip install -r requirements.txt")
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError("GEMINI_API_KEY not set (checked environment and .env files).")

    contents = [prompt]
    for ref in (references or []):
        ref_path = Path(ref)
        if not ref_path.exists():
            print(f"  warning: reference image not found, skipping: {ref}", file=sys.stderr)
            continue
        contents.append(_resize_for_upload(Image.open(ref_path)))

    client = genai.Client(api_key=api_key)

    # Up to 3 attempts — content / recitation filter blocks are often transient.
    last_err = "unknown"
    for attempt in range(1, 4):
        response = client.models.generate_content(
            model="gemini-3-pro-image-preview",
            contents=contents,
            config=types.GenerateContentConfig(
                response_modalities=["TEXT", "IMAGE"],
                image_config=types.ImageConfig(aspect_ratio=aspect_ratio),
            ),
        )
        candidates = getattr(response, "candidates", None) or []
        content = getattr(candidates[0], "content", None) if candidates else None
        parts = getattr(content, "parts", None) if content else None
        for part in (parts or []):
            inline = getattr(part, "inline_data", None)
            if inline is not None and getattr(inline, "data", None):
                _save_image_bytes(inline.data, output_path)
                return output_path
        finish = getattr(candidates[0], "finish_reason", "no candidates") if candidates else "no candidates"
        text = "".join(p.text for p in (parts or []) if getattr(p, "text", None))
        last_err = f"finish_reason={finish}; {text[:200]}".strip()
        if attempt < 3:
            print(f"  image attempt {attempt} returned no image ({last_err}) — retrying...",
                  file=sys.stderr)
            time.sleep(2)

    raise RuntimeError(
        f"No image returned after 3 attempts ({last_err}). The prompt may be "
        f"triggering a content or recitation filter — reword it to be more specific.")


# ---- provider: OpenAI GPT Image (gpt-image-2) ------------------------------
def _generate_openai(prompt, output_path, aspect_ratio, references):
    if not _HAS_OPENAI:
        raise RuntimeError("openai not installed. pip install openai")
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY not set (checked environment and .env files).")

    client = OpenAI(api_key=api_key)
    size = _OPENAI_SIZES.get(aspect_ratio, "1024x1024")
    refs = [Path(r) for r in (references or []) if Path(r).exists()]

    try:
        if refs:
            # Reference images -> the edits endpoint composes from them
            files = [open(r, "rb") for r in refs]
            try:
                result = client.images.edit(
                    model="gpt-image-2", image=files, prompt=prompt,
                    size=size, quality="high",
                )
            finally:
                for f in files:
                    f.close()
        else:
            result = client.images.generate(
                model="gpt-image-2", prompt=prompt, size=size, quality="high",
            )
    except Exception as e:  # noqa: BLE001
        raise RuntimeError(
            f"OpenAI gpt-image-2 request failed: {e}. If this is an access "
            f"error, the org may need API verification for GPT Image models.")

    b64 = result.data[0].b64_json
    if not b64:
        raise RuntimeError("OpenAI returned no image data.")
    _save_image_bytes(base64.b64decode(b64), output_path)
    return output_path


def generate_image(prompt, output_path, provider="gemini", aspect_ratio="16:9",
                   references=None, append_no_text=True):
    """Generate one image and save it to output_path. Returns the Path on success.

    provider:     "gemini" (Nano Banana Pro) or "openai" (gpt-image-2)
    aspect_ratio: one of VALID_ASPECTS
    references:   optional list of paths to style/likeness/composition reference images
    """
    if not _HAS_PIL:
        raise RuntimeError("Pillow not installed. pip install -r requirements.txt")
    if aspect_ratio not in VALID_ASPECTS:
        raise ValueError(f"aspect_ratio '{aspect_ratio}' invalid. "
                         f"Use one of: {', '.join(sorted(VALID_ASPECTS))}")

    load_dotenv()
    full_prompt = prompt + (NO_TEXT_SUFFIX if append_no_text else "")
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    if provider == "gemini":
        return _generate_gemini(full_prompt, output_path, aspect_ratio, references)
    if provider == "openai":
        return _generate_openai(full_prompt, output_path, aspect_ratio, references)
    raise ValueError(f"Unknown provider '{provider}'. Use 'gemini' or 'openai'.")


def main():
    parser = argparse.ArgumentParser(description="Generate an on-brand image (Gemini or OpenAI)")
    parser.add_argument("--prompt", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--aspect", default="16:9",
                        help="16:9 / 9:16 / 1:1 / 4:3 / 3:4 / 21:9 / 3:2 / 2:3")
    parser.add_argument("--provider", default="gemini", choices=["gemini", "openai"],
                        help="gemini = Nano Banana Pro (default); openai = gpt-image-2")
    parser.add_argument("--reference", nargs="*", default=[],
                        help="Reference image paths for style/likeness/composition")
    parser.add_argument("--variations", type=int, default=1,
                        help="Generate N variations (suffixed -1, -2, ...)")
    args = parser.parse_args()

    if args.variations == 1:
        path = generate_image(args.prompt, args.output, args.provider,
                              args.aspect, args.reference)
        print(f"Saved: {path}")
    else:
        out = Path(args.output)
        stem = out.stem
        suffix = out.suffix or ".png"
        for i in range(1, args.variations + 1):
            variant = out.with_name(f"{stem}-{i}{suffix}")
            try:
                generate_image(args.prompt, variant, args.provider,
                               args.aspect, args.reference)
                print(f"Saved: {variant}")
            except Exception as e:  # noqa: BLE001
                print(f"Variation {i} failed: {e}", file=sys.stderr)


if __name__ == "__main__":
    main()

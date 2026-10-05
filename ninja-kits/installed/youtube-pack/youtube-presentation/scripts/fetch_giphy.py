#!/usr/bin/env python3
"""
Search Giphy and download a GIF to a local path.

Usage:
    python3 fetch_giphy.py \
        --query "mind blown" \
        --output "presentations/my-talk-assets/gif-0-mind-blown.gif"

Environment:
    GIPHY_API_KEY must be set.
"""

import argparse
import json
import os
import sys
import urllib.request
import urllib.parse
from pathlib import Path


def parse_args():
    parser = argparse.ArgumentParser(description="Fetch a GIF from Giphy")
    parser.add_argument("--query", required=True, help="Search term for Giphy")
    parser.add_argument("--output", required=True, help="Local path to save the GIF")
    parser.add_argument("--rating", default="g", help="Content rating (g, pg, pg-13, r)")
    parser.add_argument("--offset", type=int, default=0, help="Result offset for variety")
    return parser.parse_args()


def main():
    args = parse_args()

    api_key = os.environ.get("GIPHY_API_KEY")
    if not api_key:
        print("Error: GIPHY_API_KEY environment variable not set", file=sys.stderr)
        print("Get a free key at https://developers.giphy.com/", file=sys.stderr)
        sys.exit(1)

    params = urllib.parse.urlencode({
        "api_key": api_key,
        "q": args.query,
        "limit": 1,
        "offset": args.offset,
        "rating": args.rating,
    })
    url = f"https://api.giphy.com/v1/gifs/search?{params}"

    try:
        req = urllib.request.Request(url, headers={"User-Agent": "PresentationSkill/1.0"})
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode())
    except Exception as e:
        print(f"Error searching Giphy: {e}", file=sys.stderr)
        sys.exit(1)

    if not data.get("data"):
        print(f"No GIFs found for query: {args.query}", file=sys.stderr)
        sys.exit(1)

    gif_data = data["data"][0]
    # Use downsized for reasonable file size, fall back to original
    gif_url = (
        gif_data.get("images", {}).get("downsized", {}).get("url")
        or gif_data.get("images", {}).get("original", {}).get("url")
    )

    if not gif_url:
        print("Error: Could not extract GIF URL from response", file=sys.stderr)
        sys.exit(1)

    # Download the GIF
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    try:
        req = urllib.request.Request(gif_url, headers={"User-Agent": "PresentationSkill/1.0"})
        with urllib.request.urlopen(req, timeout=30) as resp:
            output_path.write_bytes(resp.read())
    except Exception as e:
        print(f"Error downloading GIF: {e}", file=sys.stderr)
        sys.exit(1)

    print(f"GIF saved to: {output_path}")
    print(f"Title: {gif_data.get('title', 'Unknown')}")


if __name__ == "__main__":
    main()

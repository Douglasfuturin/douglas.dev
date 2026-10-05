#!/usr/bin/env python3
"""
reddit_research.py, research a webinar's TOPIC and AUDIENCE on Reddit.

Run this before authoring a deck, for both research passes:
  - Topic research  , what the webinar teaches: how the subject really works,
                       current state, what people are actually saying about it.
                       Feeds assets/topic-research.md.
  - Audience research - the viewers' objections, pains, and language.
                       Feeds assets/audience-research.md.

Uses the ScrapeCreators Reddit API (search + post comments). Pair it with
WebSearch / WebFetch for primary-source verification of any statistic or claim.

Usage:
  python3 reddit_research.py --queries "Claude Code business" "AI agents real use"
  python3 reddit_research.py --queries "..." --comments      # also pull top comments
  python3 reddit_research.py --queries "..." --top 8 --comments

Environment:
  SCRAPECREATORS_API_KEY must be set (or present in a .env walking up from here).
"""

import argparse
import json
import os
import sys
import urllib.parse
import urllib.request
from pathlib import Path

API = "https://api.scrapecreators.com/v1/reddit"


def load_dotenv():
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


def _get(path, params, api_key):
    qs = urllib.parse.urlencode(params)
    req = urllib.request.Request(f"{API}/{path}?{qs}", headers={"x-api-key": api_key})
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read().decode())
    except Exception as e:  # noqa: BLE001
        print(f"  request failed ({path}): {e}", file=sys.stderr)
        return {}


def search(query, api_key, top=8):
    """Search Reddit posts for a query, sorted by relevance."""
    data = _get("search", {"query": query, "sort": "relevance", "trim": "true"}, api_key)
    return data.get("posts", [])[:top]


def comments(url, api_key, top=8):
    """Pull top comments from a Reddit post URL."""
    data = _get("post/comments", {"url": url, "trim": "true"}, api_key)
    rows = data.get("comments", [])
    rows.sort(key=lambda c: c.get("ups", 0) if isinstance(c.get("ups", 0), int) else 0,
              reverse=True)
    return rows[:top]


def main():
    parser = argparse.ArgumentParser(description="Research a webinar topic or audience on Reddit")
    parser.add_argument("--queries", nargs="+", required=True,
                        help="Search queries, the topic's subject matter, or the audience's objections/pains")
    parser.add_argument("--top", type=int, default=8, help="Posts per query (default 8)")
    parser.add_argument("--comments", action="store_true",
                        help="Also pull top comments from the top post of each query")
    parser.add_argument("--comment-posts", type=int, default=2,
                        help="How many posts per query to pull comments from (default 2)")
    args = parser.parse_args()

    load_dotenv()
    api_key = os.environ.get("SCRAPECREATORS_API_KEY")
    if not api_key:
        print("Error: SCRAPECREATORS_API_KEY not set (env or .env).", file=sys.stderr)
        sys.exit(1)

    for query in args.queries:
        print(f"\n{'='*70}\nQUERY: {query}\n{'='*70}")
        posts = search(query, api_key, args.top)
        if not posts:
            print("  (no posts)")
            continue
        for p in posts:
            print(f"  r/{p.get('subreddit','')} "
                  f"[{p.get('score',0)}up {p.get('num_comments',0)}c] "
                  f"{p.get('title','')}")
            print(f"     {p.get('url','')}")
        if args.comments:
            for p in posts[:args.comment_posts]:
                url = p.get("url", "")
                if not url:
                    continue
                print(f"\n  --- top comments: {p.get('title','')[:60]} ---")
                for c in comments(url, api_key):
                    body = " ".join((c.get("body", "") or "").split())[:300]
                    if body and body not in ("[removed]", "[deleted]"):
                        print(f"    • {body}")

    print("\nDone. Synthesize findings into assets/topic-research.md or "
          "assets/audience-research.md.", file=sys.stderr)


if __name__ == "__main__":
    main()

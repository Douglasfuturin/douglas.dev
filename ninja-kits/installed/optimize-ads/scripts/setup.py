#!/usr/bin/env python3
"""Interactive setup wizard for the optimize-ads skill.

Walks the user through:
  1. Creating a Meta Business Manager System User token
  2. Finding their ad account ID
  3. Writing META_ACCESS_TOKEN and META_AD_ACCOUNT_ID to .env
  4. Copying config.example.json -> config/config.json
  5. Verifying the token works with a real API call

Usage:
    python3 .claude/skills/optimize-ads/scripts/setup.py
    python3 .claude/skills/optimize-ads/scripts/setup.py --verify-only
"""
from __future__ import annotations

import argparse
import json
import os
import shutil
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path


SKILL_DIR = Path(__file__).resolve().parent.parent
PROJECT_ROOT = SKILL_DIR.parent.parent.parent  # .claude/skills/optimize-ads -> project root
ENV_PATH = PROJECT_ROOT / ".env"
CONFIG_DIR = SKILL_DIR / "config"
CONFIG_PATH = CONFIG_DIR / "config.json"
CONFIG_EXAMPLE = CONFIG_DIR / "config.example.json"
DEFAULT_API_VERSION = "v21.0"


SETUP_INSTRUCTIONS = """
================================================================
  Meta Marketing API setup — System User token
================================================================

You'll need:
  • Admin access to a Meta Business Manager
  • The ad account you want to optimize already assigned to that BM

Steps (do these in your browser):

  1. Go to https://business.facebook.com/settings/system-users
  2. Click "Add" → name it something like "ad-optimizer-bot" → Admin role
  3. With your new System User selected, click "Add Assets"
       → Ad Accounts → pick your account → enable "Manage campaigns"
  4. Click "Generate New Token"
       → App: pick (or create) a Business app
       → Token expiration: NEVER (this is the whole point of System Users)
       → Scopes: check  ads_read, ads_management, business_management
       → Generate, then COPY the token (you can't see it again — if you
         lose it, just generate a new one)

  5. Find your Ad Account ID:
       Open https://adsmanager.facebook.com → top-left account selector
       → the number shown like "1234567890" is your ID
       → prefix it with "act_" when entering below
         (e.g. act_1234567890)

================================================================
"""


def prompt(question: str, default: str | None = None, secret: bool = False) -> str:
    suffix = f" [{default}]" if default else ""
    if secret:
        try:
            import getpass

            value = getpass.getpass(f"{question}{suffix}: ")
        except (ImportError, EOFError):
            value = input(f"{question}{suffix}: ")
    else:
        value = input(f"{question}{suffix}: ")
    value = value.strip()
    if not value and default is not None:
        return default
    return value


def read_env(path: Path) -> dict[str, str]:
    if not path.exists():
        return {}
    out: dict[str, str] = {}
    for raw in path.read_text().splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, _, v = line.partition("=")
        out[k.strip()] = v.strip()
    return out


def write_env(path: Path, updates: dict[str, str]) -> None:
    """Update .env in place, preserving existing keys and comments."""
    if path.exists():
        lines = path.read_text().splitlines()
    else:
        lines = []
    seen: set[str] = set()
    for i, raw in enumerate(lines):
        if "=" in raw and not raw.lstrip().startswith("#"):
            k = raw.split("=", 1)[0].strip()
            if k in updates:
                lines[i] = f"{k}={updates[k]}"
                seen.add(k)
    for k, v in updates.items():
        if k not in seen:
            lines.append(f"{k}={v}")
    path.write_text("\n".join(lines) + "\n")


def http_get_json(url: str) -> dict:
    req = urllib.request.Request(url, headers={"User-Agent": "optimize-ads-setup/1.0"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode("utf-8"))


def verify_token(token: str, account_id: str, api_version: str) -> tuple[bool, str]:
    """Returns (ok, message). On success, message includes the account name + currency."""
    base = f"https://graph.facebook.com/{api_version}"
    fields = "name,currency,account_status,timezone_name"
    url = f"{base}/{account_id}?{urllib.parse.urlencode({'fields': fields, 'access_token': token})}"
    try:
        data = http_get_json(url)
    except urllib.error.HTTPError as e:
        try:
            body = json.loads(e.read().decode("utf-8"))
            err = body.get("error", {})
            return False, f"HTTP {e.code}: {err.get('message', e.reason)} (code {err.get('code')})"
        except Exception:
            return False, f"HTTP {e.code}: {e.reason}"
    except Exception as e:  # noqa: BLE001 — surface the message
        return False, f"{type(e).__name__}: {e}"
    if "id" in data and "name" in data:
        return True, (
            f"Account: {data['name']} ({data.get('currency', '?')}), "
            f"status={data.get('account_status')}, tz={data.get('timezone_name')}"
        )
    return False, f"Unexpected response: {json.dumps(data)[:200]}"


def main() -> int:
    parser = argparse.ArgumentParser(description="Set up Meta Ads API credentials for optimize-ads.")
    parser.add_argument(
        "--verify-only",
        action="store_true",
        help="Skip prompts; just verify the existing .env credentials work.",
    )
    args = parser.parse_args()

    existing = read_env(ENV_PATH)

    if args.verify_only:
        token = existing.get("META_ACCESS_TOKEN", "")
        account = existing.get("META_AD_ACCOUNT_ID", "")
        api_version = existing.get("META_API_VERSION", DEFAULT_API_VERSION)
        if not token or not account:
            print("ERROR: META_ACCESS_TOKEN or META_AD_ACCOUNT_ID missing from .env", file=sys.stderr)
            return 2
        ok, msg = verify_token(token, account, api_version)
        print(("OK — " if ok else "FAIL — ") + msg)
        return 0 if ok else 1

    print(SETUP_INSTRUCTIONS)
    input("Press Enter when you have your System User token and account ID ready... ")

    token = prompt("Paste your META_ACCESS_TOKEN", secret=True)
    if not token:
        print("No token entered. Aborting.", file=sys.stderr)
        return 2
    account = prompt(
        "Enter META_AD_ACCOUNT_ID (with act_ prefix)",
        default=existing.get("META_AD_ACCOUNT_ID"),
    )
    if not account.startswith("act_"):
        print(f"Note: prefixing 'act_' → act_{account}")
        account = f"act_{account}"
    api_version = prompt("Graph API version", default=existing.get("META_API_VERSION", DEFAULT_API_VERSION))

    print("\nVerifying token against the Meta Graph API...")
    ok, msg = verify_token(token, account, api_version)
    if not ok:
        print(f"FAIL — {msg}", file=sys.stderr)
        print(
            "\nDouble-check that the token has scopes ads_read, ads_management, business_management\n"
            "and that the System User has been granted access to this ad account.",
            file=sys.stderr,
        )
        return 1
    print(f"OK — {msg}")

    write_env(
        ENV_PATH,
        {
            "META_ACCESS_TOKEN": token,
            "META_AD_ACCOUNT_ID": account,
            "META_API_VERSION": api_version,
        },
    )
    print(f"\nWrote credentials to {ENV_PATH}")

    if not CONFIG_PATH.exists():
        shutil.copy(CONFIG_EXAMPLE, CONFIG_PATH)
        # Patch the ad_account_id into the new config
        cfg = json.loads(CONFIG_PATH.read_text())
        cfg["ad_account_id"] = account
        cfg["api_version"] = api_version
        CONFIG_PATH.write_text(json.dumps(cfg, indent=2) + "\n")
        print(f"Created {CONFIG_PATH} from template (you can edit this).")
    else:
        print(f"Existing {CONFIG_PATH} left as-is.")

    print("\nSetup complete. You can now run the skill normally.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

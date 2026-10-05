# Meta Marketing API Guide

Quick reference for the Graph API calls used by this skill. The skill's scripts wrap these — you usually won't call them directly — but read this when something breaks or when you want to extend the scripts.

## Auth

The skill uses a **System User access token** from Meta Business Manager. System User tokens don't expire (unlike user tokens, which expire in ~60 days), and they survive password changes on the user account. This is the right token type for unattended scripts.

Required token scopes:
- `ads_read` — required to pull insights and campaign/adset/ad metadata
- `ads_management` — required for any write action (the skill doesn't use this today, but if you ever flip on auto-apply mode, you'll need it)
- `business_management` — required for some account-level fields

Env vars the scripts expect:

```
META_ACCESS_TOKEN=EAAG…
META_AD_ACCOUNT_ID=act_1234567890     # the act_ prefix is required
META_API_VERSION=v21.0                 # optional; defaults to v21.0
```

The setup script (`scripts/setup.py`) walks through getting these from Business Manager. The flow:
1. Business Manager → Business Settings → System Users → Add → create a System User with admin role
2. Add Assets → Ad Accounts → assign your ad account with "Manage campaigns" permission
3. Click Generate New Token → select the System User → check the three scopes above → copy
4. Find your ad account ID: Ads Manager → top-left account selector → the number after "act\_"

## Base URL

```
https://graph.facebook.com/{API_VERSION}/
```

Default API version: `v21.0`. Bump it in `META_API_VERSION` if Meta deprecates fields (they give ~2 years' notice; the API versioning page lists current versions: https://developers.facebook.com/docs/graph-api/changelog).

## Endpoints used

### Account-level insights

```
GET /{ad_account_id}/insights
  ?level=account
  &time_range={"since":"YYYY-MM-DD","until":"YYYY-MM-DD"}
  &fields=spend,impressions,reach,frequency,clicks,ctr,cpc,cpm,actions,action_values,cost_per_action_type,purchase_roas
```

### Campaign / adset / ad insights

Same endpoint, change `level`:

```
GET /{ad_account_id}/insights
  ?level=campaign      # or adset, or ad
  &time_range={"since":"…","until":"…"}
  &fields=campaign_id,campaign_name,objective,spend,impressions,reach,frequency,clicks,ctr,cpc,cpm,actions,action_values,cost_per_action_type,purchase_roas
  &limit=500
```

For adset level add `adset_id,adset_name`; for ad level add `ad_id,ad_name,adset_id,campaign_id`.

### Listing campaigns/adsets/ads (for status, names, objective)

```
GET /{ad_account_id}/campaigns?fields=id,name,objective,status,effective_status,daily_budget,lifetime_budget,start_time,stop_time&limit=500
GET /{ad_account_id}/adsets?fields=id,name,campaign_id,status,effective_status,daily_budget,targeting,optimization_goal&limit=500
GET /{ad_account_id}/ads?fields=id,name,adset_id,campaign_id,status,effective_status,creative&limit=500
```

`status` is what you set; `effective_status` is what's actually live (accounts for parent pauses, billing issues, etc.). Use `effective_status` to decide if an ad is actually running.

## The `actions` and `action_values` shape

These come back as arrays of objects keyed by `action_type`. Common action types:

- `purchase` — actual purchases
- `omni_purchase` — purchases across all channels (Meta's preferred metric for Advantage+ Shopping)
- `offsite_conversion.fb_pixel_purchase` — pixel-tracked purchases
- `lead` — lead form submissions
- `complete_registration` — registration completions
- `add_to_cart`
- `initiate_checkout`

Example:

```json
"actions": [
  {"action_type": "purchase", "value": "42"},
  {"action_type": "add_to_cart", "value": "180"}
]
```

The scripts normalize these — you'll see `purchases`, `purchase_value`, `cpa`, `roas` in the snapshot JSON, not the raw API shape.

## Rate limits

Meta uses a sliding window. The pull script handles 4xx rate-limit errors by sleeping and retrying. Common headers to watch:

- `x-business-use-case-usage` — JSON object with call_count, total_cputime, total_time, type per BUC
- `x-app-usage` — same, app-wide

If you hit the limit hard, the script will surface the error to you. Typical fix is to narrow the date range or reduce the number of `level=ad` calls (ad-level data is the most expensive).

## Common errors and fixes

- **`(#190) Error validating access token`** → token expired or revoked. Run setup again.
- **`(#100) Tried accessing nonexisting field`** → API version drift. Bump `META_API_VERSION` and check the changelog for renamed fields.
- **`(#10) Application does not have permission for this action`** → missing scope on the token. Regenerate with the three scopes listed above.
- **`(#17) User request limit reached`** → rate limit. Wait, then retry with a narrower window.
- **`(#80004) There have been too many calls`** → ad-account-level rate limit. Worth caching aggressively; the pull script writes the snapshot to a temp file so you don't re-pull within a session.
- **Empty insights response** → either the date range is in the future, the account hasn't spent, or there's a pixel/tracking issue. Cross-check in Ads Manager UI.

## What we don't do via API

- **Creating ads / creatives** — that lives in the `generate-ads` skill (creative side) and Ads Manager UI (publishing).
- **Pausing / enabling / budget changes** — recommend-only; the human applies in Ads Manager. (This is intentional. Flip the action mode in skill.md only after you trust the frameworks.)
- **Comments / messages / inbox** — out of scope.

## Useful Meta docs to bookmark

- Insights API: https://developers.facebook.com/docs/marketing-api/insights
- Field reference: https://developers.facebook.com/docs/marketing-api/reference/ad-account/insights
- System Users: https://developers.facebook.com/docs/marketing-api/system-users
- Versioning / changelog: https://developers.facebook.com/docs/graph-api/changelog

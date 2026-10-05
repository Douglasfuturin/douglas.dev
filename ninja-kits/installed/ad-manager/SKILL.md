---
name: ad-manager
description: Upload creatives and create campaigns, ad sets, and ads via the Meta Ads API with consistent naming and UTM parameters
---

# Ad Upload — Meta Ads API

Create campaigns, ad sets, and ads via the Meta Marketing API. Handles image uploads, creative creation, ad creation, and UTM parameter generation in a consistent format.

## Prerequisites

- `.env` file must contain `META_ACCESS_TOKEN`, `META_AD_ACCOUNT_ID`, `META_APP_ID`, `META_APP_SECRET`
- Read `creative-db.json` for existing IDs, image hashes, and campaign structure
- Read `naming-convention.md` for naming format
- Use the `utm-params` skill format for all URLs (call /utm-params if unsure)

## API Basics

```
API_BASE = https://graph.facebook.com/v22.0
AD_ACCOUNT = act_{META_AD_ACCOUNT_ID}
```

All API calls use the access token from `.env`. Use `curl` with `-F` flag for file uploads (images) and `--data-urlencode` for non-file POST requests.

## Process

### 1. Create Campaign

```bash
curl -s -X POST "{API_BASE}/{AD_ACCOUNT}/campaigns" \
  --data-urlencode "access_token={TOKEN}" \
  -d "name={campaign_name}" \
  -d "objective={objective}" \
  -d "status=PAUSED" \
  -d "special_ad_categories=[]" \
  -d "is_adset_budget_sharing_enabled=false"
```

**Campaign naming:** `[{Brand}] – {Product} – {Budget Type} – {Phase} – {Objective}`

| Objective | API Value |
|-----------|-----------|
| Purchase | `OUTCOME_SALES` |
| Leads | `OUTCOME_LEADS` |
| Traffic | `OUTCOME_TRAFFIC` |

**Always create campaigns as PAUSED.** Tyler will activate manually.

### 2. Create Ad Sets

```bash
curl -s -X POST "{API_BASE}/{AD_ACCOUNT}/adsets" \
  --data-urlencode "access_token={TOKEN}" \
  -d "campaign_id={campaign_id}" \
  --data-urlencode "name={adset_name}" \
  -d "daily_budget={budget_in_cents}" \
  -d "billing_event=IMPRESSIONS" \
  -d "optimization_goal=OFFSITE_CONVERSIONS" \
  -d "bid_strategy=LOWEST_COST_WITHOUT_CAP" \
  --data-urlencode "targeting={targeting_json}" \
  --data-urlencode "promoted_object={promoted_object_json}" \
  -d "status=PAUSED"
```

**Ad set naming:** `[{Brand}] – {Product} – {Targeting Type} – {Countries} – {Angle} – ${Budget}/day`

**Budget:** Always in cents (e.g., $30/day = `3000`)

**Countries — use what's actually in the targeting, not what you wish was there:**
- If targeting US, CA, GB, AU, NZ → name says `US/CA/UK/AU/NZ`
- If targeting full Tier 1 including EU → name says `US/CA/UK/AU/NZ/EU`
- Always verify targeting matches the name

**Standard targeting JSON (broad, Tier 1 core):**
```json
{
  "age_min": 18,
  "age_max": 65,
  "geo_locations": {
    "countries": ["US", "NZ", "CA", "GB", "AU"],
    "location_types": ["home", "recent"]
  },
  "excluded_custom_audiences": [{"id": "YOUR_EXISTING_CUSTOMERS_AUDIENCE_ID"}],
  "targeting_relaxation_types": {"lookalike": 0, "custom_audience": 0}
}
```

**Promoted object** — use the event that matches your conversion goal:
```json
// Purchase / paid product
{"pixel_id": "YOUR_PIXEL_ID", "custom_event_type": "PURCHASE"}

// Lead / free sign-up
{"pixel_id": "YOUR_PIXEL_ID", "custom_event_type": "COMPLETE_REGISTRATION"}

// Call booking / lead form
{"pixel_id": "YOUR_PIXEL_ID", "custom_event_type": "LEAD"}
```

### 3. Upload Images

```bash
curl -s -X POST "{API_BASE}/{AD_ACCOUNT}/adimages" \
  -F "access_token={TOKEN}" \
  -F "filename=@{filepath}"
```

**Important:** Image uploads require `-F` (multipart form) for both the token and the file. Response format:
```json
{"images": {"filename.png": {"hash": "abc123..."}}}
```

Extract the hash — you need it for creating ad creatives.

### 4. Create Ad Creative + Ad

**Step 1: Create the creative**
```bash
curl -s -X POST "{API_BASE}/{AD_ACCOUNT}/adcreatives" \
  -F "access_token={TOKEN}" \
  -F "name={ad_name}" \
  -F 'object_story_spec={"page_id":"{PAGE_ID}","link_data":{"image_hash":"{hash}","link":"{url_with_utms}","message":"{primary_text}","name":"{headline}","description":"{description}","call_to_action":{"type":"LEARN_MORE"}}}'
```

**Step 2: Create the ad**
```bash
curl -s -X POST "{API_BASE}/{AD_ACCOUNT}/ads" \
  -F "access_token={TOKEN}" \
  -F "adset_id={adset_id}" \
  -F "name={ad_name}" \
  -F 'creative={"creative_id":"{creative_id}"}' \
  -F "status=PAUSED"
```

**Ad naming:** `{Creative-Name} – {Copy Variant}`
- Copy variants: `Short`, `Med`, `Long`, `Multi` (if using asset_feed_spec with multiple texts)

### 5. Generate UTM URLs

**Every ad URL must include UTMs.** Use this format:

```
{base_url}?utm_source=meta&utm_medium=paid&utm_campaign={campaign_slug}&utm_content={angle_slug}&utm_term={creative_slug}
```

**Base URL:** Set `DESTINATION_URL` in `.env` — this is where every ad sends traffic.

**All UTM values are lowercase, hyphen-separated.** Never use underscores, spaces, or camelCase.

**Derive utm_campaign from the campaign name:**
- `[YY] – [Free Community] – ABO – Testing – Leads` → `free-community-testing-leads`
- `[XX] – [Your Product] – ABO – Testing – Purchase` → `your-product-launch`

**Derive utm_content from the ad set angle:** `native-organic`, `value-stack`, `meme-humor`, etc.

**Derive utm_term from the creative slug:** `sticky-note`, `drake`, `reverse-psych`, etc.

### 6. Update creative-db.json

After creating ads, update `creative-db.json` with:
- New campaign IDs (in `meta.campaigns`)
- New ad set objects (with id, name, angle, daily_budget)
- New creative entries (with slug, file, image_hash, angle, ad_set, description, ad_id, creative_id, status, ad_name)

## Key IDs (from creative-db.json)

| Resource | ID |
|----------|-----|
| Ad Account | `act_YOUR_AD_ACCOUNT_ID` |
| Pixel | `YOUR_PIXEL_ID` |
| Your Page | `YOUR_PAGE_ID` |
| Product Page | `YOUR_PRODUCT_PAGE_ID` |
| Exclusion Audience | `YOUR_EXISTING_CUSTOMERS_AUDIENCE_ID` |

**Always run ads from your personal brand page** — personal brand has reach, product pages typically do not.

## Rate Limits

The Meta API rate-limits per ad account. If you hit `error code 17` ("Too Many API Calls"), wait 5 minutes and retry. Batch operations when possible to minimize calls.

## Rules

- **Always create campaigns and ads as PAUSED** — you activate manually
- **Always include UTM parameters** on every ad URL
- **Always update creative-db.json** after creating ads
- **Never use Meta's AI text suggestions** — all copy is written manually
- **Ad set names must match actual targeting** — don't put "EU" in the name if EU countries aren't in the targeting
- **Verify image uploads succeeded** before creating creatives — check for the hash in the response

---
name: email-sequence
description: Use when the user wants to draft an email sequence — welcome, nurture, abandoned cart, launch, re-engagement, post-purchase, evergreen, or webinar. Generates the full sequence (subjects + bodies + send timing + CTA flow) in [VOICE OWNER]'s voice, voice-checked, and structured for [EMAIL PLATFORM] automation. Never auto-sends — always proposes for approval.
---

# Email Sequence — [CLIENT NAME]

Drafts full email sequences for [CLIENT NAME] — voice-checked, fact-checked, mapped to the [EMAIL PLATFORM] automation structure. Sending is always human-approved (per CLAUDE.md hard stop).

- **Email platform:** [EMAIL PLATFORM — default ActiveCampaign]
- **Connector script:** `scripts/[platform]/` (see `connectors.md`)
- **Voice:** [VOICE OWNER]
- **Approval required:** sending, audience selection, large list operations

## What lives in this skill folder

```
.claude/skills/email-sequence/
├── SKILL.md                          # this file — the process
├── frameworks/                       # one per sequence type
│   ├── welcome.md                    # arc, beats, psychology, length, common failures
│   ├── nurture.md
│   ├── abandoned-cart.md
│   ├── launch.md                     # PLF + Soap Opera Sequence variants
│   ├── re-engagement.md
│   ├── post-purchase.md
│   ├── evergreen.md
│   └── webinar.md
└── assets/
    ├── subject-swipes.md             # proven subject patterns per sequence type
    ├── deliverability.md             # hard rules / soft rules / pre-send checklist
    └── examples/                     # [CLIENT NAME]'s actual past winners (overrides frameworks)
        └── README.md
```

The frameworks are the floor. The examples folder (if populated) is the ceiling. Always read both.

---

## Supported sequence types

| Sequence | Default length | Triggers |
|----------|----------------|----------|
| `welcome` | 5 emails over 7 days | new subscriber |
| `nurture` | 6 emails over 14 days | post-welcome, no purchase |
| `abandoned-cart` | 3 emails over 72 hours | cart abandon event |
| `launch` | 7-10 emails over 5-7 days | product launch / cart open |
| `re-engagement` | 4 emails over 10 days | 60+ days inactive |
| `post-purchase` | 4 emails over 14 days | order completed |
| `evergreen` | 8-12 emails over 30 days | tripwire / low-ticket buyers |
| `webinar` | 5 pre + 3 post (8 total) over 14 days | webinar registration |

If the user asks for a sequence type not listed, propose the closest match and ask for confirmation before drafting.

---

## Process

### Step 1: Get inputs

Required:
- **Sequence type** (from the table above)
- **Goal** (one sentence — e.g., "drive demo bookings", "recover the cart", "warm subs to the $497 offer")
- **Offer** (the thing being sold / promised — name + price + key promise)

Optional (will pull from brain if not provided):
- **Audience** (defaults to primary persona from `brains/marketing/audience.md`)
- **Sender** (defaults to [VOICE OWNER])
- **Tone shift** (e.g., "more urgent" or "softer than usual")
- **Existing assets** (sales page URL, VSL, lead magnet, etc.)

### Step 2: Load the framework + assets for this sequence type

This step is non-negotiable. The framework files have the beat-by-beat arc, length guidance, and known failure modes for each sequence type. Do not draft from memory.

```
Read .claude/skills/email-sequence/frameworks/{sequence-type}.md
Read .claude/skills/email-sequence/assets/subject-swipes.md
Read .claude/skills/email-sequence/assets/deliverability.md
Read .claude/skills/email-sequence/assets/examples/{sequence-type}/*.md  (if exists — overrides framework defaults)
```

### Step 3: Pull context from brains

```
Read agents/marketing/voice-bible.md
Read brains/marketing/audience.md
Read brains/marketing/offers/{offer-slug}.md   (if exists)
Read brains/email/winners/{sequence-type}.md   (past top performers, if exists)
Read brains/email/banned-subjects.md           (subject lines that got flagged / unsubs)
```

**Precedence order when these conflict:**
1. `assets/examples/{sequence-type}/` — [CLIENT NAME]'s actual past winners (highest priority)
2. `brains/email/winners/{sequence-type}.md` — performance-tracked winners
3. `frameworks/{sequence-type}.md` — the framework default
4. The general process below

The examples file is the ground truth when present. The framework is the floor when no examples exist.

### Step 4: Plan the sequence arc

Use the framework file's default arc as the starting table. Override beats / lengths / send times from `assets/examples/` if those exist for this client. Show the arc to the user before generating bodies:

```
| # | Day | Time | Subject angle | Body purpose | CTA |
|---|-----|------|--------------|--------------|-----|
| 1 | 0 | within 5 min | welcome + identity | establish voice + first value | soft (read this) |
| 2 | 1 | 9am | story | bond + relate to pain | soft (reply) |
| 3 | 3 | 9am | mechanism | introduce the unique angle | medium (learn more) |
| ... |
```

Pause here. Confirm the arc with the user before drafting full bodies. Drafting then editing 7 full emails wastes time if the arc is wrong.

### Step 5: Draft each email

For each email in the approved arc:

1. **Subject line:** generate 3 options. Pull patterns from `assets/subject-swipes.md` for this sequence type, then voice-check each. Each ≤ 7 words. No clickbait. No banned subjects (from brain).
2. **Preview text:** 30-60 characters that complement (not repeat) the subject — same rule as thumbnails.
3. **Body:** in [VOICE OWNER]'s voice. Length appropriate per the framework file (welcome email 1 = short, evergreen case-study = longer, last-call = short again).
4. **CTA:** one clear ask. Match the body purpose. Soft CTA = reply / read / watch. Medium = click to learn. Hard = buy / book.
5. **Send timing:** day, time, conditions (e.g., "only if not clicked email 2") — per the framework file.
6. **Personalization tokens:** flag any `{first_name}`, `{offer_name}`, etc., that the [EMAIL PLATFORM] should populate.

Reference the framework file's "Common failure modes" section as you draft — do not ship an email that matches a known failure pattern.

### Step 6: Voice-check the whole sequence

Run `/voice-check` on every body. Drop anything that fails. Either rewrite in-line or mark for the user to review.

### Step 7: Fact-check claim-bearing lines

For any line that makes a factual claim (stats, results, social proof, dates, pricing), run `/fact-check` against the brain. Cite sources in a footer comment on each email.

### Step 8: Deliverability check

Run every email and subject through `assets/deliverability.md` pre-send checklist. Hard rules block — soft rules surface as warnings to the user. Do not push to [EMAIL PLATFORM] until hard rules pass.

### Step 9: Output the full sequence

Deliver as a single Markdown file under `agents/marketing/campaigns/{YYYY-MM-DD}-{sequence-type}-{slug}.md`:

```markdown
# {Sequence type} — {slug}
Generated: {date}
Sender: [VOICE OWNER]
Goal: {goal}
Offer: {offer name} ({price})
Voice check: PASS / PASS WITH NOTES / FAIL (per email)
Fact check: PASS / NOTES (per email)
Status: DRAFT — awaiting human approval

## Arc
{the table from Step 3}

---

## Email 1
**Send:** Day 0, within 5 min of trigger
**Subject options:**
1. {…}
2. {…}
3. {…}
**Preview text:** {…}
**Personalization:** {tokens used}

**Body:**

{full body}

**CTA:** {…}
**Voice check:** PASS (Vocabulary 9 / Rhythm 8 / Tone 9 / Signature 8 / Anti-pattern 10)
**Fact check:** N/A (no factual claims)

---

## Email 2
…
```

### Step 10: Propose for approval

Print a one-screen summary to the user with:
- Sequence path
- Number of emails
- Subject lines for all emails (1 option per — the recommended pick)
- Send timing summary
- Voice check verdict per email
- Deliverability warnings (if any soft rules tripped)
- **Explicit ask: "Approve to push to [EMAIL PLATFORM] as a draft automation?"**

Do not push to [EMAIL PLATFORM] without explicit "yes" from the user. Even then, push as a **draft** — never auto-activate the automation.

### Step 11: (After approval) Push to [EMAIL PLATFORM]

```bash
python3 scripts/[platform]/create_automation.py \
  --type {sequence-type} \
  --source agents/marketing/campaigns/{generated-file}.md \
  --status draft
```

The connector script reads the markdown file, parses each email block, and creates the automation as a DRAFT in [EMAIL PLATFORM]. The user activates it manually in the [EMAIL PLATFORM] UI after a final review.

---

## Hard rules

- **Read the framework file first.** Don't draft from memory. The `frameworks/{sequence-type}.md` file has the arc, lengths, and known failure modes that took years to encode.
- **Voice check every email.** Not just the first one. Sequences drift — the email-7 voice often doesn't match email-1 voice unless you check every step.
- **Fact check every claim.** Especially in launch sequences where the pressure to oversell is highest.
- **Run deliverability check before push.** Hard rules in `assets/deliverability.md` block push — soft rules surface as warnings.
- **Never auto-send.** This skill drafts and proposes. Sending is a human action (per CLAUDE.md hard stop).
- **Never overwrite an existing automation.** Always create new drafts. If iterating, version the file (`-v2`, `-v3`).
- **Stop at arc approval.** If the user wants a different arc, redo the arc — don't push forward to bodies.
- **CTA discipline.** One ask per email. Stacked CTAs ("reply OR click OR book OR buy") split attention and tank conversion.

---

## Anti-patterns (don't do these)

- Generating all 7 bodies before showing the arc — wastes a generation cycle if the arc is wrong
- Repeating the subject in the preview text — they're two surfaces, complement them
- Adding fake urgency that doesn't match a real deadline ("LAST CHANCE!" on day 2 of 7)
- Copy-pasting structure across sequences — each sequence type has its own arc rhythm
- Auto-pushing to [EMAIL PLATFORM] without explicit user approval
- Activating an automation instead of saving as draft

---

## Customization checklist (Friday Labs onboarding)

- [ ] Replace `[CLIENT NAME]`, `[VOICE OWNER]`, `[EMAIL PLATFORM]` placeholders throughout SKILL.md and the framework files
- [ ] Confirm [EMAIL PLATFORM] connector script exists at `scripts/{platform}/` with `create_automation.py`
- [ ] Confirm `agents/marketing/voice-bible.md` is populated
- [ ] Confirm `brains/marketing/audience.md` and `brains/marketing/offers/` have current data
- [ ] Drop 2-3 of [CLIENT NAME]'s past best-performing sequences into `assets/examples/{sequence-type}/` per type they actually run
- [ ] Seed `brains/email/winners/` with sequence performance data over time
- [ ] Verify approval flow: run a test sequence end-to-end, confirm it lands in [EMAIL PLATFORM] as DRAFT (not active)
- [ ] Confirm `brains/email/banned-subjects.md` exists (even if empty)
- [ ] Confirm deliverability prerequisites: domain SPF/DKIM/DMARC set up, sender warm, physical address in footer
- [ ] Trim `frameworks/` to only the sequence types [CLIENT NAME] actually uses (optional — extras are inert but reduce noise)

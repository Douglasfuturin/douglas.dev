# Audience Research, [CLIENT NAME]

> What the target audience actually thinks, fears, and says, in their own words. Researched before authoring the deck so the webinar handles real objections, not invented ones. Refresh with `scripts/research_audience.py` whenever the audience or offer changes.

**Current research subject:** business owners considering done-for-you AI / AI agents / AI agencies (the Friday Labs AIOS buyer).
**Method:** ScrapeCreators Reddit API, search + top comments across r/AI_Agents, r/Entrepreneur, r/agency, r/AiForSmallBusiness, r/ClaudeAI, r/aiToolForBusiness, r/n8n and others.
**Date:** 2026-05.

---

## The objection landscape (real, not invented)

These are the objections that surfaced repeatedly. The deck must defuse each one, through genuine teaching, not by arguing.

### 1. "AI agents are hype"
> "AI agents are hype. They're being promoted by big tech because they're profitable to the AI companies, they burn tokens like California wildfire."
> "90% of the time it's just if/then logic with an LLM call bolted on."

The skeptic believes "agent" is a marketing word for a glorified script. **Deck response:** don't lead with the word "agent" as magic. Teach *why* multiple focused agents genuinely outperform one, the context/role argument (composite Secret 1). Earn the term.

### 2. "AI agency gurus are grifters"
> "Grifters have moved from crypto to AI. Just like crypto they usually have no idea how the underlying tech actually works."
> "If they know how to get rich, why would they waste time selling lessons?"
> "Funny to see people still doing the price ending in 7 thing."

This is the most dangerous objection, the buyer pattern-matches AI-services sellers to course scammers. **Deck responses:**
- **Show real expertise, not claims.** "Real engineers will gladly show you whatever you want for free." Teach generously and specifically, that is the anti-grifter signal.
- **Avoid prices ending in 7.** `$X,XX7` (e.g., $2,997, $1,497) is a recognized course-scam tell to this audience. Use clean round numbers ($8,000, not $7,997).
- **Don't oversell or hype.** Calm, specific, evidence-led. The moment the deck sounds like a guru, this audience is gone.

### 3. "What happens when the AI gets it wrong?"
> "AI being non-deterministic and making things up is what worries me about putting it in automation tasks."
> "garbage in, garbage out. AI doesn't magic it away."
> The most-saved advice: ask "what happens when the AI gets it wrong?"

Reliability is the deepest practical fear. **Deck response:** address it head-on, human-in-the-loop / approval gates ("it drafts, it doesn't send"), and the brains/winners argument (good inputs → good outputs). Don't pretend AI is infallible; show the control system around it.

### 4. "Integration is where it dies"
> "The software you're already using is gonna be your biggest enemy."
> "Integration kills all excitement when it comes to any technology."
> "The biggest mess isn't the models, it's the wiring, the monitoring, the guardrails, the debugging at 2am."

Buyers (and especially the technically-aware ones) know the hard part is connecting to their real, messy stack. **Deck response:** this is a strength to claim, "we've done this 100+ times, we know what breaks." The Secret 3 (build-is-hard) section already leans here; keep it.

### 5. "Generic AI output is obviously bad"
> "yet another useless ChatGPT vomit."
> "The more it tries the more it's obvious that AI is AI."
> Posts visibly written by AI get torn apart in comments.

This audience can *smell* generic AI and they hate it. **Deck response:** this is the wedge, the brains/winners argument (composite Secret 2) directly answers it. "Generic AI writes the average of the internet; an agent with a brain writes like you." Lean in hard.

### 6. Distrust of self-promotion
> "On Reddit there are so many posts on how they're doing great stuff, just to sneakily plug something they want to sell."

The audience is allergic to the bait-and-switch. **Deck response:** the educational-first structure IS the answer, teach for 100+ slides before the offer is named. The structure earns the right to pitch.

---

## What this audience actually pays for

The flip side, what surfaced as genuinely valued:

> **"You're not selling them an agent, you're selling them relief from a specific pain."**

This is the single best framing in the research. The webinar should sell *relief from a named pain*, not technology.

- **Results today.** "Clients pay for automations that deliver results today." Speed-to-value beats sophistication.
- **Reliability over cleverness.** They'd rather have a boring thing that works than an impressive thing that might not.
- **A real problem solved.** "Most people waste time trying a bunch of AI tools that sound cool but don't solve a real problem." Specificity wins.
- **Claude is trusted.** Across r/aiToolForBusiness, Claude is the repeatedly-recommended tool for non-technical owners ("automates most of the workflow from product, design to code and marketing"). Naming Claude Code as the foundation is a credibility asset with this audience, not a risk.

---

## Language that resonates (use these registers)

- Plain, specific, unhyped. The audience rewards "here's exactly what breaks" over "this changes everything."
- "Relief from a specific pain", outcome language, named pain.
- "Results today" / "what actually works" / "a real problem."
- Honest about limitations, "it drafts, it doesn't send," "garbage in, garbage out, so we fix the inputs."
- Avoid: "revolutionary," "10x," "game-changer," "unlock," and anything that sounds like a course funnel.

---

## How the deck uses this file

- **Secret 1 (multi-agent)** must defuse objection #1, teach *why* focused agents beat one, don't assert "agents are magic."
- **Secret 2 (brains)** is the direct answer to objection #5, the generic-AI-copy problem. Lean in hardest here.
- **Secret 3 (build-is-hard)** claims objection #4 (integration) as proof of expertise.
- **The offer / closes** must defuse objection #2, clean round-number pricing (no 7-enders), calm tone, generous teaching as the anti-grifter signal.
- **The whole deck** must include a reliability beat (objection #3), human approval gates, good-inputs argument.
- **The FAQ slide** should pull its questions from objections #2, #3, #4 above, they are real, not invented.

---

## Refreshing this research

Re-run before any major deck or when the offer/audience shifts:

```bash
python3 scripts/research_audience.py --comments --queries \
  "AI automation agency" \
  "tried AI it was generic" \
  "AI agency scam" \
  "what happens when AI gets it wrong" \
  "AI tool for small business owner"
```

Then synthesize the output back into this file. The objection landscape moves, generic-AI fatigue, guru backlash, and reliability fear are all live and intensifying as of this research date.

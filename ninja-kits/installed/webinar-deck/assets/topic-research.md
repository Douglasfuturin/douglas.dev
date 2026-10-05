# Topic Research, [CLIENT NAME]

> The subject matter the webinar teaches, researched and verified, not written from memory. An educational-first webinar lives or dies on whether the teaching is *accurate and current*. Refresh before every deck with WebSearch + `scripts/reddit_research.py` + WebFetch on primary sources.

**Current research subject:** the evolution of business automation → AI agents → Claude Code, and the architecture of a working AI operating system (the topic the Friday Labs AIOS webinar teaches).
**Method:** WebSearch + ScrapeCreators Reddit API + primary-source verification.
**Date:** 2026-05.

---

## The four eras of automation (verified)

The webinar's spine. Each era's facts are checked, not assumed.

### Era 1, Zapier (the rule era)
- Founded 2011. Now 3M+ users, 100,000+ paying customers, 7,000+ app integrations.
- Model: rigid **"When X happens, do Y"**, a trigger and a predetermined action.
- Strength: reliable, simple. Weakness: it can only follow rules wired by hand; the moment the situation changes, it breaks.

### Era 2, ChatGPT + Make (the "thinking" era)
- AI enters the loop, it can write, summarize, classify, make fuzzy judgments.
- But ChatGPT is trained on the internet, it doesn't know *your* business. And Make.com still needs every step wired by hand.
- Net: smarter than Era 1, still generic, still brittle.

### Era 3, n8n and the first agents (the "goal" era)
- AI you hand a *goal*, it reasons, plans, and figures out the steps itself.
- Real autonomy arrives. But early agents are fragile, hard to control, and take an engineer to run and babysit.
- Net: powerful, not yet usable by a business owner.

### Era 4, Claude Code (the agentic era)
- An **agentic system**: acts toward a goal with autonomy instead of responding one prompt at a time.
- The agentic loop: **reads context → plans a sequence of actions → executes them with real tools → evaluates the result → adjusts.**
- Operates at the project level, understands a whole system, not line-by-line.
- For the first time, AI can *run the work*, not just talk about it.

**Market context:** the AI-agent market was $7.84B in 2025, projected to $52.62B by 2030. The shift from rule-based automation to autonomous agents is the defining business-tech move of the moment, useful for the "why now" urgency.

---

## What makes Claude Code genuinely different (verified, credibility for the deck)

- **Agentic, not conversational.** A chatbot answers a prompt. Claude Code pursues a goal across many steps with real tools.
- **Tool use + execution.** It doesn't suggest, it acts: reads files, runs commands, integrates with real systems.
- **Deep context.** Analyzes an entire codebase/system without chunking or losing the thread.
- **Default-cautious, human-controlled.** Claude Code asks before making changes or running commands; the operator sets how much autonomy it has, from approving every action to letting it run. **This is the factual basis for the deck's reliability beat** ("it drafts, it doesn't send" / approval gates are real, built-in behavior, not a marketing promise).

---

## Why multiple agents with defined roles (verified, backs Secret 1)

Real research, not intuition:

- **The 60-70% rule.** Anthropic research shows model accuracy drops measurably once context utilization exceeds **60-70% of the window**, especially for information in the middle of the context.
- **The 15-20 tool wall.** Once a single agent has access to **15-20 tools, tool-selection accuracy drops below 80%.** A business has far more than 20 tools.
- **The fix is architectural, not bigger models.** "The solution isn't larger models with longer contexts, it's **smaller, specialized agents, each with 3-5 tools they know deeply.**"
- **Past the limit, the agent loses its own plan.** When a context window overflows, the earliest information drops out and the agent loses track of what it was doing. A second agent with its own fresh context solves what compression can't.
- **Separation of concerns.** Each subagent has distinct tools, prompts, and trajectory, reducing path-dependency and confusion.

**For the deck:** Secret 1 (one AI can't do everything) is now backed by hard numbers, the 60-70% accuracy threshold and the sub-80% tool selection at 15-20 tools. Use these. They turn an intuitive claim into a researched one, exactly what the skeptical audience (see `audience-research.md`) needs.

---

## Agent brains, knowledge bases (verified, backs Secret 2)

- In 2026, agent **memory is a first-class architectural component**, a production engineering discipline with its own benchmarks and research literature.
- **The dominant pattern is markdown files.** "The most widely adopted memory pattern is also the simplest: a markdown file injected into the LLM's context." Markdown files have become "the de facto standard for AI agent memory systems" and "the source of truth."
- Structured memory directories are standard: `learnings.md` (curated knowledge), `observations.md` (raw patterns), `goals.md` (active objectives), skills directories (reusable recipes).
- Context engineering best practice: clear delimiters, structured formats, and a clean separation of instructions / tools / memory / retrieved data.

**For the deck:** Secret 2 (agent brains) isn't a Friday Labs invention, it's literally the 2026 industry-standard pattern. The deck can say so: "the way every serious AI system stores knowledge now is structured markdown the agents read." That's credibility, and it directly answers the audience's "generic AI output is bad" objection, a brain is what makes output specific.

---

## Cloud hosting, team access (Secret 3)

Less of a published-research topic, more an operational truth, state it plainly:

- Claude Code and its agents/brains, set up on one person's machine, are reachable only by that person.
- A system one person can reach is a personal tool, not a company operating system.
- Hosting the agents + brains in the cloud is what lets the whole team connect to the same system, and lets routines run on a schedule (overnight, unattended).
- This is the step that converts "an impressive thing the founder has" into "infrastructure the business runs on."

**For the deck:** Secret 3 is the operational completion of the argument. It doesn't need a statistic, it needs the clear "only-you-can-reach-it" contrast. Keep it concrete.

---

## How the deck uses this file

- **Origin story / four eras (Section 4)**, the era facts above are verified; use the real dates and the trigger→action vs agentic-loop contrast.
- **Secret 1**, cite the 60-70% context-accuracy threshold and the 15-20-tool / sub-80% figure. Hard numbers beat assertions for a skeptical audience.
- **Secret 2**, note that structured-markdown brains are the *de facto industry standard*, not a proprietary trick. Credibility + the answer to the generic-AI objection.
- **Secret 3**, keep it concrete and operational; the only-you-can-reach-it contrast.
- **The reliability beat**, Claude Code's default-cautious, human-approval behavior is *real and built in*. The deck can state it as fact.
- **"Why now" urgency**, the $7.84B → $52.62B market trajectory is a legitimate, non-manufactured urgency anchor.

---

## Refreshing this research

Re-run before any major deck or when the topic shifts:

```bash
python3 scripts/reddit_research.py --comments --queries \
  "Claude Code business" "AI agents real use" "multi-agent system"
```

Plus WebSearch the core claims (the framework names, the statistics, the dates) and WebFetch primary sources. The AI-agent space moves monthly, verify every statistic and every "newest thing" claim before it goes on a slide.

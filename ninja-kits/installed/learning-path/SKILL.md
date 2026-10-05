---
name: learning-path
description: Build a calibrated, week-by-week learning plan for any skill — vetted resources, weekly deliverables, projects that prove competence. Trigger when the user says "I want to learn X," "how do I get good at," "build me a roadmap for," "study plan for," "teach me," "curriculum for," "where do I start with," or any variant of asking for structure to go from where they are to where they want to be in a defined time window.
---

# Skill Roadmap

Most learning plans fail in the first three weeks because they overestimate available time, underestimate the awkwardness of being a beginner, and skip the part where you actually build something. This skill writes plans that don't fail there.

## The core idea

Learning compresses into four loops, repeated across the plan:

1. **Calibrate** — figure out where the user actually is, not where they say they are.
2. **Scaffold** — choose the smallest set of resources that covers the skill graph.
3. **Sequence** — order them so each week produces something visible by Sunday.
4. **Drill** — protect time for spaced retrieval, not just new input.

A plan that does all four can survive a missed week. A plan that's just a list of courses cannot.

## Calibrate first

Before writing a roadmap, you need five things from the user. Ask them in one batch — not five questions across five turns.

| Question | Why it changes the plan |
|---|---|
| What exactly do you want to be able to do? | "Learn Python" and "Build a working data dashboard at work" need very different plans |
| What's the deadline or target date? | A 4-week sprint and a 6-month plan have different shapes; without a target the plan drifts |
| How many hours per week — honestly? | Most people overstate by 2×; ask for the *worst* week's hours, not the best |
| What do you already know that's adjacent? | A backend dev learning React skips weeks; a complete beginner doesn't |
| Why does this matter to you? | Job change, side project, exam, curiosity — different motivations need different proof points |

If the user gives a vague topic ("I want to learn AI"), narrow it once with a single question — "AI for what? Building products with LLMs, machine-learning fundamentals, or hands-on Python ML?" — and then proceed with whatever they say. Do not ask three rounds of clarifying questions.

## Research the skill graph

Use web search to verify the resources before recommending them. Concretely:

- Confirm the resource still exists and is updated for the current version of the technology.
- Read the table of contents or syllabus and pick specific modules, not the whole course. "Weeks 1–4 of Andrew Ng's course" beats "take Andrew Ng's course."
- Find at least one **free** path through the skill before recommending paid resources. Recommend paid only when the free path has a real gap.
- Avoid resources older than ~3 years for fast-moving fields (AI, frontend, devops). Avoid courses with last-updated dates that don't show.
- Check the community discussion (Reddit, HN, niche forums) for what people who actually got good in this field recommend versus what shows up in SEO content.

Pull at least 3 candidate resources for each phase before settling on the one you'll prescribe. Quality varies wildly within any topic.

## Plan structure

The output is a markdown document with this shape. Adjust phase count to the timeline (a 4-week plan has 2 phases; a 6-month plan has 4).

```markdown
# [Skill] in [N] weeks

**The promise:** by [end date] you will be able to [specific, demonstrable outcome].
**Time budget:** [N] hrs/week × [N] weeks = [total] hours.
**Starting point:** [the user's current level, in their own words].
**Proof of completion:** [the artifact or test that proves they got there].

---

## Phase 1 — [Name that captures the phase's job, e.g. "Learn the alphabet"] · weeks 1–[N]

**By the end of this phase, you can:** [specific capability, testable].

### Week 1 — [Topic]
- **Input** (~[X] hrs): [specific resource — course module, chapter, video with link]
- **Practice** (~[X] hrs): [hands-on exercise tied to the input]
- **Drill** (~30 min): [retrieval exercise — recall, flashcards, re-implementation from scratch]
- **Ship by Sunday:** [visible artifact — a script, a working query, a paragraph explanation]

### Week 2 — [Topic]
[same shape]

### Phase project — week [N]
[A real project that uses everything from this phase. Specific, not "build an app." Examples: "A CLI that reads a CSV and outputs the top 10 most common values per column," "A one-page write-up explaining backpropagation to a friend who knows calculus."]

---

## Phase 2 — [Name] · weeks [N]–[N]
[same structure]

---

## Resource budget

| Resource | Format | Cost | Used in |
|---|---|---|---|
| [Specific course/book/tutorial with link] | Video / Book / Tutorial | Free / $X | Phase X, weeks Y–Z |

## Common ways this plan fails (and what to do)

- **You miss a week.** Don't try to catch up by doubling next week. Skip the week's *new input* and keep the *drill*. The plan reorganizes around the missed input next phase.
- **You hit a wall on a concept.** Spend one extra session on it. If still stuck, post the specific question to [community/forum]. Do not silently fall behind.
- **You start enjoying tangents more than the plan.** Good — but timebox them. Tangent days are fine; tangent weeks kill momentum.
- **Resources turn out to be wrong for you.** Switch. The point is the skill, not the resource. The "Resource budget" table has alternates pre-listed where possible.

## How to know you're done

Three concrete tests:
1. [Tangible test, like: "You can build [project] from scratch without looking up syntax for the basics."]
2. [Tangible test of explanation, like: "You can explain [concept] to someone who knows the adjacent field, in 5 minutes, without notes."]
3. [Real-world test, like: "You can read open-source code in this language and follow what's happening."]

If you pass all three, you don't just "know" the topic — you can use it.
```

## How to choose what each week contains

The trap is to fill each week with the maximum input the schedule allows. The correct move is to fill each week with the *minimum* input that supports the week's drill and ship-by-Sunday. New input should be ~50–60% of weekly hours; practice ~30%; drill and review ~10–20%. The drill is the part everyone wants to skip and the part that turns input into actual recall.

For practice projects, follow the **rule of escalating realism**: the first project per phase can be artificial; the phase-end project must be something the user would actually want or use. Otherwise it feels like homework and doesn't get finished.

For input cadence, alternate **video-first** weeks (lower friction, good for motivation) with **reading-first** weeks (higher information density, better retention). Pure-video plans make people feel productive without learning much; pure-reading plans burn out anyone who isn't already a reader.

## Save and offer

Save the final plan as `Roadmap-[SkillSlug]-[NumWeeks]wk.md` in the working directory.

After delivering, ask one specific follow-up — not all of them at once:

> Want me to (a) build a daily schedule that fits your calendar, (b) go deeper on any phase, (c) find alternative resources for any of these, or (d) write the first week's check-in prompt so we can review your progress next Sunday?

## Hard rules

- **Honesty over optimism.** If a topic genuinely takes 6 months to get useful at, do not pretend it takes 6 weeks. Adjust the user's deadline or narrow the goal — do not fabricate an unrealistic plan.
- **Verified resources only.** Never recommend a resource you didn't search for and confirm exists. Outdated or dead links destroy trust.
- **One project per phase, minimum.** Learning without building is forgetting.
- **Front-load wins.** Week 1 must produce something the user can show someone by Sunday — even if it's small. The first visible result is what makes weeks 2–4 happen.
- **Free first.** Recommend paid resources only when the free path has a real gap. "$1,200 bootcamp" is rarely the right call for someone who has not yet committed 10 free hours.
- **Buffer weeks for any plan over 8 weeks.** Add a "consolidation" week every 4–6 weeks where the only job is to revisit, drill, and ship a small thing. Plans without buffer weeks fail the moment life happens.
- **Convert to absolute dates** when the user gives you a timeline. "12 weeks from today" → compute and write in actual dates so the plan reads correctly six weeks from now.

---
name: email-writer
description: Write an email that sounds like the user wrote it on their best day — sharp, specific, no filler, one clear ask. Trigger when the user says "draft an email," "write to my [boss/client/landlord/etc]," "help me reply to this," "send a follow-up," "say no to this," "ask for a raise," "introduce me to," or any variant of needing email words that they can paste and send.
---

# Email Composer

Most email advice tells you to be polite. Polite is the floor, not the goal. The goal is an email the recipient can answer in under thirty seconds because you've made the ask, the context, and the path forward unmissable. This skill writes those.

## How this skill thinks about email

Three things make an email work, in this order:

1. **Voice** — does it sound like the sender? Not a template, not LinkedIn-ese, not ChatGPT default warmth.
2. **Form** — is the ask in the first or second sentence? Are there fewer than five sentences? Is the subject line specific?
3. **Friction** — what does the recipient have to do to reply yes? Every word of friction reduces reply rate. Cut anything that isn't doing work.

If you nail voice and the form is wrong, you sound charming and ineffective. If you nail form and the voice is wrong, you sound like a cold-outreach script. Both have to work.

## What to gather before writing

Read the user's request and the conversation context. Before drafting, you need:

- **Recipient** — name, role, relationship (first contact / ongoing / responding to a thread).
- **The ask** — the *one* thing the recipient should do. If there are two asks, you are writing two emails.
- **Context the recipient already has** — do not re-explain things they know. If they sent the user a question, the email should reference it specifically.
- **Tone signal** — pull this from the user's CLAUDE.md if it exists, the prior thread if there is one, or how the user phrased the request. "Help me reply to my boss" is different from "help me reply to a recruiter who keeps spamming me."

If the ask isn't clear, ask one question and stop. Don't ask three things at once. The clarifying question is the single thing blocking you from writing — usually it's the ask, the recipient, or the desired outcome.

## The shape of a good email

This is the default skeleton. Use it unless the situation demands otherwise (a one-line "yes" reply doesn't need it; a layoff notification has its own form).

```
Subject: [specific noun + verb + when, ≤ 8 words]

[Greeting that matches the relationship]

[Hook line — names the reason for writing in a way the recipient cares about. Never "I hope this finds you well." Never "Reaching out to..." Lead with their world, not yours.]

[1–2 sentences of context, only what they need to act.]

[The ask — one sentence, action verb, specific. "Could you review by Thursday?" beats "Wanted to see if you might have a chance to take a look at this when you get a moment."]

[Sign-off]
[Name]
```

Five sentences total is the target. Six is the ceiling. If you wrote eight, cut two.

## Subject lines

Subjects do work the body cannot. Write the subject *after* the body so it can preview the ask.

| Bad | Why | Better |
|---|---|---|
| "Following up" | Tells the recipient nothing | "Q1 budget — your sign-off by Friday?" |
| "Quick question" | Lies about being quick | "1 question on the Acme contract scope" |
| "Touching base" | Implies no purpose | "Status on the design review — anything blocked?" |
| "Hi!" | Filler | "Intro: [their name] ↔ [other person], re: [topic]" |

Three subject patterns that consistently outperform:
- **Noun + verb + deadline** — "Contract redlines — need by Tuesday"
- **Question that implies the answer** — "Move the standup to 10am?"
- **Specific reference + ask** — "Your Stripe Press piece — can I quote it?"

## Format by situation

The skeleton flexes. Here's how it bends for the cases you'll actually see.

**Cold outreach.** Open with a specific signal you've actually paid attention (a line from their last post, a project they shipped, a mutual connection by name — never "I love your content"). One sentence on why you. One sentence on the ask. One short paragraph max.

**Follow-up.** Reference the prior thread by date or topic in the first line. Add new value (a deadline approaching, a development on their end, a thought you had on the original question) — never just "checking in." If the previous thread was 5+ days ago, a short polite nudge with a yes/no question outperforms a long re-pitch.

**Negotiation.** State your position as a proposal, not a question. "I'd like to propose $X for the Y scope" beats "I was wondering if maybe $X could work?" — the second one telegraphs you'll cave. Anchor first when you have data; ask their range first when you don't.

**Saying no.** Direct + brief reason + alternative if you have one. Three sentences. "Thanks for asking — I can't take this on right now because [one-line reason]. [Optional: I'd suggest [name] who does this kind of work, or I'd be open in [timeframe]]."

**Update / status.** Headline first. "Project on track — final review Wednesday." Then 2–3 bullets if needed. End with what you need from them, or "no action needed" if there's nothing.

**Apology.** Acknowledge → take responsibility → say what you're doing → no excuses. If the apology has the word "but" in it, rewrite. The goal is to make the recipient feel taken seriously, not to make yourself feel forgiven.

**Asking for something hard** (raise, intro, favor, second chance). Open with the ask. Justify it briefly with specifics, not adjectives — "I closed three of the four enterprise deals last quarter" beats "I've been working really hard." Make it easy to say yes by proposing the path: "Could we put 20 minutes on the calendar next week to discuss a comp adjustment?"

**Replying to a thread.** Quote-reply style — match the energy and length of what they sent. If they wrote two sentences, do not write five paragraphs. The most common error is over-replying to a casual message.

## What to delete on the second pass

Almost every first draft contains these. Cut them all:

- "I hope this email finds you well" / "I hope you're doing well"
- "I just wanted to..." (delete "just wanted to" — it apologizes for emailing)
- "I was wondering if..." (replace with the actual ask)
- "Sorry to bother you" (delete — it primes them to feel bothered)
- "When you get a chance" (delete unless you genuinely don't have a deadline; if you do, name it)
- "Does that make sense?" (condescending and unanswerable)
- "Per my last email" (passive-aggressive — instead, restate the ask cleanly)
- "Circling back" (cliché — say what you actually need)
- "Touching base" (meaningless)
- Adverbs in general — "really excited," "very interested," "absolutely love" all weaken the sentence

## Voice calibration

Three quick reads to check before delivering:

1. **Read it as the recipient.** Does it feel like work to reply? Where would you stall?
2. **Read it back to yourself out loud.** If it doesn't sound like something you'd say in a 1:1, rewrite.
3. **Check the relationship match.** A note to a longtime client should not sound like a cold email; a cold email should not sound like banter with a friend.

## What you deliver

Hand the user the email — subject line on top, body underneath, ready to copy-paste. No preamble. No "here's a draft for you to consider." Just the email. After it, offer in one short line:

> Want it shorter, more formal, or with a follow-up scheduled if they don't reply in [N] days?

If the request is open enough that two angles are plausible (e.g., a cold pitch where you could lead with their work or with the user's credentials), draft both versions, label them "A" and "B," and let the user pick.

## Hard rules

- Never start with "I hope this email finds you well." It is a tell that the email contains nothing the recipient needs.
- Never write more than 5 sentences unless the user asked for long form.
- Never write a subject line that doesn't preview the ask.
- Never invent context. If the user didn't tell you a name, a number, or a date, leave the bracket empty `[name?]` and ask once at the end.
- Never sign off "Best regards" by default — match the tone. "Thanks," "Cheers," "Talk soon," and just "—Name" all beat "Best regards" in 90% of cases.
- Pull the user's name, role, and signature style from CLAUDE.md if available. Don't make up a job title.

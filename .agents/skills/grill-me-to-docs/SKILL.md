---
name: grill-me-to-docs
description: Use when the user wants their firsthand knowledge of building, deploying, or running this project with real customers, users, or developers turned into published documentation — e.g. "interview me for docs", "extract what I know", "help me document this so others can run it without me".
---

# Grill Me to Docs

<what-to-do>

Interview me relentlessly to extract what I know about this project that isn't written down anywhere, and publish it as documentation while we talk. Success criterion: someone who has never met me can set up, run, facilitate, and extend this project from the docs alone.

Ask exactly one question per message and wait for my answer. With each question, offer your best-guess answer for me to confirm, correct, or expand — never make me structure a brain-dump.

If a question can be answered from the codebase, specs, or existing docs, explore instead of asking. My time is reserved for what only I know.

</what-to-do>

<supporting-info>

## Where docs live

- Prose: `/doc/*.md`, rendered by the Docusaurus site under `docs/` (sidebar: `docs/sidebars.js`). The site scaffold may live on a docs branch or worktree — locate it with `find . -maxdepth 5 -name "docusaurus.config.*" -not -path "*/node_modules/*"` before concluding it's missing.
- Specs: `/specs/` is mounted into the site as a second docs instance. Specs are protected — propose changes to the user, don't edit them here.

Before the first question, survey the existing pages and sidebar so questions extend the docs rather than duplicate them.

## The gold is tacit

Prioritize questions about knowledge no file contains:

| Vein | Examples |
|------|----------|
| Setup reality | true ordering, environment gotchas, what breaks when done out of order |
| Field experience | what real customers/SMEs misunderstood, asked, got stuck on |
| The unwritten script | what a facilitator actually says, demos, skips, and how long each part takes |
| Failure & recovery | what went wrong live and what you did about it |
| Judgment calls | when to X vs Y, rules of thumb, what "good" looks like |
| Boundaries | what this is NOT for; anti-patterns you've watched people fall into |

## During the session

### One reader per page
Every page serves one reader (new facilitator, customer admin, SME participant, developer). Pin the reader before drafting. If material serves two readers, make two pages.

### Probe with concrete scenarios
Stress-test answers with persona-in-trouble scenarios: "A field engineer is 30 minutes into a live workshop and trace ingestion hangs — what should the doc tell them to do?"

### Chase the war story, then distill
When I mention something that happened with a real customer, dig in: what happened, what did you do, what do you wish you'd known going in? The doc gets the distilled lesson, not the anecdote — unless the anecdote teaches faster.

### Cross-reference claims
When I state how something works, verify against code and existing docs. Surface contradictions immediately: "FACILITATOR_GUIDE.md says X, but you just said Y — which is current?"

### Publish inline
When a piece of knowledge crystallizes, write or update the page right then — don't wait for an approved outline, don't batch drafts at the end. Rewrite stale sections in place; never append corrections below stale content. When a new page is born, add it to `docs/sidebars.js` (or note the needed entry if the scaffold isn't in this checkout).

### Show, don't describe — generate UI media
When a page needs a screenshot or walkthrough of the app, never hand-capture or describe the UI from memory. Add or extend a Playwright demo spec (`client/tests/demos/*.demo.ts`, reusing the E2E scenario tooling) and run `just docs-demos` — media lands in `docs/static/demos/<SPEC_NAME>/` and embeds as `/docs/demos/<SPEC_NAME>/<name>.webm`. Generated media re-captures with one command when the UI changes; hand-captured media silently rots.

### Test for transfer
After updating a page, re-read it as its target reader: where would they still have to ask me a question? That gap is your next interview question.

## Red flags — you've drifted off the method

- More than one question mark in your message → split it, ask the first one
- "Give me a brain-dump of..." → you're offloading structure onto the user
- "Once we agree on the outline I'll write everything up" → publish inline instead
- Asking where docs live or how a feature works → explore the repo first
- A page that mixes setup steps with philosophy → split by reader and purpose

## Ending a session

Recap pages created/updated, knowledge captured, and open veins worth a future session.

</supporting-info>

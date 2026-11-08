---
name: trim-design-note
description: Write or trim an engineering design note into the canonical nine-section shape - Problem, Root cause, Proposed change, Alternatives considered, Impact and risk, Rollout, Verification, Rollback, Open questions. Use when asked for a design doc, design note, RFC, or change proposal, or to trim/cut down a sprawling design discussion or draft into the standard template. Do NOT activate for reviewing a design, answering a design question, or a request to explain a change - those want prose, not a restructured note.
---

# Trim Design Note

Turn a design into a note someone can act on at 3am: what is broken, what
changes, what it costs, how to prove it, how to undo it. The template below is
the whole shape. Everything else is detail that either earns a line or gets cut.

## When this is the wrong tool

If the request is to *evaluate* a design, answer a question about one, or explain
a change already made, write prose. Restructuring someone's thinking into nine
headings is a way of answering a question nobody asked. This skill is for
producing or trimming a note, not for discussing one.

## The template

```markdown
# <Short imperative title, e.g. "Pin AWS provider to 5.x to stop RDS replacement">

| Author | Date | Status | Ticket / Incident |
|--------|------|--------|-------------------|
| <name> | YYYY-MM-DD | Draft / In review / Approved / Done | <link> |

<!-- Problem and Proposed change are always required. For any other section that
     genuinely does not apply, keep the heading and write:
     _Not required — <one-line reason>._ -->

## Problem
What is broken or at risk, who/what is affected, and how we know.
Include concrete evidence: error message, failing plan, alert, log line.

## Root cause
One or two paragraphs. Why it happens, not just what happens.

## Proposed change
What changes and where (repo, module, file, resource address, namespace).
Include the key snippet or diff — only the lines that matter.

## Alternatives considered
One line each: the option and why it was rejected.

## Impact and risk
- Blast radius: environments, services, teams affected.
- Disruption: downtime, restarts, resource replacement, data-loss risk.
- Dependencies / ordering: anything that must happen first.

## Rollout
Ordered steps, environment by environment, with exact commands where useful.

## Verification
How we prove it worked: expected plan output, kubectl/health checks, metrics, alerts clearing.

## Rollback
Exact steps to undo. State explicitly if rollback is not clean (state changes, destroyed resources, migrations).

## Open questions
Only real unresolved items, each with an owner if known.
```

## Trimming

The hard part is not filling nine headings. It is cutting until each one is
load-bearing.

- **A good note is about a page.** Three pages means something was not trimmed.
- **Cut any sentence that would survive being pasted into a different design
  note** — background, motivation, general best practice, "this is a common
  problem." It is true of every design and therefore true of none.
- **Do not restate Problem in Root cause.** Problem is what is broken; Root
  cause is the mechanism. If a reader could delete a section without losing
  anything, delete it.
- **Concrete or cut.** If a section cannot name a specific file, resource
  address, namespace, command, or number, it is too abstract to be useful.
- **One line per alternative**, and only alternatives that were genuinely
  weighed. A list of options nobody considered is padding, not rigour.
- **Zero open questions is a valid answer.** Do not manufacture one to look
  thorough.

## Never fabricate

A design note with invented evidence is worse than one with a blank, because
it is trusted.

- No invented error messages, log lines, plan output, metrics, or alert names.
  If the Problem section has no concrete evidence, ask for it or write
  `_Need evidence: <what to capture>_`.
- No invented author, date, ticket, or approver. Use `<name>` / `<link>`
  placeholders.
- Do not state a root cause you have not traced. "Various causes" is an honest
  answer; a confident wrong mechanism sends someone down the wrong path for a
  week.

## `Not required` is not a parking space

Only Problem and Proposed change are truly always required. But the sections a
reader needs at 3am are Impact, Rollout, Verification, and Rollback. Reach for
`_Not required — <reason>_` when the section genuinely does not apply: no
alternatives were considered, nothing can be rolled back because nothing
persists. Do not use it to skip a section that is empty because nobody thought
about it — write `Unknown — <who needs to answer this>` and put it in Open
questions with an owner.

## Trimming an existing draft

Do not restructure silently. When you cut or rewrite someone's prose, report
what you dropped in one line per item, so nothing disappears without a trace.
Content that had no home in the nine sections but carried real decisions
belongs in that report — not quietly deleted.

## Output

Write the note as a single markdown file. Unless told otherwise, do not commit
it, open a PR, or touch any other file in the repo.
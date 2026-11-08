---
name: team-brainstorm
description: MANUAL-ONLY. Multi-persona design debate and plan review. Invoke with /brainstorm. Do NOT activate this skill from topic matching or context - not for "brainstorm", "options", "trade-offs", "review this plan", or any open-ended design question. Activate only when the user names this skill or its slash command explicitly. If a request merely sounds like a fit, answer normally instead.
---

# Team Brainstorm

Six named agents with distinct tendencies debate a design question, then vote. The
point is friction: a single-voice answer smooths over the trade-offs that matter.

## Invocation

Manual only. If you reached this file because a request *sounded* like a brainstorm,
stop and answer normally - a six-agent debate is an expensive answer to a question
that wanted two sentences. Proceed only if the user typed the slash command or asked
for the team by name.

## Pick a mode first

| Mode | Use when | Phases | Output |
|---|---|---|---|
| **Full brainstorm** | New feature, architecture, or greenfield direction | 1, 2, 3 + vote | Transcript + design note |
| **Mini brainstorm** | One scoped decision ("how should the scoreboard work?") | 1 + 2, no vote | In chat, or transcript only if asked |
| **Consilium** | Reviewing an existing plan, PRD, sprint, or PR | Review only | Flagged issues + fixes. See `~/.config/opencode/skills/team-brainstorm/docs/consilium.md` |

Default to **mini** unless the question is big enough to justify the full run. A
three-line question does not need a 400-line design note.

## Non-negotiables

- **Name every agent.** "The team thinks..." produces bland consensus. Kira thinks
  something; Sage disagrees.
- **At least 2 genuine disagreements** in Phase 2, resolved or logged as open questions.
- **Sourced numbers, or the word "assumed".** Any number that drives the design, like a threshold, ratio, limit, quota, price, tier boundary - carries the source it came
  from or is labelled an assumption where it first appears. A number that reaches the
  note with neither is a bug in the note, not a detail. If an agent is challenged on
  where a number came from, "it's only a v1" is not an answer.
- **A non-answer is an open question.** Phase 1 threads must all close; so must Phase 2
  challenges. Every challenge ends in a concession, a synthesis, or an **Open
  questions** entry. An answer that changes the subject, defers to "v1", or restates
  the original claim is none of the three - log it. The failure mode is quiet: the
  challenge is in the transcript, it reads as settled, and nobody can tell later that
  it never was.
- **No pre-cooked winner.** Do not decide the answer and then stage a debate that
  arrives at it. If the vote is unanimous, you did it wrong.
- **One premise challenge.** Remy (or whoever owns scope) argues once that the
  requirement itself is wrong - that the obvious solution solves a problem the user
  does not have. The team answers on the merits; "out of scope" is not an answer.
  If the challenge wins, the note's **Decision** opens with it: the user asked for X,
  the team is proposing Y, and this is why.
  Name its owner before Phase 1 starts, in the roster line. If Remy is not on the
  roster or is cast in another lane, the challenge transfers - it does not lapse. A
  run with no premise challenge in the transcript is an incomplete run.
- **Proportional output.** Two files: transcript and note. The note stays under ~400
  lines; the transcript is however long the debate was.
- **No code edits.** This is a design session. The only files you write are those two.

## Workflow

### 0. Ground in the facts (do this before any ideation)

The original format is for blue-sky product work. In a codebase, ungrounded ideation
produces agents arguing about files that do not exist. Greenfield is not exempt: it
produces agents arguing about APIs that do not behave the way they remember.

**In a codebase:** find the 3-6 files this decision actually touches - query the graph
first if `graphify-out/graph.json` exists (global Graphify rule), otherwise `grep` /
`glob`. `read` each one. Note real module names, existing patterns,
current dependencies.

**Greenfield:** there is still ground truth. Read the sources the design depends on -
vendor API references and the exact fields they return, rate limits and quotas,
platform policies and ToS, pricing, and the local toolchain (what is installed, what
is missing). "No repo" is not "no facts."

**Either way:**

- If a claim needs a fact you have not read, read it. Never invent a path, API,
  schema field, threshold, or limit.
- If a source is unreachable, say so explicitly and mark anything resting on it as an
  assumption. A blocked source named is worth more than a fact recalled.
- Read any existing notes in `docs/design/` on this topic. Points a prior run settled
  are constraints for this one - state them in the roster brief so the team argues
  past them rather than back to them.
- Record what you read, and what you tried and could not read, under **Context read**
  at the top of both files.

This step never gets skipped. If you cannot find anything to read, write that sentence
under **Context read** and let the reader judge it.

### 1. Choose the roster

Default roster and swap-ins for other domains: `~/.config/opencode/skills/team-brainstorm/docs/personas.md`. Use 4-6 agents.
Fewer than 4 loses the friction; more than 6 turns into filler.

### 2. Phase 1 - Free ideation

Each agent pitches 2-3 raw ideas, max two lines each. No filtering, no critique yet.
Wild is fine. Repetition across agents is not - if two agents land on the same idea,
the second one says so and pitches something else.

### 3. Phase 2 - Debate and refinement

Agents address each other by name ("Nova, that's three services for a checkbox").
They combine ideas, kill weak ones, and surface constraints from Step 0. Each
disagreement ends one of three ways: someone concedes, they find a synthesis, or it
becomes an entry in **Open questions**. Never let one dissolve into vague agreement.

**Close every Phase 1 thread.** Before moving to Phase 3, check each idea raised in
Phase 1. Every one must be picked up in the debate, killed with a stated reason, or
promoted to an open question. Ideas that quietly disappear between phases are the
main failure mode of this format - and the ones that disappear are usually the
correctness concerns nobody wanted to answer, not the weak ideas. If an agent raised
a failure mode (orphaned state, idempotency, partial writes) and no concept addresses
it, that is an open question, not a resolved point.

### 4. Phase 3 - Final pitches

**Name the coupling unit first.** If the design ties one thing's lifetime, ownership,
or scope to another's, say which object owns it and why that one. List at least one
alternative unit and why it loses. Most designs have a defensible second answer here,
and it is usually the more interesting one - a boundary chosen by default is a
boundary nobody argued about.

3-5 polished concepts. Three real concepts beat five padded ones. Each needs:

- **Name** - short and memorable
- **Description** - 2-4 sentences
- **Pros / Cons** - at least two each, cons must be real
- **Effort** - S / M / L plus a rough day range
- **Touches** - the actual files or modules from Step 0

### 5. Vote

One line of justification per agent. Ties go to Remy (or whoever owns scope). Record
dissent - "Ivy voted B, still thinks A is untestable" is more useful than a clean 6-0.
If the vote is unanimous, stop before writing. A 6-0 means the concepts were not real
alternatives - they were one idea at three sizes. Name the strongest argument against
the winner and which agent should have made it, then either reopen that argument or
record it in the note as an unmade case. Do not manufacture a dissent to hit a quota;
an honest "the roster converged and here is what nobody argued" is the useful artifact.

### 6. Write both files - transcript first

**Transcript before note.** Write `docs/design/<topic>-transcript.md` first, while the
debate is freshest in context, then the note. Never the other way round.

- **Transcript:** the full debate, near-verbatim. Format and rules:
  `~/.config/opencode/skills/team-brainstorm/docs/transcript-format.md`. This is a copy operation, not a writing task.
- **Note:** the distilled decision. Skeleton: `~/.config/opencode/skills/team-brainstorm/docs/output-template.md`.
  Path: `docs/design/<topic>-brainstorm.md`.

The two are not redundant. The note answers "what did we decide"; the transcript
answers "why was the obvious alternative wrong". Each links to the other.

### 7. Close out in three lines

Once the files are written, the chat message is a pointer, not a third copy. Give the
two paths, the winning concept in one line, and stop. Do not re-list the open
questions, re-summarise the debate, or restate the vote - all three are in the files,
and a chat summary that paraphrases them is a version that can drift from them.

The one exception: if something needs a decision from the user before implementation
can start, say that in one line and name it.

### 8. Consilium the note before implementation

The brainstorm's output is a plan, and plans get reviewed. Run `~/.config/opencode/skills/team-brainstorm/docs/consilium.md`
against the note that was just written, with the same roster. Ivy reviews the
acceptance criteria she helped produce; Remy checks whether the effort estimate
survives the constraints the debate established.

This catches the class of error the debate cannot: an estimate that was honest for the
concept as pitched and wrong for the concept as written up. Cheap - the context is
already loaded - and it is the difference between a design note and a design note
someone checked.

**Findings go into the note, not into a third file.** Consilium's normal default is
in-chat, because a review of a sprint plan gets acted on the same day. A design note
is different: it outlives the session and a later run reads it as prior art. A blocker
that lives only in chat is inherited silently, with the note's authority attached.
Route each finding:

- **Blocker you fix now** - fix the note, and add one line under **Decision** saying
  what changed and why. The review is consumed; nothing to file.
- **Blocker or risk you cannot fix now** - an **Open questions** entry with an owner.
  That section already exists for exactly this.
- **Nit** - fix it or drop it.

Then mark the header so a future reader, and a future Step 0, can tell "checked and
clean" from "never checked":

    Reviewed: consilium 2026-09-21 - 1 blocker fixed, 2 risks in Open questions

Write a separate `docs/design/<topic>-consilium.md` only when the review kills or
substantially reshapes the winning concept. Then the reasoning is the same genre as
the transcript - why the obvious answer was wrong - and folding it into Open questions
loses it.
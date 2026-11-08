---
name: build-plan
description: MANUAL-ONLY. Turn a settled design into a versioned design note, a short build plan, a tracker, a runbook and working rules for the implementing agent - light process around the implementation, not in front of it. Invoke with /build-plan. Do NOT activate from topic matching - not for "plan this", "how should I build X", or any open-ended design question. Activate only when the user names this skill or its slash command explicitly.
---

# Build Plan

Hands a project to an implementing agent - usually a local model in OpenCode - without a
human re-explaining it every session, and without a process that gets in the way of
building it.

| File | Answers |
|---|---|
| `docs/design/<topic>.md` | What are we building, and why not the obvious alternative |
| `docs/build-plan.md` | What order, and how do we know each part works |
| `docs/todo.md` | Where are we |
| `.opencode/rules/<topic>.md` | How the implementing agent behaves |
| `RUNBOOK.md` | What the human says - half a page |
| `docs/steps/SNN.md` | What this step changes - one sentence, a diagram, a few plain bullets |
| `scripts/checks/SNN.sh` | Does this step work - a script that explains itself as it runs |
| `docs/stages/<stage>.md` | Where the stage ended up: checks, what changed, what is left to decide |

The first five are written by this skill. The step summary and the check are written by
the implementing agent with each step; the stage report when a stage ends.

Runs after a decision exists. If the decision is still open, run `team-brainstorm` first -
this skill writes plans, it does not choose between concepts.

## Principles

- **The implementation is the point.** The agent builds; the process exists to tell the
  human it worked. Any rule that stops useful work without preventing a real failure has
  been removed, and should be removed again if it creeps back.
- **A step is a slice that runs.** No step that is only ceremony. Few steps: eight good
  slices beat twenty procedural ones.
- **A checkpoint is a script that exits non-zero on failure, and it explains itself.**
  What the step proves, one line per check, and on a failure what was expected, what was
  found, and where to look. `scripts/checks/lib.sh` does this; every checkpoint sources it.
- **Checks are written with the step, before its code, from the plan's Check lines.**
  Not all up front: written in advance they describe a system nobody has built yet and are
  wrong by the time they are needed.
- **The agent keeps the checks right, and never loosens one silently.** A wrong check gets
  fixed, with one line in the plan's Changes log saying what it checked before and what it
  checks now. A change that makes a check prove less is marked as a loosening and listed in
  the stage report. That mark is the whole safeguard against a gate reworded until it
  passes - so it is the one checkpoint rule that is not negotiable.
- **The plan is a map, not a rail.** The agent reorders, merges, splits or skips steps
  when what it has learned makes the plan wrong, and logs one line each time. The human
  can do the same by saying so.
- **The agent stops only for a reason.** A check that fails twice, the riskiest assumption
  failing, a clash with the design's load-bearing decision, a need to leave its scope.
  Otherwise it keeps going to the end of what it was asked to do.
- **Review is a ceremony at the end of a stage, not a gate on every step.** A different
  model, a new session, a short prompt. It is the only independent look at code and checks
  that share an author, so it is on by default - but it never blocks a step.
- **Every step gets a one-screen summary a human can read without reading code.** One
  sentence on what works after the step that did not before; a diagram - sequence when
  components call each other, state or flow when it is about states or branching, none
  when there is nothing to draw; three to six bullets on what each part does, in plain
  words rather than function names; up to three choices the human might want made
  differently. Written before the step's code, corrected to match what was built, and
  never a reason to wait: "do" builds straight through, "plan" writes the summary and
  stops for anyone who wants to look first.
- **The human gets a short report per stage.** Links to the step summaries, the check
  results, which checks changed, what is left to decide. One screen, no code.
- **Ground in the operational docs, interrogate before writing, name the load-bearing
  decision, version the design note.** The planning half is unchanged.

## Workflow

### 1. Ground

Read the project's operational surface before anything else:

- README, and any `docs/` guide covering scripts, build, test, or deploy
- The Makefile or task runner
- The existing verification script, and **how it reports failure**
- Any `lessons.md`, known-limitations section, or troubleshooting table

That last category is where the expensive surprises are. Record what you read under
**Context read** in the design note. Never invent a path or a flag.

### 2. Interrogate

Question bank: `~/.config/opencode/skills/build-plan/docs/interrogation.md`.

Grounding first, then questions - never ask what the repo already says. Three questions
per turn at most, usually one, with options offered where possible.

Two earn their place on their own:

- **What owns the lifecycle, and what else could?**
- **Who can actually edit the object carrying the configuration?**

When an answer breaks the design, say so in the same turn and name the options. Close by
summarising the decisions taken and any still open, and get confirmation before writing.

### 3. Write the design note

Skeleton: `~/.config/opencode/skills/build-plan/docs/design-note-template.md`.

- **The load-bearing decision**, with the alternative and why it lost.
- **Verification** - a numbered table of checks that would convince a sceptic. Write this
  *before* the build plan. It is what the checkpoints ladder up to.

### 4. Write the build plan

Skeleton: `~/.config/opencode/skills/build-plan/docs/build-plan-template.md`.

Sequencing advice, in priority order - advice for writing the plan, not gates on running it:

1. **Baseline first.** The existing system works, unmodified, on the new substrate.
2. **Riskiest assumption early.** The one step where failing means stop and rethink, and
   the plan says what changes if it does.
3. **Novel logic against a stub** before integration.
4. **Migration last**, with every test, script or assumption it invalidates listed row by
   row. "Update the tests" is not a plan.

Group steps into stages. A stage ends where there is something worth a human's attention:
a report, a full run of the checks, a review.

Each step has a goal, the files to read, what to do, and three to five plain-English
Check lines. No code in the plan, and no checkpoint scripts yet.

### 5. Write the rules, the runbook and the tracker

- Rules: `~/.config/opencode/skills/build-plan/docs/agent-rules-template.md` →
  `.opencode/rules/<topic>.md`. Make sure the project's `opencode.json` has
  `".opencode/rules/*.md"` in `"instructions"` - a rules file nothing loads is a rules file
  nothing obeys.
- Runbook: `~/.config/opencode/skills/build-plan/docs/runbook-template.md` →
  `RUNBOOK.md` at the project root.
- Tracker: `docs/todo.md`, one checkbox per step, links only.

### 6. Set up the harness

A minute, no ceremony. Copy from `~/.config/opencode/skills/build-plan/docs/`:

- `checkpoint-runner-template.sh` → `scripts/checkpoint.sh` (executable)
- `checkpoint-lib-template.sh` → `scripts/checks/lib.sh`
- `step-summary-template.md` → `docs/steps/TEMPLATE.md`
- `stage-report-template.md` → `docs/stages/TEMPLATE.md`
- `review-prompt-template.md` → `docs/REVIEW-PROMPT.md`

Do **not** write the checkpoints now. Each is written with its step.

### 7. Hand off in three lines

The artefact paths, the first step, and stop. Do not summarise the plan in chat - it is in
the files, and a chat summary is a version that can drift.

## Re-issuing for a project already in flight

When the project has artefacts from the earlier, stricter version of this skill: keep the
design note and the finished work. Then:

1. Rewrite `.opencode/rules/<topic>.md` and `RUNBOOK.md` from the current templates.
2. In `docs/build-plan.md`, group the unfinished steps into stages, merge or drop any that
   are only ceremony, and add a **Changes** log.
3. Replace `scripts/checkpoint.sh`; add `scripts/checks/lib.sh`, `docs/steps/TEMPLATE.md`,
   `docs/stages/TEMPLATE.md` and `docs/REVIEW-PROMPT.md`; remove `scripts/review-guard.sh` and
   `docs/reviews/REVIEW-PROMPT-TEMPLATE.md`.
4. Leave checkpoints for finished steps alone. Checkpoints already written for unfinished
   steps are rewritten with each step, sourcing `lib.sh`.
5. Collapse the tracker to one box per step.

## Anti-patterns

- Writing every checkpoint before any code exists
- A checkpoint the agent is forbidden to fix
- Loosening a checkpoint without marking it
- A checkpoint that reads "verify the service is working", or prints `FAIL` and nothing else
- A step with no runnable result
- A review, a guard or a hand-over standing between one step and the next
- "That is step 9, we are on step 6" as a reason not to do something useful now
- Stopping to ask about something the plan or the design already answers
- A third speculative rewrite after a check has failed twice
- A step with no summary, or a summary with code, function names or a file list in it
- A summary with no diagram when the step is about components talking to each other
- A summary that still describes the intent after the build went a different way
- Waiting for approval of a summary when the human said "do", not "plan"
- A stage report that lists files instead of saying what now works
- A build plan whose first step is building the new thing
- "Update the tests" as a migration step
- Code snippets in `docs/build-plan.md`
- Patching a design note through a decision reversal instead of versioning it
- A tracker that restates the plan
- Reviewing with the same model that implemented

# Build Plan Template

Copy into `docs/build-plan.md`. Keep it short: a step is a few lines, not a page.

````md
# <Topic> - Build Plan

Design: [./design/<topic>.md](./design/<topic>.md) · Tracker: [./todo.md](./todo.md) ·
Rules: [../.opencode/rules/<topic>.md](../.opencode/rules/<topic>.md) ·
Runbook: [../RUNBOOK.md](../RUNBOOK.md)

<N> steps in <M> stages. Each step is a slice that runs, with a check that proves it.

This is a map. Steps get reordered, merged, split or skipped as the build teaches us
things - each change is one line in the **Changes** log at the bottom.

## Stage A - <Baseline and the risky assumption>

### S0. <The existing system works, unmodified>

**Goal:** <one line - what runs afterwards that did not before>
**Read:** <exact paths>
**Do:** <concrete actions>
**Check:**
- <what will be true if this works>

### S1. <The riskiest assumption>

**Goal:**
**Read:**
**Do:**
**Check:**
- <...>

**If it fails:** stop. <What changes in the design. This is the one step where a failure
means rethink rather than fix and continue.>

## Stage B - <The new thing, against a stub>

### S2. <...>

**Goal:**
**Read:**
**Do:**
**Check:**

## Stage C - <Integration>

## Stage D - <Migration>

### S<n>. <Change the existing system>

| Existing check or script | Currently | Becomes |
|---|---|---|

## Done

- [ ] `scripts/checkpoint.sh all` green from a cold start
- [ ] Every row of the design note's Verification table is covered by a check
- [ ] What changed from the design, and why
- [ ] What production needs that this omits

## Changes

<One line each, newest first. Date - what changed in the plan or a check - why.
A check that now proves less starts with LOOSENED:.>

- YYYY-MM-DD - <merged S4 into S3 - the split had no runnable result>
- YYYY-MM-DD - <LOOSENED: S5 no longer checks latency - the stub cannot simulate it; moved to S9>
````

## Step anatomy

| Part | Purpose |
|---|---|
| **Goal** | One line. What runs afterwards that did not before. |
| **Read** | Exact paths. Keeps a small context window for the work. |
| **Do** | Concrete actions, not outcomes. No code. |
| **Check** | Three to five plain-English assertions. The script is written with the step. |
| **If it fails** | Only on the riskiest-assumption step. |

Each step also gets `docs/steps/SNN.md` when it is worked: one sentence, a diagram and a
few plain bullets on what it changes. Nothing for it goes in the plan.

## Checkpoints

Written by the implementing agent with the step - before the step's code - at
`scripts/checks/SNN.sh`, from the step's **Check** lines:

```bash
#!/usr/bin/env bash
. "$(dirname "$0")/lib.sh"

describe "<the step's goal>" <<'EOF'
Proves: <what will be true if this passes>
How:    <what the script actually does to find out>
Needs:  <what must be running or built first>
EOF

require  "<precondition>"     "<where to look>"  <command>
check_eq "<what is proved>"   "<where to look>"  "<expected>" "$(<command>)"
check    "<what is proved>"   "<where to look>"  <command>

finish
```

Run with `scripts/checkpoint.sh N`. A passing run reads:

    == S07  Reconciler ignores a duplicate request
       Proves: a second identical request creates nothing new.
       How:    sends the same request twice to the stub and counts the objects.

      [1] ok    stub answers on :8080
      [2] ok    first request creates one object
      [3] ok    second request creates nothing

    PASS: S07 - 3 of 3 checks passed

and a failing check says what it wanted, what it got, and where to look:

      [3] FAIL  second request creates nothing
            expected: 1
            found:    2
            look at:  src/reconciler.py, reconcile(), the existence test

- `describe`, a description and a "where to look" on every check, `finish` as the last line.
- `require` for a precondition later checks depend on; `check` otherwise, so one run
  reports every failure.
- The description is the first argument, on the same line, in double quotes -
  `scripts/checkpoint.sh N --explain` lists them by reading the script.
- `scripts/checkpoint.sh all` runs every checkpoint that exists and prints a summary.
- Each run is saved to `evidence/SNN.log` and committed with the step.

<If the project's existing test script does not exit non-zero on failure, say so here and
say not to copy it. This is common and it silently disables every check built on it.>

## Sequencing advice

For writing the plan. None of it is a gate on running it.

1. **Baseline first** - the existing system, unmodified, on the new substrate.
2. **Riskiest assumption early**, with what happens to the design if it fails.
3. **Novel logic against a stub** before integration.
4. **Migration last**, with what it invalidates listed row by row.

## Sizing

- A step should fit one session of a small-context model: about three files to read, about
  five checks, and a change that one screen and one diagram can explain. Past that, split it.
- But as few steps as give a runnable result each. If a step shows nothing new when it is
  done, fold it into its neighbour.
- A stage is two to five steps, ending where a human would want to look.

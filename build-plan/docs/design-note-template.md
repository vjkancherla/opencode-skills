# Design Note Template

Copy into `docs/design/<topic>.md`. Trim sections that carry nothing.

Versioning: when a new constraint invalidates the design, rename the current file to
`<topic>-vN-superseded.md` and write a fresh one. Link backwards. Never patch a design
note through a reversal - the reasoning that changed is the most valuable thing in it.

```md
# <Topic> - Design Note (v<N>)

Date: YYYY-MM-DD
Scope: <what this is and is not. "Proof of concept, not production grade.">
Supersedes: [v1](./topic-v1-superseded.md) (<one line: what changed and why>)

Context read:
- <file> - <the facts taken from it>
- <operational doc> - <scripts, entry points, how failure is reported>
- <stated constraint from the user, quoted>

## Decision

<Two or three sentences. The winning shape, not the reasoning.>

## Why <the load-bearing decision>

<Every design has one choice everything else hangs off: what owns the lifecycle, what
the unit of work is, where state lives. Name it. Give the alternative and why it lost.
If a previous version chose differently, say what broke.>

Alternative considered - <X>. <Why it loses here, and the condition under which it
would win instead.>

## What this simulates          <!-- only for a PoC or a scaled-down build -->

| Real thing | This build | Why it maps |
|---|---|---|

Deliberately **not** simulated: <list>. <Why they cannot be learned here.>

## Shape

<ASCII diagram. Components, boundaries, and the direction of every call.>

## <Core mechanism>

<The part a reader would otherwise get wrong. State machines, ownership chains,
idempotence rules. Include what happens on the second identical request.>

## Failure modes handled

<Three or four, numbered. For each: what the user sees, and what the system does. Then
say plainly which failure modes are NOT handled and why that is acceptable here.>

## Verification

<Numbered table. Write this BEFORE the build plan - it is what the checkpoints ladder
up to. Each row is a check that would convince someone who doubts this works.>

| # | Check |
|---|---|
| V1 | ... |

<Name the two or three that actually matter and why.>

## Roads not taken

- **<Option>** (<where it was raised>): the strongest case for it was <one line>. It
  lost because <reason>. It would win if <condition>.

## Open questions

- [ ] <question> (<owner>)

## Effort

<Range, with the breakdown. Name which part is the error-prone one and say when to do
it - usually last.>
```

## Rules

- **Decision at the top.** Never make the reader scroll to learn what was chosen.
- **The load-bearing decision gets its own section.** It is the thing a future reader
  will want to challenge, so make it easy to find and argue with.
- **Verification before build plan.** Written the other way round, the plan tests
  whatever is convenient rather than whatever matters.
- **Say what is not handled.** A design note that only lists strengths reads like
  marketing and gets trusted in situations it should not be.
- **Cons must be real.** "Slightly more code" is not a con.
- **Roads not taken is for reframes**, not for every rejected option - the ones that
  changed the shape of the problem.

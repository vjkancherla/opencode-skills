# Transcript Format

The transcript preserves the debate itself. The note says what was decided; this says
why the alternatives lost, which is the part that is hard to reconstruct later.

Path: `docs/design/<topic>-transcript.md`

## The one rule that matters

**This is a copy operation, not a writing task.** The phases already happened in chat.
Reproduce what each agent actually said, in the words they said it. Do not:

- rewrite argument into tidy prose
- merge two agents' points because they overlap
- drop an idea because Phase 3 rejected it - rejected ideas are the whole point
- soften a blunt exchange into "the team discussed trade-offs"
- add reasoning nobody voiced, or clean up a point that landed badly

If the transcript reads more polished than the chat did, you compressed it. The
messy version is the correct one.

## Structure

```md
# <Topic> - Brainstorm Transcript
Date: YYYY-MM-DD
Team: Kira, Nova, Sage, Ivy, Remy
Context read: src/api/session.ts, src/db/schema.sql
Decision: see [<topic>-brainstorm.md](./<topic>-brainstorm.md)

## Phase 1 - Free ideation

**Kira**
- Inline undo toast, 5s window. Cheapest path to "I can't break this".
- Full history sidebar. Probably too much for v1.

**Nova**
- ...

## Phase 2 - Debate

**Nova -> Kira:** A 5s toast means holding uncommitted state client-side. What
happens on navigate?

**Kira:** Then it commits. Undo is a nicety, not a guarantee.

**Sage:** That is a guarantee to the user even if it isn't one to us. If we show
"undo" we own it. Soft-delete column, reconcile on a job.

**Remy:** That is a migration and a worker for a toast.

*Unresolved -> open question: does undo survive navigation?*

## Phase 3 - Final pitches
<as pitched, including the ones that lost>

## Vote
| Agent | Vote | Why |
|---|---|---|
```

## Formatting

- `**Agent**` for a pitch, `**Agent -> Agent:**` when addressing someone directly.
- Keep the phase headings even if a phase was short.
- Mark each disagreement's outcome inline: *conceded*, *synthesised into X*, or
  *unresolved -> open question*.
- If an agent concedes in one line to an idea that reframed the problem, mark it
  *conceded - candidate for Roads not taken*. A one-line concession is where good
  reframes die: the idea is in the transcript, nobody argued for it, and the note
  has no reason to carry it. Tag it here, while the exchange is still in context.
- No summary section. The note is the summary; duplicating it here means the two
  files drift apart on the next edit.

## If context was compacted

Long sessions get compacted, and the early phases may no longer be verbatim in
context. If that happened, say so in the file rather than reconstructing from memory:

```md
> Phase 1 was compacted from this session's context and is summarised, not verbatim.
```

A flagged gap is honest. An invented transcript is worse than no transcript, because
it reads authoritative and nobody can tell which parts were made up.

# Design Note Template

Copy this shape into `docs/design/<topic>-brainstorm.md`. Trim sections that carry
nothing - an empty heading is worse than a missing one.

Write this **after** the transcript (`transcript-format.md`, next to this file), not before.

```md
# <Topic> - Team Brainstorm
Date: YYYY-MM-DD
Team: Kira, Nova, Sage, Ivy, Remy
Context read: src/api/session.ts, src/db/schema.sql, docs/adr/002-auth.md
Full debate: [<topic>-transcript.md](./<topic>-transcript.md)

## Decision
<The winning concept, in two sentences. This is the only part most readers will
read - put it first, not at the bottom after the debate.>

## Concepts

### 1. <Name>  *(selected)*
<2-4 sentences.>
- **Pros:** ...
- **Cons:** ...
- **Effort:** M (~3-4 days)
- **Touches:** src/api/session.ts, src/db/schema.sql

### 2. <Name>
...

## Debate highlights
- **Sage vs Remy on the migration:** Sage wanted a backfill before cutover; Remy
  argued it costs a week for a table with 400 rows. *Resolved:* dual-write, no backfill.
- **Ivy vs Kira on the undo flow:** unresolved - see Open questions.

## Roads not taken
- **<Idea>** (raised by X, conceded in Phase 2): the strongest case for it was
  <one line>. It lost because <reason>. It would win if <condition>.

## Vote
| Agent | Vote | Why |
|---|---|---|
| Kira | 1 | Fewest clicks to value. |
| Ivy | 2 | Still thinks 1's undo path is untestable. |

## Open questions
- [ ] Does undo need to survive a page reload? (Ivy, Kira)

## Next steps
- [ ] <concrete first task>
```

## Rules for the write-up

- **Decision at the top.** Never make the reader scroll through Phase 1 to learn what
  was chosen.
- **The Decision is what the vote produced.** Name the winning concept by number and
  name. A synthesis is allowed when the vote genuinely did not settle it - say so
  explicitly, name which concepts it merges and which agent's constraint forced the
  merge. A Decision that quietly describes something nobody voted for is the
  pre-cooked winner arriving one step later than usual.
- **Debate highlights, not a transcript.** 3-5 bullets, and only the exchanges that
  changed the outcome. The full version lives in the transcript file - keeping this
  section short is what makes the two files worth having separately.
- **Roads not taken is for reframes, not rejects.** List an idea here only if it
  changed the shape of the problem - a different lifecycle unit, a different owner,
  a different question - rather than offering another way to build the same thing.
  One or two entries, none if the debate produced none. If a killed idea's strongest
  case is "it is cheaper", it belongs in Concepts as a losing option. The transcript
  already holds every rejected idea; this section is for the one that should have
  been harder to reject than it was.
      Wrong: "API-first architecture (lost 3-1-1): strongest case was long-term
    sustainability. Lost because cold-start means identical accuracy for 4-5x effort."
    That is another way to build the same thing - it belongs in Concepts as a losing
    option.

    Right: "Viewing session as the coupling unit: the estimate would be owned by video +
    region + viewer rather than by the video. Lost because observing the viewer makes us
    ad-tech. Would win if we ever had per-viewer data." That changes what the design is
    about.
- **Cons must be real.** "Slightly more code" is not a con.
- **Open questions get owners.** An unowned question is a question that dies here.
- **Under ~400 lines.** If it is longer, the brainstorm was too broad - split the topic.

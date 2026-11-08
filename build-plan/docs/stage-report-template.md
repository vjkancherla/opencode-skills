# Stage Report Template

Copy into the project as `docs/stages/TEMPLATE.md`. The implementing agent writes
`docs/stages/<stage>.md` when a stage ends. It is for a human who has not been watching
and does not want to read the code.

````md
# Stage <X> - <name>

## What works now

<Two to four sentences, in plain terms. What a person could do or see now that they could
not before this stage.>

## Steps

- [S<N> - <goal>](../steps/S<NN>.md)
- [S<N> - <goal>](../steps/S<NN>.md)

## Checks

`scripts/checkpoint.sh all` - <N of N passed | which failed and what that means>

## Checks that changed

- <S04 - LOOSENED: no longer checks X, because Y. Covered instead by Z | not covered.>
- <S06 - corrected: expected the wrong port.>

<"None." if none.>

## Plan changes

- <merged / skipped / reordered, one line each, from the Changes log>

## Different from the design

- <anything built differently from the design note, and why. "Nothing." if nothing.>

## For you to decide

- <a question only the human can answer, with the options. "Nothing." if nothing.>

## Review

Different model, new session:

    Read and follow docs/REVIEW-PROMPT.md for <first sha of the stage>..<last sha>
````

## Rules

- **One screen.** If it is longer, it is too detailed.
- **Plain terms, no code, no file lists.** Name things by what they do. A technical term
  the human has not used gets a few words of explanation or gets replaced.
- **Link every step's summary; do not repeat them.** The diagrams and the detail of what
  changed live in `docs/steps/`. This report is what is true of the stage as a whole.
- **Every loosened check is listed, with whether something else now covers it.** This is
  the section the human should read even if they read nothing else.
- **Fill in the review line's commit range.** The human pastes it as it stands.
- **No selling.** If a check is weak or something was left rough, it goes under
  "Different from the design" or "For you to decide", not left out.

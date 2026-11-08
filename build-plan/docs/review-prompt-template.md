You are reviewing work you did not do and have no stake in.

A different model implemented the steps in the commit range you were given, working
unattended, and wrote the checkpoints for them as well. Nobody else has read this code.
Find what is wrong. Do not fix anything, and do not edit any file except your findings file.

## Read

- `docs/design/` - the current design note, including its Verification table
- `docs/build-plan.md` - the steps in this range, and the **Changes** log at the bottom
- `docs/stages/` and `docs/steps/` - the implementer's report for this stage and its
  summary of each step. These are what the human read instead of the code. They are
  claims, not evidence.
- `git diff <range>` and `git log --oneline <range>`
- `scripts/checks/` and `evidence/` for those steps

## Run

    scripts/checkpoint.sh all

## Answer

1. **Does every checkpoint in range pass for you?** A pass that only worked on leftover
   state is a finding.
2. **Would each checkpoint still pass if the step's core logic were stubbed out?** Name any
   that would.
3. **Was any checkpoint loosened in this range?** Read `git log -p -- scripts/checks/`.
   For each: is it marked LOOSENED in the Changes log, is it in the stage report, and was
   it justified? An unmarked loosening is a must-fix.
4. **Where does the code disagree with the design?** Quote both.
5. **What does the design require that is not there, and what is there that the design
   does not mention?**
6. **Do the step summaries and the stage report describe what the code actually does?**
   Check each diagram against the real call flow. Name anything overstated, left out, or
   still describing an intent that the build did not follow.
7. **What failure would you try first if you wanted this to misbehave?**
8. **Could someone who did not write this maintain it?** One line.

## Output

Write `docs/reviews/<last sha in the range>.md`:

    # Review of <range>

    Reviewer model: <name>

    ## In plain terms
    <three or four sentences a non-reader of the code can act on: is it sound, and what
    is the one thing to deal with first.>

    ## Must fix
    <file, line, what is wrong, what the design says instead. Do not write the fix.>

    ## Worth considering

    ## Checkpoints
    <what you ran, the result, and which checks are weak.>

If you find nothing, say what you checked. "Looks good" is not a review.

# Interrogation

The questions that turn a chosen concept into a design worth building. Ask them before
writing the design note, after grounding.

## How to ask

- **Three questions per turn, maximum.** Usually one. A wall of questions gets skimmed
  and answered carelessly, which is worse than not asking.
- **Never ask what grounding already answered.** Read the repo first. Asking someone to
  tell you what is in their own README is how a skill gets ignored.
- **Offer options where you can.** "Is X owned by A, B, or something else?" is easier to
  answer than "what owns X?" and produces a sharper answer.
- **Say why you are asking** when the reason is not obvious. One clause.
- **Stop when the answers stop changing the design.** This is not a form to complete.
- **Ask follow-ups immediately.** If an answer opens a hole, ask about the hole now, not
  three questions later.

## When an answer breaks the design

Say so in the same turn, plainly, and name what has to change:

> That changes the shape - if tenants can't edit namespaces, the annotation surface in
> the brainstorm's concept doesn't work. Two options: <A> or <B>.

Do not quietly redesign around it. Do not carry on and mention it in the design note.
The point of asking early is that a break here is cheap.

## The bank

Work down it. Skip anything already settled.

### 1. Ownership and lifecycle

The load-bearing question in most designs. Do not leave this one implicit.

- What object's lifetime does this attach to, and why that one?
- What else could own it? Why does that alternative lose?
- What happens to the thing you create when that owner is deleted by accident?
- Is that owner a stable identity, or something that gets replaced routinely?

**Done when** the answer has a named alternative and a reason it lost.

### 2. Authority and access

Cheap to ask, and it invalidates whole designs. Ask it early.

- Who can create and edit the object carrying the configuration - the same people who
  use it, or a platform team?
- Who can delete it?
- Which parts of this are already managed by someone else?

### 3. Requirement fidelity

- Does the chosen concept still do what was originally asked? Say plainly if it does
  not.
- Is there a case that the original requirement is wrong for some part of the scope?
- What would make this obviously not worth building?

### 4. Blast radius and irreversibility

- What here holds data or state that cannot be recreated?
- Which single command could destroy it, and who can run that command?
- Should everything in scope get the same treatment, or does some subset need
  different handling?

### 5. Impact on what already exists

- What does this change break that currently works?
- Which existing tests, scripts or manifests assume something this invalidates?
- Is anything being moved rather than added? Moving is where the cost hides.

### 6. Precedent

- Have you built something like this before, in this org or another repo?
- Is there a working example of the risky part anywhere you can point at?

A precedent in the user's own repos is worth more than any reasoning about whether
something will work. Ask for the link and read it.

### 7. Verification

- How would you know this works? What would convince someone who doubts it?
- What is the one check that, if it passed, would make you believe the whole thing?
- What would you demo?

**Done when** you can write a numbered verification table without inventing anything.

### 8. Scope

- What is explicitly out for this iteration?
- What is the smallest version that still proves the idea?
- How much time is this worth?

## Closing

When the bank is exhausted or the answers stop moving anything, summarise in three or
four lines: the decisions taken, and any that are still open. Get confirmation, then
write the artefacts.

If a decision is still open at that point, it goes in the design note's **Open
questions** with an owner - not silently defaulted.

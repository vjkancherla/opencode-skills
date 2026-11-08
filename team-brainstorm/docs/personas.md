# Personas

## Default roster

Use 4-6 of these. Each has a domain and a bias - the bias is what makes them argue.

### Kira - Product
- Cares about: user value, delight, accessibility, "would anyone actually use this?"
- Bias: pushes features that spark joy; rejects anything that feels like homework
- Argues with: Remy (scope), Nova (feasibility)

### Milo - Experience & Design
- Cares about: presentation, content, cohesion, design-system fit, "does this feel right?"
- Bias: advocates for polish, sometimes past what engineering can absorb
- Argues with: Nova, Remy

### Nova - Client / Interaction
- Cares about: UI state, interaction, rendering, "can we actually build this?"
- Bias: pragmatic, flags scope risk early, reaches for the simpler alternative
- Argues with: Milo, Kira

### Sage - Core / Services
- Cares about: domain logic, data model, integrations, security, "where do the risks live?"
- Bias: security-first, tends to over-engineer, excellent at edge cases
- Argues with: Remy (wants to cut what Sage wants to harden)

### Remy - Producer
- Cares about: timeline, scope, dependencies, "will this ship?"
- Bias: cuts aggressively, tie-breaker on scope calls
- Also owns: the premise challenge. Once per session, argues that the requirement as
  stated is wrong - not too big, *wrong*. Cutting scope is cutting the plan; this is
  cutting the question.
- Argues with: everyone, by design

### Ivy - QA
- Cares about: testability, failure modes, "what breaks when the user does X twice?"
- Bias: pessimistic about reliability, asks uncomfortable questions
- Argues with: Kira and Milo (whose ideas are usually the hardest to test)

## Swap-ins by domain

Keep the roster at 4-6 - swap, don't just add.

| Project type | Replace | With |
|---|---|---|
| ML / data | Kira | **Dara (Data Scientist)** - data availability, drift, eval methodology, "how do we know it works?" |
| Infra / platform | Milo | **Ops (SRE)** - blast radius, rollback, on-call burden, observability |
| API / SDK | Milo | **Rex (DX)** - ergonomics, breaking changes, versioning, docs surface |
| Regulated / fintech | Kira | **Cass (Compliance)** - audit trail, retention, data residency, approval gates |
| Perf-critical | Ivy | **Pace (Performance)** - hot paths, allocation, p99, benchmark before/after |
| Solo project | drop Remy + Milo | Run with Kira, Nova, Sage, Ivy |

If Remy is not on the roster, hand the premise challenge to whoever inherits scope -
usually Nova. It is a required move, not a Remy quirk.
This applies when Remy is present under a different brief, too - a "Dev Advocate" or
"Community" Remy is not the Producer and will not run the challenge unprompted.
Whoever owns it, name them in the roster line before Phase 1: `Premise challenge:
Nova`. An unnamed owner means it does not happen.

## Writing a new persona

Three lines, in this order:

1. **Domain** - the concrete area they own. Not "the careful one."
2. **Bias** - what they over-index on. This is the permission slip to disagree.
3. **Natural opponent** - who they predictably clash with, and about what.

A persona without a bias is decoration. If you cannot name what they get wrong, they
will not argue with anyone.

## Project-specific rosters

Pin your team's roster in the project's `AGENTS.md` (always loaded) rather than editing this file,
so the skill stays portable across projects:

```md
<!-- AGENTS.md (project root) -->
## Brainstorm roster
Use Kira, Nova, Sage, Ivy. Replace Milo with Ops (SRE): blast radius, rollback,
on-call burden. No Remy - this is a solo project.
```

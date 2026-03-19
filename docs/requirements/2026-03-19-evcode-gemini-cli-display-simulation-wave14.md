# EvCode Gemini CLI Display Simulation Wave14 Requirement

## Goal

Simulate a real interactive CLI run and verify whether the current design-oriented Gemini invocation behaves normally and whether Gemini is displayed correctly in the CLI actor surface.

## Deliverable

- Captured interactive CLI output from a real TTY run or trace view
- Cross-check between CLI-visible actor display and saved runtime artifacts
- A conclusion about whether Gemini display is normal in the current CLI surface

## Constraints

- Prefer real TTY behavior over JSON-only inspection.
- Preserve the same frontend-visual task shape that should route to Gemini.
- Keep evidence grounded in saved runtime artifacts and terminal output.

## Acceptance Criteria

- A real TTY invocation is executed.
- The CLI-visible output mentions or renders Gemini in a way consistent with runtime artifacts.
- The conclusion distinguishes between provider health, routing correctness, and CLI display correctness.

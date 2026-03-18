# Governed Requirement

## Goal

Plan a realistic, governed validation of EvCode's current multi-assistant design using real Claude and Gemini API calls, with simulation paths that mirror actual user behavior rather than isolated unit checks.

## Deliverable

A verification plan that tests whether the current EvCode design is good enough for practical use by checking:
- standard CLI behavior with real provider-backed Claude and Gemini advisory calls
- benchmark CLI behavior with expected specialist suppression
- real user-like tasks across planning, frontend visual work, and mixed UI collaboration
- artifact traceability from requirement to routing receipts to cleanup receipts
- realistic failure handling when external providers misbehave or return degraded outputs

## Constraints

- Keep Codex as the only final execution authority.
- Preserve the governed runtime stage order and artifact contract.
- Use real Claude and Gemini API calls for the standard channel validation.
- Do not claim local CLI integration if the actual implementation path is API-backed rather than shelling out to separate Claude/Gemini binaries.
- Treat benchmark-channel specialist suppression as a feature to validate, not a bug to bypass.
- Avoid storing or echoing live secrets in tracked files or validation docs.

## Acceptance Criteria

- The plan covers both standard and benchmark entrypoints.
- The plan includes at least one real Claude planning/documentation scenario.
- The plan includes at least one real Gemini frontend-visual scenario.
- The plan includes at least one mixed task that checks routing quality and Codex-owned completion semantics.
- The plan includes explicit evidence artifacts, rollback criteria, and failure-mode checks.
- The plan is executable without widening the current runtime architecture.

## Non-Goals

- Re-architecting providers during this validation turn.
- Claiming support for arbitrary OpenAI-compatible vendors beyond the already documented current boundary.
- Converting API-backed specialists into local CLI-backed specialists in this task.

## Assumptions

- The user wants a practical qualification plan before deciding whether the design is production-credible.
- The meaningful realism test is governed runtime behavior under actual provider responses, not only direct single-request smoke calls.
- Benchmark suppression must remain intact during validation.

## Runtime Mode

- mode: `interactive_governed`
- profile: `standard`
- channel: `standard`

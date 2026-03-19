# EvCode Claude Gemini Capability Clarification Wave8 Requirement

## Goal

Clarify why a prior answer said Claude and Gemini could not be directly called, and distinguish between the current Codex chat session capabilities versus EvCode runtime capabilities.

## Deliverable

- A precise explanation of the capability boundary
- Evidence from current EvCode status/config/runtime code
- Governed trace artifacts for this clarification turn

## Constraints

- Do not change product behavior in this turn.
- Base the explanation on repository-local evidence and fresh status output.
- Preserve governed runtime traceability.

## Acceptance Criteria

- Explain the difference between chat-environment tools and EvCode runtime providers.
- State whether EvCode is configured for Claude/Gemini and under what conditions live invocation works.
- Record proof and cleanup receipts.

## Non-Goals

- Reconfigure provider keys.
- Trigger live Claude or Gemini calls.

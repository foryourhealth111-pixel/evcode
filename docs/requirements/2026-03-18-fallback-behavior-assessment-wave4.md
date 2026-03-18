# Fallback Behavior Assessment Wave4 Requirement

## Goal

Verify whether EvCode can safely fall back to Codex-led execution when Claude fails at runtime.

## Deliverable

A fresh governed execution sample, a concise assessment of fallback behavior, and proof/cleanup receipts.

## Constraints

- Do not modify routing or provider policy in this assessment.
- Use explicit live env only for the verification run.
- Preserve benchmark suppression rules.
- Preserve unrelated local changes.

## Acceptance Criteria

- A fresh standard-channel run that requests Claude is executed.
- Evidence shows whether Codex remains the final executor after Claude failure.
- The assessment explains what still degrades when fallback occurs.

## Non-Goals

- Repairing the external Claude provider.
- Broad code changes.
- Making claims without fresh evidence.

# Non-Silent Fallback Warning Wave5 Requirement

## Goal

Ensure EvCode does not silently fall back to Codex when a specialist CLI/provider fails. The user should be explicitly told that a specialist path failed and that execution is continuing in degraded Codex-led mode.

## Deliverable

A code change that surfaces fallback warnings to users and receipts, plus fresh verification evidence and cleanup artifacts.

## Constraints

- Preserve current Codex takeover behavior.
- Preserve benchmark specialist suppression.
- Do not require the external provider to succeed in order to verify the warning path.
- Preserve unrelated local changes.

## Acceptance Criteria

- A fresh specialist failure is visible in runtime summary or equivalent user-facing output rather than being silent.
- Degradation is reflected in receipts/summaries, not only deep specialist result files.
- Targeted tests and a fresh run confirm the behavior.

## Non-Goals

- Repairing the external Claude provider.
- Changing the fallback owner away from Codex.

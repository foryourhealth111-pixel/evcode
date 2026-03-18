# Governed Requirement

## Goal

Add a lightweight provider probe surface so users can validate the currently configured assistant `key`, `url`, and `model` values without expanding EvCode into a heavy provider orchestration layer.

## Deliverable

A minimal CLI-visible provider probe that:
- reports the current configured assistant-provider resolution
- can perform live compatibility checks against the configured assistant API surfaces
- preserves governed defaults and benchmark suppression policy
- keeps the implementation narrow and easy to reason about

## Constraints

- Do not redesign the runtime around provider auto-negotiation.
- Do not store secrets in tracked files.
- Keep the probe output JSON-first and small.
- Avoid introducing a second routing authority or a persistent provider registry.

## Acceptance Criteria

- `evcode` exposes a provider probe command.
- `evcode-bench` exposes the same command against benchmark policy.
- The probe reports whether each configured assistant is enabled, skipped, or live-compatible.
- The probe can run safely without credentials and return actionable non-live statuses.
- Tests cover the non-live probe path.

## Non-Goals

- Full automatic provider fallback or schema negotiation during task execution.
- Background health daemons or persistent probe caches.
- Replacing the governed assistant-policy defaults.

## Assumptions

- A narrow explicit probe command is the right next step for usability without bloating runtime behavior.
- Users prefer a real validation command over only reading docs or status metadata.

## Runtime Mode

- mode: `interactive_governed`
- profile: `standard`
- channel: `standard`

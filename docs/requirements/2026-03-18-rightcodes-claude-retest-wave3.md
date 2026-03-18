# RightCodes Claude Retest Wave3 Requirement

## Goal

Retest the RightCodes Claude integration with fresh governed evidence to determine whether the current failures are transient flakiness or still reproducible blocking behavior.

## Deliverable

A governed retest package containing repeated live Claude probes, repeated standard-channel Claude-requesting governed runs, a concise proof summary, and mandatory cleanup receipts.

## Constraints

- Keep offline gate behavior unchanged.
- Use the existing explicit live env only for the retest.
- Preserve Codex final authority and benchmark specialist suppression.
- Preserve unrelated local changes.
- Audit node/codex processes without terminating long-lived unrelated sessions.

## Acceptance Criteria

- Fresh Claude probes are run multiple times against the configured RightCodes endpoint.
- A targeted governed standard-channel run that requests Claude is re-executed with fresh evidence.
- The retest clearly states whether Claude succeeds intermittently, fails consistently, or shows mixed endpoint behavior.
- Proof and cleanup artifacts are written under the new run id.

## Non-Goals

- Modifying provider policy or benchmark routing.
- Claiming a fix without fresh passing evidence.
- Refactoring unrelated code paths.

## Source References

- `docs/status/evcode-gate-integration-live-hybrid-wave2-proof.md`
- `docs/status/evcode-gate-integration-live-hybrid-wave2-report.json`

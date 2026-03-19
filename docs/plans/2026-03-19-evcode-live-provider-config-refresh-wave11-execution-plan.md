# EvCode Live Provider Config Refresh Wave11 Execution Plan

## Requirement Source

- `docs/requirements/2026-03-19-evcode-live-provider-config-refresh-wave11.md`

## Internal Grade

- `M`

## Waves

1. Confirm current provider-env resolution state and identify blocking prerequisites.
2. Write a repo-local provider override file using the updated Claude endpoint and live-specialist opt-in.
3. Refresh tracked examples and setup docs so contributor guidance matches the current live endpoint.
4. Run `status` and provider probes; capture proof with explicit distinction between configuration readiness and authenticated live verification.
5. Emit proof summary and rely on governed phase cleanup receipts.

## Verification Commands

- `node apps/evcode/bin/evcode.js status --json`
- `node apps/evcode/bin/evcode.js probe-providers --json`
- `node apps/evcode/bin/evcode.js probe-providers --json --live`

## Rollback Rules

- If the local provider override produces an invalid status surface, remove `config/assistant-providers.env.local` and return to tracked defaults.
- Do not overwrite any existing secret-bearing env file outside the repo.

## Phase Cleanup Expectations

- No temp artifacts beyond proof docs.
- No node process cleanup expected unless probes spawn residue.

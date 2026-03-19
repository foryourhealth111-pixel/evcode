# EvCode Claude Gemini Capability Clarification Wave8 Execution Plan

## Requirement Source

- `docs/requirements/2026-03-19-evcode-claude-gemini-capability-clarification-wave8.md`

## Internal Grade

- `M`

## Waves

1. Capture fresh `evcode status --json` evidence.
2. Inspect assistant policy and runtime bridge code paths.
3. Explain the boundary between current assistant tools and EvCode runtime providers.
4. Emit proof and cleanup receipts.

## Verification Commands

- `evcode status --json`
- `sed -n ... apps/evcode/bin/evcode.js`
- `sed -n ... scripts/runtime/runtime_lib.py`
- `sed -n ... config/assistant-policy.standard.json`

## Rollback Rules

- No code changes in this wave, so no rollback action required.

## Phase Cleanup Expectations

- Leave only trace artifacts for this clarification wave.
- Audit only; no process cleanup required.

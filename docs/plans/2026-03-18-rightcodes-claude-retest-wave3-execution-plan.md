# RightCodes Claude Retest Wave3 Execution Plan

## Requirement Source

- `docs/requirements/2026-03-18-rightcodes-claude-retest-wave3.md`

## Internal Grade

- `M`

## Waves

1. Recreate governed receipts and log roots for the retest.
2. Run repeated Claude live probes against `/claude/v1` and `/claude`.
3. Run repeated standard-channel governed tasks that request Claude.
4. Compare outcomes and error signatures.
5. Emit proof and cleanup receipts.

## Verification Commands

- `python3 scripts/verify/probe_assistant_providers.py --repo-root /home/lqf/table/table3 --channel standard --json --live`
- `node apps/evcode/bin/evcode.js run --task "Plan the product architecture and UX workflow for an ambiguous redesign" --artifacts-root <temp> --run-id <id>`
- `python3 scripts/verify/run_live_hybrid_validation.py --repo-root /home/lqf/table/table3 --json` (optional comparison snapshot)

## Rollback Rules

- If Claude still fails, record the exact provider evidence and do not change offline gates.
- If Claude passes intermittently, report the pass/fail ratio and keep the result scoped to empirical evidence only.

## Phase Cleanup Expectations

- Archive retest logs inside the repo-owned run directory.
- Remove `/tmp` retest roots after archiving.
- Audit node/codex processes without killing unrelated sessions.

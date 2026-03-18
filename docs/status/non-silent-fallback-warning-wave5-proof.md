# Non-Silent Fallback Warning Wave5 Proof

## Scope

This proof closes the 2026-03-18 wave that changed specialist/provider fallback from silent degradation into explicit user-visible warning behavior while preserving Codex takeover safety.

## Verdict

This wave is verified.
When a specialist/provider fails, EvCode now does three things that it did not do honestly enough before:

- emits a top-level warning in the runtime summary,
- marks the execution outcome as `degraded_fallback_to_codex`,
- prints a warning to stderr in the `evcode run` CLI path so the user is explicitly told a specialist path failed.

Codex remains the final executor.

## Commands Executed

- `python3 -m pytest tests/test_app_entrypoints.py tests/test_runtime_bridge.py tests/test_specialist_routing.py -q` -> exit 0 | evidence: `19 passed in 0.97s`
- `python3 scripts/verify/check_contracts.py` -> exit 0 | evidence: `contract checks: ok`
- `node apps/evcode/bin/evcode.js run --task "Plan the product architecture and UX workflow for an ambiguous redesign" --artifacts-root /tmp/evcode-non-silent-fallback-wave5/run --run-id warning-fallback-fresh` with a deliberately failing local Claude URL -> exit 0 | evidence files: `/home/lqf/table/table3/outputs/runtime/vibe-sessions/2026-03-18-non-silent-fallback-warning-wave5/logs/fresh-run.stdout.json`, `/home/lqf/table/table3/outputs/runtime/vibe-sessions/2026-03-18-non-silent-fallback-warning-wave5/logs/fresh-run.stderr.txt`, `/home/lqf/table/table3/outputs/runtime/vibe-sessions/2026-03-18-non-silent-fallback-warning-wave5/logs/fresh-run-summary.json`

## Fresh Behavior Change

The fresh run now shows:

- top-level `execution_outcome: degraded_fallback_to_codex`
- top-level `warnings` containing the failed assistant and reason
- `specialist_routing.degraded_delegates` including `claude`
- `codex_integration_receipt.degraded_specialists` including `claude`
- a visible stderr line: `Warning: claude specialist/provider failed; continuing in Codex-led degraded mode.`

## Why This Matters

Previously, the specialist result file knew about provider failure, but the user-facing summary path could still look too clean.
Now the user gets an explicit reminder that the specialist/CLI path had a problem and that execution is continuing in degraded Codex-led mode.
That satisfies the non-silent fallback requirement without changing takeover ownership.

## Cleanup And Artifact Preservation

- Repo-owned evidence was preserved under `/home/lqf/table/table3/outputs/runtime/vibe-sessions/2026-03-18-non-silent-fallback-warning-wave5`.
- Fresh temp run artifacts were archived under `/home/lqf/table/table3/outputs/runtime/vibe-sessions/2026-03-18-non-silent-fallback-warning-wave5/live-warning-artifacts/fresh-run`.
- The temp root `/tmp/evcode-non-silent-fallback-wave5` was removed after archiving.
- Node processes were audited only and not terminated. Evidence: `/home/lqf/table/table3/outputs/runtime/vibe-sessions/2026-03-18-non-silent-fallback-warning-wave5/logs/node-process-audit.txt`.


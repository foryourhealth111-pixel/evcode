# Fallback Behavior Assessment Wave4 Proof

## Scope

This proof answers one operational question: when Claude fails at runtime, does EvCode correctly fall back to Codex-led execution?

## Verdict

Yes, functionally it does.
A fresh standard-channel governed run requested Claude, Claude failed with a provider 403, and the governed runtime still kept Codex as the final executor.
So the takeover path works.
What degrades is specialist assistance quality, not control-plane ownership.

There is one observability caveat:
`degraded_delegates` remained empty in the routing summary even though the Claude specialist result ended as `provider_failure`.
That does not break fallback itself, but it means the degradation ledger is not fully honest yet.

## Fresh Evidence

- Fresh run command: `node apps/evcode/bin/evcode.js run --task "Plan the product architecture and UX workflow for an ambiguous redesign" --artifacts-root /tmp/evcode-fallback-assessment-wave4/run --run-id fallback-assessment-fresh --json`
- Fresh summary: `/home/lqf/table/table3/outputs/runtime/vibe-sessions/2026-03-18-fallback-behavior-assessment-wave4/logs/fresh-run-summary.json`
- Runtime summary: `/tmp/evcode-fallback-assessment-wave4/run/outputs/runtime/vibe-sessions/fallback-assessment-fresh/runtime-summary.json`
- Claude result: `/tmp/evcode-fallback-assessment-wave4/run/outputs/runtime/vibe-sessions/fallback-assessment-fresh/specialists/claude-result.json`
- Codex integration receipt: `/tmp/evcode-fallback-assessment-wave4/run/outputs/runtime/vibe-sessions/fallback-assessment-fresh/specialists/codex-integration-receipt.json`
- Execute receipt: `/tmp/evcode-fallback-assessment-wave4/run/outputs/runtime/vibe-sessions/fallback-assessment-fresh/phase-execute.json`
- Cleanup receipt: `/tmp/evcode-fallback-assessment-wave4/run/outputs/runtime/vibe-sessions/fallback-assessment-fresh/cleanup-receipt.json`

## What The Fresh Run Proved

- Routing still requested Claude for the planning task.
- Claude returned `provider_failure` with the same RightCodes 403 signature.
- `claude-result.json` explicitly set `recommended_next_actor` to `codex`.
- `codex-integration-receipt.json` explicitly kept `final_executor` as `codex`.
- The governed run completed and emitted its own cleanup receipt.

## Practical Meaning

When Claude is unavailable:

- EvCode does not hand ownership to a broken specialist.
- Codex keeps execution authority and can continue carrying the task.
- The system becomes less capable on planning/design specialization, but it does not become leaderless.

## Residual Risk

- The fallback works at execution level.
- The degradation telemetry is slightly inconsistent because `degraded_delegates` stayed empty while the specialist result clearly failed.
- That inconsistency should be fixed if you want operator dashboards and receipts to reflect reality exactly.

## Cleanup And Artifact Preservation

- Repo-owned evidence was preserved under `/home/lqf/table/table3/outputs/runtime/vibe-sessions/2026-03-18-fallback-behavior-assessment-wave4`.
- Fresh temp artifacts were archived under `/home/lqf/table/table3/outputs/runtime/vibe-sessions/2026-03-18-fallback-behavior-assessment-wave4/live-assessment-artifacts/fresh-run`.
- The temp root `/tmp/evcode-fallback-assessment-wave4` was removed after archiving.
- The fresh governed run's own cleanup receipt reported `cleanup_status: ok`.


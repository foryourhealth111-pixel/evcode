# EvCode Gate Integration And Live Hybrid Validation Proof

## Scope

This proof closes the 2026-03-18 wave that promoted offline hybrid baseline and distribution-portability validators into EvCode's formal gate surfaces, added a live opt-in hybrid validator, and verified the resulting check surfaces end to end.

## Verdict

The code and gate integration portion of this wave is verified.
Default offline verification now includes the formal baseline-family and distributed-install portability validators, package-level `npm run check` passes, and the live validator executes real provider traffic when explicit env is supplied.
The external live-provider outcome is not a clean pass: Codex and Gemini are live-compatible on RightCodes, while Claude currently fails with HTTP 403 on both `https://right.codes/claude/v1` and `https://right.codes/claude`.
That Claude failure is an external provider-compatibility finding, not a failure of the new gate integration itself.

## Commands Executed

- `python3 -m pytest tests/test_live_hybrid_validation.py tests/test_hybrid_baseline.py tests/test_distribution_portability.py tests/test_contracts.py tests/test_app_entrypoints.py -q` -> exit 0 | evidence: `16 passed in 2.08s` | file: `/home/lqf/table/table3/outputs/runtime/vibe-sessions/2026-03-18-evcode-gate-integration-live-hybrid-wave2/logs/targeted-pytest.txt`
- `python3 scripts/verify/check_contracts.py` -> exit 0 | evidence: `contract checks: ok` | file: `/home/lqf/table/table3/outputs/runtime/vibe-sessions/2026-03-18-evcode-gate-integration-live-hybrid-wave2/logs/check-contracts.txt`
- `python3 scripts/verify/run_hybrid_baseline.py --repo-root /home/lqf/table/table3 --json` -> exit 0 | evidence file: `/home/lqf/table/table3/outputs/runtime/vibe-sessions/2026-03-18-evcode-gate-integration-live-hybrid-wave2/logs/hybrid-baseline.json`
- `python3 scripts/verify/validate_distribution_portability.py --repo-root /home/lqf/table/table3 --json` -> exit 0 | evidence file: `/home/lqf/table/table3/outputs/runtime/vibe-sessions/2026-03-18-evcode-gate-integration-live-hybrid-wave2/logs/distribution-portability.json`
- `npm run check` -> exit 0 | evidence: `67 tests passed via npm run check` | file: `/home/lqf/table/table3/outputs/runtime/vibe-sessions/2026-03-18-evcode-gate-integration-live-hybrid-wave2/logs/npm-run-check.txt`
- `python3 scripts/verify/probe_assistant_providers.py --repo-root /home/lqf/table/table3 --channel standard --json --live` with `EVCODE_CLAUDE_BASE_URL=https://right.codes/claude/v1` -> exit 0 | Claude evidence: `provider_http_error:403:{"error":{"message":"openai_error","type":"bad_response_status_code","param":"","code":"bad_response_status_code"}}` | file: `/home/lqf/table/table3/outputs/runtime/vibe-sessions/2026-03-18-evcode-gate-integration-live-hybrid-wave2/logs/live-probe-claude-v1.json`
- `python3 scripts/verify/probe_assistant_providers.py --repo-root /home/lqf/table/table3 --channel standard --json --live` with `EVCODE_CLAUDE_BASE_URL=https://right.codes/claude` -> exit 0 | Claude evidence: `provider_http_error:403:error code: 1010` | file: `/home/lqf/table/table3/outputs/runtime/vibe-sessions/2026-03-18-evcode-gate-integration-live-hybrid-wave2/logs/live-probe-claude-no-v1.json`
- `python3 scripts/verify/run_live_hybrid_validation.py --repo-root /home/lqf/table/table3 --json` with live env -> exit 1 | evidence file: `/home/lqf/table/table3/outputs/runtime/vibe-sessions/2026-03-18-evcode-gate-integration-live-hybrid-wave2/logs/live-hybrid-validation.json`

## What Passed

- `package.json` now wires offline baseline-family and distributed-install validators into the formal `check` path, and the release workflow mirrors the same offline-only safety posture.
- `scripts/verify/check_contracts.py` now enforces baseline-family profile bindings and the presence of the new verification/config surfaces.
- The offline hybrid baseline validator passes, proving standard `hybrid_governed` behavior and benchmark `core_benchmark` suppression behavior under the formal baseline-family model.
- The distributed-install portability validator passes, proving external-workspace startup and portable config resolution remain path-independent.
- Package-level `npm run check` passes end to end after this wave restored the repository's missing `apps/site` static Product Preview contract required by `tests/test_marketing_site.py`.
- The live validator does execute real governed traffic when env is supplied and preserves Codex final authority plus benchmark specialist suppression, even when a provider fails.

## Live Provider Findings

- Codex probe: live-compatible.
- Gemini probe: live-compatible on `https://right.codes/gemini/v1` with model `gemini-2.5-pro`.
- Claude probe with `/claude/v1`: fails with `provider_http_error:403:{"error":{"message":"openai_error","type":"bad_response_status_code","param":"","code":"bad_response_status_code"}}`.
- Claude probe without `/v1`: still fails with `provider_http_error:403:error code: 1010`.
- Live governed standard runs confirm the same pattern: Claude degrades back to Codex, while Gemini can return live advisory output. Benchmark control still suppresses both specialists.

## Residual Notes

- The live hybrid validator is intentionally outside default CI and default `npm run check`; the offline gate remains deterministic.
- The remaining blocker to a fully passing live hybrid proof is the current external Claude compatibility on RightCodes, not repo-local routing/governance logic.
- Gemini advisory output remains real but should still be treated as advisory-only; Codex remains the final integrator and verifier.

## Cleanup And Artifact Preservation

- Repo-owned evidence was preserved under `/home/lqf/table/table3/outputs/runtime/vibe-sessions/2026-03-18-evcode-gate-integration-live-hybrid-wave2`.
- The latest live validation temp tree was archived under `/home/lqf/table/table3/outputs/runtime/vibe-sessions/2026-03-18-evcode-gate-integration-live-hybrid-wave2/live-validation-artifacts/rightcodes-run-latest` before cleanup.
- Node and Codex processes were audited only and intentionally not terminated. Evidence: `/home/lqf/table/table3/outputs/runtime/vibe-sessions/2026-03-18-evcode-gate-integration-live-hybrid-wave2/logs/node-process-audit.txt`.


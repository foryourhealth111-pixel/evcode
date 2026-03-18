# EvCode Hybrid Baseline Family And Distributed Install Validation Proof

## Scope

This proof closes the wave that formalizes EvCode baseline families and validates broad-distribution path portability on 2026-03-18.
The verified surfaces were baseline-family contract exposure in status/probe outputs, offline hybrid-vs-core baseline verification, and external-path startup/config behavior from a distributed-install perspective.

## Verdict

This wave is verified.
EvCode now exposes a formal `hybrid_governed` baseline family for standard governed mixed-assistant coverage and a separate `core_benchmark` family for the Codex-only benchmark lane. The benchmark line remains specialist-suppressed, and the product now has a repeatable validator proving that both source-mode and assembled launchers can run from an external workspace while portable unified configuration is resolved from an external config root.

## Commands Executed

- `python3 -m pytest tests/test_hybrid_baseline.py tests/test_distribution_portability.py tests/test_specialist_routing.py tests/test_app_entrypoints.py tests/test_contracts.py -q` -> exit 0 | evidence: `21 passed in 2.03s`
- `python3 -m pytest tests/test_portable_paths.py tests/test_benchmark_artifact_contract.py tests/test_distribution_portability.py tests/test_hybrid_baseline.py tests/test_specialist_routing.py tests/test_app_entrypoints.py tests/test_runtime_bridge.py tests/test_assistant_adapters.py tests/test_contracts.py -q` -> exit 0 | evidence: `38 passed in 2.38s`
- `node apps/evcode/bin/evcode.js status --json` -> exit 0 | evidence: `/home/lqf/table/table3/outputs/runtime/vibe-sessions/2026-03-18-evcode-hybrid-baseline-distribution-wave1/logs/evcode-status.json`
- `node apps/evcode-bench/bin/evcode-bench.js status --json` -> exit 0 | evidence: `/home/lqf/table/table3/outputs/runtime/vibe-sessions/2026-03-18-evcode-hybrid-baseline-distribution-wave1/logs/evcode-bench-status.json`
- `node apps/evcode/bin/evcode.js probe-providers --json` -> exit 0 | evidence: `/home/lqf/table/table3/outputs/runtime/vibe-sessions/2026-03-18-evcode-hybrid-baseline-distribution-wave1/logs/evcode-probe.json`
- `node apps/evcode-bench/bin/evcode-bench.js probe-providers --json` -> exit 0 | evidence: `/home/lqf/table/table3/outputs/runtime/vibe-sessions/2026-03-18-evcode-hybrid-baseline-distribution-wave1/logs/evcode-bench-probe.json`
- `python3 scripts/verify/run_hybrid_baseline.py --repo-root /home/lqf/table/table3 --json` -> exit 0 | evidence: `/home/lqf/table/table3/outputs/runtime/vibe-sessions/2026-03-18-evcode-hybrid-baseline-distribution-wave1/logs/hybrid-baseline.json`
- `python3 scripts/verify/validate_distribution_portability.py --repo-root /home/lqf/table/table3 --json --keep-temp` -> exit 0 | evidence: `/home/lqf/table/table3/outputs/runtime/vibe-sessions/2026-03-18-evcode-hybrid-baseline-distribution-wave1/logs/distribution-portability.json`

## What Passed

- Standard and benchmark status surfaces now expose formal baseline-family membership and definition payloads. Standard reports `hybrid_governed`, and benchmark reports `core_benchmark`. Evidence: `/home/lqf/table/table3/outputs/runtime/vibe-sessions/2026-03-18-evcode-hybrid-baseline-distribution-wave1/logs/evcode-status.json` and `/home/lqf/table/table3/outputs/runtime/vibe-sessions/2026-03-18-evcode-hybrid-baseline-distribution-wave1/logs/evcode-bench-status.json`.
- Probe surfaces also expose baseline-family identity. This makes operator-level health output consistent with the new baseline-family contract. Evidence: `/home/lqf/table/table3/outputs/runtime/vibe-sessions/2026-03-18-evcode-hybrid-baseline-distribution-wave1/logs/evcode-probe.json` and `/home/lqf/table/table3/outputs/runtime/vibe-sessions/2026-03-18-evcode-hybrid-baseline-distribution-wave1/logs/evcode-bench-probe.json`.
- The hybrid baseline runner passes offline family assertions. It proves three standard-lane expectations and one benchmark-lane guard: backend/runtime tasks can remain Codex-only, planning tasks route to Claude, visual frontend tasks route to Gemini, and benchmark stays `codex_only_benchmark` with Claude and Gemini suppressed. Evidence: `/home/lqf/table/table3/outputs/runtime/vibe-sessions/2026-03-18-evcode-hybrid-baseline-distribution-wave1/logs/hybrid-baseline.json`.
- Distributed-install validation passes from an external workspace. Source-mode status can resolve portable unified configuration from an external `XDG_CONFIG_HOME`, and assembled standard/benchmark launchers can start from an empty external workspace while pointing `CODEX_HOME` and runtime roots at the assembled install tree rather than the repo path. Evidence: `/home/lqf/table/table3/outputs/runtime/vibe-sessions/2026-03-18-evcode-hybrid-baseline-distribution-wave1/logs/distribution-portability.json`.
- Fresh targeted and broader regressions both pass. Evidence: `21 passed in 2.03s` and `38 passed in 2.38s`.

## Residual Notes

- This wave formalizes the hybrid baseline family and external-path validation, but it does not make live specialist traffic part of the default baseline gate.
- The assembled launcher validation proves startup portability and path independence, not a full packaged installer flow.

## Cleanup And Artifact Preservation

- Repo-owned evidence was preserved under `/home/lqf/table/table3/outputs/runtime/vibe-sessions/2026-03-18-evcode-hybrid-baseline-distribution-wave1`.
- The external distributed-install validation temp root was removed after the JSON report was copied into the repo-owned session logs.
- Existing `node` and `codex` processes were audited only and intentionally left untouched. Evidence: `/home/lqf/table/table3/outputs/runtime/vibe-sessions/2026-03-18-evcode-hybrid-baseline-distribution-wave1/node-process-audit.txt`.

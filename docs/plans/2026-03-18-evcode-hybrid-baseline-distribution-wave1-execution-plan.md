# EvCode Hybrid Baseline Family And Distributed Install Validation Execution Plan

## Requirement Source

- `docs/requirements/2026-03-18-evcode-hybrid-baseline-distribution-wave1.md`

## Internal Grade

- `XL`

## Waves

1. Formalize baseline-family config and surface it through profile/status/probe contracts.
2. Add a dedicated hybrid baseline runner with offline route assertions and optional live smoke mode.
3. Add regression tests for baseline-family contracts and channel isolation.
4. Add distribution-style portability validation for external cwd, external config root, and assembled launchers.
5. Run focused tests, then broader regression and real validation scripts.
6. Emit proof docs, cleanup receipts, and node audit output.

## Ownership Boundaries

- Codex owns all code changes, receipt emission, verification, and cleanup.
- Claude and Gemini remain advisory-only in the hybrid family and are never granted repository mutation authority.
- Benchmark remains Codex-only regardless of hybrid baseline coverage.

## Verification Commands

- `python3 -m pytest tests/test_hybrid_baseline.py tests/test_specialist_routing.py tests/test_app_entrypoints.py tests/test_contracts.py -q`
- `python3 -m pytest tests/test_portable_paths.py tests/test_distribution_portability.py tests/test_runtime_bridge.py tests/test_assistant_adapters.py -q`
- `python3 scripts/verify/run_hybrid_baseline.py --repo-root /home/lqf/table/table3 --json`
- `python3 scripts/verify/validate_distribution_portability.py --repo-root /home/lqf/table/table3 --json`

## Rollback Rules

- If baseline-family surfacing changes benchmark semantics, revert to status-only reporting and keep benchmark routing untouched.
- If distribution validation requires product-scope packaging changes beyond this wave, keep the validator as proof-only and avoid widening the install surface.
- If live hybrid smoke proves flaky, keep the runner offline-first and gate live mode behind explicit opt-in.

## Phase Cleanup Expectations

- Remove temporary validation roots created outside the repo after preserving proof artifacts.
- Preserve repo-owned reports and session receipts.
- Audit node/codex processes; do not kill long-lived pre-existing sessions.

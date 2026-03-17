# EvCode VCO Upstream Refresh Execution Plan

Date: 2026-03-18

## Internal Grade

L

The refresh spans an embedded upstream snapshot plus local bridge, config, and test reconciliation. It is broader than a narrow one-file update, but still centered on one integration boundary rather than parallel product streams.

## Waves

### Wave 1

- inspect the local runtime lock, contract metadata, and bridge assumptions
- fetch the latest upstream VCO source into a temporary comparison directory
- identify version, commit, and file-level deltas that affect EvCode integration

### Wave 2

- refresh `runtime/vco` materialization from upstream
- update lock files, freshness/materialization metadata, and any version references required by the refreshed snapshot
- preserve EvCode-specific bridge invariants and reconcile any changed upstream files that EvCode depends on

### Wave 3

- adjust local configuration and bridge tests to match the refreshed runtime expectations
- update documentation or contract fixtures only where needed to preserve traceability and correctness

### Wave 4

- run targeted verification for runtime bridge, contract, distribution, and benchmark adapter surfaces
- inspect workspace state for leftover temporary artifacts
- record verification evidence and leave cleanup receipts in place before claiming completion

## Verification Commands

```bash
python3 scripts/verify/check_contracts.py
python3 scripts/verify/check_host_bridge.py
python3 -m pytest tests/test_runtime_bridge.py tests/test_contracts.py tests/test_distribution_assembly.py tests/test_hooks.py tests/test_benchmark_execution_bridge.py tests/test_benchmark_adapter.py tests/test_release_packages.py tests/test_host_bridge_analysis.py
```

## Rollback Rule

If the refreshed runtime introduces incompatible changes that cannot be reconciled without violating the governed runtime contract, revert the local runtime materialization and metadata updates together rather than carrying a partially integrated snapshot.

## Cleanup Expectation

- remove temporary upstream comparison directories and diff artifacts
- do not leave ad hoc debug files in the repository root
- keep planning files and governed runtime artifacts as intentional trace records

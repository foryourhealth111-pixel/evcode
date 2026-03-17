# EvCode VCO Upstream Refresh Requirement

Date: 2026-03-18

## Goal

Upgrade the embedded `runtime/vco` snapshot to the latest upstream VCO ecosystem state and bring EvCode bridge wiring, configuration, and tests into a verifiably passing state.

## Deliverables

- refreshed `runtime/vco` materialization from upstream main
- updated lock and contract metadata for the embedded runtime
- any required bridge/config adjustments so EvCode still honors governed runtime invariants
- updated tests and verification surfaces aligned with the refreshed runtime
- verification evidence showing the repository passes the relevant checks after the refresh

## Constraints

- preserve the governed runtime truth: one `vibe` entry, fixed 6-stage order, requirement freeze before execution, plan before execution, mandatory verification, mandatory cleanup
- keep standard and benchmark channels aligned with the same runtime core
- do not introduce a second router or wrapper-first control loop
- avoid unrelated refactors outside the runtime refresh and compatibility fixes required to keep EvCode correct
- work within the existing repository even if the worktree contains unrelated local modifications not created by this task

## Acceptance Criteria

- `runtime/vco` reflects the latest upstream main snapshot used for this refresh
- `config/sources.lock.json` and related runtime metadata point to the refreshed upstream commit and version information that can be justified from the mirrored source
- bridge/config behavior still enforces the governed runtime contract and any changed upstream expectations are reconciled locally
- repository tests and contract checks relevant to runtime, bridge, distributions, and benchmark adapters pass
- no temporary investigation artifacts remain unaccounted for at phase completion

## Non-Goals

- redesigning EvCode product architecture beyond what is required for compatibility with the refreshed VCO runtime
- changing the selected host baseline away from `stellarlinkco/codex`
- broad cleanup of unrelated upstream-bundled skill changes already present in the worktree

## Assumptions

- the latest upstream branch to track is `https://github.com/foryourhealth111-pixel/vco-skills-codex` on `main`
- the user wants implementation, not just a proposal, and chose the moderate compatibility path rather than an aggressive architecture expansion

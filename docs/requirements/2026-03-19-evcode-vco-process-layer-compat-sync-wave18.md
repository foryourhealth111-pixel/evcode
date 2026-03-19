# EvCode VCO Process-Layer Compatibility Sync Wave18 Requirement

## Goal

Sync the upstream VCO fixes that clarify process-layer ownership boundaries and harden phase-cleanup document safety into EvCode's embedded runtime mirror and host-bridge contract.

## Deliverable

- Refresh the embedded `runtime/vco/upstream` materialization from the newer upstream commit that contains the process-layer compatibility and cleanup-safety fixes
- Update EvCode runtime materialization metadata to the synced commit
- Align EvCode host-bridge documentation with the same ownership split so EvCode and the embedded runtime do not drift semantically
- Produce verification evidence that the embedded runtime mirror, metadata receipts, and bridge docs now reflect the upstream fix

## Constraints

- Preserve existing EvCode local work that is unrelated to this sync
- Do not revert unrelated worktree changes
- Prefer the smallest full-fidelity upstream sync surface that keeps materialization metadata truthful
- Keep VCO as the single governed runtime authority and avoid introducing a second runtime surface in EvCode

## Acceptance Criteria

- `runtime/vco/upstream` includes the upstream `Compatibility With Process Layers` changes in the canonical and bundled `vibe` skill surfaces
- the synced runtime mirror includes the upstream protected document cleanup policy and helper script additions
- `config/sources.lock.json`, `runtime/vco/.source.json`, `runtime/vco/materialization.json`, and `runtime/vco/freshness.json` consistently point at the synced upstream commit
- EvCode bridge documentation reflects the same ownership split and forbidden parallel-runtime outcomes
- materialization verification passes against the updated commit pin

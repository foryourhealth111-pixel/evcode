# EvCode Runtime Protected Document Cleanup Alignment Wave19 Requirement

## Goal

Align EvCode's Python governed runtime cleanup behavior with the newly synced upstream VCO protected-document cleanup contract so runtime receipts reflect real preview/quarantine safety semantics instead of a placeholder cleanup stub.

## Deliverable

- Implement a minimal Python cleanup path in `scripts/runtime/runtime_lib.py` that reads the embedded VCO cleanup policy
- Snapshot protected document assets across the declared roots
- Detect protected documents inside the temporary cleanup root
- Prefer quarantine over destructive removal for protected `.docx`, `.xlsx`, `.pptx`, and `.pdf` assets found under `.tmp`
- Emit cleanup evidence rich enough to show manifest, quarantine actions, post-check results, and resulting cleanup mode
- Add focused tests that prove protected tmp documents are quarantined while protected assets outside `.tmp` are retained

## Constraints

- Preserve unrelated worktree changes already present in the repository
- Do not widen this wave into broader runtime refactors or host-entry changes
- Keep EvCode as the execution authority; this wave only aligns cleanup semantics
- Reuse the upstream protected-document policy as the source of truth instead of inventing a second cleanup contract

## Acceptance Criteria

- `scripts/runtime/runtime_lib.py` reads the embedded VCO protected-document cleanup policy from `runtime/vco/upstream/config/phase-cleanup-policy.json`
- cleanup receipts contain protected document manifest details, quarantine evidence, and post-cleanup assertions
- protected documents inside `.tmp` are quarantined into the policy-declared quarantine root before `.tmp` is removed
- protected documents outside `.tmp` remain present after cleanup
- targeted automated tests cover at least one mixed protected-document scenario and one preview-only scenario or equivalent safety assertion path

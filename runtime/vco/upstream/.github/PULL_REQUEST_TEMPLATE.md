## Summary

- Change class:
  - [ ] Docs-only (Class A)
  - [ ] Governance / policy (Class B)
  - [ ] Mirror / fixture / provenance / compliance (Class C)
  - [ ] Runtime-affecting (Class D)
- Linked issue:
- Linked plan (`docs/plans/*.md`) if required:

## Touched Zones

- [ ] Z0 Frozen Control Plane
- [ ] Z1 Guarded Governance and Policy Surface
- [ ] Z2 Guarded Mirror, Fixture, Provenance, and Compliance Surface
- [ ] Z3 Preferred Contribution Zones

## Frozen / Guarded Area Declaration

- Frozen or guarded area touched:
  - [ ] No
  - [ ] Yes, Z0 touched
  - [ ] Yes, Z1 touched
  - [ ] Yes, Z2 touched
- If yes, explain why this could not stay additive in Z3:

## Proof Run

List the exact commands you ran and the result you observed. Use `Command -> Output -> Claim`.

| Command | Output | Claim |
| --- | --- | --- |
| `git diff --check` |  |  |
|  |  |  |
|  |  |  |

## Escalation / Stop-Ship

- Escalation needed before merge:
  - [ ] No
  - [ ] Yes, owner / maintainer review required
  - [ ] Yes, blocked until additional plan or proof is attached
- Stop-ship conditions triggered:
  - [ ] None
  - [ ] Plan missing for Z0 or runtime-affecting change
  - [ ] Required proof bundle is incomplete
  - [ ] Frozen / guarded surface touched without explicit justification
  - [ ] Source-of-truth / mirror / provenance path is unclear
- Escalation details:

## Contributor Checklist

- [ ] I identified the touched zone(s) before editing.
- [ ] I did not treat `bundled/**`, `references/fixtures/**`, tracked `outputs/**`, or vendored material as source-of-truth unless explicitly governed by this PR.
- [ ] If I touched Z0, Z1, or Z2, I linked the governing plan and attached the required proof.
- [ ] If this PR changes contributor-facing governance, the template declarations above are complete and not left blank.

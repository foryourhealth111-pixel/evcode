# One-Shot Setup Closure Report (2026-03-13)

## Outcome

The repository now has an executable one-shot bootstrap path for Codex runtime setup:

```powershell
pwsh -File .\scripts\bootstrap\one-shot-setup.ps1
```

This path is no longer only documented. It has been executed against the local target runtime at `C:\Users\羽裳\.codex`, and the runtime closure gates completed successfully.

## Delivered

- Added `scripts/bootstrap/one-shot-setup.ps1`
- Added `scripts/setup/materialize-codex-mcp-profile.ps1`
- Added `scripts/verify/vibe-bootstrap-doctor-gate.ps1`
- Added `docs/one-shot-setup.md`
- Added `docs/plans/2026-03-13-one-shot-full-setup-closure-plan.md`
- Updated `check.ps1` with `-Deep`
- Updated `check.sh` with `--deep`
- Updated deployment / script-index docs to expose the one-shot bootstrap and doctor flow
- Refreshed `config/skills-lock.json`
- Synced canonical runtime changes into `bundled/skills/vibe`

## Verified Commands

Executed from canonical repo root:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\bootstrap\one-shot-setup.ps1 -TargetRoot "$env:USERPROFILE\.codex"
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\verify\vibe-version-packaging-gate.ps1 -WriteArtifacts
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\verify\vibe-offline-skills-gate.ps1
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\governance\phase-end-cleanup.ps1 -WriteArtifacts
```

## Evidence

- `outputs/verify/vibe-bootstrap-doctor-gate.json`
- `outputs/verify/vibe-version-packaging-gate.json`
- `outputs/verify/vibe-installed-runtime-freshness-gate.json`
- `outputs/verify/vibe-release-install-runtime-coherence-gate.json`
- `outputs/verify/vibe-output-artifact-boundary-gate.json`

## Current Readiness Result

The one-shot bootstrap currently classifies the local runtime as:

- `readiness_state = manual_actions_pending`
- `blocking_issue_count = 0`

Manual actions still pending by design:

- required host plugins: `superpowers`, `everything-claude-code`, `claude-code-settings`, `hookify`, `ralph-loop`
- plugin-backed MCP surfaces: `github`, `context7`, `serena`

These are intentionally not auto-provisioned by repo scripts because they are host/platform managed surfaces or secret/permission bound surfaces.

## Bug Fixed During Execution

`scripts/verify/vibe-bootstrap-doctor-gate.ps1` failed under `Set-StrictMode` when reading missing environment variables through `.Value` on a null object. The secret-surface env read path has been corrected so the doctor gate now completes successfully even when optional env vars are absent.

## Remaining Boundary

This closure does not claim that host plugins or provider secrets can or should be silently auto-installed. The contract is:

- auto-install and verify what the repo can safely govern
- classify the rest explicitly as manual follow-up

That is the intended one-shot setup boundary.

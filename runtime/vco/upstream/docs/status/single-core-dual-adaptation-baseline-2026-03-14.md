# Single-Core Dual-Adaptation Baseline 2026-03-14

## Scope

This baseline records the first implementation batch of the single-core / dual-adaptation / dual-proof / dual-release program. It is not a promotion claim. It captures which platform-neutral contracts have already landed, what evidence exists, and which blockers remain open.

## Landed In This Batch

### 1. Root and home resolution moved into shared governance helpers

The shared helper surface in `scripts/common/vibe-governance-helpers.ps1` now provides:

- `Resolve-VgoHomeDirectory`
- `Resolve-VgoTargetRoot`
- `Resolve-VgoInstalledSkillsRoot`
- `Get-VgoPowerShellCommand`
- `Get-VgoPowerShellFileInvocation`
- `Invoke-VgoPowerShellFile`

This is the first explicit root/platform adapter layer for the repo. It removes the previous assumption that `USERPROFILE` is the only trustworthy home source.

### 2. Critical entrypoints no longer default to `USERPROFILE`

The following entrypoints were changed from `Join-Path $env:USERPROFILE '.codex'` to the shared resolver contract:

- `check.ps1`
- `install.ps1`
- `scripts/bootstrap/one-shot-setup.ps1`
- `scripts/setup/materialize-codex-mcp-profile.ps1`
- `scripts/verify/vibe-installed-runtime-freshness-gate.ps1`

Current effective precedence for these entrypoints is:

1. explicit `-TargetRoot`
2. `CODEX_HOME`
3. resolved platform home + default `.codex`

### 3. Linux installed-runtime fallback no longer depends on `USERPROFILE`

`scripts/router/modules/46-confirm-ui.ps1` no longer resolves installed skills from:

`$env:USERPROFILE\.codex\skills`

It now resolves installed skills from `Resolve-VgoInstalledSkillsRoot`, which follows the same target-root contract as install/check.

### 4. Promotion and no-regression gates no longer hardcode `powershell.exe`

The following verify scripts now launch subgates through the shared PowerShell host adapter instead of a Windows-only executable literal:

- `scripts/verify/vibe-platform-promotion-bundle.ps1`
- `scripts/verify/vibe-universalization-no-regression-gate.ps1`

This change is required for Linux `pwsh` authoritative proof to be possible later. It does not yet prove Linux promotion by itself.

### 5. Strict-mode crashes in the offline skills gate were fixed

`scripts/verify/vibe-offline-skills-gate.ps1` had deterministic strict-mode crashes caused by assuming pipeline results always exposed `.Count`. Those crashes were fixed by normalizing the affected collections to arrays before count-based logic.

This removes one false-negative installer failure mode, but does not close the deeper `skills-lock` hash drift described below.

## Verification Evidence

### Git hygiene

- `git diff --check` passed after the batch.

### Installed-runtime behavior-first freshness proof

The installed-runtime freshness gate itself now includes behavior assertions instead of stopping at mirror and marker parity.

Specifically, `scripts/verify/vibe-installed-runtime-freshness-gate.ps1` now verifies that the installed confirm-ui module can resolve skills from the target-root runtime under `CODEX_HOME`, not from an author-machine or repo-local fallback.

Current behavior assertions cover:

- `vibe`
- `dialectic`

For each skill, the gate now checks:

- installed confirm-ui module exists
- expected installed skill exists under `<TargetRoot>/skills`
- resolved skill path exists
- resolved path stays under the target-root installed skills root
- resolved path equals the expected installed path

This closes the specific blind spot that previously allowed static parity to pass while installed-runtime routing could still be broken on Linux.

### Relative and absolute target-root contract

`install.ps1` and `check.ps1` were exercised against both:

- relative target root: `outputs/tmp/dual-adapt-smoke-3`
- absolute target root: `D:\table\new_ai_table\_ext\vco-skills-codex\outputs\tmp\dual-adapt-smoke-abs`

Observed result:

- install completed successfully when `StrictOffline` was not forcing the unrelated lock-drift gate
- install artifacts were written to the requested target roots
- `check.ps1` resolved both relative and absolute target roots correctly

### Installed-runtime route resolution smoke

With `CODEX_HOME` pointed at an installed runtime target and `Resolve-SkillMdPath` called without a repo-root bundled fallback, the router confirm UI resolved:

- `outputs/tmp/dual-adapt-smoke-abs/skills/vibe/SKILL.md`

This is the direct proof that the installed-runtime lookup path no longer depends on `USERPROFILE`.

### Check-gate result snapshot

For both relative and absolute smoke targets, `check.ps1 -SkipRuntimeFreshnessGate` produced:

- `46 passed`
- `1 failed`
- `1 warnings`

The single failure was expected:

- missing runtime freshness receipt

The single warning was expected:

- runtime freshness gate skipped by request

This means the current entrypoint and installed-runtime layout are operational under the new root-resolution contract. It is not yet proof of full installed-runtime freshness behavior because the freshness gate was intentionally skipped during this smoke.

### Refreshed absolute-target runtime proof

After the behavior assertions were added, the absolute smoke target was reinstalled and revalidated:

- install target: `outputs/tmp/dual-adapt-smoke-abs`
- runtime freshness gate: `80 passed, 0 failed`
- full health check: `57 passed, 0 failed, 0 warnings`
- runtime freshness receipt written to:
  - `outputs/tmp/dual-adapt-smoke-abs/skills/vibe/outputs/runtime-freshness-receipt.json`

This is still not a Linux promotion claim. It is the first artifact-backed proof that installed-runtime freshness now includes real skill-resolution behavior in addition to mirror parity.

## Open Blockers After This Batch

### 1. `StrictOffline` still fails for real lock drift

`install.ps1 -StrictOffline` still fails, but the remaining failure is no longer a root-resolution crash. The current blocker is the existing `config/skills-lock.json` drift against the vendored skills tree.

This is an install-governance problem, not evidence that the new target-root contract regressed behavior.

### 2. Author-machine path leakage still exists in governed config

The following governed files still encode author-machine-specific absolute paths and must be normalized in a later batch:

- `config/dependency-map.json`
- `bundled/skills/vibe/config/dependency-map.json`
- `config/upstream-corpus-manifest.json`
- `bundled/skills/vibe/config/upstream-corpus-manifest.json`
- `config/ruc-nlpir-runtime.json`

### 3. Some docs still encode `~/.codex` as architecture truth instead of default host root

This batch only corrected the first critical protocol wording. Repo-wide wording convergence still remains for install, deployment, verify, and status surfaces.

### 4. Linux is not yet promotion-ready

This batch removes the first hard blockers for Linux authoritative proof, but it does not yet prove:

- installed-runtime freshness on Linux
- Linux promotion bundle pass
- Linux no-regression pass
- Linux fresh-machine proof bundle closure

## Current Judgment

The repo is now materially closer to a real single-core dual-adaptation architecture:

- root resolution is centralized
- installed-runtime skill lookup is no longer Windows-home-bound
- installed-runtime freshness now proves real target-root skill resolution for representative routed skills
- key proof gates are no longer hardcoded to `powershell.exe`

But the repo is **not yet** entitled to claim:

- full Linux authoritative promotion
- full host-neutral installed-runtime closure
- full one-shot install closure under `StrictOffline`

Those claims remain blocked until the next batches close behavior-first proof and config/doc distribution cleanup.

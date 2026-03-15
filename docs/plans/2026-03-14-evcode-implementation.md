# EvCode Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Build a new `evcode` CLI that wraps `codex`, applies a persistent Vibe bootstrap at session start, defaults to an `XL` workflow policy, and manages the VCO runtime as a first-class controlled payload without adding an external team scheduler.

**Terminology note:** In this plan, `governance` means the startup Vibe bootstrap policy toggle exposed by the CLI. It is not a second orchestration layer, and subtask skill activation still relies on appending ` $vibe` to child-task prompts.

**Architecture:** Use a TypeScript command facade that delegates execution to the native `codex` binary, injects a compact Vibe bootstrap contract at session start, defaults to `XL` planning/execution semantics, routes startup through skeleton and plan detection, and manages a pinned `vco-skills-codex` runtime under an isolated EvCode home. Keep compatibility logic thin, preserve `codex` native team as the only orchestration authority, and restrict EvCode to bootstrap, prompt-suffix, runtime, and cleanup responsibilities.

**Tech Stack:** TypeScript, Node.js, native `codex` CLI, JSON config files, shell/PowerShell adapters for upstream runtime scripts.

---

### Task 1: Scaffold the CLI workspace

**Files:**
- Create: `package.json`
- Create: `tsconfig.json`
- Create: `src/index.ts`
- Create: `src/commands/`
- Create: `src/shared/`
- Test: `tests/cli/`

**Step 1: Create the package manifest**

- Define package name `evcode`
- Add `bin` entry for CLI execution
- Add scripts for `build`, `test`, `lint`, and `dev`

**Step 2: Create TypeScript compiler config**

- Configure `src/` as source root
- Configure `dist/` as output directory
- Enable strict type checking

**Step 3: Create the CLI entrypoint**

- Parse argv
- Route to command handlers
- Return stable exit codes for success and failure

**Step 4: Add a smoke test target**

- Add a CLI test harness that can call the command parser without invoking real subprocesses

**Step 5: Verify the scaffold**

Run: `npm run build`
Expected: build succeeds and emits CLI entry files into `dist/`

### Task 2: Add configuration and EvCode home management

**Files:**
- Create: `src/config/load.ts`
- Create: `src/config/schema.ts`
- Create: `src/config/defaults.ts`
- Create: `src/runtime/paths.ts`
- Test: `tests/config/config.test.ts`

**Step 1: Define the EvCode config schema**

- Model `codex` and `evcode` config namespaces separately
- Include governance mode, default workflow grade, unattended policy, prompt suffix policy, runtime source, runtime version, provider, and MCP profile

**Step 2: Implement config loading**

- Load config from `~/.evcode/config/default.json`
- Allow command-line overrides
- Validate config shape before use

**Step 3: Implement home path resolution**

- Resolve `~/.evcode/`
- Resolve subpaths for config, runtime, sessions, logs, receipts, and cache

**Step 4: Add tests**

- Verify defaults load correctly
- Verify malformed config is rejected with clear errors

**Step 5: Verify the config flow**

Run: `npm test -- tests/config/config.test.ts`
Expected: config tests pass

### Task 3: Implement native Codex process adapter

**Files:**
- Create: `src/codex/spawn.ts`
- Create: `src/codex/args.ts`
- Create: `src/codex/detect.ts`
- Test: `tests/codex/spawn.test.ts`

**Step 1: Detect the `codex` binary**

- Resolve from PATH
- Provide a clear error when unavailable

**Step 2: Build argument mapping helpers**

- Map `evcode exec` to `codex exec`
- Map raw sessions to native `codex`
- Preserve cwd, model, approval, and sandbox options

**Step 3: Implement subprocess spawning**

- Support interactive and non-interactive execution
- Propagate exit status and stderr cleanly

**Step 4: Add tests**

- Mock process spawning
- Verify command mapping is correct

**Step 5: Verify the adapter**

Run: `npm test -- tests/codex/spawn.test.ts`
Expected: mapping and spawn tests pass

### Task 4: Implement session-start governance injection

**Files:**
- Create: `src/governance/bootstrap.ts`
- Create: `src/governance/policy.ts`
- Create: `src/governance/session-mode.ts`
- Test: `tests/governance/bootstrap.test.ts`

**Step 1: Define the compact bootstrap contract**

- Encode the session-start Vibe governance semantics
- Encode the default system prompt contract:
  - inspect repo
  - detect VCO skeleton
  - detect plan
  - initialize skeleton if missing
  - use `XL` planning if no plan
  - use unattended `XL` execution if a plan exists
- Keep the injected payload concise and versioned

**Step 2: Implement governance modes**

- Support `vibe-on` and `vibe-off`
- Default `vibe-on` to workflow grade `XL`
- Implement explicit raw escape

**Step 3: Implement injection assembly**

- Build the session-start prompt payload
- Expose a function to produce the final initial context for a new session

**Step 4: Add tests**

- Verify `vibe-on` always injects
- Verify `raw` never injects
- Verify the `XL` workflow marker is always present in Vibe-bootstrapped sessions
- Verify the system prompt contract includes skeleton and plan checks

**Step 5: Verify governance behavior**

Run: `npm test -- tests/governance/bootstrap.test.ts`
Expected: governance injection tests pass

### Task 5: Implement base commands: `evcode`, `evcode exec`, and `evcode raw`

**Files:**
- Create: `src/commands/run.ts`
- Create: `src/commands/exec.ts`
- Create: `src/commands/raw.ts`
- Modify: `src/index.ts`
- Test: `tests/commands/run.test.ts`

**Step 1: Implement the default interactive command**

- Start a new Codex session
- Apply governance injection by default
- Default to `XL` workflow mode

**Step 2: Implement `exec`**

- Run a non-interactive command with the same governance bootstrap
- Default to `XL` workflow mode

**Step 3: Implement `raw`**

- Start a native-compatible session without governance injection

**Step 4: Add tests**

- Verify command routing
- Verify governance behavior per command

**Step 5: Verify the command surface**

Run: `npm test -- tests/commands/run.test.ts`
Expected: run, exec, and raw tests pass

### Task 6: Implement skeleton detection, plan detection, and startup workflow routing

**Files:**
- Create: `src/governance/skeleton-detector.ts`
- Create: `src/governance/plan-detector.ts`
- Create: `src/governance/workflow-spec.ts`
- Test: `tests/governance/routing.test.ts`

**Step 1: Implement skeleton detection**

- Detect whether the repository has the minimum EvCode/VCO scaffold markers

**Step 2: Implement plan detection**

- Detect whether a valid plan file already exists
- Start with `docs/plans/*.md` support

**Step 3: Implement startup workflow routing**

- If skeleton is missing, route to scaffold initialization
- If no plan exists, route to `XL planning mode`
- If a plan exists, route to unattended `XL execution mode`

**Step 4: Add tests**

- Verify all three startup states route correctly

**Step 5: Verify workflow routing**

Run: `npm test -- tests/governance/routing.test.ts`
Expected: startup workflow routing tests pass

### Task 7: Add runtime pinning and receipt storage

**Files:**
- Create: `src/runtime/receipts.ts`
- Create: `src/runtime/pin.ts`
- Create: `src/runtime/status.ts`
- Test: `tests/runtime/pin.test.ts`

**Step 1: Define the runtime receipt format**

- Store source URL, pinned version, install time, and verification result

**Step 2: Implement receipt write and read**

- Persist receipts to `~/.evcode/receipts/`
- Load receipts for status and doctor commands

**Step 3: Implement runtime pin state**

- Track the active VCO runtime version
- Expose API for sync, update, and rollback to use later

**Step 4: Add tests**

- Verify read and write symmetry
- Verify missing receipts are handled gracefully

**Step 5: Verify runtime state**

Run: `npm test -- tests/runtime/pin.test.ts`
Expected: runtime pin tests pass

### Task 8: Implement `doctor` and `status`

**Files:**
- Create: `src/commands/doctor.ts`
- Create: `src/commands/status.ts`
- Create: `src/doctor/checks.ts`
- Test: `tests/doctor/doctor.test.ts`

**Step 1: Implement binary and config checks**

- Check `codex` availability
- Check config readability
- Check EvCode home layout

**Step 2: Implement runtime checks**

- Check runtime payload presence
- Check receipt consistency
- Check governance mode validity
- Check default `XL` workflow policy is valid
- Check skeleton detector and plan detector can run
- Check stage cleaner can run

**Step 3: Implement status rendering**

- Show governance mode, workflow grade, profile, runtime version, and MCP profile

**Step 4: Add tests**

- Verify doctor output classification
- Verify status output includes required fields

**Step 5: Verify diagnostics**

Run: `npm test -- tests/doctor/doctor.test.ts`
Expected: doctor and status tests pass

### Task 9: Integrate the VCO runtime payload

**Files:**
- Create: `src/runtime/sync.ts`
- Create: `src/runtime/verify.ts`
- Create: `src/runtime/source.ts`
- Test: `tests/runtime/sync.test.ts`

**Step 1: Define runtime source strategy**

- Support pinned git source first
- Leave room for release artifacts later

**Step 2: Implement sync behavior**

- Download or sync the upstream `vco-skills-codex` payload into EvCode home

**Step 3: Implement verification hooks**

- Detect required payload subpaths
- Validate expected config, protocol, and script roots exist

**Step 4: Add tests**

- Verify sync state transitions
- Verify incomplete runtime is reported as not ready

**Step 5: Verify runtime integration**

Run: `npm test -- tests/runtime/sync.test.ts`
Expected: runtime sync tests pass

### Task 10: Add unattended XL execution helpers and stage cleanup

**Files:**
- Create: `src/governance/subagent-prompt.ts`
- Create: `src/cleanup/node-zombies.ts`
- Create: `src/cleanup/temp-files.ts`
- Create: `src/cleanup/stage-cleaner.ts`
- Test: `tests/cleanup/stage-cleaner.test.ts`

**Step 1: Implement subagent prompt suffix injection**

- Ensure every child task prompt ends with ` $vibe`

**Step 2: Implement zombie Node cleanup**

- Detect stale Node processes attributable to EvCode-managed stages
- Kill only managed zombies, not arbitrary user processes

**Step 3: Implement temp file cleanup**

- Remove EvCode-managed temporary artifacts after each stage
- Keep receipts, logs, and persistent runtime files intact

**Step 4: Implement stage cleaner orchestration**

- Run cleanup after each completed stage
- Emit cleanup status for observability

**Step 5: Verify cleanup behavior**

Run: `npm test -- tests/cleanup/stage-cleaner.test.ts`
Expected: cleanup tests pass

### Task 11: Add governance and runtime management commands

**Files:**
- Create: `src/commands/governance.ts`
- Create: `src/commands/runtime.ts`
- Test: `tests/commands/governance.test.ts`

**Step 1: Implement governance mode switching**

- Add `on`, `off`, and `status`
- Persist changes into EvCode config

**Step 2: Implement runtime management**

- Add `status`, `sync`, `update`, and `rollback`
- Use receipts and pins for safety

**Step 3: Add tests**

- Verify state changes are persisted
- Verify invalid mode input is rejected

**Step 4: Verify management commands**

Run: `npm test -- tests/commands/governance.test.ts`
Expected: governance and runtime command tests pass

### Task 12: Add documentation and release-ready validation

**Files:**
- Create: `README.md`
- Create: `docs/architecture.md`
- Modify: `docs/plans/2026-03-14-evcode-b-design.md`
- Test: `tests/integration/`

**Step 1: Write user-facing README**

- Explain what EvCode is
- Explain the difference between `evcode` and `evcode raw`
- Explain that Vibe-bootstrapped sessions default to `XL`
- Explain skeleton and plan detection and unattended progression

**Step 2: Write architecture notes**

- Summarize the four-layer design
- Document session-start injection behavior

**Step 3: Add an integration smoke test**

- Verify `evcode` resolves config, builds the bootstrap contract, and produces the correct codex invocation plan
- Verify a child-task prompt receives the ` $vibe` suffix
- Verify stage completion triggers cleanup hooks

**Step 4: Run the full validation suite**

Run: `npm run build`
Expected: PASS

Run: `npm test`
Expected: PASS

**Step 5: Prepare first release candidate**

Run: `git status --short`
Expected: only intended files are modified

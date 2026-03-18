# EvCode Portable Paths And Hybrid Baseline Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Make EvCode portable across machines and install locations while adding a governed hybrid-agent baseline test lane that complements, rather than replaces, the Codex-primary benchmark baseline.

**Architecture:** Introduce a shared runtime path model that separates install, state, config, workspace, and artifacts roots. Use that path model to move the primary user config surface out of repo-only assumptions, normalize artifact behavior, and add baseline tests that separately cover deterministic benchmark behavior and governed hybrid specialist routing.

**Tech Stack:** Node.js entrypoints, Python governed runtime scripts, JSON policy/config files, pytest/unittest-based verification, existing VCO routing and provider adapter layers.

---

### Task 1: Add a first-class portable path model

**Files:**
- Modify: `apps/evcode/bin/evcode.js`
- Modify: `apps/evcode-bench/bin/evcode-bench.js`
- Modify: `packages/provider-runtime/src/local_provider_env.js`
- Modify: `scripts/runtime/run_governed_runtime.py`
- Modify: `scripts/runtime/runtime_lib.py`
- Modify: `scripts/runtime/execute_benchmark_task.py`
- Test: `tests/test_app_entrypoints.py`
- Test: `tests/test_runtime_bridge.py`
- Create: `tests/test_portable_paths.py`

**Step 1: Write the failing path-resolution tests**

Cover at least:

- source mode with repo-local override present
- source mode without repo-local override
- non-repo portable state/config root resolution
- benchmark artifact path resolution when caller requests an in-workspace path
- moved-workspace simulation using temporary directories

**Step 2: Run only the new path tests and verify failure**

Run: `python3 -m pytest tests/test_portable_paths.py -q`
Expected: failing assertions for missing portable path resolution and current redirect semantics

**Step 3: Implement a shared path resolver contract**

Implement explicit helpers for:

- install root
- state root
- config root
- workspace root
- artifacts root

Rules:

- no user-facing primary config contract may require repo checkout paths
- repo-local config remains a development override only
- env and CLI overrides stay highest precedence

**Step 4: Update JS and Python entrypoints to consume the shared model**

Ensure standard and benchmark paths use the same vocabulary and precedence model.

**Step 5: Run the focused tests again**

Run: `python3 -m pytest tests/test_portable_paths.py tests/test_app_entrypoints.py tests/test_runtime_bridge.py -q`
Expected: pass

### Task 2: Fix the benchmark artifact contract

**Files:**
- Modify: `scripts/runtime/runtime_lib.py`
- Modify: `scripts/runtime/execute_benchmark_task.py`
- Modify: `apps/evcode-bench/bin/evcode-bench.js`
- Test: `tests/test_runtime_bridge.py`
- Test: `tests/test_contracts.py`
- Create: `tests/test_benchmark_artifact_contract.py`

**Step 1: Write failing tests for requested path handoff behavior**

Cover at least:

- requested `--artifacts-root` inside workspace
- requested `--result-json` inside workspace
- resulting contract still exposes the safe execution root
- requested path receives a stable manifest or copied final artifact

**Step 2: Run the failing artifact contract tests**

Run: `python3 -m pytest tests/test_benchmark_artifact_contract.py -q`
Expected: fail under current silent redirect behavior

**Step 3: Implement the new contract**

Recommended implementation:

- keep safe execution root external when needed
- after run completion, materialize a stable user-visible handoff at the requested path
- include both requested path and effective execution path in runtime summary
- make CLI output explain the handoff clearly

**Step 4: Verify benchmark summary shape and path predictability**

Run: `python3 -m pytest tests/test_benchmark_artifact_contract.py tests/test_contracts.py tests/test_runtime_bridge.py -q`
Expected: pass

### Task 3: Move the primary provider setup story to a portable config surface

**Files:**
- Modify: `packages/provider-runtime/src/local_provider_env.js`
- Modify: `packages/provider-runtime/README.md`
- Modify: `docs/configuration/openai-compatible-provider-setup.md`
- Modify: `apps/evcode/bin/evcode.js`
- Modify: `apps/evcode-bench/bin/evcode-bench.js`
- Test: `tests/test_assistant_adapters.py`
- Create: `tests/test_provider_env_resolution.py`

**Step 1: Write failing tests for config precedence**

Cover precedence:

- CLI/env override
- portable user config file
- repo-local dev override
- tracked defaults

**Step 2: Run config precedence tests and confirm failure**

Run: `python3 -m pytest tests/test_provider_env_resolution.py -q`
Expected: fail until portable config root is introduced

**Step 3: Implement the portable config lookup**

Requirements:

- keep one user document for key/url/model setup
- keep repo-local `config/assistant-providers.env.local` as development compatibility only
- surface which root actually supplied the configuration in `status` and `doctor`

**Step 4: Update docs to reflect the portable-first story**

Document one main setup path for distributed users and one explicit development override path for source-mode contributors.

**Step 5: Re-run focused tests**

Run: `python3 -m pytest tests/test_provider_env_resolution.py tests/test_assistant_adapters.py tests/test_app_entrypoints.py -q`
Expected: pass

### Task 4: Add a hybrid governed baseline family

**Files:**
- Modify: `config/specialist-routing.json`
- Modify: `profiles/standard/profile.json`
- Modify: `profiles/benchmark/profile.json`
- Modify: `scripts/verify/probe_assistant_providers.py`
- Create: `scripts/verify/run_hybrid_baseline.py`
- Create: `tests/test_hybrid_baseline.py`
- Modify: `tests/test_specialist_routing.py`
- Modify: `docs/architecture/evcode-multi-assistant-routing.md`

**Step 1: Write failing routing and baseline tests**

Cover at least:

- planning task routes to Claude in governed standard mode
- visual frontend task routes to Gemini in governed standard mode
- backend/runtime task remains Codex-owned
- benchmark mode suppresses specialists by default
- hybrid baseline reports separately from core benchmark

**Step 2: Run only hybrid baseline tests and confirm failure**

Run: `python3 -m pytest tests/test_hybrid_baseline.py tests/test_specialist_routing.py -q`
Expected: fail until the new baseline family exists

**Step 3: Implement a separate hybrid baseline runner**

Requirements:

- do not replace the existing benchmark lane
- do not require live providers by default
- support offline contract assertions first
- support optional live smoke mode second
- emit distinct receipts and result summaries

**Step 4: Re-run hybrid tests**

Run: `python3 -m pytest tests/test_hybrid_baseline.py tests/test_specialist_routing.py -q`
Expected: pass

### Task 5: Improve status, doctor, and help ergonomics

**Files:**
- Modify: `apps/evcode/bin/evcode.js`
- Modify: `apps/evcode-bench/bin/evcode-bench.js`
- Test: `tests/test_app_entrypoints.py`
- Test: `tests/test_contracts.py`

**Step 1: Write failing CLI behavior tests**

Cover at least:

- `run --help` must show help instead of failing for missing `--task`
- `status --json` must distinguish portable config root, repo-local override, and effective source cleanly
- benchmark summary must describe requested vs effective artifact paths clearly

**Step 2: Run the CLI behavior tests and confirm failure**

Run: `python3 -m pytest tests/test_app_entrypoints.py tests/test_contracts.py -q`
Expected: fail under current behavior

**Step 3: Implement the CLI/help/status corrections**

Requirements:

- standard help semantics for `run --help`
- clearer status fields for config source and path domains
- no misleading implication that repo-local config is the only supported path

**Step 4: Re-run targeted tests**

Run: `python3 -m pytest tests/test_app_entrypoints.py tests/test_contracts.py -q`
Expected: pass

### Task 6: End-to-end proof across portable and hybrid scenarios

**Files:**
- Modify: `docs/status/evcode-production-user-journey-proof.md`
- Create: `docs/status/evcode-portable-paths-hybrid-baseline-proof.md`
- Create: `docs/status/evcode-portable-paths-hybrid-baseline-report.json`

**Step 1: Run offline verification suite**

Run:

```bash
python3 -m pytest \
  tests/test_portable_paths.py \
  tests/test_benchmark_artifact_contract.py \
  tests/test_provider_env_resolution.py \
  tests/test_hybrid_baseline.py \
  tests/test_specialist_routing.py \
  tests/test_app_entrypoints.py \
  tests/test_runtime_bridge.py \
  tests/test_contracts.py -q
```

Expected: pass

**Step 2: Run portable smoke checks in a temp workspace**

Required checks:

- source-mode with repo-local override
- source-mode without repo-local override
- portable user config root outside repo
- benchmark run with caller-requested artifacts path and stable handoff

**Step 3: Run opt-in live hybrid smoke checks**

Required checks:

- live `probe-providers --json --live`
- one Claude-routed governed standard task
- one Gemini-routed governed standard task
- one Codex-only benchmark task

**Step 4: Write proof and structured report**

Document:

- which paths were resolved
- which roots were used
- whether requested artifact paths were honored or mirrored correctly
- whether hybrid baseline routing matched expected assistants
- whether Codex final authority remained intact

### Task 7: Rollout and compatibility guardrails

**Files:**
- Modify: `docs/architecture/evcode-governed-specialist-repair.md`
- Modify: `docs/architecture/evcode-multi-assistant-routing.md`
- Modify: `README.md`
- Create: `docs/configuration/portable-runtime-paths.md`

**Step 1: Document the compatibility story**

Document explicitly:

- portable-first user story
- source-mode development override story
- benchmark core vs hybrid baseline distinction
- Codex-only final mutation authority

**Step 2: Add rollout gates**

Add release gates requiring:

- offline path-resolution tests pass
- offline hybrid routing tests pass
- CLI help/status contract checks pass
- optional live smoke proof generated for release candidates

**Step 3: Final verification**

Run a lightweight documentation consistency check and confirm all referenced files exist.

Run: `python3 scripts/verify/check_contracts.py`
Expected: pass

## Rollback Rules

- If portable path resolution destabilizes source-mode development, fall back to compatibility mode while preserving the new path-domain API surface.
- If hybrid baseline introduces flakiness into core CI, keep the hybrid family as a separate report-only lane until stabilized.
- If benchmark artifact handoff becomes ambiguous, prefer explicit failure over silent redirection.

## Phase Cleanup Expectations

- remove external temporary benchmark roots created during proof runs
- preserve copied evidence under repo-owned session artifacts
- keep long-lived user-owned agent processes audit-only unless explicitly launched by the current run
- emit cleanup receipt before claiming the rollout proof is complete

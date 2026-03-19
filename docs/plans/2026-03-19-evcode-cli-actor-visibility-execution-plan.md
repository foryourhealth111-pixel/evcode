# EvCode CLI Actor Visibility Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Add a governed, evidence-backed CLI actor visibility surface that shows real Codex, Claude, and Gemini participation during `evcode run`, plus trace replay for completed runs.

**Architecture:** The runtime remains the source of truth and emits a JSONL event ledger under each vibe session. The CLI renders that ledger in either a compact actor-board mode or a verbose trace mode while preserving `--json` machine output. Codex remains final executor, and degraded specialist states remain explicit.

**Tech Stack:** Node.js CLI entrypoints, Python governed runtime bridge, JSONL event ledger, Python unittest suite.

---

### Task 1: Freeze the runtime event contract

**Files:**
- Modify: `scripts/runtime/runtime_lib.py`
- Create: `docs/architecture/evcode-cli-actor-visibility.md`
- Test: `tests/test_runtime_bridge.py`

**Step 1: Write or extend failing tests**
- Add assertions that a standard governed run emits a runtime events artifact and that the event ledger contains route and actor state transitions.

**Step 2: Run test to verify it fails**
- Run: `python3 -m unittest tests.test_runtime_bridge.RuntimeBridgeTests.test_standard_run_writes_governed_and_specialist_artifacts -v`
- Expected: FAIL because no events artifact or ledger exists yet.

**Step 3: Implement runtime event helpers**
- Add append-only JSONL event writing helpers.
- Emit route, actor, degraded, integration, and cleanup events from the governed runtime.
- Add the events artifact path to `runtime-summary.json`.

**Step 4: Run test to verify it passes**
- Run the same unit test.
- Expected: PASS with event ledger and summary references present.

### Task 2: Add actor-aware CLI rendering for standard runs

**Files:**
- Modify: `apps/evcode/bin/evcode.js`
- Create: `apps/evcode/lib/runtime_display.js`
- Test: `tests/test_app_entrypoints.py`

**Step 1: Write or extend failing tests**
- Add tests for `evcode run --trace` and default non-JSON output proving the actor board, route line, and degraded visibility are present.

**Step 2: Run test to verify it fails**
- Run: `python3 -m unittest tests.test_app_entrypoints.AppEntrypointTests.test_standard_run_trace_surfaces_actor_timeline -v`
- Expected: FAIL because no trace renderer exists.

**Step 3: Implement the CLI renderer**
- Parse CLI flags for `--trace` and `--json`.
- Use asynchronous child execution for non-JSON runs.
- Poll the runtime event ledger during execution.
- Render a compact actor board for TTY and deterministic line output for non-TTY.
- Keep `--json` untouched.

**Step 4: Run test to verify it passes**
- Run the targeted test.
- Expected: PASS with the new actor timeline output.

### Task 3: Add trace replay command

**Files:**
- Modify: `apps/evcode/bin/evcode.js`
- Modify: `apps/evcode-bench/bin/evcode-bench.js`
- Modify: `apps/evcode/README.md`
- Test: `tests/test_app_entrypoints.py`

**Step 1: Write or extend failing tests**
- Add a replay test that runs a standard task, then calls `evcode trace <run-id>` and verifies actor and event output.

**Step 2: Run test to verify it fails**
- Run: `python3 -m unittest tests.test_app_entrypoints.AppEntrypointTests.test_standard_trace_replays_saved_runtime_events -v`
- Expected: FAIL because `trace` is unsupported.

**Step 3: Implement replay support**
- Add `trace` command parsing.
- Resolve runtime session roots from run id and artifacts root.
- Render event history from the saved JSONL ledger.
- Mirror this command in `evcode-bench` for channel consistency.

**Step 4: Run test to verify it passes**
- Run the targeted replay test.
- Expected: PASS with deterministic replay output.

### Task 4: Finalize UX spec and docs

**Files:**
- Create: `docs/architecture/evcode-cli-actor-visibility.md`
- Modify: `apps/evcode/README.md`
- Create: `docs/status/evcode-cli-actor-visibility-proof.md`

**Step 1: Document the UI and event mapping**
- Record actor states, content kinds, rendering rules, fallback behavior, and no-fake-live guarantees.

**Step 2: Capture proof evidence**
- Run representative standard tasks.
- Record commands, outputs, artifact paths, and degraded/live observations.

**Step 3: Update the proof doc**
- Write a verification matrix tied to concrete session artifacts.

### Task 5: Verification, cleanup, and closure

**Files:**
- Modify: `docs/status/evcode-cli-actor-visibility-proof.md`
- Update generated artifacts under `outputs/runtime/vibe-sessions/`

**Step 1: Run focused verification**
- `python3 -m unittest tests.test_runtime_bridge tests.test_app_entrypoints tests.test_specialist_routing -v`

**Step 2: Run broader regression checks**
- `python3 -m unittest discover -s tests -p 'test_*.py'`

**Step 3: Run real CLI validation**
- Execute at least one standard run using `--trace`.
- Execute one degraded specialist scenario.
- Replay one saved run with `evcode trace <run-id>`.

**Step 4: Cleanup**
- Remove temporary files and `__pycache__` directories created during testing.
- Audit Node processes and confirm no VCO-managed zombie processes remain.
- Preserve runtime cleanup receipts referenced by the proof doc.

## Verification Commands

- `python3 -m unittest tests.test_runtime_bridge tests.test_app_entrypoints tests.test_specialist_routing -v`
- `python3 -m unittest discover -s tests -p 'test_*.py'`
- `node apps/evcode/bin/evcode.js run --task "Design a responsive frontend landing page with typography, spacing, motion, and visual polish" --trace --run-id cli-actor-visibility-demo`
- `node apps/evcode/bin/evcode.js trace cli-actor-visibility-demo`
- `node apps/evcode/bin/evcode.js run --task "Plan the product architecture and UX workflow for an ambiguous redesign" --trace --run-id cli-actor-visibility-fallback`

## Rollback Rules

- Do not emit UI states that cannot be reconstructed from runtime events.
- Do not break `--json` compatibility for automation surfaces.
- If live specialist display logic becomes misleading, fall back to result-backed activity lines rather than faking streaming.
- If trace replay and live rendering diverge, treat that as a correctness bug and revert the renderer changes until the event model is fixed.

## Phase Cleanup Expectations

- delete temporary CLI validation directories
- remove `__pycache__`
- confirm no test-created Node zombies remain
- cite cleanup receipts in the proof doc

# EvCode CLI Actor Visibility Proof

## Status

- Status: Verified implementation
- Date: 2026-03-19
- Scope: Governed CLI actor visibility for Codex, Claude, and Gemini

## Deliverables Completed

1. Requirement document
   - `docs/requirements/2026-03-19-evcode-cli-actor-visibility.md`
2. Execution plan
   - `docs/plans/2026-03-19-evcode-cli-actor-visibility-execution-plan.md`
3. Architecture document
   - `docs/architecture/evcode-cli-actor-visibility.md`
4. Proof document
   - `docs/status/evcode-cli-actor-visibility-proof.md`

## Implemented Surfaces

- runtime event ledger: `outputs/runtime/vibe-sessions/<run-id>/runtime-events.jsonl`
- runtime summary reference: `artifacts.runtime_events`
- standard CLI actor-board rendering in interactive mode
- `evcode run --trace`
- `evcode trace <run-id>`
- benchmark trace replay parity via `evcode-bench trace <run-id>`

## Verification Matrix

### 1. Runtime contract emission

Command:

```bash
python3 -m unittest tests.test_runtime_bridge.RuntimeBridgeTests.test_standard_run_writes_governed_and_specialist_artifacts -v
```

Observed result:

- PASS
- confirms runtime events artifact exists
- confirms route and codex events are emitted
- confirms summary telemetry includes event count

### 2. Standard CLI trace surface

Command:

```bash
python3 -m unittest tests.test_app_entrypoints.AppEntrypointTests.test_standard_run_trace_surfaces_actor_timeline -v
```

Observed result:

- PASS
- confirms `evcode run --trace` prints header, actor board, timeline, and runtime-events artifact path

### 3. Saved trace replay

Command:

```bash
python3 -m unittest tests.test_app_entrypoints.AppEntrypointTests.test_standard_trace_replays_saved_runtime_events -v
```

Observed result:

- PASS
- confirms `evcode trace <run-id>` replays the saved timeline from artifacts

### 3.1 Benchmark trace replay

Command:

```bash
python3 -m unittest tests.test_app_entrypoints.AppEntrypointTests.test_benchmark_trace_replays_saved_runtime_events -v
```

Observed result:

- PASS
- confirms `evcode-bench trace <run-id>` can replay benchmark-session runtime events from saved artifacts

### 4. Focused regression set

Command:

```bash
python3 -m unittest tests.test_runtime_bridge tests.test_app_entrypoints tests.test_specialist_routing -v
```

Observed result:

- PASS
- 21 tests passed
- no routing or entrypoint regressions detected

### 5. Full regression suite

Command:

```bash
python3 -m unittest discover -s tests -p 'test_*.py'
```

Observed result:

- PASS
- 71 tests passed

## Real CLI Evidence

### Frontend-visual governed run

Command:

```bash
node apps/evcode/bin/evcode.js run --task "Design a responsive frontend landing page with typography, spacing, motion, and visual polish" --trace --run-id repo-cli-actor-visibility-demo
```

Observed facts:

- route: `codex_with_specialists`
- domain: `frontend_visual`
- `gemini` visible in the actor board
- `gemini` explicitly degrades when live specialist invocation is unavailable
- `codex` explicitly shows integration and final completion

Artifacts:

- runtime summary: `outputs/runtime/vibe-sessions/repo-cli-actor-visibility-demo/runtime-summary.json`
- runtime events: `outputs/runtime/vibe-sessions/repo-cli-actor-visibility-demo/runtime-events.jsonl`
- cleanup receipt: `outputs/runtime/vibe-sessions/repo-cli-actor-visibility-demo/cleanup-receipt.json`
- routing receipt: `outputs/runtime/vibe-sessions/repo-cli-actor-visibility-demo/specialist-routing-receipt.json`

### Planning governed run

Command:

```bash
node apps/evcode/bin/evcode.js run --task "Plan the product architecture and UX workflow for an ambiguous redesign" --trace --run-id repo-cli-actor-visibility-fallback
```

Observed facts:

- route: `codex_with_specialists`
- domain: `planning`
- `claude` visible in the actor board
- `claude` explicitly degrades when live specialist invocation is unavailable
- `gemini` is explicitly suppressed for the planning task
- `codex` remains final executor and integration owner

Artifacts:

- runtime summary: `outputs/runtime/vibe-sessions/repo-cli-actor-visibility-fallback/runtime-summary.json`
- runtime events: `outputs/runtime/vibe-sessions/repo-cli-actor-visibility-fallback/runtime-events.jsonl`
- cleanup receipt: `outputs/runtime/vibe-sessions/repo-cli-actor-visibility-fallback/cleanup-receipt.json`
- routing receipt: `outputs/runtime/vibe-sessions/repo-cli-actor-visibility-fallback/specialist-routing-receipt.json`

### Trace replay

Command:

```bash
node apps/evcode/bin/evcode.js trace repo-cli-actor-visibility-demo
```

Observed facts:

- replay reproduces the actor board and timeline from saved artifacts
- no live routing recomputation occurs during replay
- replay remains tied to saved runtime truth

### Live provider compatibility and fallback check

Commands used with the supplied RightCodes settings:

```bash
node apps/evcode/bin/evcode.js probe-providers --json --live
node apps/evcode/bin/evcode.js run --task "Plan the product architecture and UX workflow for an ambiguous redesign" --trace --run-id live-claude-fallback-proof
node apps/evcode/bin/evcode.js run --task "Design a responsive frontend landing page with typography, spacing, motion, and visual polish" --trace --run-id live-gemini-fallback-proof
```

Observed facts:

- `codex` is live-compatible on the supplied `https://right.codes/codex/v1` + `gpt-5.4` configuration
- `claude` currently fails live probing on the supplied `https://right.codes/claude/v1` + `claude-opus-4-6` configuration with provider HTTP `403`
- `gemini` currently fails live probing on the supplied `https://right.codes/gemini/v1` + `gemini-3.1-pro-preview` configuration with provider HTTP `503` and `model_not_found`
- both governed fallback runs still show actor-board degradation, explicit warning text, and Codex takeover rather than silent success language

Artifacts:

- live probe summary: `docs/status/evcode-cli-actor-visibility-live-provider-check.json`
- Claude fallback summary: `outputs/runtime/vibe-sessions/live-claude-warning-proof/runtime-summary.json`
- Claude fallback events: `outputs/runtime/vibe-sessions/live-claude-warning-proof/runtime-events.jsonl`
- Gemini fallback summary: `outputs/runtime/vibe-sessions/live-gemini-warning-proof/runtime-summary.json`
- Gemini fallback events: `outputs/runtime/vibe-sessions/live-gemini-warning-proof/runtime-events.jsonl`

## Stability Claims and Evidence

### Stable event source

Claim: the CLI now renders from a dedicated runtime event ledger rather than inventing status in the UI.

Evidence:

- `scripts/runtime/runtime_lib.py` now emits `runtime-events.jsonl`
- `runtime-summary.json` records the event path under `artifacts.runtime_events`
- tests assert existence and readability of the event ledger

### Stable compatibility surface

Claim: automation-safe JSON behavior remains intact.

Evidence:

- default non-TTY runs still return JSON when `--trace` is not used
- `--json` is preserved explicitly
- existing runtime bridge and app entrypoint tests still pass

## Usability Claims and Evidence

### CLI-visible actor identity

Claim: the user can now tell which actor is engaged without inspecting artifacts manually.

Evidence:

- actor board rows for `CODX`, `CLAU`, and `GEMI`
- route, domain, and final executor shown in the CLI header
- recent activity or timeline section shows actor-specific events

### Non-silent fallback

Claim: specialist degradation is no longer hidden.

Evidence:

- degraded actor states are visible in the board
- timeline includes degradation reason or contract-ready live-unavailable message
- existing non-silent fallback test still passes

## Intelligence Claims and Evidence

This feature does not attempt to prove model quality. It proves governed orchestration intelligence and truthful display.

Evidence:

- frontend-visual tasks visibly route to Gemini
- planning tasks visibly route to Claude
- backend/high-risk tasks still remain codex-led or specialist-suppressed by policy
- Codex is never displaced as final executor in the visible UI or artifact chain

## Known Boundary

True token-by-token specialist streaming is not claimed here because the current specialist adapter uses blocking request/response invocation. The implemented feature truthfully displays:

- request selection
- in-flight dispatch state
- completed or degraded result state
- Codex integration state

without pretending to provide live token streaming where it does not exist.

## Cleanup

Cleanup completed after implementation and verification.

Actions performed:

- no temporary tracked files left behind beyond intended docs and runtime proof artifacts
- runtime cleanup receipts preserved for the repo-local proof runs and the live fallback proof runs
- broad unit test run completed successfully after changes
- distribution-portability validator temp roots were removed automatically after validation

Cleanup receipts cited:

- `outputs/runtime/vibe-sessions/repo-cli-actor-visibility-demo/cleanup-receipt.json`
- `outputs/runtime/vibe-sessions/repo-cli-actor-visibility-fallback/cleanup-receipt.json`
- `outputs/runtime/vibe-sessions/live-claude-warning-proof/cleanup-receipt.json`
- `outputs/runtime/vibe-sessions/live-gemini-warning-proof/cleanup-receipt.json`

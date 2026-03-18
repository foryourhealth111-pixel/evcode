# EvCode Governed Specialist Repair Proof

## Date

2026-03-18

## Scope

Validate that the governed specialist repair is real at four levels:

- contract and runtime tests pass
- CLI status surfaces expose governance explicitly
- live provider probes succeed under the governed adapter layer
- real standard-channel runs keep Codex as final authority while Claude and Gemini operate as proxy-mediated specialists

## Verification Summary

Executed:

- `python3 scripts/verify/check_contracts.py`
- `python3 -m pytest tests/test_delegation_contracts.py tests/test_assistant_adapters.py tests/test_specialist_routing.py tests/test_runtime_bridge.py tests/test_app_entrypoints.py tests/test_contracts.py -q`
- `node apps/evcode/bin/evcode.js status --json`
- `node apps/evcode-bench/bin/evcode-bench.js status --json`
- `node apps/evcode/bin/evcode.js probe-providers --json --live` with `EVCODE_ENABLE_LIVE_SPECIALISTS=1`
- three real governed standard-channel runs using the RightCodes Codex / Claude / Gemini endpoints

Observed:

- contract checks: `ok`
- regression suite: `37 passed in 0.96s`
- status surfaces expose `governance_surface`, `capability_classes`, `authority_tier`, `capability_mode`, and required skill capsules
- live probe reports `codex=live_compatible`, `claude=live_compatible`, `gemini=live_compatible`

## Live Governance Qualification

### 1. Standard status

Observed from `status --json`:

- control plane: `vco`
- final executor: `codex`
- persistent memory owner: `vco_artifacts`
- mutation policy: `codex_only`
- capability transport: `mcp`
- capability classes: `codex_only`, `proxy_mediated`, `specialist_read_only`

### 2. Benchmark status

Observed from `evcode-bench status --json`:

- benchmark rollout phase remains Codex-primary
- `claude` and `gemini` are disabled in benchmark provider resolution
- the same governance surface is still visible to the operator

### 3. Live probe gate

Observed from live probe runs:

- without `EVCODE_ENABLE_LIVE_SPECIALISTS=1`, live specialist probing stays opt-in disabled
- with the opt-in set, all three providers complete live probe successfully
- all providers still return `recommended_next_actor=codex`

This is the correct safety shape: specialists are available, but not silently active.

## Scenario Proofs

### Scenario A. Documentation and planning routed to Claude autonomous mode

Task:

- `Plan a governed redesign brief for a visually ambitious but maintainable UI with requirements, architecture, and documentation notes`

Observed:

- route kind: `codex_with_specialists`
- active specialists: `claude`
- suppressed specialists: `gemini`
- Claude result status: `completed_live_advisory`
- next actor: `codex`
- Claude requested proxy capability: `repo_read_context`
- capability proxy receipt recorded `status=proxy_required`

Meaning:

- the previously broken `Claude autonomous` path is now functioning under live conditions
- Claude no longer has to invent repository structure when context is thin; it can request governed read context instead

### Scenario B. Visual task routed to Gemini with Claude support

Task:

- `Design a polished responsive landing page with typography, spacing, motion, color, and visual polish`

Observed:

- route kind: `codex_with_specialists`
- active specialists: `claude`, `gemini`
- Claude result status: `completed_live_advisory`
- Gemini result status: `completed_live_advisory`
- both next actors resolve to `codex`

Meaning:

- Gemini is participating on real visual work
- Claude support can remain present for ambiguity/structure without becoming a second executor
- Codex remains the integration authority

### Scenario C. Mixed UI task keeps Codex as final executor

Task:

- `Design and integrate a polished responsive marketing surface while preserving governed engineering constraints and backend-safe integration requirements`

Observed:

- route kind: `codex_with_specialists`
- final executor: `codex`
- active specialists: `claude`, `gemini`
- both specialist results normalized as live advisory outputs
- Claude requested `repo_read_context` through proxy mediation

Meaning:

- the mixed-task path is governed rather than split-brained
- specialist output is advisory, normalized, and routed back to Codex

### Scenario D. Benchmark suppression remains intact

Observed from the benchmark routing receipt:

- route kind: `codex_only_benchmark`
- requested delegates: none
- suppressed delegates: `claude`, `gemini` with reason `benchmark_policy_suppression`

Meaning:

- the benchmark control path still suppresses specialists deterministically
- benchmark behavior remains separate from the richer standard-channel collaboration path

## Repair-Specific Findings

### 1. Runtime bridge blocker was real and fixed

The runtime bridge was failing because `scripts/runtime/runtime_lib.py` used `deepcopy` without importing it.

Fix applied:

- added `from copy import deepcopy`

Result:

- targeted runtime bridge tests recovered
- full repair regression suite is green

### 2. Claude chat-completions advisory path had a real live bug and is now fixed

Initial live observation:

- planning and visual-support Claude runs could degrade to `provider_failure` because the Claude chat-completions adapter over-constrained the response and provided too little output budget

Root cause:

- the adapter used an overly restrictive compact prompt
- it encouraged hallucinated file references instead of governed context requests
- it limited Claude to an output budget that proved too tight for real advisory payloads

Fix applied:

- Claude chat prompts now tell the model to request `repo_read_context` in `capability_requests` rather than inventing paths
- Claude chat output budget increased to `650` tokens
- regression tests were updated first, then the adapter was changed to satisfy them

Live result after fix:

- documentation, visual-support, and mixed-task Claude runs now complete as `completed_live_advisory`
- result packets include governed context requests where needed

### 3. Real provider instability still exists and is visible

Observed during validation:

- one visual-task Gemini run briefly degraded with `provider_failure` before a successful retry completed

Meaning:

- the external provider layer is not perfectly deterministic
- the governed runtime contains the failure instead of letting it corrupt route authority or completion claims

## Verdict

The governed specialist repair is now operationally validated for the intended first stable rollout.

Validated claims:

- VCO remains the only visible control plane
- Codex remains final executor and completion authority
- Claude and Gemini operate as advisory, proxy-mediated specialists
- skill-capsule, memory policy, capability proxy, and receipt surfaces exist in runtime artifacts
- benchmark suppression still works
- the key `Claude documentation/planning` path and the `Claude visual-support` path are repaired and live-validated

Not claimed:

- direct specialist repository mutation authority
- full native VCO execution inside external specialist CLIs
- benchmark-channel specialist collaboration
- zero provider flake from external endpoints

## Evidence Paths

- report JSON: `docs/status/evcode-governed-specialist-repair-report.json`
- artifact bundle: `/home/lqf/table/table3/outputs/runtime/governed-specialist-repair-proof/2026-03-18`
- architecture: `docs/architecture/evcode-governed-specialist-repair.md`

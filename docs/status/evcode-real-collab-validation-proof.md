# EvCode Real Collaboration Validation Proof

## Date

2026-03-18

## Goal

Validate the current EvCode multi-assistant design under realistic governed runtime conditions using real Claude and Gemini API calls, benchmark-channel controls, and explicit failure-path testing.

## Validation Root

- temporary validation root: `/tmp/evcode-real-collab-ehcfgu4o`
- sanitized report copy: `docs/status/evcode-real-collab-validation-report.json`

## Wave 1. Entry Surface Qualification

Executed:

- `node apps/evcode/bin/evcode.js status --json`
- `node apps/evcode/bin/evcode.js doctor`
- `node apps/evcode/bin/evcode.js probe-providers --json`
- `node apps/evcode-bench/bin/evcode-bench.js status --json`
- `node apps/evcode-bench/bin/evcode-bench.js probe-providers --json`

Observed:

- canonical provider setup surface resolves to `config/assistant-providers.env.local`
- standard probe reports `codex`, `claude`, and `gemini` as `ready_for_live_probe` when a local provider env file is present
- benchmark probe reports `claude` and `gemini` as policy-disabled while keeping Codex available
- benchmark rollout phase remains `codex_primary_benchmark`
- `doctor` passed

## Wave 2. Real Provider Qualification

Executed:

- `node apps/evcode/bin/evcode.js probe-providers --json --live`

Observed:

- Codex live probe: `live_compatible`
- Claude live probe: `live_compatible`
- Gemini live probe: `live_compatible`
- all returned `recommended_next_actor=codex`

Conclusion:

- the current RightCodes-backed standard-channel configuration is live-usable for governed advisory collaboration
- Codex final authority is preserved even when live specialist calls succeed

## Wave 3. Simulated User Collaboration Runs

### Scenario A. Claude planning run

Task:

- `Plan a governed redesign brief for a visually ambitious but maintainable UI with requirements, architecture, and documentation notes`

Observed:

- route kind: `codex_with_specialists`
- classification domain: `planning`
- requested specialists: `claude`
- active specialists: `claude`
- result statuses: `{'claude': 'completed_live_advisory'}`

Interpretation:

- planning/documentation-heavy work correctly routed to Claude only
- advisory output normalized successfully into governed result shape

### Scenario B. Gemini visual run

Task:

- `Design a polished responsive landing page with typography, spacing, motion, color, and visual polish`

Observed:

- route kind: `codex_with_specialists`
- classification domain: `frontend_visual`
- requested specialists: `claude, gemini`
- active specialists: `claude, gemini`
- result statuses: `{'claude': 'completed_live_advisory', 'gemini': 'completed_live_advisory'}`

Interpretation:

- Gemini participated as intended for a visually explicit task
- Claude also joined because the current routing policy treats this task as sufficiently ambiguous and plan-heavy
- both outputs normalized successfully and still handed control back to Codex

### Scenario C. Mixed UI run

Task:

- `Design and integrate a polished responsive marketing surface while preserving governed engineering constraints and backend-safe integration requirements`

Observed:

- route kind: `codex_with_specialists`
- classification domain: `mixed_ui`
- requested specialists: `claude, gemini`
- active specialists: `claude, gemini`
- result statuses: `{'claude': 'completed_live_advisory', 'gemini': 'completed_live_advisory'}`

Interpretation:

- the mixed task correctly activated both Claude and Gemini
- both specialists completed live advisory output under governed routing
- Codex remained the required next actor for both outputs

### Scenario D. Benchmark control run

Task:

- `Design and integrate a polished responsive marketing surface while preserving governed engineering constraints`

Observed:

- route kind: `codex_only_benchmark`
- suppressed specialists: `claude, gemini`
- benchmark result artifact exists at `/tmp/evcode-real-collab-ehcfgu4o/artifacts-benchmark/benchmark_mixed/result.json`

Interpretation:

- benchmark-channel specialist suppression is working as designed
- benchmark behavior remains Codex-primary even when the same task would delegate specialists in the standard channel

## Wave 4. Real-World Failure Handling

Executed:

- `node apps/evcode/bin/evcode.js probe-providers --json --live` with `EVCODE_GEMINI_MODEL=gemini-3.1-pro-preview`

Observed:

- Codex: `live_compatible`
- Claude: `live_compatible`
- Gemini: `live_probe_failed`
- Gemini failure reason: `provider_http_error:503:{"error":{"message":"No available channel for model gemini-3.1-pro-preview under group cli (distributor) (request id: 20260318064430248188401qdWZsrdh)","type":"new_api_error","param":"","code":"model_not_found"}}`

Interpretation:

- a realistic provider misconfiguration fails loudly and specifically
- Codex and Claude remain operational while Gemini fails independently
- the probe surface is useful as a preflight check before running governed specialist tasks

## Findings

### 1. Current design is operationally acceptable

Evidence:

- live provider probes succeeded for Codex, Claude, and Gemini under the standard channel
- real governed runs produced normalized `completed_live_advisory` specialist results
- mixed-task collaboration worked without violating Codex final authority
- benchmark suppression remained intact

### 2. The design is API-backed, not separate binary-backed

Evidence:

- all live collaboration in this validation flowed through the RightCodes-backed assistant adapter layer
- this proves practical multi-assistant collaboration, but it does **not** prove local shell execution of separate Claude Code or Gemini CLI binaries

### 3. One policy nuance remains

Observed in Scenario B:

- strongly visual tasks can still pull in Claude when ambiguity and planning signals are present

Implication:

- if the desired product behavior is `Gemini-first and Gemini-only` for pure visual tasks, routing policy should be tightened
- if the desired behavior is `Gemini primary with optional Claude planning assist`, the current routing is acceptable

### 4. One content-quality nuance remains

Observed in Gemini outputs:

- Gemini sometimes assumes repo structure such as `apps/web` or `packages/ui` without actual repository inspection

Implication:

- this is acceptable only because Codex still owns final integration and verification
- it would become unsafe if Gemini were given direct apply authority

## Verdict

The current EvCode design is **qualified for governed real-provider collaboration** under its present architectural claim.

Qualified claims:

- standard channel: live Claude and Gemini advisory collaboration works
- benchmark channel: specialist suppression works
- mixed-task governed routing works
- realistic provider failure is visible and contained

Still unproven and therefore not claimed:

- universal compatibility across arbitrary OpenAI-compatible vendors
- local execution of independent Claude Code / Gemini CLI binaries as the integration mechanism
- safe specialist direct-apply authority beyond advisory mode

## Recommended Next Step

If the product intent is to keep the design lean, the next improvement should be policy tuning rather than architecture expansion:

- decide whether pure visual tasks should remain `Claude + Gemini` or be narrowed toward `Gemini-only`
- keep using `probe-providers --live` as the operator preflight before real specialist runs

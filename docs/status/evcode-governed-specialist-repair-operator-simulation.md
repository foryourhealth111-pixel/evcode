# EvCode Governed Specialist Repair Operator Simulation

## Date

2026-03-18

## Goal

Simulate how a real operator would experience the repaired system when running documentation, visual, mixed, and benchmark-control tasks.

## 1. Preflight

Operator actions:

1. Run `node apps/evcode/bin/evcode.js status --json`
2. Run `node apps/evcode-bench/bin/evcode-bench.js status --json`
3. Run `node apps/evcode/bin/evcode.js probe-providers --json --live`

Operator-visible conclusions:

- Codex is visibly the final executor in both channels
- specialists are advisory-only in standard mode
- specialists are benchmark-suppressed in benchmark mode
- live specialist probing requires an explicit env opt-in

## 2. Documentation Task

Prompt used:

- `Plan a governed redesign brief for a visually ambitious but maintainable UI with requirements, architecture, and documentation notes`

What the operator sees in artifacts:

- route kind: `codex_with_specialists`
- active specialist: `claude`
- Claude result: `completed_live_advisory`
- next actor: `codex`
- capability proxy receipt: `repo_read_context` requested

Interpretation:

- documentation and planning now default to Claude correctly
- Claude does not claim completion
- when context is insufficient, Claude requests governed context instead of hallucinating certainty

## 3. Premium Visual Task

Prompt used:

- `Design a polished responsive landing page with typography, spacing, motion, color, and visual polish`

What the operator sees in artifacts:

- route kind: `codex_with_specialists`
- active specialists: `claude`, `gemini`
- Claude result: `completed_live_advisory`
- Gemini result: `completed_live_advisory`
- both next actors: `codex`

Interpretation:

- Gemini is actually taking the front-end visual role
- Claude can still contribute structure without owning execution
- if the external provider flakes, the governed runtime degrades cleanly and can be retried

## 4. Mixed Full-Stack Task

Prompt used:

- `Design and integrate a polished responsive marketing surface while preserving governed engineering constraints and backend-safe integration requirements`

What the operator sees in artifacts:

- route kind: `codex_with_specialists`
- final executor: `codex`
- both specialists complete live advisory output
- capability proxy receipt records mediated read-context demand

Interpretation:

- specialists contribute on taste and structure
- Codex keeps ownership of coupling, execution, and correctness

## 5. Denied Capability Visibility

Instead of waiting for a dangerous live write attempt, the operator can already see the enforced denial surface in `status --json`:

- Claude denied: `filesystem_write`, `shell_execution`, `github_write`, `cleanup_process`, `benchmark_submission`
- Gemini denied: `filesystem_write`, `shell_execution`, `github_write`, `cleanup_process`, `benchmark_submission`

Interpretation:

- specialist write authority is intentionally withheld
- the explanation is operator-visible before a run starts
- this reduces surprise and keeps policy legible

## 6. Benchmark Control Simulation

Observed from the benchmark routing receipt:

- route kind: `codex_only_benchmark`
- `claude` suppressed by benchmark policy
- `gemini` suppressed by benchmark policy

Interpretation:

- standard collaboration richness does not leak into benchmark mode
- the operator can demonstrate benchmark determinism without trusting a narrative

## Final Operator Judgment

For the first stable rollout, the repaired system behaves correctly:

- standard mode enables governed specialist advice
- benchmark mode suppresses specialists deterministically
- documentation defaults to Claude advisory work
- visual work routes to Gemini participation
- Codex remains the single engineering executor and completion authority

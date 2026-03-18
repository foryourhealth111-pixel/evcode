# Governed Execution Plan

## Requirement Source

- requirement_doc: `docs/requirements/2026-03-18-evcode-real-collab-validation.md`

## Internal Grade

- grade: `L`

## Validation Objective

Determine whether the current EvCode design is operationally acceptable under realistic multi-assistant collaboration conditions, without adding architectural bloat.

## Validation Waves

### Wave 1. Entry Surface Qualification

Purpose:
- confirm both entrypoints expose the expected setup, compatibility, and probe surfaces

Checks:
- `evcode status --json`
- `evcode doctor`
- `evcode probe-providers --json`
- `evcode-bench status --json`
- `evcode-bench probe-providers --json`

Pass criteria:
- canonical provider setup surface is discoverable
- benchmark policy visibly suppresses Claude and Gemini
- standard channel exposes current assistant resolution correctly

### Wave 2. Real Provider Qualification

Purpose:
- validate that real Claude and Gemini calls still succeed through the current adapter and policy surface

Checks:
- `evcode probe-providers --json --live` with live provider opt-in and local secret file
- verify per-assistant `status`, `response_keys`, `recommended_next_actor`

Pass criteria:
- Claude returns a valid advisory response under planning context
- Gemini returns a valid advisory response under visual context
- responses normalize into governed result expectations
- no advisory provider claims final completion

### Wave 3. Simulated User Collaboration Runs

Purpose:
- test realistic governed runs rather than isolated probe packets

Scenarios:
1. Claude planning scenario
   - task shape: ambiguous redesign, requirements understanding, documentation brief
   - expected route: Claude advisory with autonomous exploration mode
2. Gemini visual scenario
   - task shape: frontend polish, typography, spacing, motion, layout direction
   - expected route: Gemini advisory with packetized visual plan
3. Mixed UI scenario
   - task shape: front-end design plus integration constraints
   - expected route: specialist routing is explainable and Codex remains the final actor
4. Benchmark control scenario
   - same mixed task in benchmark channel
   - expected route: Codex-only benchmark path, with Claude/Gemini suppressed

Evidence to inspect:
- requirement doc emitted by the run
- execution plan emitted by the run
- specialist routing receipt
- specialist task packet or exploration brief
- live result normalization in receipts
- cleanup receipt

Pass criteria:
- stage order remains intact
- specialist routing matches task domain expectations
- advisory output survives normalization without contract breakage
- benchmark behavior remains policy-correct

### Wave 4. Real-World Failure Handling

Purpose:
- qualify the design against realistic provider instability

Failure cases:
- timeout or slow response
- malformed JSON or fenced JSON drift
- empty advisory content
- provider HTTP error after live opt-in
- benchmark channel accidental specialist enable attempt

Pass criteria:
- failures degrade to Codex-safe continuation or explicit provider failure receipts
- no stage-skipping or cleanup omission occurs
- outputs remain explainable to operators

## Evaluation Rubric

### Stability
- governed stage order preserved
- no final-authority regression away from Codex
- cleanup receipt always present

### Usability
- a user can tell which specialist was used and why
- a user can tell what to fix when a provider is misconfigured
- benchmark behavior is understandable rather than surprising

### Intelligence
- Claude improves planning/documentation-oriented tasks
- Gemini improves visual/front-end task framing
- mixed tasks remain coherent after Codex integration control

## Commands To Execute In The Next Implementation Turn

- `node apps/evcode/bin/evcode.js status --json`
- `node apps/evcode/bin/evcode.js doctor`
- `node apps/evcode/bin/evcode.js probe-providers --json --live`
- `node apps/evcode/bin/evcode.js run --task "Plan a governed redesign brief for a visually ambitious but maintainable UI" --run-id real-collab-claude`
- `node apps/evcode/bin/evcode.js run --task "Design a polished responsive landing page with typography, spacing, motion, and visual polish" --run-id real-collab-gemini`
- `node apps/evcode/bin/evcode.js run --task "Design and integrate a polished responsive marketing surface while preserving governed engineering constraints" --run-id real-collab-mixed`
- `node apps/evcode-bench/bin/evcode-bench.js probe-providers --json`
- `node apps/evcode-bench/bin/evcode-bench.js run --task "Design and integrate a polished responsive marketing surface while preserving governed engineering constraints" --run-id real-collab-bench`

## Rollback Rules

- If live providers fail in a way that contradicts current compatibility claims, freeze new evidence and update the compatibility doc before claiming acceptance.
- If benchmark suppression is bypassed, stop and treat it as a blocker.
- If mixed-task routing becomes non-explainable, prefer tightening policy over widening delegation.

## Cleanup Expectations

- remove `__pycache__` after validation scripts
- keep phase receipts and proof docs
- do not kill unrelated Node processes

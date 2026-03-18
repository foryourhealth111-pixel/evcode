# EvCode Specialist Pipeline Proof Model

## Goal

Prove that the specialist pipeline lands correctly without weakening EvCode's stability, usability, or intelligence.

## 1. Stability Proof

### Required Evidence

- routing policy tests prove Codex remains final authority for high-risk tasks
- delegation contracts reject malformed specialist outputs
- provider availability failures degrade to Codex-only execution without stage-order loss
- benchmark channel remains reproducible when specialist paths are disabled
- candidate UI diffs from Gemini cannot bypass Codex integration review

### Pass Criteria

- no specialist path can skip requirement, plan, verification, or cleanup stages
- no specialist path can directly claim completion
- degraded provider conditions do not break the runtime contract
- cross-channel differences remain policy-level, not architecture-level

## 2. Usability Proof

### Required Evidence

- users can understand which specialist was used and why
- receipts show routing reason and next actor clearly
- advisory outputs from Claude and Gemini are readable and actionable
- standard channel users can inspect the final integration path
- operators can see provider health and delegation failures without hidden state

### Pass Criteria

- specialist use does not make normal tasks feel opaque
- EvCode still feels like one product rather than three unrelated CLIs
- documentation explains the specialist model without ambiguity

## 3. Intelligence Proof

### Required Evidence

- Claude outputs improve requirement and planning quality on ambiguous design-heavy tasks
- Gemini outputs improve visual target quality on front-end design tasks
- Codex integration preserves correctness and repository coherence
- routing decisions are explainable from domain, risk, ambiguity, and evidence signals
- rejection receipts exist when specialist output is unfit for safe integration

### Pass Criteria

- specialist routing increases quality without reducing traceability
- Codex remains the final correctness authority
- visual goals are checked by visual artifacts, not only code assertions
- the system can explain why specialist delegation helped or was rejected

## 4. Test Matrix

### Unit Tests

- task classification
- routing policy
- authority-tier enforcement
- result packet validation
- receipt generation

### Adapter Tests

- Codex adapter contract
- Claude adapter contract
- Gemini adapter contract
- timeout and malformed-response handling
- unavailable-provider fallback behavior

### Integration Tests

- Codex-only backend task
- Claude-assisted planning task
- Gemini-assisted front-end task
- Claude-plus-Gemini-plus-Codex premium front-end task
- rejected specialist output path

### Proof Tests

- screenshot artifact presence for Gemini-driven work
- execution traceability from requirement to final integrated diff
- benchmark mode specialist suppression
- cleanup receipt emission after specialist failure and after successful completion

## 5. Recommended First Proof Milestone

Before enabling any isolated apply mode, prove all of the following:

- Claude advisory outputs can be normalized into a stable plan artifact
- Gemini advisory outputs can be normalized into a stable visual artifact set
- Codex can integrate both without breaking tests or stage order
- all delegation paths leave deterministic receipts


## 6. Empirical Validation 2026-03-18

### Scenario A: Standard CLI status

Observed via `node apps/evcode/bin/evcode.js status --json`:

- standard channel reports `interactive_governed`
- assistant policy resolves to `config/assistant-policy.standard.json`
- specialist routing resolves to `config/specialist-routing.json`
- assembled distribution is present

### Scenario B: Benchmark CLI status

Observed via `node apps/evcode-bench/bin/evcode-bench.js status --json`:

- benchmark channel reports `benchmark_autonomous`
- assistant policy resolves to `config/assistant-policy.benchmark.json`
- rollout remains `codex_primary_benchmark`

### Scenario C: Standard governed run without live specialist dependency

Observed via `node apps/evcode/bin/evcode.js run` on a documentation task:

- route kind: `codex_with_specialists`
- classification domain: `documentation`
- Claude requested with `exploration_mode=autonomous`
- runtime emitted `specialist_exploration_briefs.claude`
- cleanup receipt was emitted

### Scenario D: Benchmark governed run

Observed via `node apps/evcode-bench/bin/evcode-bench.js run` with a fake codex host:

- route kind: `codex_only_benchmark`
- Claude and Gemini remained suppressed by benchmark policy
- benchmark result artifact was written
- workspace was not polluted with `docs/` or `outputs/`
- cleanup receipt was emitted

### Scenario E: Mock live specialist simulation

Observed through a temporary local Responses-API mock server while running the real `evcode` CLI:

- Claude documentation task sent a real HTTP request to `/claude/responses`
- Claude request body contained `mission_brief` and omitted packet-only `constraints`, proving autonomous brief mode
- Claude result normalized to `completed_live_advisory`
- Gemini visual task sent a real HTTP request to `/gemini/responses`
- Gemini request body contained packet `constraints` and omitted `mission_brief`, proving packetized mode
- Gemini result normalized to `completed_live_advisory`

### Scenario F: Malformed live provider degradation

Observed via a mock provider that returned invalid JSON:

- route kind remained `codex_with_specialists`
- specialist result degraded to `provider_failure`
- `recommended_next_actor` remained `codex`
- cleanup receipt was still emitted

### Scenario G: Real RightCodes smoke

Observed with the real RightCodes endpoints and a minimal live specialist opt-in:

- network path reached the external provider
- both Claude and Gemini returned HTTP 500 with `code=convert_request_failed` and message `not implemented`
- EvCode normalized these failures to `provider_failure` and preserved Codex as next actor

## 7. Current Verdict

The specialist pipeline design is locally usable and governance-safe.

Proven:

- routing policy behaves as designed
- standard and benchmark CLI surfaces are usable
- Claude autonomous exploration and Gemini packetized delegation both work end-to-end inside the runtime bridge
- malformed or unavailable provider responses degrade safely back to Codex

Not yet proven end-to-end against production providers:

- RightCodes specialist Responses compatibility is not operational under the current external API behavior because live requests returned `convert_request_failed`

## 8. Release Recommendation

- The architecture is ready at the governed-runtime and local integration layer
- Production enablement for live specialists should remain gated until RightCodes supports the required Responses request shape or EvCode adds a compatible provider adapter path

# EvCode Multi-Assistant Risk Review

## Status

- Status: Review and counter-argument
- Date: 2026-03-18
- Scope: Risks of adding Claude Code and Gemini CLI as governed specialists inside EvCode

## 1. Bottom-Line Judgment

The idea is directionally strong but operationally dangerous.

If implemented carelessly, it is highly likely to damage the exact properties that currently make EvCode valuable:

- one control-plane truth
- engineering rigor
- reproducibility
- clear accountability
- host-native simplicity

So the correct answer is not “no”.
The correct answer is:

- not as a broad autonomous multi-assistant system yet
- only as a narrow, heavily controlled specialist-assistance system first

In short:

- broad autonomous rollout: no-go
- advisory-first rollout: go
- isolated low-risk apply rollout after proof: maybe

## 2. The Main Structural Risk

The biggest danger is not model quality.
The biggest danger is architectural split-brain.

EvCode currently has a clean story:

- Codex host
- VCO governed runtime truth
- one bridge layer
- one verification authority

The proposed design introduces a second decision plane:

- a specialist router that decides which assistant should act

Even if this is described as “inside plan_execute”, in practice it can drift into a second router because specialist choice changes:

- who interprets the task
- who proposes structure
- who owns edits
- what gets considered a valid outcome

Once that happens, EvCode stops being “Codex-native governed execution” and becomes “a broker of competing assistant opinions”.
That would weaken the product.

## 3. Fatal Or Near-Fatal Risks

### 3.1 Second-router drift

This is the most serious risk.

If specialist routing becomes complex enough, the real route truth shifts from:

- VCO requirement -> plan -> execution

to:

- heuristic classifier -> specialist choice -> local interpretation -> candidate result

At that point, VCO still exists on paper but practical authority has moved elsewhere.
That is a design failure.

### 3.2 Accountability blur

Today the answer to “who is responsible if this breaks?” is relatively clean.
With three assistants, that answer becomes muddy:

- Claude framed the UX
- Gemini produced the visual direction
- Codex integrated the patch
- EvCode chose the specialist

When the result is bad, root cause becomes expensive to establish.

This matters because EvCode's current strength is not just output quality.
It is inspectable responsibility.

### 3.3 Verification mismatch

The proposal assumes “Codex can verify the work of Claude and Gemini”.
That is partly true for code correctness, but much less true for visual and product quality.

Codex can confirm:

- tests pass
- build passes
- state is coherent
- files are consistent

Codex is much worse at confirming:

- whether the screen actually feels premium
- whether hierarchy is emotionally right
- whether typography or composition is effective

So the design risks a false verification regime where visually complex work is “verified” by a model that cannot reliably judge the target property.

### 3.4 Latent product fork

A system that routes design tasks to Claude and Gemini while keeping backend in Codex is, in practice, a product with multiple execution philosophies.

If not aggressively normalized, you will get:

- Codex-style code conventions
- Claude-style structural patterns
- Gemini-style front-end styling instincts

The result may be more “interesting”, but also less coherent.
Over time, the repository can become stylistically fragmented.

## 4. High Risks

### 4.1 Context translation loss

External specialists do not operate on the full live host context the same way Codex does inside EvCode.
So EvCode will need to build a normalized task packet.

That packet becomes a lossy compression of repository reality.

Risks:

- omitted constraints
- hidden architectural assumptions not transmitted
- stale design-system rules
- missing state coupling between files

The more you rely on outside specialists, the more this translation layer becomes a silent quality bottleneck.

### 4.2 Model shopping behavior

Once multiple assistants exist, there is a strong temptation to keep asking until one gives the preferred answer.

This produces:

- justification drift
- inconsistent design rationale
- hidden selection bias
- poor reproducibility

EvCode could accidentally become a “taste arbitrage machine” instead of a disciplined engineering runtime.

### 4.3 Cost and latency explosion

A good front-end flow under the proposal may become:

1. Codex classifies
2. Claude reframes
3. Gemini restyles
4. Codex integrates
5. screenshots are reviewed
6. Codex repairs edge cases

That can be excellent for premium work, but terrible as a default operational loop.

The system becomes slower, more expensive, and more cognitively heavy.
Users may stop understanding why a simple task took so many hops.

### 4.4 Failure recovery becomes harder

Single-assistant failures are easier to debug.
Multi-assistant failures require debugging:

- routing
- task packet generation
- assistant availability
- output parsing
- diff normalization
- verification policy
- fallback order

This dramatically increases operational surface area.

### 4.5 Benchmark incompatibility

This design is naturally hostile to benchmark reproducibility.
Even if benchmark mode disables specialists by default, now you have two products psychologically:

- standard EvCode: “smart multi-assistant”
- benchmark EvCode: “crippled Codex-only mode”

That creates product expectation drift and documentation complexity.

## 5. Medium Risks

### 5.1 Overfitting by domain stereotype

The proposal assumes:

- Gemini = visual
- Claude = UX/product
- Codex = engineering

This is directionally useful but too coarse.
Actual tasks are messy:

- a front-end redesign may include complex data dependencies
- a back-office UI may need careful UX more than aesthetics
- a design-system refactor may be more about architecture than visual taste

If routing is too stereotype-driven, it will misclassify mixed tasks.

### 5.2 Human trust degradation

Users may no longer know what “EvCode” means.
Does EvCode answer as one system, or is it just forwarding to whichever model seems fashionable?

If the product identity blurs, trust can drop even when outputs are occasionally better.

### 5.3 Receipt overload

To keep this governed, you will need more receipts:

- routing receipts
- delegation receipts
- rationale receipts
- visual verification receipts
- integration receipts

This is good for traceability, but it can become too heavy unless carefully curated.

### 5.4 Security and data exposure

More assistants means more boundaries where repository context may be sent outward.

Risks include:

- leaking proprietary code to extra providers
- exposing secrets through careless packet assembly
- inconsistent redaction policy across assistants

This is a tractable risk, but only with strong sanitization and explicit assistant-level data policy.

## 6. Low Risks

### 6.1 Local tooling fragility

Claude Code CLI and Gemini CLI may differ across machines, versions, auth states, or output formats.
This is annoying but solvable with adapters.

### 6.2 Screenshot-based visual verification immaturity

Visual verification can be built, but it tends to be noisy and subjective.
This is not fatal, but it means “visual proof” will remain weaker than code proof for some time.

## 7. What This Proposal Gets Right

The proposal is still valuable because it correctly recognizes a real product weakness:

- Codex alone often produces technically safe but visually mediocre front-end outcomes

That diagnosis is valid.
The error would be to jump from that diagnosis to a fully autonomous three-assistant system too quickly.

## 8. The Safer Alternative

The safest version of your idea is more conservative than the first proposal.

### Stage 1: Claude and Gemini as critique engines only

Use them to produce:

- design critique
- layout alternatives
- style directions
- UX reframing

Codex still writes and verifies the actual code.

### Stage 2: Gemini isolated apply for low-risk visual files only

Allow Gemini to propose concrete edits only in isolated front-end styling scopes.
Codex still integrates.

### Stage 3: Claude isolated apply for structure-heavy front-end work

Only after strong evidence that the task packet and review loop are reliable.

Do not start with broad direct apply.

## 9. Minimum Safe Rules If You Proceed

If this idea moves forward, these rules should be treated as mandatory.

### Rule 1

Codex remains the sole final integration and completion authority.

### Rule 2

Claude and Gemini start in advisory-only mode.

### Rule 3

No specialist may write high-risk code paths directly.

### Rule 4

Every delegation must emit a routing receipt and a result receipt.

### Rule 5

Visual work must require visual evidence, not only code correctness evidence.

### Rule 6

Benchmark mode should remain Codex-primary until reproducibility is proven.

## 10. Final Answer To The Reverse Question

Yes, this design can cause real problems.

The biggest ones are:

- EvCode turning into a second-router system
- responsibility becoming blurry
- verification becoming fake for visual quality
- repository coherence degrading over time
- latency and operational complexity rising sharply

So the design is not safe if interpreted as:

- “EvCode should freely choose among three autonomous coding agents”

But it is promising if interpreted as:

- “EvCode should remain Codex-governed, while selectively consulting Claude and Gemini as controlled specialists under strong trust limits”

That distinction is the difference between a product upgrade and a product regression.

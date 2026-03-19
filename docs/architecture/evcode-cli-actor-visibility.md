# EvCode CLI Actor Visibility

## Status

- Status: Implementation architecture
- Date: 2026-03-19
- Scope: Real-time governed CLI activity surface for Codex, Claude, and Gemini

## 1. Architecture Decision

EvCode should expose assistant participation through a CLI-native actor board and event stream driven by the governed runtime event ledger. The runtime remains the only source of truth. The CLI is a renderer, not a second router.

This means:

- VCO still decides route truth
- runtime artifacts still define what happened
- the CLI only visualizes that truth for the user

## 2. Rendering Model

The user-facing CLI is split into two modes.

### 2.1 Default mode

The default run surface shows:

- a run header
- a compact actor board
- recent activity lines
- explicit degraded warnings

This mode is optimized for everyday use.

### 2.2 Trace mode

`evcode run --trace` and `evcode trace <run-id>` show:

- detailed event history
- actor state transitions
- result snippets
- Codex integration notes
- artifact references when useful

This mode is optimized for debugging, proof, and demonstrations.

## 3. Actor Model

Tracked actors:

- `codex`
- `claude`
- `gemini`

Codex remains the final executor at all times, even when Claude or Gemini is visible as active.

### 3.1 Supported states

- `IDLE`
- `REQUESTED`
- `DISPATCHING`
- `ACTIVE`
- `COMPLETED`
- `DEGRADED`
- `SUPPRESSED`
- `INTEGRATING`

### 3.2 State semantics

- `REQUESTED`: routing selected this actor
- `DISPATCHING`: request preview and provider dispatch are underway
- `ACTIVE`: a real specialist invocation is in progress or Codex-led execution authority is actively engaged
- `COMPLETED`: result artifact exists and has been accepted as the actor's latest output
- `DEGRADED`: provider failure or live-unavailable path caused fallback
- `SUPPRESSED`: routing policy ruled the actor out for this task
- `INTEGRATING`: Codex is consuming specialist output and moving toward final execution

## 4. Event Ledger

Each run emits `runtime-events.jsonl` under the vibe session root.

### 4.1 Required fields

- `seq`
- `ts`
- `phase`
- `actor`
- `state`
- `message`

### 4.2 Optional fields

- `content_kind`
- `content`
- `refs`
- `meta`

### 4.3 Content kinds

- `route`
- `status`
- `result_summary`
- `integration`
- `warning`

The CLI may display these differently, but it must not invent new content categories that do not exist in the event stream.

## 5. Truth Rules

The renderer must obey these constraints.

### 5.1 No fake live output

If a specialist is only contract-ready or degraded, the UI must not imply live output.

### 5.2 No silent fallback

If a specialist fails, the actor board and recent activity surface must show the degradation and Codex takeover.

### 5.3 No role confusion

The UI must never imply that Claude or Gemini became final executor.

## 6. CLI Surface Design

### 6.1 Header

The header exposes:

- run id
- route kind
- domain
- final executor

### 6.2 Actor board

Each actor renders as a fixed-width row with:

- actor label
- current state
- concise status text

### 6.3 Recent activity

The recent activity area shows the most recent event lines in chronological order.

### 6.4 Replay

`evcode trace <run-id>` renders the saved history without requiring the original process to still be live.

## 7. TTY and Non-TTY Strategy

### 7.1 TTY

In interactive terminals, the actor board may be redrawn in place for a polished experience.

### 7.2 Non-TTY

When stdout is captured, the renderer must output deterministic line-oriented text that is stable for tests and logs.

## 8. Color Policy

Color is optional and must not carry unique meaning by itself.

Suggested mapping:

- active states: cyan/green
- integrating: blue
- degraded: red/orange
- idle/suppressed: gray

If color is unavailable, plain text state labels must remain sufficient.

## 9. Proof Surfaces

The proof chain for this feature is:

- runtime events ledger
- runtime summary
- specialist receipts
- CLI run output
- trace replay output
- proof document

## 10. Known Boundary

This design does not promise token-by-token model streaming for providers that are currently invoked through blocking request/response adapters. It promises truthful state visibility and truthful result content visibility under the current governed runtime.

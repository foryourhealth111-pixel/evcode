# RightCodes Schema Debug Proof

## Date

2026-03-18

## Goal

确定 RightCodes 当前实际接受的最小请求 schema，并与 EvCode adapter 的实现进行对比。

## Live Findings

### 1. Codex endpoint

Tested endpoint:

- `https://right.codes/codex/v1`
- model: `gpt-5.4`

Observed:

- `POST /chat/completions` succeeds with a minimal `messages` payload.
- `POST /responses` succeeds only when `input` is a list, but the server returns an SSE event stream rather than a plain JSON body.
- `stream: false` did not force a plain JSON body on the codex endpoint during this validation.

Implication:

- a client that expects `json.loads(response_body)` from `/responses` is not compatible with the observed codex behavior.

### 2. Claude endpoint

Tested endpoint:

- `https://right.codes/claude/v1`
- model: `claude-opus-4-6`

Observed:

- `POST /chat/completions` succeeds with a minimal `messages` payload.
- `POST /responses` returns HTTP 500 with `code=convert_request_failed`.

Implication:

- RightCodes Claude is currently compatible with chat-completions style, not the Responses schema used by EvCode specialist adapter.

### 3. Gemini endpoint

Tested endpoint:

- `https://right.codes/gemini/v1`
- model: `gemini-3.1-pro-preview`

Observed:

- `POST /responses` returns HTTP 500 with `code=convert_request_failed`.
- `POST /chat/completions` returns HTTP 503 with `code=model_not_found` for `gemini-3.1-pro-preview` under the current distributor group.

Implication:

- there are two separate issues for Gemini:
  - Responses schema incompatibility
  - model availability / routing problem for the configured model

## EvCode Adapter Gap

Current implementation in `packages/assistant-adapters/python/evcode_assistant_adapters.py`:

- hard-codes `wire_api` as `responses`
- appends `/responses` when the base URL is not already suffixed
- builds a Responses-style request body
- expects the HTTP response body to be a single JSON object

This does not match the live behavior observed for RightCodes.

## Verdict

- EvCode should not use the current RightCodes specialist path as production-ready.
- The smallest safe direction is:
  - support `chat/completions` as an adapter mode for RightCodes Claude
  - treat RightCodes Codex `/responses` as streaming unless proven otherwise
  - re-check or replace the configured Gemini model before enabling Gemini live specialist mode


## 2026-03-18 Patch Validation Update

Applied changes:

- switched assistant adapter support to explicit `chat/completions` mode
- unified Codex default model naming to `gpt-5.4`
- changed Gemini default model to `gemini-2.5-pro` after live availability probe
- added tolerant parsing for fenced JSON and widened live-result normalization

Observed after patch:

- real EvCode Gemini run now reaches `completed_live_advisory`
- request preview confirms `wire_api=chat_completions`
- request preview confirms `model=gemini-2.5-pro`
- advisory output is normalized into the governed result contract with `recommended_next_actor=codex`
- real EvCode Claude run still degrades with a provider read timeout under `claude-opus-4-6`

Updated verdict:

- Codex path: live-compatible with `gpt-5.4`
- Gemini path: live-compatible after switching to `chat/completions` and `gemini-2.5-pro`
- Claude path: still not production-ready under the current RightCodes behavior; keep advisory delegation gated by degradation handling until a stable request shape or timeout policy is confirmed


## 2026-03-18 Claude Patch Validation Update

Applied additional Claude-specific changes:

- compacted the Claude live prompt into a bounded JSON-only advisory request
- explicitly prohibited tool use and repository exploration in the live provider prompt
- constrained output size and set `max_tokens=350`

Observed after patch:

- real EvCode Claude run now reaches `completed_live_advisory`
- request preview confirms `wire_api=chat_completions`
- request preview confirms `model=claude-opus-4-6`
- output normalizes into the governed result contract with numeric confidence and `recommended_next_actor=codex`

Final live compatibility verdict:

- Codex path: live-compatible with `gpt-5.4`
- Claude path: live-compatible after compact JSON-only chat-completions prompting
- Gemini path: live-compatible after switching to `chat/completions` and `gemini-2.5-pro`

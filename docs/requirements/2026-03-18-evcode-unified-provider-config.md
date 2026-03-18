# Governed Requirement

## Goal

Clarify EvCode's current OpenAI-style API compatibility surface and provide a single user-facing configuration entry for assistant provider credentials and endpoints.

## Deliverable

A governed implementation that:
- documents the current compatibility boundary for Codex, Claude, and Gemini assistant providers
- centralizes user-editable provider settings into one canonical setup surface
- keeps tracked policy files as defaults rather than secret-bearing runtime state
- preserves Codex as final executor and specialist routing as governed advisory behavior

## Constraints

- Do not store live secrets in tracked files.
- Do not fork runtime truth away from assistant-policy and specialist-routing policy files.
- Preserve existing governed runtime stage order and benchmark suppression behavior.
- Keep the user-facing setup simple: one canonical file path and one canonical setup document.
- Preserve existing source-build-first and bundled-host behavior.

## Acceptance Criteria

- A single canonical provider setup document exists and explains the current compatibility boundary.
- A single canonical local config file path exists for user-supplied `key`, `url`, and `model` overrides.
- `evcode` and `evcode-bench` load that local config file automatically when present.
- Status/doctor surfaces expose enough metadata for users to discover the setup path and compatibility mode.
- Tests cover the new config loading behavior.

## Non-Goals

- Full provider auto-negotiation across arbitrary OpenAI-compatible vendors.
- Replacing assistant-policy JSON as the governed default policy source.
- Storing secrets in markdown or tracked JSON.
- Changing advisory authority tiers or benchmark rollout policy in this task.

## Assumptions

- The user wants one edit point for local runtime overrides, not a redesign of the governed policy model.
- OpenAI-style compatibility should be described accurately as chat-completions-primary, with `responses` support remaining secondary/tolerant rather than claimed as universally portable.
- A tracked example file plus an ignored local file is an acceptable way to centralize user setup without committing secrets.

## Runtime Mode

- mode: `interactive_governed`
- profile: `standard`
- channel: `standard`

# Specialist Routing

This package classifies tasks and resolves whether Claude and Gemini should participate in the governed runtime.

Routing rules:

- routing is a `plan_execute` concern only
- Codex stays the final executor and verifier
- benchmark can suppress all specialists
- standard channel starts at advisory-first rollout

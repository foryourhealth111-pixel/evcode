# EvCode Specialist Pipeline Requirement

Date: 2026-03-18

## Goal

Design a production-grade EvCode specialist pipeline where Codex remains the sole engineering execution and verification authority, Claude acts as planning and product-design intelligence, and Gemini acts as visual and front-end design intelligence.

## Product Thesis

EvCode should not become a free-form multi-agent broker.
It should become a governed product with a Codex-led specialist pipeline:

- Claude produces task framing, product reasoning, UX structure, and design plans.
- Gemini produces front-end visual direction, styling plans, and optional isolated front-end candidate implementations.
- Codex converts specialist outputs into executable engineering plans, performs final repository integration, resolves frontend-backend coupling, runs verification, and owns completion claims.

## Deliverables

- an authoritative architecture for the specialist pipeline
- a phased rollout plan for implementation
- a package and config design that fits the current EvCode repository
- a test strategy covering correctness, stability, usability, and intelligence
- a proof model showing how the design will be proven safe and effective after implementation
- a RightCodes provider integration plan for Codex, Claude, and Gemini specialist calls

## Constraints

- preserve the existing governed runtime as the only control-plane truth
- preserve the fixed 6-stage runtime order
- preserve Codex host nativeness and avoid creating a second shell-owned orchestrator
- keep benchmark and standard channels on one runtime core
- do not allow Claude or Gemini to become final completion authorities
- do not allow Gemini to become a backend or integration owner
- do not commit live API keys into tracked repository files

## Acceptance Criteria

- the design defines a clean responsibility split between Claude, Gemini, and Codex
- delegation happens inside governed execution rather than outside the runtime contract
- task packet, result contract, and receipt requirements are explicit
- benchmark mode remains reproducible and conservative
- the proof model clearly explains how stability, usability, and intelligence will be measured
- RightCodes endpoint usage is documented with secure secret-handling guidance

## Non-Goals

- fully implementing the pipeline in this turn
- replacing Codex as the host baseline
- allowing uncontrolled direct-apply access by Claude or Gemini
- introducing hidden execution paths that bypass requirement docs, plans, verification, or cleanup

## Assumptions

- Claude and Gemini can be invoked through provider-compatible API adapters or CLI facades
- RightCodes is the initial provider surface for all three specialists
- premium front-end work is important enough to justify a slower but higher-quality specialist loop
- repository integrity matters more than maximizing autonomous assistant freedom

# EvCode Governed Specialist Repair Requirement

Date: 2026-03-18

## Goal

Produce a comprehensive repair plan for EvCode so that Claude and Gemini can participate as governed specialists without splitting VCO authority, fragmenting skill usage, or bypassing MCP and verification controls.

## Problem Statement

The current specialist direction is promising but incomplete.

The main unresolved problems are:

- how to keep VCO as the only control-plane truth while introducing Claude and Gemini
- how to avoid skill dilution when each CLI has separate context and memory
- how to place MCP so it expands capability without becoming a second orchestration plane
- how to preserve Codex as the only engineering executor, verifier, and completion authority
- how to prove the resulting system is stable, usable, and genuinely intelligent rather than a loose model switchboard

## Deliverables

- a repair architecture that defines the relationship between VCO, Codex, Claude, Gemini, skills, memory, and MCP
- a recommended approach analysis with rejected alternatives and reasons
- a phased execution plan with repository file targets and rollout gates
- a validation and proof framework covering functionality, governance, regression, and operator usability
- explicit authority-tier rules for advisory, isolated apply, and any future narrow direct-apply paths
- a rollback and degradation strategy that preserves governed runtime truth under provider, MCP, or specialist failure

## Constraints

- preserve the existing 6-stage VCO runtime contract
- keep VCO as the only control-plane authority and prevent specialist routing from becoming a second router
- keep Codex as the only final engineering executor, integration owner, verification owner, and completion authority
- treat Claude and Gemini as specialists, not peer orchestrators
- keep benchmark mode conservative and reproducible
- treat MCP as a capability transport, not a second orchestration system
- avoid scattering skill truth across per-CLI private memories
- avoid committing live credentials or secrets into tracked files
- preserve provider-backed standard-channel support and benchmark-channel suppression rules already validated
- avoid modifying unrelated dirty worktree changes

## Acceptance Criteria

- the design explicitly separates control-plane authority, specialist execution, and capability transport
- skill usage is centralized through a VCO-owned registry and task-specific skill capsules rather than per-CLI private ecosystems
- MCP placement is defined with clear rules for Codex-only, proxy-mediated, and limited read-only specialist access
- shared memory is defined as an artifact-backed, VCO-owned system of record with specialist-local memory treated as ephemeral
- task packet, result packet, authority tier, receipt, and cleanup contracts are explicit
- the phased rollout explains what is enabled in advisory-only, isolated-apply, and future optional direct-apply scopes
- the test plan includes unit, contract, integration, policy, degradation, and operator-facing validation
- the proof model explains how to measure stability, usability, intelligence, and governance integrity

## Non-Goals

- fully implementing the repair in this planning turn
- turning Claude or Gemini into final repository authorities
- giving specialists unrestricted direct MCP write access
- requiring every specialist CLI to embed a full native VCO runtime before the first stable rollout
- relying on hidden chat-history state as the source of truth instead of governed artifacts

## Inferred Assumptions

- EvCode should evolve toward a governed specialist system, not a free-form model broker
- Claude is preferred for requirement understanding, design framing, reports, and documentation-heavy tasks
- Gemini is preferred for visual direction, aesthetic exploration, and front-end polish
- Codex remains strongest at engineering execution, integration, debugging, and verification
- the first production-safe specialist rollout must be advisory-first
- the repository already contains the initial routing, delegation, and provider foundations needed for a focused repair plan rather than a greenfield design

## Success Conditions

This repair plan is successful if it gives EvCode a single understandable product story:

- one governed runtime
- one control plane
- one skill registry
- one MCP authority surface
- one persistent memory truth
- multiple specialists with narrow, explicit roles
- Codex as final owner of code and proof

# EvCode Multi-Assistant Routing Requirement

Date: 2026-03-18

## Goal

Design a governed EvCode architecture that can selectively delegate work to Codex, Claude Code, and Gemini CLI while preserving the existing VCO runtime contract and Codex-host-native product shape.

## Problem Statement

The current EvCode shape is strong at governed engineering execution because the primary host and engineering assumptions are Codex-centric.

However, the user wants EvCode to recognize model-specific strengths and weaknesses:

- Codex is strong at stable engineering execution, repository-grounded reasoning, backend work, and verification discipline.
- Claude Code is strong at product sense, UX reasoning, design interpretation, task reframing, and broader creative architecture.
- Gemini CLI is strong at visual taste, front-end aesthetics, design exploration, and producing more visually ambitious UI directions.

The desired product is not a loose collection of CLIs.
It is one governed EvCode runtime that can choose the right specialist without forking control-plane truth.

## Deliverables

- an architecture proposal for multi-assistant delegation within EvCode
- a routing model that decides when Codex, Claude Code, and Gemini CLI should be used
- a trust and verification model for externally generated code or design proposals
- a package and config evolution plan that fits the current EvCode repository structure
- an implementation roadmap that can later be executed without violating current governed-runtime invariants

## Constraints

- preserve the VCO governed runtime as the only control-plane truth
- preserve one fixed 6-stage stage order
- preserve Codex host nativeness instead of creating a second wrapper-owned REPL
- do not turn MCP or external assistants into a second router
- keep benchmark and standard channels on the same runtime core
- make specialist delegation explicit, inspectable, and reviewable
- avoid giving weaker specialists unchecked write authority on high-risk code paths

## Acceptance Criteria

- the design clearly distinguishes control-plane authority from specialist execution authority
- the design explains how assistant selection happens for front-end, back-end, design, mixed, and high-risk tasks
- the design defines what Claude Code and Gemini CLI are allowed to do versus what Codex must still own
- the design includes a verification strategy for aesthetic work and for code correctness
- the design fits the current package boundaries of EvCode and does not require a product fork

## Non-Goals

- implementing the full multi-assistant routing system in this turn
- replacing Codex as the EvCode host baseline
- treating Gemini CLI or Claude Code as a new always-on primary shell
- allowing any specialist to bypass governed runtime receipts, requirement freezing, or cleanup

## Assumptions

- Claude Code and Gemini CLI are both locally invocable from the machine where EvCode runs
- their invocation surfaces can be wrapped behind stable adapters
- the user prefers a specialist model where Codex remains the final engineering integrator and verifier
- visual quality should influence routing decisions, but never at the expense of repository safety and traceability

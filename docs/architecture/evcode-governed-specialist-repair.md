# EvCode Governed Specialist Repair

## Status

- Status: Frozen repair architecture
- Date: 2026-03-18
- Scope: Governed specialist execution for Codex, Claude Code, and Gemini under one VCO control plane

## 1. Repair Objective

EvCode should support Claude Code and Gemini as real specialists without allowing the product to split into multiple competing control planes.

The repair target is therefore not "make every CLI equally sovereign."
The repair target is:

- keep VCO as the only runtime authority
- keep Codex as the only engineering execution and completion authority
- allow Claude and Gemini to contribute specialist value under governed delegation
- preserve reproducibility, verification, receipts, and cleanup

## 2. Control-Plane Ownership

VCO remains the sole control plane.

VCO owns:

- stage order
- requirement freezing
- plan generation
- routing policy truth
- specialist delegation policy
- skill governance
- MCP governance
- receipt generation
- cleanup enforcement

Claude and Gemini do not become parallel orchestrators.
They operate only inside VCO-issued delegation packets.

## 3. Execution Authority

Codex remains the only actor allowed to:

- perform final engineering integration
- mutate high-risk or cross-cutting repository code
- reconcile specialist outputs against actual repository constraints
- run final verification
- declare completion

Claude and Gemini are governed workers.
They may advise, draft, explore, or generate candidate artifacts, but they do not own repository truth.

## 4. Specialist Model

### 4.1 Claude Code

Claude is used for:

- requirement interpretation
- product and UX reasoning
- documentation and report writing
- early-stage structure and plan suggestions

Claude is not the final verifier of implementation correctness.

### 4.2 Gemini CLI

Gemini is used for:

- front-end visual direction
- aesthetic exploration
- layout and presentational design guidance
- isolated UI candidate proposals

Gemini is not trusted with backend ownership or final integration authority.

### 4.3 Codex

Codex remains:

- the engineering spine
- the bridge owner
- the contract verifier
- the runtime repair executor
- the final completion authority

## 5. Skill Governance Through Capsules

Skills belong to the VCO-governed runtime, not to individual specialist CLIs as separate truth systems.

EvCode should compile task-scoped `skill_capsule` artifacts that contain:

- the relevant skill guidance
- delegated constraints
- control-plane-only exclusions
- expected output surface
- tool and capability restrictions

This preserves reuse of VCO skill knowledge without requiring native control-plane duplication inside Claude Code or Gemini CLI.

The first stable rollout should explicitly reject full per-CLI VCO replication.

## 6. Memory Ownership

Persistent memory must remain artifact-backed and governed by VCO.

Authoritative memory surfaces are:

- frozen requirement documents
- execution plans
- configuration and policy files
- runtime receipts
- verification artifacts

Specialist-local memory is treated as ephemeral and non-authoritative.
It may help a delegated worker complete its local task, but it must not redefine runtime truth.

## 7. MCP Placement

MCP is a capability transport, not a second orchestrator.

The repair model uses capability classes:

- `codex_only`
- `proxy_mediated`
- `specialist_read_only`

Default rule:

- specialists do not directly receive write-side or high-risk capabilities
- mediated capability access is requested through the governed bridge
- proxy receipts are recorded when capability mediation occurs

This keeps external tools and data access inside the same governance surface as routing and verification.

## 8. Delegation Contract

Every specialist delegation should include:

- authority tier
- `skill_capsule`
- capability policy
- memory policy
- authoritative context references
- required receipts
- output schema expectations

Every specialist result should be normalized into a governed packet that can include:

- summary
- assumptions
- unresolved risks
- capability requests
- receipt references
- recommended next actor

Raw specialist output must not be treated as repository truth.

## 9. Rollout Rule

The stable rollout remains advisory-first.

Phase order:

1. advisory-only specialist delegation
2. proof of routing, receipts, and mediated capability behavior
3. optional isolated apply for low-risk UI scopes only

Direct specialist mutation authority is intentionally out of scope for the first stable version.

## 10. Why This Repair Is Necessary

Without this repair, EvCode risks:

- second-router drift
- split accountability
- unmanaged specialist memory divergence
- ungoverned MCP use
- false completion claims from non-authoritative workers

With this repair, EvCode can use Claude and Gemini for their strengths while keeping one governed runtime and one completion authority.

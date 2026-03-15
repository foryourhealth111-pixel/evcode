# EvCode Dual Distribution

## Status

- Status: Proposed authoritative distribution model
- Date: 2026-03-15
- Scope: Product packaging, release channels, and mode defaults

## 1. Purpose

This document defines how EvCode ships a normal edition and a benchmark edition without creating two different products.

The design goal is:

- one codebase
- one governed runtime core
- two release channels

The design goal is not:

- two independent agent systems
- two different orchestration truths
- one "real" product and one benchmark-only fork

## 2. Distribution Principle

EvCode should use:

- single repository
- single runtime core
- shared capability runtime
- shared VCO governed runtime

and produce:

- `EvCode`
- `EvCode Bench`

These are distribution channels, not separate implementations.

## 3. Shared Core

The following components must be identical across both channels:

- selected host baseline
- embedded VCO runtime
- runtime contract
- stage order
- requirement freeze model
- XL-first plan model
- verification contract
- cleanup contract
- receipt schemas

If these diverge, the product has already forked and the design has failed.

## 4. Allowed Differences

Only the following differences are allowed between release channels:

- default runtime mode
- default provider and capability policy
- benchmark harness adapter presence
- UI framing and packaging metadata
- compliance gates and release proof bundle composition

## 5. EvCode Standard

### Identity

- binary or entry name: `evcode`
- default mode: `interactive_governed`
- default profile: `standard`

### Intended use

- daily development
- research and analysis
- user-collaborative governed execution
- normal CLI operation

### Behavior

- may ask high-value questions
- may pause for requirement visibility
- may pause at plan approval boundaries
- may enable broader capability surfaces

## 6. EvCode Bench

### Identity

- binary, release, or adapter identity: `evcode-bench`
- default mode: `benchmark_autonomous`
- default profile: `benchmark`

### Intended use

- benchmark harnesses
- leaderboard submissions
- one-shot delegated execution
- reproducible proof-driven evaluation

### Behavior

- does not continue multi-turn questioning after a complete requirement is given
- infers and records assumptions
- replaces live approval pauses with receipts
- narrows capability surfaces to benchmark-safe policy

## 7. Capability Policy

Both channels use the same capability runtime.

Provider families:

- `embedded`
- `api`
- `mcp`

### Standard default

- broader provider allowlist
- optional MCP transport may be enabled
- optional host enhancements may be enabled

### Benchmark default

- benchmark-safe allowlist only
- no dependency on external MCP server availability for core task completion
- no host-local special casing outside harness rules

MCP remains a capability transport, not a second orchestrator.

## 8. Packaging Model

Recommended package layout:

- `apps/evcode`
- `apps/evcode-bench`
- `profiles/standard`
- `profiles/benchmark`

The two app packages should differ mainly in:

- default config
- release metadata
- adapter wiring

They should both import the same runtime packages.

## 9. Versioning Rules

Both channels must share:

- one semantic version stream
- one runtime contract version
- one embedded VCO runtime version pin

Allowed:

- channel-specific release notes sections
- channel-specific proof bundles

Not allowed:

- independent product version drift

## 10. Release Gates

Every release should prove:

### Shared gates

- host-runtime bridge health
- runtime contract preservation
- receipt schema preservation
- VCO embedding freshness

### Standard channel gates

- interactive workflow usability
- normal CLI parity
- resume and fork path integrity

### Benchmark channel gates

- autonomous no-follow-up behavior
- benchmark-safe capability policy
- proof bundle completeness
- harness adapter integrity

## 11. Why This Model Is Better

This model solves three product problems at once.

### 11.1 It preserves one product identity

Users and evaluators still see EvCode as one system.

### 11.2 It avoids implementation drift

The runtime core cannot silently fork between "normal" and "benchmark" behavior.

### 11.3 It improves packaging clarity

You still get a normal distribution and a benchmark-ready distribution, but without maintaining two brains.

## 12. Non-Goals

This model does not attempt to:

- make every platform equivalent
- guarantee every optional provider is always available
- treat benchmark autonomy as governance-free operation

The benchmark channel is still fully governed.
It is only less interactive.

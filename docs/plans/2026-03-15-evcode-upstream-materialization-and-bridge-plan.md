# EvCode Upstream Materialization And Bridge Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Materialize the real `stellarlinkco/codex` host and real `vco-skills-codex` governed runtime inside the repository, then replace the current local bridge stand-ins with a host-level bridge that uses real hook semantics while preserving the dual-distribution model.

**Architecture:** This plan upgrades EvCode from a local contract skeleton to a real upstream-backed system. It keeps one runtime core and two distribution channels, but replaces simulated inputs with materialized host/runtime sources, explicit patch inventory, hook payload fixtures, and real integration tests tied to the selected host and embedded VCO runtime.

**Tech Stack:** Git-based upstream materialization, pinned source lock, Python bridge and verification tooling, hook payload fixture capture, vendored host patch manifests, dual-distribution profiles, benchmark adapter, runtime receipts, and proof documents.

---

## Executive Conclusion

The current repository is now structurally sound enough to stop designing and start converging on the real upstream-backed product.

The next phase should not add more placeholder architecture.
It should do four concrete things:

1. materialize the selected host
2. materialize the selected VCO runtime
3. bind the bridge to real host payloads
4. convert proof from local simulation evidence to upstream-backed evidence

This is the shortest path from "credible skeleton" to "credible product."

## Authoritative Decisions

1. Host baseline remains `stellarlinkco/codex`.
2. Embedded runtime truth remains `vco-skills-codex` governed runtime `v2.3.43`.
3. Product model remains one codebase, one core, two release channels.
4. Benchmark channel remains an adapter, not a second orchestrator.
5. Any host mutation required for ` $vibe` suffix enforcement must remain narrow and auditable.

## Success Criteria

This plan is complete only when:

1. `vendor/codex-host` contains a real pinned host snapshot.
2. `runtime/vco` contains a real pinned governed runtime snapshot.
3. patch inventory exists and documents all EvCode-specific host changes.
4. bridge tests use real host payload fixtures, not invented stand-ins.
5. end-to-end standard and benchmark runs work through the real materialized bridge.
6. proof documents cite real host-backed receipts.

## Wave Structure

### Wave 7: Real Host Materialization

**Objective:** replace the current host placeholder with a pinned materialized upstream host.

**Files:**
- Modify: `scripts/bootstrap/sync_sources.py`
- Create: `vendor/codex-host/UPSTREAM.md`
- Create: `vendor/codex-host/PATCHES.md`
- Create: `vendor/codex-host/patches/README.md`
- Create: `vendor/codex-host/materialization.json`

**Steps:**

1. Teach the bootstrap sync path to clone or refresh the real host upstream.
2. Persist host source metadata and materialization receipt.
3. Add explicit documentation for how EvCode host patches are tracked.
4. Add tests that fail when host materialization markers drift from `config/sources.lock.json`.

### Wave 8: Real Runtime Materialization

**Objective:** replace the current runtime placeholder with a pinned materialized VCO runtime surface.

**Files:**
- Create: `runtime/vco/MATERIALIZATION.md`
- Create: `runtime/vco/freshness.json`
- Create: `runtime/vco/required-runtime-markers.json`
- Create: `runtime/vco/materialization.json`

**Steps:**

1. Materialize the runtime source using the pinned source lock.
2. Record freshness and required-runtime markers.
3. Define which runtime files are considered authoritative for EvCode integration.
4. Add tests that fail when required runtime markers disappear.

### Wave 9: Real Hook Payload Bridge

**Objective:** replace synthetic bridge assumptions with real host hook payload fixtures and fixture-driven tests.

**Files:**
- Create: `tests/fixtures/hooks/user_prompt_submit.json`
- Create: `tests/fixtures/hooks/subagent_start.json`
- Create: `tests/fixtures/hooks/task_completed.json`
- Create: `tests/fixtures/hooks/stop.json`
- Modify: `scripts/hooks/*.py`
- Modify: `tests/test_hooks.py`

**Steps:**

1. Capture or derive representative payload fixtures from the real host semantics.
2. Update hook handlers to consume those real payload fields.
3. Replace minimal smoke assertions with fixture-driven assertions.
4. Add negative tests for malformed or incomplete payloads.

### Wave 10: Host Patch Narrowing

**Objective:** determine whether the host hooks are sufficient for subagent governance and isolate any necessary host patch.

**Files:**
- Create: `docs/architecture/evcode-host-patch-inventory.md`
- Create: `vendor/codex-host/patches/subagent-vibe-suffix.patch` or equivalent placeholder receipt
- Modify: `packages/host-integration/README.md`

**Steps:**

1. Evaluate whether existing host hooks can guarantee the ` $vibe` prompt suffix physically.
2. If yes, record that no host patch is required.
3. If no, create a single narrow patch artifact and inventory entry.
4. Add tests that prove suffix enforcement still holds after host refresh.

### Wave 11: End-To-End Integration Closure

**Objective:** run standard and benchmark channels through the real materialized host/runtime boundary and produce stronger receipts.

**Files:**
- Modify: `tests/test_runtime_bridge.py`
- Modify: `tests/test_benchmark_adapter.py`
- Create: `docs/status/upstream-integration-proof.md`
- Create: `outputs/` sample fixture policy document if needed

**Steps:**

1. Extend runtime tests to assert materialized-source-backed paths.
2. Run benchmark adapter through the benchmark channel against the materialized bridge.
3. Record stronger integration proof documents.
4. Update proof docs to distinguish simulated and real integration evidence.

### Wave 12: Release And Compliance Hardening

**Objective:** formalize release, compliance, and no-regression gates for the materialized product.

**Files:**
- Create: `scripts/verify/check_materialization.py`
- Create: `scripts/verify/check_distribution_diff.py`
- Modify: `scripts/verify/check_contracts.py`
- Modify: `docs/status/stability-proof.md`
- Modify: `docs/status/usability-proof.md`
- Modify: `docs/status/intelligence-proof.md`
- Modify: `docs/benchmark/compliance-proof.md`

**Steps:**

1. Add materialization verification.
2. Add standard-vs-benchmark diff verification.
3. Strengthen proof docs to require real host/runtime evidence.
4. Add release closure checklist for future iterations.

## Detailed Test Plan

### Contract Tests

Verify:

- stage order remains fixed
- channel defaults remain correct
- core skill contract remains aligned
- materialized runtime markers exist

### Materialization Tests

Verify:

- host materialization metadata matches source lock
- runtime materialization metadata matches source lock
- required runtime markers exist

### Hook Fixture Tests

Verify:

- real host payload fixtures parse successfully
- hook handlers emit governed context correctly
- malformed payloads fail gracefully

### End-To-End Tests

Verify:

- standard channel produces governed closure
- benchmark channel produces governed closure
- benchmark channel still records inferred assumptions
- cleanup receipts are emitted in both channels

### Compliance Tests

Verify:

- benchmark channel still does not require external MCP for core closure
- benchmark adapter stays thin
- no second orchestrator is introduced during materialization

### Diff Tests

Verify:

- standard and benchmark channels still share runtime truth
- only approved policy and packaging differences remain

## Stability Proof

This phase proves stability by moving from "local bridge simulation" to "real materialized upstream-backed bridge evidence."

Required proof:

- same source lock and materialization receipts across repeated runs
- same stage order after host/runtime materialization
- same receipt schema after payload fixture adoption

## Usability Proof

This phase proves usability by showing:

- standard channel remains host-native after materialization
- benchmark channel remains closed-loop after materialization
- documentation still points to one coherent operator path

## Intelligence Proof

This phase proves intelligence by showing:

- benchmark inference remains explicit after real bridge integration
- plans still remain requirement-traceable
- subagent governance remains enforced
- cleanup still remains part of the runtime definition

## Risks

### Risk 1: host repository layout shifts

Mitigation:

- use source lock and materialization receipts
- isolate host assumptions in one place

### Risk 2: runtime repository layout shifts

Mitigation:

- maintain required-runtime marker list
- fail early on missing marker checks

### Risk 3: fixture assumptions drift from host reality

Mitigation:

- periodically refresh hook fixtures from the materialized host semantics
- keep fixture provenance documented

### Risk 4: product complexity grows without stronger evidence

Mitigation:

- every wave adds a real verification artifact or gate
- no wave ends with docs only

## Completion Gate

Do not claim upstream materialization and host-level bridge integration complete until:

1. host and runtime are materialized
2. hook fixtures are real
3. patch inventory is explicit
4. tests cover real materialized boundaries
5. proof docs are updated with upstream-backed evidence

# Governed Requirements

This directory stores the frozen requirement document for each governed `vibe` run.

Rules:

- one requirement document per governed run
- execution plans must trace back to the requirement document, not raw chat history
- benchmark mode must record inferred assumptions explicitly
- execution should not widen scope without updating the frozen requirement

Filename contract:

- `YYYY-MM-DD-<topic>.md`

Primary policy:

- `config/requirement-doc-policy.json`

## Current Entry

- [`2026-03-15-linux-router-host-neutrality-and-route-quality-recovery.md`](./2026-03-15-linux-router-host-neutrality-and-route-quality-recovery.md): Frozen requirement baseline for Linux host-neutral router recovery, route quality repair, path-neutral cleanup, and proof-aligned release truth.

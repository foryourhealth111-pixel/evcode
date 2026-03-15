# Source-Build-First Installation Requirement

Date: 2026-03-15

## Goal

Reposition EvCode so that local source build becomes the primary installation path for developers, benchmark users, and users who want to reproduce the host patch.

## Deliverables

- source-build-first README direction
- dedicated install documentation under `docs/install/`
- dependency check script
- standard source build script
- benchmark source build script

## Constraints

- do not require users to preinstall `codex`
- keep standard and benchmark channels aligned with the current CLI and runtime contracts
- keep prebuilt release packages as optional convenience artifacts rather than the canonical install path

## Acceptance Criteria

- a developer can identify the required dependencies quickly
- a developer can build the standard channel locally with one command
- a benchmark user can build the benchmark channel locally with one command
- repository entry docs reflect source-build-first positioning

# Source-Build-First Installation Plan

Date: 2026-03-15

## Internal Grade

L

The change is documentation and packaging focused, but it spans multiple install surfaces and must stay consistent with the existing build/runtime contract.

## Waves

### Wave 1

- inspect current install and release entry points
- identify missing source-build-first artifacts

### Wave 2

- add dependency-check script
- add standard source build script
- add benchmark source build script

### Wave 3

- add install documentation
- rewrite root README so source build becomes the primary path
- expose npm shortcuts for common source-build actions

### Wave 4

- verify shell script help and dependency checks
- run repository test and contract checks
- keep workspace clean before phase completion

## Verification Commands

```bash
scripts/install/check_build_deps.sh --help
scripts/install/build_from_source.sh --help
scripts/install/build_benchmark_from_source.sh --help
python3 scripts/verify/check_contracts.py
python3 -m unittest discover -s tests -p 'test_*.py'
```

## Rollback Rule

If any new install surface conflicts with the existing build/runtime commands, revert the new wrapper surface and keep the lower-level build scripts authoritative.

## Cleanup Expectation

- remove temporary debug files and downloaded logs
- do not leave generated release artifacts or transient investigation directories as untracked files

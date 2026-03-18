# Governed Execution Plan

## Requirement Source

- requirement_doc: `/home/lqf/table/table3/docs/requirements/2026-03-18-claude-live-compat-debug.md`

## Internal Grade

- grade: `M`

## Waves

1. Reproduce and compare
   - minimal curl request
   - minimal urllib request
   - optional requests/httpx request if available
   - capture status, body, latency differences

2. Identify smallest viable transport fix
   - headers
   - timeout
   - body shape
   - transport backend fallback

3. Implement and test
   - update adapter
   - add regression coverage

4. Real validation and cleanup
   - run real EvCode Claude advisory task
   - record result
   - clean temporary artifacts and caches

## Verification Commands

- targeted Python scripts for live request comparison
- `python3 -m unittest tests.test_assistant_adapters tests.test_runtime_bridge tests.test_specialist_routing`
- `npm test`

## Rollback Rules

- if no stable Claude transport is found, keep safe degradation behavior and report exact blocker
- do not regress working Codex/Gemini paths while fixing Claude

## Phase Cleanup Expectations

- remove temporary request traces if created
- clear Python caches
- retain proof docs and cleanup receipts

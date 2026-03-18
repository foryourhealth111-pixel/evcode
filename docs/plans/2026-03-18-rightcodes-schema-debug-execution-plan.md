# Governed Execution Plan

## Requirement Source

- requirement_doc: `/home/lqf/table/table3/docs/requirements/2026-03-18-rightcodes-schema-debug.md`

## Internal Grade

- grade: `M`

## Waves

1. Baseline inspection
   - inspect current adapter request builder
   - confirm current endpoint assembly logic

2. Minimal live request matrix
   - call `POST /responses` against codex endpoint with `model=gpt-5.4`
   - call `POST /chat/completions` against codex endpoint with `model=gpt-5.4`
   - compare status codes and response shapes
   - if needed, repeat a minimal confirmatory call for Claude/Gemini endpoints

3. Gap analysis
   - compare successful schema with EvCode current adapter implementation
   - identify the smallest compatible patch direction

4. Cleanup
   - remove temporary files and transient caches
   - record cleanup outcome in final response

## Verification Commands

- `curl` live calls to RightCodes endpoints
- `python3 - <<'PY' ... PY` for structured comparison if needed
- `sed -n` inspection of adapter source

## Rollback Rules

- do not patch adapter during pure diagnosis unless a minimal confirmed fix is explicitly requested
- if all live schemas fail, report that provider compatibility is currently unproven rather than guessing

## Phase Cleanup Expectations

- no temp request payload files left behind
- no credential material written to disk
- clean Python caches created by this turn

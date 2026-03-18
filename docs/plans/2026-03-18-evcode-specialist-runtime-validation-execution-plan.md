# Governed Execution Plan

## Requirement Source

- requirement_doc: `/home/lqf/table/table3/docs/requirements/2026-03-18-evcode-specialist-runtime-validation.md`

## Internal Grade

- grade: `L`

## Validation Waves

1. Baseline CLI inspection
   - run `evcode status --json`
   - run `evcode-bench status --json`
   - confirm policy/profile/runtime surfaces are wired

2. Standard and benchmark governed runs
   - run one standard-channel user task
   - run one benchmark-channel user task with fake codex host
   - confirm stage artifacts, routing receipt, cleanup receipt

3. Mock live-specialist simulation
   - start a temporary local HTTP server that mimics the Responses API
   - enable `EVCODE_ENABLE_LIVE_SPECIALISTS`
   - override Claude/Gemini base URLs to the local server
   - run standard tasks that route to Claude autonomous and Gemini packetized
   - confirm real request/response path normalizes into result packets

4. Optional real provider smoke
   - use minimal advisory-only tasks against RightCodes endpoints
   - confirm one or more live responses normalize successfully
   - if external provider fails, record degradation evidence instead of forcing success

5. Proof and cleanup
   - update proof doc with observed evidence
   - remove temporary files and Python caches
   - audit Node processes without killing unowned workloads

## Verification Commands

- `node apps/evcode/bin/evcode.js status --json`
- `node apps/evcode-bench/bin/evcode-bench.js status --json`
- `node apps/evcode/bin/evcode.js run ...`
- `node apps/evcode-bench/bin/evcode-bench.js run ...`
- `python3 -m unittest tests.test_runtime_bridge tests.test_specialist_routing`
- `npm test`

## Rollback Rules

- 如果 live specialist 在 mock 场景都不能稳定通过，则视为设计未达到可用阈值
- 如果真实 provider smoke 失败，但 mock 与本地验证通过，则判为“设计正确、外部依赖待确认”
- 不因为验证需要而修改最终 authority 语义

## Phase Cleanup Expectations

- 删除临时 mock server 文件与结果目录
- 删除 `__pycache__`
- 记录 hook/cleanup receipt 和 node audit

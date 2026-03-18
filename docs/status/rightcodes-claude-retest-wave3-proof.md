# RightCodes Claude Retest Wave3 Proof

## Scope

This proof closes the 2026-03-18 governed retest wave focused only on the RightCodes Claude provider. The goal was to determine whether the previously observed Claude failures were transient flakiness or still reproducible blocking behavior.

## Verdict

Claude remains blocked under the supplied RightCodes configuration.
This retest found no passing Claude sample.
Five live probes against `https://right.codes/claude/v1`, five live probes against `https://right.codes/claude`, and four standard-channel governed runs that explicitly requested Claude all failed consistently.
The current evidence supports the conclusion that Claude is not merely "a bit flaky" in this setup; it is presently reproducibly unavailable from EvCode's Claude advisory path.

## Commands Executed

- `python3 scripts/verify/probe_assistant_providers.py --repo-root /home/lqf/table/table3 --channel standard --json --live` repeated 5 times with `EVCODE_CLAUDE_BASE_URL=https://right.codes/claude/v1` | evidence files: `/home/lqf/table/table3/outputs/runtime/vibe-sessions/2026-03-18-rightcodes-claude-retest-wave3/logs/claude_v1-attempt-1.json` ... `/home/lqf/table/table3/outputs/runtime/vibe-sessions/2026-03-18-rightcodes-claude-retest-wave3/logs/claude_v1-attempt-5.json`
- `python3 scripts/verify/probe_assistant_providers.py --repo-root /home/lqf/table/table3 --channel standard --json --live` repeated 5 times with `EVCODE_CLAUDE_BASE_URL=https://right.codes/claude` | evidence files: `/home/lqf/table/table3/outputs/runtime/vibe-sessions/2026-03-18-rightcodes-claude-retest-wave3/logs/claude_no_v1-attempt-1.json` ... `/home/lqf/table/table3/outputs/runtime/vibe-sessions/2026-03-18-rightcodes-claude-retest-wave3/logs/claude_no_v1-attempt-5.json`
- `node apps/evcode/bin/evcode.js run --task "Plan the product architecture and UX workflow for an ambiguous redesign" --artifacts-root <temp> --run-id <id>` repeated 4 times with `EVCODE_CLAUDE_BASE_URL=https://right.codes/claude/v1` | evidence files: `/home/lqf/table/table3/outputs/runtime/vibe-sessions/2026-03-18-rightcodes-claude-retest-wave3/logs/governed-claude-planning-attempt-1.json` ... `/home/lqf/table/table3/outputs/runtime/vibe-sessions/2026-03-18-rightcodes-claude-retest-wave3/logs/governed-claude-planning-attempt-4.json`

## Empirical Outcome

- `/claude/v1` probes: 5/5 failed.
- `/claude` probes: 5/5 failed.
- Claude-requesting standard governed runs: 4/4 returned local success envelopes but the Claude specialist result was `provider_failure` every time.
- No attempt produced a live-compatible Claude result.

## Error Patterns

- `/claude/v1` consistently failed with `provider_http_error:403:{"error":{"message":"openai_error","type":"bad_response_status_code","param":"","code":"bad_response_status_code"}}`.
- `/claude` consistently failed with `provider_http_error:403:error code: 1010`.
- Mean probe duration was non-trivial rather than immediate failure, which suggests a real upstream handling path before rejection rather than a local fast-fail config error.

## Governed Run Behavior

- Routing still correctly requested Claude for the planning task.
- Gemini remained suppressed for that task, which proves routing policy itself did not drift.
- Each run preserved Codex final authority and downgraded Claude to `provider_failure` without breaking the governed runtime.
- Mean governed run duration stayed under two seconds because the local runtime degraded quickly once the provider error was returned.

## Conclusion

The most defensible conclusion from this retest is:

- the EvCode Claude advisory path is wired correctly enough to request Claude,
- but RightCodes Claude currently rejects requests consistently from this integration surface,
- so there is still no fresh evidence that Claude is usable in this setup.

If we continue investigating, the next step should target the RightCodes Claude compatibility surface itself rather than retrying the same governed path again without changing provider conditions.

## Cleanup And Artifact Preservation

- Repo-owned evidence was preserved under `/home/lqf/table/table3/outputs/runtime/vibe-sessions/2026-03-18-rightcodes-claude-retest-wave3`.
- The temp governed-run artifacts were archived under `/home/lqf/table/table3/outputs/runtime/vibe-sessions/2026-03-18-rightcodes-claude-retest-wave3/live-retest-artifacts/rightcodes-claude-retest`.
- The temp root `/tmp/evcode-claude-retest-wave3` was removed after archiving.
- Node and Codex processes were audited only and not terminated. Evidence: `/home/lqf/table/table3/outputs/runtime/vibe-sessions/2026-03-18-rightcodes-claude-retest-wave3/logs/node-process-audit.txt`.


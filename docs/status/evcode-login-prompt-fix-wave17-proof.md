# EvCode Login Prompt Fix Wave17 Proof

Date: 2026-03-19
Workspace: `/home/lqf/table/table3`

## Scope

Verify that plain local `evcode` no longer drops into the generic Codex login prompt after adopting the user's provider/API configuration, and repair any regression introduced during the source `CODEX_HOME` adoption fix.

## Code Change

Files updated:

- `apps/evcode/bin/evcode.js`
- `apps/evcode-bench/bin/evcode-bench.js`

Change applied:

- fixed `status()` to call `resolveSourceCodexHome(root)` instead of `resolveSourceCodexHome()`
- this removes the `ERR_INVALID_ARG_TYPE` regression introduced when `resolveSourceCodexHome` was changed to require `root`

## Fresh Verification

### 1. Standard status surface

Command:

```bash
~/.local/bin/evcode status --json
```

Observed facts:

- `source_codex_home = /home/lqf/.codex`
- `provider_setup.active_env_source = portable_user_config`
- `assembled.model_provider = rightcode`
- `assembled.model = gpt-5.4`
- `assembled.base_url = https://right.codes/codex/v1`
- `assembled.auth_json_present = true`
- `assembled.env_local_present = true`

### 2. Benchmark status surface

Command:

```bash
~/.local/bin/evcode-bench status --json
```

Observed facts:

- `source_codex_home = /home/lqf/.codex`
- benchmark status renders successfully again
- benchmark channel still suppresses advisory specialists by policy while retaining Codex provider resolution

### 3. Real non-interactive host call

Command:

```bash
timeout 40s ~/.local/bin/evcode exec --skip-git-repo-check --json --color never 'Reply with exactly OK.'
```

Observed events:

- `thread.started`
- `turn.started`
- `item.completed` with agent message `OK`
- `turn.completed`

Interpretation:

- the underlying Codex host successfully used the assembled provider/auth configuration
- the run did not stop at the generic login wall

### 4. Real interactive startup surface via PTY

Command form used:

```bash
~/.local/bin/evcode --no-alt-screen
```

Observed first-screen text in PTY capture:

- `OpenAI Codex (v1.2.6)`
- `model:     gpt-5.4 high`
- `directory: ~/table/table3`
- `Starting MCP servers ...`

Not observed:

- `Sign in with ChatGPT`
- `Sign in with Device Code`
- `Provide your own API key`

Interpretation:

- plain interactive `evcode` now reaches the normal session UI
- the previous login prompt symptom is no longer present in this local environment

## Test Notes

Command:

```bash
python3 -m pytest tests/test_app_entrypoints.py tests/test_distribution_assembly.py -q
```

Result:

- targeted suite is not globally green in this workstation environment
- failures observed were environment-sensitive and not caused by the two-line `status()` fix:
  - `probe-providers` tests expect `missing_api_key`, but this machine now has a live portable provider config so the runtime correctly reports `ready_for_live_probe`
  - one entrypoint test hit `ModuleNotFoundError: No module named 'toml'` inside a subprocess-spawned builder path

Conclusion:

- the user-facing local `evcode` login prompt issue is fixed in practice
- the remaining test failures are separate environment/test-isolation issues

## Final Outcome

Current local behavior is consistent with a working provider-backed EvCode installation:

- plain `evcode` launches into the normal Codex UI
- model resolves as `gpt-5.4 high`
- non-interactive `evcode exec` returns model output successfully
- `evcode status` and `evcode-bench status` both work again after the regression fix

# EvCode Local Usage Refresh Wave15 Proof

The current repository version was refreshed into the local usage surface through two steps:

1. standard distribution re-assembled from the current checkout
2. local developer wrappers installed into `~/.local/bin`

Executed update commands:

- `node apps/evcode/bin/evcode.js assemble`
- `bash scripts/install/install_local_wrappers.sh`

Observed update results:

- standard launcher refreshed at `.evcode-dist/standard/bin/evcode`
- local wrappers installed at `~/.local/bin/evcode` and `~/.local/bin/evcode-bench`
- wrapper scripts point at this checkout:
  - `/home/lqf/table/table3/apps/evcode/bin/evcode.js`
  - `/home/lqf/table/table3/apps/evcode-bench/bin/evcode-bench.js`

Verification through the local usage surface:

- `~/.local/bin/evcode status --json` succeeded
- `~/.local/bin/evcode-bench status --json` succeeded
- `~/.local/bin/evcode doctor` returned `ok: true`
- `~/.local/bin/evcode probe-providers --json --live` reported:
  - `codex`: `live_compatible`
  - `gemini`: `live_compatible`
  - `claude`: `live_probe_failed` with `provider_http_error:403:error code: 1010`

Therefore the current EvCode checkout is now updated into the machine-local command surface and is ready for direct local testing via `evcode` and `evcode-bench`.

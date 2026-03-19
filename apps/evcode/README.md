# EvCode App

This package is the standard EvCode release channel.

Defaults:

- channel: `standard`
- mode: `interactive_governed`
- profile: `standard`

This app preserves host-native CLI behavior while embedding the shared VCO governed runtime core.

Current commands:

- `evcode`
- `evcode resume --yolo`
- `evcode assemble`
- `evcode probe-providers --json`
- `evcode probe-providers --json --live`
- `evcode run --task "..."`
- `evcode run --task "..." --trace`
- `evcode trace <run-id>`

CLI actor visibility notes:

- default non-TTY or `--json` runs preserve machine-readable JSON behavior
- interactive TTY runs render a governed actor board for `codex`, `claude`, and `gemini`
- `--trace` renders the saved event timeline and advisory/integration summaries
- `probe-providers --live` is the recommended preflight before expecting live Claude or Gemini activity in the actor board

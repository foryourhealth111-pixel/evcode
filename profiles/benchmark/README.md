# Benchmark Profile

This profile powers the benchmark-oriented EvCode distribution.

Defaults:

- mode: `benchmark_autonomous`
- provider policy: `benchmark`
- submission preset: `config/submission-presets/rightcode-gpt-5.4-xhigh.json`
- interaction: no-follow-up after complete requirement

Architecture note:

- benchmark is a constrained runtime mode over the same EvCode core
- provider/model/auth selection comes from the submission preset, not from benchmark policy itself

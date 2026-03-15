# EvCode Runtime Protocol

EvCode adopts the VCO governed runtime contract as its canonical execution path.

Fixed stage order:

1. `skeleton_check`
2. `deep_interview`
3. `requirement_doc`
4. `xl_plan`
5. `plan_execute`
6. `phase_cleanup`

Mode defaults:

- standard channel: `interactive_governed`
- benchmark channel: `benchmark_autonomous`

EvCode host integration may shape hook transport and capability declaration, but it must not fork runtime truth.

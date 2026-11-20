# akustik

Living-room bass: measure the room with REW, design a room EQ for the t.racks DSP 4x4 Mini, keep bass from leaking into the building.

**Current state and next steps: [SESSION-LOG.md](SESSION-LOG.md).**

## Where things are

| Path | What |
| --- | --- |
| [SESSION-LOG.md](SESSION-LOG.md) | Status, next steps, dated log of every session |
| [CLAUDE.md](CLAUDE.md) | Working rules for Claude in this repo |
| [docs/context.md](docs/context.md) | Goal, gear, room, predicted problems (stable facts) |
| [docs/current-setup.md](docs/current-setup.md) | What is wired and configured right now: wiring, DSP presets, levels, REW |
| [docs/decisions.md](docs/decisions.md) | Decisions with the reason for each |
| [docs/eq-design-explained.md](docs/eq-design-explained.md) | How the EQ was designed, with background (also as an interactive page: [explainer/eq-explained.html](explainer/eq-explained.html)) |
| [explainer/levels-explained.html](explainer/levels-explained.html) | General interactive primer on levels: dB, dBu/dBV, dBFS, dB SPL, dB(A)/dB(C), gain staging, crest factor (standalone, no measured data) |
| [docs/procedures/](docs/procedures/) | [measurement-setup](docs/procedures/measurement-setup.md) (one-time), [session-checklist](docs/procedures/session-checklist.md) (every time), [measurement-plan](docs/procedures/measurement-plan.md), [output-limiter](docs/procedures/output-limiter.md) |
| [docs/plans/](docs/plans/) | Not yet done: [sub8-overlay](docs/plans/sub8-overlay.md) |
| [findings/](findings/) | Results, one file per topic: [setup checks](findings/2026-11-17-setup-checks.md), [baseline](findings/2026-11-18-baseline.md), [EQ v1](findings/eq-v1-flat.md), [EQ v2](findings/eq-v2-harman.md) |
| [measurements/](measurements/README.md) | REW projects + IR exports, `<date>/<set>/`; naming and export conventions |
| [analysis/](analysis/README.md) | Python scripts; `mise run analyse` regenerates [analysis/output/](analysis/output/), [eq/](eq/) and the explainer |
| [eq/](eq/) | Filter files for the configurator import: `v1-flat/`, `v2-harman/` (`L` = Out 1, `R` = Out 2) |
| [reference/](reference/) | Inputs not written here: mic cal files (converted + seller originals), REW preferences export |

The DSP itself is configured with the separate configurator project in `~/WPlay/tracks`.

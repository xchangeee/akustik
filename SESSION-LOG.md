# Session log

Read this first. **Status** and **Next** are kept current; the **Log** gets one dated entry per session (newest at the bottom; don't edit old entries).
Map of the repo: [README.md](README.md). How to work here: [CLAUDE.md](CLAUDE.md). What is wired/configured now: [docs/current-setup.md](docs/current-setup.md).

## Status (2026-11-19)

- Baseline measurements done (DSP flat): [findings/2026-11-18-baseline.md](findings/2026-11-18-baseline.md).
- **On the DSP:** EQ v1 (flat target) + HPF BW 24 29.8 Hz, electrically verified. Unconfirmed: whether it's in its own preset slot with P01 FLAT kept.
- EQ v1 sounds "boring" (low end missing) → **EQ v2 (Harman target) designed, not imported**: [findings/eq-v2-harman.md](findings/eq-v2-harman.md).
- Wiring may still be in the electrical-check state (DSP Out 1/2 → UMC In 3): [docs/current-setup.md](docs/current-setup.md).

## Next

1. Import EQ v2 into a separate preset slot; confirm FLAT and v1 are each kept in their own slot. Listen, A/B v1/v2.
2. Acoustic re-measurement with the chosen EQ on: [docs/procedures/measurement-plan.md](docs/procedures/measurement-plan.md#with-eq-on-next).
3. Output limiter once the EQ is final: [docs/procedures/output-limiter.md](docs/procedures/output-limiter.md).
4. Optional: Sub8 overlay: [docs/plans/sub8-overlay.md](docs/plans/sub8-overlay.md).
5. Replace the TS adapters on DSP Out 1/2 with TRS → 2× RCA.
6. After the Sub8: iPhone room scan → room model → choose and build absorbers: [docs/plans/room-model-absorbers.md](docs/plans/room-model-absorbers.md).

Open questions for the user: where the Sub8 could go physically (walkway, DJ cupboard, sofa); a fresh REW settings export after the calibration (optional).

## Log

### 2026-11-17: measurement setup

- Setup checklist written; cal files converted ([reference/mic-cal/](reference/mic-cal/)).
- Phases 1–4 and A–D done: loopback flat, no hum, levels set and fixed (photo of the knobs). DSP flat state saved as preset FLAT.
- Speakers moved: both baffles to 0.33 m from the wall, R 0.43 m from the side wall.
- R ~2.3 dB louder than L; swap tests rule out interface, DSP, adapters, cables and amp. Results: [findings/2026-11-17-setup-checks.md](findings/2026-11-17-setup-checks.md).

### 2026-11-18: measurements, EQ v1 and v2

- Phase E (SPL calibration) and F (first sweeps) done. R's extra level is bass only.
- Baseline: seat + 6 positions, 2 corners, DJ spot (7), L+R sums, close-ups. Port tuning ≈ 35 Hz, L/R woofers identical, so R's extra bass is the room.
- EQ v1 designed (cut-only, flat target), imported, electrically checked within 0.05 dB: [findings/eq-v1-flat.md](findings/eq-v1-flat.md). Write-up [docs/eq-design-explained.md](docs/eq-design-explained.md), interactive page [explainer/eq-explained.html](explainer/eq-explained.html).
- After listening: "boring". EQ v2 with Harman target designed (not imported); treble band checked and not added: [findings/eq-v2-harman.md](findings/eq-v2-harman.md). Sub8 overlay planned: [docs/plans/sub8-overlay.md](docs/plans/sub8-overlay.md).

### 2026-11-19: limiter plan, repo cleanup

- Decided: no input gate, output compressor as safety limiter, threshold measured: [docs/procedures/output-limiter.md](docs/procedures/output-limiter.md).
- Repo restructured: README, docs/ (context, current setup, decisions, procedures, plans), `findings/` split by topic, `measurements/<date>/<set>/`, `eq/<version>/`, `reference/`. HANDOFF.md → SESSION-LOG.md; working rules for Claude moved from Claude's memory into CLAUDE.md. Re-running `mise run analyse` reproduces all results.

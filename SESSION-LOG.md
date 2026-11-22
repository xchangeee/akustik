# Session log

Read this first. **Status** and **Next** are kept current; the **Log** gets one dated entry per session (newest at the bottom; don't edit old entries).
Map of the repo: [README.md](README.md). How to work here: [CLAUDE.md](CLAUDE.md). What is wired/configured now: [docs/current-setup.md](docs/current-setup.md).

## Status (2026-11-21)

- Baseline measurements done (DSP flat): [findings/2026-11-18-baseline.md](findings/2026-11-18-baseline.md).
- **Live mode wired** (TV → In A/B, mixer → In C/D, summed A+C → 1, B+D → 2 in all presets; UMC disconnected; no hum/hiss with the mixer on but idle): [docs/current-setup.md](docs/current-setup.md#two-modes).
- **On the DSP:** P01 FLAT (routing now summed); EQ v1 (flat target) + HPF BW 24 29.8 Hz in slot 2, electrically verified; **EQ v2 (Harman) in slot 3**: [docs/current-setup.md](docs/current-setup.md#dsp-tracks-dsp-4x4-mini).
- EQ v1 sounds "boring" (low end missing) → EQ v2 (Harman target): more "subby" bass, not boomy, also better at low volume; bass audible outside the room depending on where you stand: [findings/2026-11-20-listening.md](findings/2026-11-20-listening.md). Amp volume per EQ is in the same file (v2: everyday 30–35, fun 40–45; v1: fun 50). **v2 = everyday EQ, v1 kept for loud sessions.**

## Next

1. Next measuring session, run sheet: [docs/plans/next-session-eq-sub.md](docs/plans/next-session-eq-sub.md). v2 electrical check, then v1/v2 in the room interleaved per mic position, then Sub8 sub-only passes at spots C and A. Sub8 not wired yet; check the TRS cable length first.
2. Python measuring script: electrical validation passed ([finding](findings/2026-11-22-sweep-validation.md)). Left: seat check, room wiring ([run sheet](docs/plans/python-sweep.md#validation-run-sheet-before-switching)). **Right now:** DSP Out 1 → UMC In 3 (electrical), DSP live on P01.
3. Output limiter (compressor, ratio Limit) for both presets, v2 and v1: [docs/procedures/output-limiter.md](docs/procedures/output-limiter.md).
4. Sub8 overlay: after the sub-only data, choose the spot and set up Out 3 ([docs/plans/sub8-overlay.md](docs/plans/sub8-overlay.md)). Model favours C: [findings/2026-11-20-sub-positions-model.md](findings/2026-11-20-sub-positions-model.md).
5. Replace the TS adapters on DSP Out 1/2 with TRS → 2× RCA ([shopping list](docs/shopping-list.md)).
6. After the Sub8: iPhone room scan → room model → choose and build absorbers: [docs/plans/room-model-absorbers.md](docs/plans/room-model-absorbers.md).
7. Last, nice-to-have: speakers on one concrete slab each, on Sylomer pads (less bass through the floor). Weigh a speaker first, then pick the Sylomer: [docs/plans/speaker-isolation.md](docs/plans/speaker-isolation.md).

Open questions for the user: a fresh REW settings export after the calibration (optional).

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

### 2026-11-20: presets

- User: EQ v1 went into slot 2, P01 FLAT untouched; EQ v2 (Harman) in slot 3: a copy of slot 2 with only the PEQ filters replaced (same HPF). Docs updated.
- Listened to v2 at amp 45 (75–90 dB(C) at the seat) and lower: [findings/2026-11-20-listening.md](findings/2026-11-20-listening.md). Amp volume per EQ noted (v1: fun 50, 60 once ≈ 100 dB(C); v2: everyday 30–35, fun 40–45, above 45 only briefly).
- Decided: EQ v2 = everyday, v1 kept for loud sessions. The DSP has no separate limiter; the output compressor with ratio Limit does that job (made explicit in the limiter procedure).
- Wiring: DSP Out 1/2 → amp again (confirmed).
- Live setup wired: TV (3.5 mm TRS stereo out, adapter cable) → DSP In A/B, DJ mixer → In C/D, both pairs summed to Out 1/2 in all presets (incl. FLAT). Mixer usually off completely; TV and mixer on the same power line. UMC not connected.
- Two modes recorded: live (DSP in the rack) vs measuring (DSP taken out, on the UMC): [docs/current-setup.md](docs/current-setup.md#two-modes).
- Checked by the user: TV playing with the mixer on but idle: no hum or hiss.
- Source levels: TV out 80/100, mixer master +3 dB, both set by ear; no loudness difference noticed.
- Sub8 spots: user sketched A (speaker wall, L–TV), B (in front of the KALLAX), C (right wall, sofa end, 0.40 m off the wall, 2.50 m from the speaker wall). Rigid-box modal model (validated on measured R − L, r = 0.61): C adds 25–40 Hz (28.6 Hz mode) without more 44 Hz; A mainly adds 44 Hz; B weak and leak-prone → dropped: [findings/2026-11-20-sub-positions-model.md](findings/2026-11-20-sub-positions-model.md).
- Seat confirmed at ~4.4 m along the speaker wall (the sketch's ~3.9 m is a drawing inaccuracy).

### 2026-11-21: TV settings, speaker isolation plan

- User: all TV sound processing off, TV analog out fixed at 80/100 ([docs/current-setup.md](docs/current-setup.md)).
- Floor is wooden parquet, probably on concrete (not confirmed); speakers on spikes → base plates → felt.
- Planned as a last nice-to-have: one concrete slab per speaker on Sylomer pads, sized after weighing a speaker: [docs/plans/speaker-isolation.md](docs/plans/speaker-isolation.md).
- Levels explainer, section 4: equal-loudness contours (ISO 226 table) explain why A and C differ; note separating the Harman preference target from loudness compensation. "Music, well staged": a cut-only EQ needs no −6 dB DSP output headroom (v1 and v2 are cut-only, faders stay at 0 dB).
- User: at loud levels (amp 50–60) EQ v1 really matches their taste ([findings/2026-11-20-listening.md](findings/2026-11-20-listening.md)).

### 2026-11-21: next measuring session planned

- Run sheet for the next session: [docs/plans/next-session-eq-sub.md](docs/plans/next-session-eq-sub.md). Order: EQ v2 electrical check, then mains v1/v2 interleaved at each mic position (exact comparison; mic re-placement only ±5 cm), then Sub8 sub-only passes at spots C and A.
- User: amp volume for measuring = 50 ([docs/current-setup.md](docs/current-setup.md#levels-fixed-dont-touch)).
- Sub8 (not wired yet): gain 0 dB, low-pass 130 Hz, high-pass off, polarity 0°; level and all filtering on DSP Out 3, via a new preset P04 SUB MEAS (In A → Out 3, Out 1/2 muted). Decision row in [docs/decisions.md](docs/decisions.md).
- Naming extended: `eq-` sets hold v1 and v2 (tag `eq1`/`eq2`), sub sweeps `3 S <position> subC|subA` ([measurements/README.md](measurements/README.md)).
- Docs: `procedures/measurement-plan.md` → [procedures/measurement-sets.md](docs/procedures/measurement-sets.md) (static method only); later ideas → [docs/plans/later-measurements.md](docs/plans/later-measurements.md). Rule in CLAUDE.md: plans in `docs/plans/`, how-to in `docs/procedures/`.

### 2026-11-22: Python measuring script

- `mise run measure <plan.json> <set>` = [tools/sweep.py](tools/sweep.py): sweep + loopback on the UMC, DSP preset recall, checks, IR/raw/JSON, REW import. Spec: [tools/README.md](tools/README.md).
- tracks probe: new `--recall N` (slot 1..30, tone off, reads back current preset and name).
- Tested offline only: REW IRs → simulated recordings → same IRs back (within 0.02 dB, same t=0). No real sweep yet.
- REW's "−24 dBFS" is probably RMS (sweep peak −21 dBFS); the script plays it so; the validation checks it.
- `check_dsp_electrical.py`, `analyse_closeups.py` take the set folder as an argument now (output unchanged). `rew_measure.py` deleted.
- Electrical validation on the hardware: matches REW within 0.016 dB (P01). Found: REW's level is peak; a low-end bug in sweep.py (fixed, all sets reprocessed); P03's PEQ makes 2–12 Hz noise at −59 dBFS on the DSP output (cables, ground, USB ruled out). [Finding](findings/2026-11-22-sweep-validation.md).
- CLAUDE.md: write user docs short, agent docs dense; delete superseded scripts.

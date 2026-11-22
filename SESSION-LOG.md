# Session log

Read this first. **Status** and **Next** are kept current; the **Log** gets one dated entry per session (newest at the bottom; don't edit old entries).
Map of the repo: [README.md](README.md). How to work here: [CLAUDE.md](CLAUDE.md). What is wired/configured now: [docs/current-setup.md](docs/current-setup.md).

## Status (2026-11-22)

- Baseline measurements done (DSP flat): [findings/2026-11-18-baseline.md](findings/2026-11-18-baseline.md).
- **Live mode wired** (TV → In A/B, mixer → In C/D, summed A+C → 1, B+D → 2 in all presets; UMC disconnected; no hum/hiss with the mixer on but idle): [docs/current-setup.md](docs/current-setup.md#two-modes).
- **On the DSP:** P01 FLAT (routing now summed); EQ v1 (flat target) + HPF BW 24 29.8 Hz in slot 2, electrically verified; **EQ v2 (Harman) in slot 3**: [docs/current-setup.md](docs/current-setup.md#dsp-tracks-dsp-4x4-mini).
- **Sub8 at spot C measured** and designed in as Out 3: EQ v3 (v1 + sub) and v4 (v2 + sub), mains unchanged; **on the DSP as P05 / P06** (sub matched at amp 50 / 45), not listened to yet: [findings/2026-11-22-sub-c.md](findings/2026-11-22-sub-c.md). **Now the second design** (no 28 Hz overshoot at the seat), written over P05/P06 the same day: [findings/2026-11-22-sub-c-28hz.md](findings/2026-11-22-sub-c-28hz.md).
- EQ v1 sounds "boring" (low end missing) → EQ v2 (Harman target): more "subby" bass, not boomy, also better at low volume; bass audible outside the room depending on where you stand: [findings/2026-11-20-listening.md](findings/2026-11-20-listening.md). Amp volume per EQ is in the same file (v2: everyday 30–35, fun 40–45; v1: fun 50). **v2 = everyday EQ, v1 kept for loud sessions.**

## Next

1. **Sub8: P05 first listen "sounds great with sub" ([notes](findings/2026-11-22-sub-listening.md)). Still to do: P06 (v4, amp 45), and both (P05 at amp 50)** with the sub on/off, steps in [docs/plans/sub8-overlay.md](docs/plans/sub8-overlay.md#status-2026-11-22-designed-next-steps). Then a seat check of mains + sub (needs a sweep.py change: both outputs at once).
2. Measuring: `mise run measure <plan.json> <set>` ([tools/README.md](tools/README.md)). Spot A (`subA-*`) skipped for now.
3. Output limiter (compressor, ratio Limit) for both presets, v2 and v1: [docs/procedures/output-limiter.md](docs/procedures/output-limiter.md).
4. Later, nice-to-have: real 2.1 presets (mains high-passed, sub does all the bass), from the same data.
5. TV audio digital (HDMI extractor → TOSLINK → SMSL D1 → DSP In A/B), replaces the worn TV 3.5 mm out (hum): [docs/plans/tv-digital-audio.md](docs/plans/tv-digital-audio.md).
6. Replace the TS adapters on DSP Out 1/2 with TRS → 2× RCA ([shopping list](docs/shopping-list.md)).
7. After the Sub8: iPhone room scan → room model → choose and build absorbers: [docs/plans/room-model-absorbers.md](docs/plans/room-model-absorbers.md).
8. Last, nice-to-have: speakers on one concrete slab each, on Sylomer pads (less bass through the floor). Weigh a speaker first, then pick the Sylomer: [docs/plans/speaker-isolation.md](docs/plans/speaker-isolation.md).

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
- Seat check: REW vs Python at the same spot within the room's own sweep-to-sweep scatter (Python vs Python differs more). SNR check now on the IR (room rumble made the old one fire).
- CLAUDE.md: write user docs short, agent docs dense; delete superseded scripts.

### 2026-11-22: Sub8 at spot C

- Sub back at C (back to the right wall, driver 0.73 m off it, centre 2.40 m from the speaker wall); P04 SUB MEAS made; sub knobs 0 dB / LP 130 / HP off / 0° (no photo).
- Level tests: Out 3 −20 dB too quiet (SNR 43 dB in band), −10 dB kept. Sub-set SNR check lowered to 40 dB (the full-band check counts noise where the sub plays nothing).
- `subC-seat`, `subC-corners`, `subC-dj` measured (16 positions). Spot A skipped.
- `analysis/analyse_sub_c.py`: Out 3 designed per preset → `eq/v3-flat-sub/`, `eq/v4-harman-sub/` (LPF BW24 38.5 / LR24 52 Hz, 180°, ~6 ms, one PEQ band at 46–47 Hz). Every seat and DJ position gets better: [findings/2026-11-22-sub-c.md](findings/2026-11-22-sub-c.md).
- User: v3/v4 = new versions with the sub as the 3rd output; real 2.1 maybe later.
- P05/P06 written to the DSP by a new tracks probe mode `--make-preset` (and `--set-out3-gain`), read back. Problem found: the amp knob doesn't move the sub. Decided: sub for fun sessions at the preset's fun amp position (v3 50, v4 45; A300 = 1 dB/step), P06 Out 3 lowered to −4.5 dB. TV out can't be variable; slight hiss at amp 50.

### 2026-11-22: write-up for other audio nerds

- [WRITEUP.md](WRITEUP.md): the whole project on one GitHub page (room, method, before/after, sub, tool checks, glossary), linking into the findings.
- Plots from the new `analysis/build_writeup.py` (one style, plots only); `analyse_eq_room.py` / `analyse_sub_c.py` now also export their curves as `.npz`. Re-run changed no numbers.
- User's updated room sketch with Sub spots A/B/C: [docs/img/room-layout-sketch.svg](docs/img/room-layout-sketch.svg) (replaces the PNG).

### 2026-11-22: sub 28 Hz overshoot fixed

- `analyse_sub_c.py`: leak guard (seat overshoot < 35 Hz weighted ×2) + a cut-only Out 3 band at 25–32 Hz. Seat 28 Hz +3.7/+3.9 → +0.4/+0.6 dB (v3/v4); DJ −3 dB there; new `eq/v3-flat-sub`, `eq/v4-harman-sub` (2 bands, pass `rewImport`): [finding](findings/2026-11-22-sub-c-28hz.md).
- tracks probe `--make-preset`: `--peq` repeatable (0..7 bands), `--overwrite "NAME"` to replace a used slot (name must match). The script prints the commands; both run (user OK): P05/P06 overwritten, state as predicted, read back. DSP left on P06.
- User listened to P05 (v3 + sub) at amp 45, TV 50, 70–75 dB(C): first design too subby, second "sounds great", nothing off; almost no leakage into other rooms, mostly through the door: [findings/2026-11-22-sub-listening.md](findings/2026-11-22-sub-listening.md).

# Plan: next measuring session (EQ v1/v2 in the room, v2 electrical, Sub8 spots C and A)

Written 2026-11-21. Run sheet for one session. When it's done, the results go to `findings/` and this file can be deleted (or kept as a record, linked from the session log).
Method and positions: [procedures/measurement-sets.md](../procedures/measurement-sets.md). Sub background: [sub8-overlay.md](sub8-overlay.md), spot screening: [findings/2026-11-20-sub-positions-model.md](../../findings/2026-11-20-sub-positions-model.md). Every-session checks: [procedures/session-checklist.md](../procedures/session-checklist.md). Naming and IR export: [measurements/README.md](../../measurements/README.md).

## Why this order

- **v2 electrical first:** v2 was never checked electrically; doing it first, before the room, needs no amp and no mic and catches a wrong import early.
- **Mains v1/v2 interleaved** at each mic position, without touching the mic: an exact v1 vs v2 comparison (mic re-placement is only good to ±5 cm, too coarse above ~500 Hz). v1 is electrically verified, so its result tests the method on its own. Compare each with its simulation: [findings/eq-v1-flat.md](../../findings/eq-v1-flat.md), [findings/eq-v2-harman.md](../../findings/eq-v2-harman.md); waterfall: did the ringing get shorter?
- **Sub in separate passes** (C, then A): ±5 cm is fine below ~120 Hz, and the loopback timing lets the scripts sum sub and mains IRs.

## Overview

| Part | What | DSP preset | Sweeps |
| --- | --- | --- | --- |
| 0 | Prepare: P04 SUB MEAS in the configurator, cables | – | – |
| 1 | Electrical check of EQ v2 (no amp, no mic) | P03 | 2 |
| 2 | Rewire for the room, SPL check, sub gain | P01, P04 | – |
| 3 | Mains, interleaved: at every mic position v1 L/R, then v2 L/R | P02, P03 | 16 × 4 = 64 |
| 4 | Sub at spot C, every mic position | P04 | 16 |
| 5 | Sub at spot A, as many positions as you can manage (at least seat, 2 corners, DJ pos) | P04 | 4–16 |
| 6 | Back to live mode | P03 | – |

16 mic positions: seat + pos1–pos6, corner front left/right, DJ pos + 6 DJ offsets (names as on 2026-11-18).
Each sweep (512k) takes ~11 s. With naming and mic moves, figure on ~1.5 h for part 3 and ~30 min per sub pass.
If time runs short, drop DJ offsets in parts 4–5 before anything else. Keep seat + pos1–pos6 complete in part 3.

## 0. Before the session

- [ ] **Cable for the sub:** TRS–TRS (balanced) from the DSP's place on the measuring table to spot C and to spot A. Check the length on hand; otherwise buy one first.
- [ ] **Make preset P04 "SUB MEAS"** in the configurator (once, saved to the empty slot 4):
  - Start from a copy of P01 FLAT.
  - Routing: In A → Out 3 only. Nothing routed to Out 1/2, and **Out 1/2 muted**.
  - Out 3: fader 0 dB, PEQ bypassed (all bands 0 dB), HPF/LPF off, delay 0, polarity normal, compressor off.
  - Save to slot 4. Check that P01–P03 are unchanged (recall each once, look at the routing/PEQ).
- [ ] From here on: **recall only, never save.**

Sub8 settings (fixed for parts 2–5; the DSP does all filtering later, these runs measure the raw sub):

| Knob / switch | Setting | Why |
| --- | --- | --- |
| Low-pass | **130 Hz (max)** | Sub as wide as it goes; the crossover is chosen in simulation and set on DSP Out 3 later |
| High-pass switch | **off** | Acts on the pass-through outputs (believed), which stay unused |
| Polarity | **0°** | Polarity relative to the mains is chosen in simulation and set on the DSP |
| Gain | **0 dB**, photo, unchanged for C **and** A; level is set on DSP Out 3 instead | DSP output gain is stored per preset and repeatable to 0.1 dB (−60…+12 dB); same drive at both spots, so A vs C compares directly |
| Input | DSP Out 3 → **left** balanced TRS input only (use the one marked Mono if there is one); right input, RCA and pass-through outputs unused | Out 3 is already mono: the DSP sums the sources into it. Feeding both inputs would only add level (the sub sums them internally, probably) and use up Out 4, which stays free for a second sub |

Placement: spot C = right side wall at the sofa's right end, ~0.40 m from the wall, ~2.50 m from the speaker wall. Spot A = speaker wall between L and the TV. Driver facing into the room. Note the exact spot and orientation (photo).

## 1. Electrical check of EQ v2

Same as the v1 check of 2026-11-18 ([findings/eq-v1-flat.md](../../findings/eq-v1-flat.md#dsp-electrical-check)).

- [ ] Amp off. DSP Out 1 unplugged from the amp.
- [ ] DSP on the UMC: UMC Out 1 → DSP In A, UMC Out 2 → DSP In B, loopback UMC Out 3 → UMC In 2.
- [ ] UMC: MIX at PLAYBACK, 48 kHz. macOS output = Mac speakers.
- [ ] Recall **P03** (EQ v2).
- [ ] DSP Out 1 → UMC In 3 (TRS–TRS). REW: input 3, output 1, **no cal file**, loopback reference.
- [ ] Raise In 3's gain until the IR peaks at about −20 dBFS. In 3 isn't used for the room, so this doesn't touch the SPL calibration.
- [ ] Sweep, name `1 L dsp electrical v2 <date>`.
- [ ] Move the cable to DSP Out 2, REW output 2, sweep, name `2 R dsp electrical v2 <date>`.
- [ ] Save as set `dsp-electrical-v2`. Unplug In 3.

## 2. Rewire for the room, levels

- [ ] DSP Out 1/2 → amp (TS adapters as before). Amp volume at **50**.
- [ ] TV and mixer stay disconnected from the DSP.
- [ ] Mic at the seat. REW: input 1, 90° cal file, +48 V on, In 1 gain unchanged.
- [ ] Generator: pink noise, **Full range**, −24 dBFS.
- [ ] **SPL check** with P01 FLAT, L and R together. Should read ~80 dB(C) at the seat, within ~1 dB of 2026-11-18.
- [ ] One sanity sweep: loopback impulse at t = 0.
- [ ] **Sub level** (sub at spot C, DSP Out 3 → sub, sub gain 0 dB; switch the sub on after the DSP and amp). The level doesn't have to match the mains: the simulation sets Out 3's gain later. It only has to be clean:
  1. Recall P04, one test sweep at the seat (−24 dBFS, Full range).
  2. REW input peak well below clipping (about −12 dBFS like the mains; the 28 Hz mode at C may push it up) and the curve clearly above the noise floor.
  3. If it clips: lower Out 3 in P04 and save P04 (the only save allowed). If it's very quiet: raise Out 3, not the sub knob.
  4. Note the Out 3 gain. It stays the same for C and A. **Photo of the sub knobs.**

## 3. Mains, interleaved v1/v2

At each of the 16 mic positions, without touching the mic in between:

1. Recall **P02** (check the name in the configurator) → L sweep, R sweep.
2. Recall **P03** (check the name) → L sweep, R sweep.
3. Move the mic.

Naming: `<n> <L|R> <position> <eq1|eq2> <date>`, e.g. `1 L pos1 left30 eq1 Nov 22`, `2 R pos1 left30 eq2 Nov 22`.
One REW project per group, holding both presets: sets `eq-seat` (seat + pos1–pos6), `eq-corners`, `eq-dj`.
The sub can already stand at spot C during this part. Without routing to Out 3 it stays silent.

## 4. Sub at spot C

- [ ] Recall **P04**. Mains are muted: check that nothing comes from L/R.
- [ ] REW output 1 (→ In A → Out 3).
- [ ] Same 16 positions, ±5 cm is good enough below ~120 Hz. One sweep each.
- [ ] Naming: `3 S <position> subC <date>`. Sets `subC-seat`, `subC-corners`, `subC-dj`.

## 5. Sub at spot A

- [ ] Move the sub to spot A. **Gain unchanged** (compare with the photo).
- [ ] Positions: at least seat, corner front left, corner front right, DJ pos; more if there's energy.
- [ ] Naming: `3 S <position> subA <date>`. Sets `subA-seat`, `subA-corners`, `subA-dj`.

## 6. End of session

- [ ] Export all IRs (32-bit float, t=0 at sample 256, no normalise, no window), save the REW projects into their set folders.
- [ ] Optional: fresh REW settings export (calibrated state).
- [ ] Back to live mode ([current-setup.md](../current-setup.md#wiring-live-as-wired-now-2026-11-20)), recall P03 (everyday).
- [ ] Sub: unplugged or left in place, as you like. It isn't configured for listening yet (Out 3 is only fed in P04).

## Afterwards (Claude)

- Electrical v2 vs prediction (`check_dsp_electrical.py` gets a version switch).
- v1 and v2 in the room vs their simulations, waterfall before/after.
- Sub: A vs C at seat/DJ/corners, then sum with the mains (same loopback timing) to choose crossover, delay, polarity and the Out 3 PEQ.

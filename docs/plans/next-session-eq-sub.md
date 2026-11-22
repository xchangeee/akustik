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
| 1 | Electrical check of EQ v2 (no amp, no mic) ✅ 2026-11-22 | P03 | 2 |
| 2 | Rewire for the room, SPL check, mic on the seat spot ✅ 2026-11-22 | P01 | – |
| 3 | Mains, interleaved: at every mic position v1 L/R, then v2 L/R | P02, P03 | 16 × 4 = 64 |
| 3b | Prepare the sub: P04 SUB MEAS, cable, sub level (only before the sub parts) | P04 | – |
| 4 | Sub at spot C, every mic position | P04 | 16 |
| 5 | Sub at spot A, as many positions as you can manage (at least seat, 2 corners, DJ pos) | P04 | 4–16 |
| 6 | Back to live mode | P03 | – |

16 mic positions: seat + pos1–pos6, corner front left/right, DJ pos + 6 DJ offsets (names as on 2026-11-18).
Each sweep (512k) takes ~11 s. With naming and mic moves, figure on ~1.5 h for part 3 and ~30 min per sub pass.
If time runs short, drop DJ offsets in parts 4–5 before anything else. Keep seat + pos1–pos6 complete in part 3.

## 1. Electrical check of EQ v2 (done 2026-11-22)

Result: matches the design, [findings/2026-11-22-eq-v2-electrical.md](../../findings/2026-11-22-eq-v2-electrical.md).

Same as the v1 check of 2026-11-18 ([findings/eq-v1-flat.md](../../findings/eq-v1-flat.md#dsp-electrical-check)).

- [x] Amp off. DSP Out 1 unplugged from the amp.
- [x] DSP on the UMC: UMC Out 1 → DSP In A, UMC Out 2 → DSP In B, loopback UMC Out 3 → UMC In 2.
- [x] UMC: MIX at PLAYBACK, 48 kHz. macOS output = Mac speakers.
- [x] Recall **P03** (EQ v2).
- [x] DSP Out 1 → UMC In 3 (TRS–TRS). REW: input 3, output 1, **no cal file**, loopback reference.
- [x] Set In 3's gain with REW's **Check levels** (Measure dialog): input level ≈ output level (−24 dBFS in → ~−24 dBFS on In 3), as on 2026-11-18. That gave IR peaks around −21 dBFS. In 3 isn't used for the room, so this doesn't touch the SPL calibration.
- [x] Sweep, name `1 L dsp electrical v2 <date>`.
- [x] Move the cable to DSP Out 2, REW output 2, sweep, name `2 R dsp electrical v2 <date>`.
- [x] Save as set `dsp-electrical-v2`. Unplug In 3.

## 2. Rewire for the room, levels (done 2026-11-22)

- [x] DSP Out 1/2 → amp (TS adapters as before). Amp volume at **50**.
- [x] TV and mixer stay disconnected from the DSP.
- [x] Mic at the seat. REW: input 1, 90° cal file, +48 V on, In 1 gain unchanged.
- [x] Generator: pink noise, **Full range**, −24 dBFS.
- [x] **SPL check** with P01 FLAT, L and R together. Should read ~80 dB(C) at the seat, within ~1 dB of 2026-11-18. (2026-11-22: 80 ±0.5 dB(C).)
- [x] One sanity sweep: loopback impulse at t = 0.
- [x] Mic on the baseline seat spot via the loopback delays (L 9.28 / R 9.18 ms vs 9.29 / 9.15 ms on 2026-11-18); placed by eye it was 18 cm off.

## 3. Mains, interleaved v1/v2

At each of the 16 mic positions, 4 sweeps without touching the mic: L and R with v1 (P02), L and R with v2 (P03). Then move the mic.
At every spot: recall **P02** (v1) → L, R; recall **P03** (v2) → L, R. Check the preset name in the configurator after each recall.

Naming: REW "Prefix with output" on, "Use as entered"; type `<L|R> <position> <eq1|eq2>`, output 1 for L, output 2 for R. REW adds the output number: `1 L pos1 left30 eq1`, `2 R pos1 left30 eq2` (no date: it's in the folder).
One REW project per group (set), holding both presets, saved as `measurements/2026-11-22/<set>/<set>.mdat`. Before starting a set, REW is empty (Remove all); after it, save the project and export its IRs before clearing.
The sub can already stand at spot C during this part. Without routing to Out 3 it stays silent.

#### Set `eq-seat`

**seat**: mic seat spot (delays L 9.29 / R 9.15 ms)

- [x] recall **P02**
- [x] #1 output 1: `L seat eq1`
- [x] #2 output 2: `R seat eq1`
- [x] recall **P03**
- [x] #3 output 1: `L seat eq2`
- [x] #4 output 2: `R seat eq2`

**pos1 left30**: mic 30 cm left of seat

- [x] recall **P02**
- [x] #5 output 1: `L pos1 left30 eq1`
- [x] #6 output 2: `R pos1 left30 eq1`
- [x] recall **P03**
- [x] #7 output 1: `L pos1 left30 eq2`
- [x] #8 output 2: `R pos1 left30 eq2`

**pos2 right30**: mic 30 cm right of seat

- [x] recall **P02**
- [x] #9 output 1: `L pos2 right30 eq1`
- [x] #10 output 2: `R pos2 right30 eq1`
- [x] recall **P03**
- [x] #11 output 1: `L pos2 right30 eq2`
- [x] #12 output 2: `R pos2 right30 eq2`

**pos3 fwd20**: mic 20 cm forward (towards speakers)

- [x] recall **P02**
- [x] #13 output 1: `L pos3 fwd20 eq1`
- [x] #14 output 2: `R pos3 fwd20 eq1`
- [x] recall **P03**
- [x] #15 output 1: `L pos3 fwd20 eq2`
- [x] #16 output 2: `R pos3 fwd20 eq2`

**pos4 back20**: mic 20 cm back

- [x] recall **P02**
- [x] #17 output 1: `L pos4 back20 eq1`
- [x] #18 output 2: `R pos4 back20 eq1`
- [x] recall **P03**
- [x] #19 output 1: `L pos4 back20 eq2`
- [x] #20 output 2: `R pos4 back20 eq2`

**pos5 up10**: mic 10 cm up

- [x] recall **P02**
- [x] #21 output 1: `L pos5 up10 eq1`
- [x] #22 output 2: `R pos5 up10 eq1`
- [x] recall **P03**
- [x] #23 output 1: `L pos5 up10 eq2`
- [x] #24 output 2: `R pos5 up10 eq2`

**pos6 down10**: mic 10 cm down

- [x] recall **P02**
- [x] #25 output 1: `L pos6 down10 eq1`
- [x] #26 output 2: `R pos6 down10 eq1`
- [x] recall **P03**
- [x] #27 output 1: `L pos6 down10 eq2`
- [x] #28 output 2: `R pos6 down10 eq2`

- [x] Save `eq-seat.mdat` in `eq-seat/`, export the IRs there, then REW **Remove all**

#### Set `eq-corners`

**corner front left**: mic floor corner, front left

- [x] recall **P02**
- [x] #29 output 1: `L corner front left eq1`
- [x] #30 output 2: `R corner front left eq1`
- [x] recall **P03**
- [x] #31 output 1: `L corner front left eq2`
- [x] #32 output 2: `R corner front left eq2`

**corner front right**: mic floor corner, front right

- [x] recall **P02**
- [x] #33 output 1: `L corner front right eq1`
- [x] #34 output 2: `R corner front right eq1`
- [x] recall **P03**
- [x] #35 output 1: `L corner front right eq2`
- [x] #36 output 2: `R corner front right eq2`

- [x] Save `eq-corners.mdat` in `eq-corners/`, export the IRs there, then REW **Remove all**

#### Set `eq-dj`

**DJ pos**: mic DJ spot, as on 2026-11-18

- [ ] recall **P02**
- [ ] #37 output 1: `L DJ pos eq1`
- [ ] #38 output 2: `R DJ pos eq1`
- [ ] recall **P03**
- [ ] #39 output 1: `L DJ pos eq2`
- [ ] #40 output 2: `R DJ pos eq2`

**DJ left30**: mic 30 cm left of DJ pos

- [ ] recall **P02**
- [ ] #41 output 1: `L DJ left30 eq1`
- [ ] #42 output 2: `R DJ left30 eq1`
- [ ] recall **P03**
- [ ] #43 output 1: `L DJ left30 eq2`
- [ ] #44 output 2: `R DJ left30 eq2`

**DJ right30**: mic 30 cm right of DJ pos

- [ ] recall **P02**
- [ ] #45 output 1: `L DJ right30 eq1`
- [ ] #46 output 2: `R DJ right30 eq1`
- [ ] recall **P03**
- [ ] #47 output 1: `L DJ right30 eq2`
- [ ] #48 output 2: `R DJ right30 eq2`

**DJ fwd30**: mic 30 cm forward

- [ ] recall **P02**
- [ ] #49 output 1: `L DJ fwd30 eq1`
- [ ] #50 output 2: `R DJ fwd30 eq1`
- [ ] recall **P03**
- [ ] #51 output 1: `L DJ fwd30 eq2`
- [ ] #52 output 2: `R DJ fwd30 eq2`

**DJ back30**: mic 30 cm back

- [ ] recall **P02**
- [ ] #53 output 1: `L DJ back30 eq1`
- [ ] #54 output 2: `R DJ back30 eq1`
- [ ] recall **P03**
- [ ] #55 output 1: `L DJ back30 eq2`
- [ ] #56 output 2: `R DJ back30 eq2`

**DJ up30**: mic 30 cm up

- [ ] recall **P02**
- [ ] #57 output 1: `L DJ up30 eq1`
- [ ] #58 output 2: `R DJ up30 eq1`
- [ ] recall **P03**
- [ ] #59 output 1: `L DJ up30 eq2`
- [ ] #60 output 2: `R DJ up30 eq2`

**DJ down30**: mic 30 cm down

- [ ] recall **P02**
- [ ] #61 output 1: `L DJ down30 eq1`
- [ ] #62 output 2: `R DJ down30 eq1`
- [ ] recall **P03**
- [ ] #63 output 1: `L DJ down30 eq2`
- [ ] #64 output 2: `R DJ down30 eq2`

- [ ] Save `eq-dj.mdat` in `eq-dj/`, export the IRs there, then REW **Remove all**

REW adds the output number in front ("Prefix with output", "Use as entered"): `L seat eq1` becomes `1 L seat eq1`. v1 = P02 = `eq1`, v2 = P03 = `eq2`.

## 3b. Prepare the sub (only before parts 4–5)

Not needed for the mains passes; do this when the mains are done.

- [ ] **Cable for the sub:** TRS–TRS (balanced) from the DSP's place on the measuring table to spot C and to spot A. Check the length on hand; otherwise buy one first.
- [ ] **Make preset P04 "SUB MEAS"** in the configurator (once, saved to the empty slot 4):
  - Start from a copy of P01 FLAT.
  - Routing: In A → Out 3 only. Nothing routed to Out 1/2, and **Out 1/2 muted**.
  - Out 3: fader 0 dB, PEQ bypassed (all bands 0 dB), HPF/LPF off, delay 0, polarity normal, compressor off.
  - Save to slot 4. Check that P01–P03 are unchanged (recall each once, look at the routing/PEQ).
- [ ] From here on: **recall only, never save.**

Sub8 settings (fixed for parts 3b–5; the DSP does all filtering later, these runs measure the raw sub):

| Knob / switch | Setting | Why |
| --- | --- | --- |
| Low-pass | **130 Hz (max)** | Sub as wide as it goes; the crossover is chosen in simulation and set on DSP Out 3 later |
| High-pass switch | **off** | Acts on the pass-through outputs (believed), which stay unused |
| Polarity | **0°** | Polarity relative to the mains is chosen in simulation and set on the DSP |
| Gain | **0 dB**, photo, unchanged for C **and** A; level is set on DSP Out 3 instead | DSP output gain is stored per preset and repeatable to 0.1 dB (−60…+12 dB); same drive at both spots, so A vs C compares directly |
| Input | DSP Out 3 → **left** balanced TRS input only (use the one marked Mono if there is one); right input, RCA and pass-through outputs unused | Out 3 is already mono: the DSP sums the sources into it. Feeding both inputs would only add level (the sub sums them internally, probably) and use up Out 4, which stays free for a second sub |

Placement: spot C = right side wall at the sofa's right end, ~0.40 m from the wall, ~2.50 m from the speaker wall. Spot A = speaker wall between L and the TV. Driver facing into the room. Note the exact spot and orientation (photo).
- [ ] **Sub level** (sub at spot C, DSP Out 3 → sub, sub gain 0 dB; switch the sub on after the DSP and amp), mic at the seat. The level doesn't have to match the mains: the simulation sets Out 3's gain later. It only has to be clean:
  1. Recall P04, one test sweep at the seat (−24 dBFS, Full range).
  2. REW input peak well below clipping (about −12 dBFS like the mains; the 28 Hz mode at C may push it up) and the curve clearly above the noise floor.
  3. If it clips: lower Out 3 in P04 and save P04 (the only save allowed). If it's very quiet: raise Out 3, not the sub knob.
  4. Note the Out 3 gain. It stays the same for C and A. **Photo of the sub knobs.**

## 4. Sub at spot C

- [ ] Recall **P04**. Mains are muted: check that nothing comes from L/R.
- [ ] REW output 1 (→ In A → Out 3).
- [ ] Same 16 positions, ±5 cm is good enough below ~120 Hz. One sweep each.
- [ ] Naming: `3 S <position> subC`. Sets `subC-seat`, `subC-corners`, `subC-dj`.

## 5. Sub at spot A

- [ ] Move the sub to spot A. **Gain unchanged** (compare with the photo).
- [ ] Positions: at least seat, corner front left, corner front right, DJ pos; more if there's energy.
- [ ] Naming: `3 S <position> subA`. Sets `subA-seat`, `subA-corners`, `subA-dj`.

## 6. End of session

- [ ] Export all IRs (32-bit float, t=0 at sample 256, no normalise, no window), save the REW projects into their set folders.
- [ ] Optional: fresh REW settings export (calibrated state).
- [ ] Back to live mode ([current-setup.md](../current-setup.md#wiring-live-as-wired-now-2026-11-20)), recall P03 (everyday).
- [ ] Sub: unplugged or left in place, as you like. It isn't configured for listening yet (Out 3 is only fed in P04).

## Afterwards (Claude)

- ~~Electrical v2 vs prediction~~ done ([findings](../../findings/2026-11-22-eq-v2-electrical.md)).
- Mic positions vs 2026-11-18 from the loopback delays in the exported IRs.
- v1 and v2 in the room vs their simulations, waterfall before/after.
- Sub: A vs C at seat/DJ/corners, then sum with the mains (same loopback timing) to choose crossover, delay, polarity and the Out 3 PEQ.

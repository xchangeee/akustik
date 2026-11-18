# Measurement plan

What to measure, in which order, and how to read it. Gear setup: [measurement-setup.md](measurement-setup.md); before every session: [session-checklist.md](session-checklist.md). Folder and file naming, IR export settings: [measurements/README.md](../../measurements/README.md).

General:

- Measure through the same DSP outputs and amp as in normal use (interface on DSP In 1/2, see [current-setup.md](../current-setup.md)).
- 90° cal file, mic pointing at the ceiling, for everything except close-ups (0° file, mic pointing at the driver).
- DSP input clipping: keep the interface output level moderate. DSP inputs clip at ~+9.5 dBu and the clip LEDs aren't reliable.

## Baseline (DSP flat): done 2026-11-18

Results: [findings/2026-11-18-baseline.md](../../findings/2026-11-18-baseline.md).

1. Sanity checks: loopback impulse at t = 0, same polarity L/R, same levels. (Done in setup Phase F.)
2. L and R separately at the main seat: middle of the sofa, ear height, head 1.2 m from the back wall (sitting upright).
3. 6 more positions per speaker around it: ±30 cm left/right, ±20 cm forward/back, ±10 cm up/down.
   Power average per speaker. This is the basis for the EQ.
   - 3b. **Corners ("what the room really does"):** mic in a floor–wall corner, L and R separately.
     A floor corner is where all modes are loudest, so this shows the room's real bass energy (and is the leakage proxy).
     Only the two front corners are accessible.
   - 3c. **DJ position:** 7 spots at standing ear height in front of the turntables, L and R separately.
   - 3d. Optional, not done: walk through the room with the RTA (pink PN, slow sweep of the mic) to see how uneven the bass is.
4. L+R together: computed from the L and R IRs (coherent sum, same mic spot and loopback timing) instead of measured.
5. Close-up of the woofer and the port (~1 cm, 0° cal, −40 dBFS): speaker-only bass response and port tuning.
6. Decay: RT60 (T20) per octave and narrow-band decay at the peaks (in the analysis scripts). Target ~0.3–0.5 s, even across frequency.
7. Electrical DSP check with the EQ loaded: DSP out → UMC In 3 (no amp, no mic), compared with the predicted filter curve. Done for EQ v1.

## With EQ on: next

- Re-measure seat + 6 positions, DJ 7 spots, 2 corners with the same names into a new set folder (e.g. `measurements/<date>/eq1-seat/`), then compare with the simulation in [findings/eq-v1-flat.md](../../findings/eq-v1-flat.md) (or eq-v2, whichever is loaded).
- Look at a waterfall to see whether the ringing got shorter.
- Rewire for this: DSP Out 1/2 back to the amp, UMC In 3 out, mic cal 90° back on, In 1 gain and amp volume unchanged, −24 dBFS.

## Optional, later

- R at different side/rear distances (SBIR dip at ~173–190 Hz).
- Duvet held behind the head to test whether an absorber is worth it.
- REW Room Simulator with the data above, to compare with the measurements.
- Final check: play a sweep from the TV (e.g. a REW sweep file on a USB stick) to make sure no TV processing is left on.
- Sub8: sub-only sweeps at candidate spots, see [plans/sub8-overlay.md](../plans/sub8-overlay.md).

## Interpretation rules

- Below ~300 Hz: use 1/24 oct smoothing or none. Above: Var or 1/6 oct.
- EQ peaks that stay at the same frequency at all positions and ring in the waterfall.
- **Never boost dips.** If a dip moves or changes depth when the mic moves 30 cm, it's a cancellation.
- Check excess group delay: where it's flat, EQ works.
- Add delay only if L/R arrivals differ by more than ~0.2 ms.

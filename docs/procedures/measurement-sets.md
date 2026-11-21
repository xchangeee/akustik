# Measurement sets

What a full set of measurements contains and how to read it. This file only holds the static method; what to measure next is in [plans/](../plans/) (next session: [plans/next-session-eq-sub.md](../plans/next-session-eq-sub.md), later: [plans/later-measurements.md](../plans/later-measurements.md)). What has been measured: [measurements/README.md](../../measurements/README.md#sessions). Gear setup: [measurement-setup.md](measurement-setup.md); before every session: [session-checklist.md](session-checklist.md). Folder and file naming, IR export settings: [measurements/README.md](../../measurements/README.md).

General:

- Measure through the same DSP outputs and amp as in normal use (measuring mode: DSP out of the rack, interface on DSP In 1/2 (A/B), TV and mixer not connected; see [current-setup.md](../current-setup.md#two-modes)).
- 90° cal file, mic pointing at the ceiling, for everything except close-ups (0° file, mic pointing at the driver).
- DSP input clipping: keep the interface output level moderate. DSP inputs clip at ~+9.5 dBu and the clip LEDs aren't reliable.

## The standard set

First measured with the DSP flat on 2026-11-18 (baseline: [findings/2026-11-18-baseline.md](../../findings/2026-11-18-baseline.md)). Later sets (with EQ, sub) reuse the same positions and names, so the scripts can pair them.

1. Sanity checks: loopback impulse at t = 0, same polarity L/R, same levels.
2. L and R separately at the main seat: middle of the sofa, ear height, head 1.2 m from the back wall (sitting upright).
3. 6 more positions per speaker around it: ±30 cm left/right, ±20 cm forward/back, ±10 cm up/down.
   Power average per speaker. This is the basis for the EQ.
   - 3b. **Corners ("what the room really does"):** mic in a floor–wall corner, L and R separately.
     A floor corner is where all modes are loudest, so this shows the room's real bass energy (and is the leakage proxy).
     Only the two front corners are accessible.
   - 3c. **DJ position:** 7 spots at standing ear height in front of the turntables, L and R separately.
4. L+R together: computed from the L and R IRs (coherent sum, same mic spot and loopback timing) instead of measured.
5. Close-up of the woofer and the port (~1 cm, 0° cal, −40 dBFS): speaker-only bass response and port tuning.
6. Decay: RT60 (T20) per octave and narrow-band decay at the peaks (in the analysis scripts). Target ~0.3–0.5 s, even across frequency.
7. Electrical DSP check with an EQ loaded: DSP out → UMC In 3 (no amp, no mic, no cal file), compared with the predicted filter curve. Once per EQ version.
8. Mic re-placement is only good to about ±5 cm. Fine below ~120 Hz (λ ≥ 2.9 m); above ~500 Hz it already changes the comb-filtering. So anything compared across the full range (e.g. two EQ presets) is measured interleaved at the same mic spot.

## Interpretation rules

- Below ~300 Hz: use 1/24 oct smoothing or none. Above: Var or 1/6 oct.
- EQ peaks that stay at the same frequency at all positions and ring in the waterfall.
- **Never boost dips.** If a dip moves or changes depth when the mic moves 30 cm, it's a cancellation.
- Check excess group delay: where it's flat, EQ works.
- Add delay only if L/R arrivals differ by more than ~0.2 ms.

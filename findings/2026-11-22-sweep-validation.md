# sweep.py vs REW: validation (2026-11-22)

Python measuring script ([tools/sweep.py](../tools/sweep.py)) compared with REW: electrically (DSP Out 1 → UMC In 3, no amp) and at the seat. **Validated: the script replaces REW for measuring.**

## Result

- **Passes with P01 FLAT:** 3 Python sweeps vs 1 REW sweep, 20 Hz–20 kHz within **0.016 dB**, t=0 within 0.9 samples, level within 0.001 dB.
- Both agree with steady sine tones (no sweep at all) within 0.02 dB from 10 to 100 Hz.
- With P03 (EQ v2) vs this morning's REW set: within 0.04 dB above 50 Hz, up to 0.6 dB at 20 Hz. That's the DSP's own noise (below), in both measurements.

Data: [sweep-check-electrical-flat](../measurements/2026-11-22/sweep-check-electrical-flat/) (incl. `1 L dsp rew`), [sweep-check-electrical-flat-pre2](../measurements/2026-11-22/sweep-check-electrical-flat-pre2/), [sweep-check-electrical](../measurements/2026-11-22/sweep-check-electrical/) (P03), [tone-check](../measurements/2026-11-22/tone-check/). Comparison: [analysis/output/sweep_vs_rew_electrical_flat.txt](../analysis/output/sweep_vs_rew_electrical_flat.txt), [sweep_vs_rew_electrical.txt](../analysis/output/sweep_vs_rew_electrical.txt).

## Seat (room wiring, P03, mic at the seat)

- Same spot, mic untouched: REW sweep, then 2 Python sweeps ([sweep-check-seat2](../measurements/2026-11-22/sweep-check-seat2/)).
  - REW vs Python: mean within ±0.2 dB above 50 Hz (50–200 Hz: max 0.5 dB), t=0 within 1 sample, IR SNR 85–86 dB for both.
  - **Python vs Python differs more than Python vs REW** (narrow spots up to 6 dB at 412 Hz and 1–5 kHz): the room changes between sweeps (people, air). That scatter, not the tool, limits a room comparison.
  - Below 25 Hz every seat sweep scatters by 10–20 dB, REW ones too: the speaker is 30–40 dB down there, in the room's rumble (−55 dBFS at 20–45 Hz on the mic).
- First try ([sweep-check-seat](../measurements/2026-11-22/sweep-check-seat/), L and R): mic about 5 cm too high (user). The delay check can't see height; floor/desk notches at 200–300 Hz moved by up to 8 dB vs `eq-seat`.
- Sub8 out of the room since the `nosub` test: the 77 Hz dip of `eq-seat` L is shallower now (+5 dB).
- Comparisons: [sweep_vs_rew_seat2.txt](../analysis/output/sweep_vs_rew_seat2.txt), [sweep_vs_rew_seat.txt](../analysis/output/sweep_vs_rew_seat.txt).

## Found on the way

- **REW's sweep level is peak:** "−24 dBFS" = sweep peak −24 dBFS. A first try with an RMS guess came out exactly +3.0 dB ([sweep-check-electrical-run1](../measurements/2026-11-22/sweep-check-electrical-run1/)).
- **Low-end bug in sweep.py, fixed:** the first version read 0.3 dB too low at 20 Hz (0.6 at 10 Hz). Steady tones showed REW was right. Cause: a filter in the processing cut below 10 Hz, but the sweep does contain energy there. Fixed, all sets reprocessed from their raw recordings, self-test extended so it would catch it.
- **The DSP adds noise at 2–12 Hz with P03:** −59 dBFS on the output, also with no input connected. P01: −74, muted: −82. It comes from the PEQ bands, not from cables, ground or USB (tried one by one: [in3-noise](../measurements/2026-11-22/in3-noise/noise.txt)). Inaudible; it limits electrical checks of P03 below ~50 Hz to about ±0.5 dB.
- **Preset recall disturbs the output for a moment:** the first sweep right after a recall had SNR ~30 dB instead of 52–56. The script now waits 2 s after a recall.
- **SNR check changed:** the recording-based SNR (sweep vs pre-roll) gave 22 dB at the seat because of room rumble, although the IR was clean. Now the IR's SNR (peak vs its tail): room 66–86 dB, electrical 105–113 dB; limit 50 dB.
- The measuring chain (DSP + UMC) itself rolls off a little at the ends: −0.23 dB at 20 Hz, −0.5 dB at 20 kHz. REW and Python both see it; it's real.


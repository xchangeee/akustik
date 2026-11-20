# EQ v2: Harman target (2026-11-18)

**Status:** imported into DSP preset slot 3 (2026-11-20: copy of v1's slot 2 with only the PEQ replaced, so same HPF BW 24 29.8 Hz; FLAT = slot 1). Listening: [2026-11-20-listening.md](2026-11-20-listening.md).
Why: v1 sounded "boring" ([docs/plans/sub8-overlay.md](../docs/plans/sub8-overlay.md), section 1). Compared against: [eq-v1-flat.md](eq-v1-flat.md).

## Design (no new measurements)

Same script, same IRs, same weights, HPF and device grid as v1: `design_eq.py . analysis/output eq harman`.
Output: [eq_design_harman.txt](../analysis/output/eq_design_harman.txt), plots [before/after (with v1 for comparison)](../analysis/output/eq_design_harman.png), [filters](../analysis/output/eq_filters_harman.png).
Filter files: [eq/v2-harman/L.txt](../eq/v2-harman/L.txt) (out 1), [eq/v2-harman/R.txt](../eq/v2-harman/R.txt) (out 2). v1 files unchanged.

**Target:** Harman-style in-room bass rise = RBJ low shelf **+6 dB, 105 Hz, Q 0.707** on top of each set's 300 Hz–3 kHz level
(+6.0 dB at 30 Hz, +5.7 at 50, +4.4 at 80, +3.3 at 100, +1.2 at 150, +0.5 at 200 Hz). This is an approximation of the
bass part of the Harman preferred in-room curve; its gentle treble tilt isn't included (the EQ only works in the bass).

**One method change for v2:** the dip penalty counts only the *extra* depth the EQ adds, squared ((e − e0)²), instead of v1's e² − e0².
With the raised target many spots are already several dB below it (e.g. 47 Hz next to the 43 Hz mode), and e² − e0² made
each dB of filter skirt there ~10× as expensive. The first run with the v1 formula therefore left the 43 Hz mode +5.6 dB above target
at the seat. v1 still uses its original formula (re-run reproduces its filters exactly).

Values as the configurator shows them (device Q). HPF unchanged: Butterworth 24, 29.8 Hz.

| L (out 1) | Freq | Gain | Q | | R (out 2) | Freq | Gain | Q |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | 43.2 | −6.9 | 11.99 | | 1 | 43.2 | −5.1 | 10.68 |
| 2 | 92.6 | −2.1 | 8.98 | | 2 | 53.2 | −7.6 | 12.70 |
| 3 | 114.0 | −6.4 | 11.31 | | 3 | 84.4 | −12.0 | 16.00 |
| 4 | 125.0 | −2.1 | 8.98 | | 4 | 125.0 | −8.2 | 11.99 |
| 5 | 185.1 | −0.9 | 8.48 | | 5–7 | flat | | |
| 6 | 227.9 | −1.1 | 8.48 | | | | | |
| 7 | flat | | | | | | | |

Simulated (30–200 Hz, deviation from the Harman target; bass energy 30–150 Hz):

| | rms: before / v1 / v2 | max above target: before / v1 / v2 | bass energy vs no EQ: v1 / v2 |
| --- | --- | --- | --- |
| Seat L+R | 4.6 / 4.9 / 3.4 dB | +9.4 / +1.7 / +3.1 dB | −7.9 / −4.4 dB |
| DJ L+R | 6.3 / 6.7 / 6.1 dB | +11.2 / +4.0 / +4.4 dB | −7.7 / −5.1 dB |
| Corners L+R (leakage proxy) | | | −6.4 / −4.2 dB |

- Seat L+R vs v1, 1/24 oct: 40 Hz +1.5 → +5.7, 43 Hz +3.0 → +8.8, 51 Hz +2.2 → +7.0, 60 Hz +0.2 → +4.6, 85 Hz +2.2 → +5.9 dB (target +6…+4).
  So the 35–130 Hz region sits **~4–5 dB higher than with v1**, on the target with ±3 dB peaks.
- Every seat position's highest peak above target drops (+9…+13 → +3…+7 dB). DJ positions too (+8…+12 → +5…+8).
- **What the cut-only EQ can't reach:** the bottom of the target. Below 35 Hz the seat L+R is −2.5 dB at 30 Hz, −14 at 25 Hz (target +6): port tuning 35 Hz + HPF.
  Dips stay dips too (seat 47 Hz +0.3, 140–165 Hz −3…−6 dB). Boosting either isn't sensible (excursion below the port tuning; cancellations at the dips). The Sub8 overlay is the way to fill 25–40 Hz if wanted.
- Leakage cost: ~2–3.5 dB more bass energy than v1 in every set (corners +2.2 dB), still 4–5 dB below no EQ. Matches the rough guess in [docs/plans/sub8-overlay.md](../docs/plans/sub8-overlay.md).
- Import: same as v1 (onto the flat PEQ state, or into a new preset slot so v1 stays available for A/B). L uses 6 bands now, R 4: bands the file marks OFF must end up flat.

## Treble tilt: checked, not added (2026-11-18)

Question: v2 leaves bands free (L 1, R 3), so could they add the Harman curve's treble tilt? The DSP has high-shelf bands and the configurator imports `HSQ`, so it's technically possible.
Script: [analysis/analyse_treble.py](../analysis/analyse_treble.py). Output: [treble.txt](../analysis/output/treble.txt), [plot](../analysis/output/treble.png). Comparison tilt: 0 dB to 1 kHz, then −1 dB/oct (−3.3 dB at 10 kHz).

- **The seat already has the Harman slope:** fitted slope 1–16 kHz −0.9 dB/oct (L), −1.4 dB/oct (R). rms deviation from the tilt 1.8 / 1.6 dB, which is within what position and mic orientation change.
- Shape: flat to ~6 kHz (+2…+3 dB above the tilt at 4–6 kHz), then falls faster (10 kHz −2.5, 16 kHz −5…−6 dB, about on or below the tilt).
- Best single band (fitted): a very broad peak cut, about −2.4 dB at 3.7–4.8 kHz, Q 0.4–0.55. That brings the seat to 0.6 dB rms from the tilt, but in effect it's just "treble −2 dB from 2 to 8 kHz". A high shelf does the same (−1.2…−1.7 dB from 1 kHz up) and also dulls 10–16 kHz, which is already at or below the tilt.
- The DJ spot is already 1 dB below the tilt at 4–16 kHz (slope −1.8 / −2.2 dB/oct). Either band would make it ~2.5 dB duller there.
- Background: above ~500 Hz the in-room curve mostly reflects the speaker's own directivity. The Harman in-room curve describes what a good speaker produces in a normal room, not a target to EQ towards. These speakers already produce it.
- **Decision: no treble band in v2.** If, after listening, the presence region sounds too forward, try a single broad cut (≈ −1.5…−2 dB, ~4 kHz, cookbook Q ~0.5) on both outputs as a taste adjustment, A/B'd by ear.

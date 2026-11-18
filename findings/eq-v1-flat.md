# EQ v1: flat target (2026-11-18)

**Status:** imported on the DSP 2026-11-18 and checked electrically (matches the design within 0.05 dB). Not yet confirmed whether it was stored in a new preset slot with FLAT kept. Acoustic re-measurement with EQ on: pending.
After listening: sounds "boring", low end missing → [EQ v2](eq-v2-harman.md).
Data it's designed from: [2026-11-18-baseline.md](2026-11-18-baseline.md). Background on the method: [docs/eq-design-explained.md](../docs/eq-design-explained.md).

## Design

Script: [analysis/design_eq.py](../analysis/design_eq.py). Output: [eq_design.txt](../analysis/output/eq_design.txt), plots [before/after](../analysis/output/eq_design.png), [filters](../analysis/output/eq_filters.png). Filter files: [eq/v1-flat/L.txt](../eq/v1-flat/L.txt) (out 1), [eq/v1-flat/R.txt](../eq/v1-flat/R.txt) (out 2).

REW plays no part in the design. The files only use REW's filter text format because the user's own configurator (`../tracks`, a 1:1 reimplementation of the t.racks editor, built from the reverse-engineered protocol) imports that format. Its import treats Q as a cookbook Q, converts to the device's Q (Q_dev = Q_rbj · A) and rounds to the device grid. The script designs directly on that grid and writes the values so the import lands exactly on them (checked with the configurator's own `rewImport`: no errors, identical raw values).

Device facts used (from `tracks/docs/protocol.md` §5, §6.2): PEQ gain ±12 dB in 0.1 dB steps; frequency in 1/30-octave steps (Hz = 1000·2^((raw−170)/30)); Q in 1/12-octave steps (Q = 2^((raw−16)/12)); Peak = RBJ peaking with Q_rbj = Q_dev / A, A = 10^(|G|/40); HPF Butterworth 24 = textbook sections. Not modelled: peaks below 150 Hz measured up to 41 cents low on the device (open in tracks' TODO, maybe a measurement artefact). The electrical check will show it.

Method: the EQ is applied to every measured IR as a complex multiply, so the L+R sums include the filters' phase. Target flat at each set's own 300 Hz–3 kHz level, fit 25–250 Hz at 1/24 oct. Cut-only, ≥ −12 dB per band, cookbook Q ≤ 8 (≈ device Q ≤ 16 at −12 dB), ≤ 7 bands. Asymmetric cost: excess above target counts fully, going below target counts only where the EQ made it deeper. Weights: seat L+R 1.0, seat L 0.5, seat R 0.5, DJ L+R 0.4; small penalty per dB of cut. Bands stacked within 1/12 oct are merged and re-fitted; then snapped to the device grid and refined there step by step.

**High-pass (crossover HPF, set by hand, not in the file): Butterworth 24 (slope raw 8), 29.8 Hz (freq raw 18), both outputs.** Protects the woofer below the 35 Hz port tuning. 35 Hz costs ~2 dB at 35 Hz and saves only 0.4 dB of bass energy; it's an option for a DJ/leakage preset.

Values as the configurator shows them (device Q):

| L (out 1) | Freq | Gain | Q | | R (out 2) | Freq | Gain | Q |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | 43.2 | −12.0 | 16.00 | | 1 | 42.2 | −11.6 | 16.00 |
| 2 | 82.5 | −1.8 | 8.98 | | 2 | 52.0 | −12.0 | 16.00 |
| 3 | 94.7 | −7.4 | 11.99 | | 3 | 62.5 | −6.7 | 5.99 |
| 4 | 114.0 | −7.8 | 12.70 | | 4 | 82.5 | −11.0 | 15.10 |
| 5 | 125.0 | −4.6 | 10.68 | | 5 | 88.4 | −8.2 | 12.70 |
| 6, 7 | flat | | | | 6 | 111.4 | −3.2 | 9.51 |
| | | | | | 7 | 125.0 | −6.6 | 11.99 |

Simulated result (30–200 Hz, relative to the mid level):

| | rms before → after | max before → after | bass energy 30–150 Hz |
| --- | --- | --- | --- |
| Seat L+R | 7.1 → 2.2 dB | +15.2 → +3.2 dB | −7.9 dB |
| DJ L+R | 7.2 → 3.9 dB | +17.0 → +4.9 dB | −7.7 dB |
| Corners L+R (leakage proxy) | | | −6.4 dB |

- Every single seat and DJ position improves too (max peak per position +14…+18 → +3…+8.5 dB), so the result doesn't come only from the averaging.
- Dips are left alone (seat L+R min −7 → −8 dB, from the HPF and filter skirts).
- DJ 55–75 Hz hole: ~1 dB thinner (R 62.5 Hz cut), as planned "moderate".
- Mid/treble untouched; L/R mid levels within 0.7 dB, so no channel gain change.
- Import note: bands the file leaves out (L 6, 7) keep what the output already holds, so import onto the flat state.
- Next check: electrical measurement (DSP out → interface in, no amp) against the predicted curve, before the acoustic re-measurement.

## DSP electrical check

Data: [`measurements/2026-11-18/dsp-electrical/`](../measurements/2026-11-18/dsp-electrical/). DSP Out 1 / Out 2 → UMC In 3 via TRS–TRS, no amp, no mic cal, preset with EQ v1 loaded (HPF BW 24 29.8 Hz + PEQ, EQ Bypass off). IR peaks −20.7 / −21.0 dBFS after raising In 3's gain.
Script: [analysis/check_dsp_electrical.py](../analysis/check_dsp_electrical.py). Output: [dsp_electrical.txt](../analysis/output/dsp_electrical.txt), [plot](../analysis/output/dsp_electrical.png).

| measured − predicted | 20–30 Hz | 30–60 Hz | 60–150 Hz | 150 Hz–1 kHz | 1–20 kHz |
| --- | --- | --- | --- | --- | --- |
| L rms (max) | 0.64 (0.93) | 0.20 (0.37) | 0.03 (0.07) | 0.02 (0.04) | 0.15 (0.52) |
| R rms (max) | 1.00 (1.36) | 0.19 (0.34) | 0.04 (0.17) | 0.02 (0.04) | 0.16 (0.54) |

- **The DSP does exactly what the design assumes.** In the filter region (30–150 Hz) the error is a few hundredths of a dB; every notch sits at its design frequency and depth (e.g. L 43.2 Hz −12.4 vs −12.3 dB, R 52.0 Hz −15.65 vs −15.64 dB).
- Fitting one common frequency factor gives only +4 cents (no gain in fit). **The 26–41 cent "low-frequency offset" from the tracks PEQ measurements doesn't show here** (512k sweep, 500 ms window, 1/48 oct). That supports tracks' "cause 1: the measurement" (short sweep / 1 s window there).
- Below 30 Hz the chain is up to ~1 dB lower than the model, and −0.5 dB at 20 kHz: converter / coupling roll-off of UMC + DSP, not the filters. Irrelevant for the room EQ.

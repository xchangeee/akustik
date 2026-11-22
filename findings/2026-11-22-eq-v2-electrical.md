# EQ v2: DSP electrical check (2026-11-22)

Data: [`measurements/2026-11-22/dsp-electrical-v2/`](../measurements/2026-11-22/dsp-electrical-v2/). Preset P03 (EQ v2 Harman: HPF BW 24 29.8 Hz + PEQ from [eq/v2-harman/](../eq/v2-harman/), EQ Bypass off; band 7 at 0 dB). DSP Out 1 / Out 2 → UMC In 3 via TRS–TRS, no amp, no mic cal, loopback timing. In 3 gain from REW's Check levels: −24.6 dBFS on In 3 for −24 dBFS out (unity, unchanged since 2026-11-18). IR peaks −22.4 / −22.6 dBFS.
Script: [analysis/check_dsp_electrical.py](../analysis/check_dsp_electrical.py) `v2`. Output: [dsp_electrical_v2.txt](../analysis/output/dsp_electrical_v2.txt), [plot](../analysis/output/dsp_electrical_v2.png). Same method as v1: [eq-v1-flat.md](eq-v1-flat.md#dsp-electrical-check).

| measured − predicted | 20–30 Hz | 30–60 Hz | 60–150 Hz | 150 Hz–1 kHz | 1–20 kHz |
| --- | --- | --- | --- | --- | --- |
| L rms (max) | 0.40 (0.59) | 0.17 (0.35) | 0.04 (0.09) | 0.02 (0.04) | 0.15 (0.52) |
| R rms (max) | 0.68 (0.84) | 0.13 (0.42) | 0.03 (0.12) | 0.02 (0.04) | 0.16 (0.54) |

- **The import is correct; the DSP does what the design assumes.** Every notch sits at its design frequency and depth within ~0.2 dB (e.g. L 114.0 Hz −7.25 vs −7.27 dB, R 84.4 Hz −12.32 vs −12.39 dB).
- Common frequency factor: +8 cents (L), +5 cents (R), no real gain in fit. Like v1 (+4 cents), no sign of the tracks "low-frequency offset".
- Below 30 Hz and at 20 kHz the same small chain roll-off as on 2026-11-18 (UMC + DSP converters/coupling, not the filters).

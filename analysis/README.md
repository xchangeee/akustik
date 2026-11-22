# Analysis

Python scripts that analyse the REW impulse-response exports in [../measurements/](../measurements/).
Findings and interpretation: [../findings/](../findings/). How the EQ was designed, with background: [../docs/eq-design-explained.md](../docs/eq-design-explained.md).

## Run

```sh
mise run analyse     # installs deps with uv (.venv), runs every script, writes analysis/output/
```

Tools come from [../mise.toml](../mise.toml) (Python 3.14, uv); dependencies from [../pyproject.toml](../pyproject.toml) / `uv.lock`.
A single script: `uv run python analysis/<script>.py . analysis/output`.

## Input format

IR exports as described in [../measurements/README.md](../measurements/README.md) (WAV, 32-bit float, **t=0 at sample 256**, 48 kHz).
Common processing: 500 ms right window (half-Tukey, last 25 %), FFT, mic cal subtracted (`reference/mic-cal/MM-1C_90deg.txt`, close-ups `0deg`), fractional-octave power smoothing.
Absolute level: fixed offset of 100.9 dB so that the L seat 1–8 kHz average is 73.5 dB (matches REW's calibrated SPL within ~1 dB). Close-ups are relative only.

## Scripts → outputs (in `output/`)

| Script | What it does | Output |
| --- | --- | --- |
| `inspect_irs.py` | Sample rate, length, peak time after t0 (= arrival delay), tail noise per file | `inspect_irs.txt` |
| `analyse_positions.py` | Seat + 6 positions per speaker: FR, power average, min/max spread, bass peaks/dips with spread, RT60 per octave (T20), narrow-band decay at peaks | `positions.txt`, `positions.png`, `LR_average.png`, `averages.npz` |
| `analyse_corners.py` | Two front floor corners vs seat average, peaks in the corner average | `corners.txt`, `corners.png` |
| `analyse_dj_sum.py` | DJ spot (7 positions) vs seat, plus **L+R = coherent sum of the L and R IRs** (same mic spot, same loopback timing) | `dj_sum.txt`, `dj_vs_seat.png` |
| `analyse_closeups.py` | Woofer/port close-ups (0° cal): port tuning, L vs R woofer. Args `<set folder> <plot.png> [cal file]` (cal from `<set>.json` for sweep.py sets); `tools/sweep.py` runs it after a close-up set | `closeups.txt`, `closeups.png` |
| `design_eq.py` | Optional 4th arg `harman` (EQ v2: +6 dB low-shelf target, outputs `*_harman.*`, `eq/v2-harman/`). Cut-only PEQ design (≤7 bands/channel) + fixed HPF, fitted on seat L/R/L+R and DJ L+R; simulates seat/DJ/corner from the IRs (complex multiply, so sums include filter phase) | `eq_design.txt`, `eq_design.png`, `eq_filters.png`, `eq_design.log`; filter files in [../eq/](../eq/) (`v1-flat/`, `v2-harman/`) |
| `analyse_treble.py` | Seat/DJ treble (1/6 oct) vs a Harman-style tilt (−1 dB/oct above 1 kHz), slope fit | `treble.txt`, `treble.png` |
| `build_explainer.py` | Inlines the bass spectra, IR, design stages and electrical check into [../explainer/template.html](../explainer/template.html) → interactive explainer page | `../explainer/eq-explained.html` |
| `check_dsp_electrical.py` | DSP out → UMC In 3 (no amp/mic) vs the curve predicted from an `eq/` folder (or `flat`); fits a common frequency offset. Args `<set folder> <eq folder\|flat> <plot.png> [--tol dB --band lo hi] [--files …]`; one line per checked EQ in `mise run analyse`, and `tools/sweep.py` runs it after an electrical set (PASS/FAIL with `--tol`) | `dsp_electrical[_v2].txt`, `dsp_electrical[_v2].png` |
| `check_sweep_vs_rew.py` | Validation of `tools/sweep.py`: pairs of REW / Python IRs of the same setup: level difference (1/24 oct) with pass tolerance, t=0 offset, noise. Args `[--t0-info] <plot> (<rew.wav> <py.wav> <f_lo> <f_hi> <tol>)…`. Goes into `mise run analyse` once the validation data exist | — |
| `../tools/sweep_selftest.py` | Offline check of `tools/sweep.py`'s processing: REW IRs → simulated recordings → sweep.py → compared with the REW IRs (length, t=0, spectrum within 0.02 dB, THD) | `sweep_selftest.txt` |
| `sub_positions_modes.py` | Rigid-box modal model (no measurement): candidate Sub8 positions A/B/C at seat, DJ and room average; validated on measured R − L at the seat | `sub_positions_modes.txt`, `sub_positions_modes.png`, `sub_positions_validation.png` |
| `build_writeup.py` | Plots only, one style, for [../WRITEUP.md](../WRITEUP.md): baseline, filters, EQ in the room, predicted vs measured, ringing, sub. Reads `eq_room_curves.npz` and `sub_c_curves.npz`, so it runs after those scripts | `writeup_*.png` |
| `analyse_eq_room.py` | EQ v1/v2 measured in the room (2026-11-22 `eq-*` sets, v1/v2 interleaved per mic spot) vs 2026-11-18 flat, vs simulated (flat IR × filter files) and vs target; mic placement from arrival delays; v2 − v1 at the same spot vs predicted; IR noise check; ringing (band energy left after t) and waterfall; scan for new narrow resonances | `eq_room.txt`, `eq_room_v1.png`, `eq_room_v2.png`, `eq_room_v2_minus_v1.png`, `eq_room_waterfall.png`, `eq_room_curves.npz` (for the write-up) |
| `check_nosub.py` | Sub-out-of-the-room test (`nosub-seat`) vs `L seat eq1`: spectra, difference IR, late energy at 77.8 Hz; plus per-spot residual eq1 − eq2 × filter ratio, L vs R, to check whether the sub played along (P02 routing) | `nosub.txt`, `nosub.png` |
| `analyse_sub_c.py` | Sub8 at spot C (`subC-*`) alone and summed with the mains (eq1/eq2 from the `eq-*` sets, complex sum on the loopback timing); Out 3 design per preset (LPF type/fc, polarity, delay, gain, 1 PEQ band) on the device grid, per-position check, live Out 3 gain; writes `eq/v3-flat-sub/Sub.txt`, `eq/v4-harman-sub/Sub.txt` | `sub_c.txt`, `sub_c.png`, `sub_c_curves.npz` (for the write-up) |

## Known limitations

- Narrow-band decay times at low frequencies are biased high by the band filter's own ringing; compare them relatively. Below ~35 Hz they're unreliable (low SNR).
- `analyse_closeups.py` reports the woofer "notch" as the minimum in 20–80 Hz; it hits the 20 Hz edge here. The real minimum is the broad dip at ~32–38 Hz (see the plot).
- Positions were ball-parked by hand.

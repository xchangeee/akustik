# Analysis

Python scripts that analyse the REW impulse-response exports in [../measurements/](../measurements/).
Findings and interpretation: [../measurements/2026-11-18-analysis.md](../measurements/2026-11-18-analysis.md).

## Run

```sh
mise run analyse     # installs deps with uv (.venv), runs every script, writes analysis/output/
```

Tools come from [../mise.toml](../mise.toml) (Python 3.14, uv); dependencies from [../pyproject.toml](../pyproject.toml) / `uv.lock`.
A single script: `uv run python analysis/<script>.py . analysis/output`.

## Input format

REW → export impulse response as WAV: 32-bit float, measured IR, **t=0 at sample 256**, no normalise, no window. 48 kHz.
Common processing: 500 ms right window (half-Tukey, last 25 %), FFT, mic cal subtracted (`cal/MM-1C_90deg.txt`, close-ups `0deg`), fractional-octave power smoothing.
Absolute level: fixed offset of 100.9 dB so that the L seat 1–8 kHz average is 73.5 dB (matches REW's calibrated SPL within ~1 dB). Close-ups are relative only.

## Scripts → outputs (in `output/`)

| Script | What it does | Output |
| --- | --- | --- |
| `inspect_irs.py` | Sample rate, length, peak time after t0 (= arrival delay), tail noise per file | `inspect_irs.txt` |
| `analyse_positions.py` | Seat + 6 positions per speaker: FR, power average, min/max spread, bass peaks/dips with spread, RT60 per octave (T20), narrow-band decay at peaks | `positions.txt`, `positions.png`, `LR_average.png`, `averages.npz` |
| `analyse_corners.py` | Two front floor corners vs seat average, peaks in the corner average | `corners.txt`, `corners.png` |
| `analyse_dj_sum.py` | DJ spot (7 positions) vs seat, plus **L+R = coherent sum of the L and R IRs** (same mic spot, same loopback timing) | `dj_sum.txt`, `dj_vs_seat.png` |
| `analyse_closeups.py` | Woofer/port close-ups (0° cal): port tuning, L vs R woofer | `closeups.txt`, `closeups.png` |
| `design_eq.py` | Cut-only PEQ design (≤7 bands/channel) + fixed HPF, fitted on seat L/R/L+R and DJ L+R; simulates seat/DJ/corner from the IRs (complex multiply, so sums include filter phase) | `eq_design.txt`, `eq_design.png`, `eq_filters.png`, `eq_design.log`; filter files in [../eq/](../eq/) |
| `check_dsp_electrical.py` | DSP out → UMC In 3 (no amp/mic) vs the curve predicted from `eq/` files; fits a common frequency offset | `dsp_electrical.txt`, `dsp_electrical.png` |

## Known limitations

- Narrow-band decay times at low frequencies are biased high by the band filter's own ringing; compare them relatively. Below ~35 Hz they're unreliable (low SNR).
- `analyse_closeups.py` reports the woofer "notch" as the minimum in 20–80 Hz; it hits the 20 Hz edge here. The real minimum is the broad dip at ~32–38 Hz (see the plot).
- Positions were ball-parked by hand.

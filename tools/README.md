# tools/

Reference for agents writing plan files and working on the measuring scripts (dense on purpose). The short user-facing version is in [../measurements/README.md](../measurements/README.md).

| Script | Job |
| --- | --- |
| `sweep.py` | Measure one set (`mise run measure <plan.json> <set>`): sweep + loopback on the UMC, preset recall via tracks `probe --recall`, IR/raw/JSON out, REW import. Docstring has the details. |
| `rew_api.py` | REW API client (free-licence calls only). Import takes full-scale floats; export returns percent. |
| `rew_load.py` | Set folder → REW → `<set>.mdat` (`mise run rew-load <set folder>`). |
| `reprocess.py` | Recompute a set's IRs from `raw/` with the current processing (`<set folder>`); then `rew-load` for the `.mdat`. |
| `noise.py` | Record inputs with nothing playing, noise per band, saved as FLAC + `noise.txt` (finding noise sources). |
| `tone_response.py` | Steady-sine response of a UMC path at given frequencies (truth for the low end). |
| `lf_check.py` | Sweep IRs (and their loopback from `raw/`) vs a `tone_response.py` table, 10–100 Hz. |
| `sweep_selftest.py` | Offline check of sweep.py's processing on simulated recordings (`mise run sweep-selftest`). |

Processing notes: no regularisation below the sweep (it removed real signal: −0.3 dB at 20 Hz, fixed 2026-11-22, `SCRIPT_VERSION` 2); 2 s pause after a recall; REW measurements matched by `rew_uuid`.

What sweep.py writes per set: `<name>.wav` (IR in REW export format, `ir.after_peak_samples` past the peak); `raw/<name>.flac` (24-bit, ch1 input, ch2 loopback) and `raw/stimulus.flac`; `<set>.json` (header: plan, kind, device, rates, cal file, dBFS@94, SPL offset, sweep params; per sweep: time, engine, preset slot/name read back, position, side, output, input, input/loopback peak, noise, SNR, IR peak, delay, baseline delay + cm diff, THD + harmonics 2–5, failed checks, git, script version); `<set>.mdat`. REW holds only the current set (the script offers to clear it). IR scale = IR of the unit-amplitude sweep (level-dependent like REW's).

## Plan file

One JSON file per session (e.g. [../docs/plans/sweep-check.json](../docs/plans/sweep-check.json), [../docs/plans/next-session-eq-sub.json](../docs/plans/next-session-eq-sub.json)). The code has no defaults: every key below is required unless marked optional, and a missing key stops the script and names it.

```json
{
  "audio":   {"device": "UMC404HD", "samplerate": 48000, "mic_in": 1, "loopback_out": 3, "loopback_in": 2},
  "sweep":   {"length_samples": 524288, "f_start_hz": 10, "f_end_hz": 22050, "level_dbfs": -24,
              "fade_in_ms": 20, "fade_out_ms": 5, "pre_s": 0.5, "silence_s": 3},
  "ir":      {"t0_sample": 256, "after_peak_samples": 83072},
  "checks":  {"clip_dbfs": -1.0, "loopback_min_dbfs": -30, "snr_min_db": 35, "delay_tol_cm": 10},
  "dsp":     {"probe": "~/WPlay/tracks/tools/probe/probe"},
  "rew":     {"import": true, "api": "http://127.0.0.1:4735", "dbfs_at_94db_spl": -22.99},
  "presets": {"P03": {"slot": 3, "name": "EQ v2 Harmann"}},
  "channel_groups":  {"mains": [{"n": 1, "side": "L", "out": 1}, {"n": 2, "side": "R", "out": 2}]},
  "position_groups": {"seat-only": [{"name": "seat", "mic": "seat spot", "delay_ms": {"L": 9.29, "R": 9.15}}]},
  "sets": {
    "eq2-seat": {"kind": "room", "positions": "seat-only", "channels": "mains", "presets": [["P03", "eq2"]],
                 "mic_cal": "reference/mic-cal/MM-1C_90deg.txt"}
  }
}
```

- `audio`: device name (substring), sample rate, UMC channels (1-based). The sweep output per sweep is the channel's `out`.
- `sweep`: `level_dbfs` = peak level, same number as in REW (REW's level is peak: checked 2026-11-22 against `dsp-electrical-v2`). `pre_s` of silence before the sweep gives the noise floor, `silence_s` after it records the decay.
- `ir`: t=0 sample in the WAV, and how far the WAV goes past the IR peak (83072 = REW's 512k export, measured on all 2026-11-18/22 exports).
- `checks`: after every sweep; on a failure the script offers a redo (`k` keeps it, the failure is logged). `delay_tol_cm` only applies to positions with `delay_ms`.
- `rew`: `import` false measures without REW. `dbfs_at_94db_spl` is used when REW isn't running; with REW, its own value is used (and a difference printed). SPL offset for the import = 94 − that value; 0 for electrical sets.
- `presets`: DSP slot and the name the DSP must report after the recall (else the script stops).
- `position_groups`: `mic` is the instruction printed before moving; `delay_ms` (optional) the baseline loopback delay per speaker.
- `sets.<name>`: `kind` is `room`, `closeup` or `electrical`; `presets` is a list of `[preset, tag]` (tag goes at the end of the name, may be `""`). Order of sweeps: per position, per preset, per channel. Optional per set: `level_dbfs` (e.g. −40 for close-ups), `checks` (overrides, e.g. a stricter `clip_dbfs`), `before` (shown and confirmed before the first sweep).
  - `room` / `closeup`: `positions`, `channels`, `mic_cal` (repo path; REW's cal file is switched to it for the import and back at the end). After a `closeup` set, `analyse_closeups.py` runs and prints the tuning per speaker (woofer/port found by position name).
  - `electrical`: `label` (used in place of the position, e.g. `dsp`), `input` (UMC input, e.g. 3), `channels`, `eq` (EQ folder, e.g. `eq/v2-harman`, or `flat`), `tolerance_db` and `check_band_hz` ([lo, hi]). No mic, no cal, no delay check. After the set, `check_dsp_electrical.py` compares with the design and prints PASS/FAIL; text and plot go to `analysis/output/<set>.txt/.png`.

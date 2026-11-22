# Plan: measure with a Python script instead of REW (sweep, IR, preset recall)

Written 2026-11-22. **Done 2026-11-22: implemented and validated** (electrical and seat, [finding](../../findings/2026-11-22-sweep-validation.md)). Nothing left in this plan.

How it was built, where it differs from the text below:
- Preset recall is its own probe mode `--recall N` (slot 1..30), not `--write 20 N`: it sends `0x20 N` and `0x39 00 00` and reads back `0x14`, `0x29 30` (live name) and `0x29 N−1` (slot name; `0x29` takes slot − 1). tracks commit, `tools/probe/README.md`.
- REW import scale checked on the free API: it takes the IR in full scale (as the WAVs), returns percent. No conversion.
- IR length: REW's exports all end 83072 samples after the IR peak (`ir.after_peak_samples` in the plan).
- Validation: one REW sweep of P01 in the same folder as the Python ones (user, 2026-11-22), plus REW's morning sets (`dsp-electrical-v2`, `eq-seat`, P03). No interleaved REW mode in the script.
- Low-end regularisation removed (it cut real signal below 10 Hz: −0.3 dB at 20 Hz); `tools/reprocess.py` recomputes a set from `raw/`; the self-test has synthetic paths with an exact truth.
- 2 s pause after each preset recall (the next sweep had low SNR otherwise). REW measurements are matched by REW id (`rew_uuid` in `<set>.json`), not by name.
- Tools for diagnosis: `tools/noise.py` (input noise per band), `tools/tone_response.py` (steady-sine response), `tools/lf_check.py` (sweep IR vs tones at the low end).
- Electrical sets name their sweeps by `label` (e.g. `dsp`) and carry `tolerance_db` and `check_band_hz`; `eq` may be `flat`.
- `tools/sweep_selftest.py` (`mise run sweep-selftest`, also in `mise run analyse`): REW IRs → simulated recordings → sweep.py's processing → same length, same t=0 and peak sample, spectrum within 0.02 dB from 20 Hz, THD 1.0 % found where 1 % was simulated. Passes on seat, electrical, corner and close-up IRs.
- Plan file format: [tools/README.md](../../tools/README.md#plan-file). `next-session-eq-sub.json` converted.

**Goal:** you run one command per set and do only two things: move the mic and press Enter. The script plays and records the sweeps, recalls the DSP presets, checks each sweep, and writes everything into `measurements/<date>/<set>/`. It also loads the set into REW, so REW stays available for analysis.

**Why:** the REW API can't start a sweep without a Pro licence (HTTP 401), so today you click Start in REW for every sweep (`tools/rew_measure.py`). The REW features we actually use (log sweep, loopback timing, IR export) are easy to do in Python.

## What's already verified (2026-11-22)

- **The free REW API can import IRs:** `POST /import/impulse-response-data` (fields `identifier`, `startTime`, `sampleRate`, `splOffset`, `applyCal`, `data` base64 big-endian float32) answered 202. The IR read back kept t=0 exactly (startTime −256/48000). The test measurement was then deleted. "Save all" to `.mdat` already works through the API (`rew_measure.py`).
- REW 5.40 Beta 151 (API 0.9.9) also has `/import/sweep-recordings/stimulus|response`: REW deconvolves raw recordings itself. Useful as a cross-check, not needed for the normal flow.
- **The free REW API can switch the mic cal file:** `PUT /audio/input-cal` with `calDataAllInputs: {calFilePath, dBFSAt94dBSPL, fullScaleSineVrms}` answered 200. A switch to the 0° file and back to 90° was confirmed by reading it back (REW left on 90°). Send `dBFSAt94dBSPL` along unchanged.
- **The SPL calibration is readable:** `GET /audio/input-cal` → `dBFSAt94dBSPL` = −22.99 (the 2026-11-18 calibration). The script reads it from REW, or from the plan JSON when REW isn't running, and logs it per set.
- **Sweep code exists:** `~/WPlay/tracks/tools/loopback/peq.py` (sounddevice, log sweep, deconvolution) was run on the same UMC.
- **Preset recall exists in the protocol:** `0x20 <slot>` recalls the slot, applies it and saves the live state. The ACK comes back in under 1 s. `0x14` reads the current preset and `0x29 30` the live preset's name (`tracks/docs/protocol.md` §4.3). The probe (`tracks/tools/probe`) currently allows only `--write 20 0` (factory preset).
- The analysis scripts apply the mic cal themselves (`reference/mic-cal/`), so the IR WAVs stay uncalibrated, as now.

## Decided

- **Everything goes into git:** IR WAVs, raw recordings (FLAC), stimulus, per-set log. About 2–3 MB per sweep, roughly 150 MB for a session like 2026-11-22.
- **Presets are recalled by the script** before every sweep block that needs a different preset (same rule as the run sheets: recall each preset every time, no order tricks). It reads the recall back and checks it.
- **File names and IR format don't change**, so the analysis scripts keep working unchanged ([measurements/README.md](../../measurements/README.md)).

## Parts

### 1. Preset recall in tracks (`~/WPlay/tracks`)

- `probe`: allow `--write 20 <slot>` for slots 1..30, not only 0. Wait up to 3 s for the ACK. Then read `0x14` (current preset) and `0x29 30` (live name) and print both.
- After the recall also send `0x39 0`, because a recall doesn't switch a running test tone off (protocol §4).
- Document it in the probe README. Commit it in the tracks repo.

### 2. `tools/sweep.py` (replaces `tools/rew_measure.py` as `mise run measure <set>`)

- **Generic: nothing session-specific in the code.** The script takes the plan file as a required argument (`mise run measure <plan.json> <set>`, no default path). Everything it uses comes from that file:
  - sets, position groups (name, mic instruction, optional baseline delays), channel groups;
  - presets (slot number + expected name);
  - audio device and channel map (sweep outputs, loopback out/in, mic in);
  - sweep parameters (length, range, level, silence tail);
  - check thresholds, SPL offset, REW import on/off.

  The code has no defaults for these. A missing key is an error that names the key. The file format is documented once in [tools/README.md](../../tools/README.md#plan-file), with a minimal example. `docs/plans/next-session-eq-sub.json` gets converted to it, and every future session writes its own plan JSON. The output folder is `measurements/<date>/<set>/`, with the date from `--date` (default today).
- **Audio:** one full-duplex sounddevice stream on the UMC404HD (CoreAudio, 48 kHz), so mic and loopback share one clock.
  - Out 1 or 2 plays the sweep (to DSP In A/B).
  - Out 3 plays the same sweep (loopback).
  - In 1 records the mic, In 2 the loopback.
- **Sweep:** same as now in REW: log sweep, 512k samples (10.9 s), 10 Hz–22.05 kHz, −24 dBFS, short fades. Then about 3 s of silence so the bass decay is recorded.
- **Processing:**
  - Deconvolve mic and loopback against the stimulus by regularised spectral division.
  - t=0 = the loopback IR peak (REW's "Loopback" timing reference).
  - Write the IR WAV exactly as today: 32-bit float, t=0 at sample 256, not normalised, no window, same length as REW's export.
  - The harmonic distortion IRs (before t=0 in the full deconvolution) go into the log as THD per sweep.
- **Per sweep it writes:**
  - `<n> <L|R|S> <position> <tag>.wav`: the IR, as now.
  - `raw/<same name>.flac`: 24-bit, 2 channels (mic, loopback), for reprocessing.
  - One entry in `<set>.json`: time, preset (slot + name as read back), position, output channel, sweep parameters, input peak in dBFS, noise floor and SNR, loopback delay and its cm difference to the 2026-11-18 baseline, THD, git commit, script version.
- **Once per set:** `raw/stimulus.flac`, the device name, and the sample rate as reported.
- **Checks after every sweep; on a failure it offers a redo:**
  - input clipping
  - loopback missing or weak
  - SNR too low
  - delay that points at the wrong speaker or a moved mic (vs the baseline, as `rew_measure.py` does now)
- **Flow per sweep:**
  - The script prints what to do (MOVE MIC → …). You press Enter.
  - The script recalls the preset if it changed and sweeps.
  - Then it checks the result, prints one line, and moves on.
  - At the prompt: `r` = redo the previous sweep, `q` = quit.
  - Resuming: sweeps already on disk are skipped (same as today).
- **REW (optional, while REW is running):** each IR is imported with `/import/impulse-response-data` (identifier = the name, `splOffset` from the plan JSON, `applyCal` true). After each sweep, "Save all" → `<set>.mdat`. If REW isn't running, the script still measures and prints a hint.

### 2b. Electrical checks of an EQ (DSP out → UMC In 3, no amp, no mic)

For each new EQ design, as was done for v1 (2026-11-18) and v2 (2026-11-22). It's the same script, with a different kind of set in the plan JSON:

- **Per-set settings in the plan JSON** (an electrical set has no mic positions, so you don't move anything between sweeps):
  - `kind: "electrical"`
  - its own input channel (UMC In 3 instead of the mic on In 1)
  - no mic cal (`applyCal` false on the REW import)
  - the EQ folder it checks against, e.g. `eq/v3-…`
  - a `before` text with the rewiring, shown before the first sweep and confirmed with Enter
- **Checks:**
  - input peak, SNR and loopback as for room sets; no baseline-delay check
  - the measured curve must match the designed curve within a tolerance set in the JSON (v1 was within 0.05 dB)
- **Comparison with the design, straight after the set:**
  - The script runs the comparison against the EQ folder and prints pass or fail with the largest deviation and where it is.
  - The plot goes to `analysis/output/`.
  - On a fail, re-measure or look at the import before anything goes into the room.
- **`analysis/check_dsp_electrical.py` made generic:** arguments `<set folder> <eq folder> <plot name>` instead of its `v1`/`v2` table with hard-coded folders. `mise run analyse` calls it once per checked EQ, and a new EQ only needs one more line there.

### 2c. Close-ups (mic at ~1 cm from woofer / port, 0° cal), e.g. Sub8 tuning

This is what the 2026-11-18 close-ups did ([closeups](../../measurements/2026-11-18/closeups/): 0° cal, −40 dBFS, port tuning ≈ 35 Hz). It's the same script with `kind: "closeup"`:

- **Per-set overrides in the plan JSON:**
  - `mic_cal`: the cal file (`reference/mic-cal/MM-1C_0deg.txt` for close-ups, the 90° file for room sets)
  - `level_dbfs`: −40 for close-ups
  - positions are the speaker parts (`woofer`, `port`, …), each with its mic instruction
  - channel group per set as usual: mains L/R, or the sub through P04
- **The cal file:**
  - The WAVs stay uncalibrated, as always. The cal file name goes into `<set>.json`, so the analysis and `rew_load.py` know which one applies.
  - For the REW import, the script sets REW's input cal file to the set's file (`PUT /audio/input-cal`, works on the free API) and reads it back. At the end of the set it switches back to the file that was loaded before.
- **Checks:**
  - input peak is strict here, because ~1 cm is loud even at −40 dBFS; a clip means redo at a lower level
  - no baseline-delay check
- **After the set:** the script runs the close-up analysis and prints the tuning per speaker (woofer minimum / port maximum). The Sub8 is bass reflex with a front port (user, 2026-11-22), so its positions are `woofer` and `port`, the same as the mains.
- **`analysis/analyse_closeups.py` made generic:**
  - arguments `<set folder> <plot name>`; the cal file comes from `<set>.json` (sets from before `sweep.py` have none, so those are given as a third argument)
  - woofer/port pairs found by position name
  - `mise run analyse` keeps one line for the 2026-11-18 set

### 3. `tools/rew_load.py <set folder>`

Generic too: works on any set folder written by `sweep.py`, reads only that folder's `<set>.json`, with no plan file needed. Builds `<set>.mdat` from a set's WAVs and `<set>.json` (for later, or when REW was closed): clear REW (asks first if REW holds measurements), import the WAVs, Save all.

### 4. `analysis/check_sweep_vs_rew.py`

Takes pairs of IR WAVs (REW, Python) as arguments, no file names in the code: level difference vs frequency (1/24 oct), t=0 offset, noise. Pass criteria: in the validation run sheet.

### 5. Dependencies and docs

- `pyproject.toml`: add `sounddevice`, `soundfile`.
- `mise.toml`: point `measure` at `sweep.py`, with the arguments passed through (`mise run measure <plan.json> <set>`). Add `rew-load <set folder>`.
- [measurements/README.md](../../measurements/README.md): new files (`raw/`, `<set>.json`), measuring section.
- [current-setup.md](../current-setup.md): DSP USB to the Mac in measuring mode.
- [decisions.md](../decisions.md): a row.
- `rew_measure.py` deleted 2026-11-22.

## Validation run sheet (before switching)

**Done, passed** (result: [findings/2026-11-22-sweep-validation.md](../../findings/2026-11-22-sweep-validation.md)).

Plan file: [sweep-check.json](sweep-check.json). Run each set with `mise run measure docs/plans/sweep-check.json <set>`, REW running.

### Electrical (done 2026-11-22)

- [x] `sweep-check-electrical`: P03, `1 L dsp py` + `py2` vs REW's `dsp-electrical-v2`: within 0.04 dB above 50 Hz; below, the P03 PEQ noise
- [x] `sweep-check-electrical-flat`: P01, `py` + `py2` + a REW sweep `1 L dsp rew` in the same folder: within 0.016 dB 20 Hz–20 kHz
- [x] `sweep-check-electrical-flat-pre2`: same with 2 s pre-roll: same result

### Set `sweep-check-seat` (room wiring, amp 50)

Sanity check: the mic is re-placed (±5 cm), so only 30–300 Hz and no t=0 test, against REW's `eq-seat` (P03).

- [x] Rewire: DSP Out 1 → amp L, DSP Out 2 → amp R, amp on, volume 50

**seat**: seat spot, placed by the loopback delays ([session checklist](../procedures/session-checklist.md))
- [x] Script recalls P03, reads it back
- [x] #1 `1 L seat py`, #2 `2 R seat py` (mic ~5 cm too high, found afterwards)
- [x] `sweep-check-seat2`, mic lowered: REW sweep `1 L seat rew`, then `1 L seat py`, `1 L seat py2`, mic untouched

Compare:

```sh
uv run python analysis/check_sweep_vs_rew.py --t0-info analysis/output/sweep_vs_rew_seat.png \
  "measurements/2026-11-22/eq-seat/1 L seat eq2 Nov 22.wav" "measurements/<date>/sweep-check-seat/1 L seat py.wav" 30 300 1.0 \
  "measurements/2026-11-22/eq-seat/2 R seat eq2 Nov 22.wav" "measurements/<date>/sweep-check-seat/2 R seat py.wav" 30 300 1.0 \
  > analysis/output/sweep_vs_rew_seat.txt
```

Planned pass criterion was ±1 dB at 30–300 Hz vs `eq-seat`; with a re-placed mic that's too tight (see the finding). The same-spot REW comparison in `sweep-check-seat2` replaced it.

## Open questions

- The REW sweep level "−24 dBFS": peak or RMS? The electrical validation set shows it (agreed 2026-11-22). The script then matches REW's level exactly.
  - **Answered 2026-11-22: peak.** The first electrical run played −24 + 3.01 dB (RMS guess) and came out +3.04 dB above REW's IR, flat 200 Hz–20 kHz. `REW_LEVEL_TO_PEAK_DB` set to 0.

Answered 2026-11-22: in measuring mode the DSP and the UMC are both on USB to the Mac (seen in `ioreg`: "Dsp Process" VID 0x0168 PID 0x0821, "UMC404HD 192k"). Chrome (configurator) is closed while measuring, so only the script talks to the DSP. The script still checks at the start that the probe can connect, and stops with a hint if not.

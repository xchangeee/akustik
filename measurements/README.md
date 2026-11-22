# Measurements

Raw data: one folder per day, one subfolder per measurement set. Each set holds the REW project (`.mdat`) and its IRs (`.wav`; from REW's export or from [tools/sweep.py](../tools/sweep.py), same format), which the scripts in [../analysis/](../analysis/README.md) read. Findings: [../findings/](../findings/).

## Sessions

| Folder | DSP state | Mic cal | Content | Findings |
| --- | --- | --- | --- | --- |
| [2026-11-18/seat/](2026-11-18/seat/) | FLAT | 90° | L, R at the main seat (sitting upright) | [setup checks](../findings/2026-11-17-setup-checks.md), [baseline](../findings/2026-11-18-baseline.md) |
| [2026-11-18/positions/](2026-11-18/positions/) | FLAT | 90° | 6 positions around the seat, L and R: pos1 left30, pos2 right30, pos3 fwd20, pos4 back20, pos5 up10, pos6 down10 (cm) | [baseline](../findings/2026-11-18-baseline.md) |
| [2026-11-18/corners/](2026-11-18/corners/) | FLAT | 90° | Floor corners front left / front right, L and R | [baseline](../findings/2026-11-18-baseline.md#corners) |
| [2026-11-18/dj/](2026-11-18/dj/) | FLAT | 90° | DJ spot, standing ear height: pos, left30, right30, fwd30, back30, up30, down30, L and R | [baseline](../findings/2026-11-18-baseline.md#dj-position--lr-sum) |
| [2026-11-18/closeups/](2026-11-18/closeups/) | FLAT | **0°** | Woofer and port at ~1 cm, L and R, −40 dBFS | [baseline](../findings/2026-11-18-baseline.md#close-ups-wooferport) |
| [2026-11-18/dsp-electrical/](2026-11-18/dsp-electrical/) | EQ v1 | none | DSP Out 1/2 → UMC In 3, no amp/mic | [eq-v1-flat](../findings/eq-v1-flat.md#dsp-electrical-check) |
| [2026-11-22/dsp-electrical-v2/](2026-11-22/dsp-electrical-v2/) | EQ v2 (P03) | none | DSP Out 1/2 → UMC In 3, no amp/mic | [eq-v2-electrical](../findings/2026-11-22-eq-v2-electrical.md) |
| [2026-11-22/eq-seat/](2026-11-22/eq-seat/) | EQ v1 (P02) + v2 (P03) interleaved | 90° | Seat + 6 positions as 11-18, L and R, tags `eq1`/`eq2` | [eq-room](../findings/2026-11-22-eq-room.md) |
| [2026-11-22/eq-corners/](2026-11-22/eq-corners/) | EQ v1 + v2 interleaved | 90° | Floor corners front left / right, L and R | [eq-room](../findings/2026-11-22-eq-room.md) |
| [2026-11-22/eq-dj/](2026-11-22/eq-dj/) | EQ v1 + v2 interleaved | 90° | DJ spot, 7 positions as 11-18, L and R (measured with `mise run measure`, no date in names) | [eq-room](../findings/2026-11-22-eq-room.md) |
| [2026-11-22/sweep-check-electrical-run1/](2026-11-22/sweep-check-electrical-run1/) | P03 | none | First sweep.py try: sweep 3 dB too loud (RMS level guess) | [sweep-validation](../findings/2026-11-22-sweep-validation.md) |
| [2026-11-22/sweep-check-electrical/](2026-11-22/sweep-check-electrical/) | P03 | none | sweep.py, DSP Out 1 → In 3, `py` + `py2` | [sweep-validation](../findings/2026-11-22-sweep-validation.md) |
| [2026-11-22/sweep-check-electrical-flat/](2026-11-22/sweep-check-electrical-flat/) | P01 | none | sweep.py `py` + `py2` and one REW sweep `1 L dsp rew` (own `.mdat`), same wiring | [sweep-validation](../findings/2026-11-22-sweep-validation.md) |
| [2026-11-22/sweep-check-electrical-flat-pre2/](2026-11-22/sweep-check-electrical-flat-pre2/) | P01 | none | Same with 2 s pre-roll | [sweep-validation](../findings/2026-11-22-sweep-validation.md) |
| [2026-11-22/sweep-check-seat/](2026-11-22/sweep-check-seat/) | P03 | 90° | sweep.py at the seat, L and R; mic ~5 cm too high | [sweep-validation](../findings/2026-11-22-sweep-validation.md#seat-room-wiring-p03-mic-at-the-seat) |
| [2026-11-22/sweep-check-seat2/](2026-11-22/sweep-check-seat2/) | P03 | 90° | Seat, L only, mic untouched: REW `1 L seat rew` (own `.mdat`), then sweep.py `py`, `py2`. Sub8 out of the room | [sweep-validation](../findings/2026-11-22-sweep-validation.md#seat-room-wiring-p03-mic-at-the-seat) |
| [2026-11-22/seat-noise/](2026-11-22/seat-noise/) | — | 90° | Mic at the seat, nothing playing (room noise per band) | [sweep-validation](../findings/2026-11-22-sweep-validation.md) |
| [2026-11-22/tone-check/](2026-11-22/tone-check/) | P01 | none | Steady sines 10 Hz–1 kHz, DSP Out 1 → In 3 (truth for the low end) | [sweep-validation](../findings/2026-11-22-sweep-validation.md) |
| [2026-11-22/in3-noise/](2026-11-22/in3-noise/) | P03 / P01 / muted | none | Noise captures on In 3 while unplugging things one by one (`noise.txt`) | [sweep-validation](../findings/2026-11-22-sweep-validation.md) |
| [2026-11-22/nosub-seat/](2026-11-22/nosub-seat/) | EQ v1 (P02) | 90° | One sweep, L at the main seat, Sub8 out of the room (resonance test) | [eq-room](../findings/2026-11-22-eq-room.md#sub-out-of-the-room-test-and-the-p02-routing) |

All 2026-11-18 sets: 512k sweep, −24 dBFS (close-ups −40), loopback timing reference, amp volume and In 1 gain as fixed in setup Phase D. Positions ball-parked by hand.

## Conventions for new measurements

- Folder: `measurements/<YYYY-MM-DD>/<set>/`, with the REW project saved in it as `<set>.mdat` (the date is in the folder; sets before 2026-11-22 have `<YYYY-MM-DD>-<set>.mdat`). Sets measured with an EQ loaded get a prefix, e.g. `eq1-seat`, `eq2-dj` (`eq-seat` for v1 and v2 interleaved in one set); sub-only sets `subC-seat`, `subA-dj`.
- REW measurement names (they become the WAV names): `<n> <L|R> <position>`, e.g. `1 L pos1 left30` (REW: "Prefix with output" on, "Use as entered"). Until 2026-11-22 the date was appended (`1 L pos1 left30 Nov 18`); the scripts don't depend on it. Same position names as above, so the scripts can pair them across sets.
  - Sub: `3 S <position> <subA|subC>` (n = DSP Out 3).
  - Sets holding several presets measured interleaved at the same mic spot (prefix `eq-`, e.g. `eq-seat`): preset tag at the end, `1 L pos1 left30 eq1`.
- **Measuring a set:** `mise run measure <plan.json> <set>` ([tools/sweep.py](../tools/sweep.py)).
  - You: move the mic when told, press Enter. `r` = redo the previous sweep, `q` = quit; running it again resumes.
  - The script: recalls the DSP preset, sweeps, checks the sweep, saves, imports into REW (if running).
  - REW was closed? `mise run rew-load <set folder>` builds the `.mdat` later.
  - Plan file format: [tools/README.md](../tools/README.md#plan-file).
- **Files per set (sweep.py):**
  - `<name>.wav`: the IR, same format as REW's export.
  - `raw/<name>.flac`: the recording (mic + loopback), to recompute the IR.
  - `<set>.json`: per sweep the preset read back, levels, SNR, delay, THD.
  - `<set>.mdat`: the REW project.
- Older sets: until `eq-corners` measured in REW by hand, `eq-dj` and `nosub-seat` with an older REW-driven script (deleted, in git history before 2026-11-22's sweep.py commit).
- **IR export** (impulse response as WAV): 32-bit float, measured IR, **t=0 at sample 256**, no normalise, no window. 48 kHz.
- Add a row to the table above.

The two seat WAVs (`1 first sweep, left speaker only …`, `2 first sweep, right speaker o…`) predate these names; the scripts find them by `first sweep`.


# Measurements

Raw data from REW: one folder per day, one subfolder per measurement set. Each set holds the REW project (`.mdat`) and its IR exports (`.wav`), which the scripts in [../analysis/](../analysis/README.md) read. Findings: [../findings/](../findings/).

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

All 2026-11-18 sets: 512k sweep, −24 dBFS (close-ups −40), loopback timing reference, amp volume and In 1 gain as fixed in setup Phase D. Positions ball-parked by hand.

## Conventions for new measurements

- Folder: `measurements/<YYYY-MM-DD>/<set>/`, with the REW project saved in it as `<set>.mdat` (the date is in the folder; sets before 2026-11-22 have `<YYYY-MM-DD>-<set>.mdat`). Sets measured with an EQ loaded get a prefix, e.g. `eq1-seat`, `eq2-dj` (`eq-seat` for v1 and v2 interleaved in one set); sub-only sets `subC-seat`, `subA-dj`.
- REW measurement names (they become the WAV names): `<n> <L|R> <position>`, e.g. `1 L pos1 left30` (REW: "Prefix with output" on, "Use as entered"). Until 2026-11-22 the date was appended (`1 L pos1 left30 Nov 18`); the scripts don't depend on it. Same position names as above, so the scripts can pair them across sets.
  - Sub: `3 S <position> <subA|subC>` (n = DSP Out 3).
  - Sets holding several presets measured interleaved at the same mic spot (prefix `eq-`, e.g. `eq-seat`): preset tag at the end, `1 L pos1 left30 eq1`.
- **Measuring a set:** `mise run measure <set>` ([tools/rew_measure.py](../tools/rew_measure.py), sets in [docs/plans/next-session-eq-sub.json](../docs/plans/next-session-eq-sub.json)). It names, exports and saves via the REW API (REW 5.40 beta); you only click Start in REW's Measure dialog. The free API can't start sweeps or set level/sweep/timing (needs REW Pro), so those stay set in REW and the script checks them.
- **One REW project per set:** REW is cleared (Remove all) before each set, so the `.mdat` holds exactly that set's measurements. Save it and export the IRs into the set folder before clearing for the next set.
- **IR export** (impulse response as WAV): 32-bit float, measured IR, **t=0 at sample 256**, no normalise, no window. 48 kHz.
- Add a row to the table above.

The two seat WAVs (`1 first sweep, left speaker only …`, `2 first sweep, right speaker o…`) predate these names; the scripts find them by `first sweep`.

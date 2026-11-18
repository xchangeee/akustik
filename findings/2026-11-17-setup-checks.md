# Setup checks (2026-11-17 / 18)

Results of the one-time setup in [docs/procedures/measurement-setup.md](../docs/procedures/measurement-setup.md) (phases A–F), before the baseline measurements ([2026-11-18-baseline.md](2026-11-18-baseline.md)).

## Mic cal files

- Seller files (JustOct `.cal`) are in [reference/mic-cal/vendor-original/](../reference/mic-cal/vendor-original/), untouched: `MM1CBP_allein_00d.cal`, `MM1CBP_allein_90d.cal`, a plot (`MM1CBP_allein_Xd.gif`) and `Test1.mdat` (the seller's REW test measurements from Feb 2024, not needed).
- Converted for REW: [reference/mic-cal/MM-1C_0deg.txt](../reference/mic-cal/MM-1C_0deg.txt) and [MM-1C_90deg.txt](../reference/mic-cal/MM-1C_90deg.txt) (frequency + dB only, UTF-8, comment lines start with `*`).
  Checked: 134 points, 10 Hz to 21.1 kHz, frequencies increasing, 0 dB at 1 kHz. The original phase column was all zeros, so it was dropped.
- What the curves say: flat from ~60 Hz to ~2 kHz. Below that the mic rolls off (−3.5 dB at 20 Hz, −11 dB at 10 Hz). REW corrects for this, so bass readings are right with the file loaded and too low without it.
  Above 2 kHz: 0° rises to +5.4 dB around 10 kHz, 90° stays within about +2.5/−5.6 dB.
- Sensitivity at 1 kHz: 3.72 mV/Pa (0°), 3.65 mV/Pa (90°). Not needed in REW (the UMC gain knob has no scale, so SPL calibration was done with the iPhone instead).
- Serial number check not needed: only one mic, files came with it.

## Phase A: loopback (2026-11-17)

Loopback (Out 3 → In 2) flat within ~0.2 dB from 20 Hz to 20 kHz, phase within ±10°, headroom 10.8 dB at −12 dBFS sweep, In 2 gain at minimum.
Soundcard cal file skipped (not needed).

## Phase B/C: noise and hum (2026-11-17)

- Mic only (gain ≈ middle, 90° cal, chain not connected): mic reacts to claps; quiet-room peak sample ≈ −55 dBFS; noise rises toward the bass (normal); no obvious 50/100/150 Hz spikes.
- Chain connected, amp at normal listening volume, 8 averages: noise floor same as mic only (56 dB vs 55 dB unweighted, uncalibrated), no new hum spikes; only a small bump near 50 Hz, far below measurement level.

## Phase D: levels and the L/R difference (2026-11-17)

- Pink periodic −24 dBFS on L+R together → iPhone ≈ 80 dB(C) at the seat, REW peak sample −12.3 dBFS, noise floor well below. Amp + mic gain fixed from here (user has a photo of both knobs). Single speaker reads ~3–6 dB lower.
- L/R check (pink −24 dBFS, RTA unweighted, uncalibrated): L 89.9 dB (peak −16.7 dBFS), R 92.2 dB (peak −15.4 dBFS), L+R 94.2 dB. **R ~2.3 dB louder.**
- After moving R closer to the walls: L 89.5 dB(C) REW / 73–74 dB(C) iPhone, peak −17.1 dBFS; R 92.1 dB(C) REW / 75–77 dB(C) iPhone, peak −14.4 dBFS. After re-centring the mic, final levels for the session:

| | REW RTA, uncalibrated | iPhone NIOSH SLM, C-weighted | Peak |
| --- | --- | --- | --- |
| L (out 1) | 89.1 dB(C) | 73–74 dB(C) | −16.7 dBFS |
| R (out 2) | 91.4 dB(C) | 75–76 dB(C) | −15.5 dBFS |

- Swap test 1 (DSP outs swapped): out 1 → right speaker 91.4 dB(C), out 2 → left speaker 89.1 dB(C) → louder side stays on the right, so interface/DSP/adapters/RCA are fine.
- Swap test 2 (speaker cables swapped at the amp): amp L → right speaker 91.5 dB(C), amp R → left speaker 89.1 dB(C) → amp is fine too. Speaker cables put back to normal afterwards (amp L → left speaker), confirmed.
- **Cause: the right speaker itself or the room around it.** Resolved 2026-11-18 by the close-ups: woofers identical, R's extra level is room bass ([baseline, close-ups](2026-11-18-baseline.md#close-ups-wooferport)).

## Phase E: SPL calibration (2026-11-18)

- REW reported input clipping at ~105 dB SPL (≈30 dB headroom at ~74 dB). iPhone showed 87.6 dB(C) during REW's calibration signal (whether Sub Cal was selected during calibration is unconfirmed; the check passed anyway).
- Check, pink random −24 dBFS, Speaker Cal (500–2000 Hz): REW L 74.6 / R 73.8 dB(C); iPhone C within 1 dB of REW.
- Side finding (calibrated REW, pink random −24 dBFS): Sub Cal 30–80 Hz L 76.2 / R 81.8 dB(C) (an earlier R reading was 77.1, unexplained); Speaker Cal 500–2000 Hz L 74.6 / R 73.8. **R's extra level is in the bass (30–80 Hz: R +5.6 dB), not the mids (500–2000 Hz: R −0.8 dB).**
- [reference/rew-settings-2026-11-17.txt](../reference/rew-settings-2026-11-17.txt) is REW's preferences export from *before* this calibration (mic cal offset still the default 120).

## Phase F: first sweeps at the seat (2026-11-18)

REW measurements 3 = L, 4 = R; sweep 512k, 10 Hz–22.05 kHz, −24 dBFS, loopback timing, 90° cal. IR exports: [measurements/2026-11-18/seat/](../measurements/2026-11-18/seat/).

- Timing reference works: delay vs loopback L 9.284 ms (3.184 m), R 9.153 ms (3.139 m); difference 0.13 ms, below the 0.2 ms threshold, so no delay needed. (With loopback timing the peak sits at the acoustic delay, not at t = 0.)
- Same polarity: both show a small spike up (+65 % L / +70 % R) and then the main spike down (−100 %).
- Levels similar from 1 to 8 kHz (L 72–75, R 72–74 dB). **Bass differs a lot.**
- Curves plausible: treble falls gently (about 74 dB at 2–8 kHz to 66–68 dB at 20 kHz); big bass peaks/dips.
- No clipping (peak input before clipping 105 dB SPL).
- Readings (1/6 oct): L: peak ~85 dB @ ~42 Hz, hump ~82 dB @ 90–110 Hz, dips @ ~55 Hz (~71), ~150 Hz, ~390 Hz (~66), steep roll-off below ~35 Hz (30 Hz ~66).
  R: peaks ~89–90 dB @ ~55 Hz and ~87 dB @ ~85 Hz, ~81 dB @ ~125 Hz, 30 Hz ~77, deep dip ~64 dB @ ~190 Hz.
  So R has much more bass from 25 to 90 Hz, with peaks and dips at different frequencies than L: points to room/position.
- R impulse has a small spike at ~−780 ms (~25 dB above the noise floor), outside the window. Probably a distortion product or a noise during the sweep; not checked.
- Early reflections visible in both impulses at ~1 ms and ~6 ms after the direct sound.

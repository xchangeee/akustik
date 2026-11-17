# Handoff: measurement session status

Last updated: 2026-11-18 (Phases E and F done).
Read this first, then [room-acoustics-context.md](room-acoustics-context.md) (room, gear, goals, measurement plan)
and [measurement-prep-checklist.md](measurement-prep-checklist.md) (step-by-step setup; ticked = done, with dated results).

## Where we are

Setup phases 1–4 and A–F of the checklist are done (2026-11-18). First sweeps at the main seat exist (REW measurements 3 = L, 4 = R; not saved to a file yet unless the user did). All sanity checks passed; results are in the checklist, Phase F.
Measurement plan step 3 done 2026-11-18: 6 positions + seat per speaker, analysed from IR exports → [measurements/2026-11-18-analysis.md](measurements/2026-11-18-analysis.md).
**Next step: corner (3b) and DJ position (3c) measurements, same workflow (measure, Save all, export IRs as WAV: 32-bit float, t=0 at 256, no normalise/window), then EQ design.**

## Current physical setup (as wired now)

| From | To | Notes |
| --- | --- | --- |
| MM-1C mic (XLR) | UMC404HD In 1 | +48 V on, PAD off, LINE/INST off |
| UMC Out 3 (rear) | UMC In 2 | loopback / timing reference, TRS–TRS, In 2 = LINE, gain min, PAD off |
| UMC Out 1 | DSP In A (1) | TRS–TRS. Plan said In 3/4; In 1/2 is fine because the EQ will sit on the outputs |
| UMC Out 2 | DSP In B (2) | TRS–TRS |
| DSP Out 1 / Out 2 | A300 RCA L / R | **temporarily via TS adapters** (sssnake 1820, RCA female → 6.3 mm TS): shorts the DSP's cold output. Replace with TRS → 2× RCA (use tip/white only). User accepted the risk for now |

- MIX knob fully at PLAYBACK. All other UMC gains at minimum except In 1 (mic) and whatever In 2 was set to in Phase A (gain min gave −12 dBFS).
- macOS output = MacBook speakers (verified). UMC at 48 kHz.
- Speakers: both pushed back to 0.33 m (front baffle to rear wall). R speaker moved farther from the right side wall (0.43 m). L side distance, L–R spacing and seat distance not yet noted.
- Mic at the main seat, centred between the speakers, pointing up, 90° cal file.

## DSP (t.racks DSP 4x4 Mini)

User has software access to it (a GUI with an "Import REW filters…" button). State is flat: routing A→1, B→2, C→3, D→4; all faders 0 dB; PEQ bypassed (all bands 0 dB); HPF/LPF off; gate/compressor off; delay 0; mute and polarity off. No separate limiter (use the compressor later).
Saved as preset **"FLAT"** (confirmed 2026-11-17).

Amp (SMSL A300): EQ modes off, no high-pass, RCA input.

## REW settings

- Soundcard: UMC404HD 192k, out port "SPEAKER", in port "MICROPHONE (In 1)"; outputs renamed 1–4 via channel mapping.
- Input 1, output 1 (L) / 2 (R), loopback input 2, timing reference output 3. Timing reference "Loopback" is chosen in the **Measure dialog** (no checkbox in Analysis in this version).
- Mic cal: `cal/MM-1C_90deg.txt`.
- Use **−24 dBFS** for pink noise and sweeps, fixed. Amp volume sets loudness. (The Measure dialog last had −12 dBFS from the loopback test: change it.)
- [rew-settings.txt](rew-settings.txt): user's export of REW preferences (17 Nov, 22:07). In it, the mic cal offset still shows the default (120), so the SPL calibration is probably not done yet.

## Levels (fixed for this session; don't touch)

Amp volume and In 1 gain were set in Phase D and must stay where they are. The user has a photo of both knobs (not needed for now).
Pink periodic −24 dBFS, mic centred:

| | REW RTA, uncalibrated | iPhone NIOSH SLM, C-weighted | Peak |
| --- | --- | --- | --- |
| L (out 1) | 89.1 dB(C) | 73–74 dB(C) | −16.7 dBFS |
| R (out 2) | 91.4 dB(C) | 75–76 dB(C) | −15.5 dBFS |

(Those REW numbers were before calibration. Phase E done 2026-11-18: REW now matches the iPhone within 1 dB; input clips at ~105 dB SPL.)

## Findings so far

- **Cal files** came from the seller as JustOct `.cal` (in `MM1CBP_allein_Xd/`, untouched originals, plus a plot and the seller's REW test file). Converted to REW format in `cal/`. Mic rolls off below 60 Hz (−3.5 dB at 20 Hz, −11 dB at 10 Hz); sensitivity 3.7 mV/Pa. Only one mic, so no serial check needed.
- **Loopback** (Out 3 → In 2): flat within 0.2 dB 20 Hz–20 kHz. No soundcard cal file needed.
- **Noise / hum:** quiet room fine; with amp on at listening volume no new hum, only a small bump near 50 Hz far below signal level.
- **R speaker ~2.3 dB louder than L.** Not the mic position (re-centred), not the interface/DSP/adapters/cables (swap test 1: swapped DSP outs), not the amp (swap test 2: swapped speaker cables). **Cause: the right speaker itself or the room around it.** 2026-11-18: band-limited noise shows the excess is in the bass only (30–80 Hz: R +5.6 dB; 500–2000 Hz: R −0.8 dB), pointing to room/boundary or R's woofer/port. Tell apart with 1 m on-axis gated sweeps of each speaker and close-up woofer measurements. Fix either way: DSP output gain per channel (after the sweeps).
- Speaker cables are back to normal (amp L → left speaker), confirmed.

## Next steps

1. ~~Phase E~~ done 2026-11-18.
2. ~~Phase F~~ done 2026-11-18.
3. Then the full measurement plan in the context file (seat positions, corner, DJ spot, close-up woofer/port with the 0° file, electrical DSP check via In 3).

## Analysis workflow

- User measures in REW and exports IRs as WAV into `measurements/<date>-<name>/`; Claude analyses with [analysis/analyse_positions.py](analysis/analyse_positions.py).
- Python env: use **mise + uv** (user's preference), e.g. `mise exec python@3.14 uv@0.13.5 -- uv venv …` then `uv pip install numpy scipy matplotlib`.

## Working with this user

- Watch the generator's band radio buttons in their screenshots (Full range / Sub Cal / Speaker Cal): they were left on Sub Cal several times.
- Communicates in short messages and screenshots of REW / the DSP GUI. Walk them through one step at a time, read the screenshots closely.
- **Read what they write carefully and don't infer facts they didn't state.** An earlier misreading ("distance unchanged" taken as "left speaker didn't move") caused real frustration. If something is ambiguous, ask.
- Keep the checklist updated with dated results as steps are done.

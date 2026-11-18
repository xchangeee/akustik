# Current setup

What is wired and configured **right now**. Keep this file true: update it whenever something is rewired or reconfigured (and note the change in [SESSION-LOG.md](../SESSION-LOG.md)).
Last checked: 2026-11-18.

## Wiring (measurement setup, as wired now)

| From | To | Notes |
| --- | --- | --- |
| MM-1C mic (XLR) | UMC404HD In 1 | +48 V on, PAD off, LINE/INST off |
| UMC Out 3 (rear) | UMC In 2 | loopback / timing reference, TRS–TRS, In 2 = LINE, gain min, PAD off |
| UMC Out 1 | DSP In A (1) | TRS–TRS |
| UMC Out 2 | DSP In B (2) | TRS–TRS |
| DSP Out 1 / Out 2 | A300 RCA L / R | **temporarily via TS adapters** (sssnake 1820, RCA female → 6.3 mm TS): shorts the DSP's cold output. Replace with TRS → 2× RCA (use tip/white only). See [decisions.md](decisions.md) |

- After the electrical check (2026-11-18) DSP Out 1/2 may still go to UMC In 3 instead of the amp: rewire before the next acoustic measurement.
- MIX knob fully at PLAYBACK. All other UMC gains at minimum except In 1 (mic) and In 2 (loopback, gain min gave −12 dBFS).
- macOS output = MacBook speakers (verified). UMC at 48 kHz.
- Mic at the main seat, centred between the speakers, pointing up, 90° cal file.
- Speaker placement: see [context.md, Room](context.md#room).

## Levels (fixed; don't touch)

Amp volume and UMC In 1 gain were set in setup Phase D (2026-11-17) and must stay where they are; the user has a photo of both knobs.
REW is SPL-calibrated for this gain (2026-11-18, within 1 dB of the iPhone; input clips at ~105 dB SPL).
REW output level for pink noise and sweeps: **−24 dBFS**, fixed (close-ups −40 dBFS). Amp volume sets loudness.
Level numbers per speaker: [findings/2026-11-17-setup-checks.md](../findings/2026-11-17-setup-checks.md#phase-d-levels-and-the-lr-difference-2026-11-17).

## DSP (t.racks DSP 4x4 Mini)

Configured with the **user's own configurator** in `~/WPlay/tracks` (browser/WebHID, 1:1 reimplementation of the vendor editor from the reverse-engineered firmware/protocol). Parameter grids, filter shapes and measurements: `tracks/docs/protocol.md`, `tracks/docs/measurements.md`; REW filter import: `tracks/web/src/rew.ts`. REW is only used for measuring.

| Preset | Content | Status |
| --- | --- | --- |
| P01 **FLAT** | routing A→1, B→2, C→3, D→4; all faders 0 dB; PEQ bypassed (all bands 0 dB); HPF/LPF off; gate/compressor off; delay 0; mute and polarity off | saved 2026-11-17; for re-measuring |
| EQ v1 (flat target) | [eq/v1-flat/](../eq/v1-flat/) PEQ on Out 1/2 + HPF Butterworth 24, 29.8 Hz (set by hand in the crossover), EQ Bypass off | imported 2026-11-18, electrically checked. **Unconfirmed:** whether it was stored in its own slot with P01 FLAT kept |
| EQ v2 (Harman) | [eq/v2-harman/](../eq/v2-harman/), same HPF | not imported; use a separate slot for A/B with v1 |

Compressor/limiter: off on all outputs (procedure: [procedures/output-limiter.md](procedures/output-limiter.md), after the EQ is final).

Amp (SMSL A300): EQ modes off, no high-pass, RCA input.

## REW

- Soundcard: UMC404HD 192k, out port "SPEAKER", in port "MICROPHONE (In 1)"; outputs renamed 1–4 via channel mapping.
- Input 1, output 1 (L) / 2 (R), loopback input 2, timing reference output 3. Timing reference "Loopback" is chosen in the **Measure dialog** (no checkbox in Analysis in this version).
- Mic cal: [reference/mic-cal/MM-1C_90deg.txt](../reference/mic-cal/MM-1C_90deg.txt) (0° file for close-ups).
- Sweep 512k, 10 Hz–22.05 kHz, −24 dBFS.
- IR export settings: [measurements/README.md](../measurements/README.md).
- [reference/rew-settings-2026-11-17.txt](../reference/rew-settings-2026-11-17.txt): REW's own preferences export from 2026-11-17, before the SPL calibration. A fresh export would capture the calibrated state.

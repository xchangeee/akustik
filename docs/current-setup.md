# Current setup

What is wired and configured **right now**. Keep this file true: update it whenever something is rewired or reconfigured (and note the change in [SESSION-LOG.md](../SESSION-LOG.md)).
Last checked: 2026-11-20.

## Two modes

The DSP is moved between two setups:

1. **Live** (normal use, **current**): DSP in the hi-fi rack, fed by TV and DJ mixer, out to the amp. UMC not connected.
2. **Measuring**: DSP taken out of the rack and connected to the UMC (table below).

## Wiring: live (as wired now, 2026-11-20)

| From | To | Notes |
| --- | --- | --- |
| TV analog out (3.5 mm TRS stereo) | DSP In A / In B | via adapter cable |
| DJ mixer RCA master out | DSP In C / In D | keep the master level moderate (inputs clip at ~+9.5 dBu): [context.md](context.md#signal-chain-normal-use-target) |
| DSP Out 1 / Out 2 | A300 RCA L / R | still via the TS adapters (see the measuring table) |

- Routing in **all presets**: A+C → Out 1, B+D → Out 2 (summed, so whichever source plays is heard).
- Usually only one source plays at a time. The mixer is usually switched off completely. TV and mixer are on the same power line.
- Checked 2026-11-20: TV playing with the mixer on but idle, no hum or hiss.
- TV settings (confirmed 2026-11-21): all TV sound processing off, analog output level fixed at 80/100.
- Source levels (2026-11-20): TV analog output volume 80/100, mixer master +3 dB on the master level meter. Both set by ear, no difference in loudness noticed. The amp volume positions per EQ ([findings/2026-11-20-listening.md](../findings/2026-11-20-listening.md#amp-volume-smsl-a300-per-eq)) assume these source levels.

## Wiring: measuring

| From | To | Notes |
| --- | --- | --- |
| MM-1C mic (XLR) | UMC404HD In 1 | +48 V on, PAD off, LINE/INST off |
| UMC Out 3 (rear) | UMC In 2 | loopback / timing reference, TRS–TRS, In 2 = LINE, gain min, PAD off |
| UMC Out 1 | DSP In A (1) | TRS–TRS |
| UMC Out 2 | DSP In B (2) | TRS–TRS |
| DSP Out 1 / Out 2 | A300 RCA L / R | **temporarily via TS adapters** (sssnake 1820, RCA female → 6.3 mm TS): shorts the DSP's cold output. Replace with TRS → 2× RCA (use tip/white only). See [decisions.md](decisions.md) |

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
| P01 **FLAT** | routing A+C→1, B+D→2 (summed, changed 2026-11-20; was A→1, B→2, C→3, D→4); all faders 0 dB; PEQ bypassed (all bands 0 dB); HPF/LPF off; gate/compressor off; delay 0; mute and polarity off | saved 2026-11-17; for re-measuring. In the measuring setup only A/B are connected, so the summing doesn't matter |
| P02 **EQ v1 (flat target)**, for loud sessions | routing as P01; [eq/v1-flat/](../eq/v1-flat/) PEQ on Out 1/2 + HPF Butterworth 24, 29.8 Hz (set by hand in the crossover), EQ Bypass off | slot 2 (P01 FLAT untouched); imported 2026-11-18, electrically checked |
| P03 **EQ v2 (Harman)**, everyday | copy of P02 with only the PEQ replaced by [eq/v2-harman/](../eq/v2-harman/); same HPF Butterworth 24, 29.8 Hz, EQ Bypass off | slot 3, imported 2026-11-20; not electrically checked; listened to 2026-11-20 ([findings/2026-11-20-listening.md](../findings/2026-11-20-listening.md)) |

Compressor/limiter: off on all outputs (procedure: [procedures/output-limiter.md](procedures/output-limiter.md), after the EQ is final).

Amp (SMSL A300): EQ modes off, no high-pass, RCA input. Volume positions per EQ (v2: everyday 30–35, fun 40–45, above 45 only briefly; v1: fun 50): [findings/2026-11-20-listening.md](../findings/2026-11-20-listening.md#amp-volume-smsl-a300-per-eq).

## REW

- Soundcard: UMC404HD 192k, out port "SPEAKER", in port "MICROPHONE (In 1)"; outputs renamed 1–4 via channel mapping.
- Input 1, output 1 (L) / 2 (R), loopback input 2, timing reference output 3. Timing reference "Loopback" is chosen in the **Measure dialog** (no checkbox in Analysis in this version).
- Mic cal: [reference/mic-cal/MM-1C_90deg.txt](../reference/mic-cal/MM-1C_90deg.txt) (0° file for close-ups).
- Sweep 512k, 10 Hz–22.05 kHz, −24 dBFS.
- IR export settings: [measurements/README.md](../measurements/README.md).
- [reference/rew-settings-2026-11-17.txt](../reference/rew-settings-2026-11-17.txt): REW's own preferences export from 2026-11-17, before the SPL calibration. A fresh export would capture the calibrated state.

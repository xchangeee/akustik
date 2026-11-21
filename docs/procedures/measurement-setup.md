# Measurement prep: step-by-step checklist

For: Omnitronic MM-1C + Behringer UMC404HD + macOS + REW, measuring through the t.racks DSP and SMSL A300
(see [../context.md](../context.md)). Results of the first run (2026-11-17/18): [findings/2026-11-17-setup-checks.md](../../findings/2026-11-17-setup-checks.md).

Work top to bottom. Don't skip the "no speakers yet" phase: it lets you learn REW without any risk to your ears or the speakers.

---

## 0. What "calibrated" actually means (read once)

There are **two separate kinds of calibration**. People mix them up all the time.

| | What it fixes | How | Needed for the EQ? |
| --- | --- | --- | --- |
| **Frequency calibration** (your cal file) | The mic isn't perfectly flat. The file says by how many dB it's off at each frequency, so REW can subtract that. | Load the file in REW. Done. | **Yes** |
| **Level (SPL) calibration** | REW only sees "digital level" (dBFS). To show real dB SPL, it has to learn how many dBFS = how many dB SPL. | Play a signal, compare with an SPL meter (or a calibrator), enter the value in REW. | **No, but nice.** The EQ only needs the *shape* of the curve. Absolute SPL matters for "how loud is it" and for comparing sessions. |

Important consequences:

- The cal file does **not** depend on any knob. It's always right as long as it's the file for *your* mic (serial number).
- The SPL calibration is only valid for **one fixed gain knob position**. Once you've calibrated, **don't touch the mic gain knob** again for the session. If you do, redo the SPL calibration.
- The gain knob doesn't change the frequency response, only the level. Too low = noisy; too high = clipping. Anything in between is fine.

---

## 1. Shopping / gathering list

- [x] Mic stand with a boom (the mic must stand still, at ear height, without your hand on it)
- [x] XLR cable (female → male) for the mic
- [x] 2× TRS–TRS (6.3 mm stereo jack, balanced) cables: interface line outs → DSP inputs 3/4.
      The UMC404HD outputs are 6.3 mm TRS jacks, not XLR, so no XLR adapters are needed.
- [x] 1× short TRS–TRS cable for the loopback (interface out → interface in)
- [x] 1× extra TRS–TRS cable for the later electrical DSP check (DSP out → interface in 3)
- [ ] 2× TRS → RCA cables for **DSP out 1/2 → amp** (tip = signal, sleeve = ground, ring **not connected**). Needed for every measurement through the DSP, and for normal use afterwards.
      **Status:** temporarily running on *the sssnake 1820* adapters (RCA female → 6.3 mm **TS** male). TS shorts the DSP's cold output to ground: replace them.
      Easy fix: a **6.3 mm TRS (stereo) male → 2× RCA** Y-cable/adapter per channel, and use only the **tip / left (white)** RCA; the ring RCA stays unused = ring not connected.
- [x] A **Windows** PC or VM (with USB passthrough) for the t.racks software: needed to load the flat preset and check the routing.
- [x] Tape measure, painter's tape (to mark mic positions on the floor/sofa), pen + paper
- [x] Optional: an SPL meter (cheap one is OK, set to **C-weighting, slow**) for level calibration.
      A phone app is a rough fallback (±3 dB or worse).
      **Status:** no meter. Using the iPhone with the free **NIOSH SLM** app (set to C-weighting / LCS, slow).
      iPhones aren't calibrated one by one, but their mics are very consistent and NIOSH tuned the app for each model, so expect roughly ±2 dB.
      That's fine for Phase D (75–80 dB SPL target) and for Phase E. Don't use the iOS/Watch "Noise" feature: it's A-weighted and only shows rough values.
      Take the case off, hold the phone at the mic capsule with its bottom mic pointing up, and keep your body out of the way.
- [x] Hearing protection nearby (in case something goes wrong at high level)

## 2. Check the cal file

- [x] Seller files (originals, leave untouched) in `reference/mic-cal/vendor-original/`; converted REW copies `reference/mic-cal/MM-1C_0deg.txt` and `MM-1C_90deg.txt`.
      Conversion checks, what the curves say, sensitivity: [setup checks, mic cal files](../../findings/2026-11-17-setup-checks.md#mic-cal-files).
- [ ] Remember the rule:
  - **90° file:** mic points straight **up at the ceiling** (used for room measurements at the seat, positions, corners, DJ spot).
  - **0° file:** mic points straight **at the speaker** (used for close-up woofer/port measurements).

## 3. Install software (Mac)

- [x] Download **REW** from roomeqwizard.com (macOS version, includes Java). Install, start it once.
- [x] The UMC404HD is "class compliant" on macOS: **no driver needed**. Plug it in via USB (directly into the Mac, not a cheap hub).

## 4. macOS settings (important, easy to forget)

Verified 2026-11-17: UMC404HD 192k shows 4 in / 4 out at 48 000 Hz. System output and alert sounds go to the MacBook Pro Speakers.

- [x] **System Settings → Sound → Output:** set to the **Mac's own speakers / headphones**, NOT the UMC404HD.
      Otherwise every notification ping, YouTube video or system sound goes through the amp at full digital level.
- [x] **System Settings → Sound → Input:** doesn't matter, REW picks its own device.
- [x] Turn off "Play sound on startup" / alert sounds, or mute them, for the measuring session.
- [x] Open **Audio MIDI Setup** (Applications → Utilities):
  - [x] Select **UMC404HD**.
  - [x] **Input tab:** Format = **48 000 Hz**, 4 ch, 24-bit (or 32-bit float).
  - [x] **Output tab:** Format = **48 000 Hz**, 4 ch.
  - [x] Output volume sliders (if shown): all at **max / 0 dB**. Volume is controlled later in REW and on the amp, not here.
  - [x] Input volume sliders (if shown): at max / 0 dB. The real input gain is the knob on the interface.
- [x] Close other audio apps (Music, Spotify, browser tabs with audio, DAWs). They can lock the sample rate.
- [x] Turn off Wi-Fi/Bluetooth audio stuff that might grab the device. Don't let the Mac sleep during the session.

## 5. Interface settings (UMC404HD)

Labels may differ slightly; go by what's printed on your unit.

**Before plugging anything in:** all gain knobs fully **left (minimum)**, MAIN and PHONES knobs fully left.

- [x] **Mic on input 1** (XLR into the combo jack).
  - [x] PAD on input 1: **off**
  - [x] LINE/INST on input 1: **off / not pressed** (XLR uses the mic preamp)
- [x] **+48 V phantom power: ON.** The MM-1C is an electret mic and needs it. On the UMC404HD one +48 V switch powers all four inputs at once. That's fine for the loopback and the DSP check: phantom power is only on the **XLR pins** of the combo jacks, not on the 6.3 mm jack contacts, so a TRS plug never sees it. Just never connect a line source (DSP, mixer) to the interface with an **XLR** cable while +48 V is on.
      Switch it on **only after** the mic is plugged in and with gain at minimum. Wait ~10 s after switching on.
- [x] **MIX / direct-monitor knob: fully to PLAYBACK.**
      If it's toward INPUT, the mic and loopback signal are sent straight back out to the outputs. That causes feedback through the speakers and wrong measurements.
- [x] **Output assignment.** Plan for this measuring setup (wired 2026-11-17):

| Interface | Goes to | Purpose |
| --- | --- | --- |
| In 1 (XLR) | MM-1C mic | measurement |
| In 2 (jack, line) | Out 3 (loopback cable) | timing reference |
| In 3 (jack, line) | (later) DSP output | electrical DSP check |
| Out 1 | DSP in 1 | left speaker |
| Out 2 | DSP in 2 | right speaker |
| Out 3 | In 2 | loopback |

  Note: the loopback uses **Out 3** (Out 1/2 feed the DSP).
- [ ] Use the rear **line outputs 1–4** for this (Out 3 loopback: done). Check whether the MAIN knob affects them; ideally the speaker level is fixed and not affected by an easily bumped knob.
- [x] In 2 (loopback): LINE (not INST, button not pressed), gain at minimum. If it clips even at minimum gain, press PAD.

## 6. REW basic settings

Done 2026-11-17 (REW on macOS, Java driver):

- [x] **Preferences → Soundcard:** output device **UMC404HD 192k**, port "SPEAKER"; input device **UMC404HD 192k**, port "MICROPHONE (In 1)". 48 kHz.
      Channels are chosen in the small drop-downs right of the port names.
      Outputs were named L/R/C/LFE: **Set Output Channel Mapping… → Use HW channel as name** renamed them 1–4.
- [x] Input channel **1** (mic), output channel **1** (L) or **2** (R).
- [x] **Loopback input 2**, **Timing reference output 3** (both in the Soundcard tab).
      There is no "Use loopback as timing reference" box in Analysis in this REW version: pick **Timing reference = Loopback** in the **Measure dialog**.
- [x] **Cal files:** mic cal = `reference/mic-cal/MM-1C_90deg.txt` (switch to `reference/mic-cal/MM-1C_0deg.txt` for close-up woofer/port).
- [ ] **Measure dialog:** 10 Hz – 24 kHz, 512k, level **−24 dBFS** (the last measurement used −12 dBFS, that was the loopback test).

## 7. Phase A: dry run, NO speakers (learn REW safely)

Goal: learn how REW measures, and check the interface, without anything that can go loud.

- [x] Amp **off**. Interface outs 1/2 **not** connected to the DSP yet.
- [x] Connect only the loopback cable (Out 3 → In 2).
- [x] Temporarily set REW input channel to **2** (the loopback), output to **Out 3**, untick the timing reference.
- [x] Press **Measure → Check levels**. The loopback input should show something around −12 dBFS. Adjust the In 2 gain knob (or PAD) until it does, and never above −3 dBFS.
- [x] Do a measurement. Result should be a **flat line** from ~10 Hz to ~20 kHz. Congratulations, that's your first measurement.
- [ ] Optional: **Preferences → Soundcard → "Make cal file from loopback"**. This removes the interface's own small deviations. The UMC is close to flat, so this is a nice-to-have.
- [x] Set REW back: input **1** (mic), output **1**, loopback input 2 / timing ref output 3.

## 8. Phase B: check the mic works

- [x] Open REW's **RTA** window (no signal playing).
- [x] Slowly turn input 1 gain up to about the middle. Talk, clap: the meter should react. No reaction → check the +48 V switch and the cable.
- [x] **Noise floor:** with the room quiet, the input level should be very low (roughly −80 dBFS or below in the bass). Note what you see; this is your noise floor.
- [x] Listen/look for hum: spikes at 50 Hz, 100 Hz, 150 Hz… in the RTA with nothing playing = a hum problem. Note it down for now.
      Hum from ground loops can only show up once the DSP/amp are connected, so **re-check the RTA with the chain on but silent in Phase C.**

## 9. Phase C: connect the playback chain, quietly

Do this in this order, every time.

- [x] **Amp OFF** while plugging/unplugging anything.
- [x] DSP flat (2026-11-17): routing A→1, B→2, C→3, D→4; all faders 0 dB; PEQ bypassed; HPF/LPF off; gate + compressor off; delay 0; mute and polarity (Ø) off. No separate limiter in the software (use the compressor at a high ratio later).
- [x] Save this state as DSP preset **"FLAT"**.
- [x] Amp: EQ modes and 50 Hz high-pass **OFF**, input = RCA (checked 2026-11-17).
- [x] Interface **Out 1 → DSP in 1**, **Out 2 → DSP in 2** (TRS–TRS). DSP out 1/2 → amp L/R (RCA). Wired 2026-11-17.
      (Plan said in 3/4; in 1/2 works the same because the EQ sits on the outputs. Keep the DSP *input* channels 1/2 flat.)
- [x] Check the DSP routing: in 1 → out 1 (L), in 2 → out 2 (R), nothing else routed to out 1/2. (2026-11-17: routing 1→1…4→4, all EQ bypassed, all in/out gains 0 dB, factory defaults.)
- [x] Amp volume: **all the way down**. Then switch on: interface → DSP → **amp last**.
      (Switching off: amp **first**.)
- [x] Hum check: REW RTA (averaging 8–16), nothing playing, amp on at the volume you'll use. Compare with the Phase B quiet curve; new spikes at 50/100/150 Hz = ground loop.

## 10. Phase D: set the levels (the gain staging)

This is the part that answers "what level where". Work from the source forward.

1. **REW output level:** use **−24 dBFS** for the pink noise *and* the sweeps, and keep it fixed. The amp volume sets the loudness. (Don't raise REW to −12 dBFS after setting the amp: that would be +12 dB louder at the seat. The A300 is very sensitive, so a low source level is right here.)
2. **Amp volume:** slowly up while REW plays pink noise (Generator → Pink noise, "PN" periodic) on Out 1 at the REW level above.
3. Put the mic at the **main seat** (head position, 1.2 m from the wall, ear height ≈ 1.1–1.2 m when seated), pointing **up**.
4. Turn the amp up until the noise is about **75–80 dB SPL** at the seat (SPL meter, C-weighted, slow). Without a meter: clearly loud, like a loud TV conversation, but not painful. Not more.
5. **Mic gain:** with the pink noise playing, set input 1 gain so REW's input meter peaks at around **−12 dBFS** (Measure → Check levels shows this).
   - Peaks above about −6 dBFS: turn gain down.
   - Below about −30 dBFS: turn gain up (or play slightly louder).
6. **From now on: don't touch the mic gain or the amp volume** for the whole session. Write the knob positions down (take a photo).
7. Check the other speaker (Out 2) gives a similar level at the seat with the same settings.

## 11. Phase E: SPL calibration (optional, after levels are fixed)

- [x] SPL meter at the mic position, as close as possible to the mic capsule, same height.
- [x] REW: **SPL meter window → Calibrate**. Follow the dialog: REW plays pink noise; type in what your SPL meter shows (C-weighted).
- [x] Done. REW's dB numbers are now real dB SPL, valid while the gain knob stays where it is.
- [ ] No SPL meter? Skip this. All the EQ work still works, the curves will just be shifted up or down.

## 12. Phase F: first real test measurement

- [x] Room quiet: windows closed, fridge/fans/dishwasher off if possible, phone on silent, you sitting still (or out of the room).
- [x] Measure **L only** at the main seat. Then **R only**.
- [x] Sanity checks (see [measurement-sets.md](measurement-sets.md), step 1):
  - [x] Timing reference works: the peak sits at the acoustic delay (not t = 0); L/R arrivals within 0.2 ms, or add delay.
  - [x] Same polarity: L and R impulses have the main spike in the same direction.
  - [x] Levels similar from 1 to 8 kHz.
  - [x] Curves plausible: treble falls gently; bass peaks/dips expected.
  - [x] No clipping.
- [ ] If something's off: compare with the troubleshooting table below before measuring more.

Once this works, you are ready to measure: [measurement-sets.md](measurement-sets.md), and the session plan in [plans/](../plans/).


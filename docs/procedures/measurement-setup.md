# Measurement prep: step-by-step checklist

For: Omnitronic MM-1C + Behringer UMC404HD + macOS + REW, measuring through the t.racks DSP and SMSL A300
(see [room-acoustics-context.md](room-acoustics-context.md)).

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
      The UMC404HD outputs are 6.3 mm TRS jacks, not XLR, so the "XLR to TRS" in the context file isn't needed here.
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

- [x] Seller files are in `MM1CBP_allein_Xd/` (originals, leave untouched): `MM1CBP_allein_00d.cal`, `MM1CBP_allein_90d.cal`,
      a plot (`MM1CBP_allein_Xd.gif`) and `Test1.mdat` (the seller's REW test measurements from Feb 2024, not needed).
- [x] Converted copies for REW: **`cal/MM-1C_0deg.txt`** and **`cal/MM-1C_90deg.txt`** (frequency + dB only, UTF-8, comment lines start with `*`).
      Checked: 134 points, 10 Hz to 21.1 kHz, frequencies increasing, 0 dB at 1 kHz. The original phase column was all zeros, so it was dropped.
- [x] What the curves say: flat from ~60 Hz to ~2 kHz. Below that the mic rolls off (−3.5 dB at 20 Hz, −11 dB at 10 Hz). REW corrects for this, so bass readings are right with the file loaded and too low without it.
      Above 2 kHz: 0° rises to +5.4 dB around 10 kHz, 90° stays within about +2.5/−5.6 dB.
- [x] Sensitivity at 1 kHz: **3.72 mV/Pa (0°)**, **3.65 mV/Pa (90°)**. Not needed in REW, because the UMC gain knob has no scale, so do the SPL calibration with the iPhone instead (Phase E).
- [x] Serial number: not needed. There is only one mic and the files came with it from the seller.
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
- [x] **Cal files:** mic cal = `cal/MM-1C_90deg.txt` (switch to `cal/MM-1C_0deg.txt` for close-up woofer/port).
- [ ] **Measure dialog:** 10 Hz – 24 kHz, 512k, level **−24 dBFS** (the last measurement used −12 dBFS, that was the loopback test).

## 7. Phase A: dry run, NO speakers (learn REW safely)

Goal: learn how REW measures, and check the interface, without anything that can go loud.

- [x] Amp **off**. Interface outs 1/2 **not** connected to the DSP yet.
- [x] Connect only the loopback cable (Out 3 → In 2).
- [x] Temporarily set REW input channel to **2** (the loopback), output to **Out 3**, untick the timing reference.
- [x] Press **Measure → Check levels**. The loopback input should show something around −12 dBFS. Adjust the In 2 gain knob (or PAD) until it does, and never above −3 dBFS.
- [x] Do a measurement. Result should be a **flat line** from ~10 Hz to ~20 kHz. Congratulations, that's your first measurement.
- [ ] Optional: **Preferences → Soundcard → "Make cal file from loopback"**. This removes the interface's own small deviations. The UMC is close to flat, so this is a nice-to-have.
      **Result 2026-11-17:** loopback flat within ~0.2 dB from 20 Hz to 20 kHz, phase within ±10°, headroom 10.8 dB at −12 dBFS sweep, In 2 gain at minimum. Skipped the soundcard cal file (not needed).
- [x] Set REW back: input **1** (mic), output **1**, loopback input 2 / timing ref output 3.

## 8. Phase B: check the mic works

- [x] Open REW's **RTA** window (no signal playing).
- [x] Slowly turn input 1 gain up to about the middle. Talk, clap: the meter should react. No reaction → check the +48 V switch and the cable.
- [x] **Noise floor:** with the room quiet, the input level should be very low (roughly −80 dBFS or below in the bass). Note what you see; this is your noise floor.
- [x] Listen/look for hum: spikes at 50 Hz, 100 Hz, 150 Hz… in the RTA with nothing playing = a hum problem. Note it down for now.
      **Result 2026-11-17** (mic gain ≈ middle, 90° cal loaded, chain not connected): mic reacts to claps; quiet-room peak sample ≈ −55 dBFS; noise rises toward the bass (normal); no obvious 50/100/150 Hz spikes.
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
      **Result 2026-11-17:** amp at normal listening volume, 8 averages: noise floor same as Phase B (56 dB vs 55 dB unweighted, uncalibrated), no new hum spikes; only a small bump near 50 Hz, far below measurement level.

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

**Result 2026-11-17:** pink periodic −24 dBFS on L+R together → iPhone ≈ 80 dB(C) at the seat, REW peak sample −12.3 dBFS, noise floor well below. Amp + mic gain fixed from here (photo!). Single speaker will read ~3–6 dB lower; that's fine.

**L/R check 2026-11-17** (pink −24 dBFS, RTA unweighted, uncalibrated): L 89.9 dB (peak −16.7 dBFS), R 92.2 dB (peak −15.4 dBFS), L+R 94.2 dB (consistent). **R is ~2.3 dB louder**, across the mids/treble more than the bass → check mic is centred (tape-measure capsule → each speaker) and amp balance. Not a blocker: per-channel DSP gain/EQ can match them later.

**After moving R closer to the walls (2026-11-17):** L 89.5 dB(C) REW / 73–74 dB(C) iPhone, peak −17.1 dBFS; R 92.1 dB(C) REW / 75–77 dB(C) iPhone, peak −14.4 dBFS. R still ~2.5 dB louder. After centring the mic: L 89.1 dB(C) REW / 73–74 iPhone, R 91.4 dB(C) REW / 75–76 iPhone → **still ~2.3 dB.** Swap test 1 (DSP outs swapped): out 1 → right speaker 91.4 dB(C), out 2 → left speaker 89.1 dB(C) → louder side stays on the **right**, so interface/DSP/adapters/RCA are fine. Swap test 2 (speaker cables swapped at the amp): amp L → right speaker 91.5 dB(C), amp R → left speaker 89.1 dB(C) → right speaker still louder, so the **amp is fine** too. **Cause: the right speaker itself or the room around it.** To tell apart later: 1 m on-axis sweeps of each speaker (gated) and close-up woofer measurements. Fix either way: DSP output gain per channel. Levels in range, amp + mic gain kept. REW reads ~16 dB too high on both channels (consistent).

## 11. Phase E: SPL calibration (optional, after levels are fixed)

Done 2026-11-18. REW reported input clipping at ~105 dB SPL (≈30 dB headroom at our ~74 dB). iPhone showed 87.6 dB(C) during REW's calibration signal (whether Sub Cal was selected during calibration is unconfirmed; the check below passed anyway).
Check, pink random −24 dBFS, Speaker Cal (500–2000 Hz): REW L 74.6 / R 73.8 dB(C); iPhone C within 1 dB of REW. ✔

- [x] SPL meter at the mic position, as close as possible to the mic capsule, same height.
- [x] REW: **SPL meter window → Calibrate**. Follow the dialog: REW plays pink noise; type in what your SPL meter shows (C-weighted).
- [x] Done. REW's dB numbers are now real dB SPL, valid while the gain knob stays where it is.
- Side finding (calibrated REW, pink random −24 dBFS): Sub Cal 30–80 Hz L 76.2 / R 81.8 dB(C) (an earlier R reading was 77.1, unexplained); Speaker Cal 500–2000 Hz L 74.6 / R 73.8. **R's extra level is in the bass, not the mids.**
- [ ] No SPL meter? Skip this. All the EQ work still works, the curves will just be shifted up or down.

## 12. Phase F: first real test measurement

Done 2026-11-18 (REW measurements 3 = L, 4 = R; sweep 512k, 10 Hz–22.05 kHz, −24 dBFS, loopback timing, 90° cal file).

- [x] Room quiet: windows closed, fridge/fans/dishwasher off if possible, phone on silent, you sitting still (or out of the room).
- [x] Measure **L only** at the main seat. Then **R only**.
- [x] Sanity checks (see "Measurement plan" in the context file):
  - [x] Timing reference works: delay vs loopback L 9.284 ms (3.184 m), R 9.153 ms (3.139 m); difference 0.13 ms, so below the 0.2 ms threshold and no delay needed. (With loopback timing the peak sits at the acoustic delay, not at t = 0.)
  - [x] Same polarity: both show a small spike up (+65 % L / +70 % R) and then the main spike down (−100 %).
  - [x] Levels similar from 1 to 8 kHz (L 72–75, R 72–74 dB). **Bass differs a lot** (see below).
  - [x] Curves plausible: treble falls gently (about 74 dB at 2–8 kHz to 66–68 dB at 20 kHz); big bass peaks/dips.
  - [x] No clipping (peak input before clipping 105 dB SPL).
- Readings (1/6 oct): L: peak ~85 dB @ ~42 Hz, hump ~82 dB @ 90–110 Hz, dips @ ~55 Hz (~71), ~150 Hz, ~390 Hz (~66), steep roll-off below ~35 Hz (30 Hz ~66).
  R: peaks ~89–90 dB @ ~55 Hz and ~87 dB @ ~85 Hz, ~81 dB @ ~125 Hz, 30 Hz ~77, deep dip ~64 dB @ ~190 Hz.
  So R has much more bass from 25 to 90 Hz, with peaks and dips at different frequencies than L: points to room/position.
- R impulse has a small spike at ~−780 ms (~25 dB above the noise floor), outside the window. Probably a distortion product or a noise during the sweep; not checked yet.
- Early reflections visible in both impulses at ~1 ms and ~6 ms after the direct sound.
- [ ] If something's off: compare with the troubleshooting table below before measuring more.

Once this works, you're ready for the full measurement plan in [room-acoustics-context.md](room-acoustics-context.md).

---

## 13. Output limiter (do after the EQ is final)

Goal: a compressor on DSP Out 1/2 (later Out 3) that does nothing at normal volume and only catches overload: DJ sets, a hot mixer, loud parties.
No input gate (nothing audible to gate; this DSP's gate opens only hold + 1 ms after the signal starts, so it would cut off starts after silence).
Why measured: the threshold works on the DSP's output level (after the output gain), and nobody knows yet where the A300 + speakers run out.
Limiter settings start from tracks `docs/protocol.md` §5/§6.4.

**Before you start**
- [ ] EQ chosen and imported (v1 or v2 Harman). v2 cuts less bass, so it reaches the limit sooner: measure with the EQ you'll actually use.
- [ ] **Pick the amp volume position the limiter is for**: the loudest position you'll ever use (or full). Mark it on the knob. The limiter only protects up to that position; turning the amp further up beyond it bypasses the protection.
- [ ] Ear protection on. Neighbours warned / sensible time of day: this part is loud.
- [ ] Wiring as for the acoustic measurements (DSP Out 1/2 → amp), mic at the seat, 90° cal, REW input level checked so the mic doesn't clip (input clips at ~105 dB SPL: lower In 1 gain for this test if needed, and note it).
- [ ] Compressor still off on all outputs (threshold "off").

**Step 1: find the limit (one speaker at a time, L then R)**
- [ ] Amp at the marked position. REW output starts at **−40 dBFS** (not −24).
- [ ] Sweep 20–200 Hz (or full range), then raise the REW level in **3 dB steps** and repeat.
- [ ] After each sweep: look at REW's **Distortion** graph (THD, H2/H3) at 35–100 Hz, and listen.
- [ ] Stop at the first step with: THD above ~10 % at 40–80 Hz, port chuffing/whistling, cone clicking or rattling, or a harsh, clipped sound. Go no further.
- [ ] Note **L_max** = the last *clean* REW level (dBFS), per speaker. The lower of L and R counts.

**Step 2: set the threshold (no dB conversion needed)**
- [ ] Compressor on Out 1 and Out 2, both the same: ratio **Limit**, knee **0–1** (~4–8 dB, soft), attack **~5–10 ms**, release **~300 ms**. Link Out 1/2 if the configurator's link mask allows it, so L and R limit together.
- [ ] Play **full-range pink periodic** (check the generator band radio button: Full range, not Sub Cal) on both speakers at **L_max − 3 dB** and read REW's SPL meter at the seat.
- [ ] Lower the threshold from the top in small steps until the SPL drops **1 dB**. That threshold is the setting. Note it (UI dB and raw).

**Step 3: check**
- [ ] Pink at L_max + 3 dB (short burst): SPL rises at most ~1 dB over step 2, no audible strain.
- [ ] Pink at the usual level (−24 dBFS, everyday amp position): SPL with limiter on = off (no gain reduction in normal use).
- [ ] Music test: a bass-heavy track loud. No pumping (if it pumps: longer release, e.g. 500 ms; if bass distorts during limiting: longer attack).
- [ ] Store in the preset (DJ/party preset at least). Note values + amp knob position here and in HANDOFF.md.
- [ ] Later, with the Sub8 on Out 3: repeat step 1 for the sub alone and give Out 3 its own threshold.

Results:
- (not done yet)

---

## Session checklist (print this, use every time)

- [ ] macOS sound output = Mac speakers, not the UMC
- [ ] Audio MIDI Setup: UMC404HD 48 kHz in/out
- [ ] Amp volume down, amp switched on last
- [ ] DSP flat preset loaded, amp EQ/high-pass off
- [ ] +48 V on, PAD off on in 1, MIX at PLAYBACK
- [ ] REW: in 1 / out 1 or 2, loopback in 2 / out 3, 48 kHz
- [ ] Correct cal file loaded (90° up at seat, 0° for close-up)
- [ ] Mic gain + amp volume = same as the photo from last time (or redo Phase D + E)
- [ ] REW output −24 dBFS (fixed), input peaks ≈ −12 dBFS, ~75–80 dB SPL at the seat
- [ ] Measurements named consistently, e.g. `L_seat_center`, `R_seat_+30cm-left`, `L_corner_R`

## Troubleshooting

| Symptom | Likely cause | Fix |
| --- | --- | --- |
| Mic shows nothing | +48 V off, bad cable, wrong REW input | Check +48 V, try another XLR cable, REW input = 1 |
| Feedback howl / sound doubles | MIX knob toward INPUT | MIX fully to PLAYBACK |
| REW: "clipping" warning | Input gain too high, or REW output too high | Lower mic gain, or lower REW output level (redo SPL cal) |
| Impulse not at t = 0 / jumps between measurements | Timing reference not working | Check loopback cable Out 3 → In 2 and REW ref channels |
| Very noisy curve, ragged bass | Level too low or room noise | More level (up to ~80 dB SPL), quieter room |
| Hum spikes at 50/100/150 Hz | Ground loop in the unbalanced chain | Note it; try a different power socket / same power strip for all gear |
| Sound from the speakers when a notification pops up | macOS output set to the UMC | Change system output to Mac speakers |
| Device missing / wrong sample rate in REW | Another app is using the UMC, or 44.1 kHz set | Quit other audio apps, set 48 kHz in Audio MIDI Setup, restart REW |
| Nothing from the speakers | DSP routing, amp input selection, amp volume | Check DSP in 3/4 → out 1/2, amp on RCA input |

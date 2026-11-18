# Living room acoustics – project context

## Goal

Tame the bass: even, controlled low end at the listening position (head 1.2 m from the wall),
and as little bass energy as reasonably possible leaking out of the room (staircase, rest of the building).
Tools: measurements in REW and per-channel EQ in a 4-ch DSP.
Today: measurements + DSP only. Absorbers maybe later.

Current problems:

- bass is audible in the staircase
- bass is very uneven across the room ("full on or nothing at all")
- worst at the **DJ position**: turntables on a cupboard to the left of L, along the speaker wall (can't be moved)

Why: room modes. Each mode has loud spots and silent spots (nulls).

- The 88 Hz mode across the 3.9 m width has a null ~0.98 m from the speaker wall, roughly where
  a DJ's head is when standing at the cupboard. At the sofa (at the opposite wall) the same mode is at its loudest.
- Other nulls: 44 Hz in the middle of the width (1.95 m); along the 6 m length, 29 Hz at 3 m,
  57 Hz at 1.5/4.5 m, 86 Hz at 1/3/5 m.
- EQ can cut the loud spots everywhere, but **can't fill nulls**. Only more bass sources (subs) or
  absorption make the room more even.
- Risk: the DJ hears little bass at the cupboard, turns it up, and the rest of the room (and the building) gets blasted.

Key idea: what leaks out of the room is the room's mode peaks (the bass that builds up throughout the room), not what
you hear at the seat. Cutting mode peaks reduces energy everywhere, which helps both. Never boost the bass.

## Gear

- Speakers: Bonsai Akustik Ideal SE (floorstanding, 2-way bass reflex), 4–8 Ω, 140 W max
  - Woofer Seas P17 RC-A H468 (170 mm), tweeter Seas K29FD H587 (26 mm)
  - Woofer centre 0.69 m above the floor
  - Bass reflex port on the front (close-up measurement of the port is easy)
  - Placement (moved 2026-11-17): **both** speakers pushed back, front baffle/woofer 0.33 m from the rear (speaker) wall.
    R speaker also moved farther from the right side wall, now 0.43 m. L side distance unchanged (value still to note), as are L–R spacing and seat distance.
  - **No subwoofer.** The mains cover the whole range, so the port tuning sets the useful low end.
  - 2026-11-18: a PreSonus Eris Sub8 is available as an occasional add-on (not connected yet). Plan: [sub-and-house-curve-notes.md](sub-and-house-curve-notes.md).
- Sources (normal use):
  1. TV: unbalanced analog output only
  2. Pioneer DJ mixer: has balanced XLR and unbalanced RCA master outputs. Currently RCA straight into the amp (bypassing the DSP). Keeps using RCA (only ~3 m cable run, fine unbalanced)
- For measuring: the balanced audio interface (see Setup)
- Amp: SMSL A300 (class D, plenty of headroom)
  - Inputs RCA (unbalanced), Bluetooth, USB; no balanced input
  - Very sensitive input: 280 mV for full power
  - Has its own EQ modes and a 50 Hz high-pass mode (for 2.1) → keep both OFF, the DSP does everything

## Signal chain

- **Important: every source must go through the DSP.** Otherwise it bypasses the EQ and the limiter.
  DJ music is probably the most bass-heavy source, so the mixer must not go straight into the amp anymore.
- **Normal use:**
  - TV analog out → DSP inputs 1/2 (unbalanced)
  - DJ mixer RCA master out → DSP inputs 3/4 (unbalanced)
  - DSP outputs 1/2 → A300 RCA in → speakers
  - Selecting the source: either two DSP presets (TV / mixer), or route both input pairs summed to the outputs
    so whichever plays is heard. The DSP sums with no adjustable mix, so check the levels match
    and an idle source doesn't add noise.
- **Measuring:** temporarily plug the interface into DSP inputs 3/4 instead of the mixer.
  The EQ sits on the outputs, so every source gets the same EQ.
- **Cables:**
  - TV RCA → DSP: RCA to TS (mono) jack. Balanced inputs accept unbalanced signals.
  - DJ mixer RCA → DSP: RCA to TS (mono) jack, ~3 m, same as the TV. Keep the master level moderate: DSP inputs clip at ~+9.5 dBu
    and a DJ mixer master can go much hotter. Keep the mixer's master meter out of the red / well below max.
  - DSP → amp: TRS to RCA, tip = signal, sleeve = ground, ring (cold) **not connected**.
    Don't plug TS jacks into the DSP's balanced outputs; that shorts the cold side.
  - Interface → DSP: TRS to TRS (balanced). The UMC404HD outputs are 6.3 mm TRS jacks, not XLR. Out 1 → DSP in 3 (L), Out 2 → DSP in 4 (R).
- **Gain staging:** the amp is very sensitive.
  - Turn the A300 volume down to a fixed position where max TV volume ≈ the loudest level you'd ever want.
  - Use the DSP output gain for fine level matching.
  - If it hisses, lower the amp gain and raise the signal earlier in the chain.
  - Watch for hum (all-unbalanced chain, DSP on a wall-wart). Check the noise floor in REW with no signal playing.
- **TV settings:** turn off all TV sound processing (bass boost, clear voice, virtual surround, auto volume, TV EQ).
  Choose a fixed or variable analog out and stay with it.
- **Level safety net:** set the DSP output limiter so the system can't go louder than a sensible maximum we pick ourselves,
  regardless of TV or amp volume.
- 4-ch XLR audio interface, calibrated measurement mics (XLR + USB), REW
- DSP: the t.racks DSP 4x4 Mini
  - 4 in / 4 out, balanced 6.3 mm TRS jacks, 48 kHz
  - Windows-only software over USB, settings stored on the unit (30 presets)
  - Per output: **7 PEQ bands** plus separate HP/LP filters (Butterworth / Linkwitz-Riley / Bessel, 6–24 dB/oct)
  - Delay, gate/compressor/limiter, routing matrix
  - Known quirks from user reviews:
    - inputs clip at ~+9.5 dBu, not the stated +12 dBu
    - clip LEDs unreliable
    - delay shown in the software is ~9% off (software assumes 44.1 kHz)

## Room

- 6.0 m × 3.9 m × 2.8 m (L × W × H)
- Speakers on a 6 m wall, firing across the 3.9 m width toward the sofa on the opposite wall
- L: membrane 0.45 m from the wall behind it, exactly 3.0 m from the left wall (and 3.0 m from the right wall, so centred on the 6 m wall)
- R: membrane 0.45 m from the wall behind it, 0.45 m from the right wall
- Speakers can move only a few cm (walkway). Toed in: stereo triangle to the middle of the sofa
- Sofa: fabric, 60 cm backrest, 5–10 cm from the wall. Middle seat ~4.1 m from the left wall
  - Head ~30–50 cm from the wall behind (to verify)
- Existing treatment: large sofa, shelf, lots of molton flat on the walls (absorbs highs only)
- No bass traps (no space)

## Predicted problems

Axial modes in Hz (c = 343 m/s):

| Room dimension | Modes (Hz) |
| --- | --- |
| 3.9 m (speakers → seat) | 44, 88, 132, 176, 220 |
| 6 m (along the speaker wall) | 29, 57, 86, 114, 143, 172 |
| 2.8 m (height) | 61, 122, 184, 245 |

- **86–88 Hz:** two modes stack and the seat is near the loudest point of both. Likely the main boom.
- **44 Hz:** strong at the seat (sofa against the wall).
- **57 / 29 Hz:** excited mainly by R (near the side wall).
- **~170–190 Hz:** messy region. Modes at 172/176/184 Hz plus the speaker/wall cancellation dip.
- **Speaker/wall cancellation (SBIR):** 343 / (4 × 0.45) ≈ 190 Hz dip.
  - R is deeper because its rear and side wall distances are equal.
  - Fix: unequal R distances (e.g. 40/50 cm) or an absorber behind the speakers.
- **Floor cancellation dip:** 343 / (4 × 0.69) ≈ 124 Hz, close to the 122 Hz height mode.
  Expect an uneven ~120–130 Hz region. Same for L and R.
- **Wall behind the head:** head-to-wall distance varies from 0.4 m (lying back) to 1.2 m (sitting at the front edge).
  The dip moves with posture: 0.4 m → ~215 Hz, 0.7 m → ~120 Hz, 1.2 m → ~70 Hz.
  It moves around, so it can't be EQ'd. The position average smears it out.
- **Bass depends on posture:** near the wall, 44/88 Hz are loudest. At 1.2 m from the wall they're clearly weaker.
  Leaning back = more boom.
- **Seat at the wall:** every mode along the 3.9 m axis is at its loudest there, so bass is strong overall.
- **Transition to reflection-dominated sound:** ~150–200 Hz. Use narrow EQ only below that.
- **L vs. R:** they will measure differently, so EQ each channel separately.

## Setup

- XLR mic on In 1. Loopback cable Out 3 → In 2 (not Out 2: Out 1/2 feed DSP in 3/4).
  - REW: Preferences → Soundcard → "Use loopback as timing reference", ref. output = Out 3, ref. input = In 2.
- Load the mic cal file. Use the 90° file with the mic pointing at the ceiling at the seat.
  - Use the 0° file for close-up speaker measurements.
- Optional: soundcard cal via the loopback.
- 48 kHz everywhere, ASIO driver on Windows.
- Input peaks ~−12 dBFS, ~75–80 dB SPL at the seat.
- Sweep 10 Hz–24 kHz, 512k length.
- DSP flat: no EQ, no delay, all gains equal.
- DSP input clipping: keep the interface output level moderate. DSP inputs clip at ~+9.5 dBu and the clip LEDs aren't reliable.
  Check with a loopback measurement through the DSP (see the EQ section).
- Measure through the same DSP outputs and amp as normal use (interface temporarily on DSP in 3/4); see Signal chain.
- Final check: play a sweep from the TV (e.g. a REW sweep file on a USB stick) to make sure no TV processing is left on.

## Measurement plan

1. Sanity checks: loopback impulse at t = 0, same polarity L/R, same levels.
2. L and R separately at the main seat: middle of the sofa, ear height, **head 1.2 m from the wall**.
3. 6–8 more positions per speaker around it:
   - ±30 cm left/right
   - ±20 cm forward/back
   - ±10 cm up/down
   Make an RMS average per speaker. This is the basis for the EQ.
3b. **Corner measurement ("what the room really does"):** mic in a floor–wall corner
    (e.g. the corner next to R and one other), L and R separately.
    A floor corner is where all modes are loudest, so this shows the room's real bass energy.
    Use it to find the modes to cut that are weak at the seat but strong in the room.
3c. **DJ position:** 4–6 measurements at standing ear height (~1.6 m) in front of the turntables, L and R separately.
    Shows what the DJ hears and which frequencies are missing there.
3d. Optional: walk through the room with the RTA (pink PN, slow sweep of the mic) to see how uneven the bass is.
4. L+R together (mono signal).
5. Close-up of the woofer and the port (1–2 cm): speaker-only bass response and port tuning frequency.
6. Waterfall, spectrogram, RT60 (T20/T30). Target ~0.3–0.5 s, even across frequency.
7. Optional:
   - R at 40/50 cm instead of 45/45.
   - Duvet held behind the head to test whether an absorber is worth it.
   - REW Room Simulator with the data above, to compare with the measurements.

## Interpretation rules

- Below ~300 Hz: use 1/24 oct smoothing or none. Above: Var or 1/6 oct.
- EQ peaks that stay at the same frequency at all positions and ring in the waterfall.
- **Never boost dips.** If a dip moves or changes depth when the mic moves 30 cm, it's a cancellation.
- Check excess group delay: where it's flat, EQ works.
- "Estimate IR delay": add delay only if L/R arrivals differ by more than ~0.2 ms.

## EQ in REW

- Equalizer type: **Generic** (the t.racks isn't in REW's list). Enter frequency, gain and Q by hand.
- **Max 7 PEQ filters per channel.** The HP filter is separate, so it doesn't use a band.
  If REW proposes more than 7: keep the 7 biggest, delete the rest, then re-run "Optimise gains".
- **Check the DSP electrically before trusting the filters.** Connect a DSP output directly to a spare
  interface input (no amp, no mic) and measure in REW. Compare with REW's predicted filter response.
  This catches different Q conventions, typos and clipping.
- Target: **flat in the bass (no bass boost)**, gentle downward tilt toward 20 kHz.
  If needed, raise the bass by 1–2 dB at most, and only if the corner measurement doesn't rise noticeably.
- Match range 20–250 Hz.
- **Cuts only (max boost 0 dB)**, flatness 1 dB, Q 3–8 is fine for clear modes.
- Run "Match response to target" separately on the L and R seat averages (1.2 m position).
- Then compare with the corner measurements. Add extra cuts for any mode clearly sticking out there
  (expected: 44, 57 (mostly R), 86–88 Hz), even if it isn't loud at the seat.
- Add a DSP high-pass slightly below the port tuning frequency. To reduce leakage, it can sit higher
  (e.g. 40–50 Hz, 24 dB/oct) and cut the deepest bass. Use the DSP's dedicated HP filter (Linkwitz-Riley or Butterworth, 24 dB/oct).
- Delay: probably not needed (stereo triangle). If used, verify by measurement; the software's value is ~9% off.
- Save the result as a DSP preset and keep the flat preset for re-measuring.
- Export the filters, enter them in the DSP, re-measure the seat positions and the corner, compare before/after.
- Re-measure the same positions with the EQ on, compare before/after, then listen.

## DJ position

- Don't EQ for the DJ position by boosting. It's probably in nulls, and boosts would only blast the rest of the room.
- Better: monitor the bass on headphones, or put a small booth monitor near the turntables
  (mixer booth out → small active speaker, or DSP outputs 3/4 + a small amp).
  Close up, it gives the bass cue at low level.
- Optional: a separate DSP preset for DJ sessions with a stricter limiter.

## Bass leaking out: beyond the EQ

- Staircase: the door is usually the weakest point. A solid door with seals around the frame and at the bottom helps a lot.
- Sound also travels through the floor into the building. Floorstanding speakers on a wooden or
  floating floor pass vibration on directly.
  Try decoupling: a heavy slab (stone/concrete) on soft pads, or dedicated isolation feet.
  Spikes couple more, not less.
- Overall level: the low end decides it. An EQ that removes the mode peaks often lets you play at
  the same perceived loudness with less bass energy.

## Later (not today)

- ~10 cm porous absorber on the wall above the sofa, at head height.
- 10–15 cm absorbers behind the speakers (better if the speakers move closer to the wall).
- Molton re-hung with a 10–20 cm air gap.
- Optional 1–2 subwoofers on the free DSP channels (smooth out modes below ~100 Hz).

## Still unknown

- Port tuning frequency (find it in the close-up measurement: woofer notch = port peak)

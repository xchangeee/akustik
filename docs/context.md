# Living room acoustics: project context

Stable facts: goal, gear, room, the predicted problems. What is wired/configured right now: [current-setup.md](current-setup.md). Why things were decided: [decisions.md](decisions.md).

## Goal

Tame the bass: even, controlled low end at the listening position,
and as little bass energy as reasonably possible leaking out of the room (staircase, rest of the building).
Tools: measurements in REW and per-channel EQ in a 4-ch DSP. Absorbers maybe later.

Problems at the start:

- bass is audible in the staircase; neighbours above hear loud sessions (user 2026-11-21)
- bass is very uneven across the room ("full on or nothing at all")
- worst at the **DJ position**: turntables on a cupboard to the left of L, along the speaker wall (can't be moved)

Why: room modes. Each mode has loud spots and silent spots (nulls).

- EQ can cut the loud spots everywhere, but **can't fill nulls**. Only more bass sources (subs) or
  absorption make the room more even.
- Risk: the DJ hears little bass at the cupboard, turns it up, and the rest of the room (and the building) gets blasted.

Key idea: what leaks out of the room is the room's mode peaks (the bass that builds up throughout the room), not what
you hear at the seat. Cutting mode peaks reduces energy everywhere, which helps both. Never boost the bass to fill dips.

## Gear

- Speakers: Bonsai Akustik Ideal SE (floorstanding, 2-way bass reflex), 4–8 Ω, 140 W max
  - Woofer Seas P17 RC-A H468 (170 mm), tweeter Seas K29FD H587 (26 mm)
  - Woofer centre 0.69 m above the floor
  - Bass reflex port on the front; **port tuning ≈ 35 Hz** (measured 2026-11-18)
  - **Mains run full range** (no high-pass), so with the sub off the port tuning sets the useful low end.
    A PreSonus Eris Sub8 will be added as an overlay: wired in permanently (once set up), switched on only occasionally. Bass reflex with a front port (user, 2026-11-22). Not connected yet: [plans/sub8-overlay.md](plans/sub8-overlay.md).
- Amp: SMSL A300 (class D, plenty of headroom)
  - Inputs RCA (unbalanced), Bluetooth, USB; no balanced input
  - Very sensitive input: 280 mV for full power
  - Has its own EQ modes and a 50 Hz high-pass mode (for 2.1) → keep both OFF, the DSP does everything
- DSP: t.racks DSP 4x4 Mini
  - 4 in / 4 out, balanced 6.3 mm TRS jacks, 48 kHz; settings stored on the unit (30 presets)
  - Vendor software is Windows-only; configured instead with the user's own configurator in `~/WPlay/tracks`
    (WebHID, reimplementation from the reverse-engineered protocol; parameter grids in `tracks/docs/protocol.md`)
  - Per output: **7 PEQ bands** plus separate HP/LP filters (Butterworth / Linkwitz-Riley / Bessel, 6–24 dB/oct)
  - Delay, gate/compressor, routing matrix (no separate limiter: use the compressor)
  - Known quirks from user reviews:
    - inputs clip at ~+9.5 dBu, not the stated +12 dBu
    - clip LEDs unreliable
- Sources (normal use):
  1. TV: unbalanced analog output only (3.5 mm TRS stereo jack)
  2. Pioneer DJ mixer: balanced XLR and unbalanced RCA master outputs. Uses RCA (only ~3 m cable run, fine unbalanced); wiring: [current-setup.md](current-setup.md#two-modes)
- Measuring: Behringer UMC404HD interface, Omnitronic MM-1C measurement mic (XLR), REW on macOS

## Signal chain (normal use, target)

- **Every source must go through the DSP.** Otherwise it bypasses the EQ and the limiter.
  DJ music is probably the most bass-heavy source, so the mixer must not go straight into the amp anymore.
- TV analog out → DSP inputs 1/2 (unbalanced)
- DJ mixer RCA master out → DSP inputs 3/4 (unbalanced)
- DSP outputs 1/2 → A300 RCA in → speakers. The EQ sits on the outputs, so every source gets the same EQ.
- Selecting the source: both input pairs are **routed summed** to the outputs (A+C → Out 1, B+D → Out 2), so whichever
  plays is heard; normally only one plays at a time ([decisions.md](decisions.md)). The DSP sums with no adjustable mix,
  so check the levels match and an idle source doesn't add noise.
- **Cables:**
  - TV → DSP: the TV's analog out is a 3.5 mm TRS stereo jack, so an adapter cable to In A/B. Balanced inputs accept unbalanced signals.
  - DJ mixer RCA → DSP: RCA to TS (mono) jack, ~3 m. Keep the master level moderate: DSP inputs clip at ~+9.5 dBu
    and a DJ mixer master can go much hotter. Keep the mixer's master meter out of the red / well below max.
  - DSP → amp: TRS to RCA, tip = signal, sleeve = ground, ring (cold) **not connected**.
    Don't plug TS jacks into the DSP's balanced outputs; that shorts the cold side.
- **Gain staging:** the amp is very sensitive.
  - Turn the A300 volume down to a fixed position where max TV volume ≈ the loudest level you'd ever want.
  - Use the DSP output gain for fine level matching.
  - If it hisses, lower the amp gain and raise the signal earlier in the chain.
- **TV settings:** turn off all TV sound processing (bass boost, clear voice, virtual surround, auto volume, TV EQ).
  Choose a fixed or variable analog out and stay with it. Done, see [current-setup.md](current-setup.md).
- **Level safety net:** a DSP output limiter so the system can't go louder than a sensible maximum,
  regardless of TV or amp volume: [procedures/output-limiter.md](procedures/output-limiter.md).

## Room

- 6.0 m × 3.9 m × 2.8 m (L × W × H)
- Floor: wooden parquet, probably on concrete (user 2026-11-21: "we think it's a concrete floor"; not confirmed). Below: only a cellar, no flat. Above: neighbours. Speakers on spikes → base plates → felt → parquet.
- Existing treatment: large sofa, shelf, lots of molton flat on the walls (absorbs highs only). No bass traps (no space).

Layout (user's sketch 2026-11-18, positions approximate): [img/room-layout-sketch.png](img/room-layout-sketch.png)

- Speaker wall = the 6 m wall with (left to right) door at the corner, DJ cupboard, L, TV, R. Speakers fire across the 3.9 m width toward the sofa.
- Speakers: L roughly centred on the 6 m wall (~3.0 m from the left wall), R near the right wall. Speakers can move only a few cm (walkway). Toed in: stereo triangle to the middle of the sofa.
  - Since 2026-11-17: **both** front baffles 0.33 m from the speaker wall (was 0.45 m), R 0.43 m from the right side wall. L side distance, L–R spacing and seat distance not measured.
- DJ stand in front of the cupboard: ~1.8 m from the left wall, ~0.75 m from the speaker wall.
- Table on the left, KALLAX in the middle, sofa (fabric, 60 cm backrest) against the back wall on the right.
- Seat ~4.4 m along the speaker wall. **Head position varies:** sitting upright at the front of the sofa (where all seat measurements were made) ~1.2 m in front of the back wall (~2.75 m from the speaker wall); lying back ~0.4 m from the back wall. The EQ is designed for upright; lying back gets more 44/88 Hz.

## Predicted problems (before measuring)

What was actually measured: [findings/2026-11-18-baseline.md](../findings/2026-11-18-baseline.md).

Axial modes in Hz (c = 343 m/s):

| Room dimension | Modes (Hz) |
| --- | --- |
| 3.9 m (speakers → seat) | 44, 88, 132, 176, 220 |
| 6 m (along the speaker wall) | 29, 57, 86, 114, 143, 172 |
| 2.8 m (height) | 61, 122, 184, 245 |

- Nulls: the 88 Hz width mode has a null ~0.98 m from the speaker wall, roughly where a DJ's head is (measured: not there, see baseline). 44 Hz in the middle of the width (1.95 m); along the 6 m length, 29 Hz at 3 m, 57 Hz at 1.5/4.5 m, 86 Hz at 1/3/5 m.
- **86–88 Hz:** two modes stack and the seat is near the loudest point of both. Likely the main boom.
- **44 Hz:** strong at the seat (sofa against the wall).
- **57 / 29 Hz:** excited mainly by R (near the side wall).
- **~170–190 Hz:** messy region. Modes at 172/176/184 Hz plus the speaker/wall cancellation dip.
- **Speaker/wall cancellation (SBIR):** 343 / (4 × 0.45) ≈ 190 Hz dip (at the original 0.45 m).
  - R is deeper when its rear and side wall distances are equal.
  - Fix: unequal R distances or an absorber behind the speakers.
- **Floor cancellation dip:** 343 / (4 × 0.69) ≈ 124 Hz, close to the 122 Hz height mode.
  Expect an uneven ~120–130 Hz region. Same for L and R.
- **Wall behind the head:** head-to-wall distance varies from 0.4 m (lying back) to 1.2 m (sitting at the front edge).
  The dip moves with posture: 0.4 m → ~215 Hz, 0.7 m → ~120 Hz, 1.2 m → ~70 Hz.
  It moves around, so it can't be EQ'd. The position average smears it out.
- **Bass depends on posture:** near the wall, 44/88 Hz are loudest. At 1.2 m from the wall they're clearly weaker.
  Leaning back = more boom.
- **Transition to reflection-dominated sound:** ~150–200 Hz. Use narrow EQ only below that.
- **L vs. R:** they will measure differently, so EQ each channel separately.

## DJ position

- Don't EQ for the DJ position by boosting. Boosts would only blast the rest of the room.
- Better: monitor the bass on headphones, or put a small booth monitor near the turntables
  (mixer booth out → small active speaker, or DSP outputs 3/4 + a small amp).
  Close up, it gives the bass cue at low level.
- Optional: a separate DSP preset for DJ sessions with a stricter limiter.

## Bass leaking out: beyond the EQ

- Staircase: the door is usually the weakest point. A solid door with seals around the frame and at the bottom helps a lot.
- Sound also travels through the floor into the building. Floorstanding speakers on a wooden or
  floating floor pass vibration on directly.
  Try decoupling: a heavy slab (stone/concrete) on soft pads, or dedicated isolation feet.
  Spikes couple more, not less. Plan: [plans/speaker-isolation.md](plans/speaker-isolation.md).
- Overall level: the low end decides it. An EQ that removes the mode peaks often lets you play at
  the same perceived loudness with less bass energy.

## Later

- ~10 cm porous absorber on the wall above the sofa, at head height.
- 10–15 cm absorbers behind the speakers (better if the speakers move closer to the wall).
- Molton re-hung with a 10–20 cm air gap.
- Subwoofer(s) on the free DSP channels: [plans/sub8-overlay.md](plans/sub8-overlay.md).

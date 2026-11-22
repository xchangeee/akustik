# Plan: "boring" bass, house curve, adding the Eris Sub8 (2026-11-18)

After listening to music with EQ v1 for a while, the sound feels a bit "boring": something is missing in the low low end.
A PreSonus Eris Sub8 is available and could be added to the DSP. It draws up to 100 W, so it should only run sometimes, for extra punch.

## Sub8 specs (as given by the user)

- Inputs: 2× balanced 1/4" TRS, 2× unbalanced RCA
- Input gain −30 to +6 dB; polarity switch 0°/180°; low-pass 50–130 Hz (variable); high-pass switch on/off
- Class AB amp, peak SPL 113 dB, S/N > 95 dB(A)
- Protections: RF interference, output-current limiting, over-temperature, turn-on/off transient, subsonic filter, external mains fuse

## 1. Probable main cause: the flat EQ target

EQ v1 targets **flat** (bass at the 300 Hz–3 kHz mid level). Simulated at the seat, L+R is about ±3 dB from 35 to 130 Hz,
−3 dB at 30 Hz and −14 dB at 25 Hz ([eq_design.txt](../../analysis/output/eq_design.txt)).
An in-room response that's flat usually sounds thin and polite. Most listeners prefer a **house curve**: bass rising about
+5…+8 dB from ~100 Hz down to ~30 Hz. Before the EQ the room had +10…+15 dB of boom, so going straight to flat is a big change.

- Fix (no power, no hardware): **EQ v2 with a gently rising target**. Still cut-only, just cutting less. Same script ([analysis/design_eq.py](../../analysis/design_eq.py)), different target. The peaks at 43, 51 and 85–89 Hz still get cut.
- Trade-off: the leakage goal. Cutting less gives back some bass energy in the staircase (rough guess 3–5 dB of the 6–8 dB EQ v1 removed). The user decides how much.
- Starting proposal was about +4 dB at 40 Hz. **Done as EQ v2 with a Harman target (+6 dB low shelf, 105 Hz):** [findings/eq-v2-harman.md](../../findings/eq-v2-harman.md).
- The acoustic re-measurement with EQ v1 on is still open (see [SESSION-LOG.md](../../SESSION-LOG.md)). It also shows whether the narrow −12 dB notches at 42–43 Hz overshoot at some positions, which would thin the low end further.

## 2. What to expect from the Sub8

- From memory of the spec sheet (not verified), the Sub8 reaches about 30 Hz. The mains already reach ~35 Hz (port tuning), and the 29.8 Hz HPF sets the limit. So the sub adds **headroom and level at 25–45 Hz** more than real extra depth.
- It's a **second bass source at a different spot**, so it can partly fill holes EQ can't fix, e.g. the DJ spot's 55–75 Hz L/R cancellation and its 30–35 Hz hole.
- Downside: deep bass is what travels through the building most. With the sub on, the staircase gets more.

## 3. Recommended setup for occasional use: overlay

Keep the mains exactly as they are. The sub only **adds** below ~45–50 Hz.

- **Sub off = today's sound.** No preset switch, and nothing breaks if someone forgets. Sub on adds extra low end on top.
- **Wiring:** DSP Out 3 (TRS) → Sub8 balanced TRS input, one channel only. Balanced to balanced, so no TS-adapter problem.
  Don't use the Sub8's pass-through outputs or its high-pass switch, which (believed, not verified) acts on those outputs. The DSP does all the filtering.
- **DSP Out 3:**
  - Routing: In A + In B summed to Out 3 (later also C + D for the DJ mixer). Watch the summed level for clipping.
  - Low-pass: Linkwitz-Riley 24 at ~45–50 Hz (final value from the simulation).
  - PEQ: its own cut bands for the modes the sub excites from its spot.
  - Delay + polarity: for alignment with the mains in the overlap region.
  - Gain trim.
- **Sub knobs:** low-pass at 130 Hz (max), so the DSP's filter dominates. Its slope is still in the chain, and the measurement captures it.
  Set the gain once and leave it. On/off = the "punch" switch.
- **Placement and alignment from measurement**, same method as the L+R sums: sub-only sweeps at 2–4 possible spots
  (mic at seat, DJ, corners), then choose spot, crossover, delay and polarity in simulation before touching the DSP.
  Avoid a corner unless it clearly measures best: corners excite every mode and increase leakage.

Alternative, not recommended for occasional use: **real 2.1**. Mains high-passed at ~80 Hz, sub does all the bass.
Better evenness and headroom, but it needs two presets, and the bass disappears if the sub is off.

## 4. Power

The 100 W is most likely the maximum rating. Class AB idle draw is probably a few tens of watts (guess). Check with the plug-in power meter (the user has one).
The sub is switched on and off manually at its own power switch (no switched strip or smart plug). Switch it on after the DSP and amp (turn-on transient protection is built in, so the order isn't critical).

## Order of work

1. Acoustic re-measurement with EQ v1 on (pending).
2. EQ v2 with a moderate house curve. Listen first: it may already fix "boring". **Designed 2026-11-18 with a Harman target (+6 dB shelf, 105 Hz), see [findings/eq-v2-harman.md](../../findings/eq-v2-harman.md); imported into slot 3, not listened yet.**
3. Sub as overlay: sub-only sweeps at candidate spots → simulate → configure Out 3.

## Status 2026-11-22: designed, next steps

Spot C measured; Out 3 designed per preset as **v3 = v1 + sub** and **v4 = v2 + sub** (mains unchanged): [findings/2026-11-22-sub-c.md](../../findings/2026-11-22-sub-c.md). Spot A skipped for now.

- [x] ~~User:~~ Done 2026-11-22 by probe `--make-preset` (read back): make **P05 "EQ v3 flat+sub"** = copy of P02, and **P06 "EQ v4 Harm+sub"** = copy of P03. In each, set Out 3 as in the finding's table: routing In A+B+C+D, LPF, polarity, delay, gain; import `eq/v3-flat-sub/Sub.txt` / `eq/v4-harman-sub/Sub.txt` into Out 3's PEQ. Leave Out 1/2 untouched.
- [ ] Listen with the sub on and off, **v3 at amp 50, v4 at amp 45** (the sub is matched there; the amp doesn't move the sub): level, the 28 Hz overshoot, the neighbours. Adjust the level only with Out 3's gain.
- [ ] Maybe: stereo volume control (with remote) between TV and DSP In A/B, so the sub follows the volume and can run at any level. Hiss at a fixed amp 50 is slight (user, 2026-11-22).
- [ ] Measuring check of P05/P06 at the seat (mains + sub together). sweep.py plays one output per sweep, so this needs the sweep on UMC Out 1 and 2 at once (or a mono feed into In A and In B); script change first.
- [ ] Optional: spot A (`subA-*` sets are in the plan JSON), if C turns out unsatisfying.

Later, nice-to-have: **real 2.1** variants (mains high-passed at ~80 Hz, sub takes all the bass) as extra presets, designed the same way from the same data. Needs the sub on, so not for everyday use.

## Open questions for the user

- Where can the sub physically go? 2026-11-20: three candidate spots A/B/C sketched, model screening: [findings/2026-11-20-sub-positions-model.md](../../findings/2026-11-20-sub-positions-model.md). B dropped; measure A and C.
- ~~How much bass rise below 100 Hz to try in v2?~~ Decided: Harman, +6 dB shelf.

# Sub8 candidate positions: modal model screening (2026-11-20)

The user's sketch of 2026-11-20 (given in chat, not in the repo) shows three possible Sub8 spots. This is a **model**, not a measurement: a first screening before the sub-only sweeps in [docs/plans/sub8-overlay.md](../docs/plans/sub8-overlay.md).
Script: [analysis/sub_positions_modes.py](../analysis/sub_positions_modes.py). Output: [sub_positions_modes.txt](../analysis/output/sub_positions_modes.txt), [plot](../analysis/output/sub_positions_modes.png), [validation plot](../analysis/output/sub_positions_validation.png).

## Positions (read off the sketch, ±0.2 m; the sketch isn't to scale, x and y scaled separately)

x = from the left wall along the speaker wall, y = from the speaker wall.

| Spot | Where | x | y |
| --- | --- | --- | --- |
| A | speaker wall, between L and TV | 3.5 | ~0.25 |
| B | open floor in front of the KALLAX | 2.9 | 1.6 |
| C | right side wall, at the sofa's right end (user: ~0.40 m from the right wall because of a heatsink, ~2.50 m from the speaker wall, ~1.50 m from the back wall) | 5.6 | 2.5 |

The sketch puts the seat at ~3.9 m along; [context.md](../docs/context.md#room) says ~4.4 m. User confirmed 4.4 m (2026-11-20); the model uses that.

## Model and validation

Rectangular rigid box 6.0 × 3.9 × 2.8 m, uniform damping from RT60 0.66 s (63 Hz), modes to 400 Hz, flat source, no crossover. No furniture, door or leaks.
Check on the mains: modelled R − L at the seat vs the measured 7-position average, 25–90 Hz: r = 0.61. The 28, 51 and 89 Hz peaks are reproduced within ~3 dB, 57 Hz is underestimated. Good enough to rank positions, not to predict exact levels.

## Results (sub band 25–50 Hz)

Low modes: 28.6 Hz (1,0,0) length, 44.0 Hz (0,1,0) width, 52.4 Hz (1,1,0) tangential (= R's measured 51.5 Hz peak).

| Spot | 28.6 Hz coupling | 44 Hz coupling | Seat level | Seat spread | What it does |
| --- | --- | --- | --- | --- | --- |
| A | 0.27 | 0.98 | 13.4 | 16.1 | like the L main: mostly 44 Hz, which is already the biggest seat peak (+13 dB). Adds little below 40 Hz |
| B | 0.05 | 0.27 | 2.9 | 8.4 | near the nodes of all three low modes: smoothest, but ~10–13 dB less level at the seat than A/C, so the Sub8 runs out of headroom first. Worst seat-to-room ratio (−4.1 dB vs −1.3 for A and C) |
| C | 0.98 | 0.43 | 16.0 | 23.2 | like the R main: drives 28.6 Hz hard (+24 dB at the seat, model), weak 44 Hz, dip ~40 Hz. Delivers the real low end; the 28 Hz peak needs a PEQ cut on Out 3 |

Levels in dB relative to the L main at the seat (80–120 Hz), model only. Spread = max − min in the band.
DJ spot: A peaks at 44 Hz (DJ already +15 there); C adds 28 Hz (DJ measured −7.6 dB at 30 Hz, so C fills that hole); B has a dip at ~37 Hz.
Leakage proxy (room-average level per seat level): A and C about equal, B worst.

## Conclusion

- **C** is the best candidate for the overlay's purpose (adding 25–40 Hz without more 44 Hz), provided a cut at ~28 Hz on Out 3. Its 28 Hz peak also coincides with R's, so the DSP cut has to handle both.
- **A** is the easy spot (next to the mains, simple alignment) but mainly adds 44 Hz, the frequency EQ v1/v2 already cut hardest.
- **B** is the smoothest but needs much more drive for the same level and puts relatively more energy into the room. User 2026-11-20: B could stand there (not directly in the walkway), but agrees it's pointless → dropped.
- To be confirmed by sub-only sweeps (seat + DJ) at A and C.

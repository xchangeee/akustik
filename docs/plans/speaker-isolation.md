# Plan: speakers on isolated concrete slabs (2026-11-21)

Nice-to-have, done last. Goal: **less bass leaking into the building through the floor**.
The in-room sound is handled by the EQ and absorbers, not by this.

Who hears it (user 2026-11-21): no flat below (only a cellar); the **neighbours above** hear loud sessions.
So the floor path only counts as structure-borne sound running through the concrete into walls and up.
The direct path (room pressure pushing on the ceiling) is likely at least as strong and isn't touched by this plan.
Cheap test before buying: see [Check that it worked](#check-that-it-worked).

## Now

Speaker on spikes → base plates → felt → wooden parquet, probably on concrete (user thinks so, 2026-11-21; not confirmed).
Felt is thin and stiff: it probably compresses so little that its resonance sits in the bass, so it does little where the leakage is.

## Decided (user 2026-11-21)

- **One** concrete slab per speaker (not stacked, not two-stage). About 40×40×4–5 cm, ~15–20 kg.
- Elastic layer: **Sylomer** (or a similar PU elastomer), as a few small pads under the slab corners, not a full mat.

Build, top to bottom: speaker on its spikes → slab → 3–4 Sylomer pads → parquet.

## Sizing the Sylomer

A mass on a spring only isolates well above its resonance f0. The port tuning is ≈ 35 Hz, so aim for f0 ≈ 10–15 Hz.
f0 ≈ 15.8 / √(static deflection in mm) Hz → the pads must compress **≈ 1–2.5 mm** under speaker + slab.

1. Weigh one speaker (unknown so far; bathroom scale: you holding it minus you alone). Add the slab's weight.
2. Load per pad = total / number of pads. Pick the Sylomer type whose static load range (N/mm²) fits load ÷ pad area,
   in the middle of its range. Pad area is the tuning knob: smaller pads = more load per area = more compression.
3. Thickness: from the manufacturer's deflection chart, choose a thickness that gives 1–2.5 mm at that load.
4. Check after building: measure the compression (caliper, before/after). Push the speaker top lightly: if it sways,
   the pads are too soft or too small. Keep the pads near the slab corners (tall speakers).

## Side effects

- The woofer rises from 0.69 m by the slab thickness (+5 cm → ~0.74 m); the floor dip moves from ~124 Hz to ~116 Hz.
  Re-measure L/R at the seat afterwards and check the EQ still fits.
- Only the floor path is reduced. Bass through the air (door, walls) is unchanged; door seals: [context.md](../context.md#bass-leaking-out-beyond-the-eq).

## Check that it worked

Same track, same amp volume, listen in the staircase / upstairs, before vs after.

Test before buying (rough): play loud, someone listens upstairs. Then stand the speakers temporarily on something very soft
(thick foam, folded mattress) and repeat. If upstairs barely changes, the floor path isn't the main one and the slabs are not worth it.

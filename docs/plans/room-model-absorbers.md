# Plan: room model from an iPhone scan, then choose absorbers by simulation (2026-11-20)

Goal: a 3D model of the room, fitted to our measurements, to compare absorber types, positions and sizes **before** building anything.

**Order:** after the Sub8 overlay ([sub8-overlay.md](sub8-overlay.md)). Absorbers have to be built, so they come last, and the model should include the sub as a source at its final position. See [decisions.md](../decisions.md).

## 1. Scan (iPhone 14 Pro, LiDAR)

- App built on Apple RoomPlan (e.g. 3D Scanner App, Polycam, Canvas). RoomPlan gives walls, door and windows as planes and furniture as boxes, which is the right level of detail for acoustics. A photo-realistic mesh isn't needed.
- Scan with speakers, sub, sofa and DJ stand in their real positions.
- Export **USDZ or OBJ** into the repo (e.g. `reference/room-scan/`).
- Check against the tape: 6.0 × 3.9 × 2.8 m, speaker distances in [context.md](../context.md#room).
- Needed from the user (the scan can't see it): wall, ceiling and floor construction (drywall absorbs bass, masonry doesn't), window sizes and glazing, door type.

## 2. Model (`analysis/room_model/`)

Two ranges, two methods:

| Range | Method | Answers |
| --- | --- | --- |
| below ~150–200 Hz (modal region) | wave-based, FEM Helmholtz (e.g. scikit-fem) with the speakers (and sub) as point sources | pressure maxima of the 44/88 Hz modes, effect of absorbers at seat, DJ spot and lying-back position |
| above | image-source / ray tracing (e.g. pyroomacoustics) | first-reflection points for broadband panels |

**Calibrate first:** fit the boundary absorption until the model reproduces the baseline measurements (seat + 6 positions, 2 corners, DJ spot: [findings/2026-11-18-baseline.md](../../findings/2026-11-18-baseline.md)) and later the re-measurements with EQ / sub. Only then add absorbers. Expect the ranking of options to be reliable and the absolute numbers off by a few dB.

## 3. Absorber options to compare

- Porous panels (thickness, air gap) at reflection points.
- Corner traps, where any space exists.
- **Tuned membrane / Helmholtz absorbers for 44 and 88 Hz.** No space for deep bass traps ([context.md](../context.md#room)), and porous absorbers need ~λ/4 depth (≈ 2 m at 44 Hz), so thin tuned absorbers at the pressure maxima are the realistic bass option. 44 Hz runs speaker wall ↔ back wall (sofa).
- Evaluate: response at the seat and DJ spot, spread across positions, and how much EQ cut is still needed afterwards.

## 4. After building

Re-measure with the same procedure, compare to the model's prediction, then redo the EQ on top.

## Caveat

The room is close to a plain box, so a simple box model already shows much of the bass behaviour. The scan mainly adds the real door, window, furniture and source positions. It takes ~10 minutes, so it's worth it.

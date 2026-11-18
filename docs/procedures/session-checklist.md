# Measurement session checklist

Use every time before measuring. First-time setup: [measurement-setup.md](measurement-setup.md). What to measure: [measurement-plan.md](measurement-plan.md).

## Checklist

- [ ] macOS sound output = Mac speakers, not the UMC
- [ ] Audio MIDI Setup: UMC404HD 48 kHz in/out
- [ ] Amp volume down, amp switched on last
- [ ] DSP flat preset loaded, amp EQ/high-pass off
- [ ] +48 V on, PAD off on in 1, MIX at PLAYBACK
- [ ] REW: in 1 / out 1 or 2, loopback in 2 / out 3, 48 kHz
- [ ] Correct cal file loaded (90° up at seat, 0° for close-up)
- [ ] Mic gain + amp volume = same as the photo from last time (or redo Phase D + E)
- [ ] REW output −24 dBFS (fixed), input peaks ≈ −12 dBFS, ~75–80 dB SPL at the seat
- [ ] Measurements named per [measurements/README.md](../../measurements/README.md) (e.g. `1 L pos1 left30`), IR export settings from there too

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

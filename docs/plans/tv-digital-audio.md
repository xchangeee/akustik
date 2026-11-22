# TV audio: digital instead of the 3.5 mm out

Planned 2026-11-22 (user).

## Why

- The TV's 3.5 mm jack is worn out: it hums on the mains with the TV silent (P06, amp 40; gone with the TV cable unplugged).

## New chain

- TV is only a display (no tuner, no TV apps). Sources (HDMI) → extractor → TV.
  - Apple TV → extractor HDMI in
  - PS5 → extractor HDMI in
  - Extractor HDMI out → TV
- Audio: extractor → TOSLINK → SMSL D1 (DAC) → RCA → DSP In A / In B → A300 (unchanged).
- The TV → DSP cable (3.5 mm adapter) goes away.
- Extractor: ROFAVEZCO HDMI 2.1 audio extractor, 2 in / 1 out (4K@120 Hz, HDCP 2.3). Audio out: SPDIF optical (up to 5.1) and analog L/R. ARC not needed.
  - Use the optical out → D1. Leave the analog L/R out unused.

## To check when it's wired

- [ ] Stereo PCM only: the D1 can't decode Dolby/DTS. Apple TV: already set to stereo (user, 2026-11-22). PS5: set Audio Output to Linear PCM, 2 ch; if the extractor has a 2CH / 5.1CH switch, set 2CH.
- [ ] D1 output level vs the DSP input clip (~+9.5 dBu; a 2 Vrms DAC is +8.2 dBu, little headroom): check the D1 spec, play a loud track, watch the DSP input meters.
- [ ] Volume: does the D1 (or a source) have a volume control before the DSP? If so, the sub would follow the volume, which changes the "sub only at a fixed amp position" decision ([decisions.md](../decisions.md)).
- [ ] Source level changed: the amp positions per EQ and the sub match (P05 at 50, P06 at 45) assume TV out 80/100. Re-check the level at the seat (pink noise, same as [listening](../../findings/2026-11-20-listening.md#amp-volume-smsl-a300-per-eq)) and adjust Out 3 gain if needed.
- [ ] Listen with the TV silent at amp 40–50: no hum.
- [ ] Then update [current-setup.md](../current-setup.md) (wiring, TV settings) and [context.md](../context.md) (signal chain).

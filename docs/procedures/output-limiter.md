# Output limiter (do after the EQ is final)

Goal: a compressor on DSP Out 1/2 (later Out 3) that does nothing at normal volume and only catches overload: DJ sets, a hot mixer, loud parties.
The DSP has no separate limiter: the output **compressor with ratio "Limit"** (index 15, measured ∞:1) is the limiter. It isn't a brickwall peak limiter: the knee is always soft (≥ ~4 dB) and the attack isn't instant, so short peaks get through a little above the threshold. That's fine for protecting against overload.
No input gate (nothing audible to gate; this DSP's gate opens only hold + 1 ms after the signal starts, so it would cut off starts after silence).
Why measured: the threshold works on the DSP's output level (after the output gain), and nobody knows yet where the A300 + speakers run out.
Limiter settings start from tracks `docs/protocol.md` §5/§6.4.

**Before you start**
- [ ] Do it for both presets: P03 EQ v2 (everyday) and P02 EQ v1 (loud sessions). v2 cuts less bass, so it reaches the limit sooner: measure each preset with its own EQ.
- [ ] **Pick the amp volume position the limiter is for**: the loudest position you'll ever use (or full). Positions used so far (2026-11-20): v2 up to 45 (higher only briefly), v1 fun at 50 and once at 60 (~100 dB(C) at the seat); see [listening](../../findings/2026-11-20-listening.md#amp-volume-smsl-a300-per-eq). The compressor is stored per preset, so v1 and v2 can each get their own threshold. Mark it on the knob. The limiter only protects up to that position; turning the amp further up beyond it bypasses the protection.
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
- [ ] Store in the preset (DJ/party preset at least). Note values + amp knob position under "Results" below and in [../current-setup.md](../current-setup.md).
- [ ] Later, with the Sub8 on Out 3: repeat step 1 for the sub alone and give Out 3 its own threshold.

Results:
- (not done yet)

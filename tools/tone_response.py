"""Steady-sine response of a UMC path (no deconvolution): ground truth for the low end of a sweep measurement.

Usage: uv run python tools/tone_response.py <out.txt> [--out 1] [--in 3] [--level -24] [--freqs 10,12,...] [--seconds 3]
Plays each sine on UMC output --out and on Out 3 (loopback, recorded on In 2), measures the RMS level of the
input --in (last 2 s, by projection on the exact frequency, so noise and hum don't count) relative to 1 kHz.
Prints and writes a table; compare with the sweep IR's magnitude at the same frequencies.
"""
import argparse
import numpy as np
import sounddevice as sd

SR = 48000


def level(x, f):
    t = np.arange(len(x)) / SR
    c, s = np.mean(x * np.cos(2 * np.pi * f * t)), np.mean(x * np.sin(2 * np.pi * f * t))
    return 20 * np.log10(2 * np.hypot(c, s) + 1e-30)  # amplitude in dBFS (peak)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("outfile")
    ap.add_argument("--out", type=int, default=1), ap.add_argument("--in", dest="inp", type=int, default=3)
    ap.add_argument("--level", type=float, default=-24), ap.add_argument("--seconds", type=float, default=3)
    ap.add_argument("--freqs", default="10,12,15,20,25,30,40,50,70,100,1000")
    ap.add_argument("--device", default="UMC404HD")
    a = ap.parse_args()
    dev = [i for i, d in enumerate(sd.query_devices()) if a.device in d["name"]][0]
    amp = 10 ** (a.level / 20)
    rows = []
    for f in [float(x) for x in a.freqs.split(",")]:
        n = int(a.seconds * SR)
        t = np.arange(n) / SR
        x = amp * np.sin(2 * np.pi * f * t)
        ramp = int(0.2 * SR)
        x[:ramp] *= np.linspace(0, 1, ramp) ** 2
        x[-ramp:] *= np.linspace(1, 0, ramp) ** 2
        rec = sd.playrec(np.stack([x, x], 1).astype(np.float32), samplerate=SR, device=dev, blocking=True,
                         input_mapping=[a.inp, 2], output_mapping=[a.out, 3]).astype(float)
        seg = rec[int(0.5 * SR):int(0.5 * SR) + int(2 * SR)]  # skip ramp + latency (~0.26 s)
        k = int(round(f * 2)) / 2  # whole number of cycles in 2 s for f on a 0.5 Hz grid
        rows.append((f, level(seg[:, 0], f), level(seg[:, 1], f)))
        print(f"  {f:7.1f} Hz  In {a.inp} {rows[-1][1]:7.2f} dBFS  loopback {rows[-1][2]:7.2f} dBFS", flush=True)
    ref = [r for r in rows if r[0] == 1000.0][0]
    lines = [f"Steady sines {a.level} dBFS peak on UMC Out {a.out} (+ Out 3 loopback); levels re 1 kHz", "     Hz    In %d   loopback" % a.inp]
    lines += [f"{f:7.1f}  {i - ref[1]:+6.2f}   {l - ref[2]:+6.2f}" for f, i, l in rows]
    txt = "\n".join(lines)
    print(txt)
    open(a.outfile, "w").write(txt + "\n")


if __name__ == "__main__":
    main()

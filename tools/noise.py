"""Record the UMC inputs with nothing playing and print the noise per band (for finding noise sources).

Usage: uv run python tools/noise.py <folder> <label> [--inputs 1,2,3] [--seconds 5] [--device UMC404HD]
Saves <folder>/<label>.flac (24-bit, one channel per input) and appends the printed table to <folder>/noise.txt.
Bands in dBFS RMS: total, <20 Hz, 20-45, 45-55 (50 Hz hum), 55-95, 95-105 (100 Hz), 105-1k, >1 kHz.
"""
import argparse, datetime, os
import numpy as np
import sounddevice as sd
import soundfile as sf

BANDS = [(0, 20), (20, 45), (45, 55), (55, 95), (95, 105), (105, 1000), (1000, 24000)]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("folder"), ap.add_argument("label")
    ap.add_argument("--inputs", default="1,2,3"), ap.add_argument("--seconds", type=float, default=5)
    ap.add_argument("--device", default="UMC404HD")
    a = ap.parse_args()
    sr = 48000
    ins = [int(x) for x in a.inputs.split(",")]
    dev = [i for i, d in enumerate(sd.query_devices()) if a.device in d["name"]][0]
    x = sd.rec(int((a.seconds + 0.5) * sr), samplerate=sr, device=dev, mapping=ins, blocking=True).astype(float)[int(0.5 * sr):]
    os.makedirs(a.folder, exist_ok=True)
    sf.write(os.path.join(a.folder, f"{a.label}.flac"), x, sr, subtype="PCM_24")
    f = np.fft.rfftfreq(len(x), 1 / sr)
    w = np.hanning(len(x))
    lines = [f"{datetime.datetime.now():%H:%M:%S} {a.label}"]
    lines.append("  input   total   " + "  ".join(f"{lo}-{hi}".rjust(9) for lo, hi in BANDS))
    for c, n in enumerate(ins):
        X = np.abs(np.fft.rfft(x[:, c] * w)) ** 2 / np.sum(w ** 2) * 2 / len(x)  # power per bin, sums to the mean square
        tot = 10 * np.log10(np.mean(x[:, c] ** 2) + 1e-30)
        b = [10 * np.log10(np.sum(X[(f >= lo) & (f < hi)]) + 1e-30) for lo, hi in BANDS]
        lines.append(f"  In {n}   {tot:6.1f}   " + "  ".join(f"{v:9.1f}" for v in b))
    txt = "\n".join(lines)
    print(txt)
    with open(os.path.join(a.folder, "noise.txt"), "a") as fh:
        fh.write(txt + "\n")


if __name__ == "__main__":
    main()

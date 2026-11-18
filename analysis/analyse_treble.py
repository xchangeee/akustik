"""Treble tilt at the seat / DJ vs a Harman-style in-room tilt. Usage: analyse_treble.py <repo> <out_dir>

Same IR processing as design_eq.py (500 ms window, 90° cal, power average over positions), 1/6-oct smoothing.
Levels relative to each set's own 300 Hz-3 kHz mean (the reference design_eq.py uses).
Harman-style tilt used for comparison: 0 dB up to 1 kHz, then -1 dB/oct (-3.3 dB at 10 kHz, -4.3 dB at 20 kHz).
"""
import sys, os, glob, re
import numpy as np
from scipy.io import wavfile
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt

repo, out = sys.argv[1], sys.argv[2]
T0, SR, NFFT = 256, 48000, 1 << 16
cal = np.loadtxt(os.path.join(repo, "cal", "MM-1C_90deg.txt"), comments="*")
fq = np.fft.rfftfreq(NFFT, 1 / SR)
calc = np.interp(np.log10(np.maximum(fq, 1)), np.log10(cal[:, 0]), cal[:, 1])


def spec(f):
    sr, x = wavfile.read(f); assert sr == SR
    x = x.astype(float); n_end = T0 + int(0.5 * SR); x = np.pad(x, (0, max(0, n_end - len(x))))[:n_end]
    fade = int(0.125 * SR); x[-fade:] *= 0.5 * (1 + np.cos(np.linspace(0, np.pi, fade)))
    return np.fft.rfft(x, NFFT) * 10 ** (-calc / 20)


GRID = np.geomspace(100, 20000, 400); FRAC = 6
lo = np.searchsorted(fq, GRID * 2 ** (-0.5 / FRAC)); hi = np.maximum(np.searchsorted(fq, GRID * 2 ** (0.5 / FRAC)), lo + 1)
sm = lambda H: (lambda cs: (cs[hi] - cs[lo]) / (hi - lo))(np.concatenate([[0], np.cumsum(np.abs(H) ** 2)]))


def pairs(folder, pat):
    d = {}
    for f in glob.glob(os.path.join(repo, "measurements", folder, "*.wav")):
        m = re.search(pat, os.path.basename(f))
        if m: d.setdefault(m.group(2), {})[m.group(1)] = spec(f)
    return d


sets = {"seat": pairs("2026-11-18-pos-sweeps-L-R", r"\d ([LR]) (pos\d \w+) "),
        "dj": pairs("2026-11-18-dj-sweeps-L-R", r"\d ([LR]) DJ (\w+) ")}
sets["seat"]["seat"] = {("L" if "left" in f else "R"): spec(f) for f in glob.glob(os.path.join(repo, "measurements", "*first sweep*.wav"))}
TILT = np.where(GRID > 1000, -np.log2(GRID / 1000), 0.0)
REFB = (GRID > 300) & (GRID < 3000)
res = {}
for n, d in sets.items():
    for w in ("L", "R"):
        y = 10 * np.log10(np.mean([sm(lr[w]) for lr in d.values()], axis=0))
        res[(n, w)] = y - y[REFB].mean()
at = lambda y, f: np.interp(np.log10(f), np.log10(GRID), y)
FS = [200, 300, 500, 1000, 1500, 2000, 3000, 4000, 5000, 6300, 8000, 10000, 12500, 16000, 20000]
print("Level rel. to own 300 Hz-3 kHz mean, 1/6 oct, power avg over positions (seat 7, DJ 7)")
print(f"{'Hz':>6} | " + " | ".join(f"{n} {w:>2}" for n, w in res) + " | Harman tilt")
for f in FS:
    print(f"{f:6} | " + " | ".join(f"{at(y, f):+7.1f}" for y in res.values()) + f" | {at(TILT, f):+6.1f}")
print("\nSlope fit 1-16 kHz (dB/oct): " + ", ".join(
    f"{n} {w} {np.polyfit(np.log2(GRID[(GRID>1000)&(GRID<16000)]/1000), y[(GRID>1000)&(GRID<16000)], 1)[0]:+.2f}" for (n, w), y in res.items()))
print("Mean deviation from Harman tilt, 4-16 kHz (dB): " + ", ".join(
    f"{n} {w} {np.mean((y-TILT)[(GRID>4000)&(GRID<16000)]):+.1f}" for (n, w), y in res.items()))
fig, ax = plt.subplots(figsize=(11, 5))
for (n, w), y in res.items():
    ax.semilogx(GRID, y, lw=2 if n == "seat" else 1, ls="-" if n == "seat" else ":", label=f"{n} {w}")
ax.semilogx(GRID, TILT, "g--", label="Harman-style tilt (-1 dB/oct above 1 kHz)")
ax.set_xlim(100, 20000); ax.set_ylim(-15, 10); ax.grid(True, which="both", alpha=0.3); ax.legend(fontsize=8)
ax.set_title("Treble at seat / DJ, rel. to 300 Hz-3 kHz mean (1/6 oct, power avg)")
plt.tight_layout(); plt.savefig(os.path.join(out, "treble.png"), dpi=110)

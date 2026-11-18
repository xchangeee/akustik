"""DJ vs seat: L, R and coherent L+R sum (IRs share the loopback timing ref). Usage: dj.py <repo> <out>"""
import sys, os, glob, re, numpy as np
from scipy.io import wavfile
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
repo, out = sys.argv[1], sys.argv[2]
T0, SR, NFFT, OFFSET = 256, 48000, 1 << 18, 100.9
cal = np.loadtxt(os.path.join(repo, "cal", "MM-1C_90deg.txt"), comments="*")
fq = np.fft.rfftfreq(NFFT, 1 / SR)
calc = np.interp(np.log10(np.maximum(fq, 1)), np.log10(cal[:, 0]), cal[:, 1])
def spec(f):
    sr, x = wavfile.read(f); x = x.astype(float)
    n_end = T0 + int(0.5 * SR); x = np.pad(x, (0, max(0, n_end - len(x))))[:n_end]
    fade = int(0.125 * SR); x[-fade:] *= 0.5 * (1 + np.cos(np.linspace(0, np.pi, fade)))
    return np.fft.rfft(x, NFFT)
def db(H): return 20 * np.log10(np.abs(H) + 1e-20) - calc
def smooth(d, frac):
    grid = np.geomspace(15, 22000, 1200); p = 10 ** (d / 10); cs = np.concatenate([[0], np.cumsum(p)])
    lo = np.searchsorted(fq, grid * 2 ** (-0.5 / frac)); hi = np.maximum(np.searchsorted(fq, grid * 2 ** (0.5 / frac)), lo + 1)
    return grid, 10 * np.log10((cs[hi] - cs[lo]) / (hi - lo)) + OFFSET
def pavg(cs): return 10 * np.log10(np.mean(10 ** (np.array(cs) / 10), axis=0))
def pairs(folder, pat):
    d = {}
    for f in glob.glob(os.path.join(repo, "measurements", folder, "*.wav")):
        m = re.search(pat, os.path.basename(f))
        if m: d.setdefault(m.group(2), {})[m.group(1)] = f
    return d
seat = pairs("2026-11-18-pos-sweeps-L-R", r"\d ([LR]) (pos\d \w+) ")
seat["seat"] = {("L" if "left" in f else "R"): f for f in glob.glob(os.path.join(repo, "measurements", "*first sweep*.wav"))}
dj = pairs("2026-11-18-dj-sweeps-L-R", r"\d ([LR]) DJ (\w+) ")
print("seat positions:", sorted(seat), "\nDJ positions:", sorted(dj))
res = {}
for name, d in (("seat", seat), ("dj", dj)):
    for frac in (6, 24):
        cL, cR, cS = [], [], []
        for p, lr in d.items():
            HL, HR = spec(lr["L"]), spec(lr["R"])
            g, a = smooth(db(HL), frac); cL.append(a)
            cR.append(smooth(db(HR), frac)[1]); cS.append(smooth(db(HL + HR), frac)[1])
        res[(name, frac)] = (g, pavg(cL), pavg(cR), pavg(cS), np.array(cS))
at = lambda g, y, f0: np.interp(np.log10(f0), np.log10(g), y)
g = res[("seat", 6)][0]; ref = (g > 300) & (g < 3000)
refs = {}
for name in ("seat", "dj"):
    _, L, R, S_, _ = res[(name, 6)]
    refs[name] = (L[ref].mean(), R[ref].mean(), S_[ref].mean())
    print(f"{name}: ref 300 Hz-3 kHz  L {refs[name][0]:.1f}  R {refs[name][1]:.1f}  L+R {refs[name][2]:.1f} dB")
print("\n1/6 oct, values relative to each set's own L+R reference (so 0 = balanced with the mids)")
print(f"{'Hz':>5} | {'seat L':>6} {'seat R':>6} {'seat L+R':>8} | {'DJ L':>6} {'DJ R':>6} {'DJ L+R':>7} | {'DJ-seat (L+R)':>13}")
for f0 in [25, 28, 30, 35, 40, 43, 47, 51, 55, 60, 65, 68, 75, 80, 85, 89, 95, 100, 105, 110, 115, 120, 128, 140, 150, 163, 175, 190, 210, 250, 300]:
    r = []
    for name in ("seat", "dj"):
        gg, L, R, S_, _ = res[(name, 6)]; rs = refs[name][2]
        r += [at(gg, L, f0) - rs, at(gg, R, f0) - rs, at(gg, S_, f0) - rs]
    print(f"{f0:5} | {r[0]:+6.1f} {r[1]:+6.1f} {r[2]:+8.1f} | {r[3]:+6.1f} {r[4]:+6.1f} {r[5]:+7.1f} | {r[5]-r[2]:+13.1f}")
# DJ spread of L+R
gg, _, _, S_, curves = res[("dj", 6)]
print("\nDJ L+R spread across positions (min..max, rel. to DJ ref):")
for f0 in [43, 51, 68, 89, 100, 115, 128]:
    print(f"  {f0} Hz: {at(gg, curves.min(0), f0)-refs['dj'][2]:+.1f} .. {at(gg, curves.max(0), f0)-refs['dj'][2]:+.1f}")
fig, axs = plt.subplots(2, 1, figsize=(12, 9), sharex=True)
for ax, name in zip(axs, ("seat", "dj")):
    gg, L, R, S_, curves = res[(name, 24)]; rs = refs[name][2]
    for c in curves: ax.semilogx(gg, c - rs, color="grey", lw=0.5, alpha=0.5)
    ax.semilogx(gg, L - rs, label="L only"); ax.semilogx(gg, R - rs, label="R only"); ax.semilogx(gg, S_ - rs, "k", lw=2, label="L+R (summed IRs)")
    ax.axhline(0, color="k", lw=0.5); ax.set_xlim(18, 1000); ax.set_ylim(-25, 25); ax.grid(True, which="both", alpha=0.3)
    ax.set_title(f"{name}: position average (1/24 oct), relative to own L+R mid level; grey = L+R per position"); ax.legend(fontsize=8)
    ax.set_xticks([20, 30, 40, 50, 60, 80, 100, 150, 200, 300, 500, 1000]); ax.set_xticklabels([20, 30, 40, 50, 60, 80, 100, 150, 200, 300, 500, "1k"])
axs[1].set_xlabel("Hz"); plt.tight_layout(); plt.savefig(os.path.join(out, "dj_vs_seat.png"), dpi=110)

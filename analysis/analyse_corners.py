"""Compare corner measurements with seat position average. Usage: corner.py <repo> <out>"""
import sys, os, glob, re, numpy as np
from scipy.io import wavfile
from scipy.signal import find_peaks
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
repo, out = sys.argv[1], sys.argv[2]
T0, SR, NFFT = 256, 48000, 1 << 18
cal = np.loadtxt(os.path.join(repo, "cal", "MM-1C_90deg.txt"), comments="*")
OFFSET = 100.9  # same as position analysis (L seat 1-8 kHz = 73.5 dB)
def fr(f):
    sr, x = wavfile.read(f); x = x.astype(float)
    n_end = T0 + int(0.5 * SR); x = np.pad(x, (0, max(0, n_end - len(x))))[:n_end]
    fade = int(0.125 * SR); x[-fade:] *= 0.5 * (1 + np.cos(np.linspace(0, np.pi, fade)))
    H = np.fft.rfft(x, NFFT); fq = np.fft.rfftfreq(NFFT, 1 / SR)
    c = np.interp(np.log10(np.maximum(fq, 1)), np.log10(cal[:, 0]), cal[:, 1])
    return fq, 20 * np.log10(np.abs(H) + 1e-20) - c
def smooth(f, db, frac):
    grid = np.geomspace(15, 22000, 1200); p = 10 ** (db / 10)
    cs = np.concatenate([[0], np.cumsum(p)])
    lo = np.searchsorted(f, grid * 2 ** (-0.5 / frac)); hi = np.maximum(np.searchsorted(f, grid * 2 ** (0.5 / frac)), lo + 1)
    return grid, 10 * np.log10((cs[hi] - cs[lo]) / (hi - lo)) + OFFSET
def pavg(cs): return 10 * np.log10(np.mean(10 ** (np.array(cs) / 10), axis=0))
seatfiles = {"L": [], "R": []}
for f in glob.glob(os.path.join(repo, "measurements", "*first sweep*.wav")):
    seatfiles["L" if "left" in f else "R"].append(f)
for f in glob.glob(os.path.join(repo, "measurements", "2026-11-18-pos-sweeps-L-R", "*.wav")):
    seatfiles[re.search(r"\d ([LR]) ", os.path.basename(f)).group(1)].append(f)
corner = {}
for f in glob.glob(os.path.join(repo, "measurements", "2026-11-18-corner-sweeps-L-R", "*.wav")):
    m = re.search(r"\d ([LR]) corner front (\w+) ", os.path.basename(f)); corner[(m.group(1), m.group(2))] = f
at = lambda g, y, f0: np.interp(np.log10(f0), np.log10(g), y)
fig, axs = plt.subplots(2, 1, figsize=(12, 9), sharex=True)
for ax, spk in zip(axs, "LR"):
    seat24 = [smooth(*fr(f), 24) for f in seatfiles[spk]]; g = seat24[0][0]
    seat = pavg([s for _, s in seat24])
    cl = smooth(*fr(corner[(spk, "left")]), 24)[1]; cr = smooth(*fr(corner[(spk, "right")]), 24)[1]
    cav = pavg([cl, cr])
    sel = (g > 20) & (g < 300)
    # corner reference: median level 30-200 Hz, to judge relative peaks
    cref = np.median(cav[(g > 30) & (g < 200)]); sref = np.median(seat[(g > 30) & (g < 200)])
    print(f"\n=== {spk}: corner (avg of 2) vs seat average; corner median 30-200 Hz {cref:.1f} dB, seat median {sref:.1f} dB ===")
    pk, pr = find_peaks(cav[sel], prominence=4)
    print(f"{'Hz':>7} {'corner':>7} {'c-med':>6} {'c-left':>7} {'c-right':>8} {'seat':>6} {'s-med':>6}")
    for i in pk:
        f0 = g[sel][i]
        print(f"{f0:7.1f} {cav[sel][i]:7.1f} {cav[sel][i]-cref:+6.1f} {at(g,cl,f0):7.1f} {at(g,cr,f0):8.1f} {at(g,seat,f0):6.1f} {at(g,seat,f0)-sref:+6.1f}")
    ax.semilogx(g, seat, "k", lw=2, label=f"{spk} seat average (7 pos)")
    ax.semilogx(g, cl, lw=1, label=f"{spk} corner front-left"); ax.semilogx(g, cr, lw=1, label=f"{spk} corner front-right")
    ax.set_xlim(18, 400); ax.set_ylim(50, 110); ax.grid(True, which="both", alpha=0.3); ax.legend(fontsize=8)
    ax.set_title(f"{spk}: corners vs seat average (1/24 oct)"); ax.set_ylabel("dB SPL (approx)")
    ax.set_xticks([20, 30, 40, 50, 60, 80, 100, 150, 200, 300]); ax.set_xticklabels([20, 30, 40, 50, 60, 80, 100, 150, 200, 300])
axs[1].set_xlabel("Hz"); plt.tight_layout(); plt.savefig(os.path.join(out, "corners.png"), dpi=110)

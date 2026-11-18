"""Analyse REW IR exports: FR per position, power average, spread, peaks, decay.
Usage: analyse.py <repo_dir> <out_dir>
"""
import sys, os, glob, re
import numpy as np
from scipy.io import wavfile
from scipy.signal import find_peaks, butter, sosfiltfilt
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

repo, out = sys.argv[1], sys.argv[2]
T0 = 256           # t=0 sample index in exports
SR = 48000
NFFT = 1 << 18     # 0.18 Hz bins

# ---------- load ----------
files = {}
seat = sorted(glob.glob(os.path.join(repo, "measurements", "2026-11-18", "seat", "*first sweep*.wav")))
for f in seat:
    spk = "L" if "left" in f else "R"
    files[(spk, "seat")] = f
for f in sorted(glob.glob(os.path.join(repo, "measurements", "2026-11-18/positions", "*.wav"))):
    m = re.search(r"\d ([LR]) (pos\d \w+) ", os.path.basename(f))
    files[(m.group(1), m.group(2))] = f
positions = ["seat"] + sorted({p for (_, p) in files if p != "seat"})

cal = np.loadtxt(os.path.join(repo, "reference", "mic-cal", "MM-1C_90deg.txt"), comments="*")

def load(f):
    sr, x = wavfile.read(f)
    assert sr == SR
    return x.astype(float)

def fr(x, right_ms=500):
    """REW-like window: start at file start (t0-5.3 ms), flat to t0+right*0.75, half-Tukey to t0+right."""
    n_end = T0 + int(right_ms / 1000 * SR)
    x = x[:n_end].copy()
    if len(x) < n_end:
        x = np.pad(x, (0, n_end - len(x)))
    fade = int(0.25 * right_ms / 1000 * SR)
    x[-fade:] *= 0.5 * (1 + np.cos(np.linspace(0, np.pi, fade)))
    H = np.fft.rfft(x, NFFT)
    f = np.fft.rfftfreq(NFFT, 1 / SR)
    db = 20 * np.log10(np.abs(H) + 1e-20)
    # mic cal: subtract cal response
    c = np.interp(np.log10(np.maximum(f, 1)), np.log10(cal[:, 0]), cal[:, 1])
    return f, db - c

def smooth(f, db, frac):
    """fractional-octave power smoothing, evaluated on a log grid"""
    grid = np.geomspace(15, 22000, 1200)
    p = 10 ** (db / 10)
    cs = np.concatenate([[0], np.cumsum(p)])
    lo = np.searchsorted(f, grid * 2 ** (-0.5 / frac))
    hi = np.searchsorted(f, grid * 2 ** (0.5 / frac))
    hi = np.maximum(hi, lo + 1)
    return grid, 10 * np.log10((cs[hi] - cs[lo]) / (hi - lo))

data = {}
for k, f in files.items():
    fq, db = fr(load(f))
    data[k] = (fq, db)

# absolute offset: REW showed L seat ~ 85 dB peak @ ~42 Hz and 72-75 dB at 1-8 kHz (1/6 oct).
# Match L seat 1-8 kHz mean (1/6 oct) to 73.5 dB. Approximate (+-1 dB).
g, s = smooth(*data[("L", "seat")], 6)
band = (g > 1000) & (g < 8000)
OFFSET = 73.5 - s[band].mean()

def sm(k, frac):
    g, s = smooth(*data[k], frac)
    return g, s + OFFSET

# ---------- averages ----------
res = {}
for spk in "LR":
    ks = [(spk, p) for p in positions if (spk, p) in data]
    for frac in (6, 24):
        curves = np.array([sm(k, frac)[1] for k in ks])
        g = sm(ks[0], frac)[0]
        avg = 10 * np.log10(np.mean(10 ** (curves / 10), axis=0))
        res[(spk, frac)] = (g, avg, curves, ks)

def at(g, y, f0):
    return np.interp(np.log10(f0), np.log10(g), y)

print(f"Offset applied: {OFFSET:.1f} dB (approx, from L seat 1-8 kHz = 73.5 dB)")
print(f"Positions per speaker: {len(res[('L',6)][3])}: {positions}")

print("\n=== 1/6-oct power average vs frequency (dB SPL approx), spread = min..max across positions ===")
print(f"{'Hz':>6} | {'L avg':>6} {'L min':>6} {'L max':>6} | {'R avg':>6} {'R min':>6} {'R max':>6} | R-L")
for f0 in [20, 25, 28, 30, 32, 35, 40, 42, 45, 50, 55, 57, 60, 65, 70, 75, 80, 85, 88, 90, 95, 100, 110, 120, 125, 130, 140, 150, 160, 170, 180, 190, 200, 220, 250, 300, 350, 400, 500, 630, 800, 1000, 1500, 2000, 3000, 5000, 8000, 10000, 15000, 20000]:
    row = []
    for spk in "LR":
        g, avg, curves, _ = res[(spk, 6)]
        row += [at(g, avg, f0), at(g, curves.min(0), f0), at(g, curves.max(0), f0)]
    print(f"{f0:>6} | {row[0]:6.1f} {row[1]:6.1f} {row[2]:6.1f} | {row[3]:6.1f} {row[4]:6.1f} {row[5]:6.1f} | {row[3]-row[0]:+5.1f}")

# reference level: 300 Hz - 3 kHz mean of average (what bass is compared to)
for spk in "LR":
    g, avg, curves, _ = res[(spk, 6)]
    b = (g > 300) & (g < 3000)
    print(f"{spk} reference level 300 Hz-3 kHz (1/6 avg): {avg[b].mean():.1f} dB")

print("\n=== Peaks in 1/24-oct power average, 20-300 Hz (prominence >= 3 dB) ===")
for spk in "LR":
    g, avg, curves, _ = res[(spk, 24)]
    sel = (g > 18) & (g < 320)
    gi, ai, ci = g[sel], avg[sel], curves[:, sel]
    pk, pr = find_peaks(ai, prominence=3)
    b = (g > 300) & (g < 3000)
    ref = res[(spk, 6)][1][(res[(spk, 6)][0] > 300) & (res[(spk, 6)][0] < 3000)].mean()
    print(f"-- {spk} (ref {ref:.1f} dB)")
    for i in pk:
        # per-position: local max within +-1/12 oct
        win = (gi > gi[i] * 2 ** (-1 / 12)) & (gi < gi[i] * 2 ** (1 / 12))
        pmax = ci[:, win].max(1)
        print(f"   {gi[i]:6.1f} Hz  avg {ai[i]:5.1f} dB ({ai[i]-ref:+5.1f} vs ref)  prom {pr['prominences'][list(pk).index(i)]:4.1f}  per-pos range {pmax.min():.1f}..{pmax.max():.1f} (sd {pmax.std():.1f})")
    dp, dpr = find_peaks(-ai, prominence=4)
    print(f"   dips:")
    for i in dp:
        win = (gi > gi[i] * 2 ** (-1 / 12)) & (gi < gi[i] * 2 ** (1 / 12))
        pmin = ci[:, win].min(1)
        print(f"   {gi[i]:6.1f} Hz  avg {ai[i]:5.1f} dB ({ai[i]-ref:+5.1f})  per-pos {pmin.min():.1f}..{pmin.max():.1f} (sd {pmin.std():.1f})")

# ---------- decay ----------
def schroeder_t(x, f_lo, f_hi, lo_db=-5, hi_db=-25):
    sos = butter(4, [f_lo, f_hi], btype="band", fs=SR, output="sos")
    y = sosfiltfilt(sos, x)[T0:]
    e = y ** 2
    # noise compensation: subtract tail mean (last 0.3 s)
    nz = e[-int(0.3 * SR):].mean()
    e = np.maximum(e - nz, 0)
    sch = np.cumsum(e[::-1])[::-1]
    sch_db = 10 * np.log10(sch / sch[0] + 1e-30)
    t = np.arange(len(sch_db)) / SR
    i1 = np.argmax(sch_db <= lo_db); i2 = np.argmax(sch_db <= hi_db)
    if i2 <= i1:
        return np.nan
    slope = np.polyfit(t[i1:i2], sch_db[i1:i2], 1)[0]
    return -60 / slope

print("\n=== Decay: T20-based RT60 (s), octave bands, mean over positions ===")
oct_c = [63, 125, 250, 500, 1000, 2000, 4000]
print("band  " + " ".join(f"{c:>6}" for c in oct_c))
for spk in "LR":
    vals = []
    for c in oct_c:
        ts = [schroeder_t(load(files[(spk, p)]), c / 2 ** 0.5, c * 2 ** 0.5) for p in positions]
        vals.append(np.nanmean(ts))
    print(f"{spk}     " + " ".join(f"{v:6.2f}" for v in vals))

print("\n=== Decay at bass peaks: T(-5..-25 dB) in 1/6-oct band around frequency, mean over positions ===")
for spk in "LR":
    g, avg, _, _ = res[(spk, 24)]
    sel = (g > 18) & (g < 320)
    gi, ai = g[sel], avg[sel]
    pk, _ = find_peaks(ai, prominence=3)
    out_s = []
    for i in pk:
        f0 = gi[i]
        ts = [schroeder_t(load(files[(spk, p)]), f0 * 2 ** (-1 / 12), f0 * 2 ** (1 / 12)) for p in positions]
        out_s.append(f"{f0:.0f} Hz: {np.nanmean(ts):.2f} s")
    print(f"{spk}: " + ", ".join(out_s))

# ---------- plots ----------
fig, axs = plt.subplots(2, 1, figsize=(12, 9), sharex=True)
for ax, spk in zip(axs, "LR"):
    g, avg, curves, ks = res[(spk, 24)]
    for c, k in zip(curves, ks):
        ax.semilogx(g, c, lw=0.7, alpha=0.6, label=k[1])
    ax.semilogx(g, avg, "k", lw=2.2, label="power average")
    ax.set_xlim(18, 20000); ax.set_ylim(45, 100); ax.grid(True, which="both", alpha=0.3)
    ax.set_title(f"{spk}: 7 positions (1/24 oct) + power average"); ax.set_ylabel("dB SPL (approx)")
    ax.legend(fontsize=7, ncol=4)
axs[1].set_xlabel("Hz")
plt.tight_layout(); plt.savefig(os.path.join(out, "positions.png"), dpi=110)

fig, ax = plt.subplots(figsize=(12, 5))
for spk, col in (("L", "tab:blue"), ("R", "tab:orange")):
    g, avg, _, _ = res[(spk, 6)]
    ax.semilogx(g, avg, col, lw=2, label=f"{spk} average (1/6 oct)")
for f0, lab in [(29, "29"), (44, "44"), (57, "57"), (61, "61"), (86, "86/88"), (122, "122"), (132, "132")]:
    ax.axvline(f0, color="grey", ls=":", lw=0.8); ax.text(f0, 98, lab, fontsize=7, ha="center")
ax.set_xlim(18, 20000); ax.set_ylim(50, 100); ax.grid(True, which="both", alpha=0.3); ax.legend()
ax.set_ylabel("dB SPL (approx)"); ax.set_xlabel("Hz"); ax.set_title("L vs R position average; dotted = predicted axial modes")
plt.tight_layout(); plt.savefig(os.path.join(out, "LR_average.png"), dpi=110)

np.savez(os.path.join(out, "averages.npz"), **{f"{s}_{fr_}": np.vstack([res[(s, fr_)][0], res[(s, fr_)][1]]) for s in "LR" for fr_ in (6, 24)})
print("\nplots:", os.path.join(out, "positions.png"), os.path.join(out, "LR_average.png"))

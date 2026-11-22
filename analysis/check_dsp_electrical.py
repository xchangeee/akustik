"""Electrical check: DSP out -> UMC In 3 (no amp, no mic) vs the predicted HPF + PEQ curve.

Usage: check_dsp_electrical.py <set folder> <eq folder | flat> <plot.png> [--tol DB --band LO HI] [--files WAV ...]
  e.g. check_dsp_electrical.py measurements/2026-11-22/dsp-electrical-v2 eq/v2-harman analysis/output/dsp_electrical_v2.png
One column per side (L/R) found in the set folder; --files picks the WAVs by name (else the one `* L *.wav` / `* R *.wav`).
`flat` predicts a flat line (no PEQ, no HPF), e.g. for P01 FLAT.
With --tol: prints PASS/FAIL for max |measured - predicted| within LO..HI Hz and exits 1 on FAIL (used by tools/sweep.py).
Predicted curve: the filter files in the eq folder (RBJ values that the configurator import maps onto the device grid, so
RBJ peaking with these exact values is the device filter, protocol §6.2) + Butterworth 24 HPF from the Notes line.
Measured: IR export, no mic cal, normalised to its 1-5 kHz level (the EQ is flat there).
Also fits one frequency scale factor (in cents) for all filters, to see the tracks "low-frequency offset".
"""
import argparse, sys, os, re, glob
import numpy as np
from scipy.io import wavfile
from scipy.signal import butter, sosfreqz
from scipy.optimize import minimize_scalar
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt

ap = argparse.ArgumentParser()
ap.add_argument("folder"), ap.add_argument("eq"), ap.add_argument("plot")
ap.add_argument("--tol", type=float), ap.add_argument("--band", type=float, nargs=2, default=(20, 20000))
ap.add_argument("--files", nargs="+")
a = ap.parse_args()
folder, plotname = a.folder, a.plot
eqname = "flat" if a.eq == "flat" else os.path.basename(os.path.normpath(a.eq))
T0, SR, NFFT = 256, 48000, 1 << 18


def read_eq(s):
    if a.eq == "flat":
        return [], None
    txt = open(os.path.join(a.eq, f"{s}.txt")).read()
    bands = [(float(f), float(g), float(q)) for f, g, q in
             re.findall(r"ON\s+PK\s+Fc\s+([\d.]+)\s*Hz\s+Gain\s+([-\d.]+)\s*dB\s+Q\s+([\d.]+)", txt)]
    hp = float(re.search(r"Butterworth 24 dB/oct ([\d.]+) Hz", txt).group(1))
    return bands, hp


def predicted(f, bands, hp, scale=1.0):
    z = np.exp(-1j * 2 * np.pi * f / SR)
    H = np.ones(len(f), complex) if hp is None else sosfreqz(butter(4, hp * scale, btype="high", fs=SR, output="sos"), worN=f, fs=SR)[1]
    for fc, g, q in bands:
        A = 10 ** (g / 40); w = 2 * np.pi * fc * scale / SR; al = np.sin(w) / (2 * q); c = np.cos(w)
        H = H * ((1 + al * A) - 2 * c * z + (1 - al * A) * z ** 2) / ((1 + al / A) - 2 * c * z + (1 - al / A) * z ** 2)
    return 20 * np.log10(np.abs(H))


def measured(path):
    sr, x = wavfile.read(path); assert sr == SR
    x = x.astype(float)
    n_end = T0 + int(0.5 * SR); x = np.pad(x, (0, max(0, n_end - len(x))))[:n_end]
    fade = int(0.125 * SR); x[-fade:] *= 0.5 * (1 + np.cos(np.linspace(0, np.pi, fade)))
    H = np.fft.rfft(x, NFFT); f = np.fft.rfftfreq(NFFT, 1 / SR)
    db = 20 * np.log10(np.abs(H) + 1e-20)
    pk = 20 * np.log10(np.abs(x).max())
    return f, db, pk


def smooth(f, db, grid, frac=48):
    p = 10 ** (db / 10); cs = np.concatenate([[0], np.cumsum(p)])
    lo = np.searchsorted(f, grid * 2 ** (-0.5 / frac)); hi = np.maximum(np.searchsorted(f, grid * 2 ** (0.5 / frac)), lo + 1)
    return 10 * np.log10((cs[hi] - cs[lo]) / (hi - lo))


def pick(side):
    names = a.files if a.files else [os.path.basename(p) for p in glob.glob(os.path.join(folder, "*.wav"))]
    hits = sorted(n for n in names if re.match(rf"\d+ {side} ", n))
    if len(hits) > 1:
        sys.exit(f"{len(hits)} WAVs for {side} in {folder}: {hits}; pick one with --files")
    return os.path.join(folder, hits[0]) if hits else None


sides = [s for s in "LR" if pick(s)]
if not sides:
    sys.exit(f"no L/R WAVs in {folder}")
grid = np.geomspace(15, 20000, 1500)
fig, axs = plt.subplots(2, len(sides), figsize=(7 * len(sides), 8), gridspec_kw=dict(height_ratios=[2.2, 1]), sharex=True, squeeze=False)
worst = (0.0, None, None)
for col, s in enumerate(sides):
    path = pick(s)
    f, db, pk = measured(path)
    m = smooth(f, db, grid)
    m -= m[(grid > 1000) & (grid < 5000)].mean()
    bands, hp = read_eq(s)
    p = predicted(grid, bands, hp)
    sel = (grid > 18) & (grid < 1000)
    err = lambda sc: np.sqrt(np.mean((m[sel] - predicted(grid, bands, hp, sc)[sel]) ** 2))
    best = minimize_scalar(err, bounds=(0.95, 1.05), method="bounded")
    cents = 1200 * np.log2(best.x)
    d = m - p
    print(f"=== {s}: {os.path.basename(path)}  (IR peak {pk:.1f} dBFS, 1-5 kHz normalised)")
    print(f"  bands: " + (", ".join(f"{fc:.1f}/{g:.1f}/{q:.3f}" for fc, g, q in bands) or "none") + f"; HPF " + (f"BW24 {hp} Hz" if hp else "off"))
    for lo, hi in [(20, 30), (30, 60), (60, 150), (150, 1000), (1000, 20000)]:
        b = (grid >= lo) & (grid < hi)
        print(f"  {lo:>5}-{hi:<5} Hz: measured - predicted  mean {d[b].mean():+5.2f}  rms {np.sqrt(np.mean(d[b]**2)):4.2f}  max |{np.abs(d[b]).max():4.2f}| dB")
    print(f"  fit 18-1000 Hz: rms {err(1.0):.2f} dB as designed; best with all filter frequencies x{best.x:.5f} ({cents:+.0f} cents): rms {best.fun:.2f} dB")
    print("  at the band centres (measured / predicted dB):")
    for fc, g, q in bands:
        print(f"    {fc:7.1f} Hz: {np.interp(fc, grid, m):+6.2f} / {np.interp(fc, grid, p):+6.2f}   min of measured within +-1/6 oct at "
              f"{grid[(grid > fc / 2**(1/6)) & (grid < fc * 2**(1/6))][np.argmin(m[(grid > fc / 2**(1/6)) & (grid < fc * 2**(1/6))])]:.1f} Hz")
    ax = axs[0, col]
    ax.semilogx(grid, m, "k", lw=2, label="measured (DSP out, electrical)")
    ax.semilogx(grid, p, "tab:orange", lw=1.2, ls="--", label="predicted (design)")
    ax.set_ylim(-30, 5); ax.grid(True, which="both", alpha=0.3); ax.legend(fontsize=8)
    inb = (grid >= a.band[0]) & (grid <= a.band[1])
    k = np.argmax(np.abs(d[inb]))
    print(f"  max |measured - predicted| {a.band[0]:.0f}-{a.band[1]:.0f} Hz: {abs(d[inb][k]):.2f} dB at {grid[inb][k]:.1f} Hz")
    if abs(d[inb][k]) >= worst[0]:
        worst = (abs(d[inb][k]), grid[inb][k], s)
    ax.set_title(f"EQ {eqname}, {s} (Out {"LR".index(s)+1}): electrical response, 1/48 oct, 0 dB = 1-5 kHz"); ax.set_ylabel("dB")
    axs[1, col].semilogx(grid, d, "k", lw=1); axs[1, col].axhline(0, color="grey", lw=0.5)
    axs[1, col].set_ylim(-3, 3); axs[1, col].grid(True, which="both", alpha=0.3); axs[1, col].set_ylabel("measured - predicted (dB)")
    axs[1, col].set_xlabel("Hz")
ticks = [20, 30, 50, 100, 200, 500, 1000, 2000, 5000, 10000, 20000]
for ax in axs.flat:
    ax.set_xlim(15, 20000); ax.set_xticks(ticks); ax.set_xticklabels(["20", "30", "50", "100", "200", "500", "1k", "2k", "5k", "10k", "20k"])
plt.tight_layout(); plt.savefig(plotname, dpi=110)
print("plot:", plotname)
if a.tol is not None:
    ok = worst[0] <= a.tol
    print(f"{'PASS' if ok else 'FAIL'}: largest deviation {worst[0]:.2f} dB at {worst[1]:.1f} Hz ({worst[2]}), tolerance {a.tol} dB in {a.band[0]:.0f}-{a.band[1]:.0f} Hz")
    sys.exit(0 if ok else 1)

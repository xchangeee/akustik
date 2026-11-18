"""Close-up woofer/port: tuning frequency, L vs R. 0 deg cal. Usage: closeup.py <repo> <out>"""
import sys, os, glob, re, numpy as np
from scipy.io import wavfile
from scipy.signal import find_peaks
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
repo, out = sys.argv[1], sys.argv[2]
T0, SR, NFFT = 256, 48000, 1 << 18
cal = np.loadtxt(os.path.join(repo, "cal", "MM-1C_0deg.txt"), comments="*")
fq = np.fft.rfftfreq(NFFT, 1 / SR)
calc = np.interp(np.log10(np.maximum(fq, 1)), np.log10(cal[:, 0]), cal[:, 1])
def spec(f, right_ms):
    sr, x = wavfile.read(f); x = x.astype(float)
    n_end = T0 + int(right_ms / 1000 * SR); x = np.pad(x, (0, max(0, n_end - len(x))))[:n_end]
    fade = int(0.25 * right_ms / 1000 * SR); x[-fade:] *= 0.5 * (1 + np.cos(np.linspace(0, np.pi, fade)))
    return np.fft.rfft(x, NFFT)
def db(H): return 20 * np.log10(np.abs(H) + 1e-20) - calc
def smooth(d, frac):
    grid = np.geomspace(10, 5000, 900); p = 10 ** (d / 10); cs = np.concatenate([[0], np.cumsum(p)])
    lo = np.searchsorted(fq, grid * 2 ** (-0.5 / frac)); hi = np.maximum(np.searchsorted(fq, grid * 2 ** (0.5 / frac)), lo + 1)
    return grid, 10 * np.log10((cs[hi] - cs[lo]) / (hi - lo))
files = {}
for f in glob.glob(os.path.join(repo, "measurements", "2026-11-18-woofer-port-sweeps-L-R", "*.wav")):
    m = re.search(r"\d ([LR]) close up (\w+) ", os.path.basename(f)); files[(m.group(1), m.group(2))] = f
at = lambda g, y, f0: np.interp(np.log10(f0), np.log10(g), y)
fig, axs = plt.subplots(2, 1, figsize=(12, 9))
cur = {}
for spk in "LR":
    for part in ("woofer", "port"):
        for win in (500, 50):
            cur[(spk, part, win)] = smooth(db(spec(files[(spk, part)], win)), 24)
g = cur[("L", "woofer", 500)][0]
# normalise everything to L woofer 200-500 Hz mean
band = (g > 200) & (g < 500)
REF = cur[("L", "woofer", 500)][1][band].mean()
for spk in "LR":
    gw, w = cur[(spk, "woofer", 500)]; gp, p = cur[(spk, "port", 500)]
    w = w - REF; p = p - REF
    sel = (g > 20) & (g < 80)
    i_notch = np.argmin(w[sel]); i_peak = np.argmax(p[sel])
    print(f"{spk}: woofer notch {g[sel][i_notch]:.1f} Hz ({w[sel][i_notch]:+.1f} dB), port peak {g[sel][i_peak]:.1f} Hz ({p[sel][i_peak]:+.1f} dB)")
    print(f"   woofer 200-500 Hz level rel. L woofer: {w[band].mean():+.2f} dB;  1 kHz {at(g,w,1000):+.1f}, 100 Hz {at(g,w,100):+.1f}, 60 Hz {at(g,w,60):+.1f}")
    print(f"   port: level rel. woofer-ref at 30/40/50/60/80/100/200/300/500/800 Hz: " + " ".join(f"{at(g,p,f0):+.1f}" for f0 in (30,40,50,60,80,100,200,300,500,800)))
    pk, pr = find_peaks(p[(g > 100) & (g < 2000)], prominence=6)
    print("   port resonances (100-2000 Hz, prom>=6):", ", ".join(f"{g[(g>100)&(g<2000)][i]:.0f} Hz ({p[(g>100)&(g<2000)][i]:+.1f})" for i in pk))
    w50 = cur[(spk, "woofer", 50)][1] - REF; p50 = cur[(spk, "port", 50)][1] - REF
    print(f"   50 ms window check: notch {g[sel][np.argmin(w50[sel])]:.1f} Hz, port peak {g[sel][np.argmax(p50[sel])]:.1f} Hz")
gL = cur[("L", "woofer", 500)]; gR = cur[("R", "woofer", 500)]
diff = gR[1] - gL[1]
print("\nR woofer minus L woofer (dB):", " ".join(f"{f0}:{at(g,diff,f0):+.1f}" for f0 in (30, 40, 50, 60, 80, 100, 150, 200, 300, 500, 800, 1000, 2000)))
for ax, spk in zip(axs, "LR"):
    ax.semilogx(g, cur[(spk, "woofer", 500)][1] - REF, label="woofer close-up")
    ax.semilogx(g, cur[(spk, "port", 500)][1] - REF, label="port close-up")
    ax.set_xlim(15, 3000); ax.set_ylim(-50, 15); ax.grid(True, which="both", alpha=0.3); ax.legend()
    ax.set_title(f"{spk}: close-ups (1/24 oct, 0° cal), relative to L woofer 200-500 Hz")
    ax.set_xticks([20, 30, 40, 50, 60, 80, 100, 200, 300, 500, 1000, 2000]); ax.set_xticklabels([20, 30, 40, 50, 60, 80, 100, 200, 300, 500, "1k", "2k"])
plt.tight_layout(); plt.savefig(os.path.join(out, "closeups.png"), dpi=110)

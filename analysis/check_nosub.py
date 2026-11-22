"""Sub-out-of-the-room test (2026-11-22, set nosub-seat) and the P02 routing question.

Usage: check_nosub.py <repo> <out_dir>

Compares at the main seat, L speaker:
  eq1   = eq-seat '1 L seat eq1'        (P02, Sub8 at spot C, switched on, connected to DSP Out 3)
  eq2   = eq-seat '1 L seat eq2'        (P03, same sub state)
  nosub = nosub-seat '1 L seat eq1 nosub' (P02, Sub8 out of the room)
  flat  = 2026-11-18 L seat (sub under the table, switched off), also x v1 filters (= simulated eq1)
User, 2026-11-22: P02's routing had In A -> Out 3, so the sub may have played along on the L sweeps.
If it did, eq1 - nosub (complex, same mic spot, same loopback timing) is the sub's own sound: late (spot C is
farther), only below the sub's 130 Hz low-pass. eq2 is converted to v1 by H_v1/H_v2 so it can be compared too.
"""
import sys, os, glob
import numpy as np
from scipy.io import wavfile
from scipy.signal import butter, sosfreqz, sosfiltfilt, resample
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
import re

repo, out = sys.argv[1], sys.argv[2]
T0, SR, NFFT = 256, 48000, 1 << 18
M = os.path.join(repo, "measurements")
F = {
    "eq1": glob.glob(os.path.join(M, "2026-11-22", "eq-seat", "1 L seat eq1*.wav"))[0],
    "eq2": glob.glob(os.path.join(M, "2026-11-22", "eq-seat", "1 L seat eq2*.wav"))[0],
    "nosub": glob.glob(os.path.join(M, "2026-11-22", "nosub-seat", "1 L seat eq1 nosub*.wav"))[0],
    "flat": glob.glob(os.path.join(M, "2026-11-18", "seat", "1 first sweep*.wav"))[0],
}
X = {k: wavfile.read(f)[1].astype(float) for k, f in F.items()}
for k, f in F.items(): print(f"{k:6} {os.path.relpath(f, repo)}")
fq = np.fft.rfftfreq(NFFT, 1 / SR); z = np.exp(-1j * 2 * np.pi * fq / SR)


def read_eq(ver):
    txt = open(os.path.join(repo, "eq", ver, "L.txt")).read()
    bands = [(float(f), float(g), float(q)) for f, g, q in
             re.findall(r"ON\s+PK\s+Fc\s+([\d.]+)\s*Hz\s+Gain\s+([-\d.]+)\s*dB\s+Q\s+([\d.]+)", txt)]
    hp = float(re.search(r"Butterworth 24 dB/oct ([\d.]+) Hz", txt).group(1))
    H = sosfreqz(butter(4, hp, btype="high", fs=SR, output="sos"), worN=fq, fs=SR)[1]
    for fc, g, q in bands:
        A = 10 ** (g / 40); w = 2 * np.pi * fc / SR; al = np.sin(w) / (2 * q); c = np.cos(w)
        H = H * ((1 + al * A) - 2 * c * z + (1 - al * A) * z ** 2) / ((1 + al / A) - 2 * c * z + (1 - al / A) * z ** 2)
    return H


Hv1, Hv2 = read_eq("v1-flat"), read_eq("v2-harman")


def spec(x, start=T0, ms=500):
    n = start + int(ms / 1000 * SR); x = np.pad(x, (0, max(0, n - len(x))))[start:n].copy()
    fade = len(x) // 4; x[-fade:] *= 0.5 * (1 + np.cos(np.linspace(0, np.pi, fade)))
    return np.fft.rfft(x, NFFT)


GRID = np.geomspace(15, 2000, 900)


def sm(H, frac=24):
    cs = np.concatenate([[0], np.cumsum(np.abs(H) ** 2)])
    lo = np.searchsorted(fq, GRID * 2 ** (-0.5 / frac)); hi = np.maximum(np.searchsorted(fq, GRID * 2 ** (0.5 / frac)), lo + 1)
    return 10 * np.log10((cs[hi] - cs[lo]) / (hi - lo) + 1e-30)


S = {k: spec(x) for k, x in X.items()}
RATIO = np.where(np.abs(Hv2) > 1e-9, Hv1 / np.where(np.abs(Hv2) > 1e-9, Hv2, 1), 1)   # HPF: 0/0 at DC
S["eq2->v1"] = S["eq2"] * RATIO
S["flat x v1"] = S["flat"] * Hv1
REF = (GRID > 300) & (GRID < 2000)
D = {k: sm(v) for k, v in S.items()}
ref = D["nosub"][REF].mean()
D = {k: v - ref for k, v in D.items()}          # all on the nosub mid level (EQ doesn't touch the mids)

# ---- 1. placement and level ----
sos_hp = butter(4, 1000, btype="high", fs=SR, output="sos")
def first_arrival(x):
    h = np.abs(sosfiltfilt(sos_hp, x)); return (np.argmax(h > 0.3 * h.max()) - T0)
print("\n=== 1. Mic placement / gain: direct sound arrival (samples after t0, 30 % of HP peak) and mid level ===")
for k in ("eq1", "eq2", "nosub", "flat"):
    print(f"   {k:6} arrival {first_arrival(X[k]):4d} samples ({first_arrival(X[k]) / SR * 1000:5.2f} ms)   "
          f"mid 300 Hz-2 kHz {sm(S[k])[REF].mean() - sm(S['nosub'])[REF].mean():+5.2f} dB re nosub")

# ---- 2. spectra ----
print("\n=== 2. L seat, 1/24 oct, dB re nosub's 300 Hz-2 kHz level ===")
cols = ["nosub", "eq1", "eq2->v1", "flat x v1", "flat"]
print(f"{'Hz':>6} | " + " ".join(f"{c:>9}" for c in cols) + f" | {'eq1-nosub':>9} {'eq2v1-nos':>9}")
for f0 in [25, 28, 30, 33, 36, 40, 43, 47, 51, 55, 60, 65, 70, 75, 77, 78, 80, 85, 90, 95, 100, 110, 120, 130, 150, 175, 200, 250, 300]:
    v = [np.interp(np.log10(f0), np.log10(GRID), D[c]) for c in cols]
    print(f"{f0:6} | " + " ".join(f"{x:+9.1f}" for x in v) + f" | {v[1] - v[0]:+9.1f} {v[2] - v[0]:+9.1f}")
for a, b in ((25, 40), (40, 80), (80, 130), (130, 300), (300, 2000)):
    sel = (GRID >= a) & (GRID < b)
    for k in ("eq1", "eq2->v1", "flat x v1"):
        d = D[k][sel] - D["nosub"][sel]
        print(f"   {a:>4}-{b:<4} Hz  {k:9} - nosub: mean {d.mean():+5.2f}  rms {np.sqrt(np.mean(d ** 2)):4.2f} dB")

# ---- 3. difference IR ----
sos_lp = butter(4, 200, btype="low", fs=SR, output="sos")
n = min(len(X["eq1"]), len(X["nosub"]))
diff = {k: sosfiltfilt(sos_lp, X[k][:n] - X["nosub"][:n]) for k in ("eq1",)}
d2 = np.fft.irfft(S["eq2->v1"] - S["nosub"], NFFT)[:n]   # 500 ms windowed, starts at t0
diff["eq2->v1"] = np.concatenate([np.zeros(T0), sosfiltfilt(sos_lp, d2)])[:n]
ref_lp = sosfiltfilt(sos_lp, X["nosub"][:n])
print("\n=== 3. Difference IR (low-passed 200 Hz) vs the nosub IR (same low-pass) ===")
print("energy in windows after t0, dB re nosub's total low-passed energy 0-500 ms")
E0 = np.sum(ref_lp[T0:T0 + int(0.5 * SR)] ** 2)
for lab, y in (("nosub", ref_lp), ("eq1 - nosub", diff["eq1"]), ("eq2->v1 - nosub", diff["eq2->v1"])):
    row = []
    for a, b in ((0, 5), (5, 10), (10, 15), (15, 20), (20, 30), (30, 50), (50, 100), (100, 300)):
        row.append(10 * np.log10(np.sum(y[T0 + int(a / 1000 * SR):T0 + int(b / 1000 * SR)] ** 2) / E0 + 1e-30))
    print(f"   {lab:16} " + " ".join(f"{a}-{b}ms {v:6.1f}" for (a, b), v in zip(((0, 5), (5, 10), (10, 15), (15, 20), (20, 30), (30, 50), (50, 100), (100, 300)), row)))
env = np.abs(diff["eq1"][T0:T0 + int(0.1 * SR)])
on = np.argmax(env > 0.3 * env.max())
print(f"   eq1 - nosub: first reaches 30 % of its peak at {on / SR * 1000:.2f} ms after t0 (L direct sound at "
      f"{first_arrival(X['nosub']) / SR * 1000:.2f} ms); peak at {np.argmax(env) / SR * 1000:.2f} ms")

# ---- 4. the 78 Hz component ----
def late(x, f0, t1=0.3, t2=1.0, bw=1 / 24):
    y = sosfiltfilt(butter(2, [f0 * 2 ** (-bw / 2), f0 * 2 ** (bw / 2)], btype="band", fs=SR, output="sos"), x)[T0:]
    e = y ** 2; return 10 * np.log10(e[int(t1 * SR):int(t2 * SR)].sum() / e[:int(0.3 * SR)].sum() + 1e-30)
print("\n=== 4. Late energy (0.3-1.0 s) vs early (0-0.3 s), 1/24-oct band, per file ===")
for f0 in (62, 70, 77.8, 80.1, 85):
    print(f"   {f0:5.1f} Hz: " + "  ".join(f"{k} {late(X[k], f0):6.1f}" for k in ("nosub", "eq1", "eq2", "flat")))
N = 1 << 20; FL = np.fft.rfftfreq(N, 1 / SR)
for k in ("nosub", "eq1", "eq2", "flat"):
    seg = X[k][T0 + int(0.3 * SR):T0 + int(1.0 * SR)]; seg = seg * np.hanning(len(seg))
    d = 20 * np.log10(np.abs(np.fft.rfft(seg, N)) + 1e-30); sel = (FL > 60) & (FL < 100)
    print(f"   {k:6} late spectrum 60-100 Hz: peak at {FL[sel][np.argmax(d[sel])]:.2f} Hz, {d[sel].max() - np.median(d[sel]):+.1f} dB over median")

# ---- 5. did the sub play along on the eq1 sweeps? all spots, L vs R ----
print("\n=== 5. Residual eq1 - eq2 x (H_v1 / H_v2), every eq-* spot, low-passed 200 Hz, 0-300 ms ===")
print("eq1 and eq2 were swept at the same mic spot; converting eq2 by the filter ratio should give eq1 exactly. A sub")
print("playing only on the P02 L sweeps leaves its sound in the L residual. R is the control (In B never went to Out 3).")
print("dB re the eq1 IR's own low-passed energy; also the residual's 30 % onset (ms after t0) vs the speaker's direct sound.")
def ratio(s):
    a, b = read_eq_s("v1-flat", s), read_eq_s("v2-harman", s)
    return np.where(np.abs(b) > 1e-9, a / np.where(np.abs(b) > 1e-9, b, 1), 1)
def read_eq_s(ver, s):
    txt = open(os.path.join(repo, "eq", ver, f"{s}.txt")).read()
    bands = [(float(f), float(g), float(q)) for f, g, q in
             re.findall(r"ON\s+PK\s+Fc\s+([\d.]+)\s*Hz\s+Gain\s+([-\d.]+)\s*dB\s+Q\s+([\d.]+)", txt)]
    hp = float(re.search(r"Butterworth 24 dB/oct ([\d.]+) Hz", txt).group(1))
    H = sosfreqz(butter(4, hp, btype="high", fs=SR, output="sos"), worN=fq, fs=SR)[1]
    for fc, g, q in bands:
        A = 10 ** (g / 40); w = 2 * np.pi * fc / SR; al = np.sin(w) / (2 * q); c = np.cos(w)
        H = H * ((1 + al * A) - 2 * c * z + (1 - al * A) * z ** 2) / ((1 + al / A) - 2 * c * z + (1 - al / A) * z ** 2)
    return H
RAT = {s: ratio(s) for s in "LR"}
LP = np.abs(sosfreqz(butter(8, 200, btype="low", fs=SR, output="sos"), worN=fq, fs=SR)[1])
W = int(0.3 * SR)
rows = []
for setname in ("eq-seat", "eq-corners", "eq-dj"):
    fs1 = sorted(glob.glob(os.path.join(M, "2026-11-22", setname, "* eq1*.wav")))
    for f1 in fs1:
        f2 = f1.replace(" eq1", " eq2"); s = os.path.basename(f1).split()[1]
        x1, x2 = wavfile.read(f1)[1].astype(float), wavfile.read(f2)[1].astype(float)
        H1, H2 = spec(x1, ms=1000), spec(x2, ms=1000)
        r = np.fft.irfft((H1 - H2 * RAT[s]) * LP, NFFT)[:W]; e = np.fft.irfft(H1 * LP, NFFT)[:W]
        lev = 10 * np.log10(np.sum(r ** 2) / np.sum(e ** 2))
        ra = np.abs(r); on = np.argmax(ra > 0.3 * ra.max()) / SR * 1000
        rows.append((setname, os.path.basename(f1).replace(" eq1", "").replace(" Nov 22", "").replace(".wav", ""), s, lev, on, first_arrival(x1) / SR * 1000))
for setname, name, s, lev, on, da in rows:
    print(f"   {setname:10} {name:28} residual {lev:6.1f} dB   onset {on:6.1f} ms (direct {da:5.1f} ms)")
for setname in ("eq-seat", "eq-corners", "eq-dj"):
    for s in "LR":
        v = [r[3] for r in rows if r[0] == setname and r[2] == s]
        print(f"   {setname:10} {s}: median residual {np.median(v):6.1f} dB  (range {min(v):.1f} .. {max(v):.1f})")

# ---- 6. the narrow line in every measurement ----
print("\n=== 6. Narrow late line 70-90 Hz in every IR: peak of the late spectrum (0.3-1.0 s, Hann, 0.07 Hz bins) ===")
print("prominence = peak over the median of 60-100 Hz (dB); lev = peak re the IR's early 60-100 Hz level (0-0.3 s)")
def late_line(x):
    seg = x[T0 + int(0.3 * SR):T0 + int(1.0 * SR)]; seg = seg * np.hanning(len(seg))
    d = 20 * np.log10(np.abs(np.fft.rfft(seg, N)) + 1e-30)
    e0 = x[T0:T0 + int(0.3 * SR)] * np.hanning(int(0.3 * SR)); de = 20 * np.log10(np.abs(np.fft.rfft(e0, N)) + 1e-30)
    w = (FL > 60) & (FL < 100); sel = (FL > 70) & (FL < 90); i = np.argmax(d[sel])
    return FL[sel][i], d[sel][i] - np.median(d[w]), d[sel][i] - np.median(de[w])
for folder in sorted(glob.glob(os.path.join(M, "*", "*"))):
    wavs = sorted(glob.glob(os.path.join(folder, "*.wav")))
    if not wavs or "electrical" in folder: continue
    print(f"-- {os.path.relpath(folder, M)}")
    for f in wavs:
        fr, pr, lv = late_line(wavfile.read(f)[1].astype(float))
        print(f"   {os.path.basename(f)[:40]:40} {fr:6.2f} Hz  prominence {pr:+5.1f}  lev {lv:+6.1f}")

# ---- plot ----
fig, axs = plt.subplots(2, 1, figsize=(12, 9))
ax = axs[0]
for k, c, ls in (("flat", "grey", "-"), ("flat x v1", "tab:orange", "--"), ("eq1", "k", "-"), ("eq2->v1", "tab:blue", ":"), ("nosub", "tab:red", "-")):
    ax.semilogx(GRID, D[k], color=c, ls=ls, lw=1.6 if k in ("eq1", "nosub") else 1.1,
                label={"flat": "flat 11-18 (sub off, under table)", "flat x v1": "simulated v1 (flat 11-18 x v1)",
                       "eq1": "v1 measured, sub at C (P02)", "eq2->v1": "v2 measured, sub at C, converted to v1",
                       "nosub": "v1 measured, sub out of the room"}[k])
ax.set_xlim(18, 1000); ax.set_ylim(-30, 20); ax.grid(True, which="both", alpha=0.3); ax.legend(fontsize=8)
ax.set_title("L at the main seat, 1/24 oct, 0 dB = nosub 300 Hz-2 kHz"); ax.set_ylabel("dB")
ax = axs[1]
t = (np.arange(n) - T0) / SR * 1000
ax.plot(t, ref_lp, color="tab:red", lw=0.8, label="nosub IR, low-passed 200 Hz")
ax.plot(t, diff["eq1"], color="k", lw=0.8, label="eq1 - nosub (sub at C playing?), low-passed 200 Hz")
ax.set_xlim(-2, 120); ax.grid(True, alpha=0.3); ax.legend(fontsize=8); ax.set_xlabel("ms after t0")
ax.set_title("Difference IR: what the sub-at-C sweep has that the sub-out sweep hasn't")
plt.tight_layout(); plt.savefig(os.path.join(out, "nosub.png"), dpi=100)
print("\nplot:", os.path.join(out, "nosub.png"))

"""EQ v1 / v2 in the room (2026-11-22 sets eq-seat, eq-dj, eq-corners) vs 2026-11-18 flat and vs the simulation.

Usage: analyse_eq_room.py <repo> <out_dir>

Data: v1 (P02, tag eq1) and v2 (P03, tag eq2) measured interleaved at each mic spot (mic not moved between them).
Baseline: the 2026-11-18 flat sets at the same position names (seat + 6 positions, DJ 7, corners 2).

1. Mic placement vs 2026-11-18: arrival delay of each IR (cross-correlation of the first 10 ms, high-passed at
   1 kHz, 16x upsampled) against the baseline IR of the same speaker and position, in samples and cm (343 m/s).
   Two speakers give two distances, so this shows how far the mic moved along the L and R lines of sight.
2. Room response: measured v1/v2 vs simulated = 2026-11-18 IR x (HPF + PEQ from eq/<version>/, complex), and vs
   the target (v1 flat, v2 RBJ low shelf +6 dB 105 Hz Q 0.707, as in design_eq.py). Each curve relative to its own
   300 Hz-3 kHz level (the EQ doesn't touch it). Power average over the positions of a set; L+R = coherent sum
   of the L and R IRs (same loopback timing). Same processing as design_eq.py (500 ms window, 90 deg mic cal).
3. v2 - v1 measured at the same spot vs predicted (H_v2 / H_v1): independent of mic placement and of room changes
   since 2026-11-18, so it checks that the DSP filters act in the room as designed.
4. Decay: Schroeder T(-5..-25 dB) in 1/6-oct bands at the modes, seat (7 positions) and DJ (7), flat vs v1 vs v2;
   waterfall (CSD) at the main seat.
"""
import sys, os, glob, re
import numpy as np
from scipy.io import wavfile
from scipy.signal import butter, sosfreqz, sosfiltfilt, resample
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt

repo, out = sys.argv[1], sys.argv[2]
T0, SR, NFFT, OFFSET = 256, 48000, 1 << 18, 100.9
C_MS = 34.3                             # cm per ms
VERS = {"eq1": "v1-flat", "eq2": "v2-harman"}
NAME = {"flat": "flat 11-18", "eq1": "v1", "eq2": "v2"}
SHELF = dict(gain=6.0, f0=105.0, q=0.707)

cal = np.loadtxt(os.path.join(repo, "reference", "mic-cal", "MM-1C_90deg.txt"), comments="*")
fq = np.fft.rfftfreq(NFFT, 1 / SR)
calc = np.interp(np.log10(np.maximum(fq, 1)), np.log10(cal[:, 0]), cal[:, 1])
z = np.exp(-1j * 2 * np.pi * fq / SR)


def load(f):
    sr, x = wavfile.read(f); assert sr == SR, f
    return x.astype(float)


def spec(x, start=T0, right_ms=500):
    n_end = start + int(right_ms / 1000 * SR); x = np.pad(x, (0, max(0, n_end - len(x))))[start:n_end].copy()
    fade = len(x) // 4; x[-fade:] *= 0.5 * (1 + np.cos(np.linspace(0, np.pi, fade)))
    return np.fft.rfft(x, NFFT) * 10 ** (-calc / 20)


GRID = np.geomspace(15, 20000, 1400)


def smooth(H, frac):
    """fractional-octave power smoothing of |H|^2 on GRID (linear power)"""
    cs = np.concatenate([[0], np.cumsum(np.abs(H) ** 2)])
    lo = np.searchsorted(fq, GRID * 2 ** (-0.5 / frac)); hi = np.maximum(np.searchsorted(fq, GRID * 2 ** (0.5 / frac)), lo + 1)
    return (cs[hi] - cs[lo]) / (hi - lo)


def avg_db(Hs, frac):
    return 10 * np.log10(np.mean([smooth(H, frac) for H in Hs], axis=0)) + OFFSET


def at(y, f0): return np.interp(np.log10(f0), np.log10(GRID), y)


# ---------- filters ----------
def read_eq(ver, s):
    txt = open(os.path.join(repo, "eq", ver, f"{s}.txt")).read()
    bands = [(float(f), float(g), float(q)) for f, g, q in
             re.findall(r"ON\s+PK\s+Fc\s+([\d.]+)\s*Hz\s+Gain\s+([-\d.]+)\s*dB\s+Q\s+([\d.]+)", txt)]
    hp = float(re.search(r"Butterworth 24 dB/oct ([\d.]+) Hz", txt).group(1))
    return bands, hp


def eq_H(ver, s):
    bands, hp = read_eq(ver, s)
    H = sosfreqz(butter(4, hp, btype="high", fs=SR, output="sos"), worN=fq, fs=SR)[1]
    for fc, g, q in bands:
        A = 10 ** (g / 40); w = 2 * np.pi * fc / SR; al = np.sin(w) / (2 * q); c = np.cos(w)
        H = H * ((1 + al * A) - 2 * c * z + (1 - al * A) * z ** 2) / ((1 + al / A) - 2 * c * z + (1 - al / A) * z ** 2)
    return H


def low_shelf_db(f, gain, f0, q):
    A = 10 ** (gain / 40); w = 2 * np.pi * f0 / SR; al = np.sin(w) / (2 * q); c = np.cos(w); sA = 2 * np.sqrt(A) * al
    b = [A * ((A + 1) - (A - 1) * c + sA), 2 * A * ((A - 1) - (A + 1) * c), A * ((A + 1) - (A - 1) * c - sA)]
    a = [(A + 1) + (A - 1) * c + sA, -2 * ((A - 1) + (A + 1) * c), (A + 1) + (A - 1) * c - sA]
    zz = np.exp(-1j * 2 * np.pi * np.asarray(f) / SR)
    return 20 * np.log10(np.abs((b[0] + b[1] * zz + b[2] * zz ** 2) / (a[0] + a[1] * zz + a[2] * zz ** 2)))


EQH = {(t, s): eq_H(v, s) for t, v in VERS.items() for s in "LR"}
TARGET = {"flat": np.zeros_like(GRID), "eq1": np.zeros_like(GRID), "eq2": low_shelf_db(GRID, **SHELF)}


# ---------- files ----------
def files(folder, pat, tagged):
    d = {}
    for f in glob.glob(os.path.join(repo, "measurements", folder, "*.wav")):
        m = re.search(pat, os.path.basename(f))
        if m:
            tag = m.group(3) if tagged else "flat"
            d.setdefault(m.group(2), {})[(tag, m.group(1))] = f
    return d


SETS = {}
base_seat = files("2026-11-18/positions", r"^\d ([LR]) (pos\d \w+) ", False)
base_seat["seat"] = {("flat", "L" if "left" in f else "R"): f
                     for f in glob.glob(os.path.join(repo, "measurements", "2026-11-18", "seat", "*first sweep*.wav"))}
SETS["seat"] = (base_seat, files("2026-11-22/eq-seat", r"^\d ([LR]) (seat|pos\d \w+) (eq[12])\b", True))
SETS["dj"] = (files("2026-11-18/dj", r"^\d ([LR]) DJ (\w+) ", False),
              files("2026-11-22/eq-dj", r"^\d ([LR]) DJ (\w+) (eq[12])\b", True))
SETS["corners"] = (files("2026-11-18/corners", r"^\d ([LR]) corner front (\w+) ", False),
                   files("2026-11-22/eq-corners", r"^\d ([LR]) corner front (\w+) (eq[12])\b", True))
POS = {}
for k, (b, n) in SETS.items():
    assert sorted(b) == sorted(n), (k, sorted(b), sorted(n))
    for p in n: assert len(b[p]) == 2 and len(n[p]) == 4, (k, p)
    POS[k] = sorted(n, key=lambda p: (p not in ("seat", "pos"), p))
    print(f"{k}: {len(POS[k])} positions: {', '.join(POS[k])}")
X = {}
for k, (b, n) in SETS.items():
    for p in POS[k]:
        for key, f in list(b[p].items()) + list(n[p].items()):
            X[(k, p) + key] = load(f)

# ---------- 0. noise check ----------
def tail_db(x): return 10 * np.log10(np.mean(x[-int(0.3 * SR):] ** 2) + 1e-30)


TAIL = {key: tail_db(x) for key, x in X.items()}
MED = np.median(list(TAIL.values()))
NOISY = {key for key, v in TAIL.items() if v > MED + 4}
print(f"\n=== 0. Noise check: IR tail level (last 0.3 s), median of all {len(TAIL)} IRs {MED:.1f} dBFS ===")
print("IRs more than 4 dB above the median (disturbed sweep; left out of section 4):")
for key in sorted(NOISY): print(f"   {' '.join(key)}: {TAIL[key]:.1f} dBFS ({TAIL[key] - MED:+.1f})")
if not NOISY: print("   none")

# ---------- 1. mic placement ----------
sos_hp = butter(4, 1000, btype="high", fs=SR, output="sos")


def onset(y, thr=0.3):
    e = np.abs(y); return int(np.argmax(e > thr * e.max()))


def delay_vs(x, ref, up=16, max_ms=1.5):
    """delay of x relative to ref in samples (positive = x arrives later), and the normalised correlation.
    Window: first arrival (30 % of the high-passed peak) -1 ms .. +3 ms; lag search +-max_ms."""
    hx, hr = sosfiltfilt(sos_hp, x), sosfiltfilt(sos_hp, ref)
    i0 = min(onset(hx), onset(hr)) - int(0.001 * SR) - int(max_ms / 1000 * SR); n = int((0.004 + 2 * max_ms / 1000) * SR)
    a, r = resample(hx[i0:i0 + n], n * up), resample(hr[i0:i0 + n], n * up)
    w = np.zeros_like(r); c0 = int(max_ms / 1000 * SR) * up; w[c0:c0 + int(0.004 * SR) * up] = 1; r = r * w
    cc = np.fft.irfft(np.fft.rfft(a, 2 * len(a)) * np.conj(np.fft.rfft(r, 2 * len(a))))
    lags = np.fft.fftfreq(len(cc), 1 / len(cc)).astype(int)
    ok = np.abs(lags) <= c0
    i = np.argmax(np.where(ok, cc, -np.inf))
    seg_a = a[c0 + lags[i]:c0 + lags[i] + int(0.004 * SR) * up]
    rho = cc[i] / np.sqrt(np.sum(seg_a ** 2) * np.sum(r ** 2) + 1e-30)
    return lags[i] / up, rho


print("\n=== 1. Mic placement vs 2026-11-18: arrival delay difference (samples at 48 kHz; cm at 343 m/s) ===")
print("positive = farther from that speaker than on 11-18. eq2-eq1 = mic/timing drift between the two sweeps of a spot.")
print("rho = normalised correlation of the first arrival with 11-18 (below ~0.8 the direct sound is too weak or changed: value unreliable).")
print(f"{'set':8} {'position':13} | {'L eq1':>6} {'cm':>5} {'rho':>4} | {'R eq1':>6} {'cm':>5} {'rho':>4} | {'L eq2-eq1':>9} {'R eq2-eq1':>9}")
DEL = {}
for k in SETS:
    for p in POS[k]:
        r = {}
        for s in "LR":
            r[s], r[s + "rho"] = delay_vs(X[(k, p, "eq1", s)], X[(k, p, "flat", s)])
            r[s + "2"], _ = delay_vs(X[(k, p, "eq2", s)], X[(k, p, "eq1", s)])
        DEL[(k, p)] = r
        print(f"{k:8} {p:13} | {r['L']:+6.2f} {r['L'] / SR * 1000 * C_MS:+5.1f} {r['Lrho']:4.2f} |"
              f" {r['R']:+6.2f} {r['R'] / SR * 1000 * C_MS:+5.1f} {r['Rrho']:4.2f} | {r['L2']:+9.2f} {r['R2']:+9.2f}")

# ---------- 2. room response ----------
H = {key: spec(x) for key, x in X.items()}


def curves(k, tag, sim=False, frac=24):
    """{'L','R','L+R': dB on GRID} power average over the set's positions; sim = 11-18 flat x filter"""
    L, R = [], []
    for p in POS[k]:
        if sim:
            L.append(H[(k, p, "flat", "L")] * EQH[(tag, "L")]); R.append(H[(k, p, "flat", "R")] * EQH[(tag, "R")])
        else:
            L.append(H[(k, p, tag, "L")]); R.append(H[(k, p, tag, "R")])
    return {"L": avg_db(L, frac), "R": avg_db(R, frac), "L+R": avg_db([a + b for a, b in zip(L, R)], frac)}


REFB = (GRID > 300) & (GRID < 3000)
RES = {}
for frac in (6, 24):
    for k in SETS:
        for tag in ("flat", "eq1", "eq2"):
            RES[(k, tag, "meas", frac)] = curves(k, tag, frac=frac)
        for tag in ("eq1", "eq2"):
            RES[(k, tag, "sim", frac)] = curves(k, tag, sim=True, frac=frac)
ABS = {key: {w: c[REFB].mean() for w, c in v.items()} for key, v in RES.items()}
REL = {key: {w: c - ABS[key][w] for w, c in v.items()} for key, v in RES.items()}

print("\n=== 2a. Mid level 300 Hz-3 kHz (dB SPL approx, 1/6 oct) - the EQ doesn't touch it ===")
print(f"{'set':8} | {'flat L':>6} {'v1 L':>6} {'v2 L':>6} | {'flat R':>6} {'v1 R':>6} {'v2 R':>6} | {'flat L+R':>8} {'v1 L+R':>7} {'v2 L+R':>7}")
for k in SETS:
    row = []
    for w in ("L", "R", "L+R"):
        row += [ABS[(k, t, "meas", 6)][w] for t in ("flat", "eq1", "eq2")]
    print(f"{k:8} | " + " ".join(f"{v:6.1f}" for v in row[:3]) + " | " + " ".join(f"{v:6.1f}" for v in row[3:6])
          + " | " + f"{row[6]:8.1f} {row[7]:7.1f} {row[8]:7.1f}")

BANDS = [(25, 40), (40, 60), (60, 100), (100, 160), (160, 250), (25, 250)]
print("\n=== 2b. rms deviation, 1/24 oct, rel. to own mid level (dB) ===")
print("meas-sim: measured vs simulated from 11-18. meas-tgt / sim-tgt: vs the design target. flat-tgt: 11-18 without EQ vs the same target.")
for k in SETS:
    print(f"-- {k}")
    print(f"   {'':16}" + "".join(f"{f'{a}-{b} Hz':>11}" for a, b in BANDS))
    for tag in ("eq1", "eq2"):
        for w in ("L", "R", "L+R"):
            m, s_, fl, t = REL[(k, tag, "meas", 24)][w], REL[(k, tag, "sim", 24)][w], REL[(k, "flat", "meas", 24)][w], TARGET[tag]
            for lab, d in (("meas-sim", m - s_), ("meas-tgt", m - t), ("sim-tgt", s_ - t), ("flat-tgt", fl - t)):
                vals = [np.sqrt(np.mean(d[(GRID >= a) & (GRID < b)] ** 2)) for a, b in BANDS]
                print(f"   {NAME[tag]} {w:3} {lab:9}" + "".join(f"{v:11.2f}" for v in vals))

FREQS = [25, 28, 30, 35, 40, 43, 47, 51, 55, 60, 65, 70, 75, 80, 85, 90, 95, 100, 105, 110, 115, 120, 125, 130, 140,
         150, 175, 200, 250, 300]
for k in SETS:
    for w in ("L+R", "L", "R"):
        if k == "corners" and w != "L+R": continue
        print(f"\n=== 2c. {k} {w}: 1/6 oct rel. to own mid level (dB); targets v1 0, v2 low shelf ===")
        print(f"{'Hz':>5} | {'flat':>6} | {'v1 sim':>6} {'v1 meas':>7} {'diff':>5} | {'v2 sim':>6} {'v2 meas':>7} {'diff':>5} {'v2 tgt':>6}")
        for f0 in FREQS:
            fl = at(REL[(k, "flat", "meas", 6)][w], f0)
            s1, m1 = at(REL[(k, "eq1", "sim", 6)][w], f0), at(REL[(k, "eq1", "meas", 6)][w], f0)
            s2, m2 = at(REL[(k, "eq2", "sim", 6)][w], f0), at(REL[(k, "eq2", "meas", 6)][w], f0)
            print(f"{f0:5} | {fl:+6.1f} | {s1:+6.1f} {m1:+7.1f} {m1 - s1:+5.1f} | {s2:+6.1f} {m2:+7.1f} {m2 - s2:+5.1f} {at(TARGET['eq2'], f0):+6.1f}")

# bass energy, as heard: 30-150 Hz mean of the 1/6-oct curve, rel. to mid
print("\n=== 2d. Bass level: mean of the 1/6-oct curve rel. to mid (dB) ===")
print(f"{'set':8} {'which':5} | {'band':>10} | {'flat':>6} {'v1 sim':>6} {'v1 meas':>7} | {'v2 sim':>6} {'v2 meas':>7} {'v2 tgt':>6}")
for k in SETS:
    for w in ("L+R",) if k == "corners" else ("L+R", "L", "R"):
        for a, b in ((30, 60), (60, 150), (30, 150)):
            sel = (GRID >= a) & (GRID < b)
            v = [REL[(k, t, m, 6)][w][sel].mean() for t, m in (("flat", "meas"), ("eq1", "sim"), ("eq1", "meas"), ("eq2", "sim"), ("eq2", "meas"))]
            print(f"{k:8} {w:5} | {f'{a}-{b} Hz':>10} | {v[0]:+6.1f} {v[1]:+6.1f} {v[2]:+7.1f} | {v[3]:+6.1f} {v[4]:+7.1f} {TARGET['eq2'][sel].mean():+6.1f}")

# ---------- 3. v2 - v1 at the same spot ----------
print("\n=== 3. v2 - v1 measured at the same spot vs predicted filter difference, 1/24 oct per position, 28-300 Hz ===")
print("rms / max |measured - predicted| (dB) per position; predicted = |H_v2 / H_v1| smoothed the same way.")
print("Below 28 Hz (under the 29.8 Hz HPF, little signal) the difference is noise-dominated and left out.")
D = {}
sel = (GRID >= 28) & (GRID <= 300)
for s in "LR":
    pred = 10 * np.log10(smooth(EQH[("eq2", s)], 24) / smooth(EQH[("eq1", s)], 24))
    D[s] = (pred, [])
    errs = []
    for k in SETS:
        for p in POS[k]:
            d = 10 * np.log10(smooth(H[(k, p, "eq2", s)], 24) / smooth(H[(k, p, "eq1", s)], 24))
            D[s][1].append(d)
            e = (d - pred)[sel]; errs.append((k, p, np.sqrt(np.mean(e ** 2)), np.abs(e).max(), GRID[sel][np.argmax(np.abs(e))]))
    print(f"-- {s}")
    for k, p, rms, mx, fmx in errs:
        print(f"   {k:8} {p:13} rms {rms:4.2f}  max {mx:4.2f} at {fmx:5.1f} Hz")

# ---------- 4. decay ----------
def remaining(x, f, times_ms, n_oct=1 / 6):
    """band energy (1/6 oct around f, zero-phase) remaining after each t, linear, noise tail (last 0.3 s) removed"""
    y = sosfiltfilt(butter(4, [f * 2 ** (-n_oct / 2), f * 2 ** (n_oct / 2)], btype="band", fs=SR, output="sos"), x)[T0:]
    e = y ** 2; e = np.maximum(e - e[-int(0.3 * SR):].mean(), 0)
    sch = np.cumsum(e[::-1])[::-1]
    return np.array([sch[int(t / 1000 * SR)] for t in times_ms])


MODES = [29, 36, 43, 52, 57, 62, 70, 84, 89, 94, 114, 125]
TIMES = [0, 100, 200, 300]
print("\n=== 4. Ringing: band energy (1/6 oct) remaining after t, dB re flat 11-18 at t=0, power mean over positions ===")
print("Each EQ's curve on the same reference, so a notch that lowers a mode shows as lower numbers at every t.")
print("(Narrow-band decay *times* don't capture this: a cut mode keeps its pole, it just starts lower.)")
for k in ("seat", "dj"):
    for s in "LR":
        print(f"-- {k} {s}")
        print("   " + f"{'Hz':>14}" + "".join(f"{f:>6}" for f in MODES))
        ps = [p for p in POS[k] if not any((k, p, t, s) in NOISY for t in ("flat", "eq1", "eq2"))]
        if len(ps) < len(POS[k]): print(f"   (left out: {', '.join(p for p in POS[k] if p not in ps)}, disturbed sweep)")
        E = {tag: np.array([[remaining(X[(k, p, tag, s)], f, TIMES) for f in MODES] for p in ps]) for tag in ("flat", "eq1", "eq2")}
        ref = E["flat"][:, :, 0].mean(0)
        for ti, t in enumerate(TIMES):
            for tag in ("flat", "eq1", "eq2"):
                v = 10 * np.log10(E[tag][:, :, ti].mean(0) / ref + 1e-30)
                print(f"   {NAME[tag]:>9} {t:3}ms" + "".join(f"{x:6.1f}" for x in v))


print("\n=== 5. New narrow resonances: late part of the IR (0.3-1.0 s, Hann) vs early part (0-0.3 s) of the same position's")
print("flat 11-18 IR, 1/48 oct, 30-200 Hz. new = min(v1, v2) - flat. Listed: peaks where new > 6 dB at >= 70 % of positions")
print("(stronger late energy than 11-18 at that frequency. Caveat: a narrow line that only shifted in frequency")
print(" also shows here; check_nosub.py section 6 tracks the line itself across all IRs).")
NL = 1 << 20; FL = np.fft.rfftfreq(NL, 1 / SR)
SG = np.geomspace(30, 200, int(48 * np.log2(200 / 30)) + 1)
_l = np.searchsorted(FL, SG * 2 ** (-1 / 96)); _h = np.maximum(np.searchsorted(FL, SG * 2 ** (1 / 96)), _l + 1)


def part_db(x, t1, t2):
    seg = x[T0 + int(t1 * SR):T0 + int(t2 * SR)]; seg = seg * np.hanning(len(seg))
    cs = np.concatenate([[0], np.cumsum(np.abs(np.fft.rfft(seg, NL)) ** 2)])
    return 10 * np.log10((cs[_h] - cs[_l]) / (_h - _l) + 1e-30)


for k in ("seat", "dj"):
    for s in "LR":
        ps = [p for p in POS[k] if not any((k, p, t, s) in NOISY for t in ("flat", "eq1", "eq2"))]
        early = np.array([part_db(X[(k, p, "flat", s)], 0, 0.3) for p in ps])
        late = {t: np.array([part_db(X[(k, p, t, s)], 0.3, 1.0) for p in ps]) - early for t in ("flat", "eq1", "eq2")}
        new = np.minimum(late["eq1"], late["eq2"]) - late["flat"]
        cnt = (new > 6).sum(0)
        need = int(np.ceil(0.7 * len(ps)))   # single positions scatter +-10 dB where the late part is near the noise floor
        score = np.where(cnt >= need, np.median(new, axis=0), -np.inf)
        idx = [i for i in range(1, len(SG) - 1) if np.isfinite(score[i]) and score[i] >= score[i - 1] and score[i] >= score[i + 1]]
        print(f"-- {k} {s}: " + ("none" if not idx else ""))
        for i in idx:
            print(f"   {SG[i]:6.1f} Hz: {cnt[i]} of {len(ps)} positions; min(v1,v2) - flat per position: "
                  + ", ".join(f"{p} {new[j, i]:+.0f}" for j, p in enumerate(ps)))


def csd(x, times_ms, frac=24, win_ms=300):
    rows = []
    for t in times_ms:
        rows.append(10 * np.log10(smooth(spec(x, start=T0 + int(t / 1000 * SR), right_ms=win_ms), frac) + 1e-30))
    return np.array(rows)


# ---------- plots ----------
TICKS = [20, 30, 40, 50, 60, 80, 100, 150, 200, 300, 500, 1000]
def xfmt(ax, lo=18, hi=1000, grid=True):
    ax.set_xscale("log"); ax.set_xlim(lo, hi); ax.set_xticks([t for t in TICKS if lo <= t <= hi])
    ax.set_xticklabels([("1k" if t == 1000 else str(t)) for t in TICKS if lo <= t <= hi])
    ax.xaxis.set_minor_formatter(matplotlib.ticker.NullFormatter())
    if grid: ax.grid(True, which="both", alpha=0.3)


for tag in ("eq1", "eq2"):
    fig, axs = plt.subplots(3, 3, figsize=(17, 11), sharex=True)
    for i, k in enumerate(SETS):
        for j, w in enumerate(("L", "R", "L+R")):
            ax = axs[i, j]
            ax.plot(GRID, REL[(k, "flat", "meas", 24)][w], color="grey", lw=1, label="flat 11-18 (measured)")
            ax.plot(GRID, REL[(k, tag, "sim", 24)][w], color="tab:orange", lw=1.3, ls="--", label=f"{NAME[tag]} simulated (11-18 x filters)")
            ax.plot(GRID, REL[(k, tag, "meas", 24)][w], color="k", lw=1.8, label=f"{NAME[tag]} measured 11-22")
            ax.plot(GRID, TARGET[tag], color="tab:green", lw=1, ls=":", label="target")
            ax.set_ylim(-25, 20); xfmt(ax)
            ax.set_title(f"{k} {w} ({len(POS[k])} pos.), 1/24 oct, 0 = own 300 Hz-3 kHz", fontsize=9)
            if j == 0: ax.set_ylabel("dB")
    axs[0, 0].legend(fontsize=7, loc="lower right")
    for ax in axs[-1]: ax.set_xlabel("Hz")
    fig.suptitle(f"EQ {NAME[tag]} ({VERS[tag]}): measured in the room vs simulated vs target")
    plt.tight_layout(); plt.savefig(os.path.join(out, f"eq_room_{NAME[tag]}.png"), dpi=100); plt.close()

fig, axs = plt.subplots(1, 2, figsize=(15, 5.5), sharey=True)
for ax, s in zip(axs, "LR"):
    pred, ds = D[s]
    for d in ds: ax.plot(GRID, d, color="grey", lw=0.6, alpha=0.6)
    ax.plot(GRID, np.mean(ds, axis=0), "k", lw=1.6, label=f"measured v2 - v1, mean of {len(ds)} spots (grey: each)")
    ax.plot(GRID, pred, color="tab:orange", lw=1.3, ls="--", label="predicted (filter files)")
    xfmt(ax, 18, 1000); ax.set_ylim(-10, 14); ax.set_title(f"{s}: v2 - v1 at the same mic spot, 1/24 oct"); ax.set_xlabel("Hz")
axs[0].set_ylabel("dB"); axs[0].legend(fontsize=8)
plt.tight_layout(); plt.savefig(os.path.join(out, "eq_room_v2_minus_v1.png"), dpi=100); plt.close()

times = np.arange(0, 401, 10)
fig, axs = plt.subplots(3, 2, figsize=(14, 12), sharex=True, sharey=True, layout="constrained")
for j, s in enumerate("LR"):
    cs_ = {tag: csd(X[("seat", "seat", tag, s)], times) for tag in ("flat", "eq1", "eq2")}
    top = cs_["flat"][0][(GRID > 20) & (GRID < 300)].max()
    for i, tag in enumerate(("flat", "eq1", "eq2")):
        ax = axs[i, j]
        m = ax.pcolormesh(GRID, times, cs_[tag] - top, vmin=-45, vmax=0, cmap="magma", shading="auto")
        ax.set_title(f"main seat {s}, {NAME[tag]}", fontsize=10)
        xfmt(ax, 20, 300, grid=False)
        if j == 0: ax.set_ylabel("ms")
for ax in axs[-1]: ax.set_xlabel("Hz")
fig.colorbar(m, ax=axs, shrink=0.6, label="dB")
fig.suptitle("Waterfall at the main seat (300 ms window, 1/24 oct); 0 dB = flat's peak 20-300 Hz at t=0, per speaker")
plt.savefig(os.path.join(out, "eq_room_waterfall.png"), dpi=100); plt.close()
print("\nplots:", ", ".join(os.path.join(out, f) for f in ("eq_room_v1.png", "eq_room_v2.png", "eq_room_v2_minus_v1.png", "eq_room_waterfall.png")))

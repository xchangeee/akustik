"""Sub8 at spot C (2026-11-22 sets subC-seat, subC-dj, subC-corners) alone and summed with the mains.

Usage: analyse_sub_c.py <repo> <out_dir>

Data: sub-only sweeps (P04: In A -> Out 3 at -10 dB, mains muted; Sub8 gain 0 dB, LP 130 Hz, HP off, 0 deg) at the
same 16 mic positions as the eq-* sets of the same day (mains v1 = eq1 / P02, v2 = eq2 / P03, mic re-placed within
~5 cm, fine below ~120 Hz). All IRs share the loopback t=0, so mains and sub add as complex spectra.
Same processing as analyse_eq_room.py: 500 ms right window, 90 deg mic cal, absolute offset 100.9 dB.

1. Sub alone vs mains alone (L+R coherent sum), power averages per group (seat 7, DJ 7, corners 2), 1/6 oct.
2. Overlay design: sub through Out 3 LPF (DSP LR24 / BW24 at the device's 1/30-oct grid), polarity, relative delay
   (sub delay on Out 3 if positive, mains delay on Out 1/2 if negative); merit = summation in the overlap band.
3. Out 3 gain for a chosen extra bass level, live-mode gain (Out 3 sums In A + In B: +6 dB for mono bass).
"""
import sys, os, glob, re
import numpy as np
from scipy.io import wavfile
from scipy.signal import sosfreqz
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt

repo, out = sys.argv[1], sys.argv[2]
T0, SR, NFFT, OFFSET = 256, 48000, 1 << 18, 100.9
M = os.path.join(repo, "measurements", "2026-11-22")

cal = np.loadtxt(os.path.join(repo, "reference", "mic-cal", "MM-1C_90deg.txt"), comments="*")
fq = np.fft.rfftfreq(NFFT, 1 / SR)
calc = np.interp(np.log10(np.maximum(fq, 1)), np.log10(cal[:, 0]), cal[:, 1])
GRID = np.geomspace(15, 400, 500)


def spec(f, right_ms=500):
    sr, x = wavfile.read(f); assert sr == SR, f
    x = x.astype(float); n_end = T0 + int(right_ms / 1000 * SR)
    x = np.pad(x, (0, max(0, n_end - len(x))))[T0:n_end].copy()
    fade = len(x) // 4; x[-fade:] *= 0.5 * (1 + np.cos(np.linspace(0, np.pi, fade)))
    return np.fft.rfft(x, NFFT) * 10 ** (-calc / 20)


def smooth(H, frac):
    cs = np.concatenate([[0], np.cumsum(np.abs(H) ** 2)])
    lo = np.searchsorted(fq, GRID * 2 ** (-0.5 / frac)); hi = np.maximum(np.searchsorted(fq, GRID * 2 ** (0.5 / frac)), lo + 1)
    return (cs[hi] - cs[lo]) / (hi - lo)


def db(p): return 10 * np.log10(p) + OFFSET
def avg(Hs, frac=6): return db(np.mean([smooth(H, frac) for H in Hs], axis=0))
def at(y, f0): return np.interp(np.log10(f0), np.log10(GRID), y)
def band(y, lo, hi): m = (GRID >= lo) & (GRID <= hi); return 10 * np.log10(np.mean(10 ** (y[m] / 10)))


# ---------- files ----------
GROUPS = {"seat": ("subC-seat", "eq-seat"), "dj": ("subC-dj", "eq-dj"), "corners": ("subC-corners", "eq-corners")}
S, MN = {}, {}   # S[(g, pos)] sub spectrum; MN[(g, pos, tag)] mains L+R spectrum
for g, (sset, eset) in GROUPS.items():
    for f in sorted(glob.glob(os.path.join(M, sset, "3 S *.wav"))):
        pos = re.match(r"3 S (.+) subC\.wav$", os.path.basename(f)).group(1)
        S[(g, pos)] = spec(f)
        for tag in ("eq1", "eq2"):
            lr = [glob.glob(os.path.join(M, eset, f"{n} {s} {pos} {tag}*.wav")) for n, s in ((1, "L"), (2, "R"))]
            assert all(len(x) == 1 for x in lr), (g, pos, tag, lr)
            MN[(g, pos, tag)] = spec(lr[0][0]) + spec(lr[1][0])
POS = {g: [p for (gg, p) in S if gg == g] for g in GROUPS}
for g in GROUPS: print(f"{g}: {len(POS[g])} positions: {', '.join(POS[g])}")

# ---------- 1. sub alone vs mains alone ----------
print("\n=== 1. Sub alone (Out 3 -10 dB, In A only) vs mains L+R, power average, 1/6 oct, dB SPL ===")
FREQS = [20, 25, 28, 31.5, 35, 40, 45, 50, 56, 63, 71, 80, 90, 100, 125, 160, 200]
print("group    curve      " + " ".join(f"{f:>5g}" for f in FREQS))
CURVES = {}
for g in GROUPS:
    CURVES[(g, "sub")] = avg([S[(g, p)] for p in POS[g]])
    for tag in ("eq1", "eq2"):
        CURVES[(g, tag)] = avg([MN[(g, p, tag)] for p in POS[g]])
    for c in ("sub", "eq2", "eq1"):
        print(f"{g:8} {('mains ' + c) if c != 'sub' else 'sub':10} " + " ".join(f"{at(CURVES[(g, c)], f):5.1f}" for f in FREQS))
print("\nSpread over the positions (max - min of the 1/6-oct curves), seat group:")
for name, Hs in (("sub", [S[("seat", p)] for p in POS["seat"]]), ("mains eq2", [MN[("seat", p, "eq2")] for p in POS["seat"]])):
    ys = np.array([db(smooth(H, 6)) for H in Hs])
    print(f"  {name:10} " + " ".join(f"{np.interp(np.log10(f), np.log10(GRID), ys.max(0) - ys.min(0)):5.1f}" for f in FREQS))

# ---------- 2. overlay design: alignment (Out 3 LPF, polarity, delay, gain) ----------
NB = int(260 / (SR / NFFT))                         # contiguous bins 0..~260 Hz are enough below 120 Hz
fb = fq[:NB]; zb = np.exp(-1j * 2 * np.pi * fb / SR)
FIT = np.geomspace(25, 120, 60)                     # fit band, 1/6-oct power smoothing on these points
f_lo = np.searchsorted(fb, FIT * 2 ** (-1 / 12)); f_hi = np.maximum(np.searchsorted(fb, FIT * 2 ** (1 / 12)), f_lo + 1)
WEIGHT = {"seat": 2 / 3, "dj": 1 / 3}
freq_hz = lambda r: 1000 * 2 ** ((r - 170) / 30)
freq_raw = lambda hz: int(np.clip(round(170 + 30 * np.log2(hz / 1000)), 0, 300))
XO = {10: ("LR24", [(1.4142, 1), (1.4142, 1)]), 8: ("BW24", [(0.7654, 1), (1.8478, 1)])}


def lpf(slope, fc, f=fb):
    """device crossover LPF (protocol.md 6.3): analog sections 1/(1 + a P + b P^2), P = s/wc, bilinear at 48 kHz"""
    wc = 2 * SR * np.tan(np.pi * fc / SR)           # prewarped
    s = 2 * SR * (1 - np.exp(-1j * 2 * np.pi * f / SR)) / (1 + np.exp(-1j * 2 * np.pi * f / SR))
    H = np.ones_like(f, complex)
    for a, b in XO[slope][1]:
        P = s / wc; H = H / (1 + a * P + b * P ** 2)
    return H


def low_shelf_db(f, gain, f0, q):
    A = 10 ** (gain / 40); w = 2 * np.pi * f0 / SR; al = np.sin(w) / (2 * q); c = np.cos(w); sA = 2 * np.sqrt(A) * al
    b = [A * ((A + 1) - (A - 1) * c + sA), 2 * A * ((A - 1) - (A + 1) * c), A * ((A + 1) - (A - 1) * c - sA)]
    a = [(A + 1) + (A - 1) * c + sA, -2 * ((A - 1) + (A + 1) * c), (A + 1) + (A - 1) * c - sA]
    zz = np.exp(-1j * 2 * np.pi * np.asarray(f) / SR)
    return 20 * np.log10(np.abs((b[0] + b[1] * zz + b[2] * zz ** 2) / (a[0] + a[1] * zz + a[2] * zz ** 2)))


def sm(P):   # P: (..., NB) power -> (..., len(FIT)) 1/6-oct means
    cs = np.concatenate([np.zeros(P.shape[:-1] + (1,)), np.cumsum(P, axis=-1)], axis=-1)
    return (cs[..., f_hi] - cs[..., f_lo]) / (f_hi - f_lo)


# mid level (300 Hz-3 kHz) of the mains L+R per group: the target is relative to it (as in analyse_eq_room.py)
MIDG = np.geomspace(300, 3000, 40)
def mid_db(Hs):
    cs = np.concatenate([[0], np.cumsum(np.mean([np.abs(H) ** 2 for H in Hs], axis=0))])
    lo = np.searchsorted(fq, MIDG * 2 ** (-1 / 12)); hi = np.searchsorted(fq, MIDG * 2 ** (1 / 12))
    return db(np.mean((cs[hi] - cs[lo]) / (hi - lo)))


TGT = {"eq2": low_shelf_db(FIT, 6.0, 105.0, 0.707), "eq1": np.zeros_like(FIT)}
MID = {(g, t): mid_db([MN[(g, p, t)] for p in POS[g]]) for g in WEIGHT for t in TGT}
GAINS = np.arange(-20, 16.01, 0.5)                  # sub gain rel. to the measured Out 3 = -10 dB, dB
Mb = {(g, t): np.array([MN[(g, p, t)][:NB] for p in POS[g]]) for g in WEIGHT for t in TGT}
Sb = {g: np.array([S[(g, p)][:NB] for p in POS[g]]) for g in WEIGHT}


def total_db(tag, Hsub, g_db, groups=WEIGHT):
    """mains + sub x Hsub x gain, power average per group, 1/6 oct on FIT, rel. to the group's mains mid level"""
    gl = 10 ** (g_db / 20)
    return {g: db(np.mean(sm(np.abs(Mb[(g, tag)] + gl * Sb[g] * Hsub) ** 2), axis=0)) - MID[(g, tag)] for g in groups}


def cost_of(tag, curves, extra=0.0):
    return np.sqrt(sum(w * np.mean((curves[g] - TGT[tag] - extra) ** 2) for g, w in WEIGHT.items()))




def delay_H(tau): return np.exp(-1j * 2 * np.pi * fb * tau / 1000)   # mains delayed by -tau = sub advanced: only the difference matters


TAGS = ("eq1", "eq2")
TNAME = {"eq1": "v1 flat (P02)", "eq2": "v2 Harman (P03)"}
NEW = {"eq1": "v3-flat-sub", "eq2": "v4-harman-sub"}
MAINS_DIR = {"eq1": "v1-flat", "eq2": "v2-harman"}


def scan(tag):
    """grid over slope, fc, polarity, relative delay; gain on GAINS via the three power terms (smoothing is linear)"""
    res = []
    A = {g: sm(np.abs(Mb[(g, tag)]) ** 2) for g in WEIGHT}
    for slope in XO:
        for fr in range(freq_raw(25), freq_raw(110) + 1, 2):
            L = lpf(slope, freq_hz(fr))
            for pol in (1, -1):
                for tau in np.arange(-10, 15.01, 0.5):
                    Hs = pol * L * delay_H(tau)
                    terms = {g: (A[g], sm(np.abs(Sb[g] * Hs) ** 2), sm(2 * np.real(Mb[(g, tag)] * np.conj(Sb[g] * Hs)))) for g in WEIGHT}
                    cs = [cost_of(tag, {g: db(np.mean(a + 10 ** (gd / 10) * b + 10 ** (gd / 20) * x, axis=0)) - MID[(g, tag)]
                                        for g, (a, b, x) in terms.items()}) for gd in GAINS]
                    i = int(np.argmin(cs)); res.append((cs[i], slope, fr, pol, tau, GAINS[i]))
    return sorted(res)


print("\n=== 2. Alignment scan: sum = mains (measured, L+R) + sub x Out 3 LPF x polarity x delay x gain ===")
print("Designed per preset (new versions v3 = v1 + sub, v4 = v2 + sub; mains filters unchanged).")
print("cost = rms dB of the sum vs the preset's target (v1 flat, v2 low shelf +6 dB 105 Hz), 25-120 Hz, 1/6 oct,")
print("seat 2/3 + DJ 1/3, each rel. to its mains mid level 300 Hz-3 kHz.")
print("delay > 0: on Out 3 (sub later); < 0: on Out 1/2 (mains later). Gain rel. to the measured Out 3 (-10 dB, In A only).")
ALONE, SCAN = {}, {}
for tag in TAGS:
    ALONE[tag] = cost_of(tag, {g: db(np.mean(sm(np.abs(Mb[(g, tag)]) ** 2), axis=0)) - MID[(g, tag)] for g in WEIGHT})
    SCAN[tag] = scan(tag)
    print(f"\n-- {TNAME[tag]}: mains alone {ALONE[tag]:.2f} dB. Best 8 (no PEQ on Out 3):")
    print("   cost  LPF   fc Hz  pol  delay ms  gain dB")
    for c, slope, fr, pol, tau, gd in SCAN[tag][:8]:
        print(f"  {c:5.2f}  {XO[slope][0]}  {freq_hz(fr):5.1f}  {'0' if pol > 0 else '180':>3}  {tau:+7.1f}  {gd:+6.1f}")


# ---------- 2b. refine + Out 3 PEQ, then onto the device grid ----------
from scipy.optimize import minimize
q_val = lambda r: 2 ** ((r - 16) / 12)
q_raw = lambda q: int(np.clip(round(16 + 12 * np.log2(q)), 0, 100))
A_of = lambda graw: 10 ** (abs((graw - 120) / 10) / 40)
# 1 band, Q <= 5: compared 2026-11-22 with 2 and 4 bands at Q <= 4/5/8 (env SUB_NPEQ / SUB_QMAX): more bands gained only
# 0.1-0.2 dB and landed somewhere else on every run; the one band (46-47 Hz, -12 dB) came out every time.
NPEQ = int(os.environ.get("SUB_NPEQ", 1)); G_MIN, G_MAX = -12.0, 6.0     # boost limited to +6 dB per band (headroom, leakage)
Q_MAX = float(os.environ.get("SUB_QMAX", 5.0))
FR_MAX = freq_raw(130)                  # PEQ bands only where the sub plays


def peq(fc, gain, q, z_=zb):
    A = 10 ** (gain / 40); w = 2 * np.pi * fc / SR; al = np.sin(w) / (2 * q); c = np.cos(w)
    return ((1 + al * A) - 2 * c * z_ + (1 - al * A) * z_ ** 2) / ((1 + al / A) - 2 * c * z_ + (1 - al / A) * z_ ** 2)


def sub_H(slope, fc, pol, tau, bands):
    H = pol * lpf(slope, fc) * delay_H(tau)
    for b in bands: H = H * peq(*b)
    return H


def curves_of(tag, slope, fc, pol, tau, gd, bands):
    return total_db(tag, sub_H(slope, fc, pol, tau, bands), gd)


def unpack(p):
    gd, tau, lfc = p[:3]
    return gd, tau, 2 ** lfc, [(2 ** p[3 + 3 * i], p[4 + 3 * i], 2 ** p[5 + 3 * i]) for i in range(NPEQ)]


def design(tag):
    c0, slope, fr, pol, tau0, g0 = SCAN[tag][0]
    cur = curves_of(tag, slope, freq_hz(fr), pol, tau0, g0, [])
    dev = sum(w * (cur[g] - TGT[tag]) for g, w in WEIGHT.items())
    # start bands at the biggest peaks of the aligned sum below 100 Hz (cuts), the rest at the biggest dips (0 dB)
    order = np.argsort(-dev); seeds = [FIT[i] for i in order if FIT[i] < 100]
    picked = []
    for f in seeds:
        if all(abs(np.log2(f / x)) > 1 / 6 for x in picked): picked.append(f)
        if len(picked) == NPEQ: break
    p0 = [g0, tau0, np.log2(freq_hz(fr))]
    for f in picked: p0 += [np.log2(f), float(np.clip(-np.interp(f, FIT, dev), G_MIN, 0)), np.log2(4.0)]
    bounds = [(-25, 25), (-10, 15), (np.log2(25), np.log2(120))] + [(np.log2(22), np.log2(130)), (G_MIN, G_MAX), (np.log2(0.5), np.log2(Q_MAX))] * NPEQ
    f_cost = lambda p: cost_of(tag, curves_of(tag, slope, unpack(p)[2], pol, unpack(p)[1], unpack(p)[0], unpack(p)[3]))
    r = minimize(f_cost, p0, method="Powell", bounds=bounds, options=dict(maxiter=20000, xtol=1e-3, ftol=1e-5))
    gd, tau, fc, bands = unpack(r.x)
    # device grid: LPF fc raw, delay in samples, Out 3 gain 0.1 dB, PEQ raw (f, gain, Q_dev = Q_rbj * A)
    D = dict(fr=freq_raw(fc), n=int(round(tau * SR / 1000)), g10=int(round(gd * 10)),
             bands=[(freq_raw(f), int(np.clip(round(g * 10 + 120), 0, 180)), q_raw(q * A_of(int(round(g * 10 + 120))))) for f, g, q in bands])
    def real(D):
        bb = [(freq_hz(a), (b - 120) / 10, q_val(c) / A_of(b)) for a, b, c in D["bands"] if b != 120]
        return freq_hz(D["fr"]), D["n"] * 1000 / SR, D["g10"] / 10, bb
    def dcost(D):
        fc_, tau_, g_, bb = real(D); return cost_of(tag, curves_of(tag, slope, fc_, pol, tau_, g_, bb))
    c_best, improved = dcost(D), True
    while improved:   # coordinate search on the integer grid, +-1 step
        improved = False
        for key in ("fr", "n", "g10"):
            for st in (-1, 1):
                T = dict(D); T[key] += st; c = dcost(T)
                if c < c_best - 1e-6: D, c_best, improved = T, c, True
        for i in range(len(D["bands"])):
            for j in range(3):
                for st in (-1, 1):
                    b = list(D["bands"][i]); b[j] += st
                    if not (0 <= b[0] <= FR_MAX and 0 <= b[1] <= 180 and 0 <= b[2] <= 100 and q_val(b[2]) / A_of(b[1]) <= Q_MAX * 2 ** (1 / 24)): continue
                    T = dict(D); T["bands"] = D["bands"][:i] + [tuple(b)] + D["bands"][i + 1:]; c = dcost(T)
                    if c < c_best - 1e-6: D, c_best, improved = T, c, True
    D["bands"] = sorted(b for b in D["bands"] if b[1] != 120)
    fc, tau, gd, bb = real(D)
    return dict(slope=slope, pol=pol, D=D, fc=fc, tau=tau, gd=gd, bands=bb, cost=c_best, cost_align=c0, cost_cont=r.fun)


print(f"\n=== 2b. Refined per preset: gain, delay, LPF fc and {NPEQ} PEQ band(s) on Out 3 (gain -12..+6 dB, Q <= {Q_MAX:g}), device grid ===")
DES = {}
for tag in TAGS:
    d = DES[tag] = design(tag)
    print(f"\n-- {TNAME[tag]} -> {NEW[tag]}: cost mains alone {ALONE[tag]:.2f}, aligned {d['cost_align']:.2f}, "
          f"with PEQ {d['cost_cont']:.2f}, on the device grid {d['cost']:.2f} dB")
    print(f"   Out 3 LPF {XO[d['slope']][0]} {d['fc']:.1f} Hz (raw {d['D']['fr']}), polarity {'180 (inverted)' if d['pol'] < 0 else '0'}, "
          f"delay {d['tau']:+.3f} ms ({d['D']['n']:+d} samples, {'Out 3' if d['tau'] >= 0 else 'Out 1/2'}), gain {d['gd']:+.1f} dB vs measured")
    for f, g, q in d["bands"]: print(f"   PEQ  {f:6.2f} Hz  {g:+5.1f} dB  Q_rbj {q:.3f}")

# ---------- 3. robustness: every position, mains alone vs with the sub ----------
print("\n=== 3. Per position: rms dB vs the target, 25-120 Hz, 1/6 oct (rel. to the group's mid level) ===")
GROUP_ALL = ("seat", "dj", "corners")
MIDc = {(g, t): mid_db([MN[(g, p, t)] for p in POS[g]]) for g in GROUP_ALL for t in TAGS}
for tag in TAGS:
    d = DES[tag]; Hs = sub_H(d["slope"], d["fc"], d["pol"], d["tau"], d["bands"]); gl = 10 ** (d["gd"] / 20)
    print(f"-- {NEW[tag]}")
    for g in GROUP_ALL:
        for p in POS[g]:
            Mx = MN[(g, p, tag)][:NB]; Sx = S[(g, p)][:NB]
            a = db(sm(np.abs(Mx) ** 2)) - MIDc[(g, tag)]; b = db(sm(np.abs(Mx + gl * Sx * Hs) ** 2)) - MIDc[(g, tag)]
            ra, rb = np.sqrt(np.mean((a - TGT[tag]) ** 2)), np.sqrt(np.mean((b - TGT[tag]) ** 2))
            print(f"   {g:8} {p:20} mains {ra:5.2f}   +sub {rb:5.2f}   {'better' if rb < ra - 0.3 else 'WORSE' if rb > ra + 0.3 else 'same'}")

# ---------- 4. curves, levels, Out 3 settings for the configurator ----------
FR4 = [25, 28, 31.5, 35, 40, 45, 50, 56, 63, 71, 80, 90, 100, 120]
print("\n=== 4. Power averages rel. to the mains mid level (dB), 1/6 oct: target, mains alone, mains + sub ===")
CUR = {}
for tag in TAGS:
    d = DES[tag]; Hs = sub_H(d["slope"], d["fc"], d["pol"], d["tau"], d["bands"]); gl = 10 ** (d["gd"] / 20)
    print(f"-- {NEW[tag]}")
    print("   group   curve     " + " ".join(f"{f:>5g}" for f in FR4))
    tg = np.interp(np.log10(FR4), np.log10(FIT), TGT[tag])
    print("   all     target    " + " ".join(f"{v:+5.1f}" for v in tg))
    for g in GROUP_ALL:
        Ms = [MN[(g, p, tag)][:NB] for p in POS[g]]; Ss = [S[(g, p)][:NB] for p in POS[g]]
        a = db(np.mean(sm(np.abs(np.array(Ms)) ** 2), axis=0)) - MIDc[(g, tag)]
        b = db(np.mean(sm(np.abs(np.array(Ms) + gl * np.array(Ss) * Hs) ** 2), axis=0)) - MIDc[(g, tag)]
        c = db(np.mean(sm(np.abs(gl * np.array(Ss) * Hs) ** 2), axis=0)) - MIDc[(g, tag)]
        CUR[(tag, g)] = (a, b, c)
        for name, y in (("mains", a), ("+sub", b), ("sub only", c)):
            print(f"   {g:7} {name:9} " + " ".join(f"{v:+5.1f}" for v in np.interp(np.log10(FR4), np.log10(FIT), y)))
    # bass energy 25-60 Hz at the seat (what leaks through the building most): with vs without the sub
    a, b, _ = CUR[(tag, "seat")]; m = FIT <= 60
    print(f"   seat bass energy 25-60 Hz with the sub: {10 * np.log10(np.mean(10 ** (b[m] / 10)) / np.mean(10 ** (a[m] / 10))):+.1f} dB vs mains alone")

print("\n=== 5. Out 3 settings per new version (configurator values) ===")
print("Gain: measured with In A only -> Out 3 at -10 dB. Live, Out 3 sums In A + In B (+ C + D), and bass is ~mono, so the")
print("live Out 3 gain is 6.0 dB lower for the same sub level: live = -10 + gain - 6.0 dB.")
print("The design matches sub and mains at the measuring amp position (50). The amp only drives the mains, so the sub is")
print("tuned for each preset's fun position (listening finding): Out 3 lower by 1 dB per amp step below 50 (A300 measured")
print("2026-11-22: 72 dB(C) at 50, 67 at 45). At lower amp positions the sub plays relatively louder.")
AMP_FUN = {"eq1": 50, "eq2": 45}
AMP_DB_PER_STEP = 1.0
SETTINGS = {}
for tag in TAGS:
    d = DES[tag]
    g_live = round(-10 + d["gd"] - 6.0 - AMP_DB_PER_STEP * (50 - AMP_FUN[tag]), 1)
    SETTINGS[tag] = dict(lpf=f"{XO[d['slope']][0]} {d['fc']:.1f} Hz", pol="180 (invert)" if d["pol"] < 0 else "0 (normal)",
                         delay=f"{d['tau']:.3f} ms = {d['D']['n']} samples" if d["tau"] >= 0 else f"{-d['tau']:.3f} ms on Out 1 and Out 2",
                         gain=f"{g_live:+.1f} dB (for amp {AMP_FUN[tag]})", hpf="off", routing="In A + In B + In C + In D")
    print(f"-- {NEW[tag]} (= {TNAME[tag]} mains unchanged, + Out 3):")
    for k, v in SETTINGS[tag].items(): print(f"   {k:8} {v}")
    for f, g, q in d["bands"]: print(f"   PEQ      {f:.2f} Hz {g:+.1f} dB Q_rbj {q:.4f}  (device Q {q_val(d['D']['bands'][0][2]):.2f})")

# filter files (REW text = transport for the configurator import, as eq/v1-flat, eq/v2-harman)
import datetime
for tag in TAGS:
    d = DES[tag]; folder = os.path.join(repo, "eq", NEW[tag]); os.makedirs(folder, exist_ok=True)
    st = SETTINGS[tag]
    fl = ["Filter Settings file", "", "Room EQ V5.31", f"Dated: {datetime.datetime.now():%d %b %Y %H:%M:%S}", "",
          f"Notes:akustik {NEW[tag]} sub (DSP out 3); designed by analysis/analyse_sub_c.py on the t.racks grid (REW text format = transport for the configurator import); "
          f"set by hand on Out 3: LPF {st['lpf']}, polarity {st['pol']}, delay {st['delay']}, gain {st['gain']}, routing {st['routing']}; mains Out 1/2 = eq/{MAINS_DIR[tag]} unchanged",
          "", "Equaliser: Generic", f"akustik {NEW[tag]} Sub"]
    for i in range(7):
        if i < len(d["bands"]):
            f, g, q = d["bands"][i]; fl.append(f"Filter {i+1:2d}: ON  PK       Fc {f:8.2f} Hz  Gain {g:5.1f} dB  Q {q:7.4f}")
        else:
            fl.append(f"Filter {i+1:2d}: OFF None")
    with open(os.path.join(folder, "Sub.txt"), "w", newline="\r\n") as fh: fh.write("\n".join(fl) + "\n")
print("\nwrote eq/" + ", eq/".join(f"{NEW[t]}/Sub.txt" for t in TAGS))

# plot
fig, axs = plt.subplots(2, 3, figsize=(16, 8.5), sharex=True, sharey=True)
for r, tag in enumerate(TAGS):
    for c, g in enumerate(GROUP_ALL):
        a, b, s_ = CUR[(tag, g)]; ax = axs[r, c]
        ax.semilogx(FIT, TGT[tag], "k--", lw=1, label="target")
        ax.semilogx(FIT, a, color="tab:blue", label="mains alone"); ax.semilogx(FIT, b, color="tab:red", lw=2, label="mains + sub")
        ax.semilogx(FIT, s_, color="tab:green", lw=1, alpha=0.7, label="sub alone (with Out 3 filters)")
        ax.set_title(f"{NEW[tag]}: {g} ({len(POS[g])} pos.)"); ax.grid(True, which="both", alpha=0.3); ax.set_ylim(-25, 15)
        ax.set_xticks([25, 30, 40, 50, 60, 80, 100, 120]); ax.set_xticklabels(["25", "30", "40", "50", "60", "80", "100", "120"])
axs[0, 0].legend(fontsize=8); axs[1, 1].set_xlabel("Hz"); axs[0, 0].set_ylabel("dB rel. mid level"); axs[1, 0].set_ylabel("dB rel. mid level")
fig.suptitle("Sub8 at spot C + mains (measured 2026-11-22), 1/6 oct power average; designed on seat 2/3 + DJ 1/3")
fig.tight_layout(); fig.savefig(os.path.join(out, "sub_c.png"), dpi=110)

# curves for analysis/build_writeup.py
np.savez(os.path.join(out, "sub_c_curves.npz"), fit=FIT, **{f"target|{t}": TGT[t] for t in TAGS},
         **{f"{t}|{g}|{w}": CUR[(t, g)][i] for t in TAGS for g in GROUP_ALL for i, w in enumerate(("mains", "with_sub", "sub"))})

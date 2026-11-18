"""EQ design: cut-only PEQs per channel (max 7) + fixed DSP high-pass, simulated on all measured IRs.

Usage: design_eq.py <repo> <out_dir> <eq_dir> [flat|harman]

Targets
- flat (default, EQ v1): bass at each set's own 300 Hz-3 kHz level. Outputs eq_design.*, eq/v1-flat/{L,R}.txt.
- harman (EQ v2): Harman-style in-room bass rise = RBJ low shelf +6 dB, 105 Hz, Q 0.707 on top of the mid level
  (about +5.8 dB at 30 Hz, +5.2 at 50, +3 at 105, +1.3 at 200, +0.6 at 300 Hz). The treble tilt of the Harman
  in-room curve isn't part of this (the EQ only touches the bass; the 300 Hz-3 kHz reference stays the 0 dB point).
  Outputs eq_design_harman.*, eq/v2-harman/{L,R}.txt; the report also simulates v1 for comparison.

Method
- Complex spectra of every IR (500 ms window, 90° mic cal). The EQ (biquads at 48 kHz, RBJ peaking,
  the definition REW's "Generic" equaliser uses) is applied as a complex multiply, so the L+R sums
  include the filters' phase.
- Target: see above, relative to each set's own 300 Hz-3 kHz level; fit range 25-250 Hz, 1/24 oct.
- Cost (asymmetric): excess above target counts fully; going below target counts only where the EQ
  made it deeper than it already was (so cuts aren't spent on dips). flat: penalty e^2 - e0^2; harman: (e - e0)^2
  for the extra depth only. With the raised target many spots sit several dB below it already (e.g. 47 Hz next to
  the 43 Hz mode), and e^2 - e0^2 then made every dB of filter skirt there ~10x as expensive, so the 43 Hz mode
  stayed +5 dB above target. Terms and weights:
    seat L+R sum 1.0, seat L 0.5, seat R 0.5, DJ L+R sum 0.4.
- High-pass (DSP HP filter, not a PEQ band) is fixed during the fit.
"""
import sys, os, glob, re, datetime
import numpy as np
from scipy.io import wavfile
from scipy.optimize import minimize
from scipy.signal import find_peaks
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt

repo, out, eqdir = sys.argv[1], sys.argv[2], sys.argv[3]
TARGET = sys.argv[4] if len(sys.argv) > 4 else "flat"
assert TARGET in ("flat", "harman"), TARGET
SFX = "" if TARGET == "flat" else "_" + TARGET     # output file suffix; v1 files stay untouched
EQSUB = "v1-flat" if TARGET == "flat" else "v2-" + TARGET   # filter files go to eq/<EQSUB>/{L,R}.txt
SHELF = dict(gain=6.0, f0=105.0, q=0.707)           # harman target: RBJ low shelf on top of the mid level
os.makedirs(os.path.join(eqdir, EQSUB), exist_ok=True)
T0, SR, NFFT, OFFSET = 256, 48000, 1 << 18, 100.9
NBANDS = 7
HPF = dict(fc=30.0, order=4)          # Butterworth 24 dB/oct
HPF_ALT = [25.0, 30.0, 35.0, 40.0]    # reported for comparison
FIT = (25, 250)
GMIN = -12.0                          # DSP (own configurator) accepts +-12 dB per band
QMAX = 8.0                            # robust to position changes (context: Q 3-8 for clear modes)
REG = 0.005                           # cost per dB of total cut: avoids stacked / wasted bands

cal = np.loadtxt(os.path.join(repo, "reference", "mic-cal", "MM-1C_90deg.txt"), comments="*")
fq_all = np.fft.rfftfreq(NFFT, 1 / SR)
KEEP = fq_all < 4000                   # bins we need (bass fit + mid reference)
fq = fq_all[KEEP]
calc = np.interp(np.log10(np.maximum(fq, 1)), np.log10(cal[:, 0]), cal[:, 1])


def spec(f):
    sr, x = wavfile.read(f); assert sr == SR
    x = x.astype(float)
    n_end = T0 + int(0.5 * SR); x = np.pad(x, (0, max(0, n_end - len(x))))[:n_end]
    fade = int(0.125 * SR); x[-fade:] *= 0.5 * (1 + np.cos(np.linspace(0, np.pi, fade)))
    return np.fft.rfft(x, NFFT)[KEEP] * 10 ** (-calc / 20)


GRID = np.geomspace(18, 3500, 700)
FRAC = 24


def low_shelf_db(f, gain, f0, q, sr=SR):
    """RBJ cookbook low-shelf magnitude in dB at frequencies f"""
    A = 10 ** (gain / 40); w = 2 * np.pi * f0 / sr; al = np.sin(w) / (2 * q); c = np.cos(w); sA = 2 * np.sqrt(A) * al
    b = [A * ((A + 1) - (A - 1) * c + sA), 2 * A * ((A - 1) - (A + 1) * c), A * ((A + 1) - (A - 1) * c - sA)]
    a = [(A + 1) + (A - 1) * c + sA, -2 * ((A - 1) + (A + 1) * c), (A + 1) + (A - 1) * c - sA]
    zz = np.exp(-1j * 2 * np.pi * np.asarray(f) / sr)
    return 20 * np.log10(np.abs((b[0] + b[1] * zz + b[2] * zz ** 2) / (a[0] + a[1] * zz + a[2] * zz ** 2)))


TGT = np.zeros_like(GRID) if TARGET == "flat" else low_shelf_db(GRID, **SHELF)   # target rel. to mid level, dB
_lo = np.searchsorted(fq, GRID * 2 ** (-0.5 / FRAC))
_hi = np.maximum(np.searchsorted(fq, GRID * 2 ** (0.5 / FRAC)), _lo + 1)


def smooth_pow(H):
    """|H|^2 -> fractional-octave power smoothing on GRID (linear power)."""
    cs = np.concatenate([[0], np.cumsum(np.abs(H) ** 2)])
    return (cs[_hi] - cs[_lo]) / (_hi - _lo)


def avg_db(Hs):
    """power average over positions of smoothed responses, dB"""
    return 10 * np.log10(np.mean([smooth_pow(H) for H in Hs], axis=0)) + OFFSET


# ---------- load ----------
def pairs(folder, pat):
    d = {}
    for f in glob.glob(os.path.join(repo, "measurements", folder, "*.wav")):
        m = re.search(pat, os.path.basename(f))
        if m: d.setdefault(m.group(2), {})[m.group(1)] = spec(f)
    return d

sets = {
    "seat": pairs("2026-11-18/positions", r"\d ([LR]) (pos\d \w+) "),
    "dj": pairs("2026-11-18/dj", r"\d ([LR]) DJ (\w+) "),
    "corner": pairs("2026-11-18/corners", r"\d ([LR]) corner front (\w+) "),
}
sets["seat"]["seat"] = {("L" if "left" in f else "R"): spec(f)
                        for f in glob.glob(os.path.join(repo, "measurements", "2026-11-18", "seat", "*first sweep*.wav"))}
for k, v in sets.items():
    assert all(len(lr) == 2 for lr in v.values()), k
print("positions:", {k: len(v) for k, v in sets.items()})

# ---------- filters ----------
z = np.exp(-1j * 2 * np.pi * fq / SR)   # z^-1 on the bins


def biquad(b, a):
    return (b[0] + b[1] * z + b[2] * z ** 2) / (a[0] + a[1] * z + a[2] * z ** 2)


def peq(fc, gain, q):
    A = 10 ** (gain / 40); w = 2 * np.pi * fc / SR; al = np.sin(w) / (2 * q); c = np.cos(w)
    return biquad([1 + al * A, -2 * c, 1 - al * A], [1 + al / A, -2 * c, 1 - al / A])


def hpf(fc, order=4):
    if fc is None: return np.ones_like(z)
    from scipy.signal import butter, sosfreqz
    sos = butter(order, fc, btype="high", fs=SR, output="sos")
    return sosfreqz(sos, worN=fq, fs=SR)[1]


def chain(bands, hp):
    H = hp.copy()
    for fc, g, q in bands:
        H = H * peq(fc, g, q)
    return H


# ---------- responses ----------
def responses(EQ, hp_fc=HPF["fc"]):
    """EQ = {'L': H, 'R': H} (PEQ only); returns dict of (set, which) -> dB on GRID"""
    hp = hpf(hp_fc)
    r = {}
    for name, d in sets.items():
        L = [lr["L"] * EQ["L"] * hp for lr in d.values()]
        R = [lr["R"] * EQ["R"] * hp for lr in d.values()]
        r[(name, "L")] = avg_db(L); r[(name, "R")] = avg_db(R)
        r[(name, "L+R")] = avg_db([a + b for a, b in zip(L, R)])
    return r


ONE = np.ones_like(z)
REFB = (GRID > 300) & (GRID < 3000)
FITB = (GRID >= FIT[0]) & (GRID <= FIT[1])
flat = responses({"L": ONE, "R": ONE}, hp_fc=None)
REF = {k: v[REFB].mean() for k, v in flat.items()}   # mid level per set/which (EQ doesn't touch it)
base = responses({"L": ONE, "R": ONE})                # HPF only

# ---------- fit ----------
TERMS = [(("seat", "L+R"), 1.0), (("seat", "L"), 0.5), (("seat", "R"), 0.5), (("dj", "L+R"), 0.4)]
# fast path for the fit: only the sets/bins in TERMS
FB = fq < 400
hp_fb = hpf(HPF["fc"])[FB]
zf = z[FB]
lo_f, hi_f = _lo[FITB], _hi[FITB]
assert hi_f.max() <= FB.sum()


def peq_f(fc, gain, q):
    A = 10 ** (gain / 40); w = 2 * np.pi * fc / SR; al = np.sin(w) / (2 * q); c = np.cos(w)
    return ((1 + al * A) + (-2 * c) * zf + (1 - al * A) * zf ** 2) / ((1 + al / A) + (-2 * c) * zf + (1 - al / A) * zf ** 2)


def sp_fit(H):
    cs = np.concatenate([[0], np.cumsum(np.abs(H) ** 2)])
    return (cs[hi_f] - cs[lo_f]) / (hi_f - lo_f)


fitdata = {n: [(lr["L"][FB] * hp_fb, lr["R"][FB] * hp_fb) for lr in sets[n].values()] for n in ("seat", "dj")}
e0 = {k: base[k][FITB] - REF[k] - TGT[FITB] for k, _ in TERMS}


COUNTS = {"L": NBANDS, "R": NBANDS}


def unpack(p):
    p = np.asarray(p).reshape(-1, 3); out, i = {}, 0
    for s in "LR":
        out[s] = [(np.exp(a), g, np.exp(b)) for a, g, b in p[i:i + COUNTS[s]]]; i += COUNTS[s]
    return out


def pack(bands):
    return np.array([v for s in "LR" for fc, g, q in bands[s] for v in (np.log(fc), g, np.log(q))])


def cost(p):
    bands = unpack(p)
    E = {}
    for s in "LR":
        H = np.ones_like(zf)
        for fc, g, q in bands[s]:
            H = H * peq_f(fc, g, q)
        E[s] = H
    tot = 0
    for (name, which), w in TERMS:
        ps = []
        for L, R in fitdata[name]:
            Lq, Rq = L * E["L"], R * E["R"]
            ps.append(sp_fit(Lq if which == "L" else Rq if which == "R" else Lq + Rq))
        e = 10 * np.log10(np.mean(ps, axis=0)) + OFFSET - REF[(name, which)] - TGT[FITB]
        pos = np.maximum(e, 0) ** 2
        if TARGET == "flat":   # v1: e^2 - e0^2 (grows with how deep the dip already was)
            neg = np.maximum(np.minimum(e, 0) ** 2 - np.minimum(e0[(name, which)], 0) ** 2, 0)
        else:                  # v2: only the extra depth the EQ adds, squared (see docstring)
            neg = np.minimum(np.minimum(e, 0) - np.minimum(e0[(name, which)], 0), 0) ** 2
        tot += w * np.mean(pos + neg)
    return tot + REG * sum(-g for s in bands for _, g, _ in bands[s])


def init_bands(s):
    """greedy start: biggest peaks of the channel's seat excess (and of the sum, for shared modes)"""
    e = base[("seat", s)] - REF[("seat", s)] - TGT
    g = GRID
    sel = FITB
    pk, pr = find_peaks(np.where(sel, e, -99), prominence=2)
    pk = [i for i in pk if e[i] > 1.5]
    pk = sorted(pk, key=lambda i: -e[i])[:NBANDS]
    bands = [(g[i], -min(e[i] * 0.7, -GMIN), 4.0) for i in pk]
    while len(bands) < NBANDS:          # unused bands start as 0 dB (optimiser may use them)
        bands.append((60.0 * (1 + len(bands) % 3), -0.1, 3.0))
    return bands


BOUND1 = [(np.log(FIT[0]), np.log(FIT[1])), (GMIN, 0), (np.log(0.7), np.log(QMAX))]


def fit(start_bands, restarts=1):
    p0 = pack(start_bands)
    bounds = BOUND1 * (len(p0) // 3)
    lo, hi = np.array([b[0] for b in bounds]), np.array([b[1] for b in bounds])
    best = None
    for rep in range(restarts):   # perturbed restarts, keep the best
        st = p0 if rep == 0 else p0 + np.random.default_rng(rep).normal(0, [0.05, 1.0, 0.2] * (len(p0) // 3))
        r = minimize(cost, np.clip(st, lo, hi), method="L-BFGS-B", bounds=bounds, options=dict(maxiter=600))
        print(f"  fit {COUNTS}: restart {rep}: cost {r.fun:.3f}")
        if best is None or r.fun < best.fun: best = r
    return unpack(best.x), best.fun


def merge(bl):
    """merge bands closer than 1/12 oct (stacked on one mode) and drop ones under 0.5 dB"""
    bl = sorted([b for b in bl if b[1] < -0.5])
    outb = []
    for fc, g, q in bl:
        if outb and abs(np.log2(fc / outb[-1][0])) < 1 / 12:
            f2, g2, q2 = outb[-1]; w = g / (g + g2)
            outb[-1] = (f2 ** (1 - w) * fc ** w, max(g + g2, GMIN), q2 * (1 - w) + q * w)
        else:
            outb.append((fc, g, q))
    return outb


start = {s: init_bands(s) for s in "LR"}
print(f"cost before EQ: {cost(pack({s: [(f, 0.0, q) for f, _, q in start[s]] for s in 'LR'})):.2f}, at init: {cost(pack(start)):.2f}")
bands, fun = fit(start, restarts=3)
while True:   # merge stacked bands, re-fit with the smaller set, until nothing merges
    m = {s: merge(bands[s]) for s in "LR"}
    if all(len(m[s]) == COUNTS[s] for s in "LR"):
        break
    COUNTS.update({s: len(m[s]) for s in "LR"})
    bands, fun = fit(m)
best_fun = fun
print(f"continuous fit cost {fun:.3f}")

# ---------- snap to the device ----------
# t.racks DSP 4x4 Mini, from the protocol RE (../tracks/docs/protocol.md §5, §6.2):
#   PEQ gain raw 0..240, dB = (raw-120)/10;  freq raw 0..300, Hz = 1000*2^((raw-170)/30);  Q raw 0..100, Q = 2^((raw-16)/12)
#   Peak = RBJ peaking with Q_rbj = Q_device / A, A = 10^(|G|/40). Butterworth 24 HPF = textbook (sections 0.7654/1.8478).
freq_hz = lambda r: 1000 * 2 ** ((r - 170) / 30)
freq_raw = lambda hz: int(np.clip(round(170 + 30 * np.log2(hz / 1000)), 0, 300))
q_val = lambda r: 2 ** ((r - 16) / 12)
q_raw = lambda q: int(np.clip(round(16 + 12 * np.log2(q)), 0, 100))
A_of = lambda graw: 10 ** (abs((graw - 120) / 10) / 40)


def dev_to_rbj(d):
    fr, gr, qr = d
    return (freq_hz(fr), (gr - 120) / 10, q_val(qr) / A_of(gr))


def rbj_to_dev(b):
    fc, g, q = b
    gr = int(np.clip(round(g * 10 + 120), 0, 120))        # cut only: raw <= 120
    return (freq_raw(fc), gr, q_raw(q * A_of(gr)))


QRAW_OK = lambda d: d[2] >= 0 and d[2] <= 100 and q_val(d[2]) / A_of(d[1]) <= QMAX * 2 ** (1 / 24)
dev = {s: [rbj_to_dev(b) for b in bands[s]] for s in "LR"}
dcost = lambda dv: cost(pack({s: [dev_to_rbj(d) for d in dv[s]] for s in "LR"}))
c_snap = dcost(dev)
improved = True
while improved:   # coordinate search on the integer grid: +-1 step per parameter
    improved = False
    for s in "LR":
        for i in range(len(dev[s])):
            for j in range(3):
                for step in (-1, 1):
                    d = list(dev[s][i]); d[j] += step; d = tuple(d)
                    if not (0 <= d[0] <= 300 and 0 <= d[1] <= 120 and QRAW_OK(d)): continue
                    trial = {k: list(v) for k, v in dev.items()}; trial[s][i] = d
                    c = dcost(trial)
                    if c < c_snap - 1e-6:
                        dev, c_snap, improved = trial, c, True
dev = {s: sorted(d for d in dev[s] if d[1] < 120) for s in "LR"}
best_fun = c_snap
HPF["fc"] = freq_hz(freq_raw(HPF["fc"]))
final = {s: [dev_to_rbj(d) for d in dev[s]] for s in "LR"}
EQ = {s: chain(final[s], ONE) for s in "LR"}
after = responses(EQ)

V1 = None   # EQ v1 (flat target) from its filter files, for comparison in the v2 report
if TARGET != "flat" and all(os.path.exists(os.path.join(eqdir, "v1-flat", f"{s}.txt")) for s in "LR"):
    rx = r"Filter\s+\d+: ON\s+PK\s+Fc\s+([\d.]+) Hz\s+Gain\s+([-\d.]+) dB\s+Q\s+([\d.]+)"
    v1b = {s: [tuple(map(float, m)) for m in re.findall(rx, open(os.path.join(eqdir, "v1-flat", f"{s}.txt")).read())] for s in "LR"}
    V1 = responses({s: chain(v1b[s], ONE) for s in "LR"})


# ---------- report ----------
def stats(r, key, lo=30, hi=200):
    b = (GRID >= lo) & (GRID <= hi)
    e = r[key][b] - REF[key] - TGT[b]
    return np.sqrt(np.mean(e ** 2)), e.max(), e.min()


def bass_energy(r, key, lo=30, hi=150):
    b = (GRID >= lo) & (GRID <= hi)
    return 10 * np.log10(np.mean(10 ** (r[key][b] / 10)))


lines = []
P = lambda *a: lines.append(" ".join(str(x) for x in a))
P(f"EQ design {datetime.date.today()} | HPF Butterworth {HPF['order']*6} dB/oct @ {HPF['fc']:.1f} Hz (DSP HP filter, freq raw {freq_raw(HPF['fc'])}, slope raw 8) | fit {FIT[0]}-{FIT[1]} Hz, 1/{FRAC} oct, target " + ("flat at mid level" if TARGET == "flat" else f"harman = mid level + low shelf {SHELF['gain']:+.0f} dB @ {SHELF['f0']:.0f} Hz Q {SHELF['q']}"))
P(f"cost terms: {TERMS}; Q max {QMAX}, cut penalty {REG}/dB; cost after snapping to the device grid {best_fun:.3f} (continuous {fun:.3f})")
P("Simulation uses the device values exactly (Peak = RBJ with Q/A). Not modelled: the open low-frequency offset (peaks below 150 Hz measured up to 41 cents low, tracks TODO).")
for s in "LR":
    P(f"\n{s} PEQ ({len(final[s])} bands):")
    P("   band | device: freq     gain   Q (raw f/g/q)      | = RBJ cookbook: Fc, Gain, Q")
    for i, (d, (fc, g, q)) in enumerate(zip(dev[s], final[s]), 1):
        P(f"   {i:4d} | {freq_hz(d[0]):7.1f} Hz {g:6.1f} dB {q_val(d[2]):6.2f} ({d[0]:3d}/{d[1]:3d}/{d[2]:3d}) | {fc:7.2f} Hz {g:6.1f} dB {q:6.3f}")
P("\nMid reference levels (300 Hz-3 kHz, dB):", ", ".join(f"{k[0]} {k[1]} {v:.1f}" for k, v in REF.items()))
if TARGET != "flat":
    P("\nTarget rel. to mid level (dB): " + ", ".join(f"{f0} Hz {low_shelf_db(f0, **SHELF):+.1f}" for f0 in (25, 30, 40, 50, 60, 80, 100, 150, 200, 300)))
P("\n=== Deviation from target, 30-200 Hz: rms / max / min (dB) ===" if TARGET != "flat" else "\n=== Flatness vs own mid level, 30-200 Hz: rms / max / min (dB) ===")
cols = [("flat (no HPF)", flat), ("HPF only", base)] + ([("EQ v1 (flat)", V1)] if V1 else []) + [("HPF + PEQ", after)]
P(f"{'set':>14} | " + " | ".join(f"{c:>20}" for c, _ in cols))
for k in REF:
    row = [stats(r, k) for _, r in cols]
    P(f"{k[0]+' '+k[1]:>14} | " + " | ".join(f"{a:5.1f} {b:+6.1f} {c:+6.1f}  " for a, b, c in row))
P("\n=== Bass energy 30-150 Hz (power mean, dB SPL approx) = leakage proxy ===")
P(f"{'set':>14} | {'flat':>6} {'HPF':>6} {'EQ':>6} | change" + (" | v1 EQ, change | v2 - v1" if V1 else ""))
for k in REF:
    a, b, c = bass_energy(flat, k), bass_energy(base, k), bass_energy(after, k)
    extra = ""
    if V1:
        v = bass_energy(V1, k); extra = f" | {v:6.1f} {v-a:+5.1f} | {c-v:+5.1f}"
    P(f"{k[0]+' '+k[1]:>14} | {a:6.1f} {b:6.1f} {c:6.1f} | {c-a:+5.1f}" + extra)
P("\n=== L+R sum, 1/24 oct, relative to own mid level: before (flat) -> after (HPF + PEQ) ===" + (" [v1 after]; target column" if V1 else ""))
P(f"{'Hz':>5} | {'seat':>13} | {'DJ':>13} | {'corner':>13}" + (" | target" if TARGET != "flat" else ""))
at = lambda y, f0: np.interp(np.log10(f0), np.log10(GRID), y)
for f0 in [25, 28, 30, 35, 40, 43, 47, 51, 55, 60, 65, 68, 75, 80, 85, 89, 95, 100, 110, 115, 120, 128, 140, 163, 190, 250]:
    row = []
    for n in ("seat", "dj", "corner"):
        k = (n, "L+R")
        row.append(f"{at(flat[k], f0)-REF[k]:+5.1f} -> {at(after[k], f0)-REF[k]:+5.1f}" + (f" [{at(V1[k], f0)-REF[k]:+5.1f}]" if V1 else ""))
    P(f"{f0:5} | " + " | ".join(row) + (f" | {at(TGT, f0):+5.1f}" if TARGET != "flat" else ""))
P("\n=== HPF alternatives (with the same PEQs): seat L+R / DJ L+R level at 25/30/35/40 Hz rel. mid, bass energy 30-150 seat L+R ===")
for fc in HPF_ALT:
    r = responses(EQ, hp_fc=fc)
    vals = " ".join(f"{at(r[('seat','L+R')], f0)-REF[('seat','L+R')]:+5.1f}" for f0 in (25, 30, 35, 40))
    vd = " ".join(f"{at(r[('dj','L+R')], f0)-REF[('dj','L+R')]:+5.1f}" for f0 in (25, 30, 35, 40))
    P(f"  HPF {fc:4.0f} Hz: seat {vals} | DJ {vd} | energy {bass_energy(r, ('seat','L+R')):.1f}")
P("\n=== Robustness: L+R per single position, 30-200 Hz rms / max vs target (own set mid level" + (" + shelf" if TARGET != "flat" else "") + "), before -> after ===")
hp = hpf(HPF["fc"])
for n in ("seat", "dj"):
    for pos, lr in sorted(sets[n].items()):
        b = (GRID >= 30) & (GRID <= 200); k = (n, "L+R")
        e1 = 10 * np.log10(smooth_pow(lr["L"] + lr["R"]))[b] + OFFSET - REF[k] - TGT[b]
        e2 = 10 * np.log10(smooth_pow((lr["L"] * EQ["L"] + lr["R"] * EQ["R"]) * hp))[b] + OFFSET - REF[k] - TGT[b]
        P(f"  {n:>5} {pos:>13}: rms {np.sqrt(np.mean(e1**2)):4.1f} -> {np.sqrt(np.mean(e2**2)):4.1f}   max {e1.max():+5.1f} -> {e2.max():+5.1f}")
txt = "\n".join(lines)
print(txt)

# ---------- REW filter files ----------
stamp = datetime.datetime.now().strftime("%d %b %Y %H:%M:%S")
for s, name in (("L", "left (DSP out 1)"), ("R", "right (DSP out 2)")):
    fl = ["Filter Settings file", "", "Room EQ V5.31", f"Dated: {stamp}", "",
          f"Notes:akustik EQ {'v1 (flat target)' if TARGET == 'flat' else 'v2 (harman target)'} {name}; designed by analysis/design_eq.py on the t.racks grid (REW text format = transport for the configurator import); HP filter separately: Butterworth 24 dB/oct {HPF['fc']:.1f} Hz",
          "", "Equaliser: Generic", f"akustik{SFX} {s}"]
    for i in range(NBANDS):   # the DSP has 7 PEQ bands per output
        if i < len(final[s]):
            fc, g, q = final[s][i]   # exact device values: the import maps Q*A and rounds back onto dev[s][i]
            fl.append(f"Filter {i+1:2d}: ON  PK       Fc {fc:8.2f} Hz  Gain {g:5.1f} dB  Q {q:7.4f}")
            assert rbj_to_dev((round(fc, 2), round(g, 1), round(q, 4))) == dev[s][i]
        else:
            fl.append(f"Filter {i+1:2d}: OFF None")
    with open(os.path.join(eqdir, EQSUB, f"{s}.txt"), "w", newline="\r\n") as fh:
        fh.write("\n".join(fl) + "\n")
with open(os.path.join(out, f"eq_design{SFX}.txt"), "w") as fh:
    fh.write(txt + "\n")

# ---------- plots ----------
ticks = [20, 30, 40, 50, 60, 80, 100, 150, 200, 300, 500]
fig, axs = plt.subplots(3, 2, figsize=(14, 12), sharex=True)
for ax, k in zip(axs.flat, [("seat", "L"), ("seat", "R"), ("seat", "L+R"), ("dj", "L+R"), ("corner", "L"), ("corner", "R")]):
    ax.semilogx(GRID, flat[k] - REF[k], color="grey", lw=1, label="before (flat DSP)")
    ax.semilogx(GRID, after[k] - REF[k], "k", lw=2, label="after (HPF + PEQ)")
    if V1: ax.semilogx(GRID, V1[k] - REF[k], color="tab:blue", lw=1, alpha=0.7, label="EQ v1 (flat target)")
    ax.semilogx(GRID, TGT, color="tab:green", lw=1, ls="--", label="target (mid level)" if TARGET == "flat" else "target (harman shelf)")
    ax.set_xlim(18, 500); ax.set_ylim(-25, 25 if k[0] != "corner" else 35); ax.grid(True, which="both", alpha=0.3)
    ax.set_title(f"{k[0]} {k[1]} (power avg, 1/24 oct, rel. to own 300 Hz-3 kHz level)", fontsize=9)
    ax.set_xticks(ticks); ax.set_xticklabels(ticks); ax.legend(fontsize=7)
plt.tight_layout(); plt.savefig(os.path.join(out, f"eq_design{SFX}.png"), dpi=110)

fig, ax = plt.subplots(figsize=(12, 4.5))
hp = hpf(HPF["fc"])
for s, col in (("L", "tab:blue"), ("R", "tab:orange")):
    Hdb = 20 * np.log10(np.abs(EQ[s] * hp) + 1e-12)
    ax.semilogx(fq[1:], Hdb[1:], col, lw=2, label=f"{s}: HPF + PEQ")
    for fc, g, q in final[s]:
        ax.semilogx(fq[1:], 20 * np.log10(np.abs(peq(fc, g, q)))[1:], col, lw=0.6, alpha=0.6)
ax.set_xlim(15, 1000); ax.set_ylim(-30, 3); ax.grid(True, which="both", alpha=0.3); ax.legend()
ax.set_xticks(ticks + [1000]); ax.set_xticklabels(ticks + ["1k"]); ax.set_ylabel("dB"); ax.set_title("Filter responses (thin = single bands)")
plt.tight_layout(); plt.savefig(os.path.join(out, f"eq_filters{SFX}.png"), dpi=110)
print("\nwrote", *(os.path.join(out, f"{n}{SFX}.{e}") for n, e in (("eq_design", "txt"), ("eq_design", "png"), ("eq_filters", "png"))),
      *(os.path.join(eqdir, EQSUB, f"{s}.txt") for s in "LR"))

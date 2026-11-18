"""Build the interactive EQ explainer: measured data + design -> explainer/eq-explained.html

Usage: build_explainer.py <repo>
Reads the IR exports, the filter files in eq/ and the template explainer/template.html, and inlines a JSON blob
(complex bass spectra of every seat/DJ/corner measurement, the IR example, the electrical check) into the page.
The page then applies filters, sums L+R, smooths and averages in the browser, with the same maths as design_eq.py.
"""
import sys, os, re, glob, json
import numpy as np
from scipy.io import wavfile
from scipy.signal import butter, sosfreqz

repo = sys.argv[1]
T0, SR, OFFSET = 256, 48000, 100.9
NFFT = 1 << 17                     # 0.366 Hz bins (true resolution of the 500 ms window is ~2 Hz)
F_LO, F_HI = 14.0, 320.0           # bass only; the 300 Hz-3 kHz reference levels are computed here (EQ is flat there)
NORM = 10 ** (70 / 20)             # store spectra relative to 70 dB SPL, so values are ~0.01..10

cal = np.loadtxt(os.path.join(repo, "cal", "MM-1C_90deg.txt"), comments="*")
fq = np.fft.rfftfreq(NFFT, 1 / SR)
i0, i1 = np.searchsorted(fq, F_LO), np.searchsorted(fq, F_HI)
calc = np.interp(np.log10(np.maximum(fq, 1)), np.log10(cal[:, 0]), cal[:, 1])


def load(path):
    sr, x = wavfile.read(path); assert sr == SR
    return x.astype(float)


def spec_full(path):
    x = load(path)
    n_end = T0 + int(0.5 * SR); x = np.pad(x, (0, max(0, n_end - len(x))))[:n_end]
    fade = int(0.125 * SR); x[-fade:] *= 0.5 * (1 + np.cos(np.linspace(0, np.pi, fade)))
    return np.fft.rfft(x, NFFT) * 10 ** ((OFFSET - calc) / 20) / NORM


def spec(path):
    return spec_full(path)[i0:i1]


RG = np.geomspace(18, 3500, 700); RB = (RG > 300) & (RG < 3000)
_lo = np.searchsorted(fq, RG * 2 ** (-1 / 48)); _hi = np.maximum(np.searchsorted(fq, RG * 2 ** (1 / 48)), _lo + 1)


def ref_db(Hs):
    """mid level as in design_eq.py: 1/24-oct power smoothing, power average over positions, mean dB 300 Hz-3 kHz"""
    ps = []
    for H in Hs:
        cs = np.concatenate([[0], np.cumsum(np.abs(H) ** 2)]); ps.append((cs[_hi] - cs[_lo]) / (_hi - _lo))
    return float(np.mean(10 * np.log10(np.mean(ps, axis=0))[RB]) + 70)


def pack(H):
    # interleaved re, im with 4 significant digits
    return [float(f"{v:.4g}") for v in np.column_stack([H.real, H.imag]).ravel()]


def pairs(folder, pat):
    d = {}
    for f in sorted(glob.glob(os.path.join(repo, "measurements", folder, "*.wav"))):
        m = re.search(pat, os.path.basename(f))
        if m: d.setdefault(m.group(2), {})[m.group(1)] = f
    return d


sets = {
    "seat": pairs("2026-11-18-pos-sweeps-L-R", r"\d ([LR]) (pos\d \w+) "),
    "dj": pairs("2026-11-18-dj-sweeps-L-R", r"\d ([LR]) DJ (\w+) "),
    "corner": pairs("2026-11-18-corner-sweeps-L-R", r"\d ([LR]) corner front (\w+) "),
}
sets["seat"] = {"seat": {("L" if "left" in f else "R"): f for f in glob.glob(os.path.join(repo, "measurements", "*first sweep*.wav"))}, **sets["seat"]}

data = {"f0": float(fq[i0]), "df": float(SR / NFFT), "n": int(i1 - i0), "norm_db": 70.0, "sets": {}}
data["ref"] = {}
for name, d in sets.items():
    data["sets"][name] = [{"pos": p, "L": pack(spec(lr["L"])), "R": pack(spec(lr["R"]))} for p, lr in d.items()]
    full = [(spec_full(lr["L"]), spec_full(lr["R"])) for lr in d.values()]
    data["ref"][name] = {"L": ref_db([a for a, _ in full]), "R": ref_db([b for _, b in full]), "LR": ref_db([a + b for a, b in full])}
    print(name, {k: round(v, 1) for k, v in data["ref"][name].items()})


# ---- design (device values as RBJ cookbook parameters) from the filter files ----
def read_eq(s):
    txt = open(os.path.join(repo, "eq", f"akustik_{s}.txt")).read()
    bands = [[float(f), float(g), float(q)] for f, g, q in
             re.findall(r"ON\s+PK\s+Fc\s+([\d.]+)\s*Hz\s+Gain\s+([-\d.]+)\s*dB\s+Q\s+([\d.]+)", txt)]
    hp = float(re.search(r"Butterworth 24 dB/oct ([\d.]+) Hz", txt).group(1))
    return bands, hp


bL, hp = read_eq("L"); bR, _ = read_eq("R")
data["design"] = {"L": bL, "R": bR, "hp": hp}

# ---- IR example: L at the seat, envelope in 1 ms blocks, first 700 ms after t0 ----
x = load(sets["seat"]["seat"]["L"])
blk = SR // 1000
seg = x[T0 % blk: T0 + 700 * blk]   # export has only 256 samples before t0
env = np.abs(seg[: len(seg) // blk * blk]).reshape(-1, blk).max(1)
data["ir"] = {"t0_ms": -(T0 // blk), "step_ms": 1, "db": [round(float(v), 1) for v in 20 * np.log10(env / env.max() + 1e-9)]}
# first 30 ms, full rate (decimated x4) for the zoom
z = x[T0 + 8 * blk: T0 + 30 * blk][::4]
data["ir_zoom"] = {"t0_ms": 8, "step_ms": 4 / 48, "v": [round(float(v), 3) for v in z / np.abs(z).max()]}

# ---- electrical check: measured vs predicted, log grid ----
grid = np.geomspace(15, 20000, 320)
fqe = np.fft.rfftfreq(1 << 18, 1 / SR)
el = {"f": [round(float(v), 2) for v in grid]}
folder = glob.glob(os.path.join(repo, "measurements", "2026-11-18-dsp-ele*trical"))[0]
for s, bands in (("L", bL), ("R", bR)):
    xx = load(glob.glob(os.path.join(folder, f"* {s} *.wav"))[0])
    n_end = T0 + int(0.5 * SR); xx = np.pad(xx, (0, max(0, n_end - len(xx))))[:n_end]
    fade = int(0.125 * SR); xx[-fade:] *= 0.5 * (1 + np.cos(np.linspace(0, np.pi, fade)))
    p = np.abs(np.fft.rfft(xx, 1 << 18)) ** 2
    cs = np.concatenate([[0], np.cumsum(p)])
    lo = np.searchsorted(fqe, grid * 2 ** (-1 / 96)); hi = np.maximum(np.searchsorted(fqe, grid * 2 ** (1 / 96)), lo + 1)
    m = 10 * np.log10((cs[hi] - cs[lo]) / (hi - lo))
    m -= m[(grid > 1000) & (grid < 5000)].mean()
    z = np.exp(-1j * 2 * np.pi * grid / SR)
    H = sosfreqz(butter(4, hp, btype="high", fs=SR, output="sos"), worN=grid, fs=SR)[1]
    for fc, g, q in bands:
        A = 10 ** (g / 40); w = 2 * np.pi * fc / SR; al = np.sin(w) / (2 * q); c = np.cos(w)
        H = H * ((1 + al * A) - 2 * c * z + (1 - al * A) * z ** 2) / ((1 + al / A) - 2 * c * z + (1 - al / A) * z ** 2)
    el[s] = {"meas": [round(float(v), 2) for v in m], "pred": [round(float(v), 2) for v in 20 * np.log10(np.abs(H))]}
data["electrical"] = el

# ---- earlier design stages (RBJ values, from the design runs on 2026-11-18, see eq-design-explained.md §7) ----
data["stages"] = [
    {"name": "Try 1: Q up to 10, cuts to −15 dB",
     "L": [[42.9, -4.9, 10], [43.6, -10.5, 10], [82.7, -2.2, 10], [94.5, -8.9, 10], [112.3, -9.2, 9.85], [126.4, -5.7, 10]],
     "R": [[42.2, -13.2, 10], [52.0, -13.4, 9.67], [62.3, -7.0, 3.98], [82.5, -14.4, 9.98], [89.4, -5.5, 10], [89.4, -3.5, 10], [122.7, -9.9, 8.86]]},
    {"name": "Try 2: Q up to 6, penalty per dB, merged",
     "L": [[43.4, -10.6, 6], [92.5, -6.8, 6], [112.6, -5.0, 6], [120.1, -4.9, 6]],
     "R": [[42.4, -9.1, 6], [52.4, -10.6, 6], [57.5, -3.1, 6], [66.7, -3.9, 6], [84.8, -15.0, 6], [122.4, -7.0, 6]]},
    {"name": "Final: Q up to 8, ±12 dB, on the DSP's grid", "L": bL, "R": bR},
]

tpl = open(os.path.join(repo, "explainer", "template.html")).read()
blob = json.dumps(data, separators=(",", ":"))
out = tpl.replace("/*__DATA__*/null", blob)
assert out != tpl, "placeholder not found"
with open(os.path.join(repo, "explainer", "eq-explained.html"), "w") as fh:
    fh.write(out)
print(f"wrote explainer/eq-explained.html ({len(out)/1e6:.2f} MB, data {len(blob)/1e6:.2f} MB)")

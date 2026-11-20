"""Rigid-box modal model of the room to compare candidate Sub8 positions (A, B, C).

Not a measurement: a first screening before the sub-only sweeps. Positions come from the
user's sketch of 2026-11-20 (not to scale: x and y scaled separately to 6.0 x 3.9 m), so +-0.2 m.

Model: rectangular room, rigid walls, uniform modal damping from the measured RT60 at 63 Hz,
modes summed up to 400 Hz, source = flat anechoic response (constant volume acceleration).
Validated first on the measured mains: R - L at the seat (the speaker response cancels).

Usage: uv run python analysis/sub_positions_modes.py . analysis/output
"""

import sys
from itertools import product
from pathlib import Path

import numpy as np
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(".")
out = Path(sys.argv[2]) if len(sys.argv) > 2 else root / "analysis/output"

C = 343.0
LX, LY, LZ = 6.0, 3.9, 2.8  # x along the speaker wall from the left wall, y away from the speaker wall
RT60 = 0.66  # 63 Hz octave, baseline mean
DELTA = 6.91 / RT60
FMAX_MODES = 400.0

# (x, y, z) in m
SOURCES = {
    "L main": (3.0, 0.33, 0.69),
    "R main": (5.47, 0.33, 0.69),
    "Sub A (speaker wall, L-TV)": (3.52, 0.25, 0.2),
    "Sub B (front of KALLAX)": (2.91, 1.61, 0.2),
    "Sub C (right wall, sofa end)": (5.6, 2.5, 0.2),
}
RECEIVERS = {
    "seat": (4.4, 2.75, 1.0),
    "DJ": (1.8, 0.75, 1.6),
}

# mode list
modes = []
nmax = [int(FMAX_MODES * 2 * L / C) + 1 for L in (LX, LY, LZ)]
for nx, ny, nz in product(*(range(n + 1) for n in nmax)):
    f = C / 2 * np.sqrt((nx / LX) ** 2 + (ny / LY) ** 2 + (nz / LZ) ** 2)
    if f <= FMAX_MODES:
        eps = (1 if nx == 0 else 2) * (1 if ny == 0 else 2) * (1 if nz == 0 else 2)
        modes.append((nx, ny, nz, f, eps))
modes_arr = np.array(modes)
N = modes_arr[:, :3]
FN = modes_arr[:, 3]
EPS = modes_arr[:, 4]


def psi(pos):
    x, y, z = pos
    return (np.cos(N[:, 0] * np.pi * x / LX) * np.cos(N[:, 1] * np.pi * y / LY)
            * np.cos(N[:, 2] * np.pi * z / LZ))


f = np.arange(15.0, 120.01, 0.25)
w = 2 * np.pi * f
WN = 2 * np.pi * FN
DEN = WN[None, :] ** 2 - w[:, None] ** 2 + 2j * DELTA * w[:, None]


def response(src, rcv):
    return (EPS * psi(src) * psi(rcv) / DEN).sum(axis=1)


def db(x):
    return 20 * np.log10(np.abs(x))


# room average (leakage proxy): mean |p|^2 over a grid filling the room
g = [np.linspace(0.1, L - 0.1, n) for L, n in ((LX, 13), (LY, 9), (LZ, 6))]
grid = list(product(*g))


def room_avg_db(src):
    ps = psi(src)
    acc = np.zeros_like(f)
    for r in grid:
        acc += np.abs((EPS * ps * psi(r) / DEN).sum(axis=1)) ** 2
    return 10 * np.log10(acc / len(grid))


# common reference: the L main at the seat, 300 Hz is outside the range, so use the model's
# L-at-seat level averaged 80-120 Hz as 0 dB (only relative comparisons are meaningful)
ref = db(response(SOURCES["L main"], RECEIVERS["seat"]))[(f >= 80) & (f <= 120)].mean()

print("Room modal model, sub position screening (2026-11-20)")
print(f"Room {LX} x {LY} x {LZ} m, RT60 {RT60} s -> delta {DELTA:.1f} 1/s, "
      f"{len(modes)} modes up to {FMAX_MODES:.0f} Hz")
print("Positions (x from left wall, y from speaker wall, z height), from the sketch, +-0.2 m:")
for k, v in {**SOURCES, **RECEIVERS}.items():
    print(f"  {k:30s} x={v[0]:.2f} y={v[1]:.2f} z={v[2]:.2f}")

# --- validation on the mains: R - L at the seat
d = np.load(root / "analysis/output/averages.npz")
mf, mL = d["L_24"]
_, mR = d["R_24"]
meas_diff = np.interp(f, mf, mR - mL)
mod_diff = (db(response(SOURCES["R main"], RECEIVERS["seat"]))
            - db(response(SOURCES["L main"], RECEIVERS["seat"])))
band = (f >= 25) & (f <= 90)
r = np.corrcoef(meas_diff[band], mod_diff[band])[0, 1]
print()
print("Validation: R - L at the seat, measured (7-position average) vs model, 25-90 Hz")
print(f"  correlation r = {r:.2f}; band means: measured {meas_diff[band].mean():+.1f} dB, "
      f"model {mod_diff[band].mean():+.1f} dB")
print("  Hz    meas  model")
for fx in (28, 35, 43, 51, 57, 68, 75, 89):
    i = np.argmin(np.abs(f - fx))
    print(f"  {fx:3d}  {meas_diff[i]:+5.1f}  {mod_diff[i]:+5.1f}")

# --- low-mode coupling table
print()
print("Coupling |psi| (1 = pressure maximum, 0 = node) for the modes below 65 Hz")
low = [i for i in np.argsort(FN) if 0 < FN[i] < 65]
names = list(SOURCES) + list(RECEIVERS)
pts = {**SOURCES, **RECEIVERS}
hdr = "  mode       Hz  " + "  ".join(f"{n.split(' (')[0]:>7s}" for n in names)
print(hdr)
for i in low:
    row = [abs(psi(pts[n])[i]) for n in names]
    print(f"  ({int(N[i,0])},{int(N[i,1])},{int(N[i,2])}) {FN[i]:6.1f}  "
          + "  ".join(f"{v:7.2f}" for v in row))

# --- band summary for the sub band
print()
print("Sub band 25-50 Hz (model, dB re L main at the seat 80-120 Hz). "
      "spread = max - min of the 1/24-oct-ish curve in the band (lower = smoother)")
print(f"  {'source':30s} {'seat':>6s} {'spread':>7s} {'DJ':>6s} {'spread':>7s} "
      f"{'room':>6s} {'seat-room':>9s}")
sb = (f >= 25) & (f <= 50)
curves = {}
for name, src in SOURCES.items():
    s = db(response(src, RECEIVERS["seat"])) - ref
    dj = db(response(src, RECEIVERS["DJ"])) - ref
    ra = room_avg_db(src) - ref
    curves[name] = (s, dj, ra)
    # energy means in the band
    em = lambda x: 10 * np.log10(np.mean(10 ** (x[sb] / 10)))
    print(f"  {name:30s} {em(s):6.1f} {np.ptp(s[sb]):7.1f} {em(dj):6.1f} {np.ptp(dj[sb]):7.1f} "
          f"{em(ra):6.1f} {em(s) - em(ra):9.1f}")
print("  seat-room: how much of the room's bass energy lands at the seat. Higher = same seat level "
      "with less energy in the room (less leakage).")

# --- each sub combined with the mains (mono, in phase, no delay/filters): does it fill?
print()
print("Peaks/dips at the seat and DJ, sub alone, 25-50 Hz (model)")
for name in [n for n in SOURCES if n.startswith("Sub")]:
    for ri, rname in enumerate(("seat", "DJ")):
        c = curves[name][ri]
        m = sb
        fi, ci = f[m], c[m]
        print(f"  {name:30s} {rname:4s} max {ci.max():+5.1f} dB at {fi[ci.argmax()]:.1f} Hz, "
              f"min {ci.min():+5.1f} dB at {fi[ci.argmin()]:.1f} Hz")

# --- plot
fig, axs = plt.subplots(1, 3, figsize=(16, 5), sharey=True)
for ax, (ri, title) in zip(axs, ((0, "seat"), (1, "DJ spot"), (2, "room average (leakage proxy)"))):
    for name, cs in curves.items():
        ls = "--" if "main" in name else "-"
        ax.semilogx(f, cs[ri], ls, label=name)
    ax.axvspan(25, 50, color="0.9", zorder=0)
    ax.set_title(title)
    ax.set_xlim(20, 120)
    ax.set_xticks([20, 25, 30, 40, 50, 60, 80, 100, 120])
    ax.set_xticklabels(["20", "25", "30", "40", "50", "60", "80", "100", "120"])
    ax.grid(True, which="both", alpha=0.3)
    ax.set_xlabel("Hz")
axs[0].set_ylabel("dB (model, re L main at seat 80-120 Hz)")
axs[0].set_ylim(-25, 25)
axs[2].legend(fontsize=8)
fig.suptitle("Modal model: candidate Sub8 positions (flat source, no crossover). Grey = sub band 25-50 Hz")
fig.tight_layout()
fig.savefig(out / "sub_positions_modes.png", dpi=110)

fig, ax = plt.subplots(figsize=(8, 4))
ax.semilogx(f, meas_diff, label="measured R - L (seat avg)")
ax.semilogx(f, mod_diff, label="model R - L")
ax.set_xlim(20, 120)
ax.grid(True, which="both", alpha=0.3)
ax.legend()
ax.set_title(f"Model validation, R - L at the seat (r = {r:.2f}, 25-90 Hz)")
fig.tight_layout()
fig.savefig(out / "sub_positions_validation.png", dpi=110)

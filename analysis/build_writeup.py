"""Plots for WRITEUP.md, all in one style.

Usage: build_writeup.py <repo> <out_dir>

Plots only: the curves come from analyse_eq_room.py (eq_room_curves.npz) and analyse_sub_c.py (sub_c_curves.npz),
so run those first (mise run analyse does). Writes writeup_*.png to <out_dir>.
Common style: 1/6-oct power averages, 0 dB = each curve's own 300 Hz-3 kHz level, log x 20-300 Hz,
fixed colours (grey = no EQ, blue = v1 flat, orange = v2 Harman; L violet, R aqua).
"""
import os, sys
import numpy as np
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
from matplotlib.ticker import NullFormatter

repo, out = sys.argv[1], sys.argv[2]
E = np.load(os.path.join(out, "eq_room_curves.npz"))
S = np.load(os.path.join(out, "sub_c_curves.npz"))
G = E["grid"]

INK, MUTED = "#1f1f1e", "#6b6a64"
FLAT, V1, V2 = "#8f8e88", "#2a78d6", "#eb6834"
CL, CR = "#6250d6", "#1baf7a"
plt.rcParams.update({"font.size": 10, "axes.edgecolor": MUTED, "axes.labelcolor": INK, "xtick.color": MUTED,
                     "ytick.color": MUTED, "axes.titlesize": 11, "axes.titleweight": "bold", "axes.titlelocation": "left",
                     "axes.spines.top": False, "axes.spines.right": False, "legend.frameon": False, "legend.fontsize": 9,
                     "lines.linewidth": 1.8, "figure.dpi": 130, "savefig.bbox": "tight", "savefig.facecolor": "white"})
TICKS = [20, 30, 40, 50, 60, 80, 100, 150, 200, 300]
TICKS_SUB = [25, 30, 40, 50, 60, 80, 100, 120]
YLAB = "dB re 300 Hz–3 kHz level"


def xfmt(ax, lo=20, hi=300):
    ax.set_xscale("log"); ax.set_xlim(lo, hi)
    t = [x for x in (TICKS_SUB if hi <= 120 else TICKS) if lo <= x <= hi]; ax.set_xticks(t); ax.set_xticklabels([str(x) for x in t])
    ax.xaxis.set_minor_formatter(NullFormatter()); ax.grid(True, which="major", color="#e6e5e0", lw=0.8); ax.set_axisbelow(True)
    ax.set_xlabel("Hz")


def label_end(ax, x, y, text, color, f=None, dy=0):
    """direct label next to a curve at frequency f (default: right edge)"""
    f = f or ax.get_xlim()[1]
    ax.annotate(text, (f, np.interp(np.log10(f), np.log10(x), y) + dy), xytext=(4, 0), textcoords="offset points",
                color=INK, fontsize=9, va="center", annotation_clip=False,
                bbox=dict(boxstyle="round,pad=0.15", fc="white", ec=color, lw=1.2))


def save(fig, name):
    fig.savefig(os.path.join(out, name)); plt.close(fig); print("wrote", os.path.join(out, name))


def c(set_, w, tag, kind="meas"): return E[f"{set_}|{w}|{tag}|{kind}"]


# 1. baseline: L and R at the seat, no EQ, with the predicted axial modes
fig, ax = plt.subplots(figsize=(10, 4.6))
MODES = {"width 3.9 m": [44, 88, 132, 176], "length 6.0 m": [29, 57, 86, 114, 143, 172], "height 2.8 m": [61, 122, 184, 245]}
for i, (name, fs) in enumerate(MODES.items()):
    y0 = 27 - 2.2 * i
    for f in fs: ax.plot([f, f], [y0 - 0.7, y0 + 0.7], color=INK, lw=1.4)
    ax.text(310, y0, f"{name} axial modes", fontsize=8, color=MUTED, va="center")
ax.axhline(0, color=MUTED, lw=0.8)
ax.plot(G, c("seat", "L", "flat"), color=CL, label="L speaker"); ax.plot(G, c("seat", "R", "flat"), color=CR, label="R speaker")
for f, txt, w, dy in ((43, "43 Hz", "R", 2.2), (51.5, "51.5 Hz", "R", 2.2), (89, "89 Hz", "R", 2.2), (28, "28 Hz", "R", 2.2)):
    y = np.interp(np.log10(f), np.log10(G), c("seat", w, "flat"))
    ax.annotate(txt, (f, y), xytext=(0, 8), textcoords="offset points", ha="center", fontsize=8, color=INK)
ax.set_ylim(-20, 29); ax.set_yticks(range(-20, 21, 10)); xfmt(ax); ax.set_ylabel(YLAB); ax.legend(loc="lower left")
ax.set_title("Before: seat, no EQ (7 mic positions, power average, 1/6 oct)")
save(fig, "writeup_baseline.png")

# 2. the EQ filters (as loaded on the DSP, incl. the 29.8 Hz HPF)
fig, axs = plt.subplots(1, 2, figsize=(10, 3.8), sharey=True)
for ax, s in zip(axs, "LR"):
    ax.axhline(0, color=MUTED, lw=0.8)
    ax.plot(G, E[f"filter|eq1|{s}"], color=V1, label="v1 flat"); ax.plot(G, E[f"filter|eq2|{s}"], color=V2, label="v2 Harman")
    xfmt(ax); ax.set_ylim(-18, 3); ax.set_title(f"Out {'1 (L)' if s == 'L' else '2 (R)'}")
axs[0].set_ylabel("filter gain, dB"); axs[0].legend(loc="lower right")
save(fig, "writeup_filters.png")

# 3. result in the room: flat vs v1 vs v2, seat and DJ, both speakers playing
fig, axs = plt.subplots(1, 2, figsize=(10, 4.2), sharey=True)
for ax, k, name in zip(axs, ("seat", "dj"), ("Seat", "DJ spot")):
    ax.plot(G, c(k, "L+R", "flat"), color=FLAT, label="no EQ (11-18)")
    ax.plot(G, c(k, "L+R", "eq1"), color=V1, label="v1 flat")
    ax.plot(G, c(k, "L+R", "eq2"), color=V2, label="v2 Harman")
    ax.plot(G, np.zeros_like(G), color=V1, lw=1, ls=":", label="v1 target")
    ax.plot(G, E["target_eq2"], color=V2, lw=1, ls="--", label="v2 target")
    xfmt(ax); ax.set_ylim(-20, 20); ax.set_title(f"{name}, L+R (7 positions)")
axs[0].set_ylabel(YLAB); axs[0].legend(loc="lower right")
save(fig, "writeup_eq_room.png")

# 4. simulated (11-18 IRs x filter files) vs measured with the EQ on (11-22)
fig, axs = plt.subplots(1, 2, figsize=(10, 4.0), sharey=True)
for ax, tag, col, name in zip(axs, ("eq1", "eq2"), (V1, V2), ("v1 flat", "v2 Harman")):
    ax.plot(G, c("seat", "L+R", tag, "sim"), color=col, lw=1.4, ls="--", label="predicted")
    ax.plot(G, c("seat", "L+R", tag), color=col, label="measured")
    xfmt(ax); ax.set_ylim(-15, 12); ax.set_title(f"Seat L+R, {name}")
    ax.legend(loc="lower right")
axs[0].set_ylabel(YLAB)
save(fig, "writeup_sim_vs_meas.png")

# 5. ringing: band energy left after t at the two worst modes
fig, axs = plt.subplots(1, 2, figsize=(10, 3.8), sharey=True)
t = E["decay_t"]
for ax, (s, f0) in zip(axs, (("L", 43), ("R", 84))):
    for tag, col, name in (("flat", FLAT, "no EQ"), ("eq1", V1, "v1 flat"), ("eq2", V2, "v2 Harman")):
        y = E[f"decay|{s}|{f0}|{tag}"]; ax.plot(t, y, color=col, label=name)
    ax.set_xlim(0, 500); ax.set_ylim(-50, 1); ax.grid(True, color="#e6e5e0", lw=0.8); ax.set_axisbelow(True)
    ax.set_xlabel("ms after the direct sound"); ax.set_title(f"Seat, {s} speaker, {f0} Hz (1/6 oct)")
axs[0].set_ylabel("energy still to come, dB re no EQ at 0 ms"); axs[0].legend(loc="upper right")
save(fig, "writeup_decay.png")

# 6. sub at spot C: mains alone vs mains + sub, per preset
F = S["fit"]
fig, axs = plt.subplots(2, 2, figsize=(10, 7), sharex=True, sharey=True)
for r, (tag, col, name) in enumerate((("eq1", V1, "v3 = v1 + sub"), ("eq2", V2, "v4 = v2 + sub"))):
    for j, (g, gname) in enumerate((("seat", "seat"), ("dj", "DJ spot"))):
        ax = axs[r, j]
        ax.plot(F, S[f"target|{tag}"], color=INK, lw=1, ls="--", label="target")
        ax.plot(F, S[f"{tag}|{g}|mains"], color=FLAT, label="mains alone")
        ax.plot(F, S[f"{tag}|{g}|with_sub"], color=col, label="mains + sub")
        xfmt(ax, 25, 120); ax.set_ylim(-20, 15); ax.set_title(f"{name}, {gname}")
        if j == 0: ax.set_ylabel(YLAB)
        if r == 0: ax.set_xlabel("")
        ax.legend(loc="lower right")
save(fig, "writeup_sub.png")

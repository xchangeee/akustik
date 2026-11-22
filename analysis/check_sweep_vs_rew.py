"""Validation of tools/sweep.py: REW and Python sweeps of the same setup, compared pair by pair.

Usage: check_sweep_vs_rew.py [--t0-info] <plot.png> <rew.wav> <py.wav> <f_lo> <f_hi> <tol_db> [<rew.wav> <py.wav> <f_lo> <f_hi> <tol_db> ...]

Per pair (same output and preset; no mic cal needed, it cancels in the difference):
- level difference py - rew vs frequency (500 ms window as the other scripts, 1/24 oct power smoothing):
  mean offset and max |difference| within f_lo..f_hi; PASS if max |difference| <= tol_db
- t=0 offset: IR peak position py - rew in samples (sub-sample by parabolic interpolation), PASS if within +-1;
  with --t0-info only printed (the mic was re-placed between the two, so the delay may differ)
- noise: IR level before t=0 (samples 0..200) and in the last 200 ms, dB re full scale
A constant level offset (e.g. +-3 dB) means a level convention differs (sweep level peak vs RMS); the mean offset
is printed so it can be fixed in the plan instead of in the data.
Pass criteria: docs/plans/python-sweep.md ("Validation run sheet").
"""
import os, sys
import numpy as np
from scipy.io import wavfile
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt

T0, SR, NFFT = 256, 48000, 1 << 18


def load(p):
    sr, x = wavfile.read(p)
    assert sr == SR, f"{p}: {sr} Hz"
    return x.astype(float)


def spectrum(x, win_ms=500, frac=24):
    n_end = T0 + int(win_ms / 1000 * SR)
    x = np.pad(x, (0, max(0, n_end - len(x))))[:n_end].copy()
    fade = int(0.25 * win_ms / 1000 * SR)
    x[-fade:] *= 0.5 * (1 + np.cos(np.linspace(0, np.pi, fade)))
    p = np.abs(np.fft.rfft(x, NFFT)) ** 2
    f = np.fft.rfftfreq(NFFT, 1 / SR)
    grid = np.geomspace(15, 20000, 1200)
    cs = np.concatenate([[0], np.cumsum(p)])
    lo = np.searchsorted(f, grid * 2 ** (-0.5 / frac))
    hi = np.maximum(np.searchsorted(f, grid * 2 ** (0.5 / frac)), lo + 1)
    return grid, 10 * np.log10((cs[hi] - cs[lo]) / (hi - lo) + 1e-30)


def peak_pos(x):
    i = int(np.argmax(np.abs(x)))
    a, b, c = np.abs(x[i - 1:i + 2])
    den = a - 2 * b + c
    return i + (0.5 * (a - c) / den if den else 0.0)


def rms_db(x):
    return 20 * np.log10(np.sqrt(np.mean(x ** 2)) + 1e-30)


def main():
    args = sys.argv[1:]
    t0_info = "--t0-info" in args
    args = [x for x in args if x != "--t0-info"]
    if len(args) < 6 or (len(args) - 1) % 5:
        sys.exit(__doc__)
    plot, groups = args[0], [args[i:i + 5] for i in range(1, len(args), 5)]
    fig, axs = plt.subplots(len(groups), 1, figsize=(12, 3.8 * len(groups)), squeeze=False)
    all_ok = True
    for ax, (rp, pp, lo, hi, tol) in zip(axs[:, 0], groups):
        lo, hi, tol = float(lo), float(hi), float(tol)
        r, p = load(rp), load(pp)
        g, sr_ = spectrum(r)
        _, sp_ = spectrum(p)
        d = sp_ - sr_
        sel = (g >= lo) & (g <= hi)
        k = np.argmax(np.abs(d[sel]))
        dt = peak_pos(p) - peak_pos(r)
        ok_lvl, ok_t = abs(d[sel][k]) <= tol, t0_info or abs(dt) <= 1
        all_ok &= ok_lvl and ok_t
        print(f"=== {os.path.basename(rp)}  vs  {os.path.basename(pp)}")
        print(f"  lengths {len(r)} / {len(p)} samples; IR peak {20 * np.log10(np.abs(r).max()):.2f} / {20 * np.log10(np.abs(p).max()):.2f} dBFS")
        print(f"  py - rew, {lo:.0f}-{hi:.0f} Hz (1/24 oct): mean {d[sel].mean():+.3f} dB, max |{abs(d[sel][k]):.3f}| dB at {g[sel][k]:.1f} Hz"
              f"  -> {'PASS' if ok_lvl else 'FAIL'} (tol {tol} dB)")
        print(f"  after removing the mean offset: max |{np.max(np.abs(d[sel] - d[sel].mean())):.3f}| dB")
        for a, b in [(20, 50), (50, 200), (200, 1000), (1000, 5000), (5000, 20000)]:
            bb = (g >= a) & (g < b)
            print(f"    {a:>5}-{b:<5} Hz: mean {d[bb].mean():+.3f}  max |{np.abs(d[bb]).max():.3f}| dB")
        print(f"  t=0: IR peak py - rew = {dt:+.2f} samples -> {'info only' if t0_info else 'PASS' if ok_t else 'FAIL'}{'' if t0_info else ' (+-1)'}")
        print(f"  noise before t=0: {rms_db(r[:200]):.1f} / {rms_db(p[:200]):.1f} dBFS; last 200 ms: "
              f"{rms_db(r[-int(0.2 * SR):]):.1f} / {rms_db(p[-int(0.2 * SR):]):.1f} dBFS (rew / py)")
        ax.semilogx(g, d, "k", lw=1)
        ax.axhspan(-tol, tol, color="tab:green", alpha=0.15)
        ax.axvspan(lo, hi, color="grey", alpha=0.06)
        ax.set_ylim(-1, 1); ax.set_xlim(15, 20000); ax.grid(True, which="both", alpha=0.3)
        ax.set_title(f"{os.path.basename(pp)} - {os.path.basename(rp)} (1/24 oct, 500 ms window); green = +-{tol} dB")
        ax.set_ylabel("dB")
    axs[-1, 0].set_xlabel("Hz")
    plt.tight_layout(); plt.savefig(plot, dpi=110)
    print("plot:", plot)
    print("ALL PASS" if all_ok else "NOT ALL PASS")


if __name__ == "__main__":
    main()

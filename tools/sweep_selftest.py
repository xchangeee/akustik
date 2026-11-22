"""Offline self-test of tools/sweep.py's processing (no audio, no DSP, no REW).

Usage: uv run python tools/sweep_selftest.py <plan.json> <set> <ir.wav> [<ir.wav> ...]   (mise run sweep-selftest)

For each REW IR export it simulates what the UMC would record: the unit-amplitude stimulus convolved with that IR
(REW's IR scale: the IR level goes with the sweep level) at a buffer latency, plus a loopback (a gain at the same
latency), plus noise; on a copy also 1 % second-harmonic distortion. Then it runs sweep.process() and checks:
- the exported IR has the same length, t=0 and peak position as the REW file;
- its spectrum (500 ms window, 1/24 oct) matches the REW file within 0.02 dB from 20 Hz to 20 kHz (with the
  distortion from 40 Hz: a long IR carries the harmonic IR into t>0 below ~30 Hz, in REW as well);
- the THD comes out near 1 % on the distorted copy and near 0 on the clean one.
Before that, synthetic paths with an exact truth (flat, 2 Hz and 5 Hz high-pass) at the real latency: 10-100 Hz
within 0.02 dB (this catches low-end processing errors that the REW IRs can't; see the 2026-11-22 regularisation bug).
Exit code 1 if anything fails.
"""
import json, os, sys
import numpy as np
from scipy.io import wavfile
from scipy.signal import fftconvolve

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sweep  # noqa: E402

SR = 48000


def spectrum(x, t0=256, win_ms=500, frac=24):
    n_end = t0 + int(win_ms / 1000 * SR)
    x = np.pad(x.astype(float), (0, max(0, n_end - len(x))))[:n_end]
    fade = int(0.25 * win_ms / 1000 * SR)
    x[-fade:] *= 0.5 * (1 + np.cos(np.linspace(0, np.pi, fade)))
    nfft = 1 << 18
    p = np.abs(np.fft.rfft(x, nfft)) ** 2
    f = np.fft.rfftfreq(nfft, 1 / SR)
    grid = np.geomspace(20, 20000, 600)
    cs = np.concatenate([[0], np.cumsum(p)])
    lo = np.searchsorted(f, grid * 2 ** (-0.5 / frac))
    hi = np.maximum(np.searchsorted(f, grid * 2 ** (0.5 / frac)), lo + 1)
    return grid, 10 * np.log10((cs[hi] - cs[lo]) / (hi - lo) + 1e-30)


def harmonic2(sw, sr):
    """sin(2 phi(t)) of the sweep, same pre-roll/fades: the 2nd harmonic of a log sweep, no DC."""
    n, f1, f2 = int(sw["length_samples"]), float(sw["f_start_hz"]), float(sw["f_end_hz"])
    t = np.arange(n) / sr
    L = n / sr / np.log(f2 / f1)
    s = np.sin(2 * 2 * np.pi * f1 * L * (np.exp(t / L) - 1))
    s[2 * f1 * np.exp(t / L) > sr / 2] = 0  # nothing above Nyquist
    fi, fo = int(sw["fade_in_ms"] / 1000 * sr), int(sw["fade_out_ms"] / 1000 * sr)
    s[:fi] *= np.sin(np.linspace(0, np.pi / 2, fi)) ** 2
    s[-fo:] *= np.cos(np.linspace(0, np.pi / 2, fo)) ** 2
    return np.concatenate([np.zeros(int(sw["pre_s"] * sr)), s, np.zeros(int(sw["silence_s"] * sr))])


def simulate(h_rew, unit, amp, latency, noise_dbfs, hd2, rng, h2=None):
    """Recording (frames, 2): input = unit ⊛ IR (t=0 of the IR at `latency`), loopback = played at `latency`."""
    T0 = 256
    played = amp * unit
    drive = played + hd2 * amp * h2 if hd2 else played  # 2nd harmonic at hd2 of the fundamental
    y = fftconvolve(drive / amp, h_rew)  # IR in REW's scale = response to the unit sweep
    y = np.roll(np.pad(y, (0, latency)), latency - T0)[:len(unit)]
    loop = np.roll(np.pad(played * 10 ** (12 / 20), (0, latency)), latency)[:len(unit)]  # +12 dB loopback gain
    n = 10 ** (noise_dbfs / 20)
    return np.stack([y + n * rng.standard_normal(len(y)), loop + n * rng.standard_normal(len(y))], axis=1)


def main():
    plan_path, set_name, files = sys.argv[1], sys.argv[2], sys.argv[3:]
    cfg, steps = sweep.resolve_set(json.load(open(plan_path)), set_name)
    unit, played, L = sweep.make_stimulus(cfg["sweep"], cfg["sr"])
    amp = sweep.peak_amplitude(cfg["sweep"]["level_dbfs"])
    rng = np.random.default_rng(1)
    h2 = harmonic2(cfg["sweep"], cfg["sr"])
    noise = float(os.environ.get("SELFTEST_NOISE_DBFS", -120))
    ok = True
    # 1. Synthetic paths with an exact truth: flat (pure delay) and 1st-order high-passes at 2 and 5 Hz, at the real
    #    stream latency (12580 samples). Magnitude re 1 kHz at 10-100 Hz in the 500 ms window must match within
    #    0.02 dB. (REW IRs can't catch low-end errors: they don't contain the real path's long low-frequency tail.)
    from scipy.signal import butter, lfilter, sosfreqz
    F = np.array([10, 12, 15, 20, 25, 30, 40, 50, 70, 100])
    nf = 1 << 18
    fr = np.fft.rfftfreq(nf, 1 / SR)
    for fc in (None, 2.0, 5.0):
        y = played if fc is None else lfilter(*butter(1, fc, "high", fs=SR), played)
        y = np.concatenate([np.zeros(12580), y])[:len(played)]
        ir, _ = sweep.process(np.stack([y, y], 1), unit, cfg, L)
        H = np.abs(np.fft.rfft(ir[:256 + 24000], nf))
        got = 20 * np.log10(np.interp(F, fr, H) / np.interp(1000, fr, H))
        true = np.zeros(len(F)) if fc is None else 20 * np.log10(np.abs(
            sosfreqz(butter(1, fc, "high", fs=SR, output="sos"), worN=np.append(F, 1000), fs=SR)[1]))
        true = true[:len(F)] - (true[-1] if fc else 0)
        err = np.max(np.abs(got - true))
        ok &= err <= 0.02
        print(f"{'FAIL' if err > 0.02 else 'ok  '} synthetic path {'flat' if fc is None else f'HPF {fc} Hz'}: "
              f"max |error| 10-100 Hz {err:.3f} dB")
    # 2. REW IR exports as paths
    for path in files:
        sr, h = wavfile.read(path)
        assert sr == SR
        h = h.astype(np.float64)
        for hd2, latency in ((0.0, 437), (0.01, 151)):
            rec = simulate(h, unit, amp, latency, noise, hd2, rng, h2)
            ir, m = sweep.process(rec, unit, cfg, L)
            g, a = spectrum(h)
            _, b = spectrum(ir)
            d = b - a
            pk_rew, pk_py = int(np.argmax(np.abs(h))), int(np.argmax(np.abs(ir)))
            fails = []
            if len(ir) != len(h):
                fails.append(f"length {len(ir)} vs REW {len(h)}")
            if pk_py != pk_rew:
                fails.append(f"peak at {pk_py} vs REW {pk_rew}")
            f_lo = 40 if hd2 else 20  # with distortion: a long IR (seat: 1.7 s) carries the harmonic IR into t>0 below ~30 Hz
            sel = g >= f_lo
            if np.max(np.abs(d[sel])) > 0.02:
                fails.append(f"spectrum off by up to {np.max(np.abs(d[sel])):.3f} dB at {g[sel][np.argmax(np.abs(d[sel]))]:.0f} Hz")
            if hd2 and abs(m["thd_pct"] - 100 * hd2) > 0.2 * 100 * hd2:
                fails.append(f"THD {m['thd_pct']:.2f} %, expected ~{100 * hd2:.1f} %")
            if not hd2 and m["thd_pct"] > 0.05:
                fails.append(f"THD {m['thd_pct']:.3f} % on a clean path")
            ok &= not fails
            print(f"{'FAIL' if fails else 'ok  '} {os.path.basename(path)}  hd2 {hd2:.2f} latency {latency}: len {len(ir)}/{len(h)}, "
                  f"peak {pk_py}/{pk_rew}, max |dB diff| {f_lo}-20k {np.max(np.abs(d[sel])):.4f} (20-20k {np.max(np.abs(d)):.4f}), delay {m['delay_ms']:.3f} ms, "
                  f"THD {m['thd_pct']:.3f} %, SNR {m['snr_db']:.0f} dB, loopback {m['loopback_peak_dbfs']:+.1f} dBFS")
            for f_ in fails:
                print("       " + f_)
    print("selftest " + ("PASSED" if ok else "FAILED"))
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()

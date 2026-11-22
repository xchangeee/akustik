"""Low-end magnitude of sweep IRs (and their loopback, recomputed from raw/) vs a tone_response.py table.

Usage: uv run python tools/lf_check.py <tones.txt> <set folder> [<set folder> ...]
Per IR: magnitude at the tone frequencies re 1 kHz (500 ms window), next to the tone result; for sweep.py sets also
the loopback IR recomputed from raw/<name>.flac with the set's stimulus.
"""
import glob, json, os, sys
import numpy as np, soundfile as sf
from scipy.io import wavfile
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sweep  # noqa: E402

SR = 48000


def curve(seg, F):
    H = np.abs(np.fft.rfft(seg, 1 << 18)); f = np.fft.rfftfreq(1 << 18, 1 / SR)
    ref = 20 * np.log10(np.interp(1000, f, H))
    return [20 * np.log10(np.interp(f0, f, H)) - ref for f0 in F]


def main():
    rows = [l.split() for l in open(sys.argv[1]).read().splitlines()[2:]]
    F = [float(r[0]) for r in rows if float(r[0]) != 1000]
    print(f"{'':34s}" + "".join(f"{f:>7.0f}" for f in F))
    print(f"{'tones In (truth)':34s}" + "".join(f"{float(r[1]):+7.2f}" for r in rows if float(r[0]) != 1000))
    print(f"{'tones loopback (truth)':34s}" + "".join(f"{float(r[2]):+7.2f}" for r in rows if float(r[0]) != 1000))
    for folder in sys.argv[2:]:
        name = os.path.basename(os.path.normpath(folder))
        js = os.path.join(folder, name + ".json")
        d = json.load(open(js)) if os.path.exists(js) else None
        for w in sorted(glob.glob(os.path.join(folder, "*.wav"))):
            x = wavfile.read(w)[1].astype(float)[:256 + 24000]
            print(f"{name[-14:] + ' ' + os.path.basename(w)[:-4]:34s}" + "".join(f"{v:+7.2f}" for v in curve(x, F)))
            rawf = os.path.join(folder, "raw", os.path.basename(w)[:-4] + ".flac")
            if d and os.path.exists(rawf):
                unit, _, _ = sweep.make_stimulus(d["sweep"], SR)
                rec, _ = sf.read(rawf)
                _, h = sweep.deconvolve([rec[:, 0], rec[:, 1]], unit, SR, d["sweep"]["f_start_hz"], d["sweep"]["f_end_hz"])
                pk = int(np.argmax(np.abs(h[:len(h) // 2])))
                print(f"{'   its loopback':34s}" + "".join(f"{v:+7.2f}" for v in curve(h[pk - 256:pk + 24000], F)))


if __name__ == "__main__":
    main()

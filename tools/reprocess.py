"""Recompute a sweep.py set's IRs from its raw recordings with the current sweep.py processing.

Usage: uv run python tools/reprocess.py <set folder> [--out <folder>]
Reads <set>.json (sweep parameters, t0, length) and raw/<name>.flac, rewrites <name>.wav (or writes into --out) and
updates each entry's numbers plus `reprocessed_with` (script version). REW isn't touched: run rew-load afterwards.
"""
import argparse, json, os, sys
import soundfile as sf
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sweep  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("folder"), ap.add_argument("--out")
    a = ap.parse_args()
    name = os.path.basename(os.path.normpath(a.folder))
    js = os.path.join(a.folder, f"{name}.json")
    d = json.load(open(js))
    cfg = dict(sweep=d["sweep"], sr=d["samplerate"], t0=d["t0_sample"], after_peak=d["after_peak_samples"])
    unit, _, L = sweep.make_stimulus(d["sweep"], d["samplerate"])
    out = a.out or a.folder
    os.makedirs(out, exist_ok=True)
    for e in d["sweeps"]:
        rec, sr = sf.read(os.path.join(a.folder, e["raw"]))
        ir, m = sweep.process(rec, unit, cfg, L)
        sweep.write_ir(os.path.join(out, e["wav"]), ir, sr)
        e.update(m, reprocessed_with=sweep.SCRIPT_VERSION)
        print(f"  {e['title']}: delay {m['delay_ms']:.3f} ms, IR peak {m['ir_peak_dbfs']:+.2f} dBFS")
    if not a.out:
        json.dump(d, open(js, "w"), indent=1)


if __name__ == "__main__":
    main()

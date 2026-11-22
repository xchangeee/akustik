"""Load a set measured by tools/sweep.py into REW and save it as <set>.mdat (for later, or when REW was closed).

Usage: mise run rew-load <set folder> [REW API URL]   (= uv run python tools/rew_load.py ...)

Reads only the set folder: <set>.json (sweep names, cal file, SPL offset, t=0) and the IR WAVs. REW API address:
the 2nd argument, else the plan named in <set>.json (if it still exists), else REW's default. Clears REW first (asks if REW holds measurements), switches REW's cal file to the
set's for the import and back afterwards, imports every sweep in measuring order, then "Save all".
"""
import json, os, sys
from scipy.io import wavfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from rew_api import Rew  # noqa: E402

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def main():
    if len(sys.argv) not in (2, 3):
        sys.exit(__doc__)
    folder = os.path.abspath(sys.argv[1])
    name = os.path.basename(os.path.normpath(folder))
    js = os.path.join(folder, f"{name}.json")
    if not os.path.exists(js):
        sys.exit(f"{js} not found: only sets written by tools/sweep.py can be loaded")
    d = json.load(open(js))
    plan_rew = None
    try:  # the REW API address from the plan the set was measured with, if it's still there
        plan_rew = json.load(open(os.path.join(REPO, d["plan"])))["rew"]["api"]
    except (OSError, KeyError, ValueError):
        pass
    rew = Rew(sys.argv[2] if len(sys.argv) == 3 else plan_rew or "http://127.0.0.1:4735")
    if not rew.running():
        sys.exit(f"REW isn't reachable at {rew.api}. Start the REW beta with the API on.")
    held = rew.measurements()
    if held:
        print(f"REW holds {len(held)} measurement(s), e.g. {', '.join(list(held)[:3])}")
        if input("  Save them first if you need them. Type 'clear' to remove ALL measurements from REW: ").strip() != "clear":
            sys.exit("Nothing changed.")
        rew.delete_all()
    cal_before = rew.input_cal()[0]
    want = os.path.join(REPO, d["mic_cal"]) if d.get("mic_cal") else None
    if want and cal_before != want:
        rew.set_cal_file(want)
        print(f"REW cal file switched to {d['mic_cal']} for the import")
    try:
        sweeps = sorted(d["sweeps"], key=lambda e: e["index"])
        for e in sweeps:
            sr, x = wavfile.read(os.path.join(folder, e["wav"]))
            rew.import_ir(e["title"], x, sr, d["t0_sample"], d["spl_offset_db"], bool(d.get("mic_cal")))
            print(f"  imported {e['title']}")
        mdat = os.path.join(folder, f"{name}.mdat")
        rew.save_all(mdat)
        print(f"{len(sweeps)} sweeps -> {os.path.relpath(mdat, REPO)}")
    finally:
        if want and cal_before != want:
            rew.set_cal_file(cal_before)
            print(f"REW cal file switched back to {cal_before or 'NONE'}")


if __name__ == "__main__":
    main()

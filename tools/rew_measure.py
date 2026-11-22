"""Run one measurement set with REW (5.40 beta, API at http://127.0.0.1:4735), semi-automatic.

Usage: uv run python tools/rew_measure.py <set> [--plan docs/plans/next-session-eq-sub.json] [--date YYYY-MM-DD] [--dry-run]

Without a REW Pro licence the API can't start a sweep or set the name/level/sweep/timing (HTTP 401), so per sweep you
only click Start in REW's Measure dialog. The script does the rest:
- before each sweep: sets REW's output channel, tells you when to move the mic or recall a DSP preset;
- after each sweep (it notices the new measurement by itself): renames it `<n> <L|R|S> <position> <tag>`,
  exports the IR as WAV (32-bit float, t=0 at sample 256, not normalised, no window: identical to REW's GUI export,
  checked 2026-11-22), prints the loopback delay, saves the REW project as measurements/<date>/<set>/<set>.mdat.
While it waits for a sweep: type r + Enter to redo the previous sweep, q + Enter to quit.
Resuming: sweeps already in REW *and* on disk are skipped, so after a quit run the same command again.
"""
import argparse, base64, datetime, json, os, select, sys, time, urllib.error, urllib.request
import numpy as np
from scipy.io import wavfile

API = "http://127.0.0.1:4735"
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
T0 = 256  # sample index of t=0 in the exported WAV (measurements/README.md)


# ---------- REW API ----------
def call(method, path, body=None, timeout=60):
    data = None if body is None else json.dumps(body).encode()
    req = urllib.request.Request(API + path, data=data, method=method, headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            txt = r.read().decode()
    except urllib.error.HTTPError as e:
        sys.exit(f"REW API {method} {path} -> HTTP {e.code}: {e.read().decode()[:300]}")
    except urllib.error.URLError as e:
        sys.exit(f"REW API not reachable at {API} ({e.reason}). Is the REW beta running with the API enabled?")
    try:
        return json.loads(txt) if txt else None
    except json.JSONDecodeError:
        return txt


get = lambda p: call("GET", p)
post = lambda p, b: call("POST", p, b)


def measurements():
    """REW's measurement list as [(index, summary)], in REW order."""
    m = get("/measurements") or {}
    return sorted(((int(k), v) for k, v in m.items()), key=lambda kv: kv[0])


def setup(rew):
    """Set what the free API allows (channels), check the rest; exit if something is off."""
    post("/application/blocking", False)
    post("/audio/java/input-channel", {"channel": rew["input_channel"]})
    post("/audio/java/ref-input-channel", {"channel": rew["ref_input_channel"]})
    post("/audio/java/ref-output-channel", {"channel": rew["ref_output_channel"]})
    lvl, sw, tref = get("/measure/level"), get("/measure/sweep/configuration"), get("/measure/timing/reference")
    calpath = (get("/audio/input-cal").get("calDataAllInputs") or {}).get("calFilePath", "")
    sr = get("/audio/samplerate")["value"]
    print(f"REW {get('/version')['message']}")
    print(f"  input {get('/audio/java/input-channel')['channel']}, loopback in {get('/audio/java/ref-input-channel')['channel']}"
          f" / out {get('/audio/java/ref-output-channel')['channel']}, timing {tref}, {sr:.0f} Hz")
    print(f"  sweep {sw['length']} {sw['startFrequency']}-{sw['endFrequency']} Hz at {lvl['value']} {lvl['unit']}")
    print(f"  mic cal: {calpath or 'NONE'}")
    want = rew["sweep"]
    problems = []
    if abs(lvl["value"] - rew["level_dbfs"]) > 0.01 or lvl["unit"] != "dBFS":
        problems.append(f"sweep level should be {rew['level_dbfs']} dBFS")
    if any(sw[k] != want[k] for k in want):
        problems.append(f"sweep should be {want['length']} {want['startFrequency']}-{want['endFrequency']} Hz")
    if tref != rew["timing_reference"]:
        problems.append(f"timing reference should be {rew['timing_reference']}")
    if rew["cal_file_contains"] not in calpath:
        problems.append(f"mic cal file should be {rew['cal_file_contains']}")
    if sr != 48000:
        problems.append("sample rate should be 48 kHz")
    if problems:
        sys.exit("Set in REW's Measure dialog / preferences, then run again:\n  " + "\n  ".join(problems))


def export_wav(uuid, path):
    r = get(f"/measurements/{uuid}/impulse-response?normalised=false")
    x = np.frombuffer(base64.b64decode(r["data"]), ">f4").astype(np.float64) / 100.0  # percent -> full scale
    i0 = int(round(-r["startTime"] * r["sampleRate"]))  # index of t=0 (loopback reference)
    if i0 < T0:
        x, i0 = np.concatenate([np.zeros(T0 - i0), x]), T0
    wavfile.write(path, int(r["sampleRate"]), x[i0 - T0:].astype(np.float32))
    return r


def save_project(path):
    post("/measurements/command", {"command": "Save all", "parameters": [path]})


def wait_for_sweep(before):
    """Poll REW for a new measurement; meanwhile read 'r'/'q' from the keyboard. Returns summary, 'r' or 'q'."""
    t = time.time()
    while True:
        ready, _, _ = select.select([sys.stdin], [], [], 1.0)
        if ready:
            a = sys.stdin.readline().strip().lower()
            if a in ("r", "q"):
                return a
        new = [v for _, v in measurements() if v["uuid"] not in before]
        if new:
            return new[0]
        print(f"\r  waiting for Start in REW ... {time.time() - t:4.0f} s  (r+Enter redo previous, q+Enter quit) ",
              end="", flush=True)


# ---------- plan ----------
def build_steps(plan, set_name):
    s = plan["sets"][set_name]
    positions = plan["position_groups"][s["positions"]]
    channels = plan["channel_groups"][s["channels"]]
    steps = []
    for pos in positions:
        for preset, tag in s["presets"]:
            for ch in channels:
                steps.append(dict(pos=pos, preset=preset, tag=tag, ch=ch,
                                  title=f"{ch['n']} {ch['side']} {pos['name']} {tag}"))
    return s, steps


def changes(st, mic, preset, plan):
    todo = []
    if st["pos"]["name"] != mic:
        todo.append(f"MOVE MIC -> {st['pos']['name']}: {st['pos']['mic']}")
    if st["preset"] != preset:
        todo.append(f"RECALL {st['preset']} in the configurator (name: {plan['presets'][st['preset']]})")
    return todo


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("set")
    ap.add_argument("--plan", default=os.path.join(REPO, "docs", "plans", "next-session-eq-sub.json"))
    ap.add_argument("--date", default=datetime.date.today().isoformat())
    ap.add_argument("--dry-run", action="store_true", help="print the run without talking to REW")
    a = ap.parse_args()
    plan = json.load(open(a.plan))
    if a.set not in plan["sets"]:
        sys.exit(f"unknown set {a.set!r}; sets in {os.path.relpath(a.plan, REPO)}: {', '.join(plan['sets'])}")
    s, steps = build_steps(plan, a.set)
    folder = os.path.join(REPO, "measurements", a.date, a.set)
    mdat = os.path.join(folder, f"{a.set}.mdat")
    wav = lambda st: os.path.join(folder, st["title"] + ".wav")
    print(f"Set {a.set}: {len(steps)} sweeps -> {os.path.relpath(folder, REPO)}/")

    if a.dry_run:
        mic = preset = None
        for i, st in enumerate(steps, 1):
            for t in changes(st, mic, preset, plan):
                print("  >>> " + t)
            mic, preset = st["pos"]["name"], st["preset"]
            print(f"  #{i:2d} output {st['ch']['rew_output']}: {st['title']}")
        return

    setup(plan["rew"])
    os.makedirs(folder, exist_ok=True)

    # what is done already? (in REW and on disk)
    in_rew = {v["title"]: v for _, v in measurements()}
    planned = {st["title"] for st in steps}
    foreign = [t for t in in_rew if t not in planned]
    if foreign:
        print(f"\nREW holds {len(foreign)} measurement(s) that aren't part of {a.set}:")
        for t in foreign[:10]:
            print("   ", t)
        if input("  Save them first if you need them. Type 'clear' to remove ALL measurements from REW: ").strip() != "clear":
            sys.exit("Nothing changed.")
        call("DELETE", "/measurements")
        in_rew = {}
    done = [st["title"] in in_rew and os.path.exists(wav(st)) for st in steps]
    half = [st["title"] for st, d in zip(steps, done) if not d and (st["title"] in in_rew or os.path.exists(wav(st)))]
    if half:
        sys.exit("These sweeps are only in REW or only on disk, not both; sort that out first:\n  " + "\n  ".join(half))
    if any(done):
        print(f"Resuming: {sum(done)} of {len(steps)} sweeps already done.")
    if s.get("before"):
        print("\nBefore this set: " + s["before"])
    print("\nOpen REW's Measure dialog. For each sweep, click Start; the name in the dialog doesn't matter.")

    mic = preset = None  # unknown at start: always tell
    last = None  # (step index, uuid) of the previous sweep, for redo
    quit_ = False
    while not quit_:
        todo_i = [i for i, d in enumerate(done) if not d]
        if not todo_i:
            if last is None or input(f"\n  Set {a.set} complete. [Enter] finish   r + Enter = redo the last sweep: ").strip().lower() != "r":
                break
            res = "r"
        else:
            i = todo_i[0]
            st = steps[i]
            out = st["ch"]["rew_output"]
            post("/audio/java/output-channel", {"channel": out})
            print()
            for t in changes(st, mic, preset, plan):
                print("  >>> " + t)
            print(f"  #{i + 1}/{len(steps)} {st['title']}  (output {out} set; check the Measure dialog shows it)")
            res = wait_for_sweep({v["uuid"] for _, v in measurements()})
        if res == "q":
            quit_ = True
            break
        if res == "r":
            if last is None:
                print("\n  nothing to redo")
                continue
            pi, uuid = last
            call("DELETE", f"/measurements/{uuid}")
            os.remove(wav(steps[pi]))
            done[pi] = False
            last = None
            mic, preset = steps[pi]["pos"]["name"], steps[pi]["preset"]  # redo happens where the mic/preset still are
            print(f"\n  removed {steps[pi]['title']!r}; sweep it again")
            continue
        m = res
        call("PUT", f"/measurements/{m['uuid']}", {"title": st["title"]})
        r = export_wav(m["uuid"], wav(st))
        save_project(mdat)
        d_ms = r["delay"] * 1000
        target = st["pos"].get("delay_ms", {}).get(st["ch"]["side"])
        cmp_ = f", 2026-11-18: {target:.2f} ms ({(d_ms - target) / 1000 * 34300:+.0f} cm)" if target else ""
        print(f"\r  #{i + 1}/{len(steps)} {st['title']}: saved, delay {d_ms:.2f} ms{cmp_}" + " " * 30)
        done[i] = True
        last = (i, m["uuid"])
        mic, preset = st["pos"]["name"], st["preset"]

    n = sum(done)
    print(f"\n{a.set}: {n} of {len(steps)} sweeps done, project saved as {os.path.relpath(mdat, REPO)}")
    if n == len(steps) and input("  Remove all measurements from REW now (they're saved)? [y/N]: ").strip().lower() == "y":
        call("DELETE", "/measurements")
        print("  REW cleared.")


if __name__ == "__main__":
    main()

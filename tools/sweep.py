"""Measure one set: log sweep + loopback on the UMC, DSP preset recall over USB, IR export, optional REW import.

Usage: mise run measure <plan.json> <set> [--date YYYY-MM-DD] [--dry-run]
       (= uv run python tools/sweep.py <plan.json> <set> ...)

Everything session-specific comes from the plan file: sets, positions, channels, presets, audio device and channel
map, sweep parameters, checks, REW import. Its format: tools/README.md ("Plan file").
Nothing has a default in the code; a missing key stops the script and names the key.

Per sweep you only move the mic and press Enter. The script recalls the DSP preset when it changes (probe --recall,
read back and checked), plays the sweep on the sweep output and the loopback output in one full-duplex stream,
deconvolves mic and loopback against the stimulus, sets t=0 at the loopback IR peak and writes into
measurements/<date>/<set>/:
  <n> <L|R|S> <position> <tag>.wav   IR, 32-bit float, t=0 at sample 256, not normalised, no window, REW's length
  raw/<same name>.flac               the recording (24-bit, ch 1 = mic/input, ch 2 = loopback), for reprocessing
  raw/stimulus.flac                  the played sweep channel (once per set)
  <set>.json                         set info + one entry per sweep (preset read back, levels, SNR, delay, THD, ...)
  <set>.mdat                         REW project (when REW runs): every IR imported, "Save all" after each sweep
At the prompt: r = redo the previous sweep, q = quit. Sweeps already on disk are skipped (resume).

"""
import argparse, datetime, json, math, os, re, subprocess, sys, time
import numpy as np
from scipy.io import wavfile

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from rew_api import Rew, RewError  # noqa: E402

SCRIPT_VERSION = 2  # 2: low-end regularisation fixed (2026-11-22)
C_CM_PER_MS = 34.3  # speed of sound, for delay -> cm
# Sweep level as REW states it = the sweep's peak level (a sine of peak 1.0 = 0 dBFS). Measured 2026-11-22: with
# +3.01 dB here (an RMS guess) the IR came out +3.04 dB above REW's of the same electrical path, flat 200 Hz-20 kHz.
REW_LEVEL_TO_PEAK_DB = 0.0
RECALL_SETTLE_S = 2.0  # pause after a preset recall; the first sweep after a recall had SNR 27-32 dB instead of 52-56


def peak_amplitude(level_dbfs):
    return 10 ** ((level_dbfs + REW_LEVEL_TO_PEAK_DB) / 20)


# ---------- plan ----------
class PlanError(SystemExit):
    pass


def need(d, key, where):
    if not isinstance(d, dict) or key not in d:
        raise PlanError(f"plan: missing key {where}.{key}")
    return d[key]


def resolve_set(plan, set_name):
    """Everything one set needs, with the per-set overrides applied. Returns (cfg, steps)."""
    sets = need(plan, "sets", "plan")
    if set_name not in sets:
        raise PlanError(f"unknown set {set_name!r}; sets in the plan: {', '.join(sets)}")
    s = sets[set_name]
    w = f"sets.{set_name}"
    kind = need(s, "kind", w)
    if kind not in ("room", "closeup", "electrical"):
        raise PlanError(f"{w}.kind must be room, closeup or electrical, not {kind!r}")
    audio = need(plan, "audio", "plan")
    sweep = dict(need(plan, "sweep", "plan"))
    for k in ("length_samples", "f_start_hz", "f_end_hz", "level_dbfs", "fade_in_ms", "fade_out_ms", "pre_s", "silence_s"):
        need(sweep, k, "sweep")
    if "level_dbfs" in s:
        sweep["level_dbfs"] = s["level_dbfs"]
    for k, v in s.get("sweep", {}).items():  # per-set override of any sweep key
        if k not in sweep:
            raise PlanError(f"{w}.sweep.{k}: not a sweep key")
        sweep[k] = v
    checks = dict(need(plan, "checks", "plan"))
    checks.update(s.get("checks", {}))
    for k in ("clip_dbfs", "loopback_min_dbfs", "snr_min_db", "delay_tol_cm"):
        need(checks, k, "checks")
    ir = need(plan, "ir", "plan")
    rew = need(plan, "rew", "plan")
    cfg = dict(
        set=set_name, kind=kind, sweep=sweep, checks=checks,
        device=need(audio, "device", "audio"), sr=need(audio, "samplerate", "audio"),
        loop_out=need(audio, "loopback_out", "audio"), loop_in=need(audio, "loopback_in", "audio"),
        input=need(s, "input", w) if kind == "electrical" else need(audio, "mic_in", "audio"),
        mic_cal=None if kind == "electrical" else need(s, "mic_cal", w),
        t0=need(ir, "t0_sample", "ir"), after_peak=need(ir, "after_peak_samples", "ir"),
        probe=os.path.expanduser(need(need(plan, "dsp", "plan"), "probe", "dsp")),
        rew_import=need(rew, "import", "rew"), rew_api=need(rew, "api", "rew"),
        dbfs_at_94=need(rew, "dbfs_at_94db_spl", "rew"),
        before=s.get("before"),
        eq=need(s, "eq", w) if kind == "electrical" else None,
        tolerance_db=need(s, "tolerance_db", w) if kind == "electrical" else None,
        check_band_hz=need(s, "check_band_hz", w) if kind == "electrical" else None,
    )
    presets = need(plan, "presets", "plan")
    if kind == "electrical":
        positions = [{"name": need(s, "label", w), "mic": None}]
    else:
        positions = need(need(plan, "position_groups", "plan"), need(s, "positions", w), "position_groups")
    channels = need(need(plan, "channel_groups", "plan"), need(s, "channels", w), "channel_groups")
    steps = []
    for pos in positions:
        for preset, tag in need(s, "presets", w):
            p = need(presets, preset, "presets")
            need(p, "slot", f"presets.{preset}"), need(p, "name", f"presets.{preset}")
            for ch in channels:
                parts = [str(need(ch, "n", "channel")), need(ch, "side", "channel"), pos["name"], tag]
                steps.append(dict(pos=pos, preset=preset, preset_slot=p["slot"], preset_name=p["name"], tag=tag,
                                  ch=ch, out=need(ch, "out", "channel"), title=" ".join(x for x in parts if x)))
    titles = [st["title"] for st in steps]
    if len(set(titles)) != len(titles):
        raise PlanError(f"{w}: two sweeps would get the same name")
    return cfg, steps


# ---------- signal processing (pure functions; tools/sweep_selftest.py checks them) ----------
def make_stimulus(sw, sr):
    """Unit-amplitude log sweep (peak 1.0) and the whole played channel at level: pre-roll + sweep + silence."""
    n = int(sw["length_samples"])
    f1, f2 = float(sw["f_start_hz"]), float(sw["f_end_hz"])
    t = np.arange(n) / sr
    T = n / sr
    L = T / math.log(f2 / f1)
    s = np.sin(2 * math.pi * f1 * L * (np.exp(t / L) - 1))
    fi, fo = int(sw["fade_in_ms"] / 1000 * sr), int(sw["fade_out_ms"] / 1000 * sr)
    if fi:
        s[:fi] *= np.sin(np.linspace(0, math.pi / 2, fi)) ** 2
    if fo:
        s[-fo:] *= np.cos(np.linspace(0, math.pi / 2, fo)) ** 2
    pre, post = int(sw["pre_s"] * sr), int(sw["silence_s"] * sr)
    unit = np.concatenate([np.zeros(pre), s, np.zeros(post)])
    return unit, peak_amplitude(sw["level_dbfs"]) * unit, L


def deconvolve(rec, unit, sr, f1, f2):
    """Regularised spectral division rec / unit (both from the start of the buffer). Returns the circular IR
    (length nfft): positive times at the start, the harmonic distortion IRs (negative times) at the end.
    Scale: IR of the unit sweep, so the IR level goes with the sweep level, as REW's does."""
    nfft = 1 << int(math.ceil(math.log2(len(rec) + len(unit))))
    X = np.fft.rfft(unit, nfft)
    f = np.fft.rfftfreq(nfft, 1 / sr)
    # Regularise only above f2 (fading in over 1/3 octave), where the sweep really has no energy. Not at the low end:
    # the sweep's start spreads energy far below f1 (at f1/2 still at the 1 kHz level), and any low-end cut rings into
    # the analysis window (-0.3 dB at 20 Hz with a cut from f1, -0.2 dB from f1/4; found 2026-11-22 against steady
    # tones). sweep_selftest.py checks a flat and a 2 Hz high-pass path against the exact truth.
    lf = np.log2(np.maximum(f, 1e-3))
    out = np.clip((lf - math.log2(f2)) / (1 / 3), 0, 1)
    eps = np.max(np.abs(X)) ** 2 * (1e-10 + np.sin(out * math.pi / 2) ** 2)
    G = np.conj(X) / (np.abs(X) ** 2 + eps)
    return [np.fft.irfft(np.fft.rfft(r, nfft) * G, nfft) for r in rec]


def thd(h, peak, sr, L, kmax=5):
    """Broadband THD from the harmonic IRs of a log sweep (harmonic k sits L*ln(k) before the fundamental)."""
    n = len(h)
    pos = lambda k: peak - L * math.log(k) * sr  # sample index of harmonic k
    e = {}
    for k in range(1, kmax + 1):
        a = pos(k) - (pos(k) - pos(k + 1)) / 2 if k > 1 else peak - 0.002 * sr
        b = pos(k) + (pos(k - 1) - pos(k)) / 2 if k > 1 else pos(1) + (pos(1) - pos(2)) / 2
        idx = np.arange(int(a), int(b)) % n
        e[k] = float(np.sum(h[idx] ** 2))
    harm = {k: 10 * math.log10(e[k] / e[1] + 1e-30) for k in range(2, kmax + 1)}
    return 100 * math.sqrt(sum(e[k] for k in range(2, kmax + 1)) / e[1]), harm


def db(x):
    return 20 * math.log10(max(float(x), 1e-12))


def process(rec, unit, cfg, L):
    """rec: (frames, 2) = input (mic), loopback. Returns the IR to export and the per-sweep numbers."""
    sw, sr, T0 = cfg["sweep"], cfg["sr"], cfg["t0"]
    h_in, h_loop = deconvolve([rec[:, 0], rec[:, 1]], unit, sr, sw["f_start_hz"], sw["f_end_hz"])
    half = len(h_in) // 2
    t0 = int(np.argmax(np.abs(h_loop[:half])))
    peak = int(np.argmax(np.abs(h_in[:half])))
    ir = np.take(h_in, np.arange(t0 - T0, peak + cfg["after_peak"]), mode="wrap")
    pre = int(sw["pre_s"] * sr)
    nsw = int(sw["length_samples"])
    noise = rec[int(0.1 * sr):pre - int(0.02 * sr), 0]  # pre-roll, skipping the stream start
    sweep_part = rec[pre:pre + nsw, 0]
    thd_pct, harm = thd(h_in, peak, sr, L)
    m = dict(
        input_peak_dbfs=round(db(np.max(np.abs(rec[:, 0]))), 2),
        loopback_peak_dbfs=round(db(np.max(np.abs(rec[:, 1]))), 2),
        noise_dbfs=round(db(np.sqrt(np.mean(noise ** 2))), 1),
        snr_db=round(db(np.sqrt(np.mean(sweep_part ** 2))) - db(np.sqrt(np.mean(noise ** 2))), 1),
        ir_peak_dbfs=round(db(np.max(np.abs(ir))), 2),
        t0_buffer_sample=t0,
        delay_ms=round((peak - t0) / sr * 1000, 3),
        thd_pct=round(thd_pct, 3),
        harmonics_db={str(k): round(v, 1) for k, v in harm.items()},
    )
    return ir.astype(np.float32), m


def run_checks(m, st, cfg):
    """List of problems (empty = fine)."""
    c, bad = cfg["checks"], []
    if m["input_peak_dbfs"] > c["clip_dbfs"]:
        bad.append(f"input peak {m['input_peak_dbfs']:+.1f} dBFS > {c['clip_dbfs']} (clipping?)")
    if m["loopback_peak_dbfs"] > c["clip_dbfs"]:
        bad.append(f"loopback peak {m['loopback_peak_dbfs']:+.1f} dBFS > {c['clip_dbfs']} (clipping?)")
    if m["loopback_peak_dbfs"] < c["loopback_min_dbfs"]:
        bad.append(f"loopback only {m['loopback_peak_dbfs']:+.1f} dBFS < {c['loopback_min_dbfs']} (cable / UMC Out {cfg['loop_out']} -> In {cfg['loop_in']}?)")
    if m["snr_db"] < c["snr_min_db"]:
        bad.append(f"SNR {m['snr_db']:.0f} dB < {c['snr_min_db']}")
    base = (st["pos"].get("delay_ms") or {}) if cfg["kind"] == "room" else {}
    own = base.get(st["ch"]["side"])
    if own is not None:
        d_cm = (m["delay_ms"] - own) * C_CM_PER_MS
        m["baseline_delay_ms"], m["delay_diff_cm"] = own, round(d_cm, 1)
        if abs(d_cm) > c["delay_tol_cm"]:
            bad.append(f"delay {m['delay_ms']:.2f} ms is {d_cm:+.0f} cm off the baseline {own:.2f} ms (mic moved?)")
            for side, v in base.items():  # L and R baselines can be close (seat: 5 cm), so only after a miss
                if side != st["ch"]["side"] and abs(m["delay_ms"] - v) * C_CM_PER_MS <= c["delay_tol_cm"]:
                    bad.append(f"delay matches the {side} speaker's baseline ({v:.2f} ms): wrong output?")
    return bad


# ---------- DSP (tracks probe) ----------
def probe(cfg, *args, timeout=20):
    try:
        r = subprocess.run([cfg["probe"], *map(str, args)], capture_output=True, text=True, timeout=timeout)
    except FileNotFoundError:
        sys.exit(f"probe not found at {cfg['probe']} (build it: swiftc -O tools/probe/probe.swift -o tools/probe/probe in ~/WPlay/tracks)")
    return r.returncode, r.stdout + r.stderr


def check_probe(cfg):
    rc, out = probe(cfg, "--lock-status")
    if rc != 0:
        sys.exit("The DSP doesn't answer over USB:\n  " + out.strip().replace("\n", "\n  ") +
                 "\nIs the DSP on USB and powered? Close Chrome / the configurator (only one program may talk to the DSP).")


def recall(cfg, st):
    """Recall the step's preset; returns (slot read back, live name read back). Stops on any mismatch."""
    rc, out = probe(cfg, "--recall", st["preset_slot"])
    cur = re.search(r"^CURRENT (\S+)", out, re.M)
    live = re.search(r"^LIVE NAME (.*)$", out, re.M)
    cur, live = (cur.group(1) if cur else "?"), (live.group(1).strip() if live else "?")
    if rc != 0 or cur != str(st["preset_slot"]) or live != st["preset_name"].strip():
        sys.exit(f"Preset recall of {st['preset']} (slot {st['preset_slot']}, expected name {st['preset_name']!r}) failed:\n"
                 f"  read back: current preset {cur}, live name {live!r}\n  probe output:\n    " + out.strip().replace("\n", "\n    "))
    return int(cur), live


# ---------- audio ----------
def find_device(cfg):
    import sounddevice as sd
    hits = [(i, d) for i, d in enumerate(sd.query_devices()) if cfg["device"] in d["name"]]
    if len(hits) != 1:
        sys.exit(f"audio device {cfg['device']!r}: {len(hits)} matches; devices:\n{sd.query_devices()}")
    i, d = hits[0]
    need_in, need_out = max(cfg["input"], cfg["loop_in"]), max(cfg["loop_out"], cfg["_max_out"])
    if d["max_input_channels"] < need_in or d["max_output_channels"] < need_out:
        sys.exit(f"{d['name']} has {d['max_input_channels']} in / {d['max_output_channels']} out, need {need_in} / {need_out}")
    return i, d


def play_record(dev, cfg, out_ch, played):
    import sounddevice as sd
    data = np.stack([played, played], axis=1).astype(np.float32)
    rec = sd.playrec(data, samplerate=cfg["sr"], device=dev, blocking=True,
                     input_mapping=[cfg["input"], cfg["loop_in"]], output_mapping=[out_ch, cfg["loop_out"]])
    return rec.astype(np.float64)


# ---------- files ----------
def git_version():
    try:
        h = subprocess.run(["git", "-C", REPO, "rev-parse", "--short", "HEAD"], capture_output=True, text=True).stdout.strip()
        dirty = subprocess.run(["git", "-C", REPO, "status", "--porcelain", "--", "tools"], capture_output=True, text=True).stdout.strip()
        return h + ("+dirty-tools" if dirty else "")
    except OSError:
        return "?"


class SetLog:
    """measurements/<date>/<set>/<set>.json, rewritten after every change."""

    def __init__(self, path, header):
        self.path = path
        if os.path.exists(path):
            self.d = json.load(open(path))
        else:
            self.d = dict(header, sweeps=[])

    def entries(self):
        return {e["title"]: e for e in self.d["sweeps"]}

    def add(self, e):
        self.d["sweeps"] = [x for x in self.d["sweeps"] if x["title"] != e["title"]] + [e]
        self.save()

    def remove(self, title):
        self.d["sweeps"] = [x for x in self.d["sweeps"] if x["title"] != title]
        self.save()

    def save(self):
        tmp = self.path + ".tmp"
        with open(tmp, "w") as f:
            json.dump(self.d, f, indent=1)
        os.replace(tmp, self.path)


def write_ir(path, ir, sr):
    wavfile.write(path, sr, np.asarray(ir, np.float32))


def write_flac(path, x, sr):
    import soundfile as sf
    sf.write(path, np.clip(x, -1, 1), sr, subtype="PCM_24", format="FLAC")


# ---------- main ----------
def prompt(text):
    try:
        return input(text).strip().lower()
    except EOFError:
        return "q"


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("plan")
    ap.add_argument("set")
    ap.add_argument("--date", default=datetime.date.today().isoformat())
    ap.add_argument("--dry-run", action="store_true", help="print the run, don't touch audio, DSP or REW")
    a = ap.parse_args()
    plan_path = os.path.abspath(a.plan)
    plan = json.load(open(plan_path))
    cfg, steps = resolve_set(plan, a.set)
    cfg["_max_out"] = max(st["out"] for st in steps)
    folder = os.path.join(REPO, "measurements", a.date, a.set)
    rel = lambda p: os.path.relpath(p, REPO)
    wav = lambda st: os.path.join(folder, st["title"] + ".wav")
    raw = lambda st: os.path.join(folder, "raw", st["title"] + ".flac")
    mdat = os.path.join(folder, f"{a.set}.mdat")
    print(f"Set {a.set} ({cfg['kind']}): {len(steps)} sweeps -> {rel(folder)}/   plan {rel(plan_path)}")

    def todo_lines(st, mic, preset):
        t = []
        if st["pos"]["mic"] is not None and st["pos"]["name"] != mic:
            t.append(f"MOVE MIC -> {st['pos']['name']}: {st['pos']['mic']}")
        if st["preset"] != preset:
            t.append(f"(the script recalls {st['preset']} {st['preset_name']!r}, slot {st['preset_slot']})")
        return t

    if a.dry_run:
        mic = preset = None
        if cfg["before"]:
            print("  Before: " + cfg["before"])
        for i, st in enumerate(steps, 1):
            for t in todo_lines(st, mic, preset):
                print("  >>> " + t)
            mic, preset = st["pos"]["name"], st["preset"]
            print(f"  #{i:2d} out {st['out']} -> in {cfg['input']}: {st['title']}")
        return

    # --- devices ---
    check_probe(cfg)
    print("  DSP answers over USB.")
    dev, devinfo = find_device(cfg)
    print(f"  audio: {devinfo['name']} (reports {devinfo['default_samplerate']:.0f} Hz), in {cfg['input']} + loopback in {cfg['loop_in']}, loopback out {cfg['loop_out']}")
    unit, played, L = make_stimulus(cfg["sweep"], cfg["sr"])
    sw = cfg["sweep"]
    print(f"  sweep {sw['length_samples']} samples ({sw['length_samples'] / cfg['sr']:.1f} s) {sw['f_start_hz']}-{sw['f_end_hz']} Hz "
          f"at {sw['level_dbfs']} dBFS peak (as REW), + {sw['silence_s']} s silence")

    rew = None
    dbfs94 = cfg["dbfs_at_94"]
    cal_restore = None
    if cfg["rew_import"]:
        r = Rew(cfg["rew_api"])
        if r.running():
            rew = r
            calpath, rew94, _ = rew.input_cal()
            print(f"  REW {rew.version()}, cal file {calpath or 'NONE'}, dBFS at 94 dB SPL {rew94}")
            if rew94 is not None and abs(rew94 - dbfs94) > 0.01:
                print(f"  note: plan says dBFS at 94 dB SPL = {dbfs94}, REW has {rew94}; using REW's")
                dbfs94 = rew94
            if cfg["mic_cal"]:
                want = os.path.join(REPO, cfg["mic_cal"])
                if calpath != want:
                    rew.set_cal_file(want)
                    cal_restore = calpath
                    print(f"  REW cal file switched to {cfg['mic_cal']} for this set (switched back at the end)")
        else:
            print(f"  REW not running: measuring without the REW import. Later: mise run rew-load {rel(folder)}")
    spl_offset = 0.0 if cfg["kind"] == "electrical" else round(94 - dbfs94, 2)

    os.makedirs(os.path.join(folder, "raw"), exist_ok=True)
    log = SetLog(os.path.join(folder, f"{a.set}.json"), dict(
        set=a.set, kind=cfg["kind"], date=a.date, plan=rel(plan_path), device=devinfo["name"],
        samplerate=cfg["sr"], samplerate_reported=devinfo["default_samplerate"], mic_cal=cfg["mic_cal"],
        input_channel=cfg["input"], loopback_out=cfg["loop_out"], loopback_in=cfg["loop_in"],
        dbfs_at_94db_spl=dbfs94, spl_offset_db=spl_offset, sweep=sw, t0_sample=cfg["t0"],
        after_peak_samples=cfg["after_peak"], ir_scale="IR of the unit-amplitude sweep (level-dependent, as REW)",
        stimulus="raw/stimulus.flac", eq=cfg["eq"], script=f"tools/sweep.py v{SCRIPT_VERSION}"))
    stim_path = os.path.join(folder, "raw", "stimulus.flac")
    if not os.path.exists(stim_path):
        write_flac(stim_path, played, cfg["sr"])

    # --- what is done already ---
    entries = log.entries()
    done = [os.path.exists(wav(st)) and st["title"] in entries for st in steps]
    half = [st["title"] for st, d in zip(steps, done) if not d and (os.path.exists(wav(st)) or st["title"] in entries)]
    if half:
        sys.exit("These sweeps have a WAV or a <set>.json entry, not both; sort that out first:\n  " + "\n  ".join(half))
    if any(done):
        print(f"  Resuming: {sum(done)} of {len(steps)} sweeps already on disk.")

    def rew_titles():
        return rew.measurements() if rew else {}

    if rew:
        # REW measurements are this set's only if their REW id is in <set>.json (names can repeat across sets)
        own = {e.get("rew_uuid") for e in log.entries().values()}
        foreign = [t for t, v in rew_titles().items() if v["uuid"] not in own]
        if foreign:
            print(f"\nREW holds {len(foreign)} measurement(s) that aren't part of {a.set}:")
            for t in foreign[:10]:
                print("   ", t)
            if prompt("  Save them first if you need them. Type 'clear' to remove ALL measurements from REW: ") != "clear":
                sys.exit("Nothing changed.")
            rew.delete_all()
        have = {v["uuid"] for v in rew_titles().values()}
        missing = [st for st, d in zip(steps, done) if d and log.entries()[st["title"]].get("rew_uuid") not in have]
        for st in missing:  # resume after REW was closed: bring the finished sweeps back in
            sr_, x = wavfile.read(wav(st))
            v = rew.import_ir(st["title"], x, sr_, cfg["t0"], spl_offset, cfg["mic_cal"] is not None)
            log.add(dict(log.entries()[st["title"]], rew_uuid=v["uuid"]))
        if missing:
            rew.save_all(mdat)
            print(f"  imported {len(missing)} finished sweep(s) into REW")

    if cfg["before"]:
        print("\nBefore this set: " + cfg["before"])
        if prompt("  [Enter] when done, q = quit: ") == "q":
            return

    version = git_version()
    mic = preset = None  # unknown at start: always tell, always recall
    preset_read = None
    last = None  # index of the previous sweep (for r)
    try:
        while True:
            todo = [i for i, d in enumerate(done) if not d]
            if not todo:
                ans = prompt(f"\n  Set {a.set} complete. [Enter] finish   r = redo the last sweep: ") if last is not None else ""
                if ans != "r":
                    break
                i = None
            else:
                i = todo[0]
                st = steps[i]
                print()
                for t in todo_lines(st, mic, preset):
                    print("  >>> " + t)
                ans = prompt(f"  #{i + 1}/{len(steps)} {st['title']}   [Enter] sweep   r = redo previous   q = quit: ")
            if ans == "q":
                break
            if ans == "r":
                if last is None:
                    print("  nothing to redo")
                    continue
                pst = steps[last]
                for p in (wav(pst), raw(pst)):
                    if os.path.exists(p):
                        os.remove(p)
                uuid = log.entries().get(pst["title"], {}).get("rew_uuid")
                log.remove(pst["title"])
                if rew and uuid in {v["uuid"] for v in rew_titles().values()}:
                    rew.delete(uuid)
                    rew.save_all(mdat)
                done[last] = False
                mic = pst["pos"]["name"]  # the redo happens where the mic still is
                print(f"  removed {pst['title']!r}; it comes next (put the mic back at {pst['pos']['name']} if you moved it)")
                last = None
                continue

            if st["preset"] != preset:
                preset_read = recall(cfg, st)
                time.sleep(RECALL_SETTLE_S)  # a recall disturbs the output for a moment (low SNR on the next sweep otherwise)
                preset = st["preset"]
                print(f"  recalled {st['preset']}: current preset {preset_read[0]}, live name {preset_read[1]!r}")
            mic = st["pos"]["name"]
            entry = dict(title=st["title"], index=i + 1, time=datetime.datetime.now().isoformat(timespec="seconds"),
                         preset=st["preset"], preset_slot_read=preset_read[0], preset_name_read=preset_read[1],
                         position=st["pos"]["name"], side=st["ch"]["side"], output=st["out"], input=cfg["input"],
                         level_dbfs=sw["level_dbfs"], wav=os.path.basename(wav(st)), git=version, script_version=SCRIPT_VERSION)

            while True:
                print(f"  sweeping ({len(played) / cfg['sr']:.0f} s) ...", end="", flush=True)
                t_start = time.time()
                rec = play_record(dev, cfg, st["out"], played)
                ir, m = process(rec, unit, cfg, L)
                bad = run_checks(m, st, cfg)
                cm = f" ({m['delay_diff_cm']:+.0f} cm vs baseline)" if "delay_diff_cm" in m else ""
                print(f"\r  #{i + 1} {st['title']}: peak {m['input_peak_dbfs']:+.1f} dBFS, loopback {m['loopback_peak_dbfs']:+.1f}, "
                      f"SNR {m['snr_db']:.0f} dB, delay {m['delay_ms']:.2f} ms{cm}, THD {m['thd_pct']:.2f} %  [{time.time() - t_start:.0f} s]")
                if not bad:
                    break
                for b in bad:
                    print("    CHECK: " + b)
                ans = prompt("    [Enter] redo   k = keep anyway   q = quit: ")
                if ans == "k":
                    break
                if ans == "q":
                    raise KeyboardInterrupt
            entry.update(m, checks_failed=bad, raw=os.path.relpath(raw(st), folder))
            write_ir(wav(st), ir, cfg["sr"])
            write_flac(raw(st), rec, cfg["sr"])
            if rew:
                entry["rew_uuid"] = rew.import_ir(st["title"], ir, cfg["sr"], cfg["t0"], spl_offset, cfg["mic_cal"] is not None)["uuid"]
            log.add(entry)
            if rew:
                rew.save_all(mdat)
            done[i] = True
            last = i
    except KeyboardInterrupt:
        print("\n  stopped; run the same command again to resume")
    finally:
        if rew and cal_restore is not None:
            try:
                rew.set_cal_file(cal_restore)
                print(f"  REW cal file switched back to {cal_restore or 'NONE'}")
            except RewError as e:
                print(f"  could not switch REW's cal file back: {e}")

    n = sum(done)
    print(f"\n{a.set}: {n} of {len(steps)} sweeps done -> {rel(folder)}/" + (f", REW project {rel(mdat)}" if rew else ""))
    if n < len(steps):
        return
    after_set(cfg, folder, steps)
    if rew and prompt("  Remove all measurements from REW now (they're saved)? [y/N]: ") == "y":
        rew.delete_all()
        print("  REW cleared.")


def after_set(cfg, folder, steps):
    """Electrical: compare with the design (one run per preset/tag, so one WAV per side). Close-up: tuning per speaker."""
    out = os.path.join(REPO, "analysis", "output")
    runs = []  # (name, cmd)
    if cfg["kind"] == "electrical":
        lo, hi = cfg["check_band_hz"]
        groups = {}
        for st in steps:
            groups.setdefault((st["preset"], st["tag"]), []).append(f"{st['title']}.wav")
        for (preset, tag), files in groups.items():
            name = cfg["set"] + (f"_{tag}" if len(groups) > 1 and tag else f"_{preset}" if len(groups) > 1 else "")
            runs.append((name, [sys.executable, os.path.join(REPO, "analysis", "check_dsp_electrical.py"), folder, cfg["eq"],
                                os.path.join(out, f"{name}.png"), "--tol", str(cfg["tolerance_db"]), "--band", str(lo), str(hi),
                                "--files", *files]))
    elif cfg["kind"] == "closeup":
        runs.append((cfg["set"], [sys.executable, os.path.join(REPO, "analysis", "analyse_closeups.py"), folder,
                                  os.path.join(out, f"{cfg['set']}.png")]))
    for name, cmd in runs:
        print(f"\n  running {os.path.basename(cmd[1])} -> analysis/output/{name}.txt/.png")
        r = subprocess.run(cmd, capture_output=True, text=True, cwd=REPO)
        with open(os.path.join(out, f"{name}.txt"), "w") as f:
            f.write(r.stdout + r.stderr)
        print("    " + (r.stdout + r.stderr).strip().replace("\n", "\n    "))
        if cfg["kind"] == "electrical":
            print(f"  ELECTRICAL CHECK {name}: " + ("PASSED" if r.returncode == 0 else "FAILED: re-measure or look at the import before using this EQ in the room"))
    if runs:
        print("  Add the analysis line(s) to mise.toml's analyse task so it stays reproducible.")


if __name__ == "__main__":
    main()

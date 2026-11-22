"""Small client for the REW API (REW 5.40 beta, free licence), used by sweep.py and rew_load.py.

Only calls that work without REW Pro are used: list/rename/delete measurements, IR import and export,
input cal file, "Save all". Verified 2026-11-22 (docs/plans/python-sweep.md):
- POST /import/impulse-response-data takes the IR in full scale (1.0 = 0 dBFS, as in the WAV files),
  big-endian float32, base64; startTime = -t0/sampleRate keeps t=0. GET .../impulse-response returns it in percent.
- PUT /audio/input-cal switches the cal file (send dBFSAt94dBSPL and fullScaleSineVrms along unchanged).
"""
import base64, json, time, urllib.error, urllib.request
import numpy as np


class RewError(RuntimeError):
    pass


class Rew:
    def __init__(self, api):
        self.api = api.rstrip("/")

    def call(self, method, path, body=None, timeout=60):
        data = None if body is None else json.dumps(body).encode()
        req = urllib.request.Request(self.api + path, data=data, method=method, headers={"Content-Type": "application/json"})
        try:
            with urllib.request.urlopen(req, timeout=timeout) as r:
                txt = r.read().decode()
        except urllib.error.HTTPError as e:
            raise RewError(f"REW API {method} {path} -> HTTP {e.code}: {e.read().decode()[:300]}") from None
        except (urllib.error.URLError, ConnectionError, TimeoutError) as e:
            raise RewError(f"REW API not reachable at {self.api} ({getattr(e, 'reason', e)})") from None
        try:
            return json.loads(txt) if txt else None
        except json.JSONDecodeError:
            return txt

    def running(self):
        try:
            self.call("GET", "/version", timeout=3)
            return True
        except RewError:
            return False

    def version(self):
        return self.call("GET", "/version")["message"]

    def measurements(self):
        """{title: summary} of everything REW holds."""
        m = self.call("GET", "/measurements") or {}
        return {v["title"]: v for _, v in sorted(((int(k), v) for k, v in m.items()), key=lambda kv: kv[0])}

    def delete(self, uuid):
        self.call("DELETE", f"/measurements/{uuid}")

    def delete_all(self):
        self.call("DELETE", "/measurements")

    def import_ir(self, title, ir, sr, t0, spl_offset_db, apply_cal, wait_s=30):
        """Import an IR (full scale floats, t=0 at sample t0) and wait until REW lists it."""
        before = {v["uuid"] for v in self.measurements().values()}
        self.call("POST", "/import/impulse-response-data", {
            "identifier": title, "startTime": -t0 / sr, "sampleRate": sr, "splOffset": spl_offset_db,
            "applyCal": bool(apply_cal), "data": base64.b64encode(np.asarray(ir, ">f4").tobytes()).decode()})
        end = time.time() + wait_s
        while time.time() < end:
            new = [v for v in self.measurements().values() if v["uuid"] not in before]
            if new:
                return new[0]
            time.sleep(0.3)
        raise RewError(f"REW didn't list the imported {title!r} within {wait_s} s")

    def save_all(self, path):
        self.call("POST", "/measurements/command", {"command": "Save all", "parameters": [path]})

    def input_cal(self):
        """(cal file path or '', dBFSAt94dBSPL, the whole calDataAllInputs dict)."""
        c = self.call("GET", "/audio/input-cal").get("calDataAllInputs") or {}
        return c.get("calFilePath", ""), c.get("dBFSAt94dBSPL"), c

    def set_cal_file(self, path):
        """Switch the cal file, keep the SPL calibration; read it back."""
        _, _, c = self.input_cal()
        self.call("PUT", "/audio/input-cal", {"calDataAllInputs": {
            "calFilePath": path, "dBFSAt94dBSPL": c.get("dBFSAt94dBSPL"), "fullScaleSineVrms": c.get("fullScaleSineVrms")}})
        got = self.input_cal()[0]
        if got != path:
            raise RewError(f"REW cal file reads back as {got!r}, expected {path!r}")


# CLAUDE.md

Instructions for Claude working in this repo. Everything Claude needs to know lives in the repo (this file and the docs it points to). **Don't use Claude's project memory** for anything about this project: put it here or in the docs.

## Start and end of a session

- Start: read [SESSION-LOG.md](SESSION-LOG.md) (status, next steps, log). [README.md](README.md) maps the rest.
- End (or when asked to hand off): update Status/Next in the session log, add a dated Log entry, keep [docs/current-setup.md](docs/current-setup.md) and [docs/decisions.md](docs/decisions.md) current, commit.
- Where things go: one job per file, each fact in one place, link instead of copying.
  - New results → a new file per topic in [findings/](findings/) (don't append to old ones).
  - New decision → a row in [docs/decisions.md](docs/decisions.md).
  - Rewiring / reconfiguring → [docs/current-setup.md](docs/current-setup.md).
  - New measurements → `measurements/<date>/<set>/`, conventions in [measurements/README.md](measurements/README.md).
  - New or changed working rules for Claude → this file.

## Working with the user

- Communicates in short messages and screenshots of REW / the DSP GUI. Walk them through one step at a time, read the screenshots closely.
- **Read what they write literally; don't infer facts they didn't state.** For physical setup changes (speaker positions, wiring, knob states), restate only what they said, and ask a short question when a needed detail is missing.
  (2026-11-17: "distance unchanged" was misread as "the left speaker didn't move", and a wrong explanation built on it caused real frustration.)
- Watch the generator's band radio buttons in their screenshots (Full range / Sub Cal / Speaker Cal): they were left on Sub Cal several times.

## Analysis

- Python via **mise + uv** only (`mise.toml`, `pyproject.toml`, `uv sync` / `uv run`), not `python3 -m venv` / pip.
- `mise run analyse` re-runs every script into [analysis/output/](analysis/output/), [eq/](eq/) and the explainer. Scripts and outputs: [analysis/README.md](analysis/README.md).
- All analysis work goes in the repo: scripts in `analysis/`, plots and the full printed text output in `analysis/output/`, committed. The scratchpad is only for throwaway files; the user wants to inspect everything.

## DSP (t.racks DSP 4x4 Mini)

- Configured with the user's own configurator in `~/WPlay/tracks` (browser/WebHID, 1:1 reimplementation of the vendor editor from the reverse-engineered firmware/protocol). REW is only the measuring tool; the EQ is designed by this repo's scripts.
- Device limits and filter maths: `tracks/docs/protocol.md` (§5 parameter grids, §6.2 PEQ = RBJ with Q_rbj = Q_dev / A, §6.3 crossover, §6.4 compressor), `tracks/docs/measurements.md`; REW-text import in `tracks/web/src/rew.ts`.
- Design EQs on the device grid (PEQ gain ±12 dB) and check the filter files with tracks' `rewImport` before handing them over.
  (2026-11-18: files with −12.6 dB and REW-style rounding were rejected by the import.)

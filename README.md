# Idea Digger

A local web app that finds non-obvious, usable connections across everything you've
made — brand frameworks, creative projects, content topics, essays. Paste sources in,
hit **Dig**, get a novelty-scored insight from two sources that don't normally touch.

No database. No dependencies. Three files and a folder of plain text.

## Run it

```sh
export OPENROUTER_API_KEY=sk-or-...
python3 server.py
# → http://localhost:8420
```

Requires Python 3 (stdlib only).

## Model

All AI calls go through OpenRouter. The model is resolved per call:

1. `M` env var, if set (e.g. `M=anthropic/claude-opus-4.8 python3 server.py`)
2. otherwise `config.json` → `model`

`config.json` is re-read on every call, so you can swap models without restarting.

## How it works

- **Save** — paste any text. The AI assigns one tag (`content-topics`,
  `brand-frameworks`, `creative-projects`, `essays`, `other`) and a short label.
  A dropdown lets you correct the tag. Each source is a plain text file in
  `sources/` with the tag and label at the top.
- **Dig** — picks two sources from *different* tags, asks the AI for a non-obvious
  connection that produces something usable (essay angle, framework, product idea,
  story premise), then scores it 1–10 on novelty. Below 7, the AI explains why it's
  obvious and generates a deeper replacement — up to 3 rounds. You see only the final
  insight, its score, and the two sources.
- **Keep** — appends the insight to `keepers.md` with date, score, and source pair.
- **Chain** — digs the current insight against a third source from a tag not already
  in the pair.
- **Filter** — runs the insight through the three gates, pass/fail each:
  REVEAL (exposes the lie of unlimited capacity?), BUILD (creates proof, practice,
  or capacity?), DELIVER (respects the bandwidth?).

## Files

| File | What |
|---|---|
| `server.py` | The whole backend — stdlib HTTP server + OpenRouter calls |
| `index.html` | The whole frontend |
| `config.json` | Model name |
| `sources/*.txt` | Your sources (`tag:` / `label:` header, then text) |
| `keepers.md` | Kept insights (created on first Keep) |
| `roadmap.md` | Phase plan |
| `docs/WIKI.md` | Full reference: architecture, API, the dig loop, design decisions |
| `docs/HAPPY-PATH.md` | The intended workflow: feed → dig → keep → make |
| `docs/DEMOS.md` | Worked examples from real sessions + headless curl recipes |
| `docs/PHASE-3-4-PICKUP.md` | Handoff notes for the not-yet-built phases |

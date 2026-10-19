# Idea Digger

A local web app that finds non-obvious, usable connections across everything you've
made — brand frameworks, creative projects, content topics, essays. Paste sources in,
hit **Dig**, get a novelty-scored insight from two sources that don't normally touch.

No database. No dependencies. The app is two files — `server.py` and
`index.html` — plus a folder of plain text.

## Run it

```sh
export OPENROUTER_API_KEY=sk-or-...
python3 server.py
# → http://localhost:8420
```

Requires Python 3.9+ (stdlib only). `DIGGER_PORT=9000 python3 server.py` changes the port.

`OPENROUTER_API_KEY` can also live in a `.env` file next to `server.py` (`KEY=value` lines; a
variable already set in your shell wins). `config.json` is local and gitignored; if it is
missing, `config.example.json` is used. Copy it and set `vault` to a folder whose parent exists.

## Model

All AI calls go through OpenRouter. The model is resolved per call:

1. `M` env var, if set — forces one model for every call (e.g. `M=<slug> python3 server.py`)
2. otherwise `config.json` → `model` for digging, judging and filtering, and
   `cheap_model` (optional) for tagging and `import.py` triage

Optional `config.json` keys: `cheap_model`, `temperature`, `data_collection` (see Privacy).

`config.json` is re-read on every call, so you can swap models without restarting.

## Privacy

Every source you save or import is sent to OpenRouter and on to whichever provider
serves the model — including raw chat text during an import. Free-tier models are the
likeliest to log or train on prompts. To route only to providers that don't, add
`"data_collection": "deny"` to `config.json`; the catch is that a model with no such
provider then fails with a 404 instead of answering, so probe it with one dig first.
Off by default for that reason.

## How it works

- **Save** — paste any text. The AI assigns one tag (`content-topics`,
  `brand-frameworks`, `creative-projects`, `essays`, `ai-practice`, `commerce`,
  `other`) and a short label. A dropdown lets you correct the tag. Each source
  is a plain text file in `sources/` with the tag and label at the top.
- **Dig** — picks two sources from *different* tags, asks the AI for a non-obvious
  connection that produces something usable (essay angle, framework, product idea,
  story premise), then scores it 1–10 on novelty. Below 7, the AI explains why it's
  obvious and generates a deeper replacement — up to 3 rounds, and you get the
  best-scoring version it saw, not just the last. The judge is the same model that
  wrote the insight, so the score is a **self-rating**, and the card says so. You see
  only the final insight, its score, and the two sources. Each source's tag is a
  dropdown on the card: fix a misfiled one the moment you notice it.
- **Keep** — writes one Obsidian note per insight into your vault, with date, score,
  tags, `sources:` (the filenames in `sources/`, the real route back to the text) and
  `[[wikilinks]]` to the source labels. `vault` in `config.json` is the
  folder the notes are written into — set it to the subfolder you want, not the
  vault root. The wikilinks are to *labels*, which are not notes in the vault, so
  Obsidian shows them as unresolved; use `sources:` to trace a note.
- **Grade** — every dig is written to `digs.jsonl` (pair, rounds, scores, models,
  tokens, cost) whether or not you keep it, so a refresh never loses one: the last
  ungraded dig is restored on load. **Keep**, **Maybe** and **Skip** are the three
  grades; the counter at the top reads "n of 30 graded", the roadmap's gate before
  the next feature is built. A one-line "why" box beside the buttons is saved with the
  grade. Skip also digs the next pair.
- **Keys** — `D` dig · `K` keep · `M` maybe · `S` skip & dig next · `C` chain ·
  `F` filter · `Cmd/Ctrl+Enter` saves the source box. Keys are ignored while you type.
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
| `config.json` | Local, gitignored. `model`, `vault` (kept notes folder; its parent must exist), optional `cheap_model`, `temperature`, `data_collection`. `config.example.json` is the tracked default |
| `digs.jsonl` | The dig ledger: one line per dig and per grade. Gitignored; included in `make backup` |
| `sources/*.txt` | Your sources (`tag:` / `label:` header, then text) |
| `<vault>/*.md` | Kept insights, one note each (folder created on first Keep) |
| `roadmap.md` | Phase plan |

Bulk tools, run from the command line, not part of the web app:

| File | What |
|---|---|
| `import.py` | Bulk-import ChatGPT and Claude chat exports into `sources/` (`--chatgpt PATH --claude PATH` to point at the zips) |
| `retag_commerce.py` | One-off pass that moved existing sources into the `commerce` tag. Finished; kept for `--undo` |

Self-checks — no network, no API key needed. Run them all with `make test`, or each
with `python3 <file>`. CI runs `make test` on every push.

| File | What it covers |
|---|---|
| `test_ai_retry.py` | Which OpenRouter failures `ai()` retries (HTTP, error bodies, timeouts, truncated JSON) and which it gives up on |
| `test_dig.py` | The dig loop's best-of selection and time budget, tolerant reply parsing, slugs, atomic `set_tag`, `keep()` validation, model tiers, `.env`, the ledger |
| `test_http.py` | Every endpoint including grading and the ledger, status codes (400/404/409/502), request bounds, and the cross-origin guard |
| `test_import.py` | The export parsers and their documented traps |
| `test_keep.py` | Vault notes and tag-weighted sampling |

**Back up `sources/`.** It is gitignored and cost real API spend to build, and the
filter is stochastic, so it can't be regenerated identically. `make backup` writes a
dated tarball (sources, resume logs, `digs.jsonl`, `config.json` and the vault folder) to your home folder; `make restore-check` lists what the newest one holds — copy that somewhere
that isn't this machine.

Docs:

| File | What |
|---|---|
| `docs/WIKI.md` | Full reference: architecture, API, the dig loop, design decisions |
| `docs/HAPPY-PATH.md` | The intended workflow: feed → dig → keep → make |
| `docs/DEMOS.md` | Worked examples from real sessions + headless curl recipes |
| `docs/PHASE-3-4-PICKUP.md` | Handoff notes for the not-yet-built phases |
| `docs/101-ways-to-use-this-project-for-fun-and-profit.md` | 101 ways to use the tool as it stands, each tagged *now* or *needs <roadmap item>* |
| `docs/REVIEW-2026-10-18.md` | Full review: defects, doc drift, and the tiered enhancement plan |
| `docs/archive/` | The 100- and 101-demo scripts, the sales letter, the plain-language manual. Written before the vault move and never run against the real corpus; kept, not maintained |
| `docs/agents/issue-tracker.md` | Where issues live and how to work them |
| `docs/research/*.md` | What the import build measured and settled |

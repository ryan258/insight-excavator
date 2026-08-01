# Pickup notes — Phases 3 & 4

For whoever (or whichever session) builds the later roadmap phases cold.
Read `roadmap.md` first for the *why*; this file is the *how/where*.

## Current architecture (30 seconds)

- `server.py` — stdlib `ThreadingHTTPServer` on port 8420. All logic in one file:
  `ai(prompt)` is the only OpenRouter call site; `classify`, `dig`, `run_filter`,
  `keep`, `by_tag`, `pick_pair`, `pick_third` are the whole domain layer.
  Routes live in `Handler.do_POST` as a flat if/elif chain.
- `index.html` — one page, vanilla JS, `api(path, body)` helper, `current` object
  holds the active insight `{insight, score, tags, pair}`.
- State on disk only: `sources/*.txt` (tag/label header + text), plus one Obsidian
  note per kept insight in `<vault>/insights/` (`vault` in `config.json`).
- Model comes from `M` env var or `config.json`, re-read per call.

**Prerequisite check:** Phase 2 (`import.py`, bulk chat-export ingestion) should be
done before Phase 3 matters — repeat-pair avoidance is pointless with a dozen sources.
If Phase 2 hasn't happened, do it first; its spec is in `roadmap.md`.

## Phase 3 — Smarter digging

0. **Tag-weighted sampling** ✅ *(done 2026-07-31, issue #10)* — `pick_pair()` and
   `pick_third()` draw tags weighted by `sqrt(tag size)` instead of uniformly. Read
   the docstring on `two_tags()` before touching either; the naive fixes in both
   directions are worse. Check: `python3 test_keep.py`.

1. **No repeat pairs**
   - Append `"{a_file}|{b_file}"` (sorted) to `dug.log` at the end of `/api/insight`.
   - In `pick_pair()`, load the set and reject picked pairs that are in it; after
     N failed attempts (say 20), fall back to allowing repeats — never hard-fail
     a dig because the corpus is exhausted.
2. **Dig against this**
   - New endpoint `/api/pick_for {file}` → returns that source + a random source
     from any *other* tag. UI: smallest possible affordance — a text input or a
     "dig this" button next to the save confirmation. Don't build a source browser
     unless Ryan asks.
3. **Cost tiering**
   - `config.json` grows a second field: `{"model": ..., "cheap_model": ...}`.
   - `ai(prompt, cheap=False)`; `classify()` and Phase 2's import filter pass
     `cheap=True`. `dig`/`run_filter` stay on the strong model.

**Done when:** 50 digs, no repeated pair, tagging runs on the cheap model.

## Phase 4 — Output pipeline

1. **Weekly digest**
   - Standalone `digest.py` (CLI, not a server route). Reads the vault's insight notes, one AI
     call: "group these kept insights by theme; what does Ryan keep circling;
     what's ready to make." Writes `digest-YYYY-MM-DD.md`.
   - Each note is YAML frontmatter (`date`, `score`, `tags`) + body + a `Dug from`
     line; parse the frontmatter or just concatenate the bodies.
2. **Brand-voice handoff**
   - Manual first: the digest ends with a "ready to make" list Ryan copies into
     his brand-voice workflow (a Claude Code skill: `/brand-voice`).
   - Only automate if the manual habit sticks (see roadmap's "deliberately not
     doing"). If automating: one button per keeper that copies insight + pair
     context to clipboard, nothing fancier.

**Done when:** one kept insight has become one published piece.

## House rules (from how this project is built)

- Stdlib only. No pip installs, no framework, no database, no build step.
- One new file max per feature (`import.py`, `digest.py`); web features go in the
  existing two files.
- Every prompt asks for a rigid reply format and parses with a regex + safe fallback
  (see `dig`'s score parse: unparseable or out-of-range = `None`/unscored, never crash).
- Ship the lazy version, test it live via curl against real API before calling done.

# Idea Digger — Roadmap

A local tool that finds non-obvious, usable connections across everything Ryan makes:
brand frameworks, creative projects, content topics, essays. Plain files, one server,
no database. Each phase ships something usable on its own and has a "done when" test.

---

## Phase 0 — Core loop ✅ (shipped)

- Paste → AI tags (one of a closed set, five at the time; `ai-practice` and
  `commerce` were added later) + 5-word label → saved as plain text in `/sources`
- Tag correction dropdown
- Dig: pick two sources from different tags → non-obvious connection → novelty
  scoring loop (rewrite until 7+, max 3 rounds) → show insight + score + source pair
- OpenRouter, model swappable in `config.json` (no restart) or `M` env var

**Done when:** a dig produces a scored insight from real sources. ✅ Verified 2026-07-18.

---

## Phase 1 — The promised extras ✅ (shipped)

The three features specced but deferred until the core loop proved out.

1. **Keep pile** — a Keep button on the insight card. Writes one Obsidian note per
   kept insight into the vault (`vault` in `config.json`), with date, score, tags,
   and `[[wikilinks]]` to the two source labels. This comes first: without it, good
   insights evaporate on refresh. *(Originally appended to `keepers.md`; moved into
   the Obsidian vault on 2026-07-31 so kept insights land where the thinking lives.)*
2. **Chain mode** — a Chain button on a kept/current insight: dig it against a third
   source from a tag not already in the pair.
3. **Filter mode** — run any insight through the three gates, pass/fail each with one
   line of reasoning:
   - REVEAL: does it expose the lie of unlimited capacity?
   - BUILD: does it create proof, practice, or capacity?
   - DELIVER: does it respect the bandwidth?

**Done when:** dig → keep → chain → filter works as one flow and the kept notes read
like a usable idea log. ✅ Verified live 2026-07-19.

---

## Phase 2 — Feed the machine (the original mission) ✅ (shipped)

**Done 2026-07-31, closed with all tickets.** Build ticket:
[#8](https://github.com/ryan258/insight-excavator/issues/8). Map:
[#1](https://github.com/ryan258/insight-excavator/issues/1).

**What the full ingest produced** (the figures below this line in the planning notes
are the *predictions*; these are the results):

| | Predicted | Actual |
| --- | --- | --- |
| Idea-pass keep rate | 16% | **27%** (916 of 3,390) — idea density is clumpy, as warned |
| Idea-pass files | ~540 | 916 |
| Technique pass (#9) | — | 1,125 kept of 2,458 re-judged drops (46%) |
| Corpus | ~540 | **2,047** (2,041 imported + 6 hand-saved); `ai-practice` is 55% |
| `commerce` backfill (#11) | — | 2,046 judged, 32 moved; finished 2026-08-01 |

So the "is ~540 enough?" question below is answered: the corpus is 3.8× larger. The
open question is now quality, not size — 99.7% of it is model-paraphrased chat, and
only 6 sources are the user's own words.

The research below is kept as the record of *why*. It lives in three documents; between
them they hold the parser, the filter prompt, and the reason for the file shape:

- [`docs/research/export-format-anatomy.md`](docs/research/export-format-anatomy.md) — field-level anatomy of both exports (#2)
- [`docs/research/idea-filter-sample.md`](docs/research/idea-filter-sample.md) — the filter prompt, proven on 100 hand-read conversations (#5)
- [`docs/research/one-source-file.md`](docs/research/one-source-file.md) — what one file contains, settled with 12 real digs (#4)

### The corpus

Exports sit in `~/Downloads`, dated 2025-12-27. **The zip names are swapped** —
`rlwd--claude.zip` is the ChatGPT export, `rlwd--gpt.zip` is the Claude one.

| | |
| --- | --- |
| Conversations | 3,438 (1,338 ChatGPT + 2,100 Claude); 3,390 have extractable text |
| Transcript after drop rules | 38,524 messages / 59.2 M chars ≈ 14.8 M tokens |
| User turns only | 9.5 M chars — **a sixth of the corpus**, and all the filter reads |
| Expected survivors | ~540 files at a measured 16% keep rate |

**Gemini is out** — no Gemini export exists. The `drive-download-*.zip` files are
Google Docs, not Takeout conversations. Nothing to parse.

### What `import.py` does

One new file, a CLI script, not part of the web app. Stdlib only.

1. Stream both `conversations.json` files out of the zips — top-level JSON arrays,
   `raw_decode` against a growing buffer, never `json.load` the whole thing.
2. Extract messages: ChatGPT walks `parent` up from `current_node` then reverses;
   Claude uses array order **as given** and must not be sorted. Never read
   Claude's top-level `.text` — it is contaminated with chain-of-thought.
3. Keep **user turns only**.
4. Filter each conversation with prompt v2 on a cheap model. It returns a
   keep/drop verdict *and* a one-sentence `IDEA` in the same call.
5. Write each survivor's `IDEA` as one source file in `/sources` with the header
   `tag`, `label`, `source`, `date`, `conv`, `title`.

**One source file = one idea statement**, median ~200 chars — the same size and
shape as the hand-written sources the app was built around, so no loader change.
The statement is free: it falls out of the filter call, so there is **no second
AI pass over the corpus**.

**Name files by conversation id, never by title.** 145 conversations share 38
titles; `New chat` appears 54 times and 13 titles are empty.

**Make it resumable.** A 3,438-call pass will be interrupted. Write files as you
go and skip ids already present — that also gives re-import dedup for free.

### Settled deliberately, don't re-open

- **Ingest the Dec-2025 exports as they are** (#3). A fresh export later is an
  id-keyed upsert, not a blocker. Cost: a seven-month hole at the recent end.
- **Drop Claude's `attachments[].extracted_content`** for this first ingest —
  +22.7 M chars (+59%) of mostly pasted code and documents.
- **The filter drops user-authored specs brought for reaction.** Known, accepted,
  costs recall in the safe direction. A v3 prompt tried to fix it and regressed
  keeps 3 → 1 — **do not retry that approach** (#5 §4).
- **Review pass:** imports land as normal sources, so the existing tag dropdown is
  the correction tool. No new UI. ~540 files rather than 3,438 may bring this back
  inside what a dropdown can handle.

### Settled during the build

- **The classify pass stays a separate call**, on survivors only (~540, not 3,390).
  Folding `TAG`/`LABEL` into the filter call to avoid it was tried and reverted:
  it changed 6 verdicts in 60, against a measured self-consistency noise floor of
  1 in 60, and cost 4 of 13 keeps. **Do not edit the filter prompt** — it is the
  one measured at 39/40, and any change moves the verdicts.
- **The filter is stochastic.** v2 disagrees with *itself* about 1 time in 60, so
  read #5's "39/40" as carrying roughly ±1 of run-to-run noise.

### Still open

- **Whether ~540 files is enough corpus.** The 1:1 conversation→statement ratio is
  by construction, not because 1:1 is right; a conversation holding three distinct
  ideas yields one file. If it reads thin, let the filter emit several statements
  per conversation — still no second pass. Only the full run answers this.

**Done when:** the real exports are ingested, a re-run adds nothing and crashes on
nothing, and a dig can pair a 2024 ChatGPT idea with a 2026 creative project.

**Status:** shipped and run in full — see the results table above. To ingest a fresh
export later: `python3 import.py --chatgpt <zip> --claude <zip>` (already-seen
conversation ids are skipped, so only new chats cost anything).

`--limit N` takes a contiguous block in export order, not a random sample — idea
density is clumpy (consecutive blocks of 40 ran 10%, 18%, 30%), so a trial run's
keep rate says little about the corpus.

---

## Phase 3 — Smarter digging

Only matters once the corpus is big (post Phase 2). Phase 2's research turned up
two defects that land here — both will be visible on the first ingest, and
neither is a bug in `import.py`.

0. **Fix `pick_pair()`'s uniform tag sampling.** ✅ (shipped) `random.sample(tags, 2)`
   drew *tags* uniformly, then one source within the chosen tag — so a small tag
   drowned out big ones. Fixed via $\sqrt{\text{size}}$ weighted sampling
   (`two_tags` and `draw_tag` in `server.py`), dropping per-source imbalance
   from 13.8x to 3.7x (issue #10).
1. **No repeat pairs** — the picker skips pairs already in `digs.jsonl` until all are
   exhausted. The ledger exists (2026-10-18); the picker does not read it yet. *Low value
   at 2,047 sources (~2 M possible pairs).*
2. **Dig against this** — pick one specific source, let the tool find its partner.
3. **Cost tiering** ✅ (2026-10-18) — `cheap_model` in `config.json` for tagging and
   import triage; `model` for digging, judging and filtering. `claude-haiku-4.5` is
   proven adequate for the filter (#5).
4. **Revisit `dig()`'s retry budget.** It retries up to three times whenever the
   novelty score is under 7. All twelve digs measured in #4 scored 5–8 and the
   judge never went below 5, so most digs burn the full budget and still return a
   5 or 6 — three extra calls to move one point. Either the judge needs
   recalibrating or the threshold does.

**Done when:** 50 digs in a row produce no repeated pair, no source is drawn
wildly more often than another, and tagging costs pennies.

---

## Phase 4 — Output pipeline (pull, don't push)

Insights are only useful if they leave the tool.

1. **Weekly digest** — script that reads the vault's insight notes, groups by theme,
   outputs one markdown brief: "what you keep circling, what's ready to make."
2. **Brand-voice handoff** — a kept insight can be sent to the existing brand-voice
   workflow as a seed for X/LinkedIn drafts (manual copy at first; automate only if
   the manual step actually gets used).

**Done when:** one kept insight has become one published piece of content.

---

## Review fixes ✅ (shipped 2026-10-06)

A full review found 16 defects; 14 were fixed in one pass and 2 only partly (wikilinks:
provenance added, links unchanged; long requests: timeout cut from 180 s to 120 s, but
no progress or cancel). Covered by `make test`. Fixed: UI retag no longer strips imported provenance headers; `ai()`
retries timeouts, connection errors, truncated JSON and empty `choices`; `dig()`
returns its best-scored insight, not its last, and stops when there is no
replacement; `keep()` validates `score`/`tags`/`files`, writes `sources:`
provenance, and never leaves an empty note; statuses are 400/404/409/502 instead of
500 for everything; `by_tag()` is cached; sources are clipped at 4,000 chars in
prompts; non-ASCII slugs; the tag dropdown now appears on every dig card, so the
2,041 imports are correctable; the score is labelled "self-rated"; `--chatgpt` and
`--claude` flags; `DIGGER_PORT`; optional `data_collection`; `make test` / `make
backup`; CI; stale docs.

**Left on purpose:** wikilinks still point at labels, not vault notes (use
`sources:`); `import.py` was not renamed (the keyword problem is already handled in
the test, and the name is cited across the research docs); `config.json` is still
tracked with a machine-specific vault path (untracking it is a `git rm --cached`
decision); the 100- and 101-demo docs are bannered as pre-vault, not deleted.

## Tier A + corrections ✅ (shipped 2026-10-18)

From `docs/REVIEW-2026-10-18.md`. **Corrections:** one tolerant `server.field()` for every
model reply (bold, bullets, any case) and `import.py` raises on an unreadable VERDICT instead
of logging a DROP; atomic source writes; bounded `Content-Length` and clipped filter input;
a 240 s per-dig budget; `BadRequest` / `NoSuchSource` replace blanket `ValueError` /
`FileNotFoundError` mapping; `.env` loader; `config.json` untracked and local with `config.example.json`
tracked; the vault's parent must exist; a complete `make backup` and `make restore-check`;
optional `temperature`; demo docs moved to `docs/archive/`. **Features:** the dig ledger
(`digs.jsonl`), Keep / Maybe / Skip grading with a "n of 30" counter, last-dig restore after
refresh, keyboard shortcuts, `cheap_model`, dark mode, wrapping layout, focus outlines.

**Left unbuilt on purpose:** streaming progress and
cancel (a dig can still sit silent for minutes), the rest of Backlog below.

## Backlog — only after one MAKE cycle

**Gate: 30 graded digs, and one kept insight shipped as a published piece.** The
vault holds one note and the last source was added 2026-08-01; the tool has not yet
been through its own "done when". Do not build below until it has. Each item is a
burst-sized package, in this order:

1. **Evaluate** — *(instrumented 2026-10-18: grade in the UI; read `digs.jsonl`)* grade 30 digs keep/skip by hand, record them, then compare models
   and prompts and calibrate the self-rated judge against the grades. The "1 in 3
   worth keeping" figure came from a 3-source test corpus and was never measured here.
2. **Dig ledger** ✅ (2026-10-18) — append every dig to `digs.jsonl` (pair, rounds, scores, model,
   tokens, cost). One file serves as the no-repeat log, the cost record, and a way
   to recover an insight you didn't keep.
3. **Directed digging** — `dig --about "<question>"` using stdlib TF-IDF over the
   sources, plus "dig against this source" and per-source mute. A professional arrives
   with a question; random pairing is the demo.
4. **Show the work** — expandable source text on the pair card (the pick endpoint
   deliberately ships labels only; revisit that), the per-round score trail, a
   "dig again" button. (Dark mode shipped 2026-10-18.)
5. **Lenses** — move `TAGS`, the three `GATES` and the dig prompt's output kinds into
   `config.json`, keeping the tag set closed, so the tool is not hardcoded to one
   brand. (`cheap_model` shipped 2026-10-18.)
6. **Corpus quality** — near-duplicate detection (56 labels are shared by 142 files;
   5 exact-duplicate bodies), a `kind: idea|technique` header backfilled from the
   resume logs, and importers for the user's own writing (markdown folders, an
   Obsidian vault) so more than 6 sources are original.
7. **Output (Phase 4)** — `digest.py`, the brand-voice handoff, JSON/CSV export.
8. **Operability** — `doctor` command (key, model, vault path, corpus health). (`.env`
   loading and `config.example.json` shipped 2026-10-18.)

## Deliberately not doing

- No database, no accounts, no deploy — this is a single-user local tool
- No embeddings/vector search until random pairing demonstrably runs dry
- No automation of Phase 4 until the manual version proves the habit exists

## Working order

Phase 1 → Phase 2 → review fixes → **use it for a couple of weeks** → let real usage
decide what the backlog above should be.

**Next action:** run 30 digs against the real corpus, grade each (K / M / S; the counter
at the top of the page tracks it), keep the ones you would be annoyed to lose, and turn
one into a published piece. That is
the project's own "done when", and it has not happened yet.

One caveat: the model has changed twice since the measurements in the research docs.
`config.json` now points at `deepseek/deepseek-v4-flash-0731`; the 12 digs behind
Phase 2's file-shape decision were run on `inclusionai/ring-2.6-1t`, and the filter
was calibrated on `anthropic/claude-haiku-4.5`. The conclusions hold — the file shape
won on cost as much as on score, and the null guard is cheap insurance — but the
numbers behind them are model-specific.

# Idea Digger — Roadmap

A local tool that finds non-obvious, usable connections across everything Ryan makes:
brand frameworks, creative projects, content topics, essays. Plain files, one server,
no database. Each phase ships something usable on its own and has a "done when" test.

---

## Phase 0 — Core loop ✅ (shipped)

- Paste → AI tags (one of 5 tags) + 5-word label → saved as plain text in `/sources`
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

## Phase 2 — Feed the machine (the original mission)

**Planning complete as of 2026-07-31. Every decision is made; what remains is
writing one file.** Build ticket: [#8](https://github.com/ryan258/insight-excavator/issues/8).
Map: [#1](https://github.com/ryan258/insight-excavator/issues/1).

The research lives in three documents. Read them before writing a line of
`import.py` — between them they hold the parser, the filter prompt, and the
reason for the file shape:

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

**Status:** `import.py` is written, tested, and verified on 90 real conversations
(20 files, no double-processing, a dig across two imported sources scored 8).
**The full ingest has not been run** — that is the one remaining step, and it is
just:

```
M=anthropic/claude-haiku-4.5 OPENROUTER_API_KEY=... python3 import.py
```

`--limit N` takes a contiguous block in export order, not a random sample — idea
density is clumpy (consecutive blocks of 40 ran 10%, 18%, 30%), so a trial run's
keep rate says little about the corpus.

---

## Phase 3 — Smarter digging

Only matters once the corpus is big (post Phase 2). Phase 2's research turned up
two defects that land here — both will be visible on the first ingest, and
neither is a bug in `import.py`.

0. **Fix `pick_pair()`'s uniform tag sampling.** `random.sample(tags, 2)` draws
   *tags*, then one source within the chosen tag — so a tag holding 5 sources is
   drawn as often as one holding 2,000. Once ~540 imported files land in seven
   tags, the five existing hand-written sources will be dug hundreds of times more
   often than any imported one. This is now the first thing to fix, not the third.
1. **No repeat pairs** — log dug pairs to `dug.log`; picker skips already-dug combos
   until all are exhausted.
2. **Dig against this** — pick one specific source, let the tool find its partner.
3. **Cost tiering** — cheap model for tagging/import-filtering, strong model for
   digging and scoring. Two model fields in `config.json`.
   `claude-haiku-4.5` is proven adequate for the filter (#5).
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

## Deliberately not doing

- No database, no accounts, no deploy — this is a single-user local tool
- No embeddings/vector search until random pairing demonstrably runs dry
- No automation of Phase 4 until the manual version proves the habit exists

## Working order

Phase 1 → Phase 2 → use it for a couple of weeks → let real usage decide whether
Phase 3 or Phase 4 matters more.

**Next action:** [#8](https://github.com/ryan258/insight-excavator/issues/8) — write
`import.py` and run the first ingest. Phase 2 planning is done; nothing blocks it.

One caveat for whoever picks this up: `config.json` moved from
`inclusionai/ring-2.6-1t` to `google/gemma-4-26b-a4b-it` on 2026-07-31. The 12
digs behind Phase 2's file-shape decision, and the ~1-in-10 null-content rate
behind the `ai()` retry (#7), were both measured on the *old* model. The
conclusions hold — the file shape won on cost as much as on score, and the null
guard is cheap insurance — but the numbers behind them are model-specific.

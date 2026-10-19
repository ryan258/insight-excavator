# Idea Digger — Wiki

The complete reference. What every piece is, how it works, and why it's built the way
it is. For the daily workflow read `HAPPY-PATH.md`; for worked examples read `DEMOS.md`;
for the future plan read `../roadmap.md`.

---

## What this tool believes

Idea Digger is built on three convictions:

1. **Your best ideas already exist — in pieces.** The value isn't in generating new
   ideas from nothing; it's in colliding things you've already made that don't
   normally touch. A brand framework and a comedy strip know things about each other
   that neither knows alone.
2. **Novelty must be enforced, not hoped for.** Every LLM will happily hand you a
   surface-level connection and call it insight. The scoring loop exists because the
   first answer is usually the obvious one — the tool's job is to refuse it.
3. **The constraint is the design.** No database, no framework, no deploy. Plain
   files you can read, grep, and back up. If the tool died tomorrow, `sources/` and
   the vault's insight notes would still be worth keeping. That's the constraint-driven-design
   brand applied to its own tooling.

---

## Architecture

```
index.html  ──fetch──▶  server.py  ──HTTPS──▶  OpenRouter  ──▶  model
    ▲                       │
 one page,             stdlib only,
 vanilla JS            reads/writes ▼
              sources/*.txt   config.json   <vault>/*.md
```

Three files, one folder. Everything on disk is human-readable text.

| Piece | Role |
|---|---|
| `server.py` | The whole backend: `ThreadingHTTPServer` on `127.0.0.1:8420`, flat route table in `do_POST`, one OpenRouter call site (`ai()`) |
| `index.html` | The whole frontend: vanilla JS, no build step, DOM-node rendering (no `innerHTML` for dynamic values — model output is untrusted) |
| `config.json` | Local and gitignored (`config.example.json` is the tracked default). `model`, `vault` (the folder notes are written into, not the vault root; its parent must exist), and optional `cheap_model`, `temperature`, `data_collection` |
| `digs.jsonl` | The dig ledger, append-only: a row per dig, a row per grade |
| `sources/*.txt` | The corpus |
| `<vault>/*.md` | The output — one Obsidian note per insight that survived your judgment |

### Concurrency & safety notes

- The server is threaded so a slow dig doesn't block a save. Source filenames are
  `<ms-timestamp>-<uuid6>.txt` — sortable by creation time, collision-resistant.
- The UI enforces **one action at a time** (`busy()` disables all buttons during any
  request) so responses can never land in a card that has been replaced.
- Binds to `127.0.0.1` only — never exposed to the network.
- All model-generated text renders via `textContent`. A pasted source that tricks the
  model into emitting HTML gets displayed as text, not executed.

---

## The model layer

Every AI call goes through one function: `ai(prompt)` → OpenRouter
`/api/v1/chat/completions`, single user message, no system prompt, no streaming.

Model resolution, per call:

1. `M` environment variable, if set — it forces one model for every call
2. `config.json` → `"model"`; tagging and `import.py` triage use `"cheap_model"` when it is set — **re-read on every call**, so editing the file
   changes the model mid-session with no restart

Auth is `OPENROUTER_API_KEY` from the environment. The server refuses to start
without it.

**Failure handling.** `ai()` makes up to 3 tries with 1 s, 2 s backoff, 120 s per
call. It retries 5xx, 429, a 200 carrying an error body, `content: null`, an empty
`choices` list, a timeout or connection error, and a truncated JSON body. It does
not retry other 4xx (402 out-of-credits will never succeed on a retry).

**Privacy switch.** `"data_collection": "deny"` in `config.json` is forwarded as
OpenRouter's provider-routing preference. Absent by default: a model with no
non-logging provider would fail with a 404 instead of answering.

**Prompt size.** A source is clipped to 4,000 characters in the `classify` and dig
prompts (`CLIP` in `server.py`); the file on disk keeps the full text.

**Prompt contract convention:** every prompt demands a rigid reply format
(`TAG:`/`LABEL:`, `SCORE:`/`REPLACEMENT:`, `GATE: PASS|FAIL — reason`) and is parsed
with a regex plus a safe fallback. The fallbacks are deliberate policy decisions:

| Parse failure | Fallback | Why |
|---|---|---|
| Tag unrecognized | `other` | A wrong tag is correctable in the UI; a crash isn't |
| Label missing | `untitled` | Same |
| Score unparseable or out of 1–10 range | `None` (shown as "unscored") | Better to show an unscored insight honestly than fabricate or clamp a number the judge didn't give |
| No usable `REPLACEMENT` below 7 | Stop, return the best insight seen | Re-judging identical text just re-rolls the score |
| Filter line unparseable | verdict `?` | Show the uncertainty instead of guessing |

---

## Data formats

### Source file (`sources/<ms>-<uuid6>.txt`)

```
tag: brand-frameworks
label: Constraint-driven system design
---
<original pasted text, verbatim>
```

Header is `key: value` lines; `\n---\n` separates header from body. Files made by
`import.py` are named `chatgpt-<id>.txt` / `claude-<id>.txt` and carry four more
headers — `source`, `date`, `conv`, `title` — the only route back to the original
chat. Nothing in the app rewrites them except the `tag:` line. The seven legal
tags: `content-topics`, `brand-frameworks`, `creative-projects`, `essays`,
`ai-practice`, `commerce`, `other`. Tags are a closed set on purpose — the dig loop needs
*categories to cross*, and a folksonomy would fragment into one-member tags. The
failure mode is the opposite of the intuitive one: a one-member tag doesn't get
ignored, it gets picked constantly, because the draw is over tags rather than
sources. See the sampling note under `/api/pick` below.

### Keeper note (one file per insight, in the vault)

`<vault>/YYYY-MM-DD-<slug-of-first-line>.md`:

```
---
date: 2026-07-19
score: 8
tags: [insight, creative-projects, brand-frameworks]
sources: [1784433194964.txt, 1784433209430.txt]
---

<insight text>

Dug from [[CEO Botsly workplace comedy]] + [[Constraint-driven system design]]
```

`sources:` is the dependable provenance — filenames in `sources/`, which an imported
file's own `conv:` header then ties to the original chat. The wikilinks are to source
*labels*, which are not notes in the vault, so Obsidian shows them as unresolved (and
56 labels in the corpus are each shared by several files — 142 files in all). `score` is omitted when unscored.

The slug comes from the insight's own first line — no second AI call for a title.
Same slug twice in a day gets a `-2` suffix rather than an overwrite.

Chained insights get a `⛓` in the pair field:
`bandwidth planner × Botsly ⛓ Smart house hauntings`.

---

## API reference

All endpoints are `POST` with JSON bodies; errors return `{"error": "..."}`. `GET /`
serves the page.

| Status | Meaning |
|---|---|
| 400 | The request is wrong (`BadRequest`): bad or non-object JSON, a bad `Content-Length`, a missing or mistyped field, an unknown tag, an invalid `score`/`tags`/`files` on keep |
| 403 | Cross-origin request rejected |
| 404 | Unknown route, or `file` / `dig` names nothing (`NoSuchSource`). A bare `ValueError` or `FileNotFoundError` is a bug and gives 500 |
| 409 | Well-formed but the corpus can't serve it: fewer than 2 populated tags, or nothing left to chain against |
| 502 | OpenRouter failed after retries (credits, rate limit, timeout) — the message says which |
| 500 | A bug. The trace is in the server terminal; the UI gets a generic message |

| Endpoint | Body | Returns | Notes |
|---|---|---|---|
| `/api/save` | `{text}` | `{file, tag, label, tags, clipped}` | Classifies via AI, writes the source file; `clipped` is true when the model will see only the start |
| `/api/retag` | `{file, tag}` | `{ok}` | Rewrites only the `tag:` line, so imported provenance headers survive; tag must be in the closed set |
| `/api/pick` | `{}` | `{a, b, tags}` (a, b each `{file, tag, label}`) | Two sources from two different tags; 409 if fewer than 2 tags populated |
| `/api/insight` | `{a, b}` (filenames) | `{insight, score, dig}` | Runs the full dig loop (below) and appends a ledger row; `dig` is its id |
| `/api/chain` | `{insight, exclude, dig?}` | `{insight, score, dig, source, tags}` | Picks a source from a tag *not* in `exclude`, digs the insight text against it |
| `/api/filter` | `{insight}` | `{gates: [{gate, verdict, why}]}` | Three-gate check, one AI call |
| `/api/keep` | `{insight, score?, pair, tags?, files?, dig?, why?}` | `{ok, note}` | Writes one note into the vault; `note` is the filename. `score` is an int 1–10 or null; `tags` come from the closed set; `files` are source filenames; `dig` (a dig id) is written to the frontmatter and records a `keep` grade carrying `why` (one line, 200 chars) |
| `/api/grade` | `{dig, grade: "maybe"\|"skip", why?}` | `{ok, digs, graded, keep, maybe, skip, target}` | Appends a grade row. The latest grade per dig counts; `keep` is recorded by `/api/keep` |
| `GET /api/stats` | — | `{digs, graded, keep, maybe, skip, target}` | Read off the ledger; `target` is the 30-graded-digs gate |
| `GET /api/last` | — | `{dig, grade}` | The newest dig row and its grade (null if ungraded); the page restores it after a refresh |

Pick and insight are separate calls **by design**: the UI shows you the pair before
the insight exists. Watching the sources first primes your own pattern-matching —
half the value of a dig is the second you spend guessing the connection before the
model answers.

**How a pair is drawn.** `pick_pair()` picks two distinct tags weighted by
`sqrt(tag size)`, then one source uniformly inside each. Neither extreme works:
drawing tags uniformly makes a source's odds *inversely* proportional to how many
neighbours it has (an 11-source tag once outdrew a 1,125-source one by 102x), while
drawing sources uniformly hands 55% of every dig to `ai-practice`. `sqrt` splits the
difference — worst-case per-source imbalance falls from 13.8x to 3.7x, and a
brand-new tag holding one file draws ~1% of the time instead of 33%. `pick_third()`
(chaining) uses the same weighting.

---

## The dig loop (the heart)

```
pick two sources, different tags
        │
        ▼
CONNECT: "Find a non-obvious connection… must produce something
usable: an essay angle, a framework, a product idea, or a story
premise. Do not give a surface-level answer."
        │
        ▼
JUDGE:  "Score this insight 1–10 on novelty. If below 7, explain
        why it's obvious, then generate a deeper replacement."
        │
   score ≥ 7? ──yes──▶ show insight + score
        │no
        ▼
swap in the replacement, judge again   (max 3 judge rounds)
        │
        ▼
return the BEST-scoring insight seen (ties: the earlier one)
```

Mechanics worth knowing:

- **The judge sees only the insight**, not the sources. It scores novelty as a
  reader would — which is the point; your audience won't see the sources either.
- **The replacement is judged before it's trusted.** On the final round the loop
  breaks *before* accepting an unscored replacement, so the score shown always
  belongs to the insight shown.
- **A rewrite can score worse than what it replaced**, so the loop remembers the
  best `(score, insight)` and returns that, not the last. An earlier real score
  beats a later unscored rewrite.
- **The score is a self-rating.** The judge is the same model that wrote the
  insight, and in the 12 digs behind #4 it never scored below 5. Treat it as a
  filter for the obvious, not a measurement; the card labels it "self-rated".
- **Sub-7 results are shown honestly.** A dig that ends at 5/10 after three rounds
  tells you something real: that pair has no deep connection today. That's signal,
  not failure — dig a different pair.
- **Chain mode reuses the same loop**, feeding the previous insight in as "thing 1"
  (tag `insight`) against a source from a tag not already in the pair. Each chain
  widens the exclusion, so a twice-chained insight has touched four tag families.

### The three-gate filter

One AI call, three verdicts, from The Human-AI Integration's own framework:

| Gate | Question |
|---|---|
| REVEAL | Does it expose the lie of unlimited capacity? |
| BUILD | Does it create proof, practice, or capacity? |
| DELIVER | Does it respect the bandwidth? |

The filter is *advisory*, not blocking — an insight can fail all three gates and
still be worth keeping (a story premise usually will). The gates measure fit with
the brand thesis, not quality.

---

## The dig ledger

`digs.jsonl` has two kinds of line. A **dig row** (has `insight`) holds `dig` (12-hex id),
`ts`, `kind` (`pair`/`chain`), `parent`, `pair`, `tags`, `files`, `sources` (what the card
shows), `insight`, `score`, `rounds` (each judge round's score), `models`, `calls`,
`tokens_in`, `tokens_out`, `cost` (null when the provider reports none), `seconds`. A
**grade row** (has `grade`) holds `dig`, `grade` (`keep`/`maybe`/`skip`), `why`, `ts`. The
latest grade per dig wins. A torn last line from a kill mid-append is skipped on read.
If the ledger write itself fails, the error is printed in the terminal and the insight
is still returned. A dig stops starting new judge
rounds after `DIG_BUDGET` (240 s); a call already in flight still finishes.

## Operational notes

| Situation | What to know |
|---|---|
| Swap model | Edit `config.json`; next call uses it. `M=slug python3 server.py` overrides entirely |
| "Need saved sources in at least 2 different tags" | The picker requires ≥2 populated tags. Save more, or retag |
| Chain says no sources outside the pair's tags | You need a third populated tag to chain |
| Port already in use on start | A previous instance is alive: `lsof -nP -iTCP:8420` then `kill <pid>` |
| Costs | Tagging is one small call; a dig is 2–4 calls (connect + 1–3 judges); filter is 1. A cheap model in `config.json` makes testing near-free; use a strong model for real digs |
| Backup | `sources/` + the `vault` folder is the entire state. `make backup` tars `sources/` and the resume logs to `~`. `sources/` is gitignored and unrepeatable, so copy it off this machine |
| Port | `DIGGER_PORT=9000 python3 server.py` |
| Speed | `by_tag()` is cached against file names and mtimes, so a pick on 2,000 sources no longer re-parses them all |
| Fix a misfiled source | Use the tag dropdown on the dig card. It rewrites only the `tag:` line |

## Design decisions log

| Decision | Why |
|---|---|
| Plain files over SQLite | Corpus must be greppable, editable, and survive the tool |
| Closed tag set | Digging needs stable categories to cross; free tags fragment |
| Judge loop capped at 3 | Diminishing returns; a pair that can't clear 7 in 3 tries won't in 10 |
| Score fallback = unscored | A format-breaking or out-of-range score is shown honestly rather than faked or looped on forever |
| Random pairing (for now) | With a small corpus, coverage beats cleverness. Embeddings wait until random provably runs dry (`roadmap.md`, "deliberately not doing") |
| No auth on the server | Localhost-only, single user |

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
              sources/*.txt   config.json   <vault>/insights/*.md
```

Three files, one folder. Everything on disk is human-readable text.

| Piece | Role |
|---|---|
| `server.py` | The whole backend: `ThreadingHTTPServer` on `127.0.0.1:8420`, flat route table in `do_POST`, one OpenRouter call site (`ai()`) |
| `index.html` | The whole frontend: vanilla JS, no build step, DOM-node rendering (no `innerHTML` for dynamic values — model output is untrusted) |
| `config.json` | Two fields: the model slug and the Obsidian `vault` path |
| `sources/*.txt` | The corpus |
| `<vault>/insights/*.md` | The output — one Obsidian note per insight that survived your judgment |

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

1. `M` environment variable, if set
2. `config.json` → `"model"` — **re-read on every call**, so editing the file
   changes the model mid-session with no restart

Auth is `OPENROUTER_API_KEY` from the environment. The server refuses to start
without it.

**Prompt contract convention:** every prompt demands a rigid reply format
(`TAG:`/`LABEL:`, `SCORE:`/`REPLACEMENT:`, `GATE: PASS|FAIL — reason`) and is parsed
with a regex plus a safe fallback. The fallbacks are deliberate policy decisions:

| Parse failure | Fallback | Why |
|---|---|---|
| Tag unrecognized | `other` | A wrong tag is correctable in the UI; a crash isn't |
| Label missing | `untitled` | Same |
| Score unparseable or out of 1–10 range | `None` (shown as "unscored") | Better to show an unscored insight honestly than fabricate or clamp a number the judge didn't give |
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

Header is `key: value` lines; `\n---\n` separates header from body. The seven legal
tags: `content-topics`, `brand-frameworks`, `creative-projects`, `essays`,
`ai-practice`, `commerce`, `other`. Tags are a closed set on purpose — the dig loop needs
*categories to cross*, and a folksonomy would fragment into one-member tags. The
failure mode is the opposite of the intuitive one: a one-member tag doesn't get
ignored, it gets picked constantly, because the draw is over tags rather than
sources. See the sampling note under `/api/pick` below.

### Keeper note (one file per insight, in the vault)

`<vault>/insights/YYYY-MM-DD-<slug-of-first-line>.md`:

```
---
date: 2026-07-19
score: 8
tags: [insight, creative-projects, brand-frameworks]
---

<insight text>

Dug from [[CEO Botsly workplace comedy]] + [[Constraint-driven system design]]
```

The slug comes from the insight's own first line — no second AI call for a title.
Same slug twice in a day gets a `-2` suffix rather than an overwrite.

Chained insights get a `⛓` in the pair field:
`bandwidth planner × Botsly ⛓ Smart house hauntings`.

---

## API reference

All endpoints are `POST` with JSON bodies; errors return `{"error": "..."}` with
an appropriate status — 500 for handler exceptions, 403 for a rejected
cross-origin request, 404 for an unknown route. `GET /` serves the page.

| Endpoint | Body | Returns | Notes |
|---|---|---|---|
| `/api/save` | `{text}` | `{file, tag, label, tags}` | Classifies via AI, writes the source file |
| `/api/retag` | `{file, tag}` | `{ok}` | Rewrites the header; tag must be in the closed set |
| `/api/pick` | `{}` | `{a, b}` (each `{file, tag, label}`) | Two sources from two different tags; errors if fewer than 2 tags populated |
| `/api/insight` | `{a, b}` (filenames) | `{insight, score}` | Runs the full dig loop (below) |
| `/api/chain` | `{insight, exclude}` | `{insight, score, source}` | Picks a source from a tag *not* in `exclude`, digs the insight text against it |
| `/api/filter` | `{insight}` | `{gates: [{gate, verdict, why}]}` | Three-gate check, one AI call |
| `/api/keep` | `{insight, score, pair, tags}` | `{ok, note}` | Writes one note into the vault; `note` is the filename |

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
```

Mechanics worth knowing:

- **The judge sees only the insight**, not the sources. It scores novelty as a
  reader would — which is the point; your audience won't see the sources either.
- **The replacement is judged before it's trusted.** On the final round the loop
  breaks *before* accepting an unscored replacement, so the score shown always
  belongs to the insight shown.
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

## Operational notes

| Situation | What to know |
|---|---|
| Swap model | Edit `config.json`; next call uses it. `M=slug python3 server.py` overrides entirely |
| "Need saved sources in at least 2 different tags" | The picker requires ≥2 populated tags. Save more, or retag |
| Chain says no sources outside the pair's tags | You need a third populated tag to chain |
| Port already in use on start | A previous instance is alive: `lsof -nP -iTCP:8420` then `kill <pid>` |
| Costs | Tagging is one small call; a dig is 2–4 calls (connect + 1–3 judges); filter is 1. A cheap model in `config.json` makes testing near-free; use a strong model for real digs |
| Backup | `sources/` + the vault's `insights/` is the entire state. Copy them anywhere |

## Design decisions log

| Decision | Why |
|---|---|
| Plain files over SQLite | Corpus must be greppable, editable, and survive the tool |
| Closed tag set | Digging needs stable categories to cross; free tags fragment |
| Judge loop capped at 3 | Diminishing returns; a pair that can't clear 7 in 3 tries won't in 10 |
| Score fallback = unscored | A format-breaking or out-of-range score is shown honestly rather than faked or looped on forever |
| Random pairing (for now) | With a small corpus, coverage beats cleverness. Embeddings wait until random provably runs dry (`roadmap.md`, "deliberately not doing") |
| No auth on the server | Localhost-only, single user |

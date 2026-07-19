# Idea Digger — Happy Path

The intended way to use this tool, start to finish. Not every feature — the *rhythm*
that makes it pay off. Reference details live in `WIKI.md`.

---

## The shape of it

```
FEED (occasionally) ──▶ DIG (in sessions) ──▶ KEEP (ruthlessly) ──▶ MAKE (weekly)
```

The tool has one failure mode: becoming a toy you poke twice and forget. The happy
path is designed around forming a loop where every stage feeds the next and the last
stage produces something you actually publish or build.

---

## 0. Start it

```sh
export OPENROUTER_API_KEY=sk-or-...
python3 server.py        # → http://localhost:8420
```

Before a real session, check `config.json` points at a strong model
(e.g. `anthropic/claude-opus-4.8`). Cheap models make shallow, jargon-dense digs —
fine for testing plumbing, bad for actual insight.

## 1. FEED — build a corpus worth colliding

Paste anything with an idea in it: a framework you wrote, a project premise, a
half-formed content angle, an essay draft, a good paragraph from an old chat.

**What makes a good source:**

- **Self-contained.** The dig prompt sends the full text; the model knows nothing
  else. "My three gates: REVEAL…, BUILD…, DELIVER…" digs well. "The gates thing
  from Tuesday" digs terribly.
- **One idea per source.** Two sources with one idea each can be paired; one source
  with two ideas can't be split. When in doubt, save twice.
- **Spread across tags.** The picker crosses *different* tags, so the corpus is only
  as rich as its rarest tag. A corpus of 30 essays and 2 projects mostly digs the
  same 2 projects. Check the spread occasionally: `grep -h '^tag:' sources/*.txt | sort | uniq -c`
- **Correct the tag when the AI misfiles.** It happens (project descriptions read as
  essays). The dropdown fix takes one second and directly improves future picks —
  tags are the collision categories.

A corpus of 15–20 well-spread sources is where digging starts getting interesting.
(Phase 2 of the roadmap bulk-imports your chat-history exports for exactly this
reason.)

## 2. DIG — in sessions, not single pulls

Digging works best as a deliberate session: 5–10 digs in a sitting, not one dig in
passing. Reasons:

- Any single dig is a lottery ticket. The hit rate is maybe 1-in-3 worth keeping —
  fine odds over a session, discouraging odds for a single pull.
- **Read the pair before the insight arrives.** The UI shows the two sources first
  on purpose. Spend that moment guessing the connection yourself — when the model's
  answer beats your guess, that's a real find; when your guess beats the model's,
  write yours down (paste it back in as a source!).
- Respect the score, loosely. A 7 means "cleared the novelty bar," not "good for
  you." An 8 that doesn't fit your work loses to a 7 that does. The score filters
  the obvious; *you* filter the useful.
- A low score after three judge rounds means that pair has no deep connection
  today. Move on — that's the system working, not failing.

## 3. KEEP — ruthlessly, immediately

When a dig lands, hit **Keep** before doing anything else. Insights not kept are
gone on the next dig — that's deliberate (one results card at a time keeps the tool
honest), so the Keep button is the only memory.

Keep bar: *"Would I be annoyed to lose this?"* Not "is this clever." `keepers.md`
should be a file you'd defend in a fire, not a scroll of everything that scored 7.

**Chain** when an insight feels 80% there — it re-digs the insight against a third
tag family, which either deepens it or productively breaks it. **Filter** when you
suspect an insight belongs to the brand — three gates, advisory only. A story
premise failing all three gates is still a story premise.

## 4. MAKE — the only stage that counts

Once a week, open `keepers.md` and pick **one** entry to turn into something real: an
essay draft, a post via the brand-voice workflow, a project note, a comic premise.

This stage is manual on purpose (roadmap Phase 4 automates the digest only after the
manual habit proves out). The tool's actual success metric is not digs run or
insights kept — it's *kept insights that shipped as something*. One published piece
a week from this file means the whole machine is working.

---

## A session in 10 minutes

```
minute 0   start server, confirm strong model in config.json
minute 1   paste 1–2 new sources since last time (feed before you dig)
minute 2   dig × 6, reading each pair before its insight arrives
minute 8   2 keeps, 1 chain that broke something open, 3 passes
minute 9   filter the keep that smells like brand material
minute 10  close the laptop; keepers.md is two entries richer
```

## Anti-patterns

| Anti-pattern | Why it hurts |
|---|---|
| Digging with 4 sources | Same pairs repeat; you'll conclude the tool is dull when the corpus is |
| Keeping everything ≥7 | `keepers.md` becomes noise and the weekly MAKE stage dies |
| Cheap model for real sessions | You'll read jargon soup and blame the idea |
| Feeding summaries instead of the real text | The model digs what you give it; thin sources make thin insights |
| Skipping the MAKE stage | The tool becomes a slot machine — entertaining, output-free |

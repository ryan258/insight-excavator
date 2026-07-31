# What is one source file?

Resolves [#4](https://github.com/ryan258/insight-excavator/issues/4). Part of [#1](https://github.com/ryan258/insight-excavator/issues/1).

One real idea-dense conversation ("Delta Blues Inspired by Poe", 9 messages,
18.6k chars) built into all three candidate shapes, each dug four times against
the same existing source (`sources/1784433194964.txt`, *Constraint-driven system
design*) using the real `server.dig()` and the app's configured model. Twelve
digs total, run 2026-07-31.

---

## 1. The answer

**One source file = one idea statement, harvested from the filter's `IDEA`
field.** Corpus is ~540 files, one per kept conversation (#5's 16% keep rate).

The decisive fact is not in the dig scores — it is that **this shape costs no
second AI pass.** The #5 filter already emits a one-sentence idea statement as a
byproduct of every keep/drop call. This ticket was opened believing
idea-extraction "is the only option that costs a second AI pass over the whole
corpus." That is now false, and it removes the only real argument against the
shape that also dug best.

## 2. The measurements

Scores are `dig()`'s own novelty judge. **A-markers** counts how many concrete
delta-blues/Poe terms (`nevermore`, `12-bar`, `melismatic`, `call-and-response`,
`turnaround`, …) appear in the resulting insight — a dig that scores well while
naming nothing from one of its two sources has drowned that source.

| shape | chars/dig | scores | mean score | mean A-markers | A-markers range |
| --- | ---: | --- | ---: | ---: | --- |
| whole-conversation | 18,659 | 5, 7, 5, 6 | 5.75 | 3.2 | **0 – 10** |
| topic-segment | 8,301 | 5, 7, 5, 7 | 6.00 | 9.2 | 4 – 15 |
| idea-statement | 245 | 5, 5, 8, 8 | **6.50** | 5.5 | 1 – 10 |

**Whole-conversation is the only shape that produced digs referencing one of its
two sources zero times — 2 of 4 runs.** Those two insights are fluent, plausible,
and built entirely out of the *other* source; the transcript contributed nothing.
This is the "mush" the ticket hypothesized, and it is real but intermittent
rather than universal — one whole-conversation run scored 7 with 10 markers. It
is also 75× the prompt size of an idea statement, for the worst mean score.

**Idea-statement scored highest and was the only shape to reach 8** (twice). Its
grounding is bimodal — runs landed at 1, 2, 9, 10 markers — so it sometimes flies
off into abstraction. Topic-segment is the most *reliably* grounded (never below
4) but never scored above 7.

Read together: a crisp statement gives the model room to make a connection;
a full transcript gives it so much material that it summarizes one side instead
of connecting two.

## 3. Why the score alone could not decide this

Every one of the twelve digs scored between 5 and 8. The judge never went below
5, and the three shapes' means sit inside one point of each other. **Novelty
score is too blunt to separate source shapes** — the marker analysis did the
actual work here.

That is worth carrying into Phase 3: `dig()` retries up to three times whenever
the score is under 7, so on this evidence a majority of digs will burn the full
retry budget and still return a 5 or 6. The scores above are already post-retry.

## 4. Fit with what already exists

The filter's idea statements are **median 199 chars** (range 126–298). The three
hand-written sources the app was designed around are 238, 304, and 331 chars.
Same size, same shape — no loader change, no header change, and the existing
`/sources` files stay coherent alongside imported ones. (The other two existing
files, at 3,878 and 19,998 chars, are pasted material and are the outliers.)

The `THIN` guard added in #5 fired on **0 of 13** keeps, so the statement is
reliably available when a conversation is kept.

## 5. Limits of this evidence

Stated plainly, because the ticket called this the decision the rest of the
import hangs off:

- **One conversation, one pairing partner, four runs per shape.** Directional,
  not conclusive. A different conversation — especially a sprawling multi-topic
  one — could favour segmentation.
- The conversation chosen is coherent and single-topic, which is the *friendliest*
  case for whole-conversation and it still lost. A multi-topic transcript would
  likely be worse, not better, so the ranking is probably safe in that direction.
- **One idea statement per conversation may under-harvest.** The filter emits a
  single `IDEA` per conversation; a genuinely dense conversation holding three
  distinct ideas yields one file. Multiplier is 1:1 by construction, not because
  1:1 is right. If ~540 files proves too thin a corpus, allowing the filter to
  emit several statements is the cheap next move — still no second pass.
- Topic-segment was built by hand here. Nothing was learned about how to segment
  mechanically, because the shape lost on other grounds before that mattered.

## 6. Provenance

Because the source file is now a distilled statement rather than the transcript,
the header's `conv` id (settled in #6) is doing real work: it is the only route
back from a one-sentence file to the conversation it came from. Keep it.

## 7. Reproducing

Throwaway prototype scripts live outside the repo:

- `dig4.py` — builds the three shapes, digs each via `server.dig()`, `RUNTAG=<x> python3 dig4.py <runs>`.
- `analyze4.py` — marker coverage per shape across all result files.

`dig4.py` monkeypatches `server.ai` with a retry because the configured model
intermittently returns a 200 with `content: null`, which crashes `ai()` — filed
as [#7](https://github.com/ryan258/insight-excavator/issues/7).

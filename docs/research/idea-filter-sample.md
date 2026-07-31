# The idea filter, proven on a sample

Resolves [#5](https://github.com/ryan258/insight-excavator/issues/5). Part of [#1](https://github.com/ryan258/insight-excavator/issues/1).

Three prompt versions run against real conversations from the corpus on
2026-07-31, every verdict read by hand. Parsing follows
[export-format-anatomy.md](export-format-anatomy.md); extraction reproduced that
document's numbers exactly (3,390 non-empty conversations = 3,438 − 45 empty
Claude − 3 empty ChatGPT; 59.2 M characters).

Filter model: `anthropic/claude-haiku-4.5`. Cheap-model filtering works.

---

## 1. The answer

**v2 of the prompt is the keeper.** It scored 39/40 correct on the calibration
sample against hand-read ground truth, with one known systematic miss (§4).

Keep rate: **16 of 100 conversations** across two samples (3/40 calibration,
13/60 validation). Extrapolated to the corpus: **~540 source files** from 3,390
conversations.

The two samples differed a lot (7.5% vs 21.7%) — idea density is clumpy, not
uniform, so do not trust a single small sample's rate. The 100-conversation
combined figure is the one to plan against.

## 2. The yes/no line

What earns a file: **the user's own words containing a belief, a framework, a
distinction they drew, a position they argued, a premise they invented, or the
shape of something they want to build.**

Length is explicitly not the test. The single best KEEP in the calibration
sample was 94 characters:

> zombie influencers, social media updates that are automated to post without
> human intervention

What does not earn a file: debugging, code review, how-do-I questions, tool and
config help, editing someone else's copy, factual lookups, requests for a list
or a deliverable, pasted transcripts and articles, model tests, small talk.

**Judge the user's turns only.** This is the single most important design
decision in the filter, and it is cheap: user text is 9.5 M of the 59.2 M
characters (16%), so the filter reads a sixth of the corpus. Median user text
per conversation is 452 characters, p90 is 5,924.

## 3. What went wrong in v1, and why

v1 fed the same user-turns-only view but without the guardrails below. It made
3 verdict errors in 40. All three are instructive.

**Hallucinated ideas from thin input (2 of 3 errors).** With a median of 452
characters to work from, the model reconstructed an idea from the *title* and
credited it to the user.

- *Hygge Essence: Cozy Dream* — KEEP, "the user is working through what hygge
  fundamentally is." The user's actual three turns: "why does the essence of
  hygge look like?", "make a style guide for hygge if it were a brand", "make a
  color palette that represents the essence of hygge." Image-prompt commissioning,
  zero thinking. **False KEEP.**
- *Automate Etsy Shop* — KEEP, "the user developed a coherent thesis about
  targeting a specific persona (Midwest, Scandinavian heritage, outdoor-loving)."
  The user's actual turn: "make some example personas for me of people who live
  in the midwest, have some scandinavian heritage…". The *assistant* invented
  the personas. The user asked. **False KEEP.**

This is the failure mode to defend against, and it is not obvious from reading
verdicts alone — both looked plausible until the raw text was pulled up. Two
guardrails fixed it: telling the model the assistant's replies are not evidence
and not available, and requiring the `IDEA` field to use only words and claims
present in the user's turns, replying `THIN` if it cannot.

**Effort mistaken for insight.** v1 also drops long technical sessions correctly
but needs to be told explicitly; "a conversation can be long, technical, and
useful and still be DROP" earns its place in the prompt.

## 4. The one known miss

v2 still drops **user-authored specs brought for reaction**.

*Chrome Extension for Organizing Reusable Text Content* — the user pasted 3,372
characters of a product spec they wrote themselves and asked "Hey what do you
think about this project idea?" That is the user's own product thinking at
length, and the map lists "product idea" as a target output. v2 drops it as
"product spec and build plan… not a belief, framework, or insight."

v2's prompt contains an explicit instruction to keep exactly this case. The
model ignores it. The prior that *spec = deliverable = drop* is stronger than
the counter-instruction.

**v3 tried to fix this and made things worse** — it restructured the prompt to
ask an explicit authorship question first, which then cannibalised the second
question: KEEPs collapsed from 3 to 1 on the same sample, losing the zombie
influencers premise and both good creative entries, and it *still* rated the
Chrome Extension spec as un-authored. v3 is recorded in the prototype script and
should not be revived without a different approach.

Accept the miss for the first ingest. It costs recall on one narrow category, in
the safe direction. If it matters later, the lead worth pulling is a mechanical
pre-rule rather than more prompt wrestling — but note that user-turn length
alone will not do it: the two largest user turns in the calibration sample
(32,332 and 10,875 characters) were both *pasted transcripts of other people's
video*, which must stay DROP. The distinction is authored-by-user vs
pasted-by-user, and it is genuinely hard mechanically.

## 5. Incidental findings for `import.py`

**Conversation titles are not unique.** 145 conversations share 38 titles —
`New chat` appears **54 times**, and 13 conversations have an empty title.
Filenames must key off the conversation id; a title-derived filename will
silently overwrite. (`sources/` already uses id-style names, so this is a
constraint to preserve, not a change.)

**Prompt-template boilerplate pollutes the user's text.** *Farmhouse Essence
Dissected* opens with a 552-character pasted "three experts / tree of thoughts"
prompt template before the user's real 187-character contribution — which is a
genuine causal hypothesis (AI job loss driving a cottagecore surge) and a correct
KEEP. The filter handled it, but the boilerplate is noise in any later
idea-extraction pass.

## 6. Reproducing

Prototype scripts are throwaway and live outside the repo (Phase 2 still gets
exactly one new file, `import.py`):

- `extract.py` — streams both zips to `corpus.jsonl` per the anatomy doc.
- `filter.py` — `V=1|2|3 python3 filter.py <n> <seed>`, writes `verdicts-v<V>.jsonl`.

Calibration sample is `n=40 seed=20260731`; validation is `n=60 seed=99`.

The v2 prompt text is reproduced in `filter.py` as `PROMPT_V2` and is what
`import.py` should carry.

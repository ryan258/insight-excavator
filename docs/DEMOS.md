# Idea Digger — Demos

Worked examples, all from real sessions against the live tool (July 2026, test corpus
of three sources). Model for these runs was a deliberately cheap one
(`openai/gpt-5.4-nano`) to prove the *plumbing*; expect noticeably better prose from a
strong model. Curl recipes at the bottom for driving it headless.

The test corpus:

| Tag | Label | Gist |
|---|---|---|
| `brand-frameworks` | Constraint-driven system design | Limited bandwidth as core design input; the REVEAL/BUILD/DELIVER gates |
| `creative-projects` | CEO Botsly workplace comedy | "The CEO is a Bot" — AI CEO takes corporate cliché literally |
| `content-topics` | Honest bandwidth planner | Planners assume 8 productive hours; real people have 2 |

---

## Demo 1 — A dig that cleared the bar (8/10, first judge round)

**Pair:** `creative-projects` / CEO Botsly × `brand-frameworks` / Constraint-driven design

> Botsly-like systems fail when they treat stakeholder statements as a *type system*
> (rules/labels) rather than as *resource-conservation* (time, review cycles,
> legal/compliance gates, compute, and attention); the deeper issue is mis-specified
> translation — an agent should map each promise into (1) measurable constraints,
> (2) a costed dependency graph, (3) verification criteria, and (4) an escalation
> plan when any resource budget is exceeded — so replacing "literal corporate logic"
> means implementing a feasibility compiler that outputs a budgeted plan plus
> uncertainty and triggers, not just a compliance decision.

**Why this one worked:** it found the *structural* rhyme between the two sources —
Botsly's comedy comes from treating promises as rules; the brand framework says
promises are resource claims. The output is usable in two directions: an essay angle
("your commitments are a type error") and a product idea (the feasibility compiler).
This is the reference example of what "non-obvious but usable" means.

## Demo 2 — The judge refusing to rubber-stamp (5/10 after 3 rounds)

**Pair:** `content-topics` / bandwidth planner × `creative-projects` / CEO Botsly

Three judge rounds, two rewrites accepted, never cleared 7. Final output was a serviceable
comedy-mechanic pitch ("Constraint Licenses" — employees file permission slips for
hydration and silence), shown honestly with its 5/10.

**What to learn:** the same pair produced a 6/10 in a different session. Some pairs
just don't have a deep seam, and the loop *reports* that instead of inflating it.
When a pair scores low twice, stop digging it — feed the corpus instead.

## Demo 3 — A full chain: dig → keep → chain → filter

**Step 1, dig (8/10):** bandwidth planner × constraint-driven design →

> Treat the bandwidth snapshot as a *runtime contract* rather than a planner: the
> system measures current "capacity state," converts tasks into testable deliverable
> units, and enforces feasibility gates with automatic scope degradation…

**Step 2, keep:** appended to `keepers.md` as
`## 2026-07-19 — 8/10 — <pair>`.

**Step 3, chain** (excluding the pair's two tags, so the third source had to come
from `creative-projects` — Botsly): scored 7/10 →

> Make the bandwidth snapshot double as a *verifiable cryptographic ledger*: each
> meeting's promised throughput stored as a signed "commit," re-computed against
> post-meeting telemetry; the CEO Bot can only take actions if the ledger verifies…

Note what chaining did: the runtime-contract idea got pushed through the comedy
project and came back as a *story mechanic* (a CEO bot that literally cannot act on
unverified promises) that is simultaneously a satire premise and a straight-faced
product sketch. That dual-use is chain mode's signature move.

**Step 4, filter** on the chained insight:

| Gate | Verdict | Reason (model's) |
|---|---|---|
| REVEAL | ✓ PASS | Exposes the "unlimited capacity" lie by making promises non-executable and measurable |
| BUILD | ✓ PASS | Concrete mechanisms: signed commits, telemetry hashes, verification gate, escalation path |
| DELIVER | ✓ PASS | Limits actions to verified ledger states; failures route to human review |

A three-gate pass means this one belongs to the brand thesis — it graduated from
"interesting" to "on-mission."

---

## Drive it headless (curl)

The UI is optional — everything is seven JSON endpoints. Useful for scripting demos
or batch sessions.

```sh
# save a source (AI tags + labels it)
curl -s -X POST localhost:8420/api/save \
  -d '{"text": "Your idea text here."}'
# → {"file": "...txt", "tag": "essays", "label": "Five word label", "tags": [...]}

# fix a wrong tag
curl -s -X POST localhost:8420/api/retag \
  -d '{"file": "<file>", "tag": "brand-frameworks"}'

# pick a cross-tag pair, then dig it
PAIR=$(curl -s -X POST localhost:8420/api/pick -d '{}')
A=$(echo "$PAIR" | python3 -c "import json,sys; print(json.load(sys.stdin)['a']['file'])")
B=$(echo "$PAIR" | python3 -c "import json,sys; print(json.load(sys.stdin)['b']['file'])")
curl -s -X POST localhost:8420/api/insight -d "{\"a\": \"$A\", \"b\": \"$B\"}"
# → {"insight": "...", "score": 8}

# chain an insight against a third tag family
curl -s -X POST localhost:8420/api/chain \
  -d '{"insight": "<insight text>", "exclude": ["content-topics", "brand-frameworks"]}'

# three-gate filter
curl -s -X POST localhost:8420/api/filter -d '{"insight": "<insight text>"}'

# keep
curl -s -X POST localhost:8420/api/keep \
  -d '{"insight": "<text>", "score": 8, "pair": "label A × label B"}'
```

A ten-dig batch session in one line of shell:

```sh
for i in $(seq 10); do
  P=$(curl -s -X POST localhost:8420/api/pick -d '{}')
  A=$(echo "$P" | python3 -c "import json,sys;print(json.load(sys.stdin)['a']['file'])")
  B=$(echo "$P" | python3 -c "import json,sys;print(json.load(sys.stdin)['b']['file'])")
  curl -s -X POST localhost:8420/api/insight -d "{\"a\":\"$A\",\"b\":\"$B\"}" \
    | python3 -c "import json,sys;d=json.load(sys.stdin);print(f\"[{d['score']}/10] {d['insight'][:120]}…\")"
done
```

(Reminder: each dig is 2–4 model calls. Ten digs on a strong model is real money —
set `config.json` accordingly before batch runs.)

---

## Demoing to someone else

The 90-second version:

1. Open the page. Paste one of *their* ideas in. Watch it get tagged. ("Everything
   is a plain text file — look in `sources/`.")
2. Hit Dig. Make them read the pair and guess the connection out loud before the
   insight arrives.
3. When the insight lands, point at the score: "It rewrote itself until a judge
   called it non-obvious — below 7 gets rejected and rewritten, three strikes and
   it shows you the honest failure."
4. Hit Chain. "Now it takes what it found and forces it through a third category."
5. Open `keepers.md`. "This file is the product. The app is just the shovel."

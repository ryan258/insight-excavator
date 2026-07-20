# 100 Brilliant Demos

One hundred ways to demo Idea Digger, each in full detail: the setup, the exact
steps, and the moment that lands. Unlike `DEMOS.md` (transcripts from real
sessions), these are *scripts* — run any of them against the live tool and the
output is real. Where sample output would help, the *shape* of it is described,
never faked.

Conventions used throughout:

- Server running: `export OPENROUTER_API_KEY=sk-or-... && python3 server.py` → `http://localhost:8420`
- The five tags: `content-topics`, `brand-frameworks`, `creative-projects`, `essays`, `other`
- The judge threshold is 7/10, max 3 rounds; sub-7 after 3 rounds is shown honestly
- The seven endpoints: `/api/save`, `/api/retag`, `/api/pick`, `/api/insight`, `/api/chain`, `/api/filter`, `/api/keep`
- Each dig costs 2–4 model calls — mind `config.json` before batch demos

---

## I. First-90-seconds demos (cold opens)

### 1. The classic 90-second demo
The canonical open, expanded from `DEMOS.md`. For anyone, any context.

**Setup:** server running, corpus of 3+ sources across at least 3 tags, `keepers.md` has at least one entry.
**Run:**
1. Open the page. Paste one of *their* ideas. Watch it get tagged and labeled. Say: "Everything is a plain text file — look in `sources/`."
2. Hit **Dig**. Make them read the two source labels and guess the connection out loud before the insight arrives.
3. When the insight lands, point at the score: "It rewrote itself until a judge called it non-obvious — below 7 gets rejected and rewritten, three strikes and it shows you the honest failure."
4. Hit **Chain**. "Now it forces what it found through a third category."
5. Open `keepers.md`. "This file is the product. The app is just the shovel."
**The moment:** step 2 — the gap between what they guessed and what the dig found is the whole pitch.

### 2. The "your idea goes first" open
Start with the audience's material, not yours. Nothing sells a mining tool like watching it dig *their* dirt.

**Setup:** server running, your existing corpus loaded. Ask them beforehand for one idea they've been chewing on — a sentence or a paragraph.
**Run:**
1. Paste their idea into Save before saying anything about the tool. Read the tag and label out loud.
2. Dig repeatedly until the pick includes their source (or force it headless: get their filename from the save response, pick any of yours from a different tag, and `curl -s -X POST localhost:8420/api/insight -d '{"a":"<theirs>","b":"<yours>"}'`).
3. Hand them the insight and ask: "Is that obvious to you?"
**The moment:** their idea colliding with your framework produces something neither of you had — instant proof it's not a toy.

### 3. The empty-folder open
Build the corpus live from zero. Proves there's no magic pre-load.

**Setup:** move `sources/` aside (`mv sources sources.bak && mkdir sources`), restart nothing — the server reads the folder per request.
**Run:**
1. Show the empty `sources/` folder in Finder or `ls`.
2. Paste three ideas from your head, one at a time, watching each get tagged.
3. Dig. First insight from a corpus that didn't exist two minutes ago.
4. Restore afterwards: `rm -r sources && mv sources.bak sources`.
**The moment:** "That's the entire onboarding. There is no import wizard because there's nothing to import into — it's a folder."

### 4. The guessing game
Turn the dig into a parlor game. Best with 2+ people watching.

**Setup:** server running, corpus of 5+ sources so pairs vary.
**Run:**
1. Hit Dig but cover the insight area (scroll, hand, or narrate from the pair labels only).
2. Everyone states their guess for the connection. Thirty seconds max each.
3. Reveal. Compare guesses to the dig. Score the humans against the judge's score.
4. Repeat three rounds.
**The moment:** round two or three, when someone's guess is *good* and the dig is still stranger — that's the "non-obvious" bar made visceral.

### 5. The one-file reveal
Mid-demo, drop out of the UI into a text editor. For anyone allergic to black boxes.

**Setup:** server running, any corpus.
**Run:**
1. Do a normal save. As soon as the tag appears, switch to a terminal: `cat sources/$(ls -t sources | head -1)`.
2. Show the anatomy: `tag:` line, `label:` line, then the raw text.
3. Edit the file by hand in the editor — change a word. Dig again. "The server read your edit. There's no cache, no database, no sync."
**The moment:** hand-editing the "database" with a text editor and having the app not care.

### 6. The keepers-first open
Show the output before the machine. For people who ask "but what do you *get*?"

**Setup:** `keepers.md` with 5+ real entries spanning a few dates.
**Run:**
1. Open `keepers.md` first. Read one 8/10 entry aloud, including the date/score/pair header.
2. "Every one of these came from two things I'd already written that had never touched."
3. Only then open the app and run one dig live so they see where entries come from.
**The moment:** the file reads like a notebook of someone smarter — then you show the shovel that dug it.

### 7. The silent demo
No narration until the end. Works on people fatigued by AI pitches.

**Setup:** server running, corpus loaded, a visible clock.
**Run:**
1. Say only: "Ninety seconds, then I'll explain."
2. Save one idea → Dig → Keep → Chain → Filter, in silence, letting them read everything on screen.
3. At ninety seconds, ask: "What do you think it just did?" Correct only what they got wrong.
**The moment:** the UI is simple enough that they narrate it back mostly right — which *is* the design pitch.

### 8. The remote screen-share demo
Same as the classic, adapted for a call.

**Setup:** screen share with the browser and a terminal split-screened; corpus loaded.
**Run:**
1. Ask them to dictate an idea over the call. Type it into Save verbatim, typos and all.
2. Dig. Read the pair labels aloud (screen-share text can be small).
3. Paste the final insight into the call's chat so they have it after the call.
4. End on `keepers.md` in the terminal: `tail -20 keepers.md`.
**The moment:** they leave the call with an artifact in their chat history — the demo mailed itself.

### 9. The skeptic open
Lead with a failure. Counterintuitive, devastatingly effective on cynics.

**Setup:** know a pair in your corpus that scores low (see demo 29 for finding one). Have `DEMOS.md` Demo 2 handy as backup.
**Run:**
1. First words: "Let me show you it failing." Dig the weak pair headless so you control it: `curl -s -X POST localhost:8420/api/insight -d '{"a":"<weak1>","b":"<weak2>"}'`.
2. Show the sub-7 score. "Three judge rounds, two rewrites, never cleared the bar. It tells you that instead of inflating it."
3. *Then* run a normal dig and let a 7+ land.
**The moment:** the low score buys credibility that makes the high score believable.

### 10. The 30-second elevator version
One dig, one sentence, done. For hallways and "so what are you building?"

**Setup:** server already running on your laptop, corpus loaded, page open.
**Run:**
1. One sentence: "It reads everything I've written and finds connections I didn't make."
2. Hit Dig. Say nothing while it works.
3. Read the insight aloud. Stop. Let them ask the next question.
**The moment:** ending on their question instead of your pitch.

---

## II. Save & tagging demos

### 11. The five-paste accuracy run
Show auto-tagging holding up across genres.

**Setup:** prepare five short texts of deliberately different kinds: a productivity observation, a framework fragment, a story premise, an essay opening, and a grocery-list-adjacent stray thought.
**Run:**
1. Paste each in turn. Read out the tag it got: expect `content-topics`, `brand-frameworks`, `creative-projects`, `essays`, `other` respectively — or narrate where it disagreed with you and why its choice is defensible.
2. Show the dropdown correction on any miss.
**The moment:** the stray thought landing in `other` — the system knows what it doesn't know.

### 12. The retag correction
Deliberately feed it something ambiguous and fix the call.

**Setup:** a text that straddles two tags — e.g., a *story about* a productivity method (creative? content?).
**Run:**
1. Save it. Note the tag it picked.
2. Argue the other reading out loud, then correct it: dropdown in the UI, or `curl -s -X POST localhost:8420/api/retag -d '{"file":"<file>","tag":"creative-projects"}'`.
3. `head -1 sources/<file>` — the header changed on disk.
**The moment:** "The AI proposes, the file is the truth, and you own the file."

### 13. The filing-cabinet view
Show that tags are the entire organizational scheme.

**Setup:** corpus of 8+ sources.
**Run:**
1. In a terminal: `head -2 sources/*.txt` — every file announces its own drawer.
2. Group them live: `grep -l "tag: brand-frameworks" sources/*.txt`.
3. "Dig picks from two *different* drawers. That's the whole cross-pollination mechanism."
**The moment:** the realization that the taxonomy is five words and a grep away — no tag manager, no UI for it, none needed.

### 14. The fixed-taxonomy defense
Demo *why* there are exactly five tags and no custom ones.

**Setup:** none beyond a running server.
**Run:**
1. Save something weird — a dream fragment, a recipe idea. Watch it land in `other`.
2. Make the argument live: "More tags = fewer cross-tag collisions = worse digs. The tags exist to force distance, not to organize."
3. Show `pick_pair()` in `server.py` — pairs must come from different tags.
**The moment:** reframing a "limitation" as the load-bearing design decision.

### 15. The label compression test
The five-word label as a summarization benchmark.

**Setup:** one long source — a full essay or several paragraphs.
**Run:**
1. Save it. Before the label appears, ask the audience to title it in five words themselves.
2. Compare theirs to the model's label.
3. Show where labels matter: they're what you read when a dig pair appears.
**The moment:** a good label on a 500-word paste — compression as a proof of comprehension.

### 16. The ten-minute corpus build
A feeding session as the demo itself.

**Setup:** ten ideas queued in a notes file, server running.
**Run:**
1. Set a ten-minute timer. Paste, glance at the tag, correct if needed, next.
2. Keep a tally of tag corrections needed (expect few).
3. End with `ls sources | wc -l` and one dig on the fresh corpus.
**The moment:** the tally — "ten sources, one correction, ten minutes" is the feeding cost, stated as data.

### 17. The clipboard pipeline
Save without touching the browser.

**Setup:** macOS terminal, server running, something copied.
**Run:**
```sh
pbpaste | python3 -c 'import json,sys; print(json.dumps({"text": sys.stdin.read()}))' \
  | curl -s -X POST localhost:8420/api/save -d @-
```
1. Copy any text anywhere — a chat reply, a note, a tweet draft.
2. Run the line. Read the returned tag and label from the JSON.
**The moment:** "Cmd-C is the entire integration surface. Everything you copy can be corpus."

### 18. The messy-input stress test
Raw, unedited chat-log text as a source.

**Setup:** a genuinely messy excerpt — your half of a chat thread, typos, fragments, no punctuation.
**Run:**
1. Paste it raw. No cleanup. Save.
2. Note that tagging and labeling worked on garbage-formatted input.
3. Dig it against a clean source and show the insight doesn't care about the mess.
**The moment:** "This is why phase 2 is bulk chat-export import — the miner already handles ore, not just polished ingots."

### 19. The near-duplicate probe
Two phrasings of one idea, saved separately.

**Setup:** write the same idea twice — once as a hot take, once as a careful paragraph.
**Run:**
1. Save both. Compare the two labels — usually they differ in emphasis, exposing what each phrasing foregrounds.
2. Discuss: duplicates are harmless here; worst case a dig pairs your idea with itself across tags and scores low.
**The moment:** the two labels side by side — the labeler as a mirror for your own framing.

### 20. The source-file anatomy lesson
Thirty seconds on the entire data format.

**Setup:** any saved source.
**Run:**
1. `cat sources/<any>.txt` — point at line 1 (`tag:`), line 2 (`label:`), and everything after (the text).
2. Create one *by hand*: write a new .txt with that header in an editor, drop it in `sources/`, dig — it's eligible immediately.
**The moment:** the schema fits on an index card and you just wrote a valid record in a text editor.

---

## III. Dig demos

### 21. The maiden dig
First dig on a brand-new corpus — pairs with demo 3 or 16.

**Setup:** a corpus you just built live, 3+ sources across 2+ tags.
**Run:**
1. Hit Dig. Narrate the wait honestly: "Two to four model calls are happening — connect, judge, maybe rewrite, judge again."
2. Read the pair, then the insight, then the score, in that order.
**The moment:** an insight that could not have existed five minutes ago, because its raw material didn't.

### 22. The cross-tag guarantee
Prove pick never pairs same-tag sources.

**Setup:** server running, mixed corpus.
**Run:**
```sh
for i in $(seq 8); do
  curl -s -X POST localhost:8420/api/pick -d '{}' \
    | python3 -c "import json,sys;d=json.load(sys.stdin);print(d['a']['tag'],'×',d['b']['tag'])"
done
```
1. Run it. Every line shows two *different* tags, eight times in a row.
2. Point at `pick_pair()` in `server.py` as the three-line reason why.
**The moment:** eight-for-eight on the guarantee, verified live rather than claimed.

### 23. The re-dig variance demo
Same pair, multiple digs — show it's a search, not a lookup.

**Setup:** pick one pair headless and hold the filenames.
**Run:**
1. `curl -s -X POST localhost:8420/api/insight -d '{"a":"<A>","b":"<B>"}'` — run it three times.
2. Compare the three insights and scores. Expect different angles into the same seam, sometimes a spread of 2–3 score points.
**The moment:** "The pair is the mine; each dig is a different tunnel. A rich pair pays out more than once."

### 24. The hand-picked pair
Skip random pick; choose the collision yourself.

**Setup:** know two specific sources you suspect rhyme.
**Run:**
1. Find their filenames: `grep -l "label: <part of label>" sources/*.txt`.
2. Dig them directly via `/api/insight` with both filenames.
3. Compare against your own hypothesis of the connection.
**The moment:** when the dig finds the rhyme you suspected *plus* a mechanism you didn't — the tool as collaborator, not oracle.

### 25. The two-one-liners dig
Minimum viable sources.

**Setup:** save two single-sentence sources in different tags.
**Run:**
1. Dig them directly. Note the insight is often *longer* than both inputs combined.
2. Discuss: the dig isn't summarizing, it's constructing — inputs are prompts, not content to compress.
**The moment:** more comes out than went in, visibly.

### 26. The asymmetric dig
A 1,000-word essay against a one-liner.

**Setup:** one long-form source, one aphorism-length source, different tags.
**Run:**
1. Dig them directly. Watch which source dominates the framing.
2. Run it twice; note whether the short source ever "wins" the frame.
**The moment:** a one-liner bending a whole essay around itself — evidence that density, not length, drives the dig.

### 27. The ten-dig batch
The shell loop from `DEMOS.md`, run as theater.

**Setup:** cheap model set in `config.json` (each dig is 2–4 calls; ten digs on a strong model is real money).
**Run:**
```sh
for i in $(seq 10); do
  P=$(curl -s -X POST localhost:8420/api/pick -d '{}')
  A=$(echo "$P" | python3 -c "import json,sys;print(json.load(sys.stdin)['a']['file'])")
  B=$(echo "$P" | python3 -c "import json,sys;print(json.load(sys.stdin)['b']['file'])")
  curl -s -X POST localhost:8420/api/insight -d "{\"a\":\"$A\",\"b\":\"$B\"}" \
    | python3 -c "import json,sys;d=json.load(sys.stdin);print(f\"[{d['score']}/10] {d['insight'][:120]}…\")"
done
```
1. Run it. Watch the scores scroll — a live histogram of your corpus's seam quality.
**The moment:** the one line that scores 8+ in a field of 6s: batch mode as prospecting, keep mode as extraction.

### 28. The guest-corpus dig
Run the machine on someone else's material entirely.

**Setup:** ask a friend for 4–5 short ideas ahead of time. `mv sources sources.mine && mkdir sources`, then save their five.
**Run:**
1. Dig their corpus in front of them, twice.
2. Ask them to score the insights *before* revealing the judge's scores; compare.
3. Restore your corpus afterwards.
**The moment:** the judge agreeing with their gut — calibration demonstrated on material you couldn't have rigged.

### 29. The dead-seam demo
Find and honor a pair with nothing in it.

**Setup:** run demo 27's batch; note any pair scoring below 7 twice.
**Run:**
1. Dig the weak pair a third time on purpose. Show the honest sub-7.
2. State the operating rule from `DEMOS.md`: "When a pair scores low twice, stop digging it — feed the corpus instead."
**The moment:** a tool that tells you when to stop using it.

### 30. The model A/B dig
Same pair, two models, side by side.

**Setup:** know one rich pair's filenames. Two terminals.
**Run:**
1. Terminal 1: dig with the cheap default from `config.json`.
2. Terminal 2: restart as `M=anthropic/claude-opus-4.8 python3 server.py` (or just edit `config.json` — it's re-read per call, no restart needed) and dig the same pair.
3. Read both insights aloud; compare scores and, more tellingly, prose quality.
**The moment:** the plumbing is identical, only the water changed — model choice as a config value, not an architecture.

---

## IV. Judge & novelty-loop demos

### 31. The rounds narration
Make the invisible rewrite loop visible by narrating it.

**Setup:** any dig, but slow the moment down.
**Run:**
1. Hit Dig. While it runs, talk through `dig()`: "Right now: connect prompt on the pair. Then a judge scores 1–10 on novelty. Below 7, the judge explains why it's obvious and a deeper replacement is generated. Up to three rounds."
2. When the result lands, note you only ever see the *final* insight — the drafts died in private.
**The moment:** "You're seeing draft three, maybe. The tool eats its own mediocre output so you don't have to."

### 32. The honest failure
Show a sub-7 result presented without cosmetics.

**Setup:** a known weak pair (demo 29), or just dig until one appears.
**Run:**
1. Present the sub-7 insight with its score, unedited.
2. Read it aloud and agree with the judge: point at *why* it's merely fine.
3. Contrast with tools that would have shown this same output with confetti.
**The moment:** "5/10" on screen — a number that costs the tool something to display, which is why you can trust its 8s.

### 33. The threshold argument
Why 7, live.

**Setup:** a batch run's worth of scored outputs (demo 27) on hand.
**Run:**
1. Read a 6 and an 8 back to back, without revealing which is which. Ask the audience to place the bar.
2. Reveal. Discuss: 7 is where "I hadn't thought of that" reliably starts; below it is recombination you'd have gotten yourself.
**The moment:** the audience independently drawing the line where the threshold already is.

### 34. The unscored honesty
The judge fails to return a number — and the tool says so.

**Setup:** open `server.py` around the score-parsing in `dig()`.
**Run:**
1. Show the code path: if the judge's reply doesn't parse to a number in 1–10, `score` is `None` and the insight is *shown as unscored* — the comment in the source says it outright: shown as unscored rather than faked.
2. Show `keep()` handling it too: an unscored keeper writes `unscored` in its header, not an invented digit.
**The moment:** integrity in the failure path, verified in ten lines of code rather than a values statement.

### 35. The judge-severity A/B
Does a stronger model judge harder?

**Setup:** one rich pair, two models (see demo 30), five digs each.
**Run:**
1. Five digs per model on the same pair; tally the score distributions.
2. Discuss whatever you find honestly — severity differences, variance differences, or no difference.
**The moment:** treating your own tool as an experiment subject, live, with whatever result actually occurs.

### 36. The score census
Ten digs, one histogram, corpus health as a number.

**Setup:** demo 27's loop, plus a tally sheet.
**Run:**
1. Run ten digs; tally scores into buckets (≤5, 6, 7, 8+).
2. Interpret: heavy ≤6 means the corpus needs feeding (thin or same-y sources); a healthy spread with 8s means rich seams remain.
**The moment:** "corpus health" turning from a vibe into a distribution you drew in real time.

### 37. The rubber-stamp test
Prove the judge isn't sycophantic by showing it withholding.

**Setup:** `DEMOS.md` Demo 2 open as the receipts: three rounds, two rewrites accepted, never cleared 7, shown honestly at 5/10.
**Run:**
1. Walk the recorded case: the loop *tried* — accepted rewrites — and still refused the stamp.
2. Then dig live and let whatever score arrives, arrive.
**The moment:** "the same pair produced a 6 in another session" — even the judge's disagreements with itself are on the record.

### 38. The three-strikes code walk
The whole novelty loop, read straight from source.

**Setup:** `server.py` open at `dig()` — it's ~30 lines.
**Run:**
1. Read the loop aloud: connect → judge → if `score >= 7` or third attempt, stop → else rewrite and re-judge.
2. Point out what's *absent*: no retry-until-it-praises, no score massaging, no hidden system prompt full of superlatives.
**The moment:** the entire "AI quality control" story fitting in one visible loop, no framework required.

### 39. The judge-as-editor frame
For writers: recast the loop in their native workflow.

**Setup:** a writer in the audience; one dig ready to run.
**Run:**
1. Before digging, say: "Draft, edit letter, revision, edit letter, revision, accept or reject. That's the loop — the judge is an editor who explains the rejection."
2. Dig. Map what happened back onto the frame: the score is the accept/reject, the sub-7 explanation (internal) is the edit letter.
**The moment:** the writer recognizing a workflow they respect inside a tool they were about to dismiss.

### 40. The live rejection reading
Narrate a below-bar score the instant it happens.

**Setup:** none — this demo is opportunistic. Run digs until a sub-7 lands during any other demo.
**Run:**
1. The instant a 5 or 6 appears, stop the planned demo.
2. Say: "Watch what it *didn't* do — it didn't call this brilliant." Read the mediocre insight and let its mediocrity be audible.
3. Resume the planned demo.
**The moment:** an unplanned failure handled as a feature, because it is one.

---

## V. Chain demos

### 41. The signature chain
The dig → keep → chain arc from `DEMOS.md` Demo 3, run fresh.

**Setup:** corpus with 3+ tags represented.
**Run:**
1. Dig until a 7+ lands. Keep it.
2. Hit Chain. Narrate: "It's taking that insight and digging it against a source from a tag *not* in the original pair."
3. Read the chained result and name what the third domain did to the idea.
**The moment:** the idea coming back wearing the third domain's clothes — a framework returning as a story mechanic, or vice versa.

### 42. The exclusion mechanics demo
Show *how* chain forces distance.

**Setup:** a fresh insight and its pair's two tags known.
**Run:**
```sh
curl -s -X POST localhost:8420/api/chain \
  -d '{"insight": "<insight text>", "exclude": ["<tagA>", "<tagB>"]}'
```
1. Run it. Show the returned third source's tag — necessarily from outside the excluded pair.
2. Point at `pick_third()` in `server.py`: exclusion list in, eligible tags out.
**The moment:** "Chain can't take the easy road even if it wants to — the easy roads are excluded by construction."

### 43. The double chain
Chain the chain. Two forced translations deep.

**Setup:** a chained insight from demo 41, plus its accumulated tags.
**Run:**
1. Chain the *chained* insight headless, excluding all three tags touched so far (pair + first chain).
2. Read the second-generation output against the original dig. Trace the idea's drift across three domains.
**The moment:** either a compounding gain (rare, keep it immediately) or visible dilution — both teach where chaining's productive depth ends.

### 44. The keeper resurrection
Chain something you kept weeks ago.

**Setup:** `keepers.md` with older entries.
**Run:**
1. Pick an old keeper. Copy its text.
2. Chain it: `curl -s -X POST localhost:8420/api/chain -d '{"insight": "<old keeper text>", "exclude": []}'` — empty exclusion, let it collide with anything.
3. Compare the fresh chain against what you remembered the idea being for.
**The moment:** an archived idea producing new work — the keep pile as a renewable resource, not a graveyard.

### 45. The comedy forge
Force any insight through `creative-projects`.

**Setup:** a straight-faced insight (framework- or content-flavored); at least one `creative-projects` source.
**Run:**
1. Chain it with `"exclude"` listing every tag *except* `creative-projects`, so the third source must be creative.
2. Read the output looking for the story mechanic hiding in the serious idea.
**The moment:** the `DEMOS.md` signature move on demand — satire premise and product sketch in one output.

### 46. The brand forge
The reverse of 45: force a creative idea through `brand-frameworks`.

**Setup:** a story premise or comedy mechanic as the seed; a `brand-frameworks` source available.
**Run:**
1. Chain with exclusions leaving only `brand-frameworks` eligible.
2. Read the output for the framework hiding inside the bit.
**The moment:** a joke revealing its serious thesis — comedy as compressed analysis, decompressed on command.

### 47. The raw-seed chain
Chain doesn't require a dig output — any sentence is a valid seed.

**Setup:** one sentence typed fresh, never saved as a source.
**Run:**
1. `curl -s -X POST localhost:8420/api/chain -d '{"insight": "<your raw sentence>", "exclude": []}'`
2. Show that the "insight" parameter is just text — the endpoint dug your sentence against a random-tag source.
**The moment:** realizing chain is a general-purpose "collide this thought with my corpus" button.

### 48. The dual-use reveal
Stage the moment where one output is two deliverables.

**Setup:** run chains (demos 41/45) until an output reads as both a story mechanic *and* a product sketch — the recorded example is the CEO bot that literally cannot act on unverified promises.
**Run:**
1. Read the output once as fiction. Pause.
2. Read it again as a product spec, straight-faced.
3. Note nothing changed but your voice.
**The moment:** the same words holding both readings — chain mode's signature, demonstrated rather than described.

### 49. The chain-until-dry run
Deliberately over-chain and watch the returns diminish.

**Setup:** one strong dig result; cheap model configured (this burns calls).
**Run:**
1. Chain, then chain the result, then chain *that* result — three or four generations, logging each score.
2. Plot the scores by hand on paper.
**The moment:** the downslope — an honest demo of the tool's limits that doubles as a usage guideline ("chain once, maybe twice").

### 50. The chain race
Two chains from one seed; corpus randomness as a feature.

**Setup:** one strong insight as seed.
**Run:**
1. Fire the same chain request twice (same seed, same exclusions). Different third sources will be picked when the eligible pool has more than one option.
2. Read both outputs side by side; keep the better one.
**The moment:** two futures for one idea, generated in under a minute — pick-the-winner as a workflow.

---

## VI. Three-gate filter demos

### 51. The full pass
An insight clearing REVEAL, BUILD, and DELIVER — graduation live.

**Setup:** your strongest recent insight (a chained 7+ is the best candidate — `DEMOS.md` Demo 3 recorded a three-gate pass on one).
**Run:**
1. Hit Filter (or `curl -s -X POST localhost:8420/api/filter -d '{"insight": "<text>"}'`).
2. Read each verdict and reason aloud, gate by gate.
3. Say what a full pass means: "It graduated from *interesting* to *on-mission*. It now belongs to the brand thesis."
**The moment:** three checkmarks turning a cool output into a committed one.

### 52. The REVEAL fail
Clever but exposes nothing — caught at gate one.

**Setup:** feed the filter something ingenious but hollow: a wordplay-level connection, a neat analogy with no lie exposed underneath.
**Run:**
1. Filter it. Expect REVEAL to fail (if it passes, read the model's reason and argue with it out loud — that's a demo too).
2. Contrast with a passing insight: REVEAL asks "does this expose the lie of unlimited capacity?" — cleverness isn't exposure.
**The moment:** the filter rejecting something the room *liked* — taste enforced by gate, not applause.

### 53. The BUILD fail
Pure observation, no mechanism — caught at gate two.

**Setup:** an insight that's all diagnosis: true, resonant, and completely inactionable.
**Run:**
1. Filter it. Watch BUILD fail on "creates proof, practice, or capacity?" — an observation builds nothing.
2. Fix it live: chain the failed insight (demo 47) hunting for a mechanism, then re-filter.
**The moment:** using chain as the repair shop for a specific gate failure — the tools composing.

### 54. The DELIVER fail
A great idea that ignores bandwidth — caught at gate three.

**Setup:** an insight whose implied project is a six-month build; the brand thesis is limited bandwidth as design input.
**Run:**
1. Filter it. DELIVER asks "respects the bandwidth?" — a plan requiring 8-hour days from a 2-hour person fails here no matter how good it is.
2. Discuss: this is the gate that makes the filter *yours* rather than generic.
**The moment:** the tool rejecting an objectively good idea for a personally true reason.

### 55. The off-brand control
Filter something deliberately foreign to calibrate the gates.

**Setup:** a solid idea from a domain the brand doesn't touch — a cooking technique, a fitness insight.
**Run:**
1. Filter it. Expect failures — not because the idea is bad, but because the gates encode a specific thesis.
2. State it plainly: "The filter isn't a quality test. It's a *belonging* test."
**The moment:** good-but-not-mine getting bounced — the difference between a judge (novelty) and a filter (mission), demonstrated.

### 56. The audience-submission filter
Let a viewer put their own idea through the gates.

**Setup:** an audience member with an idea they're willing to have judged.
**Run:**
1. They dictate; you paste into the filter verbatim.
2. Read the three verdicts. Where a gate fails, read the model's reason and ask them if it's fair.
3. Remind them the gates encode *your* thesis — their idea failing DELIVER means it's not yours to build, not that it's bad.
**The moment:** a stranger's idea meeting a personal constitution and both surviving the encounter.

### 57. The graduation workflow
Filter as the checkpoint between dig and keep.

**Setup:** a fresh 7+ dig on screen.
**Run:**
1. Before hitting Keep, hit Filter. Narrate the discipline: "Score says it's novel. Gates say whether it's mine."
2. Full pass → Keep it. Any fail → chain it or let it go, out loud.
**The moment:** watching keep become a *decision* with criteria instead of a hoarding reflex.

### 58. The retroactive audit
Run old keepers through gates that didn't exist when they were kept.

**Setup:** `keepers.md` entries predating your filter discipline.
**Run:**
1. Copy an old keeper; filter it.
2. Tally a few: how many old keeps survive the gates?
3. Prune or re-chain the failures, live.
**The moment:** the keep pile getting *smaller* on stage — curation as a demo, and proof the gates have teeth even against your own past taste.

### 59. The gate-by-gate seminar
Two minutes on why these three questions and no others.

**Setup:** the three gates written large: REVEAL (exposes the lie of unlimited capacity?), BUILD (creates proof, practice, or capacity?), DELIVER (respects the bandwidth?).
**Run:**
1. For each gate, give the failure mode it prevents: REVEAL kills clever-but-empty; BUILD kills all-diagnosis-no-mechanism; DELIVER kills right-idea-wrong-life.
2. Then run one filter so the abstractions land on a concrete verdict table.
**The moment:** the audience realizing the gates are a serialized worldview — the filter is the brand, executable.

### 60. The meta-filter
Filter the tool's own pitch.

**Setup:** write Idea Digger's one-paragraph pitch as the input text.
**Run:**
1. Filter it. Read the verdicts on the tool's own description.
2. Whatever happens is the demo: a pass means the tool is on its own mission; a fail means either the pitch or the gates need work — say which, and fix it live.
**The moment:** the snake evaluating its own tail, honestly.

---

## VII. Keep pile & keepers.md demos

### 61. The first keep
The file that creates itself.

**Setup:** a fresh clone or a corpus where `keepers.md` doesn't exist yet (`mv keepers.md keepers.bak` to stage it).
**Run:**
1. `ls keepers.md` — no such file.
2. Dig, then Keep. `ls keepers.md` — it exists now, born from first use.
3. `cat` it: one entry, full anatomy visible.
**The moment:** no setup step, no "initialize your vault" — the product file appears the first time there's product.

### 62. The shovel speech
The single most important framing in the whole tool.

**Setup:** a `keepers.md` with real accumulation — a dozen entries across dates.
**Run:**
1. Open `keepers.md` full screen. Scroll it slowly, silently.
2. Say the line: "This file is the product. The app is just the shovel."
3. Close the app entirely — kill the server — and keep reading the file.
**The moment:** the app being *gone* while the value remains on screen.

### 63. The keeper anatomy
One entry, fully parsed.

**Setup:** any keeper entry.
**Run:**
1. Read the header aloud: `## 2026-07-19 — 8/10 — <label A> × <label B>` — date, honest score (including `unscored` when the judge failed to produce one), and provenance.
2. Note what the header enables: grep by score, grep by source, grep by month — demo 68 cashes this in.
**The moment:** realizing every keeper carries its own receipts — where it came from and how good the judge thought it was.

### 64. The git-diffable idea history
Version-control your insight archive.

**Setup:** the repo is already git; `keepers.md` tracked.
**Run:**
1. `git log --oneline -- keepers.md` — each commit is a digging session.
2. `git diff HEAD~1 -- keepers.md` — exactly what this week's thinking added.
3. Discuss: idea provenance for free, because the product is a text file in a repo.
**The moment:** `git blame keepers.md` — every insight timestamped and attributable, with zero infrastructure built for it.

### 65. The weekly review ritual
The keep pile as a recurring practice, demonstrated once.

**Setup:** a week's worth of keepers (or simulate with existing entries).
**Run:**
1. `grep "^## " keepers.md | tail -7` — the week's headers at a glance.
2. Triage aloud: for each, say *make it*, *chain it*, or *cut it*.
3. Execute one of each verdict: draft an opening line from a *make*, run demo 44 on a *chain*, delete a *cut*.
**The moment:** the pile visibly shrinking and sharpening in five minutes — maintenance as demo.

### 66. The content pipeline handoff
Keeper → published content, the last mile.

**Setup:** one strong keeper; your content workflow (brand-voice) ready in another window.
**Run:**
1. Read the keeper. Identify its content shape: essay angle, thread, framework post.
2. Hand it to the content flow and draft the hook live.
3. Trace the provenance chain out loud: two old sources → dig → judge → keep → this hook.
**The moment:** a published-quality opening line whose ancestry is fully documented — the whole tool justified by one deliverable.

### 67. The fearless delete
Keepers are markdown; curation is an editor operation.

**Setup:** `keepers.md` with at least one entry you've cooled on.
**Run:**
1. Open the file in any editor. Delete the stale entry. Save.
2. Show nothing broke — no orphaned IDs, no referential integrity, no app state to reconcile.
**The moment:** "Curation is just editing a document" — the absence of a database as a *feature* you can feel.

### 68. The grep-powered archive
Search the keep pile with tools from 1973.

**Setup:** a populated `keepers.md`.
**Run:**
```sh
grep -c "^## " keepers.md                 # how many keepers
grep "^## " keepers.md | grep "8/10"      # the best ones
grep -A3 "Botsly" keepers.md              # everything touching one project
```
1. Run each; narrate what question it answers.
**The moment:** three one-liners replacing what other tools ship as a search feature, a filter UI, and a tags system.

### 69. The ouroboros feed
A keeper goes back in as a source.

**Setup:** one keeper whose idea has grown beyond its entry.
**Run:**
1. Copy the keeper text; paste into Save. It gets tagged and labeled like any thought.
2. Dig until it pairs with something (or force the pair headless).
3. Note the compounding loop: output → corpus → deeper output.
**The moment:** the tool eating its own product and getting stronger — the flywheel drawn in one motion.

### 70. The empty-handed session
A digging session that keeps nothing, reported proudly.

**Setup:** any session; this demo is about the ending.
**Run:**
1. Run 3–4 digs. Suppose none clear your personal bar even at 7 — keep none.
2. `git diff keepers.md` → empty. Say so: "Today produced nothing worth keeping, and the file says exactly that."
3. Apply the operating rule: low yield means feed the corpus, so end by saving two new sources instead.
**The moment:** a tool whose empty result is legible and actionable rather than papered over.

---

## VIII. Headless & scripting demos

### 71. The seven-endpoint tour
The entire API surface in two minutes of curl.

**Setup:** terminal beside the browser; server running.
**Run:** hit each endpoint once, in workflow order, narrating the one-line purpose:
```sh
curl -s -X POST localhost:8420/api/save   -d '{"text": "Demo idea."}'          # ingest
curl -s -X POST localhost:8420/api/retag  -d '{"file": "<f>", "tag": "essays"}' # correct
curl -s -X POST localhost:8420/api/pick   -d '{}'                               # pair
curl -s -X POST localhost:8420/api/insight -d '{"a": "<f1>", "b": "<f2>"}'      # dig
curl -s -X POST localhost:8420/api/chain  -d '{"insight": "<t>", "exclude": []}' # deepen
curl -s -X POST localhost:8420/api/filter -d '{"insight": "<t>"}'               # gate
curl -s -X POST localhost:8420/api/keep   -d '{"insight": "<t>", "score": 8, "pair": "A × B"}' # bank
```
**The moment:** "That's the whole API. The UI calls exactly these seven; you just did everything the app can do."

### 72. The one-line prospector
The batch dig as a single shell pipeline — demo 27's loop, presented as a tool.

**Setup:** cheap model configured; the loop from `DEMOS.md` saved as `prospect.sh`.
**Run:**
1. `sh prospect.sh` — ten scored one-liners scroll by.
2. Point out the pattern: scores as a triage column, truncated insights as scannable previews.
3. Re-dig the best pair at full attention in the UI.
**The moment:** prospect cheap and wide, then dig deep — a mining strategy expressed in twelve lines of shell.

### 73. The overnight shift
Set up an unattended batch and read the results next morning (compressed to two minutes for demo).

**Setup:** cheap model in `config.json`; the prospect loop redirected to a file.
**Run:**
1. `sh prospect.sh >> overnight.log 2>&1 &` — narrate: "That's the whole job system."
2. Show reading the morning after: `grep -E "^\[(8|9|10)" overnight.log` — only the winners.
3. State the cost math honestly: N digs × 2–4 calls × your model's price.
**The moment:** "batch processing infrastructure" revealed to be an append redirect and a grep.

### 74. The notes-folder ingest
Bulk-feed a directory of existing notes.

**Setup:** a folder of your real .md/.txt notes (5–10 files for demo pace).
**Run:**
```sh
for f in ~/notes-sample/*.md; do
  python3 -c 'import json,sys; print(json.dumps({"text": open(sys.argv[1]).read()}))' "$f" \
    | curl -s -X POST localhost:8420/api/save -d @-
  echo " ← $f"
done
```
1. Run it; watch each note get tagged as it lands.
2. Dig the newly fattened corpus immediately.
**The moment:** years of inert notes becoming dig-eligible in one loop — phase 2's bulk import, previewed in six lines.

### 75. The no-jq JSON handling
Every pipeline in this doc uses only python3 — demonstrate the pattern once, explicitly.

**Setup:** any endpoint response.
**Run:**
1. Show the extraction idiom: `curl -s ... | python3 -c "import json,sys; print(json.load(sys.stdin)['insight'])"`.
2. Note the symmetry with the tool itself: stdlib server, stdlib client — `jq` is a dependency the pipeline doesn't need.
**The moment:** the zero-dependency philosophy extending past the app into how you *drive* the app.

### 76. The file-to-source one-liner
Any file on disk becomes a source in one command.

**Setup:** one interesting file anywhere on disk.
**Run:**
```sh
python3 -c 'import json,sys; print(json.dumps({"text": open(sys.argv[1]).read()}))' ~/Desktop/idea.txt \
  | curl -s -X POST localhost:8420/api/save -d @-
```
1. Run it; read back the tag and label.
**The moment:** "the import feature" being a command you compose rather than a feature someone had to build.

### 77. The morning-dig cron
One scheduled dig per day, appended to a log.

**Setup:** the prospect loop trimmed to a single dig, saved as `daily-dig.sh` appending to `daily.log`.
**Run:**
1. Show the crontab line: `0 7 * * * cd ~/Projects/insight-excavator && sh daily-dig.sh`.
2. Run the script manually to show one day's output: one scored insight with its pair.
3. Show `daily.log` accumulating — a slow drip of prospecting requiring zero attention.
**The moment:** an "AI automation" whose entire stack is cron, sh, and a text file.

### 78. The clipboard round-trip
Dig result straight to clipboard, ready to paste anywhere.

**Setup:** macOS; one known-good pair.
**Run:**
```sh
curl -s -X POST localhost:8420/api/insight -d '{"a":"<A>","b":"<B>"}' \
  | python3 -c "import json,sys; print(json.load(sys.stdin)['insight'])" | pbcopy
```
1. Run it, then Cmd-V into a note, a draft, a chat.
**The moment:** dig-to-draft with no window switching — the tool as a keyboard-distance service.

### 79. The agent's shovel
Another AI drives the digger.

**Setup:** a Claude Code session (or any agent with shell access) in the repo.
**Run:**
1. Ask the agent: "Run three digs, keep anything scoring 8+, and summarize what it kept."
2. Watch it compose the same curl calls from `DEMOS.md`'s recipes.
3. Read the resulting `keepers.md` additions.
**The moment:** the API being simple enough that an agent uses it correctly from the docs alone — machine-operability as a side effect of human simplicity.

### 80. The smoke test
Health-check the whole system in one script.

**Setup:** `smoke.sh` in the repo root:
```sh
set -e
F=$(curl -s -X POST localhost:8420/api/save -d '{"text":"smoke test idea"}' \
  | python3 -c "import json,sys;print(json.load(sys.stdin)['file'])")
curl -s -X POST localhost:8420/api/retag -d "{\"file\":\"$F\",\"tag\":\"other\"}" >/dev/null
curl -s -X POST localhost:8420/api/pick -d '{}' >/dev/null
echo "OK: save, retag, pick alive (insight/chain/filter cost money — run manually)"
```
**Run:** `sh smoke.sh` — one line of green.
**The moment:** the free endpoints verified in a second, with the paid ones deliberately excluded — even the smoke test respects the budget.

---

## IX. Architecture & philosophy demos

### 81. The three-files tour
The entire system, inventoried on one screen.

**Setup:** repo root in a terminal.
**Run:**
1. `ls` — point in turn: `server.py` (whole backend), `index.html` (whole frontend), `config.json` (model name), `sources/` (the data), `keepers.md` (the product).
2. `wc -l server.py index.html` — read the totals aloud.
**The moment:** the full inventory of a working AI product fitting in one `ls` — nothing off-screen, nothing "and also the microservices."

### 82. The where's-the-database demo
State lives in the filesystem; prove it by inspection.

**Setup:** any working corpus.
**Run:**
1. Ask the audience: "Where do you think the data is?" Collect guesses (SQLite, JSON store…).
2. `ls sources/` + `cat` one file + `cat keepers.md`. That's all of it.
3. Kill the server. The data is still there, because the server never held any.
**The moment:** the backup strategy revealed as "copy the folder" and the migration strategy as "move the folder."

### 83. The stdlib-only proof
No dependencies — verified, not asserted.

**Setup:** `server.py` in a terminal.
**Run:**
1. `grep "^import\|^from" server.py` — every line is Python standard library.
2. `ls` — no `requirements.txt`, no `venv/`, no `node_modules/`, no lockfile.
3. "It runs on any Mac's system Python, forever. There is no supply chain to rot."
**The moment:** the grep output — an entire class of maintenance problems visibly absent.

### 84. The hot-swap
Change models mid-session with no restart.

**Setup:** server running, mid-demo.
**Run:**
1. Dig once on the current model.
2. Without touching the server, edit `config.json`'s `model` value and save.
3. Dig again — the new model answered. `config.json` is re-read on every call.
**The moment:** "config reload" as a non-feature: nothing was built, the file is just read when needed, and that's *why* it can't break.

### 85. The M-variable override
Per-run model choice from the environment.

**Setup:** terminal, server stopped.
**Run:**
1. `M=anthropic/claude-opus-4.8 python3 server.py` — narrate the resolution order: `M` env var first, `config.json` second.
2. Dig once on the strong model, then Ctrl-C and relaunch bare for the cheap default.
**The moment:** "expensive mode" being a shell prefix — cost control at the invocation, not in a settings screen.

### 86. The kill-and-restart
Nothing to lose because nothing is held.

**Setup:** mid-session, insights on screen.
**Run:**
1. Ctrl-C the server mid-demo, theatrically.
2. `python3 server.py` again; reload the page.
3. Every source, every keeper: intact. Only the unsaved screen state is gone — which is why Keep exists.
**The moment:** the crash-recovery story being "there is nothing to recover" — statelessness demonstrated by assassination.

### 87. The ten-minute code read
Read the entire backend, live, top to bottom.

**Setup:** `server.py` open, an audience with ten minutes.
**Run:**
1. Read it in order: `model_name`, `ai`, `classify`, `save_source`/`load_source`, `by_tag`/`pick_pair`/`pick_third`, `dig`, `run_filter`, `keep`, then the handler's seven routes.
2. At each function, one sentence on what it does — most functions are shorter than the sentence.
**The moment:** finishing. Most tools cannot be read to the end; this one can be read in a sitting, and now the whole audience has.

### 88. The constraint-driven meta-demo
The tool as an argument for its own philosophy.

**Setup:** the brand thesis stated: limited bandwidth as core design input.
**Run:**
1. Walk the constraint→decision chain: limited hours → no database to admin → files; no dependency updates → stdlib; no deployment → localhost; no UI framework → one HTML file.
2. Then run one dig, so the constrained thing is seen *working*.
**The moment:** realizing the tool is the brand's proof-of-work — it exists *because* of the constraint it preaches, not despite it.

### 89. The fearless rm
Delete a source; nothing downstream breaks.

**Setup:** a corpus with an expendable source.
**Run:**
1. `rm sources/<file>.txt` — no app, no confirmation dialog, just rm.
2. Dig — the pick simply no longer includes it. Keepers that came from it still stand (they carry their provenance in their own header).
**The moment:** no cascade, no orphan errors, no referential panic — deletion as safe as it looks, because nothing points at anything.

### 90. The cost-transparency demo
Count the money per dig, out loud.

**Setup:** `dig()` visible in `server.py`; your model's per-call rough cost known.
**Run:**
1. Trace a dig's calls: 1 connect + 1 judge = 2 calls minimum; each sub-7 round adds a rewrite + re-judge, so worst case 3 rounds ≈ 4+ calls. Chain and filter cost their own calls; save costs one (classify).
2. Do the arithmetic for a ten-dig session on your current model, on a napkin.
**The moment:** an AI tool whose complete cost model fits on a napkin because the complete call graph fits in one function.

---

## X. Audience-specific demos

### 91. For the developer
Code-forward, UI-optional.

**Setup:** terminal only; browser closed the whole time.
**Run:**
1. Open with the stdlib grep (demo 83) and the seven-endpoint tour (demo 71).
2. Run the batch loop (demo 27); pipe a winner to the filter.
3. Close with the ten-minute code read offer (demo 87) — most developers take it.
**The moment:** an entire "AI product demo" without opening a browser — developers trust what they can curl.

### 92. For the writer
The tool as an angle-generator and honest editor.

**Setup:** two or three of *their* pieces (or ideas) saved as sources before the session.
**Run:**
1. Frame the judge as an editor (demo 39).
2. Dig their material against your frameworks; read the insight as a pitch: "That's an essay angle you didn't have this morning."
3. Show `keepers.md` as the commonplace book their favorite dead authors kept — except each entry carries a score and a source pair.
**The moment:** the dig output phrased as their next piece's thesis, not as "AI content."

### 93. For the brand strategist
Gates first, digs second.

**Setup:** the three gates written out; a mixed bag of insights ready to filter.
**Run:**
1. Open with the gate-by-gate seminar (demo 59): the filter as an executable brand thesis.
2. Run the off-brand control (demo 55) — good idea, bounced, because belonging ≠ quality.
3. Then show where filter candidates come from: one dig, one chain.
**The moment:** "You could encode *your* client's positioning as three gates" — the filter pattern as a portable deliverable.

### 94. For the skeptic
Failures first, receipts always.

**Setup:** demo 9's weak pair; `DEMOS.md` Demo 2 open; `server.py` at the unscored-honesty lines.
**Run:**
1. Open with the honest failure (demo 32).
2. Show the code that refuses to fake a score (demo 34) — integrity verified in source, not asserted.
3. Only then run a live dig and let it score whatever it scores.
**The moment:** the skeptic auditing the failure path and finding it clean — after that, the successes get believed.

### 95. For the productivity person
Enter through the bandwidth thesis.

**Setup:** the honest-bandwidth-planner source in the corpus (or their own capacity complaint saved live).
**Run:**
1. Save their sentence about their real available hours. Dig it against `brand-frameworks`.
2. Read the insight through their lens: capacity as a design input, not a guilt metric.
3. Show DELIVER (demo 54): a tool that rejects ideas for *not fitting a real life*.
**The moment:** gate three — they've never seen software that says "good idea, wrong bandwidth."

### 96. For the non-technical friend
UI only; zero terminal, zero jargon.

**Setup:** browser full-screen, terminal hidden, corpus loaded.
**Run:**
1. The guessing game (demo 4) — it needs no technical framing at all.
2. Let *them* click Dig and Keep. Narrate scores as "it grades itself and shows you the grade."
3. End on `keepers.md` opened in a pretty markdown viewer: "this is my notebook of ideas it found."
**The moment:** them clicking Dig a third time without being asked — the loop is legible enough to be moreish.

### 97. For the potential collaborator
Their idea × your framework, as a compatibility test.

**Setup:** one source from them, saved with permission; your corpus intact.
**Run:**
1. Dig their idea against your `brand-frameworks` directly (hand-picked pair, demo 24).
2. Read the insight as the answer to "what would we make together?"
3. Chain it once (demo 41) to see the collaboration's second move.
**The moment:** a concrete joint-project sketch existing before the coffee is finished — the dig as a due-diligence instrument for partnerships.

### 98. For a live audience or stream
The guessing game, scaled and scored.

**Setup:** streaming/projecting the UI; chat or the room as contestants; cheap model to keep pace snappy.
**Run:**
1. Dig; freeze on the pair labels; the room posts guesses on a timer.
2. Reveal insight + score. Award the closest guess. Repeat five rounds.
3. Between rounds, take one audience idea into Save so the corpus grows on air.
**The moment:** the audience arguing with the judge's score — engagement no scripted demo produces, because the outputs are genuinely unscripted.

### 99. For future-you
The handoff demo: prove the project survives your absence.

**Setup:** pretend three months have passed. Open nothing from memory.
**Run:**
1. Cold-orient from files alone: `README.md` (how to run), `roadmap.md` (where it's going), `docs/PHASE-3-4-PICKUP.md` (exact pickup notes), `keepers.md` (what it's produced).
2. Get from cold start to a running dig using only what's written down. Time it.
**The moment:** the stopwatch — a project whose complete resurrection procedure is documented and takes minutes, because there's nothing undocumentable in it.

### 100. The mission demo
The one that explains why any of this exists.

**Setup:** the origin fact: years of ideas trapped in ChatGPT/Claude/Gemini chat exports — the original mission is mining them out. One real excerpt from an old chat export, ready to paste.
**Run:**
1. Tell it straight: "My best thinking is buried in conversations no one will ever scroll back through."
2. Paste the old excerpt into Save — a thought from a dead conversation, resurrected into the corpus in five seconds (demo 18 proved the mess is fine).
3. Dig it against something current. Whatever emerges is a collaboration between who you were and who you are.
4. Point at `roadmap.md` phase 2: "Bulk import does this for *all* of them. Everything you just watched is the machinery waiting for that ore."
**The moment:** an idea from a months-dead chat producing a scored insight today — the whole tool's reason for existing, enacted in one dig.

---

*Companion file: `DEMOS.md` has the real session transcripts and the canonical curl
recipes. Every demo above runs against the live tool — the outputs will be yours,
not these pages'.*

# 101 Demos for Fun and Profit

The companion to `100-brilliant-demos.md`. That file teaches the tool; this one
*uses* it — fifty demos for fun (games, stunts, play), fifty for profit (pipelines,
client plays, products), and one grand finale. Same rules as before: these are
scripts, not transcripts. Run any of them against the live tool and the output is
real; where sample output would help, only its shape is described, never faked.

Conventions:

- Server running: `export OPENROUTER_API_KEY=sk-or-... && python3 server.py` → `http://localhost:8420`
- Tags: `content-topics`, `brand-frameworks`, `creative-projects`, `essays`, `other`
- Judge threshold 7/10, max 3 rounds; each dig is 2–4 model calls — cheap model for anything batch or party-paced
- Endpoints: `/api/save`, `/api/retag`, `/api/pick`, `/api/insight`, `/api/chain`, `/api/filter`, `/api/keep`
- "Headless" means the curl recipes from `DEMOS.md`

---

# PART ONE: FUN

## I. Party & social games

### 1. Insight Poker
Bet on the judge before it speaks.

**Setup:** 3+ players, a pile of chips (or matchsticks), cheap model, server projected.
**Run:**
1. Hit Dig. Freeze when the pair labels appear, before the insight lands.
2. Each player antes one chip and bets on the final score: under 7, exactly 7, or 8+.
3. Reveal. Correct bracket splits the pot. Five hands per game.
4. House rule: anyone may double their bet after *reading* the insight but before the score reveals — that's the skill round.
**The payoff:** by hand three, everyone has internalized what "novel" means to the judge — you've taught your quality bar as a gambling game.

### 2. Human vs. Machine
The connection-writing duel.

**Setup:** 2+ players, paper, a timer, one dig ready.
**Run:**
1. `curl -s -X POST localhost:8420/api/pick -d '{}'` — read both source texts aloud in full.
2. Three minutes: every human writes their best non-obvious connection.
3. Fire the dig on the same pair. Read all entries — human and machine — anonymously shuffled.
4. Vote for the best *without knowing which is the machine's*. Then reveal.
**The payoff:** sometimes a human wins. Those wins are worth saving as sources themselves — the game is secretly a corpus feeder.

### 3. The Chain Gang
Collaborative deep-drilling, one exclusion at a time.

**Setup:** 3–5 players in a circle, one strong dig result as the seed.
**Run:**
1. Player one chains the seed (headless, `exclude` = the pair's tags), reads the result aloud dramatically.
2. Player two chains *that* result, excluding one more tag of their choice. Around the circle until tags run out or the chain scores below 6.
3. The group votes: which link in the chain was the peak?
**The payoff:** the peak is almost never the last link — a group-discovered lesson in when to stop chaining, disguised as a parlor game.

### 4. Two Truths and a Dig
Party classic, corpus edition.

**Setup:** one guest of honor; three insights prepared — two real keepers from `keepers.md`, one you wrote yourself in keeper style.
**Run:**
1. Read all three as if the machine dug them. The room votes on which is the human fake.
2. Reveal, then run a live dig so they see the machine's actual register.
**The payoff:** whichever way the vote goes, it's interesting: if they can't spot the fake, your style has converged with your tool's; if they can, discuss what gave it away.

### 5. The Oracle Booth
Idea Digger as a party fortune-teller.

**Setup:** laptop in a corner with a sign: "THE ORACLE. Feed it a worry, receive a strange truth. Free." Corpus loaded.
**Run:**
1. Guest types one sentence about something on their mind. Save it (it'll usually land in `other` or `content-topics`).
2. Dig their sentence against your corpus (hand-pick a `brand-frameworks` or `essays` source for gravitas).
3. Read the insight to them in a fortune-teller voice. Offer a printout if you have a printer; screenshot to their phone if not.
**The payoff:** the insights are real, which makes the bit land harder than any fake oracle — people queue.

### 6. Corpus Karaoke
Everyone feeds one source; the machine finds out who rhymes with whom.

**Setup:** a group of friends, each willing to contribute one idea; a fresh sources folder (`mv sources sources.mine && mkdir sources`).
**Run:**
1. Each person saves one idea, initialed in the text ("— R.J.").
2. Dig repeatedly. Every pair is now two *people* colliding.
3. When an 8 lands, the two contributors take a bow together.
4. Restore your corpus after.
**The payoff:** the room discovers which two friends' brains secretly run the same firmware — a social graph drawn by novelty score.

### 7. Speed Dig
Sixty seconds, most keepers wins.

**Setup:** two players, two terminals, both driving the same server headless; cheap model; a referee with a stopwatch.
**Run:**
1. Sixty seconds each turn: pick, dig, and *decide* — keep or discard — as many times as possible. Keeps must be genuine (the player defends each at the end).
2. Referee disqualifies indefensible keeps. Highest surviving count wins.
**The payoff:** under time pressure, everyone discovers their true keep bar — and how fast the judge-then-human pipeline can actually cycle.

### 8. The Bad Idea Amnesty
Everyone brings their worst idea; the machine finds its redeeming feature.

**Setup:** guests each bring one idea they've abandoned or are embarrassed by.
**Run:**
1. Save each bad idea. Dig it against your strongest `brand-frameworks` source (hand-picked pair).
2. The dig hunts for the structural rhyme — often the "bad" idea contains one sound mechanism the insight isolates.
3. Filter the best rescue through the three gates for maximum ceremony.
**The payoff:** at least one person leaves un-embarrassed about a dead idea — the digger as a redemption machine.

### 9. Judge Roulette
The audience predicts, the judge disposes, everyone argues.

**Setup:** projected screen, any group that likes arguing.
**Run:**
1. Dig. Read the insight aloud *without* the score. The room debates and settles on a consensus score.
2. Reveal the judge's number. Any gap of 2+ points triggers a structured argument: one person defends the judge, one prosecutes.
3. Loser of the argument feeds the corpus a new source as penalty.
**The payoff:** the penalty *is* the point — arguments about taste literally grow the corpus.

### 10. The Long Con
A season-long league across multiple game nights.

**Setup:** a recurring group; a `league.md` file tracking standings.
**Run:**
1. Every game night, run demos 1, 2, and 9 as fixed events. Points for poker wins, human-beats-machine wins, and closest-to-judge predictions.
2. Log standings in `league.md` next to `keepers.md`.
3. Season trophy: the winner gets a keeper formally dedicated to them in its header (`— dug in honor of <name>`).
**The payoff:** friends develop a shared model of *your* quality bar over weeks — and your corpus grows every session without you feeding it alone.

## II. Weird-corpus experiments

### 11. The All-Villains Corpus
A sources folder of nothing but antagonists.

**Setup:** swap corpora (`mv sources sources.main && mkdir sources`). Save 5–6 sources, each describing one great villain's method — fictional or historical, your call.
**Run:**
1. Dig the villains against each other. The cross-tag rule still applies, so tag them during save by *domain* (a corporate villain → `brand-frameworks` will happen naturally; a story villain → `creative-projects`).
2. Chain the best insight against your restored main corpus later for the real harvest.
**The payoff:** villain methods are just strategies with the empathy removed — digging them yields unusually crisp mechanism-first insights. Restore the folder when done.

### 12. The Dead Philosophers Dinner Party
Six thinkers, one folder.

**Setup:** fresh corpus; save one paragraph summarizing a core idea from each of six thinkers you actually know well enough to summarize.
**Run:**
1. Dig. You're now running structured collisions between, say, Stoic capacity limits and whoever else you invited.
2. Keep anything 8+; these keepers make exceptional essay seeds.
**The payoff:** it's a reading-notes review technique disguised as a séance — you only get good digs from thinkers you summarized well, so the low scores audit your own understanding.

### 13. The Genre Blender
Your horror universe versus your comedy universe.

**Setup:** main corpus, but ensure it holds at least one KVOID/DON'T STAY-flavored source and one Botsly/ByteWorks source, both in `creative-projects` — so they can't pair directly.
**Run:**
1. Dig until a horror source pairs with something; keep the insight.
2. Chain that insight with `exclude` set so the third source must come from wherever the comedy lives — or paste the horror insight as a raw chain seed and let it hit Botsly.
**The payoff:** horror logic passed through workplace comedy produces the "smiling dread" register — pin the best output for both writers' rooms.

### 14. The One-Word Sources
Minimum-information digging.

**Setup:** fresh corpus. Save five sources of exactly one word each — big words: "debt," "threshold," "rehearsal," "inventory," "haunting."
**Run:**
1. Dig. The connect prompt now has almost nothing to work with — watch what the model imports to fill the vacuum.
2. Score census across five digs: does minimal input produce inflated or deflated novelty scores?
**The payoff:** a probe of where insights actually come from — the sources or the model's priors. The answer (visible in what it imports) tells you how much your real corpus is steering.

### 15. The Time Capsule Corpus
You, five years ago, as a sources folder.

**Setup:** dig up genuinely old writing — old tweets, old notes, old bios. Save 5–8 pieces verbatim, typos preserved.
**Run:**
1. Dig old-you against old-you first. Keep the best.
2. Then chain the best insight into your *current* main corpus.
**The payoff:** the chain step is the demo — the moment your current framework metabolizes an idea you had before the framework existed. Frequently produces the "I've been circling this for years" keeper.

### 16. The Complaint Corpus
Nothing but things that annoy you.

**Setup:** fresh corpus; save 6–8 pure complaints, one per source. No solutions allowed in the text.
**Run:**
1. Dig complaints against each other. Complaints are unpriced demand — the digs will keep finding shared root mechanisms.
2. Run every 7+ through the three-gate filter. BUILD is the interesting gate: it forces mechanism onto grievance.
**The payoff:** this is a startup-idea generator wearing a grouch costume. The filter's BUILD gate converts whining into specs.

### 17. The Instruction Manual Remix
Sources from the most boring text in your house.

**Setup:** fresh corpus; save paragraphs from real manuals — a thermostat, a rice cooker, tax instructions.
**Run:**
1. Dig manuals against each other for the comedy of it (results are reliably funny read aloud).
2. The real experiment: chain one manual paragraph as a raw seed into your main corpus. Procedural language colliding with brand frameworks yields strange, precise metaphors.
**The payoff:** proof that the tool's floor is entertainment even on the worst possible corpus — and an occasional genuinely usable metaphor ("your attention has a lint trap").

### 18. The Lyric Seam
Song fragments as sources.

**Setup:** save 5–6 of your own lyric fragments or hooks (yours — don't corpus other people's copyrighted lines) tagged into `creative-projects` and `other`.
**Run:**
1. Dig lyrics against your `brand-frameworks`. Compression meets structure.
2. Keep anything that reads as either a better lyric *or* a better framework — it'll happen in both directions.
**The payoff:** lyrics are pre-compressed emotion; frameworks are pre-compressed logic. The digs trade payloads. Feeds both the music projects and the essay pile.

### 19. The Dream Journal Week
Seven mornings, seven sources, then one dig session.

**Setup:** for one week, save each morning's dream fragment (however garbled) the moment you wake. They'll mostly tag `other`.
**Run:**
1. On day eight, dig the week. Dreams against frameworks, dreams against projects.
2. Expect mostly sub-7s; keep the outliers.
**The payoff:** the judge is a surprisingly good filter for which dream-logic actually contains an idea versus which is just noise — a use case no other tool in your stack covers.

### 20. The Adversarial Corpus
Sources written specifically to break the judge.

**Setup:** fresh corpus. Write 5 sources engineered to trap the system: one that's pure buzzwords, one that's profound-sounding nonsense, one real insight dressed shabbily, one banality dressed beautifully, one normal control.
**Run:**
1. Dig all combinations you can force (hand-picked pairs). Log every score.
2. Grade the judge: did buzzwords score high? Did the shabby real insight score low?
**The payoff:** a calibration report card for your current model. Re-run whenever you change `config.json` — this corpus is a reusable test fixture. Keep it in `sources.adversarial/` for exactly that.

## III. Challenges & competitions

### 21. The 30-Day Dig Streak
One dig a day, in public.

**Setup:** the daily-dig cron from the first doc (demo 77), or a manual morning ritual; a thread or channel where you post.
**Run:**
1. Every day for 30 days: one dig, post the insight and its honest score — including the 5s.
2. Weekly recap post: score distribution, best keeper, what you fed the corpus.
**The payoff:** the honest scores are the content hook — an AI series where the machine visibly fails 40% of the time out-credibilities every cherry-picked AI feed on the timeline.

### 22. The Keeper Derby
Two corpora enter, one wins the week.

**Setup:** you and a friend who's built their own corpus (help them via demo 6's mechanics — the tool is three files, they can run their own).
**Run:**
1. Each of you runs ten digs on your own corpus this week. Exchange your top-3 keepers, stripped of scores.
2. Each scores the other's keepers blind, then compare with the judges' scores.
3. Winner: most 8+ agreements between human and judge.
**The payoff:** the derby quietly answers the real question — whose *corpus* is richer, not whose model is better. Losing means feed your sources, which is the correct incentive.

### 23. The Iron Chef Corpus
Secret ingredient digging, timed.

**Setup:** a referee picks one "secret ingredient" source neither player has seen and saves it to both players' corpora at the whistle.
**Run:**
1. Thirty minutes: each player must produce their best insight *involving the secret source* (hand-picked pairs allowed, chains allowed).
2. Present to the referee: insight, score, and a one-line "what I'd make from it."
**The payoff:** the constraint forces both players off their favorite pairs — everyone discovers a corpus region they'd been ignoring.

### 24. The Sub-7 Salvage
Competitive rescue of the judge's rejects.

**Setup:** a log of sub-7 digs (any batch run produces them); 2+ players.
**Run:**
1. Each player picks one rejected insight and gets three chain calls (any exclusions) to raise it.
2. Best final score wins; ties broken by three-gate filter results.
**The payoff:** teaches the highest-skill move in the whole tool — reading *why* something is mediocre and choosing which domain will fix it.

### 25. The Century Run
Dig every possible pair in the corpus. All of them.

**Setup:** a small corpus (6–8 sources — pairs grow fast), cheapest viable model, a Saturday.
**Run:**
1. Script the full cross-tag pair matrix headless (a nested loop over `sources/*.txt`, skipping same-tag pairs) — log every insight and score to `century.log`.
2. Produce the atlas: which source appears in the most 7+ pairs? That's your corpus's keystone.
**The payoff:** total knowledge of a small corpus — you'll find exactly one or two keystone sources, and knowing which they are changes what you feed next.

### 26. The Blindfold Filter
Predict all three gates before the model rules.

**Setup:** a stack of unfiltered insights; players write predictions (P/F × 3 gates) before each filter call.
**Run:**
1. Filter each insight. Score predictions: one point per gate called correctly, bonus for a perfect three.
2. Ten insights per round.
**The payoff:** anyone scoring 25+/30 has internalized your brand thesis well enough to apply it without you — which is exactly the test for a potential collaborator (see demo 76).

### 27. The Model Ladder
Same corpus, climbing model tiers, tracking what money buys.

**Setup:** three models of ascending price configured one at a time via `config.json` (re-read per call — no restarts); one fixed set of five hand-picked pairs.
**Run:**
1. Dig all five pairs on each model. Fifteen digs total, logged with model names.
2. Publish your findings to yourself in a note: score deltas, prose deltas, and whether the *judge* tier matters more than the *connector* tier.
**The payoff:** an evidence-based answer to "which model should M point at for real sessions" — bought once, used every session after.

### 28. The Feeding Race
Which source type fattens the corpus fastest?

**Setup:** three feeding sessions on three days: day one feed only complaints, day two only old chat excerpts, day three only fresh original thoughts. Five sources each.
**Run:**
1. After each feeding, run five digs and log the score distribution.
2. Compare the three distributions.
**The payoff:** an empirical ranking of your own ore grades — most people assume fresh thoughts win and are wrong; old chat excerpts (pre-loaded with context) often dig richer.

### 29. The Solo Time Trial
Idea-to-published, against the clock.

**Setup:** stopwatch; your content pipeline warm (brand-voice flow ready); server running.
**Run:**
1. Clock starts: dig until a 7+, filter it, keep it, draft the post from it, and get it to "publishable draft."
2. Log the time. Re-run monthly; track the trend.
**The payoff:** the metric that matters — corpus-to-content latency. When it drops under 20 minutes, the pipeline is real (see Part Two).

### 30. The Turing Keeper
Slip one machine keeper into your human notebook — can future-you tell?

**Setup:** your regular notes app plus `keepers.md`; a note to yourself scheduled a month out.
**Run:**
1. Copy one keeper into your notes, unlabeled, phrased as your own thought.
2. In a month, review the notes and try to spot the implant before checking the answer.
**The payoff:** if you can't find it, the tool's output has reached parity with your notebook voice — an important private milestone. If you can, what gave it away is a spec for better prompts.

## IV. Content & entertainment stunts

### 31. The Live Dig Stream
An hour of unscripted digging, scores and all.

**Setup:** stream or space; screen shared; cheap-but-decent model; chat able to submit sources.
**Run:**
1. Open with three digs on your corpus, narrating the loop honestly (rounds, threshold, rejections).
2. Take chat-submitted ideas into Save on air; dig them against your frameworks.
3. Close with the session's keepers read aloud, scores attached.
**The payoff:** live sub-7s are the retention mechanic — viewers stay to see whether the next one clears the bar. Fully unfakeable content.

### 32. The Insight Advent Calendar
Twenty-five pre-dug keepers, released daily.

**Setup:** a batch weekend (demo 25's century run works) yielding 25 keepers of 7+; a scheduling tool for daily posts.
**Run:**
1. Post one keeper a day with its score and pair provenance ("dug from: X × Y").
2. Day 25: post the score distribution of everything that *didn't* make the calendar.
**The payoff:** the provenance line is the differentiator — every post demonstrates the method while delivering the content. The finale post converts curiosity into "how do I do this" replies.

### 33. Botsly Reads the Keepers
The comic bot as the insight anchor.

**Setup:** your best recent keepers; the ByteWorks comic-script flow.
**Run:**
1. Feed a keeper into a strip premise: Botsly encounters the insight and takes it perfectly literally.
2. The strip's caption cites the keeper verbatim — comic as delivery vehicle, keeper as payload.
**The payoff:** one dig output serving two channels at once (comic beat + idea content) — chain mode's dual-use signature turned into a repeatable format.

### 34. The Roast My Corpus Invitational
Guests submit; the judge humiliates or crowns.

**Setup:** an open call: "send me one idea, the machine will score its collision with my frameworks." Consent implied by submission; publish first names only or handles.
**Run:**
1. Save each submission, dig it against your corpus (hand-picked against your strongest framework source for fairness).
2. Publish results as a leaderboard: score, insight excerpt, submitter handle.
**The payoff:** people share their own placement, especially the 8s and — reliably — the proud 4s. The leaderboard is self-distributing content.

### 35. The Insight Autopsy Series
Long-form breakdowns of single digs.

**Setup:** one genuinely great keeper; a writing slot.
**Run:**
1. Post the full anatomy: both source texts, the final insight, the score, and your reconstruction of *why* the seam existed.
2. End each autopsy with "what I'm making from it" and, next issue, report whether you did.
**The payoff:** the accountability loop ("did he actually make it?") converts a content series into a public commitment device — fun becomes profit at exactly this seam.

### 36. The Wrong Answers Only Special
An episode of nothing but the judge's rejects.

**Setup:** a collected log of sub-7 insights with their scores.
**Run:**
1. Present the rejects as a gallery: "the machine thought these were mediocre — was it right?"
2. Audience votes on any the judge wronged. Chain the audience's picks live or in the follow-up.
**The payoff:** inverts the AI-content formula (only showing wins) so thoroughly that it reads as a genre of its own. Also occasionally surfaces a genuinely wronged insight — free keeper.

### 37. The Two-Corpus Crossover Event
Your corpus meets a collaborator's, in public.

**Setup:** a collaborator with their own corpus (demo 22 built one); an agreed session.
**Run:**
1. Temporarily merge: copy their 5 best sources into your `sources/` with a `— guest` marker in the text.
2. Dig the crossover pairs live or recorded. Both parties keep independent keeper files from the session.
3. Unmerge after; publish both parties' takes on the same digs.
**The payoff:** two audiences, one event, and the comparison of the two write-ups is a third piece of content.

### 38. The Horror Dig at Midnight
Seasonal special: the corpus after dark.

**Setup:** ensure the corpus holds your horror-universe sources; run the session at night with appropriate staging; horror-voice rules loaded for the write-up.
**Run:**
1. Dig horror sources against `brand-frameworks` — the collision of dread mechanics and capacity constraints is the on-brand nightmare ("the smart house schedules your grief").
2. Write the best keeper up as a micro-fiction seed under the horror craft rules.
**The payoff:** an annual-format piece (October-ready) manufactured from the same corpus the business content comes from — one folder, two genres.

### 39. The Prediction Ledger
Dig the future, score yourself later.

**Setup:** a `predictions.md` beside `keepers.md`.
**Run:**
1. Once a month, dig with a twist: hand-pick pairs about trends, then rewrite the keeper as a falsifiable prediction with a date.
2. Log it. On the date, publicly grade the prediction.
**The payoff:** a slow-burn credibility asset — the graded ledger is proof-of-thinking no one can fake retroactively, and every grading day is a content day.

### 40. The 100-Demo Speedrun
Meta-stunt: perform the other doc.

**Setup:** `100-brilliant-demos.md` open; a camera or a live audience; a full afternoon.
**Run:**
1. Attempt as many of the 100 demos as possible in one sitting, in order, timeboxed at 3 minutes each.
2. Keep a completion tally; publish the run with timestamps.
**The payoff:** the failures are the entertainment and the honest ones prove the docs are real. Also functions as a full regression test of the tool, disguised as a stunt.

## V. Solo play & rituals

### 41. The Morning Seam
One dig with the coffee, before any inputs.

**Setup:** the daily cron (or a bookmarked curl) producing one dig before you wake.
**Run:**
1. Read the overnight dig *before* opening anything else — no feeds, no mail.
2. One decision, thirty seconds: keep, chain tonight, or discard. Then start the day.
**The payoff:** the first idea you meet each day is one of *yours*, recombined — a genuinely different mental start than meeting the timeline's idea first.

### 42. The Friday Excavation
End the week by digging what the week produced.

**Setup:** during the week, save stray thoughts as they occur (clipboard pipeline). Friday, they're waiting.
**Run:**
1. Friday afternoon: dig the week's fresh sources against the old corpus, 4–5 digs.
2. Keep the survivors; run the weekly review (first doc, demo 65) on the pile.
**The payoff:** the week gets a deliberate close — loose thoughts either graduate to keepers or are consciously released. Nothing lingers half-remembered.

### 43. The Stuck Button
A defined move for creative blockage.

**Setup:** none — this is a standing protocol. Write it on a sticky note: "Stuck → chain the problem."
**Run:**
1. When stuck on anything (a scene, a post, a decision), type the stuck-ness itself as one sentence.
2. Chain it raw (`/api/chain`, empty exclusions) against the corpus. Twice.
3. You're not looking for the answer — you're looking for a *different door into the room*. Either chain output usually is one.
**The payoff:** replaces the doomscroll-when-stuck reflex with a 90-second move that mines your own prior thinking instead of the feed.

### 44. The Anniversary Dig
Each project's birthday, dig it against everything since.

**Setup:** project start dates noted; each project has at least one source in the corpus.
**Run:**
1. On a project's anniversary, hand-pick digs: its founding source against the 3–4 most recent additions to the corpus.
2. Keep the best; append it to that project's notes as "year-N reflection, machine-assisted."
**The payoff:** an annual check on whether a project still rhymes with your current thinking — drift detected by novelty score rather than vague feeling.

### 45. The Shadow Corpus
A private second corpus for the unshareable thoughts.

**Setup:** a second folder, `sources.shadow/`, and a shell alias that swaps it in (`mv sources sources.pub && mv sources.shadow sources` — and back).
**Run:**
1. Feed it what you'd never post: fears, resentments, unspeakable ambitions. Tag honestly.
2. Dig it monthly, alone. Keep to a `keepers.shadow.md` that stays out of git (`.gitignore` it).
**The payoff:** the digs are *better* here — unfiltered sources have more voltage. Some shadow keepers eventually graduate to public work, arriving pre-tested.

### 46. The Rejection Meditation
Sit with the judge's reasons, deliberately.

**Setup:** one sub-7 dig where you *liked* the insight anyway.
**Run:**
1. Instead of overriding or discarding, write two sentences by hand: the strongest case the judge is right, then the strongest case it's wrong.
2. Only after writing both, decide: keep with a note, chain, or release.
**The payoff:** the discipline transfers — the same two-sentence move works on human rejections of your work, and you've practiced it on stakes-free material.

### 47. The Annual Century
Once a year, the full-matrix dig as a rite.

**Setup:** demo 25's century run, scheduled as a yearly event (end of year fits).
**Run:**
1. Run the full pair matrix on the year's corpus. Produce the atlas: keystone sources, dead seams, score distribution versus last year.
2. Archive the log as `century-2026.log`; prune the corpus based on findings.
**The payoff:** an annual state-of-the-brain report generated from artifacts, not memory — and the pruned corpus digs measurably better in January.

### 48. The Letter to the Corpus
Write to the folder like it's a correspondent.

**Setup:** an evening, no agenda.
**Run:**
1. Write one honest paragraph *addressed to the corpus*: what you've been avoiding thinking about. Save it as a source.
2. Dig it immediately, twice. The replies are, structurally, your own prior thinking responding.
**The payoff:** the closest the tool comes to conversation — and unlike a chatbot, every word in the reply traces to something you actually wrote once.

### 49. The Silence Test
A week without the tool, then measure the difference.

**Setup:** a normal usage baseline (keepers per week, saves per week), then one deliberate off week.
**Run:**
1. During the off week, note (on paper) every moment you *would* have saved or dug something.
2. Return, and immediately feed the paper list as sources. Dig the backlog.
**The payoff:** the paper list is the demo — it shows exactly which of your mental motions the tool had been catching. Also the backlog digs are unusually good; scarcity concentrated the ore.

### 50. The Last Dig
A standing instruction for the end of any project.

**Setup:** a project being retired or shipped; its sources still in the corpus.
**Run:**
1. Before archiving a finished project, dig its founding source one last time against the *newest* thing in the corpus.
2. Keep the result in the project's final notes regardless of score — it's the bridge to whatever's next.
**The payoff:** projects end with a forward pointer instead of a full stop. More than once, the last dig of one project is the first source of the next.

---

# PART TWO: PROFIT

## VI. Content monetization pipelines

### 51. The Keeper-to-Post Assembly Line
The core pipeline, formalized.

**Setup:** `keepers.md` populated; brand-voice flow ready; a posting schedule.
**Run:**
1. Weekly: pick the two best keepers (grep for 8/10s first).
2. Per keeper: identify the shape (hook, thread, essay), draft in brand voice, cite nothing — the provenance stays in the keeper header, the post stands alone.
3. Log which keepers became posts in the keeper's own entry (append `→ posted YYYY-MM-DD`).
**The payoff:** content ideation cost drops to near zero because ideation happened asynchronously, judged, in batch. The weekly bottleneck becomes drafting, which brand-voice already covers.

### 52. The Evergreen Vein
Mine the corpus specifically for undated content.

**Setup:** normal corpus; a tagging convention: append `[evergreen]` inside the text of timeless keepers when you keep them.
**Run:**
1. During any dig session, when a keeper is timeless (no trend, no date, no news peg), mark it.
2. `grep -B1 -A3 evergreen keepers.md` builds the evergreen queue — the content you post on weeks when nothing else is ready.
**The payoff:** a buffer of always-valid material means the posting streak never depends on that week's energy — bandwidth-honest content operations.

### 53. The Newsletter Second Life
Every issue seeds the next issues.

**Setup:** a newsletter (or any long-form channel); the file-to-source one-liner from the first doc.
**Run:**
1. After each issue ships, save the issue itself as a source.
2. Next planning session, dig the latest issue against older corpus. The insight is next issue's angle — with built-in continuity readers can feel.
**The payoff:** the publication becomes self-seeding; back-catalog compounds instead of depreciating. Long-time readers notice the through-lines and say so.

### 54. The Thread Factory
One dig, one thread, standardized.

**Setup:** a thread template: hook (the insight, sharpened), 3–4 body posts (the mechanism, unpacked), closer (the "what I'd build/do").
**Run:**
1. Dig until 7+. Fill the template — the insight's structure usually maps: claim → mechanism → implication.
2. The judge's score gates production: sub-7s never enter the factory, so the feed quality floor is the threshold itself.
**The payoff:** thread production time drops to the drafting alone, and the tool's quality bar becomes your feed's quality bar — visibly, over weeks.

### 55. The Comment-Section Mine
Replies to your posts, fed back in as ore.

**Setup:** clipboard pipeline; your posts getting replies.
**Run:**
1. When a reply contains a real objection or a sharp reframe, save it as a source (attribution note in the text).
2. Dig the objection against the framework it objected to. The insight is the follow-up post — and it engages the objection structurally, not defensively.
**The payoff:** your sharpest critics become unpaid corpus contributors, and the follow-up posts read as unusually honest because they metabolize the pushback instead of deflecting it.

### 56. The Series Bible Generator
Turn one rich seam into a numbered series.

**Setup:** a pair that has scored 7+ across multiple re-digs (demo 23 in the first doc found these).
**Run:**
1. Re-dig the rich pair five times; keep every distinct angle (expect 3–4 genuinely different ones).
2. Order the keepers into a series arc; each becomes one installment.
3. Announce it as a numbered series — numbered series outperform loose posts on completion-following.
**The payoff:** a content *series* manufactured from one seam in one afternoon — a month of installments from two sources that already existed.

### 57. The Repurposing Chain
One keeper, four formats, via forced translation.

**Setup:** one strong keeper; the chain endpoint.
**Run:**
1. Chain the keeper through `creative-projects` → a story/comic-shaped version (Botsly-ready).
2. Chain it through `content-topics` → a practical/how-to-shaped version.
3. With the original essay-shaped keeper, that's three registers of one idea; brand-voice drafts each for its native platform.
**The payoff:** "repurposing" that actually re-*derives* the idea per format instead of reformatting the same words — each version is native, not adapted.

### 58. The Paid Digest
The keeper file itself, curated, as the subscriber product.

**Setup:** a paid tier on whatever platform; a monthly ritual.
**Run:**
1. Monthly: select the 5 best keepers, write one paragraph of context each (what you're doing about it), and ship as the paid issue.
2. Free tier gets one of the five. The header format (score, provenance) ships intact — it *is* the format's identity.
**The payoff:** the product is literally `keepers.md`, curated — near-zero marginal production cost on top of digging you were doing anyway. The shovel/product line becomes the sales pitch.

### 59. The Course Spine
A course outlined by score, not by guess.

**Setup:** months of accumulated keepers around one theme (grep the pile to check density).
**Run:**
1. Pull every keeper touching the theme. Order them by dependency (which insight needs which first) — that order is the module sequence.
2. Each module: the keeper as the lesson's thesis, the source pair as the "where this comes from" story, the gate verdicts as the "why this matters."
**The payoff:** course design's hardest part (what's actually worth teaching, in what order) arrives pre-scored and pre-provenance'd. You write lessons, not outlines.

### 60. The Anthology Play
The year's keepers as a small book.

**Setup:** the annual century run (demo 47) done; a year of keepers.
**Run:**
1. Select the year's 40–50 best. Group by emergent theme (the groups will be visible — seams cluster).
2. Write connective tissue only: intros per section, one essay per theme peak.
3. Ship as a short ebook/PDF — the honest scores stay in, as marginalia. That's the book's differentiator.
**The payoff:** a real product whose raw material cost was zero incremental effort — it's the exhaust of a year of thinking, refined. The scores-in-marginalia gimmick is unfakeable and reviewers mention it.

## VII. Client & consulting plays

### 61. The Diagnostic Dig
A paid one-hour session: their ideas, your machine.

**Setup:** client sends 5–8 short idea/positioning texts ahead of the call; you save them to a fresh client corpus folder (swap trick from demo 45).
**Run:**
1. On the call: dig their corpus live. Their ideas colliding with each other — most clients have never seen their own portfolio cross-referenced.
2. Deliver: the session's keepers file, cleaned up, within 24 hours.
**The payoff:** a productized session with a tangible artifact, nearly zero prep, and a natural upsell (the seams found become the engagement).

### 62. The Positioning Collision
Their brand versus their market, as sources.

**Setup:** two source sets in the client folder: their positioning statements, and verbatim customer language (reviews, support tickets, sales-call phrases — with permission).
**Run:**
1. Tag so positioning and customer language sit in different tags (retag by hand as needed — you control the folder).
2. Dig across the divide. Every insight is a gap or a rhyme between what they say and what customers say.
**The payoff:** gap analysis that produces *sentences* instead of matrices — clients quote the insights back in their own decks, which is how you know it landed.

### 63. The Three-Gate Workshop
Build the client their own filter.

**Setup:** a half-day workshop; the gate pattern (REVEAL/BUILD/DELIVER) as the template.
**Run:**
1. Facilitate: what lie does your brand expose? What does it build? What constraint does it respect? Draft their three gates.
2. Edit `run_filter`'s prompt in a copy of `server.py` to their gates (it's one prompt string — show them the edit, it's the demo).
3. Filter their current campaign ideas through their own gates, live. Watch the arguments start — that's the workshop working.
**The payoff:** they leave with an executable brand thesis, not a slide. Recurring revenue angle: quarterly re-filtering of their roadmap against their gates.

### 64. The Ghost Corpus
Content strategy for a client, mined from their own archive.

**Setup:** client's existing material — old posts, talks, internal docs — bulk-fed via the notes-folder ingest (first doc, demo 74) into a client corpus.
**Run:**
1. Century-run their archive (small selection — 8–10 best pieces).
2. Deliver the atlas: their keystone ideas, their dead seams, and ten dug insights as a content quarter's worth of angles.
**The payoff:** the deliverable demonstrates its own method ("these ten angles came from *your* archive — you were sitting on them"), which sells the retainer better than any proposal deck.

### 65. The Merger Dig
Two teams, two corpora, one integration question.

**Setup:** two groups being combined (teams, brands, product lines); a handful of sources from each side's thinking.
**Run:**
1. Tag side A and side B into different tags. Dig only across the divide.
2. Present the 7+ insights as "what these two cultures can build that neither could alone" — and the persistent sub-7s honestly as "where the seam is thin."
**The payoff:** integration workshops usually produce platitudes; this produces scored, specific overlaps and an honest map of where there's no overlap — the honesty is what they'll remember.

### 66. The Pitch Sharpener
Pre-flight their pitch against its own weaknesses.

**Setup:** client's pitch deck text as one source; the strongest objections to it (write them yourself or collect from their lost deals) as sources in another tag.
**Run:**
1. Dig pitch × objection, pair by pair (hand-picked).
2. Each insight is a structural response to that objection — not a rebuttal line, a *reframe* that makes the objection the pitch's setup.
**The payoff:** pitch prep that produces judo instead of armor. Price it per objection metabolized.

### 67. The Retainer Heartbeat
A monthly dig report as the retainer's recurring deliverable.

**Setup:** an ongoing client corpus you feed monthly with their new material (calls, launches, posts).
**Run:**
1. Monthly: five digs of new material × their archive. Filter through *their* gates (demo 63).
2. Ship a two-page report: this month's keepers, gate verdicts, one recommended action per keeper.
**The payoff:** retainers die when the deliverable goes vague; this one is concrete, scored, and takes an hour to produce once the corpus exists. The corpus itself becomes the switching cost — it lives with you.

### 68. The Workshop Party Trick
Open any paid workshop with demo 5's oracle, professionalized.

**Setup:** workshop room; laptop; your corpus plus the client's corpus loaded.
**Run:**
1. First ten minutes: collect one sentence from each attendee ("the problem you brought today"), save each live.
2. Dig two or three against the client corpus while introducing the day's agenda.
3. Read the results back — the day's themes, discovered from the room instead of imposed on it.
**The payoff:** instant buy-in ("it used *our* words") and the day's agenda visibly grounded in the attendees' actual problems. No other opener competes.

### 69. The Second-Opinion Service
A standing offer: send one idea, get a scored collision report.

**Setup:** a simple intake (form or DM); a fixed low price; your corpus as the collision surface.
**Run:**
1. Per submission: save, dig against your two strongest framework sources (hand-picked), filter through the gates.
2. Deliver a one-pager: the insight, the score, the three gate verdicts, and three sentences of your read.
**The payoff:** a productized micro-service with 15 minutes of marginal work per unit — and a lead-qualification machine, because the buyers of the one-pager are the shortlist for bigger engagements.

### 70. The White-Label Digger
Install the tool itself for a client.

**Setup:** the repo (three files); a client with a corpus-shaped problem and someone technical enough to run `python3 server.py`.
**Run:**
1. Fork the repo for them: their gates in the filter prompt, their tag taxonomy if five different drawers fit their world better, their model budget in `config.json`.
2. Half-day handover: feed their first corpus together, run their first session, leave the docs.
3. Charge for the customization and the handover, not the code — it's three files of stdlib, the value is the fitting.
**The payoff:** the deliverable is a *practice*, not software — which is why it prices like consulting instead of like an app. Their keeper file becomes the testimonial.

## VIII. Product & business-idea generation

### 71. The Feasibility-First Pipeline
Only pursue product ideas that pass DELIVER.

**Setup:** a running list of product itches saved as sources over time.
**Run:**
1. Monthly: dig the itch list against `brand-frameworks`. Keep the 7+.
2. Filter every keeper; discard anything failing DELIVER *regardless of how good it is* — the gate encodes your real capacity.
3. What survives is buildable-by-you by construction.
**The payoff:** a product funnel whose first filter is your actual life, not the idea's abstract merit — the anti-graveyard. (The tool you're reading about survived exactly this filter.)

### 72. The Complaint-to-Spec Converter
Demo 16's corpus, run for money instead of fun.

**Setup:** the complaint corpus (yours, or harvested from public complaints in a niche you know — forums, reviews).
**Run:**
1. Dig complaints against your frameworks. The BUILD gate does the heavy lifting: it forces each grievance toward mechanism.
2. Each triple-gate pass gets one page: the complaint, the mechanism, the smallest sellable version.
**The payoff:** a spec pipeline where demand evidence (the complaint) is welded to the solution sketch from birth — backwards from how most product ideation fails.

### 73. The Micro-SaaS Seam Hunt
Dig for tools, specifically.

**Setup:** a session with an explicit lens: before digging, write "output must be a tool someone would pay monthly for" as a source in `other`, and hand-pick it into pairs as a forcing function.
**Run:**
1. Dig your frameworks × the forcing-function source, then chain results through `content-topics`.
2. Collect every insight that names a mechanism (the feasibility-compiler pattern from `DEMOS.md` Demo 1 is the archetype).
**The payoff:** a shortlist of tool ideas that are *structurally yours* — derived from your frameworks, so the marketing content already exists in the corpus that birthed them.

### 74. The Pricing Dig
Collide your offer with pricing psychology.

**Setup:** save 3–4 sources on pricing/value beliefs you actually hold (not textbook ones); your current offer described as a source.
**Run:**
1. Dig offer × pricing beliefs, hand-picked pairs.
2. The insights will be reframes of what's actually being sold — the unit of value, not the number. Re-derive the price from the best reframe.
**The payoff:** pricing changes that come with their own explanation attached — the insight *is* the announcement copy when you change the price.

### 75. The Competitor Rhyme
What your competitor's move means for you, structurally.

**Setup:** a competitor's announcement or positioning, saved verbatim as a source (public material only).
**Run:**
1. Dig it against your `brand-frameworks`. You're not looking for a counter-move — you're looking for the structural rhyme: what constraint are they responding to that you share?
2. Chain the insight through `content-topics` for the public take; keep the private strategic read in the keeper.
**The payoff:** competitor analysis that outputs *your* next move instead of a summary of theirs — plus a hot-take post as exhaust.

### 76. The Cofounder Compatibility Dig
Due diligence on a potential partnership, in one session.

**Setup:** the potential partner sends 4–5 sources of their real thinking; the blindfold-filter game (demo 26) as the second half.
**Run:**
1. Dig their sources × your corpus. Read the scores honestly: rich seams predict generative collaboration; consistent sub-7s across many pairs are data too.
2. Then have them predict your three-gate verdicts on a few insights (demo 26). High gate-prediction accuracy means they *get* the thesis.
**The payoff:** partnership diligence measuring the two things that matter — idea chemistry (dig scores) and thesis alignment (gate predictions) — before any paperwork exists.

### 77. The Offer Ladder Dig
Derive the product ladder from one core insight.

**Setup:** your single best keeper of the quarter — the thesis-grade one.
**Run:**
1. Chain it three ways with forced exclusions: through `content-topics` (→ the free version: a post/lead magnet), through `brand-frameworks` (→ the mid version: workshop/course shape), through `creative-projects` (→ the flagship: the built thing).
2. Sanity-check each rung with the filter — every rung must pass DELIVER individually.
**The payoff:** an offer ladder where every rung is a *derivation* of one idea rather than three unrelated products — the coherence is marketable and the production shares research.

### 78. The Dead Project Estate Sale
Harvest retired projects for sellable parts.

**Setup:** sources from projects you've formally ended (the Last Dig, demo 50, left them in the corpus).
**Run:**
1. Quarterly: dig dead-project sources against the *live* corpus only.
2. Any 7+ means a dead project contains a live part — extract it: as content, as a feature of a current project, or as a small standalone.
**The payoff:** sunk costs partially recovered on a schedule. The emotional reframe matters as much as the output: ended projects become inventory, not failures.

### 79. The Market-Timing Journal
Dig the same strategic pair quarterly; the *change* is the signal.

**Setup:** one fixed pair — your core offer source × a "state of the market" source you rewrite fresh each quarter.
**Run:**
1. Quarterly: update the market source, dig the fixed pair, log the keeper with the date.
2. Read the keepers as a sequence. The drift between quarters is your timing signal — when the insights start pointing somewhere new, the market moved.
**The payoff:** a strategy instrument with memory — most timing intuitions can't be audited later; this one leaves a dated paper trail.

### 80. The Idea Escrow
Pressure-test before you announce, on the record.

**Setup:** the idea-pressure-tester flow for the scored critique; the digger for the collision test; a dated file.
**Run:**
1. Before announcing any new venture: save it, dig it against your three strongest sources, filter it, and run the pressure test.
2. Write the verdicts into `escrow.md` with the date — *then* decide about announcing.
3. Revisit the entry at the 90-day mark: was the machine right?
**The payoff:** an announcement discipline that kills weak launches privately, cheaply, and before the audience sees them — plus a growing private dataset on your own judgment versus the gates'.

## IX. Audience & brand growth

### 81. The Method Reveal
Grow by showing the machine, not just its outputs.

**Setup:** weeks of keeper-derived content already posted (demo 51's assembly line running).
**Run:**
1. Post the reveal: the tool, the three files, the honest scores, the shovel line. Screenshot `sources/` and `keepers.md` — the real ones.
2. Link the repo docs or describe the pattern openly. The method *is* the brand (constraint-driven, bandwidth-honest); the tool is its proof.
**The payoff:** "here's the machine behind the posts you liked" converts content followers into method followers — stickier, and pre-qualified for every Part Two offer above.

### 82. The Public Corpus Experiment
Let the audience vote on what gets fed.

**Setup:** an audience; a weekly poll slot.
**Run:**
1. Weekly poll: two candidate sources (one-line summaries) — which enters the corpus?
2. Feed the winner, dig it on arrival, post the result with its score. The audience watches their choice succeed or flop honestly.
**The payoff:** participation converts spectators into stakeholders — they check back for *their* source's dig. Retention mechanics without gamification cruft.

### 83. The Scored Takes Format
Attach the judge's number to your public opinions.

**Setup:** your take-writing habit; the digger as pre-flight.
**Run:**
1. Before posting a take, run it through a dig against your frameworks (raw chain seed works). Post only 7+ material — and *say the score in the post* ("this cleared a 8/10 novelty bar against my own back-catalog").
2. Occasionally post a 5/10 flagged as such, for calibration credibility.
**The payoff:** a feed with a visible, consistent quality mechanism becomes legible in a way "good posting" never is — the score line gets quoted and asked about, which is demo 81's on-ramp.

### 84. The Collab Bait
Public crossover digs as partnership outreach.

**Setup:** demo 37's crossover mechanics; a shortlist of creators whose public ideas you respect.
**Run:**
1. With permission (ask first — it's also the outreach message), save 2–3 of a creator's public ideas and dig them against your corpus.
2. Send them the keepers privately: "your ideas × my frameworks produced these."
3. If it lands, the public version (demo 37) is the collaboration's announcement.
**The payoff:** outreach that *demonstrates* the value of collaborating instead of asserting it — response rates reflect that difference.

### 85. The Bandwidth Snapshot Tie-In
Cross-promote the flagship with dug insights.

**Setup:** the bandwidth-snapshot practice running; the digger's corpus sharing its thesis.
**Run:**
1. When a day's snapshot surfaces a pattern (a recurring capacity lie, a planning failure), save the pattern as a source.
2. Dig it against `brand-frameworks`; the keeper becomes the snapshot write-up's closing insight — each artifact feeding the other.
**The payoff:** the two flagship practices visibly reinforcing each other reads as a *system*, and the system is the brand. Cross-references between formats measurably lift both.

### 86. The Objection FAQ
Build the FAQ page from dug objections, not imagined ones.

**Setup:** demo 55's comment-section mine accumulating real objections as sources.
**Run:**
1. Quarterly: dig the objection collection against the frameworks; each insight is an FAQ answer that reframes rather than defends.
2. Ship the FAQ page; update it from new objections each quarter.
**The payoff:** an FAQ that answers what people *actually* push back on, in language that metabolizes the pushback — doubles as the sales page's objection-handling section.

### 87. The Speaking Reel Seed
Every talk proposal starts as a keeper.

**Setup:** accumulated keepers; events/podcasts you'd want.
**Run:**
1. For each target event, pick the keeper that best rhymes with their audience, and build the pitch as: the insight (hook), the source pair (the origin story — audiences love provenance), the gates (the takeaway structure).
2. The talk itself: perform the dig live as the centerpiece (first doc, demo 98's mechanics).
**The payoff:** talk proposals with a built-in live demo and a built-in structure — and every delivered talk feeds the corpus (audience questions → sources).

### 88. The Niche Atlas
Public cartography of a niche, dug rather than opined.

**Setup:** 8–10 canonical public positions/ideas in a niche you want authority in, saved as sources (attributed in the text).
**Run:**
1. Century-run the niche corpus. Publish the atlas: which ideas rhyme, which contradict structurally, where the unexplored seams are (the persistent sub-7 pairs, honestly labeled).
2. Position your own work in the map's empty seam.
**The payoff:** the atlas format earns links and citations (people share maps that include them), and the empty-seam positioning is derived in public — hard to accuse of arrogance when the method is showing.

### 89. The Testimonial Dig
Mine your own testimonials for the marketing you can't write.

**Setup:** real testimonials/thank-you messages saved as sources (with permission for any public use).
**Run:**
1. Dig testimonials against your positioning sources. The insights surface what clients *actually* bought versus what you thought you sold.
2. Rewrite the sales page's headline from the strongest keeper.
**The payoff:** positioning language sourced from the buyers' own words, structurally recombined — converts better than founder-written claims for the boring reason that it's demand-side language.

### 90. The Anti-Guru Positioning
The honest scores as the entire differentiation strategy.

**Setup:** a niche full of certainty-sellers; your feed running demos 21/83 (honest scores visible).
**Run:**
1. Lean in explicitly: post the score distributions, the sub-7 galleries (demo 36), the graded prediction ledger (demo 39).
2. The positioning sentence writes itself: "I show the misses." Say it rarely; demonstrate it constantly.
**The payoff:** in a certainty-saturated niche, verifiable fallibility is the scarce good. It filters the audience toward exactly the people who buy diagnostics and workshops over dreams — Part Two's actual customers.

## X. Selling the pattern itself

### 91. The Pattern Essay
The definitive write-up of dig-judge-gate as a thinking pattern.

**Setup:** everything this file assumes; an essay slot.
**Run:**
1. Write the pattern up tool-agnostically: collide distant material, judge novelty with a threshold and honest failures, filter through a personal thesis. Your tool is the worked example, not the subject.
2. Publish where essays travel. The tool docs are the appendix link.
**The payoff:** the pattern essay is the top of the entire funnel — people who adopt the pattern *with any tool* become the audience for everything below (workshops, installs, the digest).

### 92. The Template Kit
The gates + tags + keeper format as a sold template.

**Setup:** the three reusable artifacts: a gate-drafting worksheet (from demo 63), the tag-taxonomy rationale (five drawers, forced distance), the keeper header format.
**Run:**
1. Package as a paid template kit for people who want the practice without running the server — doable with any chat model by hand, and say so honestly.
2. The kit's upsell path: the white-label install (demo 70) for those who want it automated.
**The payoff:** a product for the audience segment that will never run `python3 server.py` — which is most of them. Honesty about "you can do this manually" is the trust that sells the automation later.

### 93. The Cohort Practicum
Four weeks, everyone builds and runs their own corpus.

**Setup:** demos 61–63's client material generalized into a curriculum; a small cohort.
**Run:**
1. Week 1: corpus feeding (everyone brings their archive). Week 2: digging + reading scores. Week 3: drafting their own gates. Week 4: their first keeper-to-content pipeline.
2. Graduation artifact: each participant's `keepers.md` with 5+ entries and their gates written.
**The payoff:** cohort-priced revenue on material this file already contains — and every graduate runs the pattern publicly, which is demo 91's essay walking around in the world.

### 94. The Licensing Angle
Your gates, licensed as a review standard.

**Setup:** a team/org that reviews ideas at volume (an agency's pitch review, a studio's development slate); demo 63 delivered to them once.
**Run:**
1. Formalize their gates + a review cadence + the honest-score discipline into a named internal standard ("the [Client] Gate Review").
2. License it: annual fee for the standard, its updates, and a quarterly calibration session (demo 20's adversarial corpus, run on their reviewers).
**The payoff:** recurring revenue attached to a *practice* rather than deliverables — renewal case is the calibration data itself showing reviewer drift caught and corrected.

### 95. The Case Study Engine
Every client engagement auto-produces its own marketing.

**Setup:** client work from section VII happening; permission clauses in your agreements for anonymized method write-ups.
**Run:**
1. Per engagement, the artifacts already exist: the before-corpus, the keepers, the gate verdicts, the shipped outcome. The case study is assembly, not writing.
2. Standard format: the seam found (anonymized), the score history, what shipped, one client sentence.
**The payoff:** a case study per engagement at near-zero marginal cost, because the method generates its own paper trail — the documentation habit *is* the marketing department.

### 96. The Conference Workshop
The three-gate workshop (demo 63), productized for rooms of strangers.

**Setup:** demo 63's facilitation, adapted: strangers draft *personal* gates instead of brand gates; the oracle opener (demo 68) warms the room.
**Run:**
1. 90-minute format: opener digs (15) → the pattern explained via one live dig (15) → gate drafting in pairs (30) → filtering their real current projects through their new gates (30).
2. Everyone leaves with three gates and one filtered project decision.
**The payoff:** a repeatable paid workshop with almost no per-run prep, whose attendee artifact (their gates) keeps your framing in their heads for months. Back-of-room: the template kit (demo 92).

### 97. The API-for-Hire
Run digs as a service for people with corpora and no time.

**Setup:** the headless recipes; a simple intake for corpus material; clear per-batch pricing tied to model costs (each dig is 2–4 calls — price transparently above cost).
**Run:**
1. Client sends material; you feed, century-run, and deliver the atlas + top keepers within a week.
2. Productize three sizes: Prospect (10 digs), Survey (full matrix, small corpus), Deep Vein (matrix + chains + gates).
**The payoff:** service revenue on pure operation of the machine — the deliverable format (atlas + keepers) is already defined by demos 25 and 64, so fulfillment is execution, not invention.

### 98. The Acquisition Story
The tool as proof-of-competence in any bigger deal.

**Setup:** any context where you're being evaluated — a big client, a partnership, an acqui-conversation, a job you actually want.
**Run:**
1. Demo the tool live (first doc, demo 1) as the answer to "how do you think?" — three stdlib files, honest scores, a filter that encodes a thesis, docs that let a stranger run it cold.
2. Leave behind `keepers.md` excerpts and the docs folder. The artifact *is* the resume.
**The payoff:** most people claim judgment; this demonstrates judgment plus restraint plus follow-through in one running system. It reframes any evaluation from "believe me" to "watch it work."

### 99. The Franchise Test
Can someone else run your entire practice from the docs alone?

**Setup:** a willing test subject (a peer, a VA, a collaborator); the full docs folder; explicit instructions to *not* ask you questions.
**Run:**
1. They must: run the server, feed a corpus, execute a dig session, apply the gates, and produce one keeper-to-content draft — using only what's written.
2. Log every point where they got stuck. Fix the docs at each point.
**The payoff:** each stuck-point fixed makes demos 70, 93, and 97 more sellable — this demo is quality assurance for every other demo in this section. When someone passes cleanly, you have proof the practice transfers, which is the claim all of Part Two rests on.

### 100. The Exit Interview
If you stopped tomorrow, what would remain sellable?

**Setup:** an honest hour with the repo and this file.
**Run:**
1. Inventory what exists without your ongoing labor: the keepers (anthology, demo 60), the pattern (essay + kit, 91–92), the practice (cohort curriculum, 93), the standard (license, 94), the tool (three files anyone can run).
2. For each, write one line: who buys it, without me in the room?
3. The lines that have no answer are the ones where you're the product — decide deliberately whether that's fine.
**The payoff:** a clear map of asset versus labor across everything this file proposes — the difference between building a practice and building a treadmill, checked annually.

---

# THE FINALE

### 101. The Full-Circle Session
Fun and profit in one sitting — every layer of the stack, live.

**Setup:** one evening; friends who'll play; the content pipeline warm for the morning after. Cheap model for the games, strong model for the money digs (`config.json` swap mid-session — it re-reads per call).
**Run:**
1. **Fun:** open with Insight Poker (demo 1), three hands. Every insight generated during the game — winners and losers — quietly accumulates in the session log.
2. **Feed:** each guest gifts the corpus one source on their way to the snacks (demo 6's mechanic).
3. **Dig for real:** after the games, swap to the strong model. Dig the evening's new sources against the old corpus. Keep the survivors — tonight's party is now in the keep pile with scores attached.
4. **Profit:** next morning, the assembly line (demo 51): best keeper → brand-voice draft → posted, with the provenance line intact ("dug from a source a friend gave me at poker night").
5. **Close the loop:** the post's best reply gets saved as a source (demo 55). The next session starts richer than this one did.
**The payoff:** the whole thesis in twelve hours — the same three files hosting a party, feeding a corpus, judging ideas honestly, and shipping revenue-bearing content, with each stage's exhaust becoming the next stage's fuel. The fun *is* the mining. The mining *is* the marketing. The file is still the product, and the app is still just the shovel.

---

*Companion files: `100-brilliant-demos.md` teaches the tool; `DEMOS.md` holds the
real transcripts and canonical curl recipes. Everything above runs against the live
tool — the outputs, the scores, and the money will be yours, not these pages'.*

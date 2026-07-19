# You don't have an idea problem. You have a collision problem.

Somewhere in your files is a framework you wrote in March.
Somewhere else, a story premise from last year.
They've never met.

Every idea system tells you to capture more. More notes, more highlights, more
inboxes. Capture was never the bottleneck. You already made the good material.
It's sitting in folders that don't talk to each other.

Idea Digger is a shovel for that.

## What it does

You paste in things you've already made, one at a time. Frameworks. Project
premises. Essay drafts. Content angles. Each becomes a plain text file with a tag.

Then you hit Dig.

The tool grabs two sources from different categories — a comedy project and a
systems framework, say — and demands a connection with a hard rule attached: it
must produce something usable. An essay angle. A framework. A product idea. A
story premise.

Then a judge scores the result for novelty. Below 7 out of 10, the judge explains
why it's obvious and forces a rewrite. Three strikes and it shows you the failure,
honest score attached.

That last part matters. Most AI tools flatter you. This one is built to refuse the
obvious answer — including its own.

Real output from a real session: it crossed a workplace comedy about a robot CEO
with a framework about capacity limits and came back with *your commitments are a
type error* — promises treated as rules when they're actually resource claims.
Scored 8/10. Essay angle and product sketch in one paragraph.

The same session scored another pair 5/10 three rewrites in a row, and said so.
Both results are the tool working.

## What it costs you

Ten minutes a session. A few cents of API calls.

Not a subscription. Not a platform. Not another inbox to feel behind on.

Three files and a folder of plain text, on your own machine. If the tool died
tomorrow, your sources and your keep file would still be there — readable, greppable,
yours. Most tools hold your thinking hostage. This one couldn't if it tried.

## What it won't do

It won't make you creative. It's a shovel, not a muse.

Maybe one dig in three is worth keeping. That's the honest hit rate — good odds
across a session, lottery odds for a single pull.

And it won't do the last step for you. Once a week, you open `keepers.md` and turn
one entry into something real. That file is the product. The app is just how it
gets filled.

## Why it's built this way

Constraint-driven design: build for the bandwidth you actually have, not the
bandwidth the plan wishes you had.

You were never going to re-read everything you've made and hold it in your head at
once. That's the lie of unlimited capacity, pointed at your own archive. So the
system does the one thing you can't — collide everything with everything — and
leaves you the one thing only you can do: recognize which collision matters.

## Start

Fifteen sources. One week. Ten minutes a session.

```sh
export OPENROUTER_API_KEY=sk-or-...
python3 server.py        # → http://localhost:8420
```

If `keepers.md` is empty after a week, delete the folder. You've lost nothing.

If it isn't, you already know.

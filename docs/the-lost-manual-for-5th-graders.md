# The Lost Manual (for 5th Graders)

This explains the whole Idea Digger program in plain words. No computer class needed.
If you can read this, you can understand every part of it.

Other docs in this folder are written for grown-up programmers. This one is not.
It says the same true things, just slower.

---

## 1. The big idea, in one picture

Imagine you have a shoebox full of notes you wrote.

One note says: *"People pretend they have unlimited time. That's a lie."*
Another note says: *"A comic strip about two grumpy goats."*

Those two notes have nothing to do with each other. You wrote them months apart.
You would never sit down and think about both at the same time.

**Idea Digger reaches into the shoebox, pulls out two notes that don't match, and
asks a robot: "What do these two secretly have in common?"**

Sometimes the answer is boring. But sometimes the answer is a brand-new idea that
you could never have thought of by staring at either note alone.

That's it. That's the whole program.

> **Why "digging"?** Because your best ideas are already buried in stuff you wrote
> and forgot. The program isn't inventing them. It's digging them up.

---

## 2. Why anyone would build this

You already have good ideas. The problem is they're *scattered*.

You had a thought in a chat window in 2024. You started a project in 2026. Those two
things have never met. They're in different rooms of your house and neither one knows
the other exists.

Most tools help you **make more stuff**. This tool helps you **connect stuff you
already made**. That's a different job, and almost nothing does it.

---

## 3. The parts (like naming the parts of a bike)

The program is only a few files. You could print them out.

| The file | What it does | Think of it as |
| --- | --- | --- |
| `server.py` | The brain. Does all the thinking and talking to the robot. | The engine |
| `index.html` | The screen you look at. Buttons, text boxes. | The dashboard |
| `config.json` | One line saying *which* robot to use. | The dial |
| `sources/` | A folder holding all your notes, one note per file. | The shoebox |
| `keepers.md` | The ideas you liked enough to save. | The trophy shelf |
| `import.py` | A separate tool that dumps thousands of old chats into the shoebox. | The dump truck |

**There is no database.** That word means "a special locked filing cabinet that
only programs can open." This project refuses to use one. Every note is a plain
text file you could open, read, and fix with any normal text editor.

That's on purpose. If the program broke forever tomorrow, your shoebox would still
be a folder of readable notes. Nothing would be trapped.

---

## 4. Turning it on

You type two things:

```sh
export OPENROUTER_API_KEY=sk-or-...
python3 server.py
```

Then you open `http://localhost:8420` in a web browser.

Two words worth knowing:

- **`localhost`** means *this computer, right here*. Not the internet. Nobody else
  can see it. It's your own private website that only exists while the program is
  running.
- **`8420`** is just a door number. A computer has thousands of numbered doors so
  different programs don't bump into each other. This program uses door 8420.

**The API key** is a password that lets the program talk to the robot. The robot
lives on someone else's computer far away. The key proves you're allowed to ask it
questions. Never show it to anyone — it's attached to a credit card.

---

## 5. The five buttons

### SAVE — put a note in the shoebox

You paste in some text. Any text. A half-finished thought, a project idea, a
paragraph you liked.

The program asks the robot two questions about it:

1. **"Which pile does this go in?"** The robot picks one of five labels (called
   **tags**). More on those in section 7.
2. **"Give this a short name."** About five words, so you can tell notes apart.

Then it saves the note as a file in the `sources/` folder.

If the robot files it wrong, there's a dropdown menu to fix the tag yourself. The
robot is often right and sometimes dumb. You're the boss.

### DIG — the main event

This is the button the whole program exists for.

1. It picks **two notes from two different piles**. (Never two from the same pile —
   that's the point. It wants things that don't normally touch.)
2. It sends both to the robot and says: *find a non-obvious connection between
   these, and make it something I could actually use — an essay idea, a way of
   thinking about something, a product, or a story.*
3. Then comes the interesting part. See section 6.

### KEEP — save the good ones

Adds the idea to `keepers.md` with today's date, its score, and which two notes made
it. Without this button, a good idea disappears the moment you reload the page.

### CHAIN — go one step further

Takes the idea you just got and digs it against a **third** note, from a pile neither
of the first two came from. It's like asking "okay, but what does *this* have to say
about it?"

### FILTER — the three-question test

Runs an idea through three yes-or-no questions. Each gets a pass or fail plus one
line explaining why:

- **REVEAL** — does it expose the lie of unlimited capacity?
- **BUILD** — does it create proof, practice, or capacity?
- **DELIVER** — does it respect the bandwidth?

These aren't generic. They're the specific things this person's work is *about*.
An idea can be clever and still fail all three, which means: interesting, not mine.

---

## 6. The "try harder" rule (the best part)

Here's a thing about robots: **the first answer is almost always the obvious one.**

Ask any AI to connect two things and it will cheerfully say something like "both are
about creativity!" That's true and useless. It sounds like an answer while being
nothing.

So the program doesn't accept the first answer. It runs a loop:

```
Robot gives an idea
        ↓
Second robot scores it 1 to 10 for "how surprising is this?"
        ↓
   Is it 7 or higher?
        ↓                    ↓
      YES                    NO
        ↓                    ↓
    Show it       "Explain why that was obvious,
                   then give me a better one."
                            ↓
                   (try again, up to 3 times total)
```

You never see the boring first tries. You only see what survived.

**Three rounds, then it stops** — even if the score is still low. That's deliberate.
A program that retried forever would burn money and hang. Sometimes two notes just
don't have anything interesting between them, and the honest thing is to show a
low score and move on.

> **A small honest detail:** if the robot replies in a format the program can't
> read, the score shows as blank instead of being made up. A fake number would be
> worse than no number.

---

## 7. Tags, and why "different piles" matters so much

Every note gets exactly one tag out of five:

| Tag | Meaning | How many notes have it right now |
| --- | --- | --- |
| `creative-projects` | Stories, comics, shows, things being made | 467 |
| `content-topics` | Things worth writing or posting about | 262 |
| `essays` | Longer arguments and thinking | 100 |
| `brand-frameworks` | Ways of explaining the work | 81 |
| `other` | Didn't fit anywhere | 11 |

Tags aren't for tidiness. **Tags are the rule that makes digging work.** The program
takes two *different* tags, then one note from each. That guarantee — that the two
notes come from different worlds — is what makes the connection surprising instead
of obvious.

Two notes from the same pile would already be related. Where's the fun in that?

> **A real wrinkle worth knowing.** The program picks a *pile* first, then a note
> from inside it. So a pile holding 11 notes gets chosen just as often as a pile
> holding 467. That means each of those 11 lonely `other` notes shows up *way* more
> often than any single `creative-projects` note. It's a known quirk, written down
> in the project's plans, not yet fixed.

---

## 8. What a note actually looks like inside

Open any file in `sources/` and you'll see this:

```
tag: creative-projects
label: Newsletter signup strategy ideas
source: claude
date: 2025-11-22
conv: cf95d03e-9128-41bd-bf52-88484be38b72
title: Room 5 pivot project documentation
---
The safe intro offering to get people to sign up for the newsletter would be
offering the aliases, potentially using a startday/good evening loop as a hook.
```

The top part is the **header** — facts *about* the note. Then `---` on its own line,
like a fence. Then the actual note.

Each header line means:

- **`tag`** — which pile
- **`label`** — the short name
- **`source`** — where it came from (`chatgpt`, `claude`, or nothing if typed by hand)
- **`date`** — when the original conversation happened. This one matters a lot: it's
  how a thought from 2024 can be paired with a project from 2026 and you can *see*
  that's what happened.
- **`conv`** — the ID number of the original conversation, so the same one never gets
  imported twice
- **`title`** — what the original chat was called

The program only actually reads `tag` and `label`. The other lines are for **you**,
so you can tell where something came from. Extra lines are ignored, which is why
adding them was cheap.

---

## 9. The dump truck (`import.py`)

Everything above describes notes typed in one at a time. But the real reason this
project exists is bigger.

This person had **years** of conversations with AI chat programs sitting in
downloaded files. Thousands of them. Full of ideas nobody would ever read again.

So a separate program was written to dig those out.

### The size of the problem

| | |
| --- | --- |
| Conversations in the pile | **3,438** |
| Of those, ones with actual text | 3,390 |
| Total words the robot would have to read | roughly 14.8 million tokens |

A "token" is about three-quarters of a word. So: a lot. Reading all of it costs
real money.

### The trick that made it affordable

Most of a chat is **the robot talking**. But the robot's words aren't *your* ideas —
they're just replies.

So the importer throws away everything the AI said and keeps **only the human's
side**. That's about one-sixth of the pile. Five-sixths of the cost, gone, without
losing a single idea.

### The bouncer

Here's the hard part: most conversations aren't ideas at all. They're "why is my
code broken," "what's a recipe for chicken," "fix this typo." Dumping all 3,390 into
the shoebox would poison it. Garbage in, garbage out.

So every conversation gets checked by a cheap fast robot acting as a bouncer at a
door. It asks one question: **did this person actually say something they think, or
were they just asking for a chore to be done?**

- A belief, an argument, a made-up premise, a plan for something to build → **KEEP**
- Debugging, lookups, "write this for me," small talk → **DROP**

Two traps the bouncer was specifically taught to watch for:

1. **A long, hard, useful conversation can still be a DROP.** Effort isn't insight.
   Three hours of debugging is work, not an idea.
2. **A fancy-sounding request is not an idea.** "Make a style guide for hygge as a
   brand" *sounds* creative, but the person is ordering a product, not saying what
   they believe.

### What actually happened when it ran

| | |
| --- | --- |
| Conversations checked | 3,390 |
| **Kept** | **916** |
| Dropped | 2,474 |

The shoebox went from **5 notes to 921**.

Every decision is written down in `import-seen.log`. So if the run gets interrupted,
starting it again picks up where it stopped instead of redoing everything — and it
never imports the same conversation twice.

---

## 10. The rules this project lives by

Most software collects parts the way a coat collects lint. This one refuses:

1. **No database.** Plain text files only.
2. **No downloaded add-ons.** Only what Python comes with in the box.
3. **No build step.** No "compiling." The files you read are the files that run.
4. **Fewest files possible.** The whole website is one HTML file. The whole brain is
   one Python file.
5. **Boring beats clever.** Clever code is code that somebody has to decode at 3am.

These aren't laziness. They're a bet: **the tool should be simpler than the ideas
it's helping you find.** If you have to maintain the tool, you stop using it.

---

## 11. Words grown-ups use, translated

| Word | What it actually means |
| --- | --- |
| **API key** | A password that proves you're allowed to ask the robot questions |
| **Token** | About ¾ of a word. Robots are priced by the token |
| **Prompt** | The instructions you give the robot |
| **Stdlib** | The tools Python already comes with, no downloading |
| **Port** (8420) | A numbered door on your computer |
| **localhost** | This computer. Not the internet |
| **JSON** | A way of writing data with lots of `{` and `"` in it |
| **Parse** | To read something messy and pull out the parts you want |
| **Corpus** | A big pile of text. Here: everything in `sources/` |
| **Novelty** | How surprising something is. The thing being scored 1–10 |
| **Header** | The facts at the top of a file, above the `---` |

---

## 12. If something goes wrong

**"Need saved sources in at least 2 different tags"** — everything is in one pile.
The digger needs two different ones. Save something different.

**The insights are boring** — check `config.json`. A cheap robot gives cheap answers.
Digging deserves the good one.

**A score is blank** — the robot replied in a format the program couldn't read. Not
a crash. It's being honest instead of inventing a number.

**Nothing loads at localhost:8420** — the program isn't running, or it's using a
different door. Look at what it printed when it started.

---

## 13. The one-sentence version

*Keep everything you think in a shoebox, then have a robot repeatedly smash two
random pieces together until something surprising falls out — and refuse to accept
the first answer, because the first answer is always the obvious one.*

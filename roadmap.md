# Idea Digger — Roadmap

A local tool that finds non-obvious, usable connections across everything Ryan makes:
brand frameworks, creative projects, content topics, essays. Plain files, one server,
no database. Each phase ships something usable on its own and has a "done when" test.

---

## Phase 0 — Core loop ✅ (shipped)

- Paste → AI tags (one of 5 tags) + 5-word label → saved as plain text in `/sources`
- Tag correction dropdown
- Dig: pick two sources from different tags → non-obvious connection → novelty
  scoring loop (rewrite until 7+, max 3 rounds) → show insight + score + source pair
- OpenRouter, model swappable in `config.json` (no restart) or `M` env var

**Done when:** a dig produces a scored insight from real sources. ✅ Verified 2026-07-18.

---

## Phase 1 — The promised extras ✅ (shipped)

The three features specced but deferred until the core loop proved out.

1. **Keep pile** — a Keep button on the insight card. Appends to `keepers.md` with
   date, score, and the two source labels. This comes first: without it, good
   insights evaporate on refresh.
2. **Chain mode** — a Chain button on a kept/current insight: dig it against a third
   source from a tag not already in the pair.
3. **Filter mode** — run any insight through the three gates, pass/fail each with one
   line of reasoning:
   - REVEAL: does it expose the lie of unlimited capacity?
   - BUILD: does it create proof, practice, or capacity?
   - DELIVER: does it respect the bandwidth?

**Done when:** dig → keep → chain → filter works as one flow and `keepers.md` reads
like a usable idea log. ✅ Verified live 2026-07-19.

---

## Phase 2 — Feed the machine (the original mission)

The tool is only as good as its corpus. Three sources of trapped ideas exist:
ChatGPT, Claude, and Gemini chat-history exports.

1. **Bulk import script** (`import.py`, run from CLI — not part of the web app):
   - Parse each export format (OpenAI `conversations.json`, Claude
     `conversations.json`, Gemini Takeout)
   - Extract idea-bearing chunks — skip small talk, code debugging, dead threads
   - Auto-tag + label each chunk through the existing classify step
   - Write straight into `/sources` with a `source: chatgpt|claude|gemini` line
     so provenance survives
2. **Junk control:** a cheap-model pre-filter scores each chunk "is there an idea
   here worth digging against?" before it earns a file. Bad corpus = bad digs.
3. **Review pass:** imports land as normal sources, so the existing tag dropdown is
   the correction tool. No new UI.

**Done when:** the real exports are ingested and a dig can pair a 2024 ChatGPT idea
with a 2026 creative project.

---

## Phase 3 — Smarter digging

Only matters once the corpus is big (post Phase 2).

1. **No repeat pairs** — log dug pairs to `dug.log`; picker skips already-dug combos
   until all are exhausted.
2. **Dig against this** — pick one specific source, let the tool find its partner.
3. **Cost tiering** — cheap model for tagging/import-filtering, strong model for
   digging and scoring. Two model fields in `config.json`.

**Done when:** 50 digs in a row produce no repeated pair and tagging costs pennies.

---

## Phase 4 — Output pipeline (pull, don't push)

Insights are only useful if they leave the tool.

1. **Weekly digest** — script that reads `keepers.md`, groups by theme, outputs one
   markdown brief: "what you keep circling, what's ready to make."
2. **Brand-voice handoff** — a kept insight can be sent to the existing brand-voice
   workflow as a seed for X/LinkedIn drafts (manual copy at first; automate only if
   the manual step actually gets used).

**Done when:** one kept insight has become one published piece of content.

---

## Deliberately not doing

- No database, no accounts, no deploy — this is a single-user local tool
- No embeddings/vector search until random pairing demonstrably runs dry
- No automation of Phase 4 until the manual version proves the habit exists

## Working order

Phase 1 → Phase 2 → use it for a couple of weeks → let real usage decide whether
Phase 3 or Phase 4 matters more.

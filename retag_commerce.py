#!/usr/bin/env python3
"""Move existing sources into the `commerce` tag. CLI, one-off, not part of the web app.

    M=anthropic/claude-haiku-4.5 OPENROUTER_API_KEY=... python3 retag_commerce.py --dry-run
    M=anthropic/claude-haiku-4.5 OPENROUTER_API_KEY=... python3 retag_commerce.py

`commerce` was specced in issue #6 and never implemented; the corpus was classified
without it. This asks one yes/no question per source and rewrites the `tag:` header of
the yeses. It only ever moves files INTO commerce — a `no` leaves the file untouched,
so an existing good tag can never be churned by this pass.

Resumable and reversible: every verdict is appended to retag-commerce.log and skipped
on re-run, and `--undo` puts every moved file back using the old tag recorded there.
"""
import argparse
import os
import sys
import threading
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import server  # noqa: E402  — reuse ai() and the OpenRouter plumbing

ROOT = Path(__file__).parent
LOG = ROOT / "retag-commerce.log"

# Definitions come from issue #6's sample: Etsy shops, print-on-demand, the Two Old
# Goats logo, pickleball MS shirts. The risk is the model reading any mention of
# money as commerce, so the prompt draws that line explicitly.
PROMPT = """Does this idea belong in a vault category called `commerce`?

`commerce` means PHYSICAL GOODS YOU SELL: running a shop or storefront,
print-on-demand, merch, apparel, prints, ceramics, Etsy/Shopify listings, a product
brand or line, pricing or positioning a physical thing you make.

It does NOT mean: business strategy in the abstract, marketing theory, career or
freelance advice, productivity, or any idea that merely mentions money, clients,
or customers in passing. The test is whether there is a PRODUCT BEING SOLD at the
centre of the idea.

CRITICAL — fiction is never commerce. If the idea is a story, comedy, sitcom,
sketch, character, joke, or premise, answer NO no matter how much buying, selling,
shopping, or business it contains. A comedy about running an Etsy shop is a STORY,
not commerce. A realtor selling a haunted house is a STORY. A ghost cursing a
garage sale is a STORY. The selling is the plot, not the point.

CRITICAL — software is never commerce. An app, tool, script, dashboard, website,
game, or AI agent is a CREATIVE PROJECT, not commerce, even when it is a product
someone could charge for, and even when it helps run a shop. A dashboard tracking
card prices is software. A tool that automates Etsy listings is software. A card
game is a game. Answer NO for all of them.

Answer YES only when there is a PHYSICAL THING being sold to real customers.

Answer with exactly one word, YES or NO.

CURRENT CATEGORY: {tag}
IDEA:
{text}"""


def ask(src):
    """-> True if this source belongs in commerce. Raises on API failure so the
    caller leaves it unlogged and a re-run retries it."""
    out = server.ai(PROMPT.format(tag=src["tag"], text=src["text"][:2000]))
    return out.strip().upper().startswith("YES")


def set_tag(name, tag):
    """Rewrite only the `tag:` header line, leaving every other byte alone."""
    path = server.SOURCES / name
    head, sep, body = path.read_text().partition("\n---\n")
    lines = [f"tag: {tag}" if ln.startswith("tag: ") else ln
             for ln in head.splitlines()]
    path.write_text("\n".join(lines) + sep + body)


def load_seen():
    if not LOG.exists():
        return set()
    return {ln.split()[0] for ln in LOG.read_text().splitlines() if ln.strip()}


def undo():
    if not LOG.exists():
        raise SystemExit(f"{LOG.name} not found — nothing to undo.")
    moved = [ln.split() for ln in LOG.read_text().splitlines() if " YES " in ln]
    for name, _verdict, old_tag in moved:
        set_tag(name, old_tag)
    print(f"put {len(moved)} files back")


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--dry-run", action="store_true",
                    help="ask, print, and log — but do not rewrite any file")
    ap.add_argument("--limit", type=int, help="stop after N unseen sources")
    ap.add_argument("--workers", type=int, default=8)
    ap.add_argument("--undo", action="store_true",
                    help="restore every file this pass moved, using the log")
    args = ap.parse_args()

    if args.undo:
        return undo()
    if "commerce" not in server.TAGS:
        raise SystemExit("`commerce` is not in server.TAGS — add it first.")

    seen = load_seen()
    todo = [f.name for f in sorted(server.SOURCES.glob("*.txt")) if f.name not in seen]
    if args.limit:
        todo = todo[:args.limit]
    print(f"model={server.model_name()}  todo={len(todo)}  already seen={len(seen)}"
          + ("  (dry run)" if args.dry_run else ""))

    log_fp = LOG.open("a")
    lock = threading.Lock()
    counts = {"YES": 0, "NO": 0, "ERR": 0}

    def handle(name):
        src = server.load_source(name)
        if src["tag"] == "commerce":
            return
        try:
            yes = ask(src)
        except Exception as e:  # unlogged on purpose — a re-run retries it
            with lock:
                counts["ERR"] += 1
                print(f"  ERR {name}: {e}", file=sys.stderr)
            return
        if yes and not args.dry_run:
            set_tag(name, "commerce")
        with lock:
            counts["YES" if yes else "NO"] += 1
            if not args.dry_run:
                # a dry run must NOT log: a logged file is skipped next run, so
                # logging without moving would strand it as a permanent miss.
                # old tag is the third field so --undo can put the file back
                log_fp.write(f"{name} {'YES' if yes else 'NO'} {src['tag']}\n")
                log_fp.flush()  # survive a kill -9 mid-run
            if yes:
                print(f"  → commerce (was {src['tag']}): {src['label']}")

    try:
        with ThreadPoolExecutor(args.workers) as ex:
            list(ex.map(handle, todo))
    finally:
        log_fp.close()
    print(f"\nmoved={counts['YES']}  left alone={counts['NO']}  errors={counts['ERR']}")
    if counts["ERR"]:
        print("Errors were not logged — re-run to retry them.")


if __name__ == "__main__":
    main()

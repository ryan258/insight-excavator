#!/usr/bin/env python3
"""Bulk-import ChatGPT and Claude chat exports into ./sources. CLI, not part of the web app.

    M=anthropic/claude-haiku-4.5 OPENROUTER_API_KEY=... python3 import.py --limit 50
    M=anthropic/claude-haiku-4.5 OPENROUTER_API_KEY=... python3 import.py

One kept conversation becomes one source file holding a single idea statement.
Resumable: every verdict is appended to import-seen.log and skipped on re-run,
so an interrupted ingest picks up where it stopped and a re-run costs nothing.

Decisions behind this file are in docs/research/{export-format-anatomy,
idea-filter-sample,one-source-file}.md — read those before changing it.
"""
import argparse
import json
import os
import re
import sys
import threading
import zipfile
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import server  # noqa: E402  — reuse ai(), TAGS, and the OpenRouter plumbing

ROOT = Path(__file__).parent
SEEN_LOG = ROOT / "import-seen.log"
TECH_LOG = ROOT / "import-technique.log"  # --technique pass, separate verdict space
DOWNLOADS = Path.home() / "Downloads"
# The zip names are swapped in the export itself; this is not a typo.
CHATGPT_ZIP = DOWNLOADS / "rlwd--claude.zip"
CLAUDE_ZIP = DOWNLOADS / "rlwd--gpt.zip"

USER_TEXT_CAP = 6000  # what the filter was calibrated on

PROMPT = """You are triaging one AI chat conversation for an idea vault. The vault
exists to be mined later for essay angles, frameworks, product ideas, and story
premises. It is fed to a tool that picks two entries at random and looks for a
non-obvious connection between them.

You will see ONLY the user's own turns. Judge only what the user actually wrote.
Whatever the assistant said back is not evidence and is not available to you.

KEEP if the user's own words contain a belief, a framework, a distinction they
drew, a position they argued, a premise they invented, or the shape of something
they want to build. Length is not the test — a one-line premise nobody else would
have thought of is a KEEP.

DROP: debugging and error-chasing, code review, how-do-I questions, tool and
config help, drafting or editing someone else's copy, factual lookups, requests
for a list or a deliverable, tests of the model itself, small talk.

Two traps, both seen in real data:

1. A conversation can be long, technical, and useful and still be DROP. Effort is
   not insight. Ask whether an *idea* is present, not whether work happened.
2. An evocative-sounding request is not an idea. "Make a style guide for hygge if
   it were a brand" is a prompt, not a thought — the user is commissioning output,
   not saying what they believe. DROP it. But a spec, pitch, or design the user
   wrote themselves and brought for reaction IS their thinking — KEEP it, even
   though it looks like a deliverable.

TITLE: {title}

WHAT THE USER SAID (their turns only, in order, truncated):
{user_text}

Reply in exactly this format, nothing else:
VERDICT: KEEP or DROP
KIND: two-to-four words naming what this is (e.g. "debugging session", "brand
framework", "story premise", "config help")
WHY: one sentence
IDEA: if KEEP, the single idea in one sentence, using only words and claims
present in the user's turns above. If you cannot state it without adding
something the user did not say, reply THIN instead. If DROP, reply NONE.
"""
# KIND and WHY are unused here, but this is the prompt that was measured at
# 39/40 in #5 and any edit moves the verdicts. Folding TAG/LABEL into this call
# to save the classify pass was tried and reverted: it changed 6 verdicts in 60
# against a measured self-consistency noise floor of 1 in 60, losing 4 of 13
# keeps. Tag and label come from server.classify() on survivors instead.


TECHNIQUE_PROMPT = """You are triaging one AI chat conversation for a vault of
PROMPTING PRACTICE. This is a different axis from the idea filter: these
conversations were already judged to contain no idea worth keeping. You are
looking for something else — evidence of how this person works with AI.

You will see ONLY the user's own turns. Judge only what the user actually wrote.
What the assistant said back is not evidence and is not available to you.

KEEP if the user's turns show a reusable way of working with an AI: a prompt
structure worth repeating, a constraint or format they imposed to get a better
answer, a role or persona they set up, a correction that redirected the model, a
decomposition of a hard task into steps, or a stated preference about how they
want AI output shaped. The subject matter does not matter — a prompt about
cocktails can carry a technique worth keeping.

DROP if there is no transferable method: a bare question with no shaping, a
one-line lookup, pasted text with no instruction attached, or a request so
specific to that moment that nothing carries over.

Three traps:

1. Short does not mean DROP and long does not mean KEEP. A single sentence that
   sets up a role and a constraint is a KEEP. Three thousand words of pasted
   article with "thoughts?" on the end is a DROP.
2. A good *result* is not a technique. You cannot see the results. Judge only
   the shape of what the user wrote.
3. Do not invent the technique. If you cannot name it using what is visibly on
   the page, that is a DROP.

TITLE: {title}

WHAT THE USER SAID (their turns only, in order, truncated):
{user_text}

Reply in exactly this format, nothing else:
VERDICT: KEEP or DROP
TECHNIQUE: if KEEP, the transferable method in one sentence, stated so it could
be reused on an unrelated task. Use only what is present in the user's turns. If
you cannot state it without inventing, reply THIN. If DROP, reply NONE.
LABEL: if KEEP, four to six words naming the technique. If DROP, reply NONE.
"""


# ---------- reading the exports ----------

def stream_array(fp):
    """Yield elements of a top-level JSON array. Peak memory is one conversation."""
    dec = json.JSONDecoder()
    buf, started = "", False
    while True:
        chunk = fp.read(1 << 20)
        if chunk:
            buf += chunk.decode("utf-8")
        if not started:
            i = buf.find("[")
            if i < 0:
                if not chunk:
                    return
                continue
            buf, started = buf[i + 1:], True
        while True:
            s = buf.lstrip(" \n\r\t,")
            if s[:1] == "]" or (not s and not chunk):
                return
            if not s:
                break
            try:
                obj, end = dec.raw_decode(s)
            except ValueError:
                buf = s
                break  # partial object, need more bytes
            buf = s[end:]
            yield obj
        if not chunk:
            return


def chatgpt_messages(conv):
    """Walk parent links up from current_node, then reverse.

    Do not iterate mapping.values() — it holds dead edit/regen branches, and
    dict order is the export writer's insertion order, not conversation order.
    """
    mapping = conv["mapping"]
    path, nid = [], conv.get("current_node")
    while nid is not None and nid in mapping:
        path.append(nid)
        nid = mapping[nid]["parent"]
    path.reverse()
    out = []
    for nid in path:
        m = mapping[nid]["message"]
        if not m:
            continue
        if m["author"]["role"] not in ("user", "assistant"):
            continue
        if m.get("recipient") not in (None, "all"):
            continue  # assistant->tool call, not conversation
        c = m.get("content") or {}
        ct = c.get("content_type")
        if ct == "text":
            text = "".join(c.get("parts") or [])
        elif ct == "multimodal_text":
            # parts is a mixed list of strings and asset-pointer dicts
            text = "".join(p for p in (c.get("parts") or []) if isinstance(p, str))
        else:
            continue
        if text.strip():
            out.append((m["author"]["role"], text.strip()))
    return out


def claude_messages(conv):
    """Array order is already chronological — do not sort, thousands of
    created_at values tie. Never read the top-level .text: it is a flattened
    render contaminated with chain-of-thought and tool chatter."""
    out = []
    for m in conv.get("chat_messages") or []:
        text = "".join(
            b.get("text") or ""
            for b in (m.get("content") or [])
            if b.get("type") == "text"
        ).strip()
        if text:
            out.append(("user" if m["sender"] == "human" else "assistant", text))
    return out


def conversations():
    """Yield every conversation in both exports as a uniform dict."""
    with zipfile.ZipFile(CHATGPT_ZIP) as z, z.open("conversations.json") as f:
        for conv in stream_array(f):
            msgs = chatgpt_messages(conv)
            if msgs:
                ts = conv.get("create_time")
                yield {
                    "src": "chatgpt",
                    "id": conv["conversation_id"],
                    "title": conv.get("title") or "",
                    "date": (
                        datetime.fromtimestamp(ts, timezone.utc).date().isoformat()
                        if ts else ""
                    ),
                    "msgs": msgs,
                }
    with zipfile.ZipFile(CLAUDE_ZIP) as z, z.open("conversations.json") as f:
        for conv in stream_array(f):
            msgs = claude_messages(conv)
            if msgs:
                yield {
                    "src": "claude",
                    "id": conv["uuid"],
                    "title": conv.get("name") or "",   # Claude calls it 'name'
                    "date": (conv.get("created_at") or "")[:10],
                    "msgs": msgs,
                }


# ---------- filtering ----------

def user_text(conv):
    parts = [t for role, t in conv["msgs"] if role == "user"]
    out = "\n---\n".join(parts)
    return out[:USER_TEXT_CAP] + ("\n[...truncated]" if len(out) > USER_TEXT_CAP else "")


def field(raw, key):
    m = re.search(rf"^{key}:\s*(.+)$", raw, re.M)
    return m.group(1).strip() if m else ""


def one_line(s, limit=200):
    """Header values must survive load_source's line-based parse."""
    return " ".join(s.split())[:limit]


def judge(conv):
    """-> (verdict, idea, tag, label). Two calls for a keep, one for a drop.

    Raises on an API failure so the caller can leave the conversation unlogged
    and retry it on the next run."""
    raw = server.ai(PROMPT.format(
        title=conv["title"] or "(untitled)",
        user_text=user_text(conv),
    ))
    if not field(raw, "VERDICT").upper().startswith("KEEP"):
        return "DROP", "", "", ""
    idea = field(raw, "IDEA")
    if not idea or idea.upper() in ("NONE", "THIN"):
        return "THIN", "", "", ""      # kept, but no statement worth a file
    tag, label = server.classify(idea)  # second call, survivors only (~16%)
    return "KEEP", idea, tag, one_line(label, 60)


def judge_technique(conv):
    """-> (verdict, technique, tag, label). One call, never two.

    The tag is always ai-practice, so there is nothing for classify() to decide
    — that is the whole point of a separate pile. The label comes back in the
    same call, so a keep costs one request instead of the idea pass's two."""
    raw = server.ai(TECHNIQUE_PROMPT.format(
        title=conv["title"] or "(untitled)",
        user_text=user_text(conv),
    ))
    if not field(raw, "VERDICT").upper().startswith("KEEP"):
        return "DROP", "", "", ""
    tech = field(raw, "TECHNIQUE")
    if not tech or tech.upper() in ("NONE", "THIN"):
        return "THIN", "", "", ""
    label = field(raw, "LABEL")
    return "KEEP", tech, "ai-practice", one_line(label or conv["title"], 60)


# ---------- writing ----------

def write_source(out_dir, conv, idea, tag, label):
    path = out_dir / f"{conv['src']}-{conv['id']}.txt"
    path.write_text(
        f"tag: {tag}\n"
        f"label: {label}\n"
        f"source: {conv['src']}\n"
        f"date: {conv['date']}\n"
        f"conv: {conv['id']}\n"
        f"title: {one_line(conv['title'])}\n"
        f"---\n{idea}\n"
    )
    return path.name


def load_seen(log):
    if not log.exists():
        return set()
    return {
        line.split()[1]
        for line in log.read_text().splitlines()
        if len(line.split()) >= 2
    }


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument(
        "--limit", type=int,
        help="stop after N unseen conversations. Note this takes a CONTIGUOUS "
             "block in export order, not a random sample — idea density is "
             "clumpy, so a trial run's keep rate is not the corpus rate "
             "(observed 10%%, 18%%, 30%% on consecutive blocks of 40).",
    )
    ap.add_argument("--out", type=Path, default=ROOT / "sources")
    ap.add_argument("--log", type=Path, default=None)
    ap.add_argument("--workers", type=int, default=8)
    ap.add_argument(
        "--technique", action="store_true",
        help="second pass: re-judge the conversations the idea filter DROPPED, "
             "looking for reusable prompting practice instead of ideas. "
             "Survivors are written as ai-practice. Uses its own log, so the "
             "two passes never skip each other.",
    )
    args = ap.parse_args()
    if args.log is None:
        args.log = TECH_LOG if args.technique else SEEN_LOG

    if not os.environ.get("OPENROUTER_API_KEY"):
        raise SystemExit("Set OPENROUTER_API_KEY first.")
    args.out.mkdir(parents=True, exist_ok=True)

    seen = load_seen(args.log)
    print(f"model={server.model_name()}  out={args.out}  already seen={len(seen)}")

    # The technique pass only ever looks at what the idea pass threw away.
    targets = None
    if args.technique:
        if not SEEN_LOG.exists():
            raise SystemExit(f"{SEEN_LOG.name} not found — run the idea pass first.")
        targets = {
            p[1] for p in (l.split() for l in SEEN_LOG.read_text().splitlines())
            if len(p) >= 3 and p[2] == "DROP"
        }
        print(f"technique pass over {len(targets)} conversations the idea filter dropped")

    pending = []
    for conv in conversations():
        if conv["id"] in seen:
            continue
        if targets is not None and conv["id"] not in targets:
            continue
        pending.append(conv)
        if args.limit and len(pending) >= args.limit:
            break
    print(f"{len(pending)} conversations to filter")

    lock = threading.Lock()
    counts = {"KEEP": 0, "DROP": 0, "THIN": 0, "ERROR": 0}
    log_fp = args.log.open("a")

    verdict_of = judge_technique if args.technique else judge

    def handle(conv):
        try:
            verdict, idea, tag, label = verdict_of(conv)
        except Exception as e:
            # Unlogged on purpose: an API failure should be retried next run,
            # not silently recorded as a decision about this conversation.
            with lock:
                counts["ERROR"] += 1
                print(f"  ERROR {conv['src']} {conv['id']}: {str(e)[:120]}")
            return
        name = ""
        if verdict == "KEEP":
            name = write_source(args.out, conv, idea, tag, label)
        with lock:
            counts[verdict] += 1
            log_fp.write(f"{conv['src']} {conv['id']} {verdict}\n")
            log_fp.flush()  # survive a kill -9 mid-run
            done = sum(counts.values())
            if verdict == "KEEP":
                print(f"  [{done}/{len(pending)}] KEEP {tag:18} {label}")
            elif done % 25 == 0:
                print(f"  [{done}/{len(pending)}] ...")

    try:
        with ThreadPoolExecutor(args.workers) as ex:
            list(ex.map(handle, pending))
    finally:
        log_fp.close()

    kept, judged = counts["KEEP"], counts["KEEP"] + counts["DROP"] + counts["THIN"]
    print(
        f"\nkept {kept}  dropped {counts['DROP']}  thin {counts['THIN']}  "
        f"errors {counts['ERROR']}"
        + (f"  ({100 * kept / judged:.0f}% keep rate)" if judged else "")
    )
    if counts["ERROR"]:
        print("Errors were not logged — re-run to retry them.")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Idea Digger — local web app. Run: python3 server.py  then open http://localhost:8420

Env: OPENROUTER_API_KEY (required), M (optional model override; else config.json).
Sources live as plain text files in ./sources. No database.
"""
import json
import os
import random
import re
import time
import urllib.error
import urllib.request
import uuid
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

ROOT = Path(__file__).parent
SOURCES = ROOT / "sources"
SOURCES.mkdir(exist_ok=True)
TAGS = ["content-topics", "brand-frameworks", "creative-projects", "essays",
        "ai-practice", "other"]
PORT = 8420


def model_name():
    # env var M wins, else config.json — re-read each call so swaps need no restart
    return os.environ.get("M") or json.loads((ROOT / "config.json").read_text())["model"]


def ai(prompt, tries=3):
    req = urllib.request.Request(
        "https://openrouter.ai/api/v1/chat/completions",
        data=json.dumps(
            {"model": model_name(), "messages": [{"role": "user", "content": prompt}]}
        ).encode(),
        headers={
            "Authorization": f"Bearer {os.environ['OPENROUTER_API_KEY']}",
            "Content-Type": "application/json",
        },
    )
    last = None
    for attempt in range(tries):
        try:
            with urllib.request.urlopen(req, timeout=180) as r:
                data = json.loads(r.read())
        except urllib.error.HTTPError as e:
            err_body = e.read().decode("utf-8", errors="ignore")
            try:
                err_json = json.loads(err_body)
                msg = err_json.get("error", {}).get("message", err_body)
            except Exception:
                msg = err_body
            raise RuntimeError(f"OpenRouter HTTP {e.code}: {msg}")
        if "choices" not in data:
            # A 200 carrying an error body instead of choices. Free-tier
            # upstreams do this constantly (504 idle timeout, 429 rate limit)
            # and it is transient — but 4xx like 402 out-of-credits will never
            # succeed on a retry, so only back off on 5xx and 429.
            err = data.get("error", data)
            code = err.get("code") if isinstance(err, dict) else None
            if isinstance(code, int) and (code >= 500 or code == 429) \
                    and attempt < tries - 1:
                time.sleep(2 ** attempt)
                continue
            raise RuntimeError(f"OpenRouter error: {err}")
        choice = data["choices"][0]
        text = (choice.get("message") or {}).get("content")
        # A 200 with content:null is a real and frequent response (~1 call in 10
        # on some models) — reasoning-only output, content filtering, truncation.
        # Transient, so retry; an unguarded null used to abort the whole run.
        if text is not None:
            return text.strip()
        last = choice.get("finish_reason")
    raise RuntimeError(
        f"OpenRouter returned no content after {tries} tries (finish_reason={last})"
    )


# ---------- sources ----------

def classify(text):
    out = ai(
        "You are filing a text source into an idea system.\n"
        f"Assign exactly ONE tag from this list: {', '.join(TAGS)}.\n"
        "Also write a short label of at most 5 words describing the item.\n\n"
        "Reply with exactly two lines:\n"
        "TAG: <tag>\n"
        "LABEL: <label>\n\n"
        f"TEXT:\n{text}"
    )
    tag = re.search(r"TAG:\s*(\S+)", out)
    label = re.search(r"LABEL:\s*(.+)", out)
    tag = tag.group(1).strip().lower() if tag else "other"
    if tag not in TAGS:
        tag = "other"
    return tag, (label.group(1).strip() if label else "untitled")


def save_source(text, tag, label):
    # timestamp keeps files chronologically sortable; uuid suffix prevents
    # same-millisecond collisions under the threaded server
    name = f"{int(time.time() * 1000)}-{uuid.uuid4().hex[:6]}.txt"
    (SOURCES / name).write_text(f"tag: {tag}\nlabel: {label}\n---\n{text}")
    return name


def load_source(name):
    raw = (SOURCES / Path(name).name).read_text()
    head, _, text = raw.partition("\n---\n")
    meta = dict(
        line.split(": ", 1) for line in head.splitlines() if ": " in line
    )
    return {
        "file": Path(name).name,
        "tag": meta.get("tag", "other"),
        "label": meta.get("label", "untitled"),
        "text": text,
    }


def by_tag():
    groups = {}
    for f in SOURCES.glob("*.txt"):
        s = load_source(f.name)
        groups.setdefault(s["tag"], []).append(s)
    return groups


def pick_pair():
    groups = by_tag()
    tags = list(groups)
    if len(tags) < 2:
        raise RuntimeError(
            "Need saved sources in at least 2 different tags before digging."
        )
    t1, t2 = random.sample(tags, 2)
    return random.choice(groups[t1]), random.choice(groups[t2])


def pick_third(exclude_tags):
    groups = by_tag()
    tags = [t for t in groups if t not in exclude_tags]
    if not tags:
        raise RuntimeError("No sources outside the original pair's tags to chain against.")
    return random.choice(groups[random.choice(tags)])


# ---------- the digging loop ----------

def dig(a, b):
    insight = ai(
        "Find a non-obvious connection between these two things. The connection "
        "must produce something usable: an essay angle, a framework, a product "
        "idea, or a story premise. Do not give a surface-level answer.\n\n"
        f"THING 1 ({a['tag']} — {a['label']}):\n{a['text']}\n\n"
        f"THING 2 ({b['tag']} — {b['label']}):\n{b['text']}"
    )
    score = None
    for attempt in range(3):
        judge = ai(
            "Score this insight 1 to 10 on novelty. If it scores below 7, "
            "explain why it's obvious, then generate a deeper replacement.\n\n"
            "Reply in exactly this format:\n"
            "SCORE: <number>\n"
            "WHY: <one line, or NONE if 7+>\n"
            "REPLACEMENT: <the deeper replacement insight, or NONE if 7+>\n\n"
            f"INSIGHT:\n{insight}"
        )
        m = re.search(r"SCORE:\s*(\d+)", judge)
        # None means the model didn't follow the format or gave an out-of-range
        # number; shown as unscored rather than faked
        n = int(m.group(1)) if m else None
        score = n if n is not None and 1 <= n <= 10 else None
        if (score is not None and score >= 7) or attempt == 2:
            break
        rm = re.search(r"REPLACEMENT:\s*(.+)", judge, re.S)
        rep = rm.group(1).strip() if rm else ""
        if rep and rep.upper() != "NONE":
            insight = rep
    return insight, score


GATES = [
    ("REVEAL", "does it expose the lie of unlimited capacity?"),
    ("BUILD", "does it create proof, practice, or capacity?"),
    ("DELIVER", "does it respect the bandwidth?"),
]


def run_filter(insight):
    gate_lines = "\n".join(f"{name} — {q}" for name, q in GATES)
    out = ai(
        "Run this insight through a three-gate filter. For each gate answer "
        "PASS or FAIL with one short reason.\n\n"
        f"Gates:\n{gate_lines}\n\n"
        "Reply in exactly this format, one line per gate:\n"
        "REVEAL: PASS or FAIL — <one-line reason>\n"
        "BUILD: PASS or FAIL — <one-line reason>\n"
        "DELIVER: PASS or FAIL — <one-line reason>\n\n"
        f"INSIGHT:\n{insight}"
    )
    results = []
    for name, _ in GATES:
        m = re.search(rf"{name}:\s*(PASS|FAIL)\s*[—:-]*\s*(.*)", out)
        results.append({
            "gate": name,
            "verdict": m.group(1) if m else "?",
            "why": m.group(2).strip() if m else "could not parse filter output",
        })
    return results


def keep(insight, score, pair):
    score_str = f"{score}/10" if score is not None else "unscored"
    # escape leading '#'s so model text can't be mistaken for a new record
    # header by a future digest parser that splits keepers.md on "^## "
    safe_insight = re.sub(r"(?m)^#", r"\\#", insight)
    entry = f"## {time.strftime('%Y-%m-%d')} — {score_str} — {pair}\n\n{safe_insight}\n\n"
    with open(ROOT / "keepers.md", "a") as f:
        f.write(entry)


# ---------- http ----------

class Handler(BaseHTTPRequestHandler):
    def _json(self, obj, status=200):
        body = json.dumps(obj).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        if self.path == "/":
            body = (ROOT / "index.html").read_bytes()
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
        else:
            self._json({"error": "not found"}, 404)

    def do_POST(self):
        # a browser sets Origin on every cross-site fetch/form POST; curl and
        # same-origin page requests don't send a mismatched one, so this blocks
        # a malicious page's script from silently POSTing here while leaving
        # documented curl usage untouched
        origin = self.headers.get("Origin")
        if origin and origin not in (f"http://127.0.0.1:{PORT}", f"http://localhost:{PORT}"):
            self._json({"error": "cross-origin requests are not allowed"}, 403)
            return
        try:
            length = int(self.headers.get("Content-Length", 0))
            body = json.loads(self.rfile.read(length)) if length else {}
            if self.path == "/api/save":
                text = body["text"].strip()
                if not text:
                    raise RuntimeError("Nothing to save.")
                tag, label = classify(text)
                name = save_source(text, tag, label)
                self._json({"file": name, "tag": tag, "label": label, "tags": TAGS})
            elif self.path == "/api/retag":
                if body["tag"] not in TAGS:
                    raise RuntimeError("Unknown tag.")
                s = load_source(body["file"])
                save = SOURCES / s["file"]
                save.write_text(
                    f"tag: {body['tag']}\nlabel: {s['label']}\n---\n{s['text']}"
                )
                self._json({"ok": True})
            elif self.path == "/api/pick":
                a, b = pick_pair()
                self._json({
                    "a": {k: a[k] for k in ("file", "tag", "label")},
                    "b": {k: b[k] for k in ("file", "tag", "label")},
                })
            elif self.path == "/api/insight":
                a = load_source(body["a"])
                b = load_source(body["b"])
                insight, score = dig(a, b)
                self._json({"insight": insight, "score": score})
            elif self.path == "/api/chain":
                c = pick_third(body.get("exclude", []))
                seed = {
                    "tag": "insight",
                    "label": "a previously dug insight",
                    "text": body["insight"],
                }
                insight, score = dig(seed, c)
                self._json({
                    "insight": insight,
                    "score": score,
                    "source": {k: c[k] for k in ("file", "tag", "label")},
                })
            elif self.path == "/api/filter":
                self._json({"gates": run_filter(body["insight"])})
            elif self.path == "/api/keep":
                keep(body["insight"], body["score"], body["pair"])
                self._json({"ok": True})
            else:
                self._json({"error": "not found"}, 404)
        except Exception as e:  # surface everything to the UI
            self._json({"error": str(e)}, 500)

    def log_message(self, *args):
        pass  # quiet


if __name__ == "__main__":
    if not os.environ.get("OPENROUTER_API_KEY"):
        raise SystemExit("Set OPENROUTER_API_KEY first.")
    print(f"Idea Digger → http://localhost:{PORT}  (model: {model_name()})")
    ThreadingHTTPServer(("127.0.0.1", PORT), Handler).serve_forever()

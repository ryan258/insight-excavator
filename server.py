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
import urllib.request
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

ROOT = Path(__file__).parent
SOURCES = ROOT / "sources"
SOURCES.mkdir(exist_ok=True)
TAGS = ["content-topics", "brand-frameworks", "creative-projects", "essays", "other"]
PORT = 8420


def model_name():
    # env var M wins, else config.json — re-read each call so swaps need no restart
    return os.environ.get("M") or json.loads((ROOT / "config.json").read_text())["model"]


def ai(prompt):
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
    with urllib.request.urlopen(req, timeout=180) as r:
        data = json.loads(r.read())
    if "choices" not in data:
        raise RuntimeError(f"OpenRouter error: {data.get('error', data)}")
    return data["choices"][0]["message"]["content"].strip()


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
    name = f"{int(time.time() * 1000)}.txt"
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


def pick_pair():
    by_tag = {}
    for f in SOURCES.glob("*.txt"):
        s = load_source(f.name)
        by_tag.setdefault(s["tag"], []).append(s)
    tags = [t for t in by_tag if by_tag[t]]
    if len(tags) < 2:
        raise RuntimeError(
            "Need saved sources in at least 2 different tags before digging."
        )
    t1, t2 = random.sample(tags, 2)
    return random.choice(by_tag[t1]), random.choice(by_tag[t2])


# ---------- the digging loop ----------

def dig(a, b):
    insight = ai(
        "Find a non-obvious connection between these two things. The connection "
        "must produce something usable: an essay angle, a framework, a product "
        "idea, or a story premise. Do not give a surface-level answer.\n\n"
        f"THING 1 ({a['tag']} — {a['label']}):\n{a['text']}\n\n"
        f"THING 2 ({b['tag']} — {b['label']}):\n{b['text']}"
    )
    score = 0
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
        score = int(m.group(1)) if m else 7  # ponytail: unparseable score counts as a pass
        if score >= 7 or attempt == 2:
            break
        rm = re.search(r"REPLACEMENT:\s*(.+)", judge, re.S)
        rep = rm.group(1).strip() if rm else ""
        if rep and rep.upper() != "NONE":
            insight = rep
    return insight, score


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

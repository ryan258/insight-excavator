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
        "ai-practice", "commerce", "other"]
PORT = 8420


def config():
    # re-read each call so edits need no restart
    return json.loads((ROOT / "config.json").read_text())


def model_name():
    # env var M wins, else config.json
    return os.environ.get("M") or config()["model"]


def vault_dir():
    """Where kept insights land — one note per insight, for Obsidian."""
    return Path(config()["vault"]).expanduser()


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


def two_tags(groups):
    """Two distinct tags, drawn with weight sqrt(size).

    Uniform over tags makes a source's odds inversely proportional to how many
    neighbours it has — an 11-source tag drowned out 1,125 (issue #10). Uniform
    over sources instead hands 55% of every dig to ai-practice. sqrt splits the
    difference: per-source imbalance drops from 13.8x to 3.7x, and a brand-new
    tag of size 1 draws ~1% instead of 33%.
    """
    tags = list(groups)
    weights = [len(groups[t]) ** 0.5 for t in tags]
    t1 = random.choices(tags, weights)[0]
    i = tags.index(t1)
    return t1, random.choices(tags[:i] + tags[i + 1:], weights[:i] + weights[i + 1:])[0]


def pick_pair():
    groups = by_tag()
    if len(groups) < 2:
        raise RuntimeError(
            "Need saved sources in at least 2 different tags before digging."
        )
    t1, t2 = two_tags(groups)
    return random.choice(groups[t1]), random.choice(groups[t2])


def pick_third(exclude_tags):
    groups = by_tag()
    groups = {t: g for t, g in groups.items() if t not in exclude_tags}
    if not groups:
        raise RuntimeError("No sources outside the original pair's tags to chain against.")
    tags = list(groups)
    t = random.choices(tags, [len(groups[x]) ** 0.5 for x in tags])[0]  # same as two_tags
    return random.choice(groups[t])


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


def slugify(text, words=8):
    first_line = next((ln for ln in text.strip().splitlines() if ln.strip()), "")
    slug = re.sub(r"[^a-z0-9]+", "-", first_line.lower()).strip("-")
    return "-".join(slug.split("-")[:words]) or "insight"


def keep(insight, score, pair, tags=()):
    """Write one Obsidian note per kept insight. Returns the path written."""
    d = vault_dir()
    d.mkdir(parents=True, exist_ok=True)
    date = time.strftime("%Y-%m-%d")
    # ponytail: slug from the insight's own opening words — no second AI call for a title
    stem = f"{date}-{slugify(insight)}"
    path = d / f"{stem}.md"
    for n in range(2, 100):  # same slug twice in a day is possible, not worth a uuid
        if not path.exists():
            break
        path = d / f"{stem}-{n}.md"

    # pair arrives as "A × B", or "A × B ⛓ C" after chaining — each part is a source label
    links = " + ".join(
        f"[[{p.strip().translate(str.maketrans('', '', '[]|#^'))}]]"
        for p in re.split(r"[×⛓]", pair) if p.strip()
    )
    all_tags = dict.fromkeys(["insight", *tags])  # dedupe, keep order
    front = [f"date: {date}", f"tags: [{', '.join(all_tags)}]"]
    if score is not None:
        front.insert(1, f"score: {score}")
    # a '---' at the start of a body line would end the frontmatter block early
    body = re.sub(r"(?m)^---$", "———", insight.strip())
    path.write_text(
        "---\n" + "\n".join(front) + "\n---\n\n" + body + f"\n\nDug from {links}\n"
    )
    return path


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
                p = keep(body["insight"], body["score"], body["pair"],
                         body.get("tags", []))
                self._json({"ok": True, "note": p.name})
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

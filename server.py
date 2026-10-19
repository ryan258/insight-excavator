#!/usr/bin/env python3
"""Idea Digger — local web app. Run: python3 server.py  then open http://localhost:8420

Env: OPENROUTER_API_KEY (required; may live in ./.env), M (optional model override
for every call; else config.json), DIGGER_PORT (optional, default 8420).
Sources live as plain text files in ./sources; every dig and grade is one line in
./digs.jsonl. No database.
"""
import json
import os
import random
import re
import threading
import time
import traceback
import unicodedata
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
PORT = int(os.environ.get("DIGGER_PORT", 8420))
TIMEOUT = 120          # seconds per OpenRouter call; free models that hang never come back
CLIP = 4000            # chars of one source sent to the model; the file keeps the rest
MAX_BODY = 1 << 20     # request bodies are pasted text, never megabytes
SRC_FILE = re.compile(r"[\w.-]+\.txt")
DIG_ID = re.compile(r"[0-9a-f]{12}")
DIG_BUDGET = 240       # seconds; no new judge round starts after this (a call in flight still finishes)
GATE = 30              # graded digs before the tool has earned its next feature (roadmap.md)
GRADES = ("maybe", "skip")   # "keep" is recorded by keep() itself
LEDGER = ROOT / "digs.jsonl"
_ledger_lock = threading.Lock()
_tl = threading.local()   # per-request list of OpenRouter calls, for the ledger's cost columns


class NotReady(Exception):
    """A well-formed request the corpus cannot serve yet (HTTP 409)."""


class BadRequest(ValueError):
    """The caller sent something wrong (HTTP 400). A bare ValueError is a bug (500)."""


class NoSuchSource(FileNotFoundError):
    """A source or dig id that does not exist (HTTP 404). A bare FileNotFoundError,
    such as a missing config.json, is a bug (500)."""


def load_env():
    """Fill os.environ from ./.env (KEY=value lines) without overriding what is set."""
    f = ROOT / ".env"
    if not f.exists():
        return
    for ln in f.read_text(encoding="utf-8").splitlines():
        k, sep, v = ln.partition("=")
        if sep and not k.lstrip().startswith("#") and k.strip():
            os.environ.setdefault(k.strip(), v.strip().strip("\"'"))


def config():
    # re-read each call so edits need no restart; config.json is local (gitignored),
    # config.example.json is the tracked default
    p = ROOT / "config.json"
    if not p.exists():
        p = ROOT / "config.example.json"
    return json.loads(p.read_text(encoding="utf-8"))


def model_name(cheap=False):
    """env var M wins for every call; else cheap_model for cheap work (if set); else model."""
    cfg = config()
    return os.environ.get("M") or (cheap and cfg.get("cheap_model")) or cfg["model"]


def vault_dir():
    """Where kept insights land — one note per insight, for Obsidian."""
    return Path(config()["vault"]).expanduser()


def transient(code):
    """5xx and 429 are worth another try; a 4xx like 402 (out of credits) never is."""
    return isinstance(code, int) and (code >= 500 or code == 429)


def ai(prompt, tries=3, cheap=False):
    """One OpenRouter call. cheap=True is for tagging and import triage, where the
    cheap_model in config.json (if any) is plenty; digging and judging stay strong."""
    cfg = config()
    payload = {"model": model_name(cheap), "messages": [{"role": "user", "content": prompt}]}
    if cfg.get("temperature") is not None:
        payload["temperature"] = cfg["temperature"]
    # Optional privacy switch: "data_collection": "deny" in config.json asks OpenRouter
    # to route only to providers that do not log or train on prompts. Off by default
    # because some models have no such endpoint and would 404.
    if cfg.get("data_collection"):
        payload["provider"] = {"data_collection": cfg["data_collection"]}
    req = urllib.request.Request(
        "https://openrouter.ai/api/v1/chat/completions",
        data=json.dumps(payload).encode(),
        headers={
            "Authorization": f"Bearer {os.environ['OPENROUTER_API_KEY']}",
            "Content-Type": "application/json",
        },
    )
    last = None
    for attempt in range(tries):
        more = attempt < tries - 1
        try:
            with urllib.request.urlopen(req, timeout=TIMEOUT) as r:
                data = json.loads(r.read())
        except urllib.error.HTTPError as e:
            err_body = e.read().decode("utf-8", errors="ignore")
            try:
                err_json = json.loads(err_body)
                msg = err_json.get("error", {}).get("message", err_body)
            except Exception:
                msg = err_body
            # A real HTTP status gets the same treatment as the 200-with-error-body
            # case below — OpenRouter sends the identical failure both ways.
            if transient(e.code) and more:
                time.sleep(2 ** attempt)
                continue
            raise RuntimeError(f"OpenRouter HTTP {e.code}: {msg}")
        except (urllib.error.URLError, TimeoutError, ConnectionError, ValueError) as e:
            # unreachable, timed out, reset mid-read, or a truncated JSON body —
            # all transient, and none of them reach the HTTPError branch above
            if more:
                time.sleep(2 ** attempt)
                continue
            raise RuntimeError(f"OpenRouter unreachable: {e}")
        if not isinstance(data, dict):
            data = {"error": {"message": str(data)[:200]}}
        if not data.get("choices"):
            # A 200 carrying an error body instead of choices. Free-tier
            # upstreams do this constantly (504 idle timeout, 429 rate limit)
            # and it is transient — but 4xx like 402 out-of-credits will never
            # succeed on a retry, so only back off on 5xx and 429.
            err = data.get("error", data)
            code = err.get("code") if isinstance(err, dict) else None
            if transient(code) and more:
                time.sleep(2 ** attempt)
                continue
            raise RuntimeError(f"OpenRouter error: {err}")
        choice = data["choices"][0]
        text = (choice.get("message") or {}).get("content")
        calls = getattr(_tl, "calls", None)
        if calls is not None:   # a null-content retry still cost tokens, so log before the check
            u = data.get("usage") or {}
            calls.append({"model": payload["model"], "in": u.get("prompt_tokens"),
                          "out": u.get("completion_tokens"), "cost": u.get("cost")})
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

def clip(text):
    """One pasted 21k-char source must not become 21k chars of every prompt."""
    return text if len(text) <= CLIP else text[:CLIP] + "\n[…truncated]"


def field(text, key, multiline=False):
    """Value of a `KEY: value` line in a model reply, or None if absent.

    Models wrap the keys they were told to emit in markdown (`**TAG:** x`,
    `- Tag: x`); a strict `KEY:` regex read those as missing and silently filed,
    scored or judged them wrong. Case-insensitive; `multiline` takes the rest of
    the reply instead of one line."""
    m = re.search(
        rf"^[ \t>*_`#-]*{re.escape(key)}[ \t*_`]*:[ \t*_`]*" + (r"(.*)\Z" if multiline else r"(.*)$"),
        text, re.I | re.M | (re.S if multiline else 0))
    return m.group(1).strip(" \t*`") if m else None


def classify(text):
    out = ai(
        "You are filing a text source into an idea system.\n"
        f"Assign exactly ONE tag from this list: {', '.join(TAGS)}.\n"
        "Also write a short label of at most 5 words describing the item.\n\n"
        "Reply with exactly two lines:\n"
        "TAG: <tag>\n"
        "LABEL: <label>\n\n"
        f"TEXT:\n{clip(text)}",
        cheap=True,
    )
    tag = (field(out, "TAG") or "other").split(None, 1)[0].lower()
    if tag not in TAGS:
        tag = "other"
    return tag, (field(out, "LABEL") or "untitled")


def write_atomic(path, content):
    """Temp file then rename: a kill mid-write must never truncate a source, which
    cannot be regenerated. The temp name ends in .tmp so by_tag's *.txt glob skips it."""
    tmp = path.with_name(f".{path.name}.{uuid.uuid4().hex[:6]}.tmp")
    try:
        tmp.write_text(content, encoding="utf-8")
        os.replace(tmp, path)
    except BaseException:
        tmp.unlink(missing_ok=True)
        raise


def save_source(text, tag, label):
    # timestamp keeps files chronologically sortable; uuid suffix prevents
    # same-millisecond collisions under the threaded server
    name = f"{int(time.time() * 1000)}-{uuid.uuid4().hex[:6]}.txt"
    write_atomic(SOURCES / name, f"tag: {tag}\nlabel: {label}\n---\n{text}")
    _groups["sig"] = None
    return name


def read_source(path):
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError:
        raise NoSuchSource("no such source") from None


def load_source(name):
    raw = read_source(SOURCES / Path(name).name)
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


def set_tag(name, tag):
    """Rewrite only the `tag:` header line. Imported files carry source/date/conv/
    title headers that are the only route back to the original conversation, so
    nothing else may be touched."""
    path = SOURCES / Path(name).name
    head, sep, body = read_source(path).partition("\n---\n")
    lines = [f"tag: {tag}" if ln.startswith("tag: ") else ln for ln in head.splitlines()]
    if not any(ln.startswith("tag: ") for ln in lines):
        lines.insert(0, f"tag: {tag}")
    write_atomic(path, "\n".join(lines) + sep + body)
    _groups["sig"] = None


_groups = {"sig": None, "val": None}


def by_tag():
    """Sources grouped by tag. Parsing 2,000 files took ~330 ms per pick, so the
    result is cached against the files' names and mtimes; writes made here reset
    it explicitly because two writes can share a coarse mtime tick."""
    files = sorted(SOURCES.glob("*.txt"))
    sig = (str(SOURCES), tuple((f.name, f.stat().st_mtime_ns) for f in files))
    if _groups["sig"] != sig:
        groups = {}
        for f in files:
            try:
                s = load_source(f.name)
            except NoSuchSource:
                continue    # deleted between the glob and the read
            groups.setdefault(s["tag"], []).append(s)
        _groups.update(sig=sig, val=groups)
    return _groups["val"]


def draw_tag(groups, tags):
    """One tag out of `tags`, drawn with weight sqrt(size). See two_tags."""
    return random.choices(tags, [len(groups[t]) ** 0.5 for t in tags])[0]


def two_tags(groups):
    """Two distinct tags, drawn with weight sqrt(size).

    Uniform over tags makes a source's odds inversely proportional to how many
    neighbours it has — an 11-source tag drowned out 1,125 (issue #10). Uniform
    over sources instead hands 55% of every dig to ai-practice. sqrt splits the
    difference: per-source imbalance drops from 13.8x to 3.7x, and a brand-new
    tag of size 1 draws ~1% instead of 33%.
    """
    t1 = draw_tag(groups, list(groups))
    return t1, draw_tag(groups, [t for t in groups if t != t1])


def pick_pair():
    groups = by_tag()
    if len(groups) < 2:
        raise NotReady(
            "Need saved sources in at least 2 different tags before digging."
        )
    t1, t2 = two_tags(groups)
    return random.choice(groups[t1]), random.choice(groups[t2])


def pick_third(exclude_tags):
    groups = by_tag()
    groups = {t: g for t, g in groups.items() if t not in exclude_tags}
    if not groups:
        raise NotReady("No sources outside the original pair's tags to chain against.")
    return random.choice(groups[draw_tag(groups, list(groups))])


# ---------- the digging loop ----------

def dig(a, b, trail=None):
    """Connect, then judge-and-rewrite up to 3 rounds. `trail`, if given, collects
    each round's score (None when unparseable) for the ledger."""
    t0 = time.monotonic()
    insight = ai(
        "Find a non-obvious connection between these two things. The connection "
        "must produce something usable: an essay angle, a framework, a product "
        "idea, or a story premise. Do not give a surface-level answer.\n\n"
        f"THING 1 ({a['tag']} — {a['label']}):\n{clip(a['text'])}\n\n"
        f"THING 2 ({b['tag']} — {b['label']}):\n{clip(b['text'])}"
    )
    best = (None, insight)  # highest-scored (score, insight) seen so far
    for attempt in range(3):
        if attempt and time.monotonic() - t0 > DIG_BUDGET:
            break   # out of time: return the best insight seen so far
        judge = ai(
            "Score this insight 1 to 10 on novelty. If it scores below 7, "
            "explain why it's obvious, then generate a deeper replacement.\n\n"
            "Reply in exactly this format:\n"
            "SCORE: <number>\n"
            "WHY: <one line, or NONE if 7+>\n"
            "REPLACEMENT: <the deeper replacement insight, or NONE if 7+>\n\n"
            f"INSIGHT:\n{insight}"
        )
        m = re.match(r"\d+", field(judge, "SCORE") or "")
        # None means the model didn't follow the format or gave an out-of-range
        # number; shown as unscored rather than faked
        n = int(m.group()) if m else None
        score = n if n is not None and 1 <= n <= 10 else None
        if trail is not None:
            trail.append(score)
        # a rewrite can score worse than what it replaced, so the loop returns the
        # best insight it saw, not the last (ties keep the earlier one)
        if score is not None and (best[0] is None or score > best[0]):
            best = (score, insight)
        if (score is not None and score >= 7) or attempt == 2:
            break
        rep = field(judge, "REPLACEMENT", multiline=True) or ""
        if not rep or rep.upper() == "NONE":
            break  # nothing new to judge; another round would just re-score this text
        insight = rep
    return (best[1], best[0]) if best[0] is not None else (insight, None)


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
        f"INSIGHT:\n{clip(insight)}"
    )
    results = []
    for name, _ in GATES:
        m = re.match(r"(PASS|FAIL)[\s—–:-]*(.*)", field(out, name) or "", re.I)
        results.append({
            "gate": name,
            "verdict": m.group(1).upper() if m else "?",
            "why": m.group(2).strip(" *`") if m else "could not parse filter output",
        })
    return results


def slugify(text, words=8):
    first_line = next((ln for ln in text.strip().splitlines() if ln.strip()), "")
    # NFKD + ascii-ignore turns "café" into "cafe" instead of "caf"
    ascii_line = unicodedata.normalize("NFKD", first_line).encode("ascii", "ignore").decode()
    slug = re.sub(r"[^a-z0-9]+", "-", ascii_line.lower()).strip("-")
    return "-".join(slug.split("-")[:words]) or "insight"


def keep(insight, score, pair, tags=(), files=(), dig=None):
    """Write one Obsidian note per kept insight. Returns the path written.

    Every argument arrives from the browser, so each is checked here: score and
    tags are written into YAML frontmatter, where a stray newline is an injection."""
    if not isinstance(insight, str) or not insight.strip():
        raise BadRequest("Nothing to keep.")
    if score is not None and (isinstance(score, bool) or not isinstance(score, int)
                              or not 1 <= score <= 10):
        raise BadRequest("score must be an integer 1-10, or null")
    if not isinstance(pair, str):
        raise BadRequest("pair must be text")
    if not isinstance(tags, (list, tuple)) or not all(
            isinstance(t, str) and t in TAGS for t in tags):
        raise BadRequest("tags must be a list from the closed tag set")
    if not isinstance(files, (list, tuple)) or not all(
            isinstance(f, str) and SRC_FILE.fullmatch(f) for f in files):
        raise BadRequest("files must be a list of source filenames")
    if dig is not None and not (isinstance(dig, str) and DIG_ID.fullmatch(dig)):
        raise BadRequest("dig must be a dig id")

    date = time.strftime("%Y-%m-%d")
    # pair arrives as "A × B", or "A × B ⛓ C" after chaining — each part is a source label
    links = " + ".join(
        f"[[{p.strip().translate(str.maketrans('', '', '[]|#^'))}]]"
        for p in re.split(r"[×⛓]", pair) if p.strip()
    )
    all_tags = dict.fromkeys(["insight", *tags])  # dedupe, keep order
    front = [f"date: {date}", f"tags: [{', '.join(all_tags)}]"]
    if score is not None:
        front.insert(1, f"score: {score}")
    if files:
        # the wikilinks point at labels, which are not notes in the vault; the
        # filenames are the real route back to the source text in sources/
        front.append(f"sources: [{', '.join(dict.fromkeys(files))}]")
    if dig:
        front.append(f"dig: {dig}")   # the row in digs.jsonl: rounds, models, cost
    # a '---' at the start of a body line would end the frontmatter block early
    body = re.sub(r"(?m)^---$", "———", insight.strip())
    content = "---\n" + "\n".join(front) + "\n---\n\n" + body + f"\n\nDug from {links}\n"

    d = vault_dir()
    if not d.parent.exists():
        # mkdir -p would quietly build a wrong tree from a mistyped "vault" in config.json
        raise NotReady(f'vault folder {d} has no parent folder — check "vault" in config.json')
    d.mkdir(exist_ok=True)
    # ponytail: slug from the insight's own opening words — no second AI call for a title
    stem = f"{date}-{slugify(insight)}"
    # O_EXCL rather than exists(): two threads keeping the same slug at once both
    # get a file, and the suffix is uncapped
    n = 1
    while True:
        path = d / (f"{stem}.md" if n == 1 else f"{stem}-{n}.md")
        try:
            fd = os.open(path, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
            break
        except FileExistsError:
            n += 1
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(content)
    except BaseException:
        path.unlink(missing_ok=True)  # never leave an empty note behind
        raise
    return path


# ---------- the dig ledger ----------
# digs.jsonl is append-only, one JSON object per line: a dig row (has "insight") per
# dig, and a grade row (has "grade") per keep/maybe/skip. Every dig is recorded whether
# or not it is kept, so a refresh never loses a paid-for insight and the 30-graded-digs
# gate in roadmap.md can be read straight off this file.

def ledger_add(row):
    with _ledger_lock, LEDGER.open("a", encoding="utf-8") as f:
        f.write(json.dumps(row, ensure_ascii=False) + "\n")


def ledger_state():
    """({dig id: dig row}, {dig id: latest grade row}), in file order."""
    digs, grades = {}, {}
    try:
        text = LEDGER.read_text(encoding="utf-8")
    except FileNotFoundError:
        return digs, grades
    for ln in text.splitlines():
        try:
            r = json.loads(ln)
        except ValueError:
            continue    # a torn last line from a kill mid-append
        if not isinstance(r, dict) or "dig" not in r:
            continue
        if "insight" in r:
            digs[r["dig"]] = r
        elif "grade" in r:
            grades[r["dig"]] = r
    return digs, grades


def ledger_stats():
    digs, grades = ledger_state()
    n = {g: 0 for g in ("keep", *GRADES)}
    for k, g in grades.items():
        if k in digs and g["grade"] in n:
            n[g["grade"]] += 1
    return {"digs": len(digs), "graded": sum(n.values()), **n, "target": GATE}


def ledger_last():
    """Newest dig and its grade (None if ungraded), so a refresh can restore the card."""
    digs, grades = ledger_state()
    if not digs:
        return {"dig": None}
    row = list(digs.values())[-1]
    g = grades.get(row["dig"])
    return {"dig": row, "grade": g["grade"] if g else None}


def clean_why(why):
    """The optional one-line reason that travels with a grade."""
    if not isinstance(why, str):
        raise BadRequest("why must be text")
    return " ".join(why.split())[:200]


def grade_dig(dig_id, grade, why=""):
    if grade not in GRADES:
        raise BadRequest(f"grade must be one of {', '.join(GRADES)}")
    why = clean_why(why)
    if not (isinstance(dig_id, str) and DIG_ID.fullmatch(dig_id)) or dig_id not in ledger_state()[0]:
        raise NoSuchSource("no such dig")
    ledger_add({"dig": dig_id, "grade": grade, "why": why,
                "ts": time.strftime("%Y-%m-%dT%H:%M:%S")})


def logged_dig(a, b, kind, sources, pair, tags, files, parent=None):
    """dig() plus its ledger row (rounds, models, tokens, cost, seconds). Returns the row.
    A ledger write failure is reported in the terminal, never at the cost of the insight."""
    _tl.calls, trail, t0 = [], [], time.monotonic()
    try:
        insight, score = dig(a, b, trail)
        calls = _tl.calls
    finally:
        _tl.calls = None
    costs = [c["cost"] for c in calls if isinstance(c.get("cost"), (int, float))]
    row = {
        "dig": uuid.uuid4().hex[:12], "ts": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "kind": kind, "parent": parent, "pair": pair, "tags": tags, "files": files,
        "sources": sources, "insight": insight, "score": score, "rounds": trail,
        "models": sorted({c["model"] for c in calls}), "calls": len(calls),
        "tokens_in": sum(c["in"] or 0 for c in calls),
        "tokens_out": sum(c["out"] or 0 for c in calls),
        "cost": round(sum(costs), 6) if costs else None,
        "seconds": round(time.monotonic() - t0, 1),
    }
    try:
        ledger_add(row)
    except OSError:
        traceback.print_exc()
    return row


def brief(s):
    return {k: s[k] for k in ("file", "tag", "label")}


# ---------- http ----------

def need(body, key, kind=str):
    """A required request field of the right type, or a BadRequest."""
    if key not in body:
        raise BadRequest(f"missing field: {key}")
    if not isinstance(body[key], kind):
        raise BadRequest(f"field {key} must be {kind.__name__}")
    return body[key]


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
        elif self.path == "/api/stats":
            self._json(ledger_stats())
        elif self.path == "/api/last":
            self._json(ledger_last())
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
            try:
                length = int(self.headers.get("Content-Length", 0))
            except ValueError:
                raise BadRequest("bad Content-Length") from None
            if not 0 <= length <= MAX_BODY:  # a negative length makes read() wait for EOF
                raise BadRequest("request body too large")
            body = json.loads(self.rfile.read(length)) if length else {}
            if not isinstance(body, dict):
                raise BadRequest("body must be a JSON object")
            if self.path == "/api/save":
                text = need(body, "text").strip()
                if not text:
                    raise BadRequest("Nothing to save.")
                tag, label = classify(text)
                name = save_source(text, tag, label)
                self._json({"file": name, "tag": tag, "label": label, "tags": TAGS,
                            "clipped": len(text) > CLIP})
            elif self.path == "/api/retag":
                if need(body, "tag") not in TAGS:
                    raise BadRequest("Unknown tag.")
                set_tag(need(body, "file"), body["tag"])
                self._json({"ok": True})
            elif self.path == "/api/pick":
                a, b = pick_pair()
                self._json({
                    "a": {k: a[k] for k in ("file", "tag", "label")},
                    "b": {k: b[k] for k in ("file", "tag", "label")},
                    "tags": TAGS,
                })
            elif self.path == "/api/insight":
                a = load_source(need(body, "a"))
                b = load_source(need(body, "b"))
                row = logged_dig(a, b, "pair", [brief(a), brief(b)],
                                 f"{a['label']} × {b['label']}", [a["tag"], b["tag"]],
                                 [a["file"], b["file"]])
                self._json({"insight": row["insight"], "score": row["score"], "dig": row["dig"]})
            elif self.path == "/api/chain":
                exclude = body.get("exclude", [])
                if not isinstance(exclude, list):
                    raise BadRequest("field exclude must be list")
                c = pick_third(exclude)
                seed = {
                    "tag": "insight",
                    "label": "a previously dug insight",
                    "text": need(body, "insight"),
                }
                parent = body.get("dig")
                if parent is not None and not (isinstance(parent, str) and DIG_ID.fullmatch(parent)):
                    raise BadRequest("dig must be a dig id")
                prev = ledger_state()[0].get(parent, {})
                row = logged_dig(
                    seed, c, "chain",
                    [{"tag": "insight", "label": "previous insight"}, brief(c)],
                    f"{prev.get('pair', 'previous insight')} ⛓ {c['label']}",
                    [*prev.get("tags", []), c["tag"]], [*prev.get("files", []), c["file"]],
                    parent)
                self._json({"insight": row["insight"], "score": row["score"],
                            "dig": row["dig"], "source": brief(c), "tags": TAGS})
            elif self.path == "/api/filter":
                self._json({"gates": run_filter(need(body, "insight"))})
            elif self.path == "/api/keep":
                dig_id = body.get("dig")
                why = clean_why(body.get("why", ""))
                p = keep(need(body, "insight"), body.get("score"), need(body, "pair"),
                         body.get("tags", []), body.get("files", []), dig_id)
                if dig_id:
                    try:
                        ledger_add({"dig": dig_id, "grade": "keep", "why": why, "note": p.name,
                                    "ts": time.strftime("%Y-%m-%dT%H:%M:%S")})
                    except OSError:
                        traceback.print_exc()
                self._json({"ok": True, "note": p.name})
            elif self.path == "/api/grade":
                grade_dig(need(body, "dig"), need(body, "grade"), body.get("why", ""))
                self._json({"ok": True, **ledger_stats()})
            else:
                self._json({"error": "not found"}, 404)
        # 4xx for what the caller did, 502 for what OpenRouter did, 500 only for bugs
        except NotReady as e:
            self._json({"error": str(e)}, 409)
        except NoSuchSource as e:
            self._json({"error": str(e)}, 404)
        except (BadRequest, json.JSONDecodeError, UnicodeDecodeError) as e:
            self._json({"error": str(e)}, 400)
        except RuntimeError as e:  # ai() gave up
            self._json({"error": str(e)}, 502)
        except Exception:
            traceback.print_exc()  # the UI gets no internals; the terminal gets the trace
            self._json({"error": "internal error — see the server terminal"}, 500)

    def log_message(self, *args):
        pass  # quiet


if __name__ == "__main__":
    load_env()
    if not os.environ.get("OPENROUTER_API_KEY"):
        raise SystemExit("Set OPENROUTER_API_KEY first.")
    print(f"Idea Digger → http://localhost:{PORT}  (model: {model_name()})")
    ThreadingHTTPServer(("127.0.0.1", PORT), Handler).serve_forever()

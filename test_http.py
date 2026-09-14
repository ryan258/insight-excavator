#!/usr/bin/env python3
"""Self-check for the HTTP layer: every endpoint, plus the cross-origin guard.

    python3 test_http.py

No network and no model — server.ai is replaced with a scripted stub, and
SOURCES/vault point at a temp dir.
"""
import json
import os
import tempfile
import threading
import urllib.error
import urllib.request
from http.server import ThreadingHTTPServer
from pathlib import Path

os.environ.setdefault("OPENROUTER_API_KEY", "test-key")
import server  # noqa: E402

# what the stub answers, keyed by a phrase in the prompt
REPLIES = [
    ("filing a text source", "TAG: essays\nLABEL: a test source"),
    ("non-obvious connection", "the connection"),
    ("Score this insight", "SCORE: 9\nWHY: NONE\nREPLACEMENT: NONE"),
    ("three-gate filter", "REVEAL: PASS — yes\nBUILD: FAIL — no\nDELIVER: PASS — sure"),
]


def fake_ai(prompt, tries=3):
    for needle, reply in REPLIES:
        if needle in prompt:
            return reply
    raise AssertionError(f"unexpected prompt: {prompt[:80]}")


def post(base, path, body, origin=None):
    req = urllib.request.Request(
        base + path, data=json.dumps(body).encode(),
        headers={"Content-Type": "application/json",
                 **({"Origin": origin} if origin else {})},
    )
    try:
        with urllib.request.urlopen(req) as r:
            return r.status, json.loads(r.read())
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read())


def main(tmp):
    server.SOURCES = tmp / "sources"
    server.SOURCES.mkdir()
    server.vault_dir = lambda: tmp / "vault"
    server.ai = fake_ai

    httpd = ThreadingHTTPServer(("127.0.0.1", 0), server.Handler)
    threading.Thread(target=httpd.serve_forever, daemon=True).start()
    # the Origin guard compares against server.PORT, so point it at the test port
    server.PORT = httpd.server_address[1]
    base = f"http://127.0.0.1:{server.PORT}"
    try:
        # the page itself is served, and nothing else is
        with urllib.request.urlopen(base + "/") as r:
            assert b"<title>Idea Digger</title>" in r.read(), "index.html not served"
        try:
            urllib.request.urlopen(base + "/nope")
            raise AssertionError("unknown GET should 404")
        except urllib.error.HTTPError as e:
            assert e.code == 404, e.code

        # a browser on another site cannot POST here, but curl (no Origin) can
        status, body = post(base, "/api/save", {"text": "x"}, origin="http://evil.example")
        assert status == 403 and "cross-origin" in body["error"], (status, body)
        # nothing saved yet, so there are not two tags to dig across
        status, body = post(base, "/api/pick", {})
        assert status == 500 and "at least 2" in body["error"], body

        status, _ = post(base, "/api/save", {"text": "x"}, origin=base)
        assert status == 200, "same-origin POST must be allowed"

        # save classifies and writes a file; the whole tag set comes back for the dropdown
        status, a = post(base, "/api/save", {"text": "first source"})
        assert status == 200 and a["tag"] == "essays" and a["label"] == "a test source", a
        assert a["tags"] == server.TAGS, a
        assert (server.SOURCES / a["file"]).exists()

        # empty text is refused rather than filed
        status, body = post(base, "/api/save", {"text": "   "})
        assert status == 500 and "Nothing to save" in body["error"], body

        # retag rewrites the header and rejects anything outside the closed set
        status, _ = post(base, "/api/retag", {"file": a["file"], "tag": "commerce"})
        assert status == 200 and server.load_source(a["file"])["tag"] == "commerce"
        status, body = post(base, "/api/retag", {"file": a["file"], "tag": "made-up"})
        assert status == 500 and "Unknown tag" in body["error"], body

        _, b = post(base, "/api/save", {"text": "second source"})
        post(base, "/api/retag", {"file": b["file"], "tag": "essays"})
        status, pair = post(base, "/api/pick", {})
        assert status == 200 and pair["a"]["tag"] != pair["b"]["tag"], pair
        assert "text" not in pair["a"], "pick must not ship whole source bodies"

        # the dig loop, then the three things you can do with what it returns
        status, dug = post(base, "/api/insight", {"a": a["file"], "b": b["file"]})
        assert status == 200 and dug == {"insight": "the connection", "score": 9}, dug

        status, ch = post(base, "/api/chain",
                          {"insight": "seed", "exclude": ["commerce", "essays"]})
        assert status == 500 and "outside the original pair" in ch["error"], ch
        status, ch = post(base, "/api/chain", {"insight": "seed", "exclude": ["essays"]})
        assert status == 200 and ch["source"]["tag"] == "commerce", ch

        status, f = post(base, "/api/filter", {"insight": "the connection"})
        assert status == 200, f
        assert [g["verdict"] for g in f["gates"]] == ["PASS", "FAIL", "PASS"], f

        status, k = post(base, "/api/keep",
                         {"insight": "the connection", "score": 9, "pair": "one × two"})
        assert status == 200 and k["note"].endswith("-the-connection.md"), k
        note = (tmp / "vault" / k["note"]).read_text()
        assert "score: 9" in note and "[[one]] + [[two]]" in note, note

        status, body = post(base, "/api/nope", {})
        assert status == 404, (status, body)
    finally:
        httpd.shutdown()
    print("ok")


if __name__ == "__main__":
    with tempfile.TemporaryDirectory() as d:
        main(Path(d))

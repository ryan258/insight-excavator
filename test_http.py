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


def fake_ai(prompt, tries=3, **kw):
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


def get(base, path):
    with urllib.request.urlopen(base + path) as r:
        return r.status, json.loads(r.read())


def main(tmp):
    server.SOURCES = tmp / "sources"
    server.SOURCES.mkdir()
    server.LEDGER = tmp / "digs.jsonl"   # never the real ledger
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
        assert status == 409 and "at least 2" in body["error"], body

        status, _ = post(base, "/api/save", {"text": "x"}, origin=base)
        assert status == 200, "same-origin POST must be allowed"

        # a negative or oversized Content-Length is refused up front, not waited on
        import socket
        for cl in ("-1", str(server.MAX_BODY + 1)):
            with socket.create_connection(("127.0.0.1", server.PORT), timeout=5) as c:
                c.sendall(f"POST /api/save HTTP/1.0\r\nContent-Length: {cl}\r\n\r\n".encode())
                reply = b""
                while chunk := c.recv(4096):   # headers and body can arrive separately
                    reply += chunk
            assert reply.startswith(b"HTTP/1.0 400") and b"too large" in reply, (cl, reply)

        # save classifies and writes a file; the whole tag set comes back for the dropdown
        status, a = post(base, "/api/save", {"text": "first source"})
        assert status == 200 and a["tag"] == "essays" and a["label"] == "a test source", a
        assert a["tags"] == server.TAGS, a
        assert (server.SOURCES / a["file"]).exists()

        # empty text is refused rather than filed
        status, body = post(base, "/api/save", {"text": "   "})
        assert status == 400 and "Nothing to save" in body["error"], body
        # caller mistakes are 400s that name the problem, never a KeyError or a 500
        status, body = post(base, "/api/save", {})
        assert status == 400 and "missing field: text" in body["error"], body
        status, body = post(base, "/api/save", {"text": 5})
        assert status == 400, body

        # retag rewrites the header and rejects anything outside the closed set
        status, _ = post(base, "/api/retag", {"file": a["file"], "tag": "commerce"})
        assert status == 200 and server.load_source(a["file"])["tag"] == "commerce"
        status, body = post(base, "/api/retag", {"file": a["file"], "tag": "made-up"})
        assert status == 400 and "Unknown tag" in body["error"], body
        status, body = post(base, "/api/retag", {"file": "nope.txt", "tag": "essays"})
        assert status == 404, (status, body)

        # a retag must not strip an imported file's provenance headers
        imported = server.SOURCES / "claude-abc.txt"
        imported.write_text("tag: essays\nlabel: L\nsource: claude\nconv: abc\n---\nbody\n")
        post(base, "/api/retag", {"file": imported.name, "tag": "commerce"})
        assert imported.read_text() == "tag: commerce\nlabel: L\nsource: claude\nconv: abc\n---\nbody\n"
        imported.unlink()

        _, b = post(base, "/api/save", {"text": "second source"})
        post(base, "/api/retag", {"file": b["file"], "tag": "essays"})
        status, pair = post(base, "/api/pick", {})
        assert status == 200 and pair["a"]["tag"] != pair["b"]["tag"], pair
        assert "text" not in pair["a"], "pick must not ship whole source bodies"
        assert pair["tags"] == server.TAGS, "the UI needs the tag set for its dropdown"

        # a retag shows up in the very next picks — the by_tag cache must not go stale.
        # Only two tags exist (essays, commerce), so every pick holds one commerce
        # source; across 30 picks `b` turns up ~15 times, and never as 'essays'.
        post(base, "/api/retag", {"file": b["file"], "tag": "commerce"})
        for _ in range(30):
            _, p = post(base, "/api/pick", {})
            for s in (p["a"], p["b"]):
                assert s["file"] != b["file"] or s["tag"] == "commerce", f"stale cache: {s}"
        post(base, "/api/retag", {"file": b["file"], "tag": "essays"})

        # the dig loop, then the three things you can do with what it returns
        status, dug = post(base, "/api/insight", {"a": a["file"], "b": b["file"]})
        assert status == 200 and (dug["insight"], dug["score"]) == ("the connection", 9), dug
        assert len(dug["dig"]) == 12, dug

        status, ch = post(base, "/api/chain",
                          {"insight": "seed", "exclude": ["commerce", "essays"]})
        assert status == 409 and "outside the original pair" in ch["error"], ch
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

        # the note records which source files it came from, and keep() refuses bad input
        status, k = post(base, "/api/keep", {"insight": "traceable", "score": 8, "pair": "a × b",
                                             "tags": ["essays"], "files": [a["file"], b["file"]]})
        assert status == 200, k

        # the ledger: every dig is recorded, grading is idempotent per dig, keep grades "keep"
        status, ch2 = post(base, "/api/chain", {"insight": "seed", "exclude": ["essays"],
                                                "dig": dug["dig"]})
        assert status == 200, ch2
        status, last = get(base, "/api/last")
        row = last["dig"]
        assert row["dig"] == ch2["dig"] and row["kind"] == "chain" and row["parent"] == dug["dig"], row
        assert " ⛓ " in row["pair"] and row["files"][:2] == [a["file"], b["file"]], row
        assert row["rounds"] == [9] and last["grade"] is None, row
        status, st = get(base, "/api/stats")
        assert st["digs"] == 3 and st["graded"] == 0 and st["target"] == server.GATE, st

        status, g = post(base, "/api/grade", {"dig": dug["dig"], "grade": "skip", "why": "obvious\nx"})
        assert status == 200 and g["skip"] == 1 and g["graded"] == 1, g
        assert server.ledger_state()[1][dug["dig"]]["why"] == "obvious x", "why is one flat line"
        status, bad = post(base, "/api/grade", {"dig": dug["dig"], "grade": "skip", "why": 5})
        assert status == 400, bad
        status, g = post(base, "/api/grade", {"dig": dug["dig"], "grade": "maybe"})
        assert g["maybe"] == 1 and g["skip"] == 0 and g["graded"] == 1, "a re-grade replaces, not adds"
        for bad, want in (({"dig": dug["dig"], "grade": "keep"}, 400), ({"dig": dug["dig"], "grade": "x"}, 400),
                          ({"dig": "0" * 12, "grade": "skip"}, 404), ({"dig": "../x", "grade": "skip"}, 404),
                          ({"grade": "skip"}, 400)):
            status, body = post(base, "/api/grade", bad)
            assert status == want, (bad, status, body)

        status, k2 = post(base, "/api/keep", {"insight": "ledgered", "score": 9, "pair": "a × b",
                                              "dig": ch2["dig"], "why": "usable premise"})
        assert status == 200 and f"dig: {ch2['dig']}" in (tmp / "vault" / k2["note"]).read_text(), k2
        status, k3 = post(base, "/api/keep", {"insight": "x", "pair": "a", "dig": "nope"})
        assert status == 400, k3
        status, st = get(base, "/api/stats")
        assert st["keep"] == 1 and st["maybe"] == 1 and st["graded"] == 2, st
        assert server.ledger_state()[1][ch2["dig"]]["why"] == "usable premise"
        lines = server.LEDGER.read_text().splitlines()
        server.LEDGER.write_text("\n".join(lines) + '\n{"torn": ')   # a kill mid-append
        assert get(base, "/api/stats")[1]["digs"] == 3, "a torn last line must not break the ledger"
        assert f"sources: [{a['file']}, {b['file']}]" in (tmp / "vault" / k["note"]).read_text()
        for bad in ({"score": "8\ninjected: yes"}, {"score": 11}, {"score": True},
                    {"tags": ["made-up"]}, {"tags": [1]}, {"files": ["../x.txt"]}):
            status, body = post(base, "/api/keep",
                                {"insight": "x", "score": 7, "pair": "a × b", **bad})
            assert status == 400, (bad, status, body)
        status, body = post(base, "/api/keep", {"insight": "x"})
        assert status == 400 and "missing field: pair" in body["error"], body

        # not JSON, and not an object
        for raw in (b"{nope", b"[1, 2]"):
            req = urllib.request.Request(base + "/api/save", data=raw)
            try:
                urllib.request.urlopen(req)
                raise AssertionError("bad JSON should be refused")
            except urllib.error.HTTPError as e:
                assert e.code == 400, e.code

        # an upstream failure is a 502, not a 500 — the server did nothing wrong
        real_ai = server.ai
        server.ai = lambda prompt, tries=3, **kw: (_ for _ in ()).throw(RuntimeError("OpenRouter HTTP 402: no credits"))
        status, body = post(base, "/api/filter", {"insight": "x"})
        server.ai = real_ai
        assert status == 502 and "402" in body["error"], (status, body)

        status, body = post(base, "/api/nope", {})
        assert status == 404, (status, body)
    finally:
        httpd.shutdown()
    print("ok")


if __name__ == "__main__":
    with tempfile.TemporaryDirectory() as d:
        main(Path(d))

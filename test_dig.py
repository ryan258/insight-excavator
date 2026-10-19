#!/usr/bin/env python3
"""Self-check for the domain logic the HTTP test only stubs: dig(), classify(),
run_filter(), slugify(), set_tag(), keep() validation, and chain picking.

    python3 test_dig.py

No network and no model — server.ai is replaced with a scripted sequence.
"""
import os
import tempfile
from pathlib import Path

os.environ.setdefault("OPENROUTER_API_KEY", "test-key")
import server  # noqa: E402

A = {"tag": "essays", "label": "a", "text": "alpha"}
B = {"tag": "commerce", "label": "b", "text": "beta"}


def script(*replies):
    """Make server.ai answer with `replies` in order; return the prompts it saw."""
    seen, it = [], iter(replies)

    def fake(prompt, tries=3, **kw):
        seen.append(prompt)
        return next(it)

    server.ai = fake
    return seen


def judge(score, rep="NONE"):
    return f"SCORE: {score}\nWHY: x\nREPLACEMENT: {rep}"


def test_dig():
    # clears the bar on the first judge: two calls, original insight kept
    seen = script("first", judge(8))
    assert server.dig(A, B) == ("first", 8) and len(seen) == 2

    # a rewrite that scores WORSE must not replace a better earlier insight
    script("first", judge(6, "second"), judge(4, "third"), judge(5))
    assert server.dig(A, B) == ("first", 6), "best-scoring insight wins, not the last"

    # a rewrite that improves is returned, with its own score
    script("first", judge(5, "second"), judge(8))
    assert server.dig(A, B) == ("second", 8)

    # ties keep the earlier insight
    script("first", judge(6, "second"), judge(6, "third"), judge(6))
    assert server.dig(A, B) == ("first", 6)

    # no usable replacement: stop instead of re-scoring the same text (2 calls, not 4)
    seen = script("first", judge(5, "NONE"))
    assert server.dig(A, B) == ("first", 5) and len(seen) == 2

    # unparseable or out-of-range scores are unscored, never faked
    script("first", "gibberish with no score line", "SCORE: nope")
    out, score = server.dig(A, B)
    assert score is None, score
    script("first", judge(42, "NONE"))
    assert server.dig(A, B) == ("first", None)

    # an earlier real score beats a later unscored rewrite
    script("first", judge(6, "second"), "no format at all", "still none")
    assert server.dig(A, B) == ("first", 6)

    # one huge source must not become one huge prompt
    seen = script("x", judge(9))
    server.dig({**A, "text": "z" * 50_000}, B)
    assert len(seen[0]) < 2 * server.CLIP + 1000 and "[…truncated]" in seen[0]


def test_classify_and_filter_parse():
    script("TAG: Commerce\nLABEL: Etsy mug line")
    assert server.classify("t") == ("commerce", "Etsy mug line"), "tag is case-folded"
    script("TAG: not-a-real-tag\nLABEL: x")
    assert server.classify("t")[0] == "other", "unknown tag falls back to other"
    script("nothing parseable")
    assert server.classify("t") == ("other", "untitled")

    script("REVEAL: PASS — yes\nBUILD: FAIL: no\nDELIVER garbled")
    got = server.run_filter("i")
    assert [g["verdict"] for g in got] == ["PASS", "FAIL", "?"], got
    assert got[2]["why"] == "could not parse filter output"


def test_markdown_wrapped_replies():
    # models bold or bullet the keys they were told to emit; none of these may fall back
    script("**TAG:** Essays\n**LABEL:** my label")
    assert server.classify("t") == ("essays", "my label")
    script("- Tag: `commerce`\n- Label: **mug line**")
    assert server.classify("t") == ("commerce", "mug line")
    script("**REVEAL:** PASS — a\n**BUILD**: fail - b\n> DELIVER: **FAIL** c")
    got = server.run_filter("i")
    assert [g["verdict"] for g in got] == ["PASS", "FAIL", "FAIL"], got
    assert got[1]["why"] == "b" and got[2]["why"] == "c", got
    script("first", "**SCORE:** 8\n**WHY:** NONE\n**REPLACEMENT:** NONE")
    assert server.dig(A, B) == ("first", 8)
    script("first", "score: 5\nWhy: x\n**Replacement:** deeper\nsecond line", judge(8))
    assert server.dig(A, B) == ("deeper\nsecond line", 8)
    assert server.field("no keys here", "TAG") is None


def test_atomic_write(tmp):
    server.SOURCES = tmp
    f = tmp / "a.txt"
    f.write_text("tag: essays\nlabel: L\n---\nbody")
    real = os.replace
    try:
        os.replace = lambda *a: (_ for _ in ()).throw(OSError("killed"))
        try:
            server.set_tag(f.name, "commerce")
            raise AssertionError("expected OSError")
        except OSError:
            pass
    finally:
        os.replace = real
    assert f.read_text() == "tag: essays\nlabel: L\n---\nbody", "failed write touched the source"
    assert [p.name for p in tmp.iterdir()] == ["a.txt"], "temp file left behind"


def test_model_tiers_and_env(tmp):
    real, m = server.config, os.environ.pop("M", None)
    try:
        server.config = lambda: {"model": "strong", "cheap_model": "weak"}
        assert server.model_name() == "strong" and server.model_name(cheap=True) == "weak"
        server.config = lambda: {"model": "strong"}
        assert server.model_name(cheap=True) == "strong", "no cheap_model falls back to model"
        os.environ["M"] = "forced"
        assert server.model_name(cheap=True) == "forced", "M overrides every call"
    finally:
        server.config = real
        os.environ.pop("M", None)
        if m:
            os.environ["M"] = m

    # .env fills gaps but never overrides what the shell already set
    real_root, server.ROOT = server.ROOT, tmp
    (tmp / ".env").write_text("# c\nDIGGER_T1=from-file\nDIGGER_T2=\"quoted\"\nDIGGER_T3=file\nbogus line\n")
    os.environ["DIGGER_T3"] = "shell"
    server.load_env()
    assert (os.environ["DIGGER_T1"], os.environ["DIGGER_T2"], os.environ["DIGGER_T3"]) == \
        ("from-file", "quoted", "shell")

    # config.json is local; without it the tracked example is used
    (tmp / "config.example.json").write_text('{"model": "ex"}')
    assert server.config() == {"model": "ex"}
    (tmp / "config.json").write_text('{"model": "mine"}')
    try:
        assert server.config() == {"model": "mine"}
    finally:
        server.ROOT = real_root


def test_logged_dig_and_ledger(tmp):
    server.LEDGER = tmp / "digs.jsonl"

    def fake(prompt, tries=3, **kw):
        server._tl.calls.append({"model": "m", "in": 10, "out": 5, "cost": 0.5})
        return judge(8) if "Score this" in prompt else "ins"

    server.ai = fake
    row = server.logged_dig(A, B, "pair", [], "a × b", ["essays", "commerce"], ["x.txt", "y.txt"])
    assert row["calls"] == 2 and row["tokens_in"] == 20 and row["tokens_out"] == 10, row
    assert row["cost"] == 1.0 and row["rounds"] == [8] and row["models"] == ["m"], row
    assert server._tl.calls is None, "per-request call log must be cleared"
    assert server.ledger_state()[0][row["dig"]]["insight"] == "ins"

    # no usage reported -> cost is unknown (None), not a faked 0
    server.ai = lambda prompt, tries=3, **kw: judge(8) if "Score this" in prompt else "ins"
    assert server.logged_dig(A, B, "pair", [], "p", [], [])["cost"] is None

    # a ledger that cannot be written must not cost the insight
    server.LEDGER = tmp / "no-such-dir" / "digs.jsonl"
    real_print, server.traceback.print_exc = server.traceback.print_exc, lambda: None
    try:
        assert server.logged_dig(A, B, "pair", [], "p", [], [])["insight"] == "ins"
    finally:
        server.traceback.print_exc = real_print


def test_dig_stops_when_over_budget():
    seen = script("first", judge(5, "second"), judge(9))
    real = server.DIG_BUDGET
    server.DIG_BUDGET = -1     # already out of time: one judge round, then return
    try:
        out = server.dig(A, B)
    finally:
        server.DIG_BUDGET = real
    assert out == ("first", 5) and len(seen) == 2, (out, len(seen))


def test_vault_parent_must_exist(tmp):
    server.vault_dir = lambda: tmp / "missing-parent" / "insights"
    try:
        server.keep("x", 7, "a × b")
        raise AssertionError("expected NotReady")
    except server.NotReady:
        pass
    assert not (tmp / "missing-parent").exists(), "keep must not build a wrong tree"


def test_slugify():
    assert server.slugify("Scaffolding is a tell.\nmore") == "scaffolding-is-a-tell"
    assert server.slugify("Café résumé: ñandú") == "cafe-resume-nandu"
    assert server.slugify("日本語の洞察") == "insight"
    assert server.slugify("one two three four five six seven eight nine ten") == \
        "one-two-three-four-five-six-seven-eight"


def test_set_tag_and_cache(tmp):
    server.SOURCES = tmp
    f = tmp / "claude-abc.txt"
    f.write_text("tag: essays\nlabel: L\nsource: claude\nconv: abc\n---\nbody\n")
    assert [s["tag"] for s in server.by_tag()["essays"]] == ["essays"]
    server.set_tag(f.name, "commerce")
    assert f.read_text() == "tag: commerce\nlabel: L\nsource: claude\nconv: abc\n---\nbody\n"
    assert "essays" not in server.by_tag(), "by_tag served a stale cache after set_tag"

    # a file with no tag header gains one rather than silently staying 'other'
    g = tmp / "notag.txt"
    g.write_text("label: L\n---\nbody")
    server.set_tag(g.name, "essays")
    assert server.load_source(g.name)["tag"] == "essays"

    # a path in the name cannot reach outside sources/
    try:
        server.set_tag("../escape.txt", "essays")
        raise AssertionError("traversal should not find a file")
    except FileNotFoundError:
        pass


def test_pick_third(tmp):
    server.SOURCES = tmp
    for i, tag in enumerate(["essays", "commerce"]):
        (tmp / f"{i}.txt").write_text(f"tag: {tag}\nlabel: L{i}\n---\nb")
    assert server.pick_third(["essays"])["tag"] == "commerce"
    try:
        server.pick_third(["essays", "commerce"])
        raise AssertionError("expected NotReady")
    except server.NotReady:
        pass


def test_keep_validation(vault):
    server.vault_dir = lambda: vault
    for bad in (dict(score="8\ninjected: yes"), dict(score=0), dict(score=11),
                dict(score=7.5), dict(score=True), dict(tags="essays"),
                dict(tags=["made-up"]), dict(tags=[3]), dict(files=["a/b.txt"]),
                dict(files=["a.md"]), dict(insight="   ")):
        kw = dict(insight="x", score=7, pair="a × b", tags=[], files=[])
        kw.update(bad)
        try:
            server.keep(**kw)
            raise AssertionError(f"accepted {bad}")
        except ValueError:
            pass
    assert not list(vault.glob("*.md")), "a refused keep must not leave a note"

    p = server.keep("Seen twice.", 9, "a × b", ["essays"], ["x.txt", "x.txt", "y.txt"])
    assert "sources: [x.txt, y.txt]" in p.read_text(), p.read_text()


def main():
    test_dig()
    test_classify_and_filter_parse()
    test_markdown_wrapped_replies()
    test_dig_stops_when_over_budget()
    with tempfile.TemporaryDirectory() as d:
        test_model_tiers_and_env(Path(d))
    with tempfile.TemporaryDirectory() as d:
        test_logged_dig_and_ledger(Path(d))
    with tempfile.TemporaryDirectory() as d:
        test_vault_parent_must_exist(Path(d))
    test_slugify()
    with tempfile.TemporaryDirectory() as d:
        test_atomic_write(Path(d))
    with tempfile.TemporaryDirectory() as d:
        test_set_tag_and_cache(Path(d))
    with tempfile.TemporaryDirectory() as d:
        test_pick_third(Path(d))
    with tempfile.TemporaryDirectory() as d:
        test_keep_validation(Path(d))
    print("ok")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Self-check for vault notes and tag-weighted sampling. Run: python3 test_keep.py"""
import os
import random
import tempfile
from pathlib import Path

os.environ.setdefault("OPENROUTER_API_KEY", "test-key")
import server  # noqa: E402


def test_note(vault):
    server.vault_dir = lambda: vault
    p = server.keep("Scaffolding is a tell.\n\n---\n\nIt shows the seams.", 8,
                    "the map is not the territory × slow tools", ["essays", "ai-practice"])
    text = p.read_text()
    assert p.name.endswith("-scaffolding-is-a-tell.md"), p.name
    assert "score: 8" in text, text
    assert "tags: [insight, essays, ai-practice]" in text, text
    assert "[[the map is not the territory]] + [[slow tools]]" in text, text
    assert text.startswith("---\n") and text.splitlines().count("---") == 2, \
        f"a body '---' must not close the frontmatter early:\n{text}"

    # same insight twice in a day gets its own file, never an overwrite
    q = server.keep("Scaffolding is a tell.", 8, "a × b", ["essays"])
    assert q != p and q.exists() and p.exists(), (p, q)

    # unscored keeps omit the field rather than writing null
    r = server.keep("No score here.", None, "a × b", [])
    assert "score:" not in r.read_text() and "tags: [insight]" in r.read_text()

    # a chained pair links all three sources
    c = server.keep("Chained.", 7, "a × b ⛓ c", [])
    assert "[[a]] + [[b]] + [[c]]" in c.read_text(), c.read_text()

    # brackets in a label would break the wikilink
    b = server.keep("Bracket.", 7, "a [weird] label × b", [])
    assert "[[a weird label]]" in b.read_text(), b.read_text()


def test_sampling():
    # the real corpus shape: ai-practice dwarfs brand-frameworks 1128:82
    groups = {"ai-practice": [0] * 1128, "creative-projects": [0] * 472,
              "content-topics": [0] * 263, "essays": [0] * 101,
              "brand-frameworks": [0] * 82, "other": [0] * 1}
    random.seed(0)
    hits = dict.fromkeys(groups, 0)
    for _ in range(20000):
        t1, t2 = server.two_tags(groups)
        assert t1 != t2, "a pair must come from two different tags"
        hits[t1] += 1
        hits[t2] += 1

    # a lone source in a fresh tag must not dominate — uniform-over-tags gave it 33%
    assert hits["other"] / 40000 < 0.05, f"size-1 tag still loud: {hits}"
    # and the big tag must not take over either, as uniform-over-sources would
    assert 0.25 < hits["ai-practice"] / 40000 < 0.45, f"big tag off: {hits}"
    # per-source odds: the worst imbalance should be ~sqrt(1128/82)=3.7x, not 13.8x
    per = {t: hits[t] / len(groups[t]) for t in ("ai-practice", "brand-frameworks")}
    ratio = per["brand-frameworks"] / per["ai-practice"]
    assert 2.5 < ratio < 5, f"per-source imbalance {ratio:.1f}x outside sqrt range"


def main():
    with tempfile.TemporaryDirectory() as d:
        test_note(Path(d) / "insights")
    test_sampling()
    print("ok")


if __name__ == "__main__":
    main()

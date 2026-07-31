#!/usr/bin/env python3
"""Self-check for import.py's parsers. No API calls. Run: python3 test_import.py

These cover the traps documented in docs/research/export-format-anatomy.md —
the ones that silently produce a plausible-but-wrong transcript.
"""
import importlib
import io
import json
import os
import sys
from pathlib import Path

os.environ.setdefault("OPENROUTER_API_KEY", "test-key")
sys.path.insert(0, str(Path(__file__).parent))
imp = importlib.import_module("import")  # 'import' is a keyword


class DribbleFP:
    """A file object that returns a few bytes at a time, so raw_decode has to
    cope with objects split across reads."""

    def __init__(self, data, chunk=7):
        self.buf, self.chunk = data, chunk

    def read(self, _n=None):
        out, self.buf = self.buf[:self.chunk], self.buf[self.chunk:]
        return out


def test_stream_array():
    items = [{"a": 1}, {"b": [1, 2, {"c": "]"}]}, {"d": "text, with, commas"}]
    got = list(imp.stream_array(DribbleFP(json.dumps(items).encode())))
    assert got == items, got
    # a string containing ']' must not end the array early
    assert got[1]["b"][2]["c"] == "]"
    assert list(imp.stream_array(io.BytesIO(b"[]"))) == []


def test_chatgpt_walk_prunes_dead_branches():
    """Order comes from walking parent up from current_node — not mapping order,
    which holds abandoned regenerations."""
    conv = {
        "current_node": "n3",
        "mapping": {
            "root": {"message": None, "parent": None, "children": ["n1"]},
            "n1": {"parent": "root", "children": ["n2", "dead"],
                   "message": {"author": {"role": "user"}, "recipient": "all",
                               "content": {"content_type": "text", "parts": ["first"]}}},
            "dead": {"parent": "n1", "children": [],
                     "message": {"author": {"role": "assistant"}, "recipient": "all",
                                 "content": {"content_type": "text", "parts": ["ABANDONED"]}}},
            "n2": {"parent": "n1", "children": ["n3"],
                   "message": {"author": {"role": "assistant"}, "recipient": "all",
                               "content": {"content_type": "text", "parts": ["second"]}}},
            "n3": {"parent": "n2", "children": [],
                   "message": {"author": {"role": "user"}, "recipient": "all",
                               "content": {"content_type": "text", "parts": ["third"]}}},
        },
    }
    got = imp.chatgpt_messages(conv)
    assert got == [("user", "first"), ("assistant", "second"), ("user", "third")], got
    assert "ABANDONED" not in json.dumps(got), "off-path branch leaked in"


def test_chatgpt_drops_tools_system_and_keeps_multimodal_strings():
    def node(nid, parent, role, ct, parts, recipient="all"):
        return {nid: {"parent": parent, "children": [],
                      "message": {"author": {"role": role}, "recipient": recipient,
                                  "content": {"content_type": ct, "parts": parts}}}}
    mapping = {"root": {"message": None, "parent": None, "children": []}}
    mapping.update(node("a", "root", "system", "text", ["SYSTEM"]))
    mapping.update(node("b", "a", "assistant", "text", ["TOOLCALL"], recipient="python"))
    mapping.update(node("c", "b", "assistant", "code", ["CODE"]))
    mapping.update(node("d", "c", "user", "multimodal_text",
                        ["kept", {"content_type": "image_asset_pointer"}]))
    mapping.update(node("e", "d", "user", "text", ["   "]))
    got = imp.chatgpt_messages({"current_node": "e", "mapping": mapping})
    assert got == [("user", "kept")], got


def test_claude_joins_text_blocks_and_ignores_dot_text():
    """.text is a flattened render contaminated with chain-of-thought."""
    conv = {"chat_messages": [
        {"sender": "human", "text": "IGNORED",
         "content": [{"type": "text", "text": "question"}]},
        {"sender": "assistant", "text": "thinking leaked in here",
         "content": [
             {"type": "thinking", "text": "SECRET REASONING"},
             {"type": "text", "text": "part one "},
             {"type": "tool_use", "text": "TOOL"},
             {"type": "text", "text": "part two"},
         ]},
        {"sender": "human", "text": "populated",
         "content": [{"type": "text", "text": "   "}]},  # whitespace-only: drop
    ]}
    got = imp.claude_messages(conv)
    assert got == [("user", "question"), ("assistant", "part one part two")], got
    blob = json.dumps(got)
    for leak in ("SECRET REASONING", "TOOL", "IGNORED", "populated"):
        assert leak not in blob, f"{leak} leaked in"


def test_one_line_flattens_header_values():
    # a newline in a title would forge a header field or a body separator
    assert imp.one_line("a\nb\n---\nc") == "a b --- c"
    assert len(imp.one_line("x" * 500)) == 200


def test_load_seen(tmp: Path):
    log = tmp / "seen.log"
    log.write_text("chatgpt abc KEEP\nclaude def DROP\n\nbad\n")
    assert imp.load_seen(log) == {"abc", "def"}
    assert imp.load_seen(tmp / "nope.log") == set()


def main():
    import tempfile
    test_stream_array()
    test_chatgpt_walk_prunes_dead_branches()
    test_chatgpt_drops_tools_system_and_keeps_multimodal_strings()
    test_claude_joins_text_blocks_and_ignores_dot_text()
    test_one_line_flattens_header_values()
    with tempfile.TemporaryDirectory() as d:
        test_load_seen(Path(d))
    print("ok")


if __name__ == "__main__":
    main()

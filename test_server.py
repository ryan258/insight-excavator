#!/usr/bin/env python3
"""Self-check for server.ai()'s null-content handling. Run: python3 test_server.py"""
import io
import json
import os
import urllib.error

os.environ.setdefault("OPENROUTER_API_KEY", "test-key")
import server  # noqa: E402


class FakeResponse(io.BytesIO):
    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False


def fake_urlopen(bodies):
    """Return a urlopen that yields each body in turn, and counts calls."""
    calls = []

    def _open(req, timeout=None):
        calls.append(1)
        return FakeResponse(json.dumps(bodies[len(calls) - 1]).encode())

    return _open, calls


NULL = {"choices": [{"message": {"content": None}, "finish_reason": "length"}]}
OK = {"choices": [{"message": {"content": "  hello  "}}]}


def main():
    real = server.urllib.request.urlopen
    try:
        # a null response is retried, and the next good one wins
        server.urllib.request.urlopen, calls = fake_urlopen([NULL, NULL, OK])
        assert server.ai("p") == "hello", "should retry past nulls and strip"
        assert len(calls) == 3, f"expected 3 attempts, got {len(calls)}"

        # persistent nulls raise something that names the cause
        server.urllib.request.urlopen, calls = fake_urlopen([NULL, NULL, NULL])
        try:
            server.ai("p")
            raise AssertionError("should have raised on persistent null content")
        except RuntimeError as e:
            assert "no content" in str(e), e
            assert "length" in str(e), f"finish_reason should be surfaced: {e}"
        assert len(calls) == 3, f"expected 3 attempts, got {len(calls)}"

        # a normal response still costs exactly one call
        server.urllib.request.urlopen, calls = fake_urlopen([OK])
        assert server.ai("p") == "hello"
        assert len(calls) == 1, f"no retry on success, got {len(calls)}"

        # an error payload with no choices is still reported, not retried
        server.urllib.request.urlopen, calls = fake_urlopen([{"error": {"message": "nope"}}])
        try:
            server.ai("p")
            raise AssertionError("should have raised on a payload with no choices")
        except RuntimeError as e:
            assert "nope" in str(e), e
        assert len(calls) == 1, "a malformed payload should not be retried"
    finally:
        server.urllib.request.urlopen = real
    print("ok")


if __name__ == "__main__":
    main()

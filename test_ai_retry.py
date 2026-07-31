"""Check that ai() retries the transient failures and gives up on the rest.

    python3 test_ai_retry.py

No network: urlopen is swapped for a scripted list of responses.
"""
import io
import json
import os
import urllib.request

os.environ.setdefault("OPENROUTER_API_KEY", "test")
import server


class _Resp(io.BytesIO):
    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False


def run(responses):
    """Feed ai() a scripted sequence; return (result_or_error, calls_made)."""
    calls = []

    def fake_urlopen(req, timeout=None):
        calls.append(1)
        return _Resp(json.dumps(responses[len(calls) - 1]).encode())

    real_urlopen, real_sleep = urllib.request.urlopen, server.time.sleep
    urllib.request.urlopen = fake_urlopen
    server.time.sleep = lambda s: None          # don't actually back off
    try:
        return server.ai("hi"), len(calls)
    except Exception as e:
        return e, len(calls)
    finally:
        urllib.request.urlopen = real_urlopen
        server.time.sleep = real_sleep


ok = {"choices": [{"message": {"content": " hello "}}]}
null = {"choices": [{"message": {"content": None}}, ]}
err504 = {"error": {"code": 504, "message": "Upstream idle timeout exceeded"}}
err402 = {"error": {"code": 402, "message": "requires more credits"}}
err429 = {"error": {"code": 429, "message": "rate limited"}}

# a transient 504 is retried, and the next good response is returned
out, n = run([err504, ok])
assert out == "hello", out
assert n == 2, n

# 429 is retried too
out, n = run([err429, ok])
assert out == "hello" and n == 2, (out, n)

# 402 will never succeed — fail on the first call, do not burn retries
out, n = run([err402, ok])
assert isinstance(out, RuntimeError), out
assert n == 1, f"402 should not retry, made {n} calls"

# transient every time: give up after `tries`, and don't raise UnboundLocalError
out, n = run([err504, err504, err504])
assert isinstance(out, RuntimeError), out
assert "504" in str(out), out
assert n == 3, n

# the pre-existing content:null retry still works
out, n = run([null, ok])
assert out == "hello" and n == 2, (out, n)

print("ok — 5 checks passed")

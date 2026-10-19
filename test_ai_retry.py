"""Check that ai() retries the transient failures and gives up on the rest.

    python3 test_ai_retry.py

No network: urlopen is swapped for a scripted list of responses.
"""
import io
import json
import os
import urllib.error
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
        r = responses[len(calls) - 1]
        if isinstance(r, Exception):
            raise r
        return _Resp(r if isinstance(r, bytes) else json.dumps(r).encode())

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


def http(code, msg):
    """A real HTTP status, not a 200 carrying an error body."""
    return urllib.error.HTTPError(
        "u", code, msg, {}, io.BytesIO(json.dumps({"error": {"message": msg}}).encode())
    )

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

# an error payload with no code at all is reported, not retried
out, n = run([{"error": {"message": "nope"}}, ok])
assert isinstance(out, RuntimeError) and "nope" in str(out), out
assert n == 1, f"an uncoded error should not retry, made {n} calls"

# the pre-existing content:null retry still works
out, n = run([null, ok])
assert out == "hello" and n == 2, (out, n)

# persistent nulls raise after exhausting retries
out, n = run([null, null, null])
assert isinstance(out, RuntimeError) and "no content" in str(out), out
assert n == 3, f"persistent nulls should try 3 times, made {n} calls"


# the same rule applies to a real HTTP status: 429 is transient, 402 is not
out, n = run([http(429, "rate limited"), ok])
assert out == "hello", out
assert n == 2, f"HTTP 429 should be retried, made {n} calls"

out, n = run([http(503, "upstream down"), http(503, "upstream down"), ok])
assert out == "hello" and n == 3, (out, n)

out, n = run([http(402, "requires more credits"), ok])
assert isinstance(out, RuntimeError) and "402" in str(out), out
assert n == 1, f"HTTP 402 should not retry, made {n} calls"

# network-level failures never reach the HTTPError branch; they must retry too
out, n = run([urllib.error.URLError("connection refused"), ok])
assert out == "hello" and n == 2, (out, n)

out, n = run([TimeoutError("timed out")] * 3)
assert isinstance(out, RuntimeError) and "unreachable" in str(out), out
assert n == 3, f"a persistent timeout should try 3 times, made {n}"

# a body cut off mid-JSON is transient as well
out, n = run([b'{"choices": [{"mess', ok])
assert out == "hello" and n == 2, (out, n)

# an empty `choices` list is an upstream error, not an IndexError
out, n = run([{"choices": []}, ok])
assert isinstance(out, RuntimeError) and n == 1, (out, n)

# data_collection in config.json is forwarded to OpenRouter; absent, it is not sent
sent = []

def spy(req, timeout=None):
    sent.append(json.loads(req.data))
    return _Resp(json.dumps(ok).encode())

real_urlopen, real_config = urllib.request.urlopen, server.config
urllib.request.urlopen = spy
try:
    server.config = lambda: {"model": "m", "data_collection": "deny"}
    server.ai("hi")
    server.config = lambda: {"model": "m"}
    server.ai("hi")
finally:
    urllib.request.urlopen, server.config = real_urlopen, real_config
assert sent[0]["provider"] == {"data_collection": "deny"}, sent[0]
assert "provider" not in sent[1], sent[1]

# cheap_model and temperature are forwarded, and usage is logged for the ledger
sent.clear()
with_usage = {"choices": [{"message": {"content": "x"}},],
              "usage": {"prompt_tokens": 7, "completion_tokens": 3, "cost": 0.25}}

def spy_usage(req, timeout=None):
    sent.append(json.loads(req.data))
    return _Resp(json.dumps(with_usage).encode())

m = os.environ.pop("M", None)
real_urlopen, real_config = urllib.request.urlopen, server.config
urllib.request.urlopen = spy_usage
server._tl.calls = []
try:
    server.config = lambda: {"model": "strong", "cheap_model": "weak", "temperature": 1.1}
    server.ai("hi")
    server.ai("hi", cheap=True)
    calls = server._tl.calls
finally:
    server._tl.calls = None
    urllib.request.urlopen, server.config = real_urlopen, real_config
    if m:
        os.environ["M"] = m
assert [x["model"] for x in sent] == ["strong", "weak"] and sent[0]["temperature"] == 1.1, sent
assert calls == [{"model": "strong", "in": 7, "out": 3, "cost": 0.25},
                 {"model": "weak", "in": 7, "out": 3, "cost": 0.25}], calls

print("ok")

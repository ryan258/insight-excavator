# Export format anatomy

Field-level reference for the two AI chat exports, plus the minimal walk from raw
file to an ordered list of `(role, text, timestamp)` per conversation.

Resolves [#2](https://github.com/ryan258/insight-excavator/issues/2). Part of [#1](https://github.com/ryan258/insight-excavator/issues/1).

**Source of every claim below:** the export files themselves, read by streaming
scan on 2026-07-31. No secondary documentation was used — these are measured
counts over the full corpus, not vendor docs.

- ChatGPT export: `~/Downloads/rlwd--claude.zip` → `conversations.json` (66 MB)
- Claude export: `~/Downloads/rlwd--gpt.zip` → `conversations.json` (197 MB)

> The zip names are swapped. `rlwd--claude.zip` holds the **ChatGPT** export;
> `rlwd--gpt.zip` holds the **Claude** export. Verified again here: the former
> contains `user.json` with `chatgpt_plus_user`, the latter `users.json` with
> `uuid`/`full_name` plus `projects.json`/`memories.json`.

---

## 0. Corrections to the map's established facts

Three numbers in #1 are slightly off. Measured twice — once by the streaming
element iterator, once by an independent brace-depth counter that never parses
JSON — both agree:

| Fact in #1 | Measured |
| --- | --- |
| 1,339 ChatGPT conversations | **1,338** |
| 2,100 Claude conversations | 2,100 (confirmed) |
| ~51k messages total | **48,073** raw (26,533 ChatGPT + 21,540 Claude) |
| ~23.6k Claude messages | **21,540** |

Corpus total is **3,438** conversations, not 3,439. After the drop rules in §3
the corpus that actually reaches an AI is **38,524 messages / 59.2 M characters**
(≈14.8 M tokens), not 48k messages.

---

## 1. Archive members

### ChatGPT (`rlwd--claude.zip`)

| Member | Size | Use |
| --- | --- | --- |
| `conversations.json` | 65.8 MB | the corpus |
| `user.json` | 136 B | `{id, email, chatgpt_plus_user, phone_number}` |
| `shared_conversations.json` | 3 KB | `{id, conversation_id, title, is_anonymous}` — public-share links |
| `chat.html` | 67 MB | rendered duplicate of the JSON. Ignore. |
| `message_feedback.json`, `sora.json`, `shopping.json` | 2 B each | empty (`[]`/`{}`) |
| `group_chats.json` | 13 B | `{"chats": []}` |
| `<conversation_id>/audio/*.wav` | ~600 MB | voice-mode audio. Ignore. |

The audio blobs are why the zip is 690 MB for a 66 MB corpus.

### Claude (`rlwd--gpt.zip`)

| Member | Size | Use |
| --- | --- | --- |
| `conversations.json` | 196.9 MB | the corpus |
| `projects.json` | 2.9 MB | 148 projects — see §5 |
| `memories.json` | 56 KB | one long generated prose profile, `[{"conversations_memory": "..."}]` |
| `users.json` | 155 B | `[{uuid, full_name, email_address, verified_phone_number}]` |

Both `conversations.json` files are a **top-level JSON array**. Neither should be
`json.load`ed whole — stream elements off with `json.JSONDecoder().raw_decode`
against a growing buffer (peak memory ≈ one conversation).

---

## 2. Message ordering

### ChatGPT — walk up from `current_node`, then reverse

A conversation carries `mapping`, a dict of `node_id → node`, and `current_node`,
the id of the leaf the UI was last showing.

```json
{
 "id": "54517f40-…",
 "message": { "…": "…" },
 "parent": "ad8e8a88-…",
 "children": ["6e0943bf-…"]
}
```

Measured invariants over all 1,338 conversations:

- Exactly **1,338 nodes have `parent: null`** — one root per conversation.
- Exactly **1,338 nodes have `message: null`** — and they are the same nodes.
  The root is always a synthetic, message-less anchor.
- **`current_node` is present in `mapping` in 1,338/1,338 conversations.** There
  is no missing-leaf case to defend against.

So the walk is:

```python
path, nid = [], conv["current_node"]
while nid is not None and nid in conv["mapping"]:
    path.append(nid)
    nid = conv["mapping"][nid]["parent"]
path.reverse()          # root … current_node, in true chronological order
```

Do **not** iterate `mapping.values()` — dict order is insertion order from the
export writer and includes dead branches. Do **not** sort by
`message.create_time` — 1,465 system messages have `create_time: null`.

**Branches are real but small.** 306 nodes have more than one child; 206 of 1,338
conversations (15%) contain at least one off-path node. The `current_node` walk
prunes **1,050 of 26,533 messages (4.0%)**. Those are superseded edits and
regenerations — the versions the user navigated away from. Dropping them is
correct: the path is exactly what the user last saw.

Empirically verified on the most-branched conversation in the corpus
(`fb42aa91-39c8-4ff0-90ff-0958cbb84b03`, "Moonlight Bay Trilogy Conclusion"):
94 nodes, 7 branch points, path length 83, 11 nodes pruned. The reconstructed
path alternates user/assistant cleanly with hidden system injections interleaved,
and reads as a coherent transcript end to end.

### Claude — array order is already correct; do not sort

`chat_messages` is a flat array. Measured over all 21,540 messages:

- **Zero messages appear out of `created_at` order relative to array order.**
- **5,237 adjacent message pairs share an identical `created_at`.**
- `created_at` is never null; always a 27-char ISO-8601 `…Z` string.

The second fact is the trap. Because thousands of adjacent timestamps tie,
sorting by `created_at` risks reordering with any non-stable sort, and buys
nothing — array order is already right. **Use the array as given.** If you sort
defensively, sort with the array index as tiebreaker (`sorted(msgs, key=lambda
m: m["created_at"])` is safe in CPython only because `list.sort` is stable; make
that explicit rather than implicit).

Longest conversation is 158 messages.

---

## 3. What to drop at the parse layer

### ChatGPT

`author.role` across all 26,533 messages:

| role | count |
| --- | --- |
| assistant | 11,657 |
| user | 9,047 |
| tool | 3,582 |
| system | 2,247 |

`content.content_type`:

| content_type | count | keep? |
| --- | --- | --- |
| `text` | 22,627 | yes (`"".join(content["parts"])`) |
| `code` | 1,415 | no — 1,410 are assistant→tool call payloads |
| `multimodal_text` | 1,070 | partially — see below |
| `tether_quote` | 753 | no — browsing tool quote |
| `tether_browsing_display` | 453 | no |
| `system_error` | 107 | no |
| `execution_output` | 106 | no |
| `thoughts` | 1 | no |
| `reasoning_recap` | 1 | no |

**The drop rule collapses to three conditions**, and they turn out to nest neatly:

1. `author.role not in ("user", "assistant")` — removes all tool and system messages.
2. `recipient not in (None, "all")` — removes assistant *tool-call* turns. 24,364
   messages are `recipient: "all"`; the rest name a tool (`dalle.text2im` 894,
   `browser` 687, `python` 118, plus ~25 plugin endpoints).
3. Empty after extraction and `.strip()` — 203 messages (121 assistant, 82 user)
   are genuinely blank.

**Surprising and load-bearing:** every one of the 20,704 user/assistant messages
has `weight == 1.0` and `is_visually_hidden_from_conversation` falsy. *All* 2,270
hidden messages and *all* 2,263 weight-0 messages are `role: "system"` (or tool).
So condition 1 already subsumes the hidden-context and weight-0 filters — you do
not need to check `metadata.is_visually_hidden_from_conversation` or `weight` at
all. Checking them is free insurance, but they buy nothing on this corpus.

Breakdown of the system messages you are discarding — all are hidden:

| flavour | count |
| --- | --- |
| hidden, `weight: 0` (dead context injection) | 1,212 |
| hidden, `weight: 1` (live context injection) | 707 |
| `is_user_system_message: true` (the user's Custom Instructions) | 328 |

The 328 Custom Instruction messages carry the user's own words in
`metadata.user_context_message_data`. They are the only system content with
authorial value, and they are near-duplicated across conversations. Recommend
dropping them with the rest; note them here so a later session does not
rediscover them and assume they were missed.

`multimodal_text` parts is a **mixed list of strings and dicts**. Keep the
strings, discard the dicts. Observed dict `content_type` values: `image_asset_pointer`
(138), `audio_transcription` (86), `audio_asset_pointer` (43),
`real_time_user_audio_video_asset_pointer` (43). Note `audio_transcription` dicts
hold real transcribed speech — currently discarded; 86 instances, low stakes.

`status` is `finished_successfully` for 25,396 on-path messages, `in_progress`
for 71 and `finished_partial_completion` for 16. Not worth filtering on.

### Claude

`sender`: `human` 10,752, `assistant` 10,788. There is no system or tool sender —
tool activity lives *inside* the assistant message's content blocks.

`content[].type` across all messages:

| block type | count | chars | keep? |
| --- | --- | --- | --- |
| `text` | 23,687 | 38.3 M | **yes** |
| `thinking` | 4,964 | 4.0 M | no — extended reasoning |
| `tool_use` | 4,022 | } 37.2 M | no |
| `tool_result` | 3,925 | } | no |
| `token_budget` | 481 | ~0 | no |
| `voice_note` | 24 | small | optional — has a real `.text` |

Tool blocks are **37.2 M characters, nearly as much as the entire real transcript
(38.3 M)**. Dropping them roughly halves the Claude corpus.

Assistant messages interleave block types in long runs; the top shapes are
`T` (7,369), `KT` (1,563), `TURT` (611), `KTURKT` (221), where
K=thinking T=text U=tool_use R=tool_result B=token_budget. A single message can
hold 30+ blocks. Extraction must concatenate *all* `type == "text"` blocks in
order, not just the first or last — 1,533 messages carry more than one.

#### The `.text` trap

Every message also has a top-level `text` string. It looks like a convenient
shortcut. It is not.

- `.text` equals the joined text blocks in 18,122 of 21,540 messages.
- In the other **3,418 messages `.text` is *longer*** — by **4.37 M characters in
  total**.
- The extra content is the model's **thinking**: in 2,529 of those messages the
  thinking block's opening text appears verbatim inside `.text`. In 1,279 the
  tool name appears too.

`.text` is a flattened render that silently includes chain-of-thought and tool
chatter. **Never read `.text`.** Always join the `type == "text"` blocks.

There is one edge case that tempts a fallback: 52 messages have text blocks that
are whitespace-only while `.text` is populated. All 52 have `thinking` or
`tool_use` blocks present — the fallback would import pure reasoning. **Do not
fall back.** Treat them as empty.

After extraction, 739 messages are empty (679 human, 60 assistant), and 45 of
2,100 conversations yield zero characters.

#### Attachments and files

Two separate arrays per message:

- `attachments[]` — `{file_name, file_size, file_type, extracted_content}`, 1,214
  total. `extracted_content` is the **full text of a pasted/uploaded file**:
  median 8,012 chars, p90 38,179, max 528,318 — **22.7 M characters** in total.
  Mostly `txt` (1,053), plus markdown, js, json, python, a few pdf/docx.
- `files[]` — `{file_name}` only, 1,790 total, **no content**. 928 `.txt`,
  515 `.png`, 75 `.md`. Pure filename references; nothing to extract.

**658 human messages have empty text but a non-empty attachment or file** — the
user uploaded a document and said nothing. If attachments are dropped, those turns
vanish entirely and the assistant's reply reads as a non-sequitur.

`extracted_content` is a genuine decision, not junk: it is the user's own source
material, and it adds 22.7 M chars (+59%) to the Claude corpus. §6 gives the
distribution both ways. Recommendation: **drop it for the first ingest** — it is
mostly code and pasted docs rather than the conversational thinking the filter is
looking for, and it nearly doubles the token bill.

---

## 4. Available metadata

### ChatGPT — conversation level

31 keys; 12 are `null` in all 1,338 conversations (`plugin_ids`,
`conversation_origin`, `is_read_only`, `context_scopes`, `sugar_item_id`,
`pinned_time`, `owner`, `is_starred`, …). Worth keeping:

| field | type | note |
| --- | --- | --- |
| `conversation_id` / `id` | str | identical values; UUID |
| `title` | str | model-generated |
| `create_time` | float | Unix epoch seconds, fractional |
| `update_time` | float | Unix epoch seconds |
| `default_model_slug` | str \| null | e.g. `"auto"`, `"gpt-4"` |
| `gizmo_id` | str \| null | **custom-GPT id — set on 213 conversations** |
| `gizmo_type` | str \| null | pairs with `gizmo_id` |
| `is_archived` | bool | |
| `memory_scope` | str | e.g. `"global_enabled"` |
| `is_study_mode` | bool | |

`gizmo_id` is the closest ChatGPT analogue to a project: 213 conversations
(16%) ran under a named custom GPT. The export gives only the opaque id — no
gizmo name is included anywhere in the archive, so it groups conversations but
cannot label the group.

### ChatGPT — message level

`{id, author, create_time, update_time, content, status, end_turn, weight,
metadata, recipient, channel}`. Useful bits:

- `author.role` — see §3.
- `create_time` — float epoch; **null on 1,465 system messages**, never null on
  user/assistant/tool.
- `metadata.model_slug` — 14,565 messages. Top values: `gpt-4` (4,717),
  `gpt-4-gizmo` (3,040), `gpt-4-dalle` (2,133), `gpt-4-plugins` (1,508),
  `text-davinci-002-render-sha` (675), `gpt-4-browsing` (621), `gpt-4o` (470),
  `gpt-4-code-interpreter` (426), down to `gpt-5` (10). This is the best
  provenance signal in either export — it dates a conversation by model era.
- `metadata.attachments` — 186 messages.
- `metadata.citations` / `content_references` — browsing citations.
- `channel` is `null` on 25,482 of 25,483 on-path messages. Ignore.

### Claude — conversation level

Only **7 keys**, all always present:

```json
{
 "uuid": "e5438fc6-…",
 "name": "IDEA MINING 1-139",
 "summary": "<str 3632>",
 "created_at": "2025-12-19T13:24:49.193685Z",
 "updated_at": "2025-12-19T15:24:58.840836Z",
 "account": {"uuid": "3a84a9f6-…"},
 "chat_messages": [ … ]
}
```

- `name` is empty on 54 conversations.
- `summary` is **non-empty on only 137 of 2,100** (6.5%). Not a reliable field.
- `account.uuid` is the only key inside `account`.

**There is no model field anywhere in the Claude export** — not per conversation,
not per message. Provenance cannot record which Claude model produced a reply.
This is an asymmetry with ChatGPT worth stating in any provenance header:
model is knowable for ChatGPT, unknowable for Claude.

### Claude — message level

`{uuid, text, content, sender, created_at, updated_at, attachments, files}` —
8 keys, all always present. `created_at`/`updated_at` are ISO-8601 `…Z`.
Content blocks additionally carry `start_timestamp`/`stop_timestamp` per block.

---

## 5. `projects.json` — a dead end for grouping, a corpus in its own right

**`project` is `null` on all 2,100 conversations.** There is no `project_uuid`,
no `project` object, no reference of any kind. Searching the entire serialised
`projects.json` for `chat_messages` returns zero hits, and no project record
contains conversation ids.

**Conclusion: the conversation↔project association is simply not present in this
export.** It cannot be recovered. Do not build a parser that looks for it.

`projects.json` is nonetheless 148 records of real content:

```json
{
 "uuid": "0d005548-…",
 "name": "MAKE CODE - STEP 2+3: fusion-chain-nodejs",
 "description": "",
 "is_private": true,
 "is_starter_project": false,
 "prompt_template": "<4460 chars>",
 "created_at": "2024-08-30T18:00:41.604138+00:00",
 "updated_at": "2024-09-01T00:21:49.861917+00:00",
 "creator": {"uuid": "3a84a9f6-…", "full_name": "Ryan Johnson"},
 "docs": [{"uuid": "…", "filename": "COMING.md", "content": "<5492 chars>", "created_at": "…"}]
}
```

- 148 projects, 47 of which carry docs; 621 docs total.
- `prompt_template` — **471,743 chars** of hand-written system prompts. This is
  the user's own methodology, densely stated.
- `docs[].content` — **2,124,435 chars** across 621 files.

That is ~2.6 M characters of first-person, deliberately-authored material, and
it is arguably the highest idea-density text in the whole export — but it is
*documents*, not conversations, which puts it on the far side of the same line
that already excludes the `.docx` pile in #1's Out of Scope. Flagging it, not
claiming it.

---

## 6. Size distribution

Characters of extractable transcript per conversation, after the §3 drop rules.

| | ChatGPT | Claude (text only) | Claude (+ attachments) |
| --- | ---: | ---: | ---: |
| conversations | 1,338 | 2,100 | 2,100 |
| min | 0 | 0 | 0 |
| p25 | 3,448 | 3,556 | 4,792 |
| **median** | **7,550** | **7,640** | **11,544** |
| p75 | 17,669 | 19,388 | 32,093 |
| p90 | 36,066 | 46,335 | 76,471 |
| p95 | 56,723 | 76,217 | 112,288 |
| p99 | 114,787 | 138,002 | 237,312 |
| **max** | **357,236** | **454,681** | **533,710** |
| mean | 15,630 | 18,231 | 29,048 |
| **total** | **20.9 M** | **38.3 M** | **61.0 M** |
| zero-length conversations | 3 | 45 | 45 |

Counts above thresholds (≈4 chars/token):

| threshold | ≈tokens | ChatGPT | Claude (text) | Claude (+attach) |
| --- | ---: | ---: | ---: | ---: |
| > 40,000 chars | 10k | 120 | 255 | 434 |
| > 100,000 chars | 25k | 19 | 61 | 138 |
| > 200,000 chars | 50k | 3 | 6 | 29 |
| > 400,000 chars | 100k | 0 | 1 | 4 |
| > 800,000 chars | 200k | 0 | 0 | 0 |

### What this means for "one file = one conversation"

**No conversation blows a modern context window.** The single largest
conversation in the corpus is 454,681 chars ≈ **114k tokens**, which fits a 200k
window whole. Including attachments the max is 533,710 chars ≈ 133k tokens —
still inside 200k.

The distribution is heavily right-skewed but the tail is thin: median ~7.6k chars
(~1.9k tokens), and only **9 conversations of 3,438 (0.26%)** exceed 50k tokens.
One file per conversation is viable with no chunking machinery. If a cheaper
model with a 128k window is used for the filter pass, exactly **1 conversation**
(the 454k-char Claude one) needs special handling, and truncation would be an
acceptable answer for a single outlier.

The 48 zero-length conversations (3 ChatGPT + 45 Claude) should be skipped before
any AI call rather than written as empty source files.

---

## 7. The minimal extraction walk

Reference pseudocode. Both functions yield `(role, text, timestamp)` in order.
Roles are normalised to `"user"` / `"assistant"`.

### ChatGPT

```python
def chatgpt_messages(conv):
    mapping = conv["mapping"]
    path, nid = [], conv["current_node"]
    while nid is not None and nid in mapping:
        path.append(nid)
        nid = mapping[nid].get("parent")
    path.reverse()

    for node_id in path:
        m = mapping[node_id].get("message")
        if not m:                                    # synthetic root
            continue
        role = m["author"]["role"]
        if role not in ("user", "assistant"):        # drops tool + system,
            continue                                 # incl. all hidden/weight-0
        if m.get("recipient") not in (None, "all"):  # drops tool-call turns
            continue
        c = m.get("content") or {}
        ct = c.get("content_type")
        if ct == "text":
            text = "".join(p for p in (c.get("parts") or [])
                           if isinstance(p, str))
        elif ct == "multimodal_text":                # mixed str/dict list
            text = "".join(p for p in (c.get("parts") or [])
                           if isinstance(p, str))
        else:                                        # code, tether_*, etc.
            continue
        text = text.strip()
        if not text:
            continue
        yield role, text, m.get("create_time")       # float epoch, may be None
```

Conversation metadata: `conv["conversation_id"]`, `conv["title"]`,
`conv["create_time"]`, `conv["update_time"]`, `conv["default_model_slug"]`,
`conv["gizmo_id"]`. Per-message model: `m["metadata"].get("model_slug")`.

### Claude

```python
ROLE = {"human": "user", "assistant": "assistant"}

def claude_messages(conv):
    for m in conv["chat_messages"]:                  # array order is correct
        text = "".join(
            b.get("text") or ""
            for b in (m.get("content") or [])
            if b.get("type") == "text"                # never thinking/tool_*
        ).strip()
        if not text:                                  # do NOT fall back to m["text"]
            continue
        yield ROLE[m["sender"]], text, m["created_at"]   # ISO-8601 str
```

Conversation metadata: `conv["uuid"]`, `conv["name"]`, `conv["created_at"]`,
`conv["updated_at"]`. No model, no project.

### Streaming the file

```python
import json

def iter_conversations(fileobj, chunk=1 << 20):
    """Yield elements of a top-level JSON array without loading the file."""
    dec, buf, started = json.JSONDecoder(), "", False
    while True:
        data = fileobj.read(chunk)
        if not data:
            return
        buf += data.decode("utf-8", "replace")
        while True:
            i, n = 0, len(buf)
            while i < n and buf[i] in " \t\r\n,":
                i += 1
            if i >= n:
                buf = ""
                break
            if not started:
                started, buf = True, buf[i + 1:]      # consume '['
                continue
            if buf[i] == "]":
                return
            try:
                obj, end = dec.raw_decode(buf, i)
            except ValueError:
                buf = buf[i:]
                break                                  # need more bytes
            yield obj
            buf = buf[end:]
```

Feed it `subprocess.Popen(["unzip", "-p", zip_path, "conversations.json"],
stdout=PIPE).stdout`, or `zipfile.ZipFile(...).open("conversations.json")` — the
latter is stdlib-only and streams fine. Peak memory stays around one conversation.

---

## 8. Summary of decisions this note settles

1. ChatGPT order: walk `parent` up from `current_node`, reverse. Prunes 4.0% of
   messages, correctly.
2. Claude order: use `chat_messages` array order as-is. Do not sort — 5,237
   timestamp ties make sorting a hazard with no benefit.
3. ChatGPT junk filter is one line: keep `role in (user, assistant)` and
   `recipient in (None, "all")`. Hidden/weight-0 filtering is redundant.
4. Claude junk filter is one line: keep `content[].type == "text"`. Never touch
   the top-level `.text` field — it contains chain-of-thought.
5. Project association for Claude is unrecoverable; `project` is null everywhere.
6. One file per conversation is safe. No conversation exceeds a 200k context;
   only 9 of 3,438 exceed 50k tokens.
7. Attachment `extracted_content` (22.7 M chars) is a live decision, recommended
   dropped for the first ingest.

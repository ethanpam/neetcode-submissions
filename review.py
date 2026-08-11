#!/usr/bin/env python3
"""Gemini PR review -> inline GitHub comments. Run from gemini-review.yml.

env: REPO, PR_NUMBER, GEMINI_API_KEY, GH_TOKEN
"""
import json
import os
import re
import sys
import urllib.error
import urllib.request

# rest are fallbacks for when the first one is out of quota
MODELS = ["gemini-3.5-flash", "gemini-flash-latest", "gemini-2.0-flash"]
GEMINI_URL = "https://generativelanguage.googleapis.com/v1beta/models/{m}:generateContent"
MAX_DIFF = 120_000

SCHEMA = {
    "type": "object",
    "properties": {
        "summary": {"type": "string"},
        "comments": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "path": {"type": "string"},
                    "line": {"type": "integer"},
                    "start_line": {"type": "integer"},
                    "body": {"type": "string"},
                },
                "required": ["path", "line", "body"],
            },
        },
    },
    "required": ["summary", "comments"],
}


def tag_lines(diff):
    # Sticks "path:N: " on every line that exists in the new file, so the model
    # quotes real line numbers instead of guessing. Those same numbers are the
    # only ones GitHub will hang an inline comment off, hence valid[path].
    out, valid, path, n = [], {}, None, 0
    for ln in diff.splitlines():
        if ln.startswith("diff --git"):
            path = None
        elif ln.startswith("+++ b/"):
            path = ln[6:]
            valid.setdefault(path, set())
        elif ln.startswith("@@"):
            m = re.search(r"\+(\d+)", ln)
            n = int(m.group(1)) if m else 0
        elif path and (ln.startswith(" ") or ln[:1] == "+" and not ln.startswith("+++")):
            out.append(f"{path}:{n}: {ln}")
            valid[path].add(n)
            n += 1
            continue
        out.append(ln)
    return "\n".join(out), valid


def ask_gemini(key, prompt):
    body = json.dumps({
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "temperature": 0.3,
            "responseMimeType": "application/json",
            "responseSchema": SCHEMA,
        },
    }).encode()
    for model in MODELS:
        req = urllib.request.Request(
            GEMINI_URL.format(m=model), data=body, method="POST",
            headers={"x-goog-api-key": key, "Content-Type": "application/json"},
        )
        try:
            with urllib.request.urlopen(req, timeout=120) as r:
                data = json.load(r)
            print(f"Review produced by {model}.", file=sys.stderr)
            return json.loads(data["candidates"][0]["content"]["parts"][0]["text"])
        except urllib.error.HTTPError as e:
            print(f"{model} failed (HTTP {e.code}): {e.read()[:200]!r}", file=sys.stderr)
        except Exception as e:
            print(f"{model} error: {e}", file=sys.stderr)
    return None


def usable_comments(review, valid):
    keep = []
    for c in review.get("comments", []):
        path, line = c.get("path"), c.get("line")
        if line not in valid.get(path, ()):
            print(f"dropping comment on {path}:{line}, not a diff line", file=sys.stderr)
            continue
        item = {"path": path, "line": line, "side": "RIGHT", "body": c.get("body", "")}
        start = c.get("start_line")
        if isinstance(start, int) and start in valid[path] and start < line:
            item["start_line"] = start
            item["start_side"] = "RIGHT"
        keep.append(item)
    return keep


def gh_post(repo, endpoint, token, payload):
    req = urllib.request.Request(
        f"https://api.github.com/repos/{repo}/{endpoint}",
        data=json.dumps(payload).encode(), method="POST",
        headers={"Authorization": f"Bearer {token}",
                "Accept": "application/vnd.github+json"},
    )
    with urllib.request.urlopen(req, timeout=60) as r:
        return r.status


def main():
    repo = os.environ["REPO"]
    pr = os.environ["PR_NUMBER"]
    token = os.environ["GH_TOKEN"]

    with open("pr.diff", encoding="utf-8", errors="replace") as f:
        tagged, valid = tag_lines(f.read()[:MAX_DIFF])
    with open(".github/review-prompt.md", encoding="utf-8") as f:
        prompt = f.read() + "\n\n" + tagged

    review = ask_gemini(os.environ["GEMINI_API_KEY"], prompt)
    if not review:
        print("No model produced a review; skipping (quota or API error).")
        return

    summary = (review.get("summary") or "").strip() or "Automated code review."
    comments = usable_comments(review, valid)

    try:
        if comments:
            gh_post(repo, f"pulls/{pr}/reviews", token,
                    {"body": summary, "event": "COMMENT", "comments": comments})
        else:
            gh_post(repo, f"issues/{pr}/comments", token, {"body": summary})
        print(f"Posted review with {len(comments)} inline suggestion(s).")
    except urllib.error.HTTPError as e:
        # inline post bounced. don't lose the review, flatten it into one comment
        print(f"Inline review failed (HTTP {e.code}): {e.read()[:200]!r}; "
            "posting as a plain comment.", file=sys.stderr)
        body = summary + "\n\n" + "\n\n".join(
            f"**`{c['path']}` line {c['line']}**\n\n{c['body']}" for c in comments)
        gh_post(repo, f"issues/{pr}/comments", token, {"body": body})
        print("Posted fallback comment.")


if __name__ == "__main__":
    main()

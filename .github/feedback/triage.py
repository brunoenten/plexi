#!/usr/bin/env python3
"""Daily feedback triage: collect new community activity, let a Cursor cloud agent
triage it (opening a PR for fixes), and post a digest issue that pings the owner."""

import json
import os
import sys
import urllib.request
from datetime import datetime, timedelta, timezone

REPO = os.environ["GITHUB_REPOSITORY"]
OWNER = os.environ.get("FEEDBACK_OWNER") or REPO.split("/")[0]
DISCUSSIONS = [d for d in os.environ.get("FEEDBACK_DISCUSSIONS", "").split() if "#" in d]
WINDOW = timedelta(hours=float(os.environ.get("FEEDBACK_WINDOW_HOURS", "24")))
TOKEN = os.environ["GITHUB_TOKEN"]
DRY_RUN = os.environ.get("DRY_RUN") == "1"
DIGEST_LABEL = "feedback-digest"


def github(path, method="GET", body=None):
    url = path if path.startswith("https://") else f"https://api.github.com{path}"
    req = urllib.request.Request(
        url,
        method=method,
        data=json.dumps(body).encode() if body is not None else None,
        headers={
            "Authorization": f"Bearer {TOKEN}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
        },
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read() or b"null")


def parse_time(value):
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def is_external(login, kind=""):
    return login and login != OWNER and kind != "Bot" and not login.endswith("[bot]")


def discussion_activity(ref, since):
    owner_repo, number = ref.split("#")
    owner, name = owner_repo.split("/")
    query = """
    query($owner: String!, $name: String!, $number: Int!) {
      repository(owner: $owner, name: $name) {
        discussion(number: $number) {
          title url
          comments(last: 100) {
            nodes {
              url createdAt body author { login }
              replies(last: 100) { nodes { url createdAt body author { login } } }
            }
          }
        }
      }
    }"""
    data = github("/graphql", "POST", {"query": query, "variables": {"owner": owner, "name": name, "number": int(number)}})
    discussion = data["data"]["repository"]["discussion"]
    items = []
    for comment in discussion["comments"]["nodes"]:
        for node, kind in [(comment, "discussion comment")] + [(r, "discussion reply") for r in comment["replies"]["nodes"]]:
            login = (node.get("author") or {}).get("login")
            if parse_time(node["createdAt"]) >= since and is_external(login):
                items.append({"kind": kind, "where": discussion["title"], "author": login, "url": node["url"], "body": node["body"]})
    return items


def repo_activity(since):
    stamp = since.strftime("%Y-%m-%dT%H:%M:%SZ")
    items = []
    for issue in github(f"/repos/{REPO}/issues?state=all&since={stamp}&per_page=100"):
        if any(label["name"] == DIGEST_LABEL for label in issue.get("labels", [])):
            continue
        user = issue["user"]
        if parse_time(issue["created_at"]) >= since and is_external(user["login"], user.get("type")):
            kind = "pull request" if "pull_request" in issue else "issue"
            items.append({"kind": f"new {kind}", "where": f"#{issue['number']} {issue['title']}", "author": user["login"], "url": issue["html_url"], "body": issue.get("body") or ""})
    for comment in github(f"/repos/{REPO}/issues/comments?since={stamp}&per_page=100"):
        user = comment["user"]
        if parse_time(comment["created_at"]) >= since and is_external(user["login"], user.get("type")):
            items.append({"kind": "issue comment", "where": comment["issue_url"].rsplit("/", 1)[1], "author": user["login"], "url": comment["html_url"], "body": comment["body"]})
    return items


def render_items(items):
    blocks = []
    for item in items:
        quoted = "\n".join("> " + line for line in item["body"].strip().splitlines()) or "> (empty)"
        blocks.append(f"**{item['kind']}** by @{item['author']} on {item['where']}\n{item['url']}\n\n{quoted}")
    return "\n\n---\n\n".join(blocks)


PROMPT = """You are maintaining **plexi**, a single-file, stdlib-only Python terminal Plex client
for Omarchy (see README.md and the `plexi` script in this repo).

New community feedback arrived in the last day:

{activity}

Do this:
1. Classify each item: question, bug report, feature request, praise, or other.
2. For bug reports, and for feature requests that are small, clearly in scope and fit the
   project's lightweight spirit, implement the change in `plexi` (keep it stdlib-only, match
   the existing style) and update README.md if user-facing behaviour changes. Bump nothing.
   If nothing warrants a code change, make no changes.
3. Do NOT comment on GitHub, open issues, or contact anyone. The maintainer reviews everything.

Your final message is posted verbatim as a digest for the maintainer. Format it as markdown:
- One section per item: who said what (one line), your classification, and a ready-to-paste
  **suggested reply** written in a friendly, concise maintainer voice.
- A final "Changes" section describing any code changes you made (or "No code changes").
"""


def run_agent(items):
    from cursor_sdk import Agent, AgentOptions, CloudAgentOptions, CloudRepository, CursorAgentError

    try:
        result = Agent.prompt(
            PROMPT.format(activity=render_items(items)),
            AgentOptions(
                api_key=os.environ["CURSOR_API_KEY"],
                model=os.environ.get("CURSOR_MODEL") or "composer-2.5",
                name=f"plexi feedback triage {datetime.now(timezone.utc):%Y-%m-%d}",
                cloud=CloudAgentOptions(
                    repos=[CloudRepository(url=f"https://github.com/{REPO}")],
                    auto_create_pr=True,
                    skip_reviewer_request=True,
                ),
            ),
        )
    except CursorAgentError as err:
        return None, [], f"The Cursor agent couldn't start: {err.message}"
    print(f"agent {result.agent_id} run {result.id}: {result.status}")
    prs = [b.pr_url for b in (result.git.branches if result.git else []) if b.pr_url]
    if result.status != "finished":
        return result, prs, f"The Cursor agent run ended with status `{result.status}` (agent `{result.agent_id}`)."
    return result, prs, None


def main():
    since = datetime.now(timezone.utc) - WINDOW
    items = []
    for ref in DISCUSSIONS:
        items += discussion_activity(ref, since)
    items += repo_activity(since)
    print(f"{len(items)} new item(s) since {since:%Y-%m-%d %H:%M} UTC")
    if not items:
        return 0
    if DRY_RUN:
        print(PROMPT.format(activity=render_items(items)))
        return 0

    result, prs, problem = run_agent(items)
    sections = [f"@{OWNER} — {len(items)} new item(s) of feedback since {since:%Y-%m-%d %H:%M} UTC."]
    if prs:
        sections.append("**Proposed fix:** " + ", ".join(prs))
    if problem:
        sections.append(f"⚠️ {problem}")
    if result and result.result:
        sections.append(result.result.strip())
    sections.append("<details><summary>Raw activity</summary>\n\n" + render_items(items) + "\n\n</details>")

    issue = github(f"/repos/{REPO}/issues", "POST", {
        "title": f"Feedback digest — {datetime.now(timezone.utc):%Y-%m-%d}",
        "body": "\n\n".join(sections),
        "labels": [DIGEST_LABEL],
    })
    print(f"digest: {issue['html_url']}")
    return 1 if problem else 0


if __name__ == "__main__":
    sys.exit(main())

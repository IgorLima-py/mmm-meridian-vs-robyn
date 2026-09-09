"""PreToolUse guard: refuse commits that would poison a public history.

This repository is private today and will be published **with its entire
history**. A bad commit is therefore not fixable by deleting the file later, so
three things are blocked outright rather than warned about:

  1. any file over 50 MB              (outputs/ holds 1.2 GB, six files >100 MB)
  2. any path under outputs/          (heavy run artifacts; extracts go to
                                       runs/*/results/)
  3. the forbidden phrase             (CLAUDE.md rule: nothing may claim an MMM
                                       was built as a credential)

Registered on PreToolUse/Bash with `if` filters on `git commit *` and
`git add *`.

Two design points that are load-bearing:

* **Exit 2, never exit 0 + a deny decision.** Only exit 2 is documented to take
  precedence over allow rules, and /tchau pre-approves `git commit` in its own
  `allowed-tools`. An exit-0 deny would be silently overridden.

* **Candidate set = index UNION working tree.** /tchau runs
  `git add -A && git commit` as a single Bash call, so at hook time the index is
  still stale. Inspecting only `git diff --cached` would wave through whatever
  `add -A` is about to stage.

Fails closed: an unexpected error exits 2. The harness default for a hook error
is non-blocking, which for a guard against an irreversible leak is the wrong
default.
"""

import json
import os
import re
import subprocess
import sys

MAX_BYTES = 50 * 1024 * 1024
HEAVY_PREFIXES = ("outputs/",)
MAX_SCAN_BYTES = 1024 * 1024          # skip diffing files larger than this

# The claim this project must never make. Two shapes: the compact credential
# phrasing, and the spelled-out version.
FORBIDDEN = re.compile(
    r"\bbuil[td]\s+(?:an?\s+|my\s+|our\s+|their\s+)*mmm\b"
    r"|\b(?:i|we)\s+(?:have\s+)?buil[td]\s+\S{0,30}?\s*marketing[- ]mix[- ]model",
    re.IGNORECASE,
)

# Files that contain the forbidden phrase by construction: the rulebook that
# forbids it, and the infrastructure that enforces it (this file included).
PHRASE_EXEMPT_PREFIXES = (".claude/",)
PHRASE_EXEMPT_PATHS = {"CLAUDE.md"}

# A line that quotes or negates the phrase is discussing it, not claiming it.
NEGATION = re.compile(
    r"\bnot\b|\bnever\b|\bno\b|\bdoes ?n[o']t\b|\bcannot\b|\bwithout\b"
    r"|\bnão\b|\bnunca\b|\bproibid|\bforbidden\b|\bclaim",
    re.IGNORECASE,
)


def git(root, *args):
    """Run git in the project root. cwd is not guaranteed to be the repo."""
    out = subprocess.run(
        ["git", "-C", root, *args],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
    )
    return out.stdout if out.returncode == 0 else ""


def candidate_paths(root, command):
    """Files this command is about to put into a commit."""
    paths = set()
    staged = git(root, "diff", "--cached", "--name-only", "-z",
                 "--diff-filter=ACMR")
    paths.update(p for p in staged.split("\0") if p)

    # `git add -A && git commit` in one call: the index is still stale here.
    if re.search(r"\bgit\s+add\b", command) or \
       re.search(r"\bcommit\b[^|;&]*\s-\w*a", command):
        status = git(root, "status", "--porcelain", "-z", "-uall")
        for entry in status.split("\0"):
            if len(entry) > 3 and entry[0] != "!":
                paths.add(entry[3:])
    return sorted(paths)


def size_of(root, rel):
    full = os.path.join(root, rel)
    if os.path.isfile(full):
        return os.path.getsize(full)
    blob = git(root, "cat-file", "-s", f":{rel}").strip()
    return int(blob) if blob.isdigit() else 0


def added_lines(root, rel):
    """Lines this change adds, from whichever diff actually has content."""
    for args in (("diff", "--cached", "-U0", "--", rel),
                 ("diff", "-U0", "--", rel)):
        diff = git(root, *args)
        if diff:
            return [ln[1:] for ln in diff.splitlines()
                    if ln.startswith("+") and not ln.startswith("+++")]
    return []


def phrase_hits(text_lines):
    return [ln.strip() for ln in text_lines
            if FORBIDDEN.search(ln) and not NEGATION.search(ln)]


def human(n):
    return f"{n / 1024 / 1024:.1f} MB"


def main():
    payload = json.load(sys.stdin)
    command = payload.get("tool_input", {}).get("command", "")
    root = os.environ.get("CLAUDE_PROJECT_DIR") or payload.get("cwd") or "."

    problems = []

    # 1 + 2: size and heavy paths.
    for rel in candidate_paths(root, command):
        norm = rel.replace("\\", "/")
        if norm.startswith(HEAVY_PREFIXES):
            problems.append(
                f"  {norm}\n      outputs/ is a run artifact and is never "
                f"committed; small extracts belong in runs/*/results/")
            continue
        n = size_of(root, rel)
        if n > MAX_BYTES:
            problems.append(
                f"  {norm}\n      {human(n)} — over the {human(MAX_BYTES)} "
                f"limit for a history that goes public")
            continue
        # 3a: the phrase inside the change itself.
        if norm in PHRASE_EXEMPT_PATHS or norm.startswith(PHRASE_EXEMPT_PREFIXES):
            continue
        if n and n <= MAX_SCAN_BYTES:
            for hit in phrase_hits(added_lines(root, rel)):
                problems.append(
                    f"  {norm}\n      forbidden claim: \"{hit[:110]}\"")

    # 3b: the phrase in the commit message — catches -m, -F and heredocs.
    for hit in phrase_hits(command.splitlines()):
        problems.append(
            f"  (commit message)\n      forbidden claim: \"{hit[:110]}\"")

    if problems:
        sys.stderr.write(
            "BLOCKED: this cannot go into a history that will be public.\n\n"
            + "\n".join(problems)
            + "\n\nFix what is listed and try again. Do not work around this "
              "with `git add -f`, by loosening .gitignore, or by rewording "
              "only to dodge the pattern.\n")
        sys.exit(2)


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:                       # fail closed, deliberately
        sys.stderr.write(
            f"BLOCKED: the publication guard itself failed ({type(exc).__name__}"
            f": {exc}). Refusing the commit rather than letting it through "
            f"unchecked. Fix .claude/hooks/guard_publication.py.\n")
        sys.exit(2)

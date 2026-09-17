"""gitguard: no-direct-push -- block direct pushes to protected branches.

Push-time companion to no-direct-commit, for commits that slipped through
(e.g. made with --no-verify) or landed on the branch another way.

pre-commit's `language: python` pre-push hooks don't receive git's pre-push
stdin ("<local-ref> <local-sha> <remote-ref> <remote-sha>" lines) -- pre-commit
reads and consumes that stdin itself to compute its own diffing context, and
exposes the result via PRE_COMMIT_* env vars instead. One consequence
inherited from pre-commit: only the first pushed ref is exposed, so
`git push --all` / multi-branch pushes only get their first branch checked.

Bypass (deliberate emergencies only): git push --no-verify
"""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
from collections.abc import Sequence

from gitguard._common import run_git, strip_refs_heads

DEFAULT_PROTECTED = ["master", "dev"]


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(prog="gitguard-no-direct-push")
    parser.add_argument(
        "--protected",
        nargs="+",
        default=DEFAULT_PROTECTED,
        help="branches that only accept merge commits (default: %(default)s)",
    )
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)

    branch = strip_refs_heads(os.environ.get("PRE_COMMIT_REMOTE_BRANCH", ""))
    if not branch or branch not in args.protected:
        return 0

    to_ref = os.environ.get("PRE_COMMIT_TO_REF") or run_git(
        "rev-parse", "-q", "--verify", f"refs/heads/{branch}"
    )
    if not to_ref:
        return 0

    from_ref = os.environ.get("PRE_COMMIT_FROM_REF", "")
    range_spec = f"{from_ref}..{to_ref}" if from_ref else to_ref

    # --first-parent restricts this to the branch's own mainline: commits
    # that only arrived as the second parent of a legitimate --no-ff merge
    # (ordinary work inside a feature branch) must not be flagged here.
    result = subprocess.run(
        ["git", "rev-list", "--no-merges", "--first-parent", range_spec],
        capture_output=True,
        text=True,
        check=False,
    )
    non_merge = result.stdout.strip()
    if not non_merge:
        return 0

    print(f"error: refusing to push directly to '{branch}'.", file=sys.stderr)
    print(
        f"       {branch} only accepts merge commits (PR/merge), not direct commits:",
        file=sys.stderr,
    )
    for line in non_merge.splitlines():
        print(f"         {line}", file=sys.stderr)
    print(
        f"       Push your work to a feat/fix/... branch and merge into {branch} instead.",
        file=sys.stderr,
    )
    print("       (deliberate override: git push --no-verify)", file=sys.stderr)
    return 1


if __name__ == "__main__":
    sys.exit(main())

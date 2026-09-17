"""gitguard: branch-name -- enforce a naming convention on new branches.

Runs at pre-push, not pre-commit: pre-commit's commit-time hooks have no
reliable way to tell "this is a brand-new branch" from a rename or an
existing one. `git ls-remote` against the actual remote is the only signal
for that which survives the trip through pre-commit's env vars, so this
only rejects a bad name the first time the branch is pushed.

Bypass (deliberate emergencies only): git push --no-verify
"""

from __future__ import annotations

import argparse
import os
import re
import subprocess
import sys
from collections.abc import Sequence

from gitguard._common import strip_refs_heads

DEFAULT_PATTERN = r"^(feat|fix|refactor|docs|chore|release|hotfix)/.+"
DEFAULT_EXEMPT = ["master", "dev"]


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(prog="gitguard-branch-name")
    parser.add_argument(
        "--pattern",
        default=DEFAULT_PATTERN,
        help="regex a new branch name must match (default: %(default)s)",
    )
    parser.add_argument(
        "--exempt",
        nargs="+",
        default=DEFAULT_EXEMPT,
        help="branches exempt from the naming check (default: %(default)s)",
    )
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)

    branch = strip_refs_heads(os.environ.get("PRE_COMMIT_REMOTE_BRANCH", ""))
    if not branch or branch in args.exempt:
        return 0

    remote_name = os.environ.get("PRE_COMMIT_REMOTE_NAME", "origin")
    already_on_remote = (
        subprocess.run(
            ["git", "ls-remote", "--exit-code", "--heads", remote_name, branch],
            capture_output=True,
            check=False,
        ).returncode
        == 0
    )
    if already_on_remote:
        return 0

    if re.match(args.pattern, branch):
        return 0

    print(f"error: branch name '{branch}' doesn't match naming convention.", file=sys.stderr)
    print(f"       expected to match: {args.pattern}", file=sys.stderr)
    print("       (deliberate override: git push --no-verify)", file=sys.stderr)
    return 1


if __name__ == "__main__":
    sys.exit(main())

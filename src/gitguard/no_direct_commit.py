"""gitguard: no-direct-commit -- block direct commits to protected branches.

A real `git commit` always has something staged against HEAD, whereas
`pre-commit run --all-files` (e.g. in CI) lints an already-finished, clean
checkout instead of creating one. MERGE_HEAD is gone by the time a merge
commit is finalized, so a clean-tree run falls back to judging the
already-made HEAD commit by its parent count instead of rejecting every
merge commit ever landed on the branch.

Bypass (deliberate emergencies only): git commit --no-verify
"""

from __future__ import annotations

import argparse
import sys
from collections.abc import Sequence

from gitguard._common import (
    current_branch,
    has_merge_head,
    has_second_parent,
    has_staged_changes,
)

DEFAULT_PROTECTED = ["master", "dev"]


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(prog="gitguard-no-direct-commit")
    parser.add_argument(
        "--protected",
        nargs="+",
        default=DEFAULT_PROTECTED,
        help="branches that only accept merge commits (default: %(default)s)",
    )
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)

    branch = current_branch()
    if not branch or branch not in args.protected:
        return 0

    if has_merge_head():
        return 0

    if not has_staged_changes() and has_second_parent():
        return 0

    print(f"error: refusing to commit directly to '{branch}'.", file=sys.stderr)
    print(
        f"       {branch} only accepts merge commits (PR/merge), not direct commits.",
        file=sys.stderr,
    )
    print("       Create a feature branch instead, e.g.:", file=sys.stderr)
    print("         git checkout -b fix/your-change", file=sys.stderr)
    print("       (deliberate override: git commit --no-verify)", file=sys.stderr)
    return 1


if __name__ == "__main__":
    sys.exit(main())

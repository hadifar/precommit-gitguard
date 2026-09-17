"""gitguard: stale-branch -- warn when the current branch is behind upstream.

Advisory only, at post-checkout: by the time this fires the checkout has
already happened, so it can't block anything.
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from collections.abc import Sequence

from gitguard._common import current_branch

DEFAULT_WATCH = ["master", "dev"]


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(prog="gitguard-stale-branch")
    parser.add_argument(
        "--watch",
        nargs="+",
        default=DEFAULT_WATCH,
        help="branches to check on checkout (default: %(default)s)",
    )
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)

    branch = current_branch()
    if not branch or branch not in args.watch:
        return 0

    upstream = subprocess.run(
        ["git", "rev-parse", "--abbrev-ref", "--symbolic-full-name", "@{u}"],
        capture_output=True,
        text=True,
        check=False,
    ).stdout.strip()
    if not upstream:
        return 0

    remote = upstream.split("/", 1)[0]
    fetched = subprocess.run(
        ["git", "fetch", "--quiet", remote, branch],
        check=False,
    )
    if fetched.returncode != 0:
        return 0

    behind = subprocess.run(
        ["git", "rev-list", "--count", f"HEAD..{upstream}"],
        capture_output=True,
        text=True,
        check=False,
    ).stdout.strip()

    if behind.isdigit() and int(behind) > 0:
        print(f"warning: '{branch}' is {behind} commit(s) behind '{upstream}'.", file=sys.stderr)
        print("         run: git pull", file=sys.stderr)

    return 0


if __name__ == "__main__":
    sys.exit(main())

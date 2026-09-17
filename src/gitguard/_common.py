"""Shared git plumbing used by every gitguard hook."""

from __future__ import annotations

import subprocess


def run_git(*args: str) -> str:
    result = subprocess.run(
        ["git", *args],
        capture_output=True,
        text=True,
        check=False,
    )
    return result.stdout.strip()


def current_branch() -> str:
    return run_git("symbolic-ref", "--short", "-q", "HEAD")


def has_merge_head() -> bool:
    return (
        subprocess.run(
            ["git", "rev-parse", "-q", "--verify", "MERGE_HEAD"],
            capture_output=True,
            check=False,
        ).returncode
        == 0
    )


def has_staged_changes() -> bool:
    return (
        subprocess.run(
            ["git", "diff", "--cached", "--quiet"],
            check=False,
        ).returncode
        != 0
    )


def has_second_parent(ref: str = "HEAD") -> bool:
    return (
        subprocess.run(
            ["git", "rev-parse", "-q", "--verify", f"{ref}^2"],
            capture_output=True,
            check=False,
        ).returncode
        == 0
    )


def strip_refs_heads(branch: str) -> str:
    return branch.removeprefix("refs/heads/")

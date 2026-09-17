from __future__ import annotations

from pathlib import Path

import pytest

from gitguard.branch_name import main


def test_blocks_new_branch_with_bad_name(
    repo_with_remote: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("PRE_COMMIT_REMOTE_BRANCH", "refs/heads/my-random-branch")
    monkeypatch.setenv("PRE_COMMIT_REMOTE_NAME", "origin")

    assert main([]) == 1


def test_allows_new_branch_matching_pattern(
    repo_with_remote: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("PRE_COMMIT_REMOTE_BRANCH", "refs/heads/feat/cool-thing")
    monkeypatch.setenv("PRE_COMMIT_REMOTE_NAME", "origin")

    assert main([]) == 0


def test_allows_branch_already_on_remote_regardless_of_name(
    repo_with_remote: Path, git_helper, monkeypatch: pytest.MonkeyPatch
) -> None:
    git_helper(repo_with_remote, "checkout", "--quiet", "-b", "my-random-branch")
    git_helper(repo_with_remote, "push", "--quiet", "-u", "origin", "my-random-branch")

    monkeypatch.setenv("PRE_COMMIT_REMOTE_BRANCH", "refs/heads/my-random-branch")
    monkeypatch.setenv("PRE_COMMIT_REMOTE_NAME", "origin")

    assert main([]) == 0


def test_exempt_branches_skip_check(
    repo_with_remote: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("PRE_COMMIT_REMOTE_BRANCH", "refs/heads/dev")
    monkeypatch.setenv("PRE_COMMIT_REMOTE_NAME", "origin")

    assert main([]) == 0


def test_custom_pattern(repo_with_remote: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("PRE_COMMIT_REMOTE_BRANCH", "refs/heads/JIRA-123-fix-bug")
    monkeypatch.setenv("PRE_COMMIT_REMOTE_NAME", "origin")

    assert main([]) == 1
    assert main(["--pattern", r"^[A-Z]+-\d+-.+"]) == 0

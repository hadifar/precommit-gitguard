from __future__ import annotations

from pathlib import Path

import pytest

from gitguard.no_direct_push import main


def test_blocks_non_merge_commit_pushed_to_protected_branch(
    repo: Path, git_helper, monkeypatch: pytest.MonkeyPatch
) -> None:
    (repo / "a.txt").write_text("x\n")
    git_helper(repo, "add", "a.txt")
    git_helper(repo, "commit", "--quiet", "-m", "direct commit")

    monkeypatch.setenv("PRE_COMMIT_REMOTE_BRANCH", "refs/heads/master")

    assert main([]) == 1


def test_allows_merge_commit_pushed_to_protected_branch(
    repo: Path, git_helper, monkeypatch: pytest.MonkeyPatch
) -> None:
    base = git_helper(repo, "rev-parse", "HEAD").stdout.strip()

    git_helper(repo, "checkout", "--quiet", "-b", "feat/x")
    (repo / "feature.txt").write_text("feature\n")
    git_helper(repo, "add", "feature.txt")
    git_helper(repo, "commit", "--quiet", "-m", "feature work")

    git_helper(repo, "checkout", "--quiet", "master")
    git_helper(repo, "merge", "--quiet", "--no-ff", "-m", "merge feat/x", "feat/x")

    monkeypatch.setenv("PRE_COMMIT_REMOTE_BRANCH", "refs/heads/master")
    monkeypatch.setenv("PRE_COMMIT_FROM_REF", base)

    assert main([]) == 0


def test_ignores_unprotected_branch(repo: Path, git_helper, monkeypatch: pytest.MonkeyPatch) -> None:
    git_helper(repo, "checkout", "--quiet", "-b", "feat/x")
    (repo / "a.txt").write_text("x\n")
    git_helper(repo, "add", "a.txt")
    git_helper(repo, "commit", "--quiet", "-m", "direct commit")

    monkeypatch.setenv("PRE_COMMIT_REMOTE_BRANCH", "refs/heads/feat/x")

    assert main([]) == 0

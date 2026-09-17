from __future__ import annotations

from pathlib import Path

import pytest

from gitguard.stale_branch import main


def test_no_warning_when_up_to_date(
    repo_with_remote: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    assert main([]) == 0
    assert capsys.readouterr().err == ""


def test_warns_when_behind_upstream(
    repo_with_remote: Path, git_helper, capsys: pytest.CaptureFixture[str]
) -> None:
    remote = repo_with_remote.parent / "remote.git"
    other_clone = repo_with_remote.parent / "other_clone"
    git_helper(repo_with_remote.parent, "clone", "--quiet", str(remote), str(other_clone))
    git_helper(other_clone, "config", "user.email", "test@example.com")
    git_helper(other_clone, "config", "user.name", "Test")

    (other_clone / "new.txt").write_text("new\n")
    git_helper(other_clone, "add", "new.txt")
    git_helper(other_clone, "commit", "--quiet", "-m", "new commit")
    git_helper(other_clone, "push", "--quiet")

    assert main([]) == 0
    err = capsys.readouterr().err
    assert "behind" in err


def test_ignores_unwatched_branch(repo_with_remote: Path, git_helper) -> None:
    git_helper(repo_with_remote, "checkout", "--quiet", "-b", "feat/x")

    assert main([]) == 0


def test_no_upstream_configured(repo: Path) -> None:
    # `repo` fixture has no remote at all.
    assert main([]) == 0

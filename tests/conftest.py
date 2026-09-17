from __future__ import annotations

import subprocess
from pathlib import Path

import pytest


def _git(repo: Path, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["git", *args],
        cwd=repo,
        capture_output=True,
        text=True,
        check=True,
    )


def _init_repo(path: Path, *, branch: str = "master") -> Path:
    path.mkdir(parents=True, exist_ok=True)
    _git(path, "init", "--quiet", "--initial-branch", branch)
    _git(path, "config", "user.email", "test@example.com")
    _git(path, "config", "user.name", "Test")
    return path


@pytest.fixture
def repo(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """A repo with one commit on master, cwd set to it."""
    path = _init_repo(tmp_path / "repo")
    (path / "README.md").write_text("hello\n")
    _git(path, "add", "README.md")
    _git(path, "commit", "--quiet", "-m", "initial commit")
    monkeypatch.chdir(path)
    return path


@pytest.fixture
def repo_with_remote(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """A repo with one commit on master, plus a bare 'origin' it tracks."""
    remote = _init_repo(tmp_path / "remote.git", branch="master")
    _git(remote, "config", "receive.denyCurrentBranch", "ignore")
    (remote / "README.md").write_text("hello\n")
    _git(remote, "add", "README.md")
    _git(remote, "commit", "--quiet", "-m", "initial commit")

    path = tmp_path / "repo"
    _git(tmp_path, "clone", "--quiet", str(remote), str(path))
    _git(path, "config", "user.email", "test@example.com")
    _git(path, "config", "user.name", "Test")

    monkeypatch.chdir(path)
    return path


@pytest.fixture
def git_helper():
    return _git

from __future__ import annotations

from pathlib import Path

from gitguard.no_direct_commit import main


def test_blocks_staged_commit_on_protected_branch(repo: Path, git_helper) -> None:
    (repo / "a.txt").write_text("x\n")
    git_helper(repo, "add", "a.txt")

    assert main([]) == 1


def test_allows_staged_commit_on_feature_branch(repo: Path, git_helper) -> None:
    git_helper(repo, "checkout", "--quiet", "-b", "feat/x")
    (repo / "a.txt").write_text("x\n")
    git_helper(repo, "add", "a.txt")

    assert main([]) == 0


def test_allows_when_merge_head_present(repo: Path, git_helper) -> None:
    (repo / "a.txt").write_text("x\n")
    git_helper(repo, "add", "a.txt")
    (repo / ".git" / "MERGE_HEAD").write_text(git_helper(repo, "rev-parse", "HEAD").stdout)

    assert main([]) == 0


def test_ci_lint_of_finished_merge_commit_is_allowed(repo: Path, git_helper) -> None:
    git_helper(repo, "checkout", "--quiet", "-b", "feat/x")
    (repo / "feature.txt").write_text("feature\n")
    git_helper(repo, "add", "feature.txt")
    git_helper(repo, "commit", "--quiet", "-m", "feature work")

    git_helper(repo, "checkout", "--quiet", "master")
    git_helper(repo, "merge", "--quiet", "--no-ff", "-m", "merge feat/x", "feat/x")

    # Clean tree, HEAD is the merge commit just landed -- simulates
    # `pre-commit run --all-files` in CI against a finished checkout.
    assert main([]) == 0


def test_ci_lint_of_clean_non_merge_head_is_blocked(repo: Path) -> None:
    # Clean tree (nothing staged), but HEAD has only one parent.
    assert main([]) == 1


def test_custom_protected_list(repo: Path, git_helper) -> None:
    git_helper(repo, "checkout", "--quiet", "-b", "release/1.0")
    (repo / "a.txt").write_text("x\n")
    git_helper(repo, "add", "a.txt")

    assert main([]) == 0
    assert main(["--protected", "release/1.0"]) == 1

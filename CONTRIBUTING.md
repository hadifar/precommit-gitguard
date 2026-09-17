# Contributing

## Setup

This project uses [uv](https://docs.astral.sh/uv/).

```console
git clone https://github.com/hadifar/precommit-gitguard.git
cd precommit-gitguard
uv sync --extra dev
```

## Project layout

Each hook is a small `argparse` CLI under `src/gitguard/`, exposed via a
`console_scripts` entry point in `pyproject.toml` and wired up in
`.pre-commit-hooks.yaml`. Shared git plumbing lives in `src/gitguard/_common.py`.

## Adding or changing a hook

1. Add/edit the module under `src/gitguard/` (`main(argv)` returning an exit code).
2. Register its entry point in `pyproject.toml` under `[project.scripts]`.
3. Add/update its entry in `.pre-commit-hooks.yaml` (id, stage, description).
4. Add tests in `tests/` against a real tmp git repo (see `tests/conftest.py`
   fixtures `repo` and `repo_with_remote`) -- exercise the exit code, not
   just that it doesn't crash.
5. Document new/changed `args` in the README's override table.

## Running checks locally

```console
uv run pytest              # unit tests
uv run ruff check .        # lint
uv run pre-commit run --all-files                    # hygiene + pytest, pre-commit stage
uv run pre-commit run --all-files --hook-stage pre-push   # pyright, pre-push stage
```

CI (`.github/workflows/ci.yml`) runs all of the above across Python 3.9 and
3.12, plus a `pre-commit try-repo` integration check against the published
hook ids themselves.

## Commit messages

Commit messages on `dev` (i.e. your PR title, if you squash-merge) must
follow [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>: <description>

feat:     a new hook or new behavior
fix:      a bug fix
docs:     documentation only
refactor: no behavior change
perf:     performance improvement
test:     test-only change
build:    packaging/build system
ci:       CI/workflow change
chore:    everything else (no release impact)
```

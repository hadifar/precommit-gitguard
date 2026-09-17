# gitguard

Gitflow guardrails, packaged as reusable [pre-commit](https://pre-commit.com) hooks:
protect branches from direct commits/pushes, enforce branch naming, and warn
about stale branches.

## Usage

```yaml
- repo: https://github.com/hadifar/precommit-gitguard
  rev: v0.1.0  # pin to a tag
  hooks:
    - id: no-direct-commit
    - id: no-direct-push
    - id: branch-name
    - id: stale-branch
```

`no-direct-push`, `branch-name`, and `stale-branch` run at pre-push /
post-checkout, which pre-commit doesn't install by default. After adding
this to `.pre-commit-config.yaml`, run:

```console
pre-commit install --hook-type pre-commit --hook-type pre-push --hook-type post-checkout
```

## Hooks

| id | stage | what it does |
| --- | --- | --- |
| `no-direct-commit` | pre-commit | Blocks `git commit` on a protected branch unless it finalizes a merge. |
| `no-direct-push` | pre-push | Blocks pushing non-merge commits directly onto a protected branch. |
| `branch-name` | pre-push | On a branch's first push, requires its name to match a pattern. |
| `stale-branch` | post-checkout | Warns (doesn't block) if the branch you checked out is behind its upstream. |

All hooks default to treating `master` and `dev` as protected/watched, and
`branch-name` defaults to requiring `(feat|fix|refactor|docs|chore|release|hotfix)/...`.
Override via `args`:

```yaml
    - id: no-direct-commit
      args: [--protected, main]
    - id: no-direct-push
      args: [--protected, main]
    - id: branch-name
      args: [--pattern, '^[A-Z]+-\d+-.+', --exempt, main]
    - id: stale-branch
      args: [--watch, main]
```

Every hook can be bypassed deliberately with `git commit --no-verify` /
`git push --no-verify`.

## Development

```console
pip install -e ".[dev]"
pytest
pre-commit run --all-files
```

Each hook is a small `argparse` CLI under `src/gitguard/`, exposed via a
`console_scripts` entry point in `pyproject.toml` and wired up in
`.pre-commit-hooks.yaml`. Shared git plumbing lives in `src/gitguard/_common.py`.

## Releasing

Tag a release (`git tag vX.Y.Z && git push --tags`); consumers pin `rev` to
that tag in their own `.pre-commit-config.yaml`. Never move a published tag.

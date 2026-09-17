# gitguard

[![CI](https://github.com/hadifar/precommit-gitguard/actions/workflows/ci.yml/badge.svg)](https://github.com/hadifar/precommit-gitguard/actions/workflows/ci.yml)
[![Version](https://img.shields.io/github/v/tag/hadifar/precommit-gitguard?label=version&sort=semver)](https://github.com/hadifar/precommit-gitguard/tags)
[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)](https://pre-commit.com)
[![License: MIT](https://img.shields.io/github/license/hadifar/precommit-gitguard)](LICENSE)

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

To add a third long-lived branch (e.g. `staging`), pass it to every hook's
`--protected` / `--exempt` / `--watch` flag alongside `master` and `dev`, so
it's treated the same way -- naming-exempt, commit/push protected, and
watched for staleness:

```yaml
- repo: https://github.com/hadifar/precommit-gitguard
  rev: v0.1.0
  hooks:
    - id: no-direct-commit
      args: [--protected, master, dev, staging]
    - id: no-direct-push
      args: [--protected, master, dev, staging]
    - id: branch-name
      args: [--exempt, master, dev, staging]
    - id: stale-branch
      args: [--watch, master, dev, staging]
```

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md).

## License

[MIT](LICENSE)
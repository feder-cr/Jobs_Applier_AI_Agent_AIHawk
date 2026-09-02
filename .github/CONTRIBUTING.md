# Contributing to AIHawk

Thanks for being here. This page says what this repository is, so you can tell
in one minute whether your change belongs here or in one of the packages.

## What lives in this repository

Documentation, and nothing else. There is no application to build or run here:
the browser, the MCP server and the fingerprint work all live in separate
packages, and this repository is the front door that explains them.

That means a change here is a change to prose: the README, this file, the issue
templates. If you are fixing behaviour, you want one of the repositories below.

## Where the code is

| Repository | What it holds |
|---|---|
| [invisible-playwright-mcp](https://github.com/feder-cr/invisible-playwright-mcp) | The MCP server the README tells you to install. The tools your client sees are defined here. |
| [invisible_playwright](https://github.com/feder-cr/invisible_playwright) | The Python wrapper, the launcher, and the patched browser it pins and drives. |
| [invisible_core](https://github.com/feder-cr/invisible_core) | Seed to fingerprint to preferences, plus proxy and geolocation. |

Each has its own tests and its own setup instructions. A few examples of where
things go:

- a tool that returns the wrong thing, or a click that does not land, is
  `invisible-playwright-mcp`
- the browser failing to start, a proxy not being used, a timezone that does not
  match the exit country, is `invisible_playwright` or `invisible_core`
- a detector spotting the browser is usually the engine, not this repository
- an install command here that does not work, or an explanation that is wrong,
  is this repository

If you are not sure, open the issue here and it will be moved.

## Opening an issue

Use one of the [templates](https://github.com/feder-cr/AIHawk/issues/new/choose):
bug report, feature request, or documentation request. Before you do, please
search the open and closed issues, because the same thing is often already
there.

For a bug, the two things that decide how fast it can be answered are the exact
commands you ran and what happened instead of what you expected. Include your OS
and Python version, and which client you attached the server to.

Please do not report a security problem in a public issue.

## Pull requests

Fork, branch, open the pull request against `main`. There is no `develop`
branch and no release train: this repository has one branch.

Keep a pull request to one change, and say in the description what a reader
would be able to do afterwards that they could not do before. If you are
changing an install command or a configuration snippet, run it first: the tests
for a documentation repository are a person reading it, so the only real check
is whether what it says is true today.

## Tone

Questions are welcome and beginners are welcome. If something in the README was
not clear enough for you, that is worth an issue on its own, because it was
probably not clear to somebody else either.

## Licence

By contributing you agree that your contribution is licensed under the MIT
licence, which is the licence in [LICENSE](../LICENSE). Everything received
before 2 September 2026 was contributed under AGPL-3.0 and stays under it: a
licence already granted is not withdrawn by changing that file.

Participation is covered by the [Code of Conduct](CODE_OF_CONDUCT.md).

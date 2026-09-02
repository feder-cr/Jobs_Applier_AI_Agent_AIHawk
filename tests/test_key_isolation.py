"""The OpenRouter key must never reach the browser child process.

`runner.child_env` builds the environment handed to the stdio child that runs
`invisible_playwright_mcp`, which in turn launches Firefox. The key belongs to
the parent only: the parent talks to OpenRouter, the child talks to a browser.
A commit in this repository calls the removal a security fix, and the history
carries a PR titled "Replace the committed API key", so the guarantee is not
theoretical.

Every test below names the known-bad input that breaks it. The two tests marked
xfail(strict=True) assert guarantees the code does NOT yet provide: they are
reachable leaks, not accepted trade-offs, and the strict marker turns the suite
red the moment somebody fixes `child_env` without deleting the marker.

None of these tests launch a browser or spawn the MCP server. The one test that
exercises `drive` replaces the transport with fakes.
"""
from __future__ import annotations

import contextlib
import os
import sys

import pytest

from aihawk import runner
from aihawk.runner import child_env

# A sentinel that cannot occur by accident inside PATH or any other real value.
KEY = "sk-or-v1-TESTSENTINEL-do-not-ship-0123456789"
KEY_NAME = "OPENROUTER_API_KEY"


def values_carrying(env, needle):
    """Names of every variable whose VALUE contains `needle`."""
    return sorted(name for name, value in env.items() if needle in str(value))


# ---------------------------------------------------------------------------
# the key is removed
# ---------------------------------------------------------------------------


def test_child_env_strips_the_key_by_name():
    """Known-bad: delete the `env.pop("OPENROUTER_API_KEY", None)` line and the
    child inherits the key verbatim under its own name."""
    env = child_env({}, {"PATH": "/x", KEY_NAME: KEY})
    assert KEY_NAME not in env
    assert env["PATH"] == "/x", "unrelated base variables must survive"


def test_no_variable_name_matches_the_key_name_in_any_case():
    """The pop is exact-match, so this asserts the OUTCOME rather than the call.

    Known-bad: replace the pop with `env.pop("OPENROUTER_KEY", None)` - a
    plausible typo that leaves the real name in place and that a test asserting
    `"OPENROUTER_KEY" not in env` would happily pass.
    """
    env = child_env({}, {KEY_NAME: KEY, "PATH": "/x"})
    assert [n for n in env if n.upper() == KEY_NAME] == []


def test_the_key_string_appears_in_no_value_at_all():
    """The guarantee that matters is about the VALUE, not the name: scan the
    whole dict.

    Known-bad: `env.pop(KEY_NAME)` replaced by `env[KEY_NAME] = ""`, which
    satisfies a name-only assertion in some shapes and, more importantly, any
    future change that copies the key into a second variable for the child.
    """
    base = {"PATH": "/x", "HOME": "/home/u", KEY_NAME: KEY, "AIHAWK_MODEL": "z-ai/glm-4.6"}
    env = child_env({"proxy": "http://h:1", "seed": 7, "binary": "C:/ff.exe"}, base)
    assert values_carrying(env, KEY) == []


def test_the_key_string_appears_in_no_value_when_it_is_also_an_option():
    """A user who passes the key as a proxy password or a profile path would be
    doing something strange, but the STEALTHFOX_* values are the ones this code
    writes itself, so they are the ones it is responsible for.

    Known-bad: a future `env["STEALTHFOX_OPENROUTER_KEY"] = key` added to give
    the child a model of its own.
    """
    env = child_env({"proxy": "http://h:1", "seed": 1}, {KEY_NAME: KEY})
    stealthfox = {n: v for n, v in env.items() if n.startswith("STEALTHFOX_")}
    assert stealthfox, "the fixture must actually produce STEALTHFOX_ values"
    assert values_carrying(stealthfox, KEY) == []


# ---------------------------------------------------------------------------
# case: what os.environ does here, measured rather than assumed
# ---------------------------------------------------------------------------


@pytest.mark.skipif(sys.platform != "win32", reason="os.environ is case-sensitive off Windows")
def test_windows_normalises_a_lowercase_name_so_the_exact_pop_still_catches_it(monkeypatch):
    """Measured on this machine: `os.environ` is `os._Environ` with
    `encodekey = str.upper`, so `set openrouter_api_key=...` in the shell is
    stored and enumerated as OPENROUTER_API_KEY. The exact-match pop therefore
    covers every case variant that a Windows shell can produce.

    This test asserts the platform contract as well as the outcome, so that if a
    future Python stops upper-casing, the failure names the reason instead of
    looking like a regression in child_env.

    Known-bad: on a Python where `dict(os.environ)` preserved the caller's case,
    the pop would miss and the child would inherit the key. That is exactly the
    xfail below, reached through a plain mapping.
    """
    monkeypatch.setenv("openrouter_api_key", KEY)
    assert os.environ.get(KEY_NAME) == KEY, "Windows environ no longer upper-cases names"
    assert "openrouter_api_key" not in dict(os.environ)

    env = child_env({}, os.environ)
    assert values_carrying(env, KEY) == []


@pytest.mark.xfail(
    strict=True,
    reason=(
        "REAL GAP, not an accepted trade-off: child_env pops one exact name. A "
        "lowercase variable survives on any case-sensitive platform (POSIX) and "
        "through any caller that passes a plain dict. Delete this marker when "
        "child_env drops names case-insensitively."
    ),
)
def test_a_case_variant_name_in_a_plain_mapping_is_stripped_too():
    """Known-bad is the current code: `env.pop("OPENROUTER_API_KEY", None)`
    against a mapping holding `openrouter_api_key`."""
    env = child_env({}, {"PATH": "/x", "openrouter_api_key": KEY})
    assert values_carrying(env, KEY) == []


@pytest.mark.xfail(
    strict=True,
    reason=(
        "REAL GAP: child_env removes the key by NAME and never scans values, so "
        "a duplicate under a second name reaches the browser child. Setting "
        "OPENAI_API_KEY to an OpenRouter key is common practice, since the "
        "client is OpenAI-compatible. Delete this marker when child_env drops "
        "every variable whose value equals the resolved key."
    ),
)
def test_a_duplicate_of_the_key_under_another_name_is_stripped_too():
    """Known-bad is the current code: the same secret under OPENAI_API_KEY is
    copied straight into the child environment."""
    env = child_env({}, {"PATH": "/x", KEY_NAME: KEY, "OPENAI_API_KEY": KEY})
    assert values_carrying(env, KEY) == []


# ---------------------------------------------------------------------------
# what SHOULD reach the child does
# ---------------------------------------------------------------------------


def test_every_option_maps_to_its_stealthfox_name():
    """Known-bad: rename any one of these to a name the MCP server does not read
    (STEALTHFOX_PROXY_URL, STEALTHFOX_HEADED) and the option becomes a silent
    no-op - the run still succeeds, just without the proxy or the seed."""
    env = child_env(
        {
            "proxy": "http://u:p@h:8080",
            "seed": 42,
            "headed": True,
            "binary": "C:/ff.exe",
            "profile_dir": "C:/prof",
        },
        {"PATH": "/x"},
    )
    assert env["STEALTHFOX_PROXY"] == "http://u:p@h:8080"
    assert env["STEALTHFOX_SEED"] == "42"
    assert env["STEALTHFOX_HEADLESS"] == "0"
    assert env["STEALTHFOX_BINARY"] == "C:/ff.exe"
    assert env["STEALTHFOX_PROFILE_DIR"] == "C:/prof"


def test_seed_zero_is_a_seed_and_not_an_absent_option():
    """Known-bad: `if opts.get("seed") is not None` weakened to
    `if opts.get("seed")`. Seed 0 is a valid deterministic fingerprint, and
    dropping it silently hands the run a random identity instead - a failure
    that no exception reports and that every other seed test misses."""
    env = child_env({"seed": 0}, {})
    assert env["STEALTHFOX_SEED"] == "0"


def test_absent_options_add_no_variable_rather_than_an_empty_one():
    """An empty string is not the same as unset: the child reads these with
    os.environ.get, so STEALTHFOX_PROXY="" is a truthy PRESENCE for any code
    that checks membership, and can select a proxy path with no proxy.

    Known-bad: rewriting the body as unconditional
    `env["STEALTHFOX_PROXY"] = str(opts.get("proxy") or "")` for each option.
    """
    env = child_env({}, {"PATH": "/x"})
    assert [n for n in env if n.startswith("STEALTHFOX_")] == []

    explicit_none = child_env(
        {"proxy": None, "seed": None, "headed": False, "binary": None, "profile_dir": None},
        {"PATH": "/x"},
    )
    assert [n for n in explicit_none if n.startswith("STEALTHFOX_")] == []


def test_no_emitted_variable_is_an_empty_string():
    """The class assertion behind the test above: whatever options exist now or
    later, none of them may be emitted empty.

    Known-bad: an option added later that maps a falsy value through str().
    """
    env = child_env({"proxy": "", "binary": "", "profile_dir": "", "seed": 3}, {"PATH": "/x"})
    assert [n for n, v in env.items() if v == ""] == []


def test_headed_false_sets_nothing_so_the_default_stays_headless():
    """Known-bad: `env["STEALTHFOX_HEADLESS"] = "0" if opts.get("headed") else "1"`
    looks harmless and pins the value, removing the server's own default."""
    env = child_env({"headed": False}, {})
    assert "STEALTHFOX_HEADLESS" not in env


def test_the_result_is_a_plain_str_to_str_dict():
    """StdioServerParameters declares env as dict[str, str] and validates it, so
    a non-str value raises at spawn time rather than at build time.

    Known-bad: dropping the str() around opts["seed"], which is typed int by the
    CLI, so the failure only appears when --seed is actually used.
    """
    env = child_env({"seed": 42, "proxy": "http://h:1"}, {"PATH": "/x"})
    assert type(env) is dict
    assert all(isinstance(n, str) and isinstance(v, str) for n, v in env.items())


# ---------------------------------------------------------------------------
# the base environment is not mutated
# ---------------------------------------------------------------------------


def test_the_base_mapping_is_not_mutated():
    """Known-bad: `env = base_env` instead of `env = dict(base_env)`. The pop
    then deletes the key from the caller's mapping - and the real caller passes
    os.environ, so the parent loses its own key. The first run works, and a
    second run in the same process cannot authenticate."""
    base = {"PATH": "/x", KEY_NAME: KEY}
    before = dict(base)
    env = child_env({"proxy": "http://h:1"}, base)

    assert base == before, "child_env must not touch the mapping it was given"
    assert base[KEY_NAME] == KEY
    assert env is not base


def test_os_environ_itself_survives_the_call(monkeypatch):
    """The same guarantee against the mapping the production path actually
    passes, which is os._Environ and not a dict.

    Known-bad: the aliasing bug above, which a dict-only test still catches, plus
    any future in-place scrub such as `base_env.pop(...)` before copying.
    """
    monkeypatch.setenv(KEY_NAME, KEY)
    env = child_env({"seed": 1}, os.environ)
    assert os.environ[KEY_NAME] == KEY
    assert KEY_NAME not in env


# ---------------------------------------------------------------------------
# the wiring: child_env being correct is worthless if drive does not use it
# ---------------------------------------------------------------------------


class _FakeSession:
    def __init__(self, read, write):
        self.read, self.write = read, write

    async def __aenter__(self):
        return self

    async def __aexit__(self, *exc):
        return False

    async def initialize(self):
        return None


async def test_drive_hands_the_child_the_scrubbed_environment(monkeypatch):
    """No browser and no child process: the transport, the OpenAI client and the
    agent loop are all replaced, and only the StdioServerParameters are read.

    This is the test that fails if somebody bypasses the helper. Known-bad:
    `env=dict(os.environ)` in drive, or dropping the `env=` argument, both of
    which leave every child_env test above green while the key ships to the
    child (the first) or every STEALTHFOX_* option silently stops working (the
    second).
    """
    monkeypatch.setenv(KEY_NAME, KEY)
    captured = {}

    @contextlib.asynccontextmanager
    async def fake_stdio_client(params):
        captured["params"] = params
        yield ("read", "write")

    async def fake_run_task(mcp, task, *, client, model):
        captured["task"] = task
        captured["model"] = model
        return "FINAL"

    monkeypatch.setattr(runner, "stdio_client", fake_stdio_client)
    monkeypatch.setattr(runner, "ClientSession", _FakeSession)
    monkeypatch.setattr(runner, "run_task", fake_run_task)
    monkeypatch.setattr(runner, "make_client", lambda key: ("client-for", key))

    out = await runner.drive(
        "read the page",
        opts={"proxy": "http://h:1", "seed": 5},
        key=KEY,
        model="z-ai/glm-4.6",
    )

    assert out == "FINAL"
    params = captured["params"]
    assert params.command == sys.executable
    assert params.args == ["-m", "invisible_playwright_mcp"]

    child = params.env
    assert child is not None, "an explicit environment is what carries the options"
    assert KEY_NAME not in child
    assert values_carrying(child, KEY) == []
    assert child["STEALTHFOX_PROXY"] == "http://h:1"
    assert child["STEALTHFOX_SEED"] == "5"
    assert os.environ[KEY_NAME] == KEY, "the parent keeps its own key"


async def test_drive_keeps_the_key_in_the_parent_client_only(monkeypatch):
    """The key must reach the OpenAI-compatible client and nothing else.

    Known-bad: passing the key into the child to let the server call the model
    itself, which would make every assertion above pointless while drive still
    returned the right answer.
    """
    monkeypatch.setenv(KEY_NAME, KEY)
    seen = {}

    @contextlib.asynccontextmanager
    async def fake_stdio_client(params):
        seen["env"] = params.env
        yield ("read", "write")

    async def fake_run_task(mcp, task, *, client, model):
        seen["client"] = client
        return "FINAL"

    monkeypatch.setattr(runner, "stdio_client", fake_stdio_client)
    monkeypatch.setattr(runner, "ClientSession", _FakeSession)
    monkeypatch.setattr(runner, "run_task", fake_run_task)
    monkeypatch.setattr(runner, "make_client", lambda key: {"api_key": key})

    await runner.drive("t", opts={}, key=KEY, model="m")

    assert seen["client"] == {"api_key": KEY}, "the parent client must get the key"
    assert values_carrying(seen["env"], KEY) == [], "the child must not"

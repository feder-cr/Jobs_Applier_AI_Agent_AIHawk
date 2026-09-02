"""The command line as a person meets it.

No browser and no model are involved here: `aihawk.cli.drive` is replaced by a
recorder, so every test asserts what the CLI decided and handed over, not what
the browser did.

The theme of this file is the API key. `aihawk` takes an OpenRouter key and
nothing else, and a key that reaches the terminal is a key in a scrollback
buffer, a CI log and a screen recording. FAKE_KEY below carries the marker
CANARY on purpose so any echo of it, whole or truncated after the prefix, is
recognisable; test_the_key_detector_is_not_vacuous proves the detector can
actually see a leak instead of always printing PASS.
"""
from __future__ import annotations

import traceback

import click
import pytest
from click.testing import CliRunner

import aihawk.cli as climod
from aihawk.llm import BASE_URL, DEFAULT_MODEL
from aihawk.runner import child_env

# A key shaped like a real OpenRouter key, with a marker in the middle so that a
# partial echo ("sk-or-v1-CANARY...") trips the detector too.
FAKE_KEY = "sk-or-v1-CANARY-9f3b2a7c-do-not-echo"
KEY_MARKER = "CANARY"
DECOY_ENV_KEY = "sk-or-v1-CANARY-env-decoy-must-lose"

# Every option `aihawk do` declares itself. --help is added by click at parse
# time and is not one of ours, so it is checked against the rendered help only.
DECLARED_OPTIONS = {
    "--openrouter-key",
    "--model",
    "--proxy",
    "--seed",
    "--headed",
    "--binary",
    "--profile-dir",
}


def key_leaked(text: str) -> bool:
    """True if a recognisable piece of FAKE_KEY appears in text."""
    return FAKE_KEY in text or KEY_MARKER in text


@pytest.fixture(autouse=True)
def clean_provider_env(monkeypatch):
    """No provider variable may reach a test from the developer's own shell.

    Known-bad this guards: a machine that happens to export OPENROUTER_API_KEY
    would turn the "no key anywhere" test green while the CLI was broken.
    """
    for name in ("OPENROUTER_API_KEY", "AIHAWK_MODEL", "OPENAI_API_KEY",
                 "ANTHROPIC_API_KEY"):
        monkeypatch.delenv(name, raising=False)


class DriveRecorder:
    """Stands in for runner.drive: records the call, returns a fixed result."""

    def __init__(self, result: str = "RESULT", raises: Exception | None = None):
        self.result = result
        self.raises = raises
        self.calls: list[dict] = []

    async def __call__(self, task, *, opts, key, model):
        self.calls.append(
            {"task": task, "opts": dict(opts), "key": key, "model": model}
        )
        if self.raises is not None:
            raise self.raises
        return self.result

    @property
    def call(self) -> dict:
        assert len(self.calls) == 1, f"expected one drive call, got {len(self.calls)}"
        return self.calls[0]


@pytest.fixture
def drive(monkeypatch):
    rec = DriveRecorder()
    monkeypatch.setattr(climod, "drive", rec)
    return rec


def run(*args, **kwargs):
    return CliRunner().invoke(climod.main, list(args), **kwargs)


# --------------------------------------------------------------------------
# the key: where it comes from, and what happens when it is missing
# --------------------------------------------------------------------------

def test_missing_key_exits_one_and_names_both_ways_to_supply_one(drive):
    """No key on the command line and none in the environment is a clean refusal.

    Exit code 1 is asserted, not merely "non-zero": 2 would mean click rejected
    the command line before our own check ran, and 0 with a message on stderr is
    the classic known-bad here, since a shell script testing $? would carry on.
    The message must name both routes; naming only the flag strands a user who
    keeps the key in the environment, and vice versa.
    """
    result = run("do", "read the page")

    assert result.exit_code == 1, result.output
    assert "--openrouter-key" in result.output
    assert "OPENROUTER_API_KEY" in result.output
    assert drive.calls == [], "a missing key must not spawn the browser"


def test_explicit_key_wins_and_the_environment_is_not_consulted(drive, monkeypatch):
    """--openrouter-key beats a key already exported in the shell.

    Known-bad: resolve_key(os.environ.get(...) or explicit, ...) reads perfectly
    well and silently prefers the environment, so a user who passes a second
    account's key on the command line would keep billing the first one.
    """
    monkeypatch.setenv("OPENROUTER_API_KEY", DECOY_ENV_KEY)

    result = run("do", "t", "--openrouter-key", FAKE_KEY)

    assert result.exit_code == 0, result.output
    assert drive.call["key"] == FAKE_KEY
    assert drive.call["key"] != DECOY_ENV_KEY


def test_key_is_taken_from_the_environment_when_the_flag_is_absent(drive, monkeypatch):
    """The documented fallback works. Known-bad: reading a differently spelled
    variable, which would leave every environment user stranded on the error
    path with a key correctly exported."""
    monkeypatch.setenv("OPENROUTER_API_KEY", FAKE_KEY)

    result = run("do", "t")

    assert result.exit_code == 0, result.output
    assert drive.call["key"] == FAKE_KEY


def test_an_openai_key_in_the_environment_is_not_accepted(drive, monkeypatch):
    """Only an OpenRouter key, which is the owner's second requirement.

    Known-bad: adding OPENAI_API_KEY to the fallback chain "for convenience".
    That is not a convenience, it is a credential for one vendor being sent to
    another vendor's endpoint by a user who never asked for it. The refusal is
    asserted through the exit code and through drive never being called.
    """
    monkeypatch.setenv("OPENAI_API_KEY", FAKE_KEY)

    result = run("do", "t")

    assert result.exit_code == 1, result.output
    assert drive.calls == []
    assert not key_leaked(result.output)


def test_the_command_offers_no_second_provider():
    """The set of options is pinned, so a new provider cannot arrive unnoticed.

    Known-bad: --openai-key, --anthropic-key or --base-url appearing later.
    Equality is used rather than a membership check precisely so that an added
    option fails this test instead of passing it.
    """
    options = [p for p in climod.do.params if isinstance(p, click.Option)]
    names = {opt for param in options for opt in param.opts}
    arguments = [p.name for p in climod.do.params if isinstance(p, click.Argument)]

    assert names == DECLARED_OPTIONS
    assert arguments == ["task"]
    assert BASE_URL.startswith("https://openrouter.ai/"), BASE_URL


def test_the_cli_does_not_put_the_key_into_its_own_environment(drive, monkeypatch):
    """The key stays a parameter and never becomes an environment variable.

    Known-bad: passing it down by writing os.environ["OPENROUTER_API_KEY"], the
    obvious shortcut, which would then be inherited by the browser child process
    that runner.child_env exists to strip it from.
    """
    import os

    run("do", "t", "--openrouter-key", FAKE_KEY)

    assert "OPENROUTER_API_KEY" not in os.environ


# --------------------------------------------------------------------------
# options: name, type, and the value that actually arrives
# --------------------------------------------------------------------------

def test_every_option_reaches_drive_with_the_right_name_and_type(drive):
    """One invocation setting everything, compared against an exact dict.

    Known-bad this catches: --profile-dir arriving as "profileDir", --seed
    arriving as the string "4242", or --headed arriving as None instead of a
    bool. None of those raise anything anywhere; they just quietly stop working
    once the value reaches runner.child_env, which reads by key.
    """
    result = run(
        "do", "read the page",
        "--openrouter-key", FAKE_KEY,
        "--model", "openai/gpt-4o-mini",
        "--proxy", "http://user:pw@host:8080",
        "--seed", "4242",
        "--headed",
        "--binary", "C:/ff/firefox.exe",
        "--profile-dir", "C:/tmp/aihawk-profile",
    )

    assert result.exit_code == 0, result.output
    call = drive.call
    assert call["task"] == "read the page"
    assert call["model"] == "openai/gpt-4o-mini"
    assert call["opts"] == {
        "proxy": "http://user:pw@host:8080",
        "seed": 4242,
        "headed": True,
        "binary": "C:/ff/firefox.exe",
        "profile_dir": "C:/tmp/aihawk-profile",
    }
    seed = call["opts"]["seed"]
    assert isinstance(seed, int) and not isinstance(seed, bool)
    assert isinstance(call["opts"]["headed"], bool)


def test_defaults_are_none_headless_and_the_default_model(drive):
    """A bare `aihawk do TASK` with a key and nothing else.

    Known-bad: a default of "" instead of None for --proxy, which child_env
    treats as falsy today but which any later `if "proxy" in opts` would treat as
    a configured proxy.
    """
    result = run("do", "t", "--openrouter-key", FAKE_KEY)

    assert result.exit_code == 0, result.output
    assert drive.call["opts"] == {
        "proxy": None,
        "seed": None,
        "headed": False,
        "binary": None,
        "profile_dir": None,
    }
    assert drive.call["model"] == DEFAULT_MODEL


def test_the_option_names_are_the_ones_the_runner_reads(drive):
    """Cross-module: the dict the CLI builds is fed to the real child_env.

    This is the trap for the rename described above, asserted end to end rather
    than described. child_env reads opts by key with .get(), so a renamed key
    produces no error at all: the browser simply launches with no proxy, no seed
    and no profile. Here every option must come out as its STEALTHFOX_ variable,
    and the API key must not come out at all.
    """
    run(
        "do", "t",
        "--openrouter-key", FAKE_KEY,
        "--proxy", "http://host:8080",
        "--seed", "7",
        "--headed",
        "--binary", "C:/ff/firefox.exe",
        "--profile-dir", "C:/tmp/prof",
    )

    env = child_env(drive.call["opts"], {"OPENROUTER_API_KEY": FAKE_KEY})

    assert env["STEALTHFOX_PROXY"] == "http://host:8080"
    assert env["STEALTHFOX_SEED"] == "7"
    assert env["STEALTHFOX_HEADLESS"] == "0"
    assert env["STEALTHFOX_BINARY"] == "C:/ff/firefox.exe"
    assert env["STEALTHFOX_PROFILE_DIR"] == "C:/tmp/prof"
    assert "OPENROUTER_API_KEY" not in env
    assert not key_leaked(repr(env))


def test_without_headed_the_child_is_left_headless(drive):
    """Omitting --headed must leave STEALTHFOX_HEADLESS unset.

    Known-bad: is_flag defaulting to True, or the CLI writing "1"/"0" for both
    cases, either of which would open a visible browser on a machine where that
    is a measurement hazard.
    """
    run("do", "t", "--openrouter-key", FAKE_KEY)

    assert "STEALTHFOX_HEADLESS" not in child_env(drive.call["opts"], {})


def test_a_non_numeric_seed_is_a_usage_error(drive):
    """--seed abc is rejected by click before anything is launched.

    Exit code 2 is the assertion: 1 would mean our own code accepted the string
    and failed later, 0 would mean it accepted it outright and the fingerprint
    seed silently became a string.
    """
    result = run("do", "t", "--openrouter-key", FAKE_KEY, "--seed", "abc")

    assert result.exit_code == 2, result.output
    assert "--seed" in result.output
    assert drive.calls == []


def test_the_task_argument_is_required(drive):
    """`aihawk do` with no task is a usage error naming the argument.

    Known-bad: a default of "" for TASK, which would send an empty task to the
    model and spend a browser launch and tokens on nothing.
    """
    result = run("do")

    assert result.exit_code == 2, result.output
    assert "TASK" in result.output
    assert drive.calls == []


def test_an_unknown_option_is_a_usage_error(drive):
    """A typo must stop the run, not be forwarded as part of the task."""
    result = run("do", "t", "--openrouter-key", FAKE_KEY, "--headless")

    assert result.exit_code == 2, result.output
    assert drive.calls == []


def test_the_task_reaches_drive_verbatim(drive):
    """Quotes, inner spaces and newlines survive the command line unchanged.

    Known-bad: a nargs=-1 variadic argument joined with " ", which collapses
    runs of whitespace and drops newlines from a multi-line task.
    """
    task = 'click the "Sign in" button,   then read\nthe first heading'

    run("do", task, "--openrouter-key", FAKE_KEY)

    assert drive.call["task"] == task


def test_drive_is_called_exactly_once(drive):
    """One command, one browser session.

    Known-bad: a retry wrapper around drive, which on this stack means a second
    Firefox process for every failure.
    """
    run("do", "t", "--openrouter-key", FAKE_KEY)

    assert len(drive.calls) == 1


# --------------------------------------------------------------------------
# what lands on stdout
# --------------------------------------------------------------------------

def test_the_result_is_printed_verbatim_with_one_trailing_newline(monkeypatch):
    """stdout is exactly the model's answer plus the newline click.echo adds.

    Known-bad: a decorative prefix such as "Result: ", or repr() instead of the
    string, either of which breaks `aihawk do ... > answer.txt` and every
    pipeline reading the answer.
    """
    answer = "line one\nline two with trailing spaces   "
    monkeypatch.setattr(climod, "drive", DriveRecorder(result=answer))

    result = run("do", "t", "--openrouter-key", FAKE_KEY)

    assert result.exit_code == 0, result.output
    assert result.stdout == answer + "\n"
    assert result.stderr == ""


def test_an_empty_result_prints_only_a_newline(monkeypatch):
    """The model answering with nothing is not an error and prints nothing.

    Known-bad: printing "None" because the empty string was passed through a
    str() of a None default.
    """
    monkeypatch.setattr(climod, "drive", DriveRecorder(result=""))

    result = run("do", "t", "--openrouter-key", FAKE_KEY)

    assert result.exit_code == 0, result.output
    assert result.stdout == "\n"


# --------------------------------------------------------------------------
# help
# --------------------------------------------------------------------------

def test_group_help_works_and_names_openrouter():
    """`aihawk --help` must tell a first-time user which credential is needed.

    OpenRouter is the only accepted provider, so the top-level help is where a
    person finds out that a key is required at all. Known-bad, and the reason
    this assertion exists: help text that describes the browser and never
    mentions the key, which sends the user to the error path to discover it.
    """
    result = run("--help")

    assert result.exit_code == 0, result.output
    assert "do" in result.output
    assert "openrouter" in result.output.lower()


def test_do_help_works_and_names_openrouter_and_the_env_variables():
    """`aihawk do --help` documents both ways to supply the key.

    Known-bad: dropping "(or env OPENROUTER_API_KEY)" from the option help,
    which leaves the environment route undiscoverable.
    """
    result = run("do", "--help")

    assert result.exit_code == 0, result.output
    assert "openrouter" in result.output.lower()
    assert "OPENROUTER_API_KEY" in result.output
    assert "AIHAWK_MODEL" in result.output
    for option in DECLARED_OPTIONS | {"--help"}:
        assert option in result.output, option


def test_bare_invocation_shows_the_do_command():
    """`aihawk` alone is a usage error that still lists what can be run."""
    result = run()

    assert result.exit_code == 2
    assert "do" in result.output


# --------------------------------------------------------------------------
# the key must never be echoed - the point of this file
# --------------------------------------------------------------------------

def test_the_key_is_never_echoed_on_any_path(monkeypatch):
    """A sweep of every CLI path, with the key present in argv or in the shell.

    Success, help, the missing-key refusal, a usage error, and a crash inside
    drive. On each one the whole output is searched for a recognisable piece of
    the key. Known-bad this catches: a debug print of the resolved key, a click
    exception message interpolating it, or an error path that echoes argv.

    The crash case also searches the formatted traceback, because a traceback is
    what a user pastes into an issue: a RuntimeError message built with an
    f-string containing the key would end up in a public bug report.
    """
    outputs: dict[str, str] = {}

    monkeypatch.setattr(climod, "drive", DriveRecorder(result="the heading is hello"))
    outputs["success"] = run("do", "t", "--openrouter-key", FAKE_KEY).output
    outputs["group_help"] = run("--help").output
    outputs["do_help"] = run("do", "--help").output
    outputs["missing_task"] = run("do", "--openrouter-key", FAKE_KEY).output
    outputs["unknown_option"] = run(
        "do", "t", "--openrouter-key", FAKE_KEY, "--nope"
    ).output

    monkeypatch.setenv("OPENROUTER_API_KEY", FAKE_KEY)
    outputs["success_from_env"] = run("do", "t").output
    outputs["help_with_key_in_env"] = run("do", "--help").output
    monkeypatch.delenv("OPENROUTER_API_KEY")

    # The refusal path: no key exists, but the marker must not appear either.
    outputs["missing_key"] = run("do", "t").output

    crash = DriveRecorder(raises=RuntimeError("the browser did not start"))
    monkeypatch.setattr(climod, "drive", crash)
    crashed = run("do", "t", "--openrouter-key", FAKE_KEY)
    outputs["crash"] = crashed.output
    if crashed.exception is not None:
        outputs["crash_traceback"] = "".join(
            traceback.format_exception(
                type(crashed.exception), crashed.exception,
                crashed.exception.__traceback__,
            )
        )

    leaks = sorted(name for name, text in outputs.items() if key_leaked(text))
    assert leaks == [], f"the API key appeared in the output of: {leaks}"


def test_the_key_detector_is_not_vacuous(monkeypatch):
    """Control for the sweep above: prove key_leaked can see a real leak.

    A check that has only ever returned False is not a check. Here drive returns
    a string containing the key, the CLI prints its result verbatim as it must,
    and the detector has to fire. If this test ever fails, the sweep above is
    asserting nothing and its green means nothing.
    """
    monkeypatch.setattr(
        climod, "drive", DriveRecorder(result=f"debug: using key {FAKE_KEY}")
    )

    result = run("do", "t", "--openrouter-key", FAKE_KEY)

    assert key_leaked(result.output)
    assert key_leaked(FAKE_KEY[:20]), "a truncated echo must trip the detector too"
    assert not key_leaked("no secret here")


def test_the_key_option_cannot_echo_its_own_value_in_a_usage_error():
    """Structural guard on --openrouter-key: plain text, no type, no callback.

    Measured on click 8.5.0: a click type or callback that rejects a value
    prints that value back. `aihawk do t --seed <key>` (a plausible typo, the
    key landing on the wrong flag) prints the key in full on stderr. That echo
    belongs to click, but it becomes ours the moment --openrouter-key gains a
    type= or a callback raising BadParameter, since the rejected value would
    then be the key itself. Known-bad: adding type=click.STRING with a callback
    validating the "sk-or-" prefix, which sounds helpful and prints the key on
    every mistyped key.
    """
    param = next(p for p in climod.do.params if p.name == "openrouter_key")

    assert param.type is click.STRING
    assert param.callback is None
    assert param.default is None
    assert not getattr(param, "is_flag", False)
    assert FAKE_KEY not in (param.help or "")

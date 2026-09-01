"""A run that cannot proceed has to say so, on the terminal and in the exit code.

It did neither. loguru starts with no sinks, src/logging.py removes them again
and only adds one if LOG_TO_FILE or LOG_TO_CONSOLE is set, and config.py had both
False. main.py catches every exception, hands it to that sink-less logger and
falls off the end of the function. Measured before the fix: a run with a required
config file missing printed nothing at all on stdout or stderr and exited 0. The
shell reported success.

Every other first-run problem went the same way: a wrong API key, no Chrome, an
unreachable posting.
"""

import os
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def run_in(folder: Path):
    env = {**os.environ, "PYTHONPATH": str(ROOT), "PYTHONIOENCODING": "utf-8"}
    return subprocess.run(
        [sys.executable, str(ROOT / "main.py")],
        cwd=folder,
        env=env,
        capture_output=True,
        text=True,
        timeout=120,
        stdin=subprocess.DEVNULL,
    )


def prepare(folder: Path):
    """Give the run a copy of the shipped example to work from."""
    shutil.copytree(ROOT / "data_folder_example", folder / "data_folder_example")
    return folder


def test_a_fresh_clone_creates_the_data_folder_and_says_what_to_edit(tmp_path):
    prepare(tmp_path)

    done = run_in(tmp_path)
    combined = done.stdout + done.stderr

    for name in ("secrets.yaml", "work_preferences.yaml", "plain_text_resume.yaml"):
        assert (tmp_path / "data_folder" / name).exists(), f"{name} was not created"
    assert done.returncode != 0, "the first run has nothing to work with yet"
    assert "secrets.yaml" in combined, (
        "the run has to name what it created and ask for real values. Got:\n"
        f"stdout={done.stdout!r}\nstderr={done.stderr!r}"
    )


def test_a_broken_config_is_reported_rather_than_swallowed(tmp_path):
    """The bootstrap above cannot help with a file that exists and is wrong, which
    is the case that used to exit 0 in silence."""
    prepare(tmp_path)
    data = tmp_path / "data_folder"
    shutil.copytree(ROOT / "data_folder_example", data)
    prefs = data / "work_preferences.yaml"
    prefs.write_text(
        prefs.read_text(encoding="utf-8").replace("distance:", "distance_typo:"),
        encoding="utf-8",
    )

    done = run_in(tmp_path)
    combined = done.stdout + done.stderr

    assert done.returncode != 0, "an invalid config must not report success"
    assert "distance" in combined.lower(), (
        "the run has to name what is wrong with the config. Got:\n"
        f"stdout={done.stdout!r}\nstderr={done.stderr!r}"
    )

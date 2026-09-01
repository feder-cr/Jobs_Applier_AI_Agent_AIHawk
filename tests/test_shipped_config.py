"""The config files this repository ships have to satisfy the validator it ships.

A broken example config is invisible to whoever breaks it and fatal to every new
user, because copying it is the first thing the setup instructions ask for. The
same goes for a committed credential: one was sitting in both secrets files for
a long time and nothing in here was looking.
"""

from pathlib import Path

import pytest
import yaml

import main

# data_folder is no longer tracked: it holds the user's key and CV, and it is
# created from this example on first run. The example is the only shipped copy.
SHIPPED = ["data_folder_example"]


@pytest.mark.parametrize("folder", SHIPPED)
def test_shipped_work_preferences_pass_the_validator(folder):
    config = main.ConfigValidator.validate_config(
        Path(folder) / "work_preferences.yaml"
    )
    assert config["positions"], "positions cannot be empty or the run has nothing to do"


@pytest.mark.parametrize("folder", SHIPPED)
def test_shipped_secrets_provide_a_key(folder):
    assert main.ConfigValidator.validate_secrets(Path(folder) / "secrets.yaml")


# Prefixes the common providers put on their keys. sk- covers OpenAI and
# Anthropic, AIza is Google, hf_ is HuggingFace, gsk_ is Groq. The project only
# calls OpenAI today, but somebody pasting any of these into the shipped file is
# the accident this guards.
KEY_PREFIXES = ("sk-", "AIza", "hf_", "gsk_", "xai-", "pplx-")


@pytest.mark.parametrize("folder", SHIPPED)
def test_shipped_secrets_are_a_placeholder_and_not_a_real_key(folder):
    key = main.ConfigValidator.validate_secrets(Path(folder) / "secrets.yaml")
    looks_real = [p for p in KEY_PREFIXES if key.startswith(p)]
    assert not looks_real, (
        f"{folder}/secrets.yaml starts with {looks_real[0]!r}, which is what a real "
        "API key looks like rather than a placeholder. Credentials must never be "
        "committed here: put yours in the file locally and keep it out of the diff."
    )


def test_the_validator_rejects_a_config_with_a_required_key_missing(tmp_path):
    """Without this, every assertion above would also pass against a validator
    that accepts anything at all."""
    config = yaml.safe_load(
        Path("data_folder_example/work_preferences.yaml").read_text(encoding="utf-8")
    )
    del config["positions"]
    broken = tmp_path / "work_preferences.yaml"
    broken.write_text(yaml.safe_dump(config), encoding="utf-8")

    with pytest.raises(main.ConfigError):
        main.ConfigValidator.validate_config(broken)


def test_the_validator_rejects_a_config_with_a_wrong_type(tmp_path):
    config = yaml.safe_load(
        Path("data_folder_example/work_preferences.yaml").read_text(encoding="utf-8")
    )
    config["distance"] = "not a number"
    broken = tmp_path / "work_preferences.yaml"
    broken.write_text(yaml.safe_dump(config), encoding="utf-8")

    with pytest.raises(main.ConfigError):
        main.ConfigValidator.validate_config(broken)

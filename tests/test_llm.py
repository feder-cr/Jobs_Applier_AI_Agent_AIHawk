import pytest
from aihawk.llm import resolve_key, resolve_model


def test_key_arg_wins_then_env_then_error():
    assert resolve_key("k1", {"OPENROUTER_API_KEY": "k2"}) == "k1"
    assert resolve_key(None, {"OPENROUTER_API_KEY": "k2"}) == "k2"
    with pytest.raises(RuntimeError):
        resolve_key(None, {})


def test_model_arg_env_default():
    assert resolve_model("m1", {"AIHAWK_MODEL": "m2"}) == "m1"
    assert resolve_model(None, {"AIHAWK_MODEL": "m2"}) == "m2"
    assert resolve_model(None, {}) == "z-ai/glm-4.6"

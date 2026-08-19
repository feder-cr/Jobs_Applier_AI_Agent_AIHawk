from aihawk.runner import child_env


def test_child_env_maps_options_and_omits_key():
    env = child_env(
        {"proxy": "http://u:p@h:8080", "seed": 42, "headed": True, "binary": "C:/ff.exe"},
        {"PATH": "/x", "OPENROUTER_API_KEY": "secret"},
    )
    assert env["STEALTHFOX_PROXY"] == "http://u:p@h:8080"
    assert env["STEALTHFOX_SEED"] == "42"
    assert env["STEALTHFOX_HEADLESS"] == "0"
    assert env["STEALTHFOX_BINARY"] == "C:/ff.exe"
    assert env["PATH"] == "/x"                      # unrelated base env preserved
    assert "OPENROUTER_API_KEY" not in env          # the key must NOT reach the child


def test_child_env_defaults_headless_and_omits_absent():
    env = child_env({}, {})
    assert "STEALTHFOX_HEADLESS" not in env       # default (headless) => don't set
    assert "STEALTHFOX_PROXY" not in env
    assert "STEALTHFOX_SEED" not in env

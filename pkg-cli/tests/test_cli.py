from click.testing import CliRunner
import aihawk.cli as climod


def test_do_prints_result(monkeypatch):
    async def fake_drive(task, *, opts, key, model):
        assert task == "read the page"
        assert opts["proxy"] == "http://h:1"
        assert key == "kkk" and model == "z-ai/glm-4.6"
        return "DONE: hello"
    monkeypatch.setattr(climod, "drive", fake_drive)
    r = CliRunner().invoke(
        climod.main,
        ["do", "read the page", "--openrouter-key", "kkk", "--proxy", "http://h:1"],
    )
    assert r.exit_code == 0, r.output
    assert "DONE: hello" in r.output


def test_do_errors_without_key(monkeypatch):
    monkeypatch.delenv("OPENROUTER_API_KEY", raising=False)
    r = CliRunner().invoke(climod.main, ["do", "x"])
    assert r.exit_code != 0
    assert "OpenRouter key" in r.output

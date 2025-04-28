import sys, types, importlib
from types import SimpleNamespace

import pytest
import config as cfg


# ------------------------------------------------------------------
#  Fixtures : fake LangChain-OpenAI layer so no real API calls happen
# ------------------------------------------------------------------
class _MockChatOpenAI:
    def __init__(self, *_, **kw):
        self.model_name = kw.get("model_name")

    # LoggerChatModel expects the llm instance to be callable
    def __call__(self, messages):            # pylint: disable=unused-argument
        return "dummy-reply"


class _MockOpenAIEmbeddings:
    def __init__(self, *_, **kw):
        self.model = kw.get("model")


@pytest.fixture(autouse=True)
def _patch_langchain(monkeypatch):
    """
    Replace `langchain_openai.ChatOpenAI` and `OpenAIEmbeddings`
    with light mocks *before* the project modules import them.
    """
    fake_mod = types.ModuleType("langchain_openai")
    fake_mod.ChatOpenAI       = _MockChatOpenAI
    fake_mod.OpenAIEmbeddings = _MockOpenAIEmbeddings
    monkeypatch.setitem(sys.modules, "langchain_openai", fake_mod)
    yield


# -------------------------------------------------------------
#  Helpers
# -------------------------------------------------------------
def _reset_module(module_path: str):
    """Ensure module is re-loaded after cfg.LLM_MODEL is patched."""
    if module_path in sys.modules:
        del sys.modules[module_path]
    return importlib.import_module(module_path)


# -------------------------------------------------------------
#  Tests
# -------------------------------------------------------------
@pytest.mark.parametrize("model_in_cfg", ["o3", "gpt-4.1-turbo"])
def test_llm_classes_use_cfg_model(monkeypatch, model_in_cfg):
    # set desired model in config
    monkeypatch.setattr(cfg, "LLM_MODEL", model_in_cfg, raising=False)

    # reload each LLM module so it picks up the patched config
    gen_resume      = _reset_module("src.libs.resume_and_cover_builder.llm.llm_generate_resume")
    gen_cover       = _reset_module("src.libs.resume_and_cover_builder.llm.llm_generate_cover_letter_from_job")
    gen_resume_job  = _reset_module("src.libs.resume_and_cover_builder.llm.llm_generate_resume_from_job")
    parser_mod      = _reset_module("src.libs.resume_and_cover_builder.llm.llm_job_parser")

    # dummy strings object (nothing accessed during construction)
    dummy_strings = SimpleNamespace()

    # ---- LLMResumer ------------------------------------------------
    resumer = gen_resume.LLMResumer("fake-key", dummy_strings)
    assert resumer.llm_cheap.llm.model_name == model_in_cfg

    # ---- LLMCoverLetterJobDescription -----------------------------
    cover = gen_cover.LLMCoverLetterJobDescription("fake-key", dummy_strings)
    assert cover.llm_cheap.llm.model_name == model_in_cfg

    # ---- LLMResumeJobDescription ----------------------------------
    resum_job = gen_resume_job.LLMResumeJobDescription("fake-key", dummy_strings)
    assert resum_job.llm_cheap.llm.model_name == model_in_cfg

    # ---- LLMParser -------------------------------------------------
    parser = parser_mod.LLMParser("fake-key")
    assert parser.llm.llm.model_name == model_in_cfg


def test_explicit_model_overrides_cfg(monkeypatch):
    monkeypatch.setattr(cfg, "LLM_MODEL", "o3", raising=False)
    override = "o4-mini"

    gen_resume = _reset_module("src.libs.resume_and_cover_builder.llm.llm_generate_resume")
    dummy_strings = SimpleNamespace()
    resumer = gen_resume.LLMResumer("fake-key", dummy_strings, model_name=override)

    assert resumer.llm_cheap.llm.model_name == override

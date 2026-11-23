"""aw reaches a language model only through ``aw.llm``: aix first, oa as a fallback (addaix/aw#12)."""

import builtins
import sys
import types

import pytest

from aw import llm


def _block(monkeypatch, *names):
    real = builtins.__import__

    def fake(name, *a, **k):
        if name in names:
            raise ImportError(name)
        return real(name, *a, **k)

    monkeypatch.setattr(builtins, "__import__", fake)


def test_default_chat_is_aix_chat():
    import aix

    assert llm.default_chat() is aix.chat


def test_json_maker_calls_aix_prompt_func_with_a_response_schema(monkeypatch):
    seen = {}
    stub = types.ModuleType("aix")
    stub.prompt_func = lambda template, **kw: seen.update(t=template, **kw) or "fn"
    monkeypatch.setitem(sys.modules, "aix", stub)
    maker = llm.default_json_function_maker()
    assert maker("T {x}", json_schema={"name": "f", "schema": {"type": "object"}}) == "fn"
    assert seen == {"t": "T {x}", "response_schema": {"type": "object"}}


def test_the_default_code_generator_runs_through_aix(monkeypatch):
    """End to end through the real aix, with only the model call faked (addaix/aw#14)."""
    import inspect

    pytest.importorskip("aix")
    import aix.prompts

    class Done:
        value = {"code": "def add(a, b):\n    return a + b"}

    monkeypatch.setattr(aix.prompts, "complete", lambda prompt, **kw: Done())
    from aw.func_calling import make_code_generator

    gen = make_code_generator()
    args = {name: "add two numbers" for name in inspect.signature(gen).parameters}
    assert gen(**args) == {"code": "def add(a, b):\n    return a + b"}


def test_falls_back_to_oa_when_aix_is_missing(monkeypatch):
    stub = types.ModuleType("oa")
    stub.chat = lambda prompt: "oa"
    stub.prompt_json_function = lambda template, json_schema: "oa-json"
    monkeypatch.setitem(sys.modules, "oa", stub)
    _block(monkeypatch, "aix")
    assert llm.default_chat()("hi") == "oa"
    assert llm.default_json_function_maker() is stub.prompt_json_function


def test_neither_installed_raises_import_error(monkeypatch):
    _block(monkeypatch, "aix", "oa")
    with pytest.raises(ImportError, match="aix"):
        llm.default_chat()
    with pytest.raises(ImportError, match="aix"):
        llm.default_json_function_maker()


def test_make_code_generator_uses_the_seam_and_names_the_missing_facade(monkeypatch):
    from aw.func_calling import make_code_generator

    _block(monkeypatch, "aix", "oa")
    with pytest.raises(ValueError, match="aix"):
        make_code_generator()

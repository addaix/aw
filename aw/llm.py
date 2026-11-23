"""The one place aw reaches a language model: ``aix`` first, ``oa`` only as a fallback.

Generation is routed through ``aix`` (the fleet's LLM facade). ``oa`` stays an optional
extra (the ``llm`` extra) and is used only when ``aix`` cannot be imported, so an
install that has only ``oa`` keeps working.

>>> callable(default_chat())
True
"""

from __future__ import annotations

from typing import Any, Callable

__all__ = ["default_chat", "default_json_function_maker"]

_MISSING = (
    "no LLM facade available: aw needs aix (or, as a fallback, oa: the 'llm' extra)"
)


def default_chat() -> Callable[..., str]:
    """``chat(prompt, **kwargs) -> str``: ``aix.chat``, else ``oa.chat``.

    Raises ``ImportError`` when neither is installed.
    """
    try:
        from aix import chat

        return chat
    except ImportError:
        pass
    try:
        from oa import chat

        return chat
    except ImportError as error:
        raise ImportError(_MISSING) from error


def _json_schema_of(schema: Any) -> Any:
    """The JSON schema in ``schema``: an OpenAI-style ``{"name", "schema": {...}}``
    wrapper is unwrapped; a JSON-schema dict, or a Pydantic model, is returned as is
    (addaix/aw#14).

    >>> _json_schema_of({"name": "f", "schema": {"type": "object"}})
    {'type': 'object'}
    >>> _json_schema_of({"type": "object"})
    {'type': 'object'}
    """
    if isinstance(schema, dict) and isinstance(schema.get("schema"), dict):
        return schema["schema"]
    return schema


def default_json_function_maker() -> Callable[..., Callable[..., Any]]:
    """``maker(template, *, json_schema) -> function``: ``aix.prompt_to_json``, else ``oa.prompt_json_function``.

    Raises ``ImportError`` when neither is installed.
    """
    try:
        from aix import prompt_func

        def maker(template: str, *, json_schema: Any, **kwargs) -> Callable[..., Any]:
            return prompt_func(
                template, response_schema=_json_schema_of(json_schema), **kwargs
            )

        return maker
    except ImportError:
        pass
    try:
        from oa import prompt_json_function

        return prompt_json_function
    except ImportError as error:
        raise ImportError(_MISSING) from error

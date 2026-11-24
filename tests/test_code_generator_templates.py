"""The code-generator templates pass the caller's output schema to the model (addaix/aw#16).

aix (and oa) leave braces inside ``` fenced ``` regions literal, so a field written
inside a fence is not a field: it is dropped from the signature and the model sees the
placeholder text. Every template must keep its fields outside fences.
"""

import inspect

import pytest

from aw import func_calling, py_gen

TEMPLATES = [
    (module, name)
    for module in (func_calling, py_gen)
    for name in (
        "CODE_WRITING_TEMPLATE",
        "STRUCTURED_CODE_WRITING_TEMPLATE",
        "MINIMAL_CODE_WRITING_TEMPLATE",
    )
]


@pytest.mark.parametrize("module, name", TEMPLATES)
def test_output_schema_reaches_the_prompt(module, name, monkeypatch):
    pytest.importorskip("aix")
    import aix.prompts

    seen = {}

    class Done:
        value = {"code": "def add_numbers(a, b):\n    return a + b"}

    def fake_complete(prompt, **kw):
        seen["prompt"] = prompt
        return Done()

    monkeypatch.setattr(aix.prompts, "complete", fake_complete)
    gen = module.make_code_generator(getattr(module, name))
    assert set(inspect.signature(gen).parameters) == {"task", "output_schema", "name"}
    schema = '{"type": "object", "properties": {"sum": {"type": "number"}}}'
    gen(task="Add {a} and {b}", output_schema=schema, name="add_numbers")
    assert schema in seen["prompt"]
    assert "{output_schema}" not in seen["prompt"]


@pytest.mark.parametrize("module", [func_calling, py_gen])
def test_task_to_function_sends_the_schema(module, monkeypatch):
    seen = {}

    def generator(**kwargs):
        seen.update(kwargs)
        return {"code": "def add_numbers(a, b):\n    return a + b"}

    module.task_to_function(
        "Add {a} and {b}",
        output_schema={"type": "number"},
        name="add_numbers",
        code_generator=generator,
    )
    assert '"type": "number"' in seen["output_schema"]

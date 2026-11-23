# aw.llm

The one place aw reaches a language model: `aix` first, `oa` only as a fallback.

Generation is routed through `aix` (the fleet’s LLM facade). `oa` stays an optional
extra (the `llm` extra) and is used only when `aix` cannot be imported, so an
install that has only `oa` keeps working.

```pycon
>>> callable(default_chat())
True
```

### Functions

| [`default_chat`](#aw.llm.default_chat)()                | `chat(prompt, **kwargs) -> str`: `aix.chat`, else `oa.chat`.                                         |
|--------------------------------------------------------------------------------|------------------------------------------------------------------------------------------------------|
| [`default_json_function_maker`](#aw.llm.default_json_function_maker)() | `maker(template, *, json_schema) -> function`: `aix.prompt_to_json`, else `oa.prompt_json_function`. |

### aw.llm.default_chat()

`chat(prompt, **kwargs) -> str`: `aix.chat`, else `oa.chat`.

Raises `ImportError` when neither is installed.

* **Return type:**
  [`Callable`](https://docs.python.org/3/library/typing.html#typing.Callable)[[`...`](https://docs.python.org/3/builtins/constants.html#Ellipsis), [`str`](https://docs.python.org/3/builtins/stdtypes.html#str)]

### aw.llm.default_json_function_maker()

`maker(template, *, json_schema) -> function`: `aix.prompt_to_json`, else `oa.prompt_json_function`.

Raises `ImportError` when neither is installed.

* **Return type:**
  [`Callable`](https://docs.python.org/3/library/typing.html#typing.Callable)[[`...`](https://docs.python.org/3/builtins/constants.html#Ellipsis), [`Callable`](https://docs.python.org/3/library/typing.html#typing.Callable)[[`...`](https://docs.python.org/3/builtins/constants.html#Ellipsis), [`Any`](https://docs.python.org/3/library/typing.html#typing.Any)]]

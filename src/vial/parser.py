from vial import prompt, confirm
import inspect

from collections.abc import Callable
from typing import Any

from vial.session import sign


def parser(func: Callable[..., Any]):
    sig = inspect.signature(func)
    args = []

    prompt_ = "[bold blue][?][/]"

    for param in sig.parameters.values():
        param_ = None
        type_ = param.annotation
        name = param.name.replace("_", " ")

        if type_ is bool:
            param_ = confirm.ask(f"{prompt_} Use {name}")

        if type_ in (str, dict):
            param_ = prompt.ask(f"{prompt_} Enter the {name}")

        if type_ is int:
            param_ = prompt.ask(f"{prompt_} Number of {name}")

        args.append(param_)

    return func(*args)


parser(sign)

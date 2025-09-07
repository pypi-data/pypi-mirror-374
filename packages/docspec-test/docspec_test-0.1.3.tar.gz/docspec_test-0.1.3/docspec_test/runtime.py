from __future__ import annotations

import builtins
import inspect
import os
from pathlib import Path
from types import ModuleType
from typing import Callable, Dict, List, Optional, Tuple

from .plugin import _parse_doc_blocks


class DocspecValidationError(AssertionError):
    pass


def _resolve_exception(module: ModuleType, exc_name: str, namespace: Dict[str, object]):
    exc = (
        namespace.get(exc_name)
        or getattr(module, exc_name, None)
        or getattr(builtins, exc_name, None)
    )
    if exc is None or not isinstance(exc, type):
        raise TypeError(f"Unknown exception type in raises=: {exc_name}")
    return exc


def execute_docstring_tests_for_object(
    obj: object, module: Optional[ModuleType] = None
) -> None:
    """Execute docstring tests defined on a specific object.

    Raises DocspecValidationError if any test fails.
    """
    if module is None:
        module = inspect.getmodule(obj) or builtins

    doc = inspect.getdoc(obj) or ""
    setup_code, teardown_code, tests = _parse_doc_blocks(doc)
    if not tests and not setup_code and not teardown_code:
        return

    # Build an execution namespace:
    # - function/class globals
    # - module globals
    # - closure freevars
    namespace: Dict[str, object] = {}
    if hasattr(obj, "__globals__") and isinstance(getattr(obj, "__globals__"), dict):
        namespace.update(getattr(obj, "__globals__"))  # type: ignore[arg-type]
    if isinstance(module, ModuleType):
        for k, v in module.__dict__.items():
            namespace.setdefault(k, v)
    if hasattr(obj, "__closure__") and hasattr(obj, "__code__"):
        closure = getattr(obj, "__closure__")
        freevars = getattr(getattr(obj, "__code__"), "co_freevars", ())
        if closure and freevars:
            for name, cell in zip(freevars, closure):
                try:
                    namespace[name] = cell.cell_contents
                except ValueError:
                    pass
    obj_name = getattr(obj, "__name__", None)
    if isinstance(obj_name, str):
        namespace.setdefault(obj_name, obj)

    try:
        if setup_code:
            exec(setup_code, namespace)

        for code, options in tests:
            if "skip" in options:
                continue

            expected_exc = options.get("raises")
            try:
                if expected_exc:
                    exc_type = _resolve_exception(module, expected_exc, namespace)  # type: ignore[arg-type]
                    try:
                        exec(code, namespace)
                    except Exception as e:  # noqa: BLE001
                        if not isinstance(e, exc_type):
                            raise DocspecValidationError(
                                f"Expected {exc_type.__name__}, got {type(e).__name__}"
                            ) from e
                    else:
                        raise DocspecValidationError(
                            f"Expected {exc_type.__name__} to be raised"
                        )
                else:
                    exec(code, namespace)
            except AssertionError as e:
                if "xfail" in options:
                    continue
                raise DocspecValidationError(str(e)) from e
    finally:
        if teardown_code:
            exec(teardown_code, namespace)


def validate_module(module: ModuleType | str | Path) -> None:
    """Validate all objects in a module by executing their docstring tests."""
    if isinstance(module, (str, Path)):
        module = _import_from_path(Path(module))

    for _, obj in inspect.getmembers(module):
        if inspect.isfunction(obj) or inspect.isclass(obj):
            execute_docstring_tests_for_object(obj, module)


def validate_on_call(
    func: Callable[..., object], *, mode: str = "once"
) -> Callable[..., object]:
    """Decorator that validates the function's docstring tests at runtime.

    mode: "once" (default) validates only on the first call, "always" validates every call.
    Env var DOCSPEC_VALIDATE_ALWAYS=1 forces validation on every call.
    """

    validate_always_env = os.getenv("DOCSPEC_VALIDATE_ALWAYS") in {"1", "true", "True"}
    validate_always = validate_always_env or mode == "always"
    validated_flag = {"done": False}

    def wrapper(*args, **kwargs):
        if validate_always or not validated_flag["done"]:
            execute_docstring_tests_for_object(func)
            validated_flag["done"] = True
        return func(*args, **kwargs)

    wrapper.__name__ = func.__name__
    wrapper.__doc__ = func.__doc__
    wrapper.__qualname__ = getattr(func, "__qualname__", func.__name__)
    return wrapper


def _import_from_path(path: Path) -> ModuleType:
    import importlib.util

    spec = importlib.util.spec_from_file_location(path.stem, path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Cannot import module from {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

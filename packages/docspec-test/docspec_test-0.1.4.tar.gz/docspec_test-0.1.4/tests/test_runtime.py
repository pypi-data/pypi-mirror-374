from docspec_test import (
    DocspecValidationError,
    execute_docstring_tests_for_object,
    validate_module,
    validate_on_call,
)


def test_execute_docstring_tests_for_object_passes():
    def add(a, b):
        """
        ```python test
        assert add(1, 2) == 3
        ```
        """

        return a + b

    execute_docstring_tests_for_object(add)


def test_execute_docstring_tests_for_object_raises():
    class MyError(Exception):
        pass

    def boom():
        """
        ```python test raises=MyError
        boom()
        ```
        """

        raise MyError()

    execute_docstring_tests_for_object(boom)


def test_validate_on_call_decorator_once_mode():
    calls = {"n": 0}

    @validate_on_call
    def inc(x):
        """
        ```python test
        assert inc(1) == 2
        ```
        """

        calls["n"] += 1
        return x + 1

    assert inc(1) == 2
    assert inc(2) == 3
    # Note: validation executes the docstring example once, causing one extra call
    assert calls["n"] == 3


def test_validate_module_executes_all_objects(tmp_path):
    code = 'def mul(a,b):\n\n    """\n    ```python test\n    assert mul(2,3) == 6\n    ```\n    """\n\n    return a*b\n'
    p = tmp_path / "mymod.py"
    p.write_text(code)
    validate_module(p)

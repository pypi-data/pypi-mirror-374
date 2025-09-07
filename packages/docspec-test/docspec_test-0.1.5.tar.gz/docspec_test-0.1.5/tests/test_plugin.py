def test_executes_code_blocks(pytester):
    pytester.makepyfile(
        test_module='''
def add(a, b):
    """
    Example with executable docstring block.

    ```python test
    assert add(1, 2) == 3
    ```
    """
    return a + b
'''
    )

    result = pytester.runpytest("-q")
    result.assert_outcomes(passed=1)


def test_reports_failure(pytester):
    pytester.makepyfile(
        test_module='''
def mul(a, b):
    """
    Example that should fail.

    ```python test
    assert mul(2, 2) == 5
    ```
    """
    return a * b
'''
    )

    result = pytester.runpytest("-q")
    result.assert_outcomes(failed=1)


def test_ignores_non_test_blocks(pytester):
    pytester.makepyfile(
        test_module='''
def sub(a, b):
    """
    Code block without 'test' info tag should be ignored.

    ```python
    # not collected as a test
    assert sub(3, 1) == 2
    ```
    """
    return a - b
'''
    )

    result = pytester.runpytest("-q")
    # No tests should be collected
    result.assert_outcomes()


def test_doctest_examples_are_executed(pytester):
    pytester.makepyfile(
        test_module='''
def square(x):
    """
    Return square.

    >>> square(3)
    9
    """
    return x * x
'''
    )

    result = pytester.runpytest("-q")
    result.assert_outcomes(passed=1)


def test_raises_directive(pytester):
    pytester.makepyfile(
        test_module='''
class MyError(Exception):
    pass


def boom():
    """
    Should raise MyError.

    ```python test raises=MyError
    boom()
    ```
    """
    raise MyError()
'''
    )

    result = pytester.runpytest("-q")
    result.assert_outcomes(passed=1)


def test_skip_and_xfail(pytester):
    pytester.makepyfile(
        test_module='''

def foo():
    """
    Skip this test.

    ```python test skip="not ready"
    assert False
    ```

    Also xfail.

    ```python test xfail
    assert False
    ```
    """
    return 1
'''
    )

    result = pytester.runpytest("-q")
    # One skipped, one xfailed
    result.assert_outcomes(skipped=1, xfailed=1)


def test_named_and_setup_teardown(pytester):
    pytester.makepyfile(
        test_module='''

def value_holder():
    """
    Prepare state.

    ```python setup
    state = {"x": 0}
    ```

    Test using the state.

    ```python test name="increments"
    state["x"] += 1
    assert state["x"] == 1
    ```

    Cleanup.

    ```python teardown
    state.clear()
    ```
    """
    return 0
'''
    )

    result = pytester.runpytest("-q")
    result.assert_outcomes(passed=1)

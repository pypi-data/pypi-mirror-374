<div align="center">

# docspec_test — Docstring tests as documentation, spec and CI

[![CI](https://github.com/alexsukhrin/docspec_test/actions/workflows/ci.yml/badge.svg)](https://github.com/alexsukhrin/docspec_test/actions/workflows/ci.yml)
[![PyPI](https://img.shields.io/pypi/v/docspec-test)](https://pypi.org/project/docspec-test/)
[![Python](https://img.shields.io/pypi/pyversions/docspec-test.svg)](https://pypi.org/project/docspec-test/)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![GitHub Repo](https://img.shields.io/badge/source-github-black)](https://github.com/alexsukhrin/docspec_test)

Turn examples in your docstrings into executable tests — without leaving your code.

</div>

Why
---

- Keep tests next to the API they validate — examples never drift from reality.
- Examples become living documentation and a precise specification.
- Perfect for TDD and quick feedback while coding.

Features
--------

- Docstring fenced blocks executed as tests: ```python test ...```
- Directives: `name`, `raises=Exception`, `skip[="reason"]`, `xfail[="reason"]`
- Optional `setup` / `teardown` blocks per object
- Pytest integration (auto-discovered plugin) and a standalone CLI
- Runtime helpers to validate directly in an interpreter or on call

Install
-------

```bash
pip install docspec-test
```

Quickstart
----------

```python
def add(a: int, b: int) -> int:
    """
    Adds two numbers.

    ```python test
    assert add(1, 2) == 3
    ```
    """
    return a + b
```

Run pytest (the plugin is discovered via `pytest11`):

```bash
pytest
```

Directives
----------

Add options to the test block header:

```markdown
```python test name="custom-name" raises=ValueError skip="reason" xfail
# test code
```
```

- name: custom test name
- raises: assert that an exception is raised (e.g. `raises=KeyError`)
- skip: skip test, with optional reason
- xfail: expected failure, with optional reason

Setup / Teardown
----------------

One optional `setup` and `teardown` block per object:

```markdown
```python setup
state = {"x": 0}
```

```python test name="increments"
state["x"] += 1
assert state["x"] == 1
```

```python teardown
state.clear()
```
```

Runtime validation (no pytest)
------------------------------

```python
from docspec_test import validate_module, execute_docstring_tests_for_object, validate_on_call

# validate an entire module by path or module object
validate_module("path/to/module.py")

# validate a single function/class
execute_docstring_tests_for_object(add)

# validate on first call (or on every call with mode="always")
@validate_on_call
def inc(x: int) -> int:
    """
    ```python test
    assert inc(1) == 2
    ```
    """
    return x + 1
```

CLI
---

Validate all Python files in the current directory:

```bash
docspec-test
```

Validate a specific path (file or directory):

```bash
docspec-test path/to/src
```

Ignore directories:

```bash
docspec-test . --ignore .venv --ignore build
```

Pytest defaults
---------------

By default, only docspec-marked tests run (`-m docspec`). To run everything:

```bash
pytest -m 'not docspec'
```

Contributing
------------

We’d love your help! Great first issues: docs, new directives, better error reporting, CI workflows.

Dev setup:

```bash
git clone https://github.com/alexsukhrin/docspec_test
cd docspec_test
python -m venv venv && source venv/bin/activate
pip install -e .[dev]  # or: pip install -e . && pip install black isort pytest build twine
```

Run checks:

```bash
isort . && black . && pytest -m 'not docspec' && pytest
```

Roadmap
-------

- Parametrized examples (table-driven)
- Inline output matching (like doctest) alongside code blocks
- Jupyter notebooks support
- VSCode/IDE integration for quick-run

Requirements
------------

- Python >= 3.8
- pytest >= 7.0.0

License
-------

MIT



import builtins
import doctest
import inspect
import re
from typing import Dict, List, Optional, Tuple

import pytest
from _pytest.pathlib import import_path


def pytest_collect_file(parent, file_path):
    # Modern pytest API: file_path is pathlib.Path
    if getattr(file_path, "suffix", None) == ".py":
        return DocspecModule.from_parent(parent, path=file_path)


class DocspecModule(pytest.File):
    def collect(self):
        module = import_path(
            self.path, root=self.path.parent, consider_namespace_packages=True
        )
        for name, obj in inspect.getmembers(module):
            if inspect.isfunction(obj) or inspect.isclass(obj):
                doc = inspect.getdoc(obj)
                if not doc:
                    continue
                setup_code, teardown_code, tests = _parse_doc_blocks(doc)
                for i, (code, options) in enumerate(tests, 1):
                    item_name = options.get("name") or f"{name}[Test {i}]"
                    yield DocspecItem.from_parent(
                        self,
                        name=item_name,
                        code=code,
                        obj_name=name,
                        setup_code=setup_code,
                        teardown_code=teardown_code,
                        options=options,
                    )

                # Add doctest-style examples (>>> ...). Use doctest parser directly.
                dt = doctest.DocTestParser().get_doctest(
                    doc, module.__dict__, name, str(self.path), 0
                )
                if dt.examples:
                    yield DocspecDoctestItem.from_parent(
                        self, name=f"{name}[doctest]", doc=doc, obj_name=name
                    )


class DocspecItem(pytest.Item):
    def __init__(
        self, name, parent, code, obj_name, setup_code, teardown_code, options
    ):
        super().__init__(name, parent)
        self.code: str = code
        self.obj_name: str = obj_name
        self.setup_code: Optional[str] = setup_code
        self.teardown_code: Optional[str] = teardown_code
        self.options: Dict[str, str] = options

        # Always mark as docspec so users can select with -m docspec
        self.add_marker(pytest.mark.docspec)

        # Apply skip/xfail markers if requested
        if "skip" in options:
            reason = options.get("skip") or "skipped by docspec directive"
            self.add_marker(pytest.mark.skip(reason=reason))
        if "xfail" in options:
            reason = options.get("xfail") or "expected failure by docspec directive"
            self.add_marker(pytest.mark.xfail(reason=reason))

    def _resolve_exception(self, module, exc_name: str):
        # Try module, then builtins
        exc = getattr(module, exc_name, None) or getattr(builtins, exc_name, None)
        if exc is None or not isinstance(exc, type):
            raise TypeError(f"Unknown exception type in raises=: {exc_name}")
        return exc

    def runtest(self):
        module = import_path(
            self.parent.path,
            root=self.parent.path.parent,
            consider_namespace_packages=True,
        )
        namespace = module.__dict__
        try:
            if self.setup_code:
                exec(self.setup_code, namespace)

            expected_exc = self.options.get("raises")
            if expected_exc:
                exc_type = self._resolve_exception(module, expected_exc)
                with pytest.raises(exc_type):
                    exec(self.code, namespace)
            else:
                exec(self.code, namespace)
        finally:
            if self.teardown_code:
                exec(self.teardown_code, namespace)

    def reportinfo(self):
        return self.path, 0, f"docspec test: {self.obj_name}"


class DocspecDoctestItem(pytest.Item):
    def __init__(self, name, parent, doc, obj_name):
        super().__init__(name, parent)
        self.doc = doc
        self.obj_name = obj_name
        # Mark as docspec as well
        self.add_marker(pytest.mark.docspec)

    def runtest(self):
        module = import_path(
            self.parent.path,
            root=self.parent.path.parent,
            consider_namespace_packages=True,
        )
        globs = module.__dict__.copy()
        # Ensure object is addressable by its name
        obj = getattr(module, self.obj_name, None)
        if obj is not None:
            globs.setdefault(self.obj_name, obj)

        parser = doctest.DocTestParser()
        test = parser.get_doctest(
            self.doc, globs, self.obj_name, str(self.parent.path), 0
        )
        runner = doctest.DocTestRunner(optionflags=doctest.NORMALIZE_WHITESPACE)
        runner.run(test)
        if runner.failures:
            raise AssertionError(
                f"doctest failures in {self.obj_name}: {runner.failures}"
            )

    def reportinfo(self):
        return self.path, 0, f"docspec doctest: {self.obj_name}"


def _parse_doc_blocks(
    doc: str,
) -> Tuple[Optional[str], Optional[str], List[Tuple[str, Dict[str, str]]]]:
    """Parse fenced code blocks in the docstring.

    Supported forms:
      ```python setup\n...```
      ```python teardown\n...```
      ```python test [name="..."] [raises=ValueError] [skip[="reason"]] [xfail[="reason"]]\n...```

    ```python test name="parse-doc-blocks"
    text = (
        '''
        Intro text

        ```python setup
        x = 1
        ```

        ```python test name="t1"
        assert x == 1
        ```

        ```python teardown
        x = 0
        ```
        '''
    )
    setup, teardown, tests = _parse_doc_blocks(text)
    assert isinstance(setup, str) and "x = 1" in setup
    assert isinstance(teardown, str) and "x = 0" in teardown
    assert len(tests) == 1 and tests[0][1]["name"] == "t1"
    ```
    """
    setup_code: Optional[str] = None
    teardown_code: Optional[str] = None
    tests: List[Tuple[str, Dict[str, str]]] = []

    pattern = re.compile(r"```python\s+(\w+)([^\n]*)\n(.*?)```", re.DOTALL)
    for kind, opts_str, code in pattern.findall(doc):
        kind = kind.strip().lower()
        if kind == "setup":
            setup_code = code
        elif kind == "teardown":
            teardown_code = code
        elif kind == "test":
            options = _parse_options(opts_str)
            tests.append((code, options))
    return setup_code, teardown_code, tests


def _parse_options(opts_str: str) -> Dict[str, str]:
    """Parse options from a test block header.

    ```python test name="parse-options"
    opts = _parse_options('name="case" raises=ValueError skip xfail="flaky"')
    assert opts["name"] == "case"
    assert opts["raises"] == "ValueError"
    assert "skip" in opts and opts["skip"] == ""
    assert opts["xfail"] == "flaky"
    ```
    """
    opts: Dict[str, str] = {}
    # name="..." (quoted), raises=ValueError, skip or skip="reason", xfail or xfail="reason"
    # name
    m = re.search(r"\bname=\"([^\"]+)\"", opts_str)
    if m:
        opts["name"] = m.group(1)

    m = re.search(r"\braises=([A-Za-z_][A-Za-z0-9_]*)\b", opts_str)
    if m:
        opts["raises"] = m.group(1)

    # skip
    if re.search(r"\bskip(?:\s|=|$)", opts_str):
        m = re.search(r"\bskip=\"([^\"]*)\"", opts_str)
        if m:
            opts["skip"] = m.group(1)
        else:
            opts["skip"] = ""

    # xfail
    if re.search(r"\bxfail(?:\s|=|$)", opts_str):
        m = re.search(r"\bxfail=\"([^\"]*)\"", opts_str)
        if m:
            opts["xfail"] = m.group(1)
        else:
            opts["xfail"] = ""

    return opts

from pathlib import Path

from docspec_test.cli import main


def write_ok_module(tmp_path: Path) -> Path:
    p = tmp_path / "ok.py"
    p.write_text(
        'def add(a,b):\n\n    """\n    ```python test\n    assert add(1,2) == 3\n    ```\n    """\n\n    return a+b\n'
    )
    return p


def write_bad_module(tmp_path: Path) -> Path:
    p = tmp_path / "bad.py"
    p.write_text(
        'def mul(a,b):\n\n    """\n    ```python test\n    assert mul(2,2) == 5\n    ```\n    """\n\n    return a*b\n'
    )
    return p


def test_cli_success(tmp_path):
    write_ok_module(tmp_path)
    assert main([str(tmp_path)]) == 0


def test_cli_failure(tmp_path):
    write_bad_module(tmp_path)
    assert main([str(tmp_path)]) == 1

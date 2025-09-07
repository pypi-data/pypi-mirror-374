import argparse
import sys
from pathlib import Path
from typing import Iterable, List

from .runtime import DocspecValidationError, validate_module

DEFAULT_IGNORES = {
    ".git",
    ".hg",
    ".svn",
    "__pycache__",
    "venv",
    ".venv",
    "build",
    "dist",
    ".eggs",
}


def iter_python_files(paths: Iterable[Path], ignores: Iterable[str]) -> Iterable[Path]:
    ignore_set = set(ignores)
    for root in paths:
        if root.is_file() and root.suffix == ".py":
            yield root
            continue
        if root.is_dir():
            for p in root.rglob("*.py"):
                # skip ignored dirs in the path
                if any(part in ignore_set for part in p.parts):
                    continue
                yield p


def main(argv: List[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="docspec-test",
        description="Validate docstring tests in Python files",
    )
    parser.add_argument(
        "paths", nargs="*", type=Path, help="Files or directories (default: .)"
    )
    parser.add_argument(
        "--ignore",
        action="append",
        default=[],
        help=f"Directories to ignore (can repeat). Defaults: {', '.join(sorted(DEFAULT_IGNORES))}",
    )
    args = parser.parse_args(argv)

    roots = args.paths or [Path.cwd()]
    ignores = list(DEFAULT_IGNORES) + list(args.ignore or [])

    failures: List[tuple[Path, str]] = []
    total = 0
    for py in iter_python_files(roots, ignores):
        total += 1
        try:
            validate_module(py)
        except DocspecValidationError as e:
            failures.append((py, str(e)))
        except Exception as e:  # noqa: BLE001
            failures.append((py, f"Error: {e}"))

    if failures:
        for file_path, msg in failures:
            print(f"FAIL: {file_path}: {msg}")
        print(f"docspec-test: {len(failures)}/{total} files failed")
        return 1

    print(f"docspec-test: all {total} files passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())

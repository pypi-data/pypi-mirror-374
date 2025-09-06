"""Small CLI wrapper to run the framework-packaged Alembic configuration.

The module is import-safe (does not import alembic at import time). The
`main()` function locates the bundled `alembic.ini` via importlib.resources and
delegates to Alembic's CommandLine. This script is intended to be exposed as
`envoxy-alembic` via console_scripts so services can run migrations without
needing to know package installation paths.
"""
from __future__ import annotations

import sys
from importlib import resources
from pathlib import Path


def _find_bundled_ini() -> Path:
    # locate the file inside the installed package
    pkg_root = resources.files("envoxy")
    ini_path = pkg_root.joinpath("tools", "alembic", "alembic.ini")
    return ini_path


def main(argv: list[str] | None = None) -> int:
    """Run Alembic CLI using the packaged alembic.ini.

    argv: list of arguments (without program name). Returns exit code.
    """
    argv = list(argv or sys.argv[1:])
    ini_path = _find_bundled_ini()

    # Defer importing alembic until runtime so importing this module is safe
    try:
        from alembic.config import CommandLine
    except Exception as exc:  # pragma: no cover - env dependent
        print("ERROR: the 'alembic' package is not installed in this Python environment.", file=sys.stderr)
        print("Install it with: pip install alembic", file=sys.stderr)
        print("Or install project dev requirements: pip install -r requirements.dev", file=sys.stderr)
        print("Full error:", exc, file=sys.stderr)
        return 2

    # prepend the -c <ini> so alembic uses the bundled config
    full_argv = ["-c", str(ini_path)] + argv
    try:
        return CommandLine().main(full_argv)
    except SystemExit as se:
        return int(getattr(se, 'code', 0) or 0)


if __name__ == "__main__":  # pragma: no cover - manual invocation
    raise SystemExit(main())

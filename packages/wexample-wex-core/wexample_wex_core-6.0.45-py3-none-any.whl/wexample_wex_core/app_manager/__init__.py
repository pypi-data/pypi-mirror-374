"""WEX Core - App Manager integration point.
Provides a stable run(argv, app_root=None) entry used by thin per-app wrappers.
"""

from __future__ import annotations

import os
import sys
from collections.abc import Iterable


def run(argv: Iterable[str] | None = None, app_root: str | None = None) -> int:
    if argv is None:
        argv = sys.argv[1:]

    root = app_root or os.getenv("APP_ROOT") or os.getcwd()
    # TODO: later: dispatch to real commands (click/argparse/typer)
    print(f"wex-core manager: OK (app_root={root}) args={' '.join(argv)}")
    return 0

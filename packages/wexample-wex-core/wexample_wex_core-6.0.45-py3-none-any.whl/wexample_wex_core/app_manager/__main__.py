from __future__ import annotations

import os
import sys

from . import run


def main() -> None:
    app_root = os.environ.get("APP_ROOT")
    argv = sys.argv[1:]
    run(argv, app_root)


if __name__ == "__main__":
    main()

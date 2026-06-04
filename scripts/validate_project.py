#!/usr/bin/env python3

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from meta_agent.validator import validate_project


def main():
    result = validate_project(ROOT)
    stream = sys.stdout if result.ok else sys.stderr
    print("\n".join(result.lines()), file=stream)
    return 0 if result.ok else 1


if __name__ == "__main__":
    raise SystemExit(main())

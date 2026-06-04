#!/usr/bin/env python3

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TARGET_DIRS = ["schemas", "workflows", "templates", "examples"]


def iter_json_files():
    for directory in TARGET_DIRS:
        path = ROOT / directory
        if path.exists():
            yield from sorted(path.rglob("*.json"))


def main():
    files = list(iter_json_files())
    failed = []

    for path in files:
        try:
            with path.open("r", encoding="utf-8") as handle:
                json.load(handle)
        except Exception as exc:
            failed.append((path, exc))

    if failed:
        for path, exc in failed:
            print(f"FAIL {path.relative_to(ROOT)}: {exc}", file=sys.stderr)
        return 1

    for path in files:
        print(f"OK   {path.relative_to(ROOT)}")
    print(f"Validated {len(files)} JSON files.")
    print("Tip: run scripts/validate_project.py for full project validation.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

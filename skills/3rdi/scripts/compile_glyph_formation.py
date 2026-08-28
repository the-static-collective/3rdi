#!/usr/bin/env python3
"""Compile a glyph formation sidecar into a deterministic formation receipt."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Sequence

from three_rdi import FieldError, compile_glyph_formation


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("field", type=Path, help="path to a 3rdi glyph formation field JSON document")
    parser.add_argument("--formation", required=True, help="formation id to compile")
    parser.add_argument(
        "--check",
        action="store_true",
        help="validate and print a compact receipt instead of full JSON",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        with args.field.open("r", encoding="utf-8") as handle:
            field = json.load(handle)
        receipt = compile_glyph_formation(field, args.formation)
    except (OSError, json.JSONDecodeError, FieldError) as error:
        print(f"3rdi: {error}", file=sys.stderr)
        return 2

    if args.check:
        output = {
            "schema": receipt["schema"],
            "field_id": receipt["field_id"],
            "formation_id": receipt["formation"]["id"],
            "receipt_digest": receipt["receipt_digest"],
        }
    else:
        output = receipt
    json.dump(output, sys.stdout, ensure_ascii=False, indent=2, sort_keys=True)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

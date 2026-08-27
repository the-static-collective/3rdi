#!/usr/bin/env python3
"""Compile a `3rdi.field/v0` JSON document into a projection receipt."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Sequence

from three_rdi import FieldError, compile_cut


def build_parser() -> argparse.ArgumentParser:
    """Build the command-line boundary parser."""

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("field", type=Path, help="path to a 3rdi.field/v0 JSON document")
    parser.add_argument("--cut", required=True, help="cut id to compile")
    parser.add_argument(
        "--check",
        action="store_true",
        help="validate and print a compact receipt instead of full JSON",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    """Run the CLI and return a process status."""

    args = build_parser().parse_args(argv)
    try:
        with args.field.open("r", encoding="utf-8") as handle:
            field = json.load(handle)
        receipt = compile_cut(field, args.cut)
    except (OSError, json.JSONDecodeError, FieldError) as error:
        print(f"3rdi: {error}", file=sys.stderr)
        return 2

    if args.check:
        print(
            json.dumps(
                {
                    "schema": receipt["schema"],
                    "field_id": receipt["field_id"],
                    "cut_id": receipt["cut"]["id"],
                    "projection_digest": receipt["projection_digest"],
                },
                sort_keys=True,
            )
        )
    else:
        json.dump(receipt, sys.stdout, ensure_ascii=False, indent=2, sort_keys=True)
        sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

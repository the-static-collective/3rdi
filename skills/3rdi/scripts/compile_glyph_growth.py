#!/usr/bin/env python3
"""Compile one declared glyph growth operation into a receipt."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from three_rdi.growth import compile_glyph_growth
from three_rdi.model import FieldError


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("field", type=Path, help="glyph growth field JSON")
    parser.add_argument("--operation", required=True, help="named operation id")
    parser.add_argument("--check", action="store_true", help="print a compact receipt")
    args = parser.parse_args()
    try:
        field = json.loads(args.field.read_text(encoding="utf-8"))
        receipt = compile_glyph_growth(field, args.operation)
    except (OSError, ValueError, FieldError) as error:
        print(f"3rdi: {error}", file=sys.stderr)
        return 2
    result = receipt
    if args.check:
        result = {
            "schema": receipt["schema"],
            "operation_id": receipt["operation"]["id"],
            "operation_kind": receipt["operation"]["kind"],
            "receipt_digest": receipt["receipt_digest"],
        }
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

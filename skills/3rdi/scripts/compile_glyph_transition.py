#!/usr/bin/env python3
"""Compile a declared glyph graph transition to its deterministic receipt."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Sequence

from three_rdi.transition import compile_glyph_transition
from three_rdi.model import FieldError


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("field", type=Path, help="3rdi.glyph-transition-field/v0 JSON file")
    parser.add_argument("--transition", required=True, help="declared transition id")
    parser.add_argument("--check", action="store_true", help="emit compact receipt summary")
    args = parser.parse_args(argv)
    try:
        field = json.loads(args.field.read_text(encoding="utf-8"))
        receipt = compile_glyph_transition(field, args.transition)
    except (OSError, ValueError, FieldError) as error:
        print(f"3rdi: {error}", file=sys.stderr)
        return 2
    if args.check:
        result = {
            "schema": receipt["schema"],
            "field_id": receipt["field_id"],
            "transition_id": receipt["transition"]["id"],
            "transition_kind": receipt["transition"]["kind"],
            "receipt_digest": receipt["receipt_digest"],
        }
    else:
        result = receipt
    json.dump(result, sys.stdout, ensure_ascii=False, indent=2, sort_keys=True)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

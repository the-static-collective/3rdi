#!/usr/bin/env python3
"""Decode a six-string fret glyph under a declared receiver constitution."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Sequence

from three_rdi import FieldError, decode_fret_glyph


def main(argv: Sequence[str] | None = None) -> int:
    """Run the foreign-domain control CLI."""

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("carrier", help="six decimal fret positions, for example 022100")
    parser.add_argument("decoder", type=Path, help="path to a decoder JSON object")
    args = parser.parse_args(argv)
    try:
        with args.decoder.open("r", encoding="utf-8") as handle:
            decoder = json.load(handle)
        receipt = decode_fret_glyph(args.carrier, decoder)
    except (OSError, json.JSONDecodeError, FieldError) as error:
        print(f"3rdi: {error}", file=sys.stderr)
        return 2
    json.dump(receipt, sys.stdout, ensure_ascii=False, indent=2, sort_keys=True)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

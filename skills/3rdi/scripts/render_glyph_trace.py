#!/usr/bin/env python3
"""Render a GlyphTrace formation receipt as standalone deterministic HTML."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Sequence

from three_rdi import FieldError, render_glyph_trace


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("receipt", type=Path, help="path to a GlyphTrace formation receipt JSON document")
    parser.add_argument("--output", required=True, type=Path, help="HTML output path")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        with args.receipt.open("r", encoding="utf-8") as handle:
            receipt = json.load(handle)
        html = render_glyph_trace(receipt)
        args.output.write_text(html, encoding="utf-8")
    except (OSError, json.JSONDecodeError, FieldError) as error:
        print(f"3rdi: {error}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

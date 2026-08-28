#!/usr/bin/env python3
"""Export exact 3rdi owner receipts for PASSAGE-WORLD-001."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from three_rdi import compile_cut, mortal_actor_handoff


ROOT = Path(__file__).resolve().parents[3]
SPECIMEN = ROOT / "specimens" / "passage-world-001.json"
CUTS = {"ROAD-A": "ROAD-A", "ROAD-B": "ROAD-B1"}


def export_receipts(output: Path) -> None:
    field = json.loads(SPECIMEN.read_text(encoding="utf-8"))
    for road_id, cut_id in CUTS.items():
        receipt = mortal_actor_handoff(compile_cut(field, cut_id))
        target = output / road_id / "3rdi.json"
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    export_receipts(args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

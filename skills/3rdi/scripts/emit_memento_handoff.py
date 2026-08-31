#!/usr/bin/env python3
"""Emit a deterministic no-authority MEMENTO handoff from a 3rdi projection."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Sequence

from three_rdi import canonical_json
from three_rdi.model import FieldError, parse_instant

SCHEMA = "3rdi.memento-handoff/v0"
AUTHORITY = "handoff-only-no-write-no-admission"
TRACE_FAMILIES = (
    "contacts",
    "attention_events",
    "decoder_applications",
    "stances",
)


class HandoffError(ValueError):
    """Raised when a projection cannot lawfully form a handoff receipt."""


def _mapping(value: Any, label: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise HandoffError(f"{label} must be an object")
    return value


def _stable_id(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value:
        raise HandoffError(f"{label} requires a stable id")
    return value


def _trace_family(trace: dict[str, Any], family: str) -> list[dict[str, Any]]:
    value = trace.get(family, [])
    if not isinstance(value, list):
        raise HandoffError(f"epistemic trace {family} must be an array")
    records: list[dict[str, Any]] = []
    for index, raw_record in enumerate(value):
        record = _mapping(raw_record, f"epistemic trace {family}[{index}]")
        _stable_id(record.get("id"), f"epistemic trace {family}[{index}]")
        records.append(record)
    return sorted(records, key=lambda item: item["id"])


def _withheld_categories(projection: dict[str, Any]) -> list[str]:
    audit = _mapping(projection.get("audit", {}), "projection audit")
    withheld = audit.get("withheld_epistemic", [])
    if not isinstance(withheld, list):
        raise HandoffError("projection audit withheld_epistemic must be an array")
    categories: set[str] = set()
    for index, raw_item in enumerate(withheld):
        item = _mapping(raw_item, f"withheld_epistemic[{index}]")
        kind = item.get("kind")
        if not isinstance(kind, str) or not kind:
            raise HandoffError(f"withheld_epistemic[{index}].kind must be a non-empty string")
        categories.add(kind)
    return sorted(categories)


def build_memento_handoff(
    projection: dict[str, object],
    *,
    emitted_at: str,
    world_instance_id: str | None = None,
) -> dict[str, object]:
    """Build one deterministic handoff from an already compiled projection receipt."""

    projection_map = _mapping(projection, "projection")
    if projection_map.get("schema") != "3rdi.projection-receipt/v0":
        raise HandoffError("projection schema must equal '3rdi.projection-receipt/v0'")

    field_id = _stable_id(projection_map.get("field_id"), "projection field")
    projection_digest = _stable_id(
        projection_map.get("projection_digest"), "projection digest"
    )
    cut = _mapping(projection_map.get("cut"), "projection cut")
    cut_id = _stable_id(cut.get("id"), "projection cut")
    observer = _stable_id(cut.get("observer"), "projection observer")

    try:
        parse_instant(emitted_at, "emitted_at")
    except FieldError as error:
        raise HandoffError(str(error)) from error

    if world_instance_id is not None:
        if not isinstance(world_instance_id, str) or not world_instance_id:
            raise HandoffError("world_instance_id must be a non-empty string when supplied")

    observer_view = _mapping(projection_map.get("observer_view"), "projection observer_view")
    trace = _mapping(observer_view.get("epistemic_trace"), "projection epistemic_trace")
    normalized_trace = {
        family: _trace_family(trace, family)
        for family in TRACE_FAMILIES
    }

    handoff: dict[str, object] = {
        "schema": SCHEMA,
        "emitted_at": emitted_at,
        "field_id": field_id,
        "projection_digest": projection_digest,
        "observer": observer,
        "cut_id": cut_id,
        "epistemic_trace": normalized_trace,
        "withheld_categories": _withheld_categories(projection_map),
        "residual_fog": [],
        "authority": AUTHORITY,
    }
    if world_instance_id is not None:
        handoff["world_instance_id"] = world_instance_id
    return handoff


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("projection", type=Path, help="3rdi.projection-receipt/v0 JSON")
    parser.add_argument("--emitted-at", required=True, help="explicit RFC3339 UTC emission time")
    parser.add_argument("--world-instance", help="optional explicit world-instance identity")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        with args.projection.open("r", encoding="utf-8") as handle:
            projection = json.load(handle)
        handoff = build_memento_handoff(
            projection,
            emitted_at=args.emitted_at,
            world_instance_id=args.world_instance,
        )
    except (OSError, json.JSONDecodeError, HandoffError) as error:
        print(f"3rdi handoff: {error}", file=sys.stderr)
        return 2

    sys.stdout.write(canonical_json(handoff))
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

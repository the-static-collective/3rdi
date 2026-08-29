"""Deterministic candidate-formation compilation for observed glyph carriers."""

from __future__ import annotations

import math
from typing import Any

from .model import FieldError, canonical_digest


SCHEMA = "3rdi.glyph-formation-field/v0"
RECEIPT_SCHEMA = "3rdi.glyph-formation-receipt/v0"
SUPPORTED_METRICS = {
    "stroke_count",
    "pen_lifts",
    "segment_count",
    "retrace_length",
    "total_length",
    "direction_reversals",
}
NON_COLLAPSE = "carrier != formation hypothesis != decoder != projection"
NON_BACKPROPAGATION = (
    "semantic projection must not back-propagate into formation assessment"
)
NON_AUTHORITY = (
    "This receipt witnesses a reproducible candidate formation, not the historical "
    "formation of the carrier."
)


def _mapping(value: Any, path: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise FieldError(f"{path} must be an object")
    return value


def _list(value: Any, path: str) -> list[Any]:
    if not isinstance(value, list):
        raise FieldError(f"{path} must be an array")
    return value


def _string(value: Any, path: str) -> str:
    if not isinstance(value, str) or not value:
        raise FieldError(f"{path} must be a non-empty string")
    return value


def _bool(value: Any, path: str) -> bool:
    if not isinstance(value, bool):
        raise FieldError(f"{path} must be a boolean")
    return value


def _number(value: Any, path: str) -> float:
    if (
        not isinstance(value, (int, float))
        or isinstance(value, bool)
        or not math.isfinite(float(value))
    ):
        raise FieldError(f"{path} must be a finite number")
    return float(value)


def _source_refs(value: Any, path: str) -> list[str]:
    if value is None:
        return []
    refs = [_string(item, f"{path}[]") for item in _list(value, path)]
    return sorted(refs)


def _pair_key(left: str, right: str) -> tuple[str, str]:
    return tuple(sorted((left, right)))


def _normalize_carrier(raw: Any) -> dict[str, Any]:
    carrier = _mapping(raw, "carrier")
    carrier_id = _string(carrier.get("id"), "carrier.id")
    representation = _mapping(carrier.get("representation"), "carrier.representation")
    if representation.get("kind") != "normalized-landmarks":
        raise FieldError("carrier.representation.kind must equal 'normalized-landmarks'")

    landmarks_raw = _mapping(
        representation.get("landmarks"), "carrier.representation.landmarks"
    )
    if not landmarks_raw:
        raise FieldError("carrier.representation.landmarks must not be empty")
    landmarks: dict[str, list[float]] = {}
    for name, coordinates in landmarks_raw.items():
        landmark_id = _string(name, "carrier.representation.landmark id")
        pair = _list(coordinates, f"carrier.representation.landmarks.{landmark_id}")
        if len(pair) != 2:
            raise FieldError(
                f"carrier.representation.landmarks.{landmark_id} must contain two coordinates"
            )
        landmarks[landmark_id] = [
            _number(pair[0], f"carrier.representation.landmarks.{landmark_id}[0]"),
            _number(pair[1], f"carrier.representation.landmarks.{landmark_id}[1]"),
        ]

    segments_raw = _list(
        representation.get("segments"), "carrier.representation.segments"
    )
    if not segments_raw:
        raise FieldError("carrier.representation.segments must not be empty")
    segment_keys: set[tuple[str, str]] = set()
    for index, segment_raw in enumerate(segments_raw):
        segment = _list(segment_raw, f"carrier.representation.segments[{index}]")
        if len(segment) != 2:
            raise FieldError(
                f"carrier.representation.segments[{index}] must contain two landmark ids"
            )
        left = _string(segment[0], f"carrier.representation.segments[{index}][0]")
        right = _string(segment[1], f"carrier.representation.segments[{index}][1]")
        if left == right:
            raise FieldError("observed carrier segment endpoints must differ")
        if left not in landmarks or right not in landmarks:
            raise FieldError("observed carrier segment references an unknown landmark")
        key = _pair_key(left, right)
        if key in segment_keys:
            raise FieldError("duplicate observed carrier segment")
        segment_keys.add(key)

    return {
        "id": carrier_id,
        "representation": {
            "kind": "normalized-landmarks",
            "landmarks": landmarks,
            "segments": [list(key) for key in sorted(segment_keys)],
        },
        "source_refs": _source_refs(carrier.get("source_refs"), "carrier.source_refs"),
    }


def _normalize_tools(raw: Any) -> list[dict[str, Any]]:
    tools: list[dict[str, Any]] = []
    seen: set[str] = set()
    for index, item in enumerate(_list(raw, "tool_constitutions")):
        tool = _mapping(item, f"tool_constitutions[{index}]")
        tool_id = _string(tool.get("id"), f"tool_constitutions[{index}].id")
        if tool_id in seen:
            raise FieldError(f"duplicate tool constitution id {tool_id!r}")
        seen.add(tool_id)
        visibility = _string(
            tool.get("retrace_visibility"),
            f"tool_constitutions[{index}].retrace_visibility",
        )
        if visibility not in {"low", "high"}:
            raise FieldError("tool retrace_visibility must be 'low' or 'high'")
        tools.append(
            {
                "id": tool_id,
                "kind": _string(tool.get("kind"), f"tool_constitutions[{index}].kind"),
                "allows_lift": _bool(
                    tool.get("allows_lift"), f"tool_constitutions[{index}].allows_lift"
                ),
                "allows_retrace": _bool(
                    tool.get("allows_retrace"),
                    f"tool_constitutions[{index}].allows_retrace",
                ),
                "retrace_visibility": visibility,
            }
        )
    return tools


def _normalize_operations(raw: Any, formation_path: str) -> list[dict[str, Any]]:
    operations: list[dict[str, Any]] = []
    seen: set[str] = set()
    items = _list(raw, f"{formation_path}.operations")
    if not items:
        raise FieldError(f"{formation_path}.operations must not be empty")
    for index, item in enumerate(items):
        operation = _mapping(item, f"{formation_path}.operations[{index}]")
        operation_id = _string(
            operation.get("id"), f"{formation_path}.operations[{index}].id"
        )
        if operation_id in seen:
            raise FieldError(f"duplicate operation id {operation_id!r}")
        seen.add(operation_id)
        op = _string(operation.get("op"), f"{formation_path}.operations[{index}].op")
        if op == "stroke":
            operations.append(
                {
                    "id": operation_id,
                    "op": "stroke",
                    "from": _string(
                        operation.get("from"),
                        f"{formation_path}.operations[{index}].from",
                    ),
                    "to": _string(
                        operation.get("to"),
                        f"{formation_path}.operations[{index}].to",
                    ),
                }
            )
        elif op == "stroke_path":
            through = [
                _string(value, f"{formation_path}.operations[{index}].through[]")
                for value in _list(
                    operation.get("through"),
                    f"{formation_path}.operations[{index}].through",
                )
            ]
            if len(through) < 2:
                raise FieldError("stroke_path must contain at least two landmarks")
            operations.append({"id": operation_id, "op": "stroke_path", "through": through})
        else:
            raise FieldError(f"unsupported formation operation {op!r}")
    return operations


def _normalize_formations(raw: Any) -> list[dict[str, Any]]:
    formations: list[dict[str, Any]] = []
    seen: set[str] = set()
    for index, item in enumerate(_list(raw, "formations")):
        formation = _mapping(item, f"formations[{index}]")
        formation_id = _string(formation.get("id"), f"formations[{index}].id")
        if formation_id in seen:
            raise FieldError(f"duplicate formation id {formation_id!r}")
        seen.add(formation_id)
        formations.append(
            {
                "id": formation_id,
                "origin": _string(
                    formation.get("origin", "manual-hypothesis"),
                    f"formations[{index}].origin",
                ),
                "operations": _normalize_operations(formation.get("operations"), f"formations[{index}]"),
            }
        )
    if not formations:
        raise FieldError("formations must not be empty")
    return formations


def _normalize_gates(raw: Any) -> list[dict[str, Any]]:
    gates: list[dict[str, Any]] = []
    seen: set[str] = set()
    for index, item in enumerate(_list(raw, "formation_gates")):
        gate = _mapping(item, f"formation_gates[{index}]")
        gate_id = _string(gate.get("id"), f"formation_gates[{index}].id")
        if gate_id in seen:
            raise FieldError(f"duplicate formation gate id {gate_id!r}")
        seen.add(gate_id)
        condition = _mapping(
            gate.get("condition"), f"formation_gates[{index}].condition"
        )
        metric = _string(
            condition.get("metric"), f"formation_gates[{index}].condition.metric"
        )
        if metric not in SUPPORTED_METRICS:
            raise FieldError(f"unsupported formation metric {metric!r}")
        if condition.get("op") != "eq":
            raise FieldError("formation gate op must equal 'eq' in v0")
        value = _number(
            condition.get("value"), f"formation_gates[{index}].condition.value"
        )
        gates.append(
            {
                "id": gate_id,
                "condition": {"metric": metric, "op": "eq", "value": value},
            }
        )
    return gates


def _normalize_field(raw: Any) -> dict[str, Any]:
    field = _mapping(raw, "field")
    if field.get("schema") != SCHEMA:
        raise FieldError(f"glyph formation field schema must equal {SCHEMA!r}")
    return {
        "schema": SCHEMA,
        "field_id": _string(field.get("field_id"), "field_id"),
        "carrier": _normalize_carrier(field.get("carrier")),
        "tool_constitutions": _normalize_tools(field.get("tool_constitutions", [])),
        "formations": _normalize_formations(field.get("formations")),
        "formation_gates": _normalize_gates(field.get("formation_gates", [])),
        "source_refs": _source_refs(field.get("source_refs"), "source_refs"),
    }


def _expand_formation(
    formation: dict[str, Any], carrier: dict[str, Any]
) -> list[dict[str, Any]]:
    landmark_ids = set(carrier["representation"]["landmarks"])
    observed = {
        _pair_key(segment[0], segment[1])
        for segment in carrier["representation"]["segments"]
    }
    traversals: list[dict[str, Any]] = []
    for stroke_index, operation in enumerate(formation["operations"]):
        if operation["op"] == "stroke":
            path = [operation["from"], operation["to"]]
        else:
            path = operation["through"]
        for landmark in path:
            if landmark not in landmark_ids:
                raise FieldError(
                    f"formation {formation['id']!r} references unknown landmark {landmark!r}"
                )
        for segment_index, (left, right) in enumerate(zip(path, path[1:], strict=False)):
            if _pair_key(left, right) not in observed:
                raise FieldError(
                    f"formation traversal {left}->{right} is not present in observed carrier"
                )
            traversals.append(
                {
                    "stroke_index": stroke_index,
                    "operation_id": operation["id"],
                    "segment_index": segment_index,
                    "from": left,
                    "to": right,
                }
            )
    return traversals


def _distance(
    landmarks: dict[str, list[float]], left: str, right: str
) -> float:
    x1, y1 = landmarks[left]
    x2, y2 = landmarks[right]
    return math.hypot(x2 - x1, y2 - y1)


def _metrics(
    formation: dict[str, Any],
    carrier: dict[str, Any],
    traversals: list[dict[str, Any]],
) -> dict[str, int | float]:
    landmarks = carrier["representation"]["landmarks"]
    total_length = 0.0
    retrace_length = 0.0
    seen_segments: set[tuple[str, str]] = set()
    direction_reversals = 0
    previous: dict[str, Any] | None = None

    for traversal in traversals:
        length = _distance(landmarks, traversal["from"], traversal["to"])
        total_length += length
        key = _pair_key(traversal["from"], traversal["to"])
        if key in seen_segments:
            retrace_length += length
        else:
            seen_segments.add(key)
        if (
            previous is not None
            and previous["stroke_index"] == traversal["stroke_index"]
            and previous["from"] == traversal["to"]
            and previous["to"] == traversal["from"]
        ):
            direction_reversals += 1
        previous = traversal

    stroke_count = len(formation["operations"])
    return {
        "stroke_count": stroke_count,
        "pen_lifts": max(stroke_count - 1, 0),
        "segment_count": len(traversals),
        "retrace_length": round(retrace_length, 12),
        "total_length": round(total_length, 12),
        "direction_reversals": direction_reversals,
    }


def _tool_results(
    tools: list[dict[str, Any]], metrics: dict[str, int | float]
) -> dict[str, str]:
    results: dict[str, str] = {}
    for tool in tools:
        if not tool["allows_lift"] and metrics["pen_lifts"] > 0:
            state = "incompatible"
        elif not tool["allows_retrace"] and metrics["retrace_length"] > 0:
            state = "incompatible"
        elif metrics["retrace_length"] > 0 and tool["retrace_visibility"] == "high":
            state = "strained"
        else:
            state = "compatible"
        results[tool["id"]] = state
    return results


def _gate_results(
    gates: list[dict[str, Any]], metrics: dict[str, int | float]
) -> dict[str, str]:
    results: dict[str, str] = {}
    for gate in gates:
        condition = gate["condition"]
        metric_value = float(metrics[condition["metric"]])
        results[gate["id"]] = (
            "pass" if metric_value == condition["value"] else "fail"
        )
    return results


def _render_model(
    carrier: dict[str, Any], traversals: list[dict[str, Any]]
) -> dict[str, Any]:
    strokes: list[dict[str, Any]] = []
    by_stroke: dict[int, list[dict[str, Any]]] = {}
    for traversal in traversals:
        by_stroke.setdefault(traversal["stroke_index"], []).append(
            {
                "segment_index": traversal["segment_index"],
                "from": traversal["from"],
                "to": traversal["to"],
            }
        )
    for stroke_index in sorted(by_stroke):
        first = next(
            traversal
            for traversal in traversals
            if traversal["stroke_index"] == stroke_index
        )
        strokes.append(
            {
                "stroke_index": stroke_index,
                "operation_id": first["operation_id"],
                "traversals": by_stroke[stroke_index],
            }
        )
    return {
        "landmarks": carrier["representation"]["landmarks"],
        "carrier_segments": carrier["representation"]["segments"],
        "strokes": strokes,
    }


def compile_glyph_formation(raw_field: Any, formation_id: str) -> dict[str, Any]:
    """Compile one declared glyph formation hypothesis into a deterministic receipt."""

    if not isinstance(formation_id, str) or not formation_id:
        raise FieldError("formation_id must be a non-empty string")
    field = _normalize_field(raw_field)
    formation_index = {item["id"]: item for item in field["formations"]}
    if formation_id not in formation_index:
        raise FieldError(f"unknown formation {formation_id!r}")

    # Validate every declared candidate against the observed carrier so malformed
    # unselected histories cannot hide inside an otherwise accepted field.
    expanded = {
        item["id"]: _expand_formation(item, field["carrier"])
        for item in field["formations"]
    }
    formation = formation_index[formation_id]
    traversals = expanded[formation_id]
    metrics = _metrics(formation, field["carrier"], traversals)

    carrier_value = field["carrier"]
    formation_value = {
        "id": formation["id"],
        "origin": formation["origin"],
        "operations": formation["operations"],
    }
    receipt: dict[str, Any] = {
        "schema": RECEIPT_SCHEMA,
        "field_id": field["field_id"],
        "carrier": {**carrier_value, "digest": canonical_digest(carrier_value)},
        "formation": {
            **formation_value,
            "digest": canonical_digest(formation_value),
        },
        "metrics": metrics,
        "tool_results": _tool_results(field["tool_constitutions"], metrics),
        "gates": _gate_results(field["formation_gates"], metrics),
        "render_model": _render_model(field["carrier"], traversals),
        "source_refs": field["source_refs"],
        "non_collapse": NON_COLLAPSE,
        "non_backpropagation": NON_BACKPROPAGATION,
        "non_authority": NON_AUTHORITY,
    }
    receipt["receipt_digest"] = canonical_digest(receipt)
    return receipt

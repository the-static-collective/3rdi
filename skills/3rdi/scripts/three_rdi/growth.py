"""Deterministic, explicitly witnessed growth of simple glyph graphs.

A growth receipt preserves declared existing vertices and edges. It is not
evidence of how a historical glyph arose, nor the inverse of a quotient.
"""

from __future__ import annotations

import math
from typing import Any

from .model import FieldError, canonical_digest
from .transition import _carrier, _topology

FIELD_SCHEMA = "3rdi.glyph-growth-field/v0"
RECEIPT_SCHEMA = "3rdi.glyph-growth-receipt/v0"
OPERATORS = ("EXTEND", "BEND", "RETURN", "FORK")
EPS = 1e-9


def _vector(a: list[float], b: list[float]) -> tuple[float, float]:
    return b[0] - a[0], b[1] - a[1]


def _dot(a: tuple[float, float], b: tuple[float, float]) -> float:
    return a[0] * b[0] + a[1] * b[1]


def _cross(a: tuple[float, float], b: tuple[float, float]) -> float:
    return a[0] * b[1] - a[1] * b[0]


def _orthogonal(a: tuple[float, float], b: tuple[float, float]) -> bool:
    return abs(_dot(a, b)) <= EPS * math.hypot(*a) * math.hypot(*b)


def _path(graph: dict[str, Any]) -> list[str]:
    """Recover either orientation of a connected simple path, deterministically."""
    topo = _topology(graph)
    if topo["components"] != 1 or topo["cycle_rank"] != 0 or len(topo["endpoints"]) != 2:
        raise FieldError("expected connected simple path")
    adj = {node: set() for node in graph["landmarks"]}
    for a, b in graph["segments"]:
        adj[a].add(b)
        adj[b].add(a)
    out, previous, current = [], None, min(topo["endpoints"])
    while current is not None:
        out.append(current)
        options = sorted(adj[current] - ({previous} if previous else set()))
        if len(options) > 1:
            raise FieldError("expected connected simple path without forks")
        previous, current = current, options[0] if options else None
    return out


def _validate_growth(source: dict[str, Any], target: dict[str, Any],
                     op: dict[str, Any]) -> dict[str, Any]:
    kind = op["kind"]
    retain = op.get("retain")
    if not isinstance(retain, dict) or set(retain) != set(source["landmarks"]):
        raise FieldError("growth requires a total retain map of source vertices")
    if (any(not isinstance(v, str) or v not in target["landmarks"] for v in retain.values())
            or len(set(retain.values())) != len(retain)):
        raise FieldError("retain must injectively map to target vertices")
    # Growth in v0 does not quietly move or delete the inherited geometry.
    for original, descendant in retain.items():
        if source["landmarks"][original] != target["landmarks"][descendant]:
            raise FieldError("growth must preserve coordinates of retained vertices")
    existing_edges = {tuple(sorted((retain[a], retain[b]))) for a, b in source["segments"]}
    target_edges = {tuple(e) for e in target["segments"]}
    if not existing_edges <= target_edges:
        raise FieldError("growth must preserve every inherited edge")
    extra_vertices = set(target["landmarks"]) - set(retain.values())
    extra_edges = target_edges - existing_edges
    old = _topology(source)
    new = _topology(target)

    if kind == "EXTEND":
        if not (old["vertices"] == 1 and old["edges"] == 0
                and new["vertices"] == 2 and new["edges"] == 1
                and len(extra_vertices) == 1 and len(extra_edges) == 1):
            raise FieldError("EXTEND requires point -> one-edge line")
        invariant = ["retained origin", "connectedness"]

    elif kind == "BEND":
        if not (old["vertices"] == 2 and old["edges"] == 1
                and new["vertices"] == 3 and new["edges"] == 2
                and len(extra_vertices) == 1 and len(extra_edges) == 1):
            raise FieldError("BEND requires one-edge line -> two-edge path")
        p = _path(target)
        pts = target["landmarks"]
        v1 = _vector(pts[p[1]], pts[p[0]])
        v2 = _vector(pts[p[1]], pts[p[2]])
        if not _orthogonal(v1, v2):
            raise FieldError("BEND requires a right-angle turn in v0")
        invariant = ["original line edge", "connectedness", "simple path"]

    elif kind == "RETURN":
        if not (old["vertices"] == 3 and old["edges"] == 2
                and new["vertices"] == 4 and new["edges"] == 3
                and len(extra_vertices) == 1 and len(extra_edges) == 1):
            raise FieldError("RETURN requires L path -> U path")
        # Orient new path so the single new vertex is last.
        p = _path(target)
        tip = next(iter(extra_vertices))
        if p[0] == tip:
            p.reverse()
        if p[-1] != tip:
            raise FieldError("RETURN requires extension at an existing endpoint")
        pts = target["landmarks"]
        v1 = _vector(pts[p[0]], pts[p[1]])
        v2 = _vector(pts[p[1]], pts[p[2]])
        v3 = _vector(pts[p[2]], pts[p[3]])
        if not (_orthogonal(v1, v2) and _orthogonal(v2, v3)
                and _dot(v1, v3) < -EPS * math.hypot(*v1) * math.hypot(*v3)
                and _cross(v1, v2) * _cross(v2, v3) > 0):
            raise FieldError("RETURN requires an open U with opposite parallel uprights")
        invariant = ["inherited L edges", "connectedness", "simple path", "open endpoints"]

    elif kind == "FORK":
        if not (old["vertices"] == 1 and old["edges"] == 0
                and new["vertices"] == 4 and new["edges"] == 3
                and len(extra_vertices) == 3 and len(extra_edges) == 3
                and len(new["branchpoints"]) == 1
                and set(new["branchpoints"]) == set(retain.values())
                and len(new["endpoints"]) == 3):
            raise FieldError("FORK requires one point -> degree-three Y junction")
        invariant = ["retained origin as junction", "connectedness"]

    else:
        raise FieldError(f"unknown growth operator {kind!r}")

    if new["components"] != 1 or new["cycle_rank"] != 0:
        raise FieldError("growth may not introduce disconnected parts or cycles")
    return {
        "kind": kind,
        "retain": dict(sorted(retain.items())),
        "added_vertices": sorted(extra_vertices),
        "added_edges": [list(edge) for edge in sorted(extra_edges)],
        "preserved_inherited_edges": len(existing_edges),
        "preserves": invariant,
        "non_inverse": "Growth is not the inverse of quotient compression; it requires a declared generative rule.",
    }


def compile_glyph_growth(field: Any, operation_id: str) -> dict[str, Any]:
    """Compile one named, declared growth transition into a canonical receipt."""
    if not isinstance(operation_id, str) or not operation_id:
        raise FieldError("operation_id must be a non-empty string")
    if (not isinstance(field, dict)
            or set(field) != {"schema", "field_id", "carriers", "operations", "source_refs"}
            or field["schema"] != FIELD_SCHEMA):
        raise FieldError(f"field must conform to {FIELD_SCHEMA}")
    if not isinstance(field["field_id"], str) or not field["field_id"]:
        raise FieldError("field_id must be non-empty")
    if not isinstance(field["carriers"], dict) or not 1 <= len(field["carriers"]) <= 64:
        raise FieldError("carriers must be a non-empty map of at most 64 glyphs")
    carriers = {}
    for key, carrier in field["carriers"].items():
        if not isinstance(key, str) or not key:
            raise FieldError("carrier identifiers must be non-empty strings")
        carriers[key] = _carrier(carrier, f"carriers[{key}]")
    refs = field["source_refs"]
    if (not isinstance(refs, list) or any(not isinstance(ref, str) or not ref for ref in refs)
            or len(set(refs)) != len(refs)):
        raise FieldError("source_refs must be unique non-empty strings")
    raw_ops = field["operations"]
    if not isinstance(raw_ops, list) or not 1 <= len(raw_ops) <= 64:
        raise FieldError("operations must be a list of 1..64 entries")
    operations = {}
    for op in raw_ops:
        if not isinstance(op, dict) or set(op) != {"id", "kind", "from", "to", "retain"}:
            raise FieldError("growth operation fields must be id, kind, from, to, retain")
        for key in ("id", "from", "to"):
            if not isinstance(op[key], str) or not op[key]:
                raise FieldError(f"growth {key} must be non-empty")
        if op["id"] in operations:
            raise FieldError("duplicate growth operation id")
        if op["kind"] not in OPERATORS:
            raise FieldError("unknown growth operator")
        if op["from"] not in carriers or op["to"] not in carriers:
            raise FieldError("growth references unknown carrier")
        operations[op["id"]] = op
    if operation_id not in operations:
        raise FieldError(f"unknown growth operation {operation_id!r}")
    op = operations[operation_id]
    source = carriers[op["from"]]
    target = carriers[op["to"]]
    effect = _validate_growth(source, target, op)
    value = {
        "schema": RECEIPT_SCHEMA,
        "field_id": field["field_id"],
        "source": {"id": op["from"], "digest": canonical_digest(source), "topology": _topology(source)},
        "target": {"id": op["to"], "digest": canonical_digest(target), "topology": _topology(target)},
        "operation": {"id": operation_id, **effect},
        "source_refs": sorted(refs),
        "non_collapse": "declared growth != historical ancestry != semantic identity != authority",
        "non_authority": "This receipt proves declared graph consistency, not its historical origin or significance.",
    }
    return {**value, "receipt_digest": canonical_digest(value)}

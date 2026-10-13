"""Receipt-first transitions between declared glyph graphs.

This sidecar does not infer handwriting, semantics, history or authority.
"""

from __future__ import annotations

import math
from collections import Counter
from typing import Any

from .model import FieldError, canonical_digest

FIELD_SCHEMA = "3rdi.glyph-transition-field/v0"
RECEIPT_SCHEMA = "3rdi.glyph-transition-receipt/v0"
MAX_VERTICES = 128
MAX_EDGES = 256


def _object(value: Any, where: str, keys: set[str]) -> dict[str, Any]:
    if not isinstance(value, dict) or set(value) != keys:
        raise FieldError(f"{where} must be an object with exactly {sorted(keys)}")
    return value


def _name(value: Any, where: str) -> str:
    if not isinstance(value, str) or not value:
        raise FieldError(f"{where} must be a non-empty string")
    return value


def _carrier(raw: Any, where: str) -> dict[str, Any]:
    graph = _object(raw, where, {"kind", "landmarks", "segments"})
    if graph["kind"] != "normalized-landmarks":
        raise FieldError(f"{where}.kind must be normalized-landmarks")
    landmarks = graph["landmarks"]
    if not isinstance(landmarks, dict) or not 1 <= len(landmarks) <= MAX_VERTICES:
        raise FieldError(f"{where}.landmarks must have 1..{MAX_VERTICES} vertices")
    normalized = {}
    positions = set()
    for label, coords in landmarks.items():
        _name(label, f"{where}.landmark")
        if (not isinstance(coords, list) or len(coords) != 2
                or any(isinstance(c, bool) or not isinstance(c, (int, float))
                       or not math.isfinite(c) for c in coords)):
            raise FieldError(f"{where}.landmarks[{label}] requires two finite numbers")
        xy = [float(c) for c in coords]
        if tuple(xy) in positions:
            raise FieldError(f"{where} has coincident landmark coordinates")
        positions.add(tuple(xy))
        normalized[label] = xy
    segments = graph["segments"]
    if not isinstance(segments, list) or len(segments) > MAX_EDGES:
        raise FieldError(f"{where}.segments must be an array of at most {MAX_EDGES} edges")
    edges = set()
    for i, segment in enumerate(segments):
        if (not isinstance(segment, list) or len(segment) != 2
                or any(not isinstance(v, str) or v not in normalized for v in segment)
                or segment[0] == segment[1]):
            raise FieldError(f"{where}.segments[{i}] has invalid endpoints")
        pair = tuple(sorted(segment))
        if pair in edges:
            raise FieldError(f"{where} has a duplicate undirected segment")
        edges.add(pair)
    return {"kind": "normalized-landmarks", "landmarks": dict(sorted(normalized.items())),
            "segments": [list(e) for e in sorted(edges)]}


def _topology(graph: dict[str, Any]) -> dict[str, Any]:
    adjacency = {node: set() for node in graph["landmarks"]}
    for a, b in graph["segments"]:
        adjacency[a].add(b)
        adjacency[b].add(a)
    seen = set()
    components = 0
    for node in sorted(adjacency):
        if node in seen:
            continue
        components += 1
        pending = [node]
        while pending:
            current = pending.pop()
            if current in seen:
                continue
            seen.add(current)
            pending.extend(adjacency[current] - seen)
    degrees = Counter(len(neighbors) for neighbors in adjacency.values())
    vertices = len(adjacency)
    edges = len(graph["segments"])
    return {"vertices": vertices, "edges": edges, "components": components,
            "cycle_rank": edges - vertices + components,
            "degree_histogram": {str(k): degrees[k] for k in sorted(degrees)},
            "endpoints": sorted(n for n in adjacency if len(adjacency[n]) == 1),
            "branchpoints": sorted(n for n in adjacency if len(adjacency[n]) >= 3)}


def _quotient(source: dict[str, Any], target: dict[str, Any], transition: dict[str, Any]) -> dict[str, Any]:
    mapping = transition.get("vertex_map")
    if not isinstance(mapping, dict) or set(mapping) != set(source["landmarks"]):
        raise FieldError("QUOTIENT requires a total vertex_map of source vertices")
    if any(v not in target["landmarks"] for v in mapping.values()):
        raise FieldError("QUOTIENT maps to an unknown target vertex")
    if set(mapping.values()) != set(target["landmarks"]):
        raise FieldError("QUOTIENT vertex_map must cover every target vertex")
    target_edges = {tuple(edge) for edge in target["segments"]}
    projected_edges = set()
    collapsed = 0
    for a, b in source["segments"]:
        x, y = mapping[a], mapping[b]
        if x == y:
            collapsed += 1
        else:
            edge = tuple(sorted((x, y)))
            if edge not in target_edges:
                raise FieldError("QUOTIENT would introduce an unobserved target edge")
            projected_edges.add(edge)
    if projected_edges != target_edges:
        raise FieldError("QUOTIENT target edges not covered by source mapping")
    return {"kind": "QUOTIENT", "vertex_map": dict(sorted(mapping.items())),
            "collapsed_source_edges": collapsed,
            "distinct_source_vertices_lost": len(source["landmarks"]) - len(target["landmarks"]),
            "invertible_from_visible_target": False,
            "preserves": ["declared target incidence under vertex_map"],
            "loses": ["distinct source vertex positions", "source edge trajectories"]}


def _deform(source: dict[str, Any], target: dict[str, Any], transition: dict[str, Any],
            source_topology: dict[str, Any], target_topology: dict[str, Any]) -> dict[str, Any]:
    """Bounded graph homeomorphism: connected simple paths, subdivisions allowed."""
    for topo in (source_topology, target_topology):
        if (topo["components"] != 1 or topo["cycle_rank"] != 0
                or len(topo["endpoints"]) != 2 or topo["branchpoints"]
                or topo["vertices"] < 2):
            raise FieldError("DEFORM v0 requires two connected simple path graphs")
    endpoints = transition.get("endpoint_map")
    if (not isinstance(endpoints, dict)
            or set(endpoints) != set(source_topology["endpoints"])
            or set(endpoints.values()) != set(target_topology["endpoints"])
            or len(set(endpoints.values())) != 2):
        raise FieldError("DEFORM requires a bijective endpoint_map")
    return {"kind": "DEFORM", "endpoint_map": dict(sorted(endpoints.items())),
            "subdivision_vertices_delta": target_topology["vertices"] - source_topology["vertices"],
            "preserves": ["one connected component", "two endpoints", "zero cycles",
                          "zero branchpoints", "endpoint pairing"],
            "does_not_establish": ["a physical morph animation", "equal geometric lengths",
                                   "same stroke history", "historical ancestry"]}


def compile_glyph_transition(raw_field: Any, transition_id: str) -> dict[str, Any]:
    """Validate a declared graph transition and return an attributable deterministic receipt."""
    _name(transition_id, "transition_id")
    field = _object(raw_field, "field", {"schema", "field_id", "carriers", "transitions", "source_refs"})
    if field["schema"] != FIELD_SCHEMA:
        raise FieldError(f"field.schema must equal {FIELD_SCHEMA!r}")
    field_id = _name(field["field_id"], "field_id")
    raw_carriers = field["carriers"]
    if not isinstance(raw_carriers, dict) or not 1 <= len(raw_carriers) <= 64:
        raise FieldError("carriers must be a non-empty mapping of at most 64 graphs")
    carriers = {_name(k, "carrier id"): _carrier(v, f"carriers[{k}]")
                for k, v in raw_carriers.items()}
    raw_refs = field["source_refs"]
    if (not isinstance(raw_refs, list) or any(not isinstance(r, str) or not r for r in raw_refs)
            or len(set(raw_refs)) != len(raw_refs)):
        raise FieldError("source_refs must be unique non-empty strings")
    if not isinstance(field["transitions"], list) or not 1 <= len(field["transitions"]) <= 64:
        raise FieldError("transitions must be 1..64 entries")
    transitions = {}
    for item in field["transitions"]:
        if not isinstance(item, dict):
            raise FieldError("transition must be an object")
        kind = item.get("kind")
        keys = {"id", "kind", "from", "to", "vertex_map"} if kind == "QUOTIENT" else (
            {"id", "kind", "from", "to", "endpoint_map"} if kind == "DEFORM" else None)
        if keys is None:
            raise FieldError("transition kind must be QUOTIENT or DEFORM")
        _object(item, "transition", keys)
        item_id = _name(item["id"], "transition.id")
        if item_id in transitions:
            raise FieldError("duplicate transition id")
        for direction in ("from", "to"):
            if item[direction] not in carriers:
                raise FieldError(f"transition {item_id} references unknown {direction} carrier")
        transitions[item_id] = item
    if transition_id not in transitions:
        raise FieldError(f"unknown transition {transition_id!r}")
    item = transitions[transition_id]
    source, target = carriers[item["from"]], carriers[item["to"]]
    a, b = _topology(source), _topology(target)
    operation = (_quotient(source, target, item) if item["kind"] == "QUOTIENT"
                 else _deform(source, target, item, a, b))
    source_receipt = {"id": item["from"], "digest": canonical_digest(source), "topology": a}
    target_receipt = {"id": item["to"], "digest": canonical_digest(target), "topology": b}
    value = {"schema": RECEIPT_SCHEMA, "field_id": field_id,
             "source": source_receipt, "target": target_receipt,
             "transition": {"id": item["id"], **operation},
             "source_refs": sorted(raw_refs),
             "non_collapse": "visible output != preserved source history != formation != authority",
             "non_authority": "This is a declared graph transformation, not a historical or semantic claim."}
    return {**value, "receipt_digest": canonical_digest(value)}

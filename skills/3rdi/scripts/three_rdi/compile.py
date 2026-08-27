"""Pure observer-local projection compilation for the 3rdi v0 floor."""

from __future__ import annotations

from typing import Any

from .model import FieldError, canonical_digest, normalize_field, parse_instant


NON_AUTHORITY = (
    "This receipt is a cut-relative projection witness. It is not the source, "
    "canonical truth, admission authority, or permission to execute side effects."
)


def _chronological_relation(occurred_at: str, focus_at: str) -> str:
    occurred = parse_instant(occurred_at, "occurrence.occurred_at")
    focus = parse_instant(focus_at, "cut.focus_at")
    if occurred < focus:
        return "past"
    if occurred == focus:
        return "present"
    return "future"


def _matching_exposure(
    occurrence_id: str,
    exposures: list[dict[str, Any]],
    cut: dict[str, Any],
) -> dict[str, Any] | None:
    known = parse_instant(cut["known_at"], "cut.known_at")
    admitted_layers = set(cut.get("audience_layers", []))
    candidates = [
        exposure
        for exposure in exposures
        if exposure["occurrence_id"] == occurrence_id
        and exposure["observer"] == cut["observer"]
        and exposure["layer"] in admitted_layers
        and parse_instant(exposure["available_from"], "exposure.available_from") <= known
    ]
    if not candidates:
        return None
    return min(candidates, key=lambda item: (item["available_from"], item["id"]))


def _compile_occurrences(
    field: dict[str, Any], cut: dict[str, Any]
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    visible: list[dict[str, Any]] = []
    withheld: list[dict[str, Any]] = []
    scope = set(cut.get("location_scope", []))
    focus = parse_instant(cut["focus_at"], "cut.focus_at")

    for occurrence in field["occurrences"]:
        relation = _chronological_relation(occurrence["occurred_at"], cut["focus_at"])
        occurrence_id = occurrence["id"]
        if relation == "future":
            withheld.append(
                {
                    "occurrence_id": occurrence_id,
                    "reason": "future-occurrence",
                    "chronological_relation": relation,
                    "available_at_cut": False,
                    "perceived_role": "unknown",
                }
            )
            continue
        if scope and occurrence.get("locus_id") not in scope:
            withheld.append(
                {
                    "occurrence_id": occurrence_id,
                    "reason": "outside-location-scope",
                    "chronological_relation": relation,
                    "available_at_cut": False,
                    "perceived_role": "unknown",
                }
            )
            continue
        exposure = _matching_exposure(occurrence_id, field["exposures"], cut)
        if exposure is None:
            withheld.append(
                {
                    "occurrence_id": occurrence_id,
                    "reason": "not-available",
                    "chronological_relation": relation,
                    "available_at_cut": False,
                    "perceived_role": "unknown",
                }
            )
            continue

        available_at = parse_instant(exposure["available_from"], "exposure.available_from")
        visible.append(
            {
                "id": occurrence_id,
                "occurred_at": occurrence["occurred_at"],
                "locus_id": occurrence.get("locus_id"),
                "chronological_relation": relation,
                "perceived_role": relation,
                "available_at_cut": True,
                "available_via": {
                    "exposure_id": exposure["id"],
                    "available_from": exposure["available_from"],
                    "layer": exposure["layer"],
                    "evidence_refs": exposure.get("evidence_refs", []),
                },
                "hindsight_bearing": available_at > focus,
                "source_refs": occurrence.get("source_refs", []),
            }
        )

    return visible, withheld


def _compile_expectations(
    field: dict[str, Any], cut: dict[str, Any]
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    visible: list[dict[str, Any]] = []
    withheld: list[dict[str, Any]] = []
    focus = parse_instant(cut["focus_at"], "cut.focus_at")
    known = parse_instant(cut["known_at"], "cut.known_at")
    admitted_layers = set(cut.get("audience_layers", []))

    for expectation in field["expectations"]:
        formed = parse_instant(expectation["formed_at"], "expectation.formed_at")
        available = parse_instant(expectation["available_from"], "expectation.available_from")
        if expectation["observer"] != cut["observer"]:
            withheld.append({"expectation_id": expectation["id"], "reason": "different-observer"})
            continue
        if expectation["layer"] not in admitted_layers:
            withheld.append({"expectation_id": expectation["id"], "reason": "audience-layer-closed"})
            continue
        if formed > focus:
            withheld.append({"expectation_id": expectation["id"], "reason": "not-yet-formed"})
            continue
        if available > known:
            withheld.append({"expectation_id": expectation["id"], "reason": "not-available"})
            continue

        target = parse_instant(expectation["target_at"], "expectation.target_at")
        if target > focus:
            role = "anticipated-future"
        elif target == focus:
            role = "present-expectation"
        else:
            role = "past-expectation"
        visible.append(
            {
                **expectation,
                "perceived_role": role,
                "hindsight_bearing": available > focus,
            }
        )

    return visible, withheld


def _compile_edges(
    field: dict[str, Any],
    cut: dict[str, Any],
    visible_occurrence_ids: set[str],
) -> tuple[dict[str, list[dict[str, Any]]], list[dict[str, Any]]]:
    known = parse_instant(cut["known_at"], "cut.known_at")
    focus = parse_instant(cut["focus_at"], "cut.focus_at")
    visible: dict[str, list[dict[str, Any]]] = {"causal": [], "relevance": []}
    withheld: list[dict[str, Any]] = []
    admitted_layers = set(cut.get("audience_layers", []))

    for edge in field["edges"]:
        edge_id = edge["id"]
        perceived = parse_instant(edge["first_perceived_at"], "edge.first_perceived_at")
        if perceived > known:
            withheld.append({"edge_id": edge_id, "reason": "not-yet-perceived"})
            continue
        if edge["from"] not in visible_occurrence_ids or edge["to"] not in visible_occurrence_ids:
            withheld.append({"edge_id": edge_id, "reason": "endpoint-withheld"})
            continue
        exposure_candidates = [
            exposure
            for exposure in field["edge_exposures"]
            if exposure["edge_id"] == edge_id
            and exposure["observer"] == cut["observer"]
            and exposure["layer"] in admitted_layers
            and parse_instant(exposure["available_from"], "edge_exposure.available_from")
            <= known
        ]
        if not exposure_candidates:
            withheld.append({"edge_id": edge_id, "reason": "not-available-to-observer"})
            continue
        exposure = min(
            exposure_candidates,
            key=lambda item: (item["available_from"], item["id"]),
        )
        available = parse_instant(
            exposure["available_from"], "edge_exposure.available_from"
        )
        history = [
            assessment
            for assessment in edge.get("assessments", [])
            if parse_instant(assessment["assessed_at"], "assessment.assessed_at") <= known
        ]
        current = history[-1] if history else None
        visible[edge["edge_class"]].append(
            {
                "id": edge_id,
                "from": edge["from"],
                "to": edge["to"],
                "edge_class": edge["edge_class"],
                "relation": edge["relation"],
                "first_perceived_at": edge["first_perceived_at"],
                "discovery_trace": edge.get("discovery_trace", []),
                "formation_history": history,
                "current_assessment": current,
                "available_via": {
                    "edge_exposure_id": exposure["id"],
                    "available_from": exposure["available_from"],
                    "layer": exposure["layer"],
                    "evidence_refs": exposure.get("evidence_refs", []),
                },
                "hindsight_bearing": available > focus
                or perceived > focus
                or any(
                    parse_instant(item["assessed_at"], "assessment.assessed_at") > focus
                    for item in history
                ),
            }
        )

    return visible, withheld


def _condition_result(
    condition: dict[str, Any],
    visible_occurrences: dict[str, dict[str, Any]],
    visible_edges: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    kind = condition["kind"]
    if kind == "occurrence_visible":
        occurrence_id = condition["occurrence_id"]
        state = "pass" if occurrence_id in visible_occurrences else "fail"
        return {"condition": condition, "state": state, "reason": f"occurrence is {state}"}
    if kind == "perceived_role":
        occurrence = visible_occurrences.get(condition["occurrence_id"])
        if occurrence is None:
            return {"condition": condition, "state": "unresolved", "reason": "occurrence withheld"}
        state = "pass" if occurrence["perceived_role"] == condition["role"] else "fail"
        return {"condition": condition, "state": state, "reason": "role comparison"}
    if kind == "edge_status":
        edge = visible_edges.get(condition["edge_id"])
        if edge is None or edge["current_assessment"] is None:
            return {"condition": condition, "state": "unresolved", "reason": "edge assessment unavailable"}
        state = (
            "pass"
            if edge["current_assessment"]["status"] == condition["status"]
            else "fail"
        )
        return {"condition": condition, "state": state, "reason": "edge status comparison"}
    raise FieldError(f"unsupported gate condition {kind!r}")


def _combine_gate(operator: str, states: list[str]) -> str:
    if operator == "not":
        return {"pass": "fail", "fail": "pass", "unresolved": "unresolved"}[states[0]]
    if operator == "all":
        if "fail" in states:
            return "fail"
        if "unresolved" in states:
            return "unresolved"
        return "pass"
    if "pass" in states:
        return "pass"
    if "unresolved" in states:
        return "unresolved"
    return "fail"


def _compile_gates(
    field: dict[str, Any],
    cut: dict[str, Any],
    occurrences: list[dict[str, Any]],
    edges: dict[str, list[dict[str, Any]]],
) -> list[dict[str, Any]]:
    gate_index = {gate["id"]: gate for gate in field["gates"]}
    occurrence_index = {item["id"]: item for item in occurrences}
    edge_index = {
        edge["id"]: edge
        for edge_class in ("causal", "relevance")
        for edge in edges[edge_class]
    }
    results: list[dict[str, Any]] = []
    for gate_id in sorted(cut.get("gate_ids", [])):
        gate = gate_index[gate_id]
        conditions = [
            _condition_result(condition, occurrence_index, edge_index)
            for condition in gate["conditions"]
        ]
        results.append(
            {
                "id": gate_id,
                "op": gate["op"],
                "state": _combine_gate(gate["op"], [item["state"] for item in conditions]),
                "conditions": conditions,
                "source_refs": gate.get("source_refs", []),
                "pure": True,
            }
        )
    return results


def _compile_location_claims(
    field: dict[str, Any],
    cut: dict[str, Any],
    visible_occurrence_ids: set[str],
) -> list[dict[str, Any]]:
    known = parse_instant(cut["known_at"], "cut.known_at")
    focus = parse_instant(cut["focus_at"], "cut.focus_at")
    admitted_layers = set(cut.get("audience_layers", []))
    decoder_index = {item["id"]: item for item in field["location_decoders"]}
    visible: list[dict[str, Any]] = []
    for claim in field["location_claims"]:
        available = parse_instant(claim["available_from"], "location_claim.available_from")
        if (
            claim["occurrence_id"] not in visible_occurrence_ids
            or claim["observer"] != cut["observer"]
            or claim["layer"] not in admitted_layers
            or available > known
        ):
            continue
        decoder = {**decoder_index[claim["decoder_id"]], "performed_by_3rdi": False}
        visible.append(
            {
                **claim,
                "decoder": decoder,
                "hindsight_bearing": available > focus,
            }
        )
    return visible


def _compile_cones(
    cut: dict[str, Any],
    visible_occurrence_ids: set[str],
    edges: dict[str, list[dict[str, Any]]],
) -> dict[str, dict[str, list[str]]]:
    """Compute admitted directed descendants for causal and relevance ledgers."""

    roots = sorted(
        occurrence_id
        for occurrence_id in cut.get("focus_occurrence_ids", [])
        if occurrence_id in visible_occurrence_ids
    )
    cones: dict[str, dict[str, list[str]]] = {}
    for edge_class in ("causal", "relevance"):
        adjacency: dict[str, set[str]] = {}
        for edge in edges[edge_class]:
            assessment = edge["current_assessment"]
            if assessment is None or assessment["status"] != "admitted":
                continue
            adjacency.setdefault(edge["from"], set()).add(edge["to"])

        descendants: set[str] = set()
        frontier = list(reversed(roots))
        visited = set(roots)
        while frontier:
            current = frontier.pop()
            for target in sorted(adjacency.get(current, set())):
                if target in visited:
                    continue
                visited.add(target)
                descendants.add(target)
                frontier.append(target)
        cones[edge_class] = {
            "root_ids": roots,
            "descendant_ids": sorted(descendants),
        }
    return cones


def compile_cut(raw_field: Any, cut_id: str) -> dict[str, Any]:
    """Compile one immutable field into an observer-local projection receipt."""

    field = normalize_field(raw_field)
    cut_index = {cut["id"]: cut for cut in field["cuts"]}
    if cut_id not in cut_index:
        raise FieldError(f"unknown cut {cut_id!r}")
    cut = cut_index[cut_id]

    occurrences, withheld_occurrences = _compile_occurrences(field, cut)
    expectations, withheld_expectations = _compile_expectations(field, cut)
    visible_ids = {item["id"] for item in occurrences}
    edges, withheld_edges = _compile_edges(field, cut, visible_ids)
    gates = _compile_gates(field, cut, occurrences, edges)
    location_claims = _compile_location_claims(field, cut, visible_ids)
    cones = _compile_cones(cut, visible_ids, edges)

    causal_ledger = [edge for edge in field["edges"] if edge["edge_class"] == "causal"]
    relevance_ledger = [edge for edge in field["edges"] if edge["edge_class"] == "relevance"]
    receipt: dict[str, Any] = {
        "schema": "3rdi.projection-receipt/v0",
        "field_id": field["field_id"],
        "cut": cut,
        "observer_view": {
            "occurrences": occurrences,
            "expectations": expectations,
            "edges": edges,
            "location_claims": location_claims,
            "gates": gates,
            "cones": cones,
            "render_model": {
                "node_ids": [item["id"] for item in occurrences],
                "causal_edge_ids": [item["id"] for item in edges["causal"]],
                "relevance_edge_ids": [item["id"] for item in edges["relevance"]],
            },
        },
        "audit": {
            "input_digest": canonical_digest(field),
            "cut_digest": canonical_digest(cut),
            "causal_ledger_digest": canonical_digest(causal_ledger),
            "relevance_ledger_digest": canonical_digest(relevance_ledger),
            "withheld": withheld_occurrences,
            "withheld_expectations": withheld_expectations,
            "withheld_edges": withheld_edges,
            "non_authority": NON_AUTHORITY,
        },
    }
    receipt["projection_digest"] = canonical_digest(receipt)
    return receipt

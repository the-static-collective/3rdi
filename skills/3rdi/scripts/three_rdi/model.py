"""Boundary parsing and canonicalization for the 3rdi reference kernel."""

from __future__ import annotations

import copy
import hashlib
import json
import math
import re
from datetime import datetime
from typing import Any


RFC3339_UTC = re.compile(
    r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?Z$"
)
EDGE_CLASSES = {"causal", "relevance"}
EDGE_STATUSES = {"perceived", "admitted", "weakened", "refused", "unresolved"}
GATE_OPERATORS = {"all", "any", "not"}
GATE_CONDITIONS = {"occurrence_visible", "edge_status", "perceived_role"}
CUT_MODES = {"historical", "reconstruction"}
ATTENTION_ACTIONS = {"attended", "ignored", "abandoned"}
STANCE_VALUES = {"accepted", "held", "rejected"}


class FieldError(ValueError):
    """Raised when external field data violates the v0 boundary contract."""


def canonical_json(value: Any) -> str:
    """Return deterministic compact JSON for an already normalized value."""

    try:
        return json.dumps(
            value,
            ensure_ascii=False,
            allow_nan=False,
            separators=(",", ":"),
            sort_keys=True,
        )
    except (TypeError, ValueError) as error:
        raise FieldError("receipt values must be finite JSON-compatible data") from error


def canonical_digest(value: Any) -> str:
    """Return a namespaced SHA-256 digest for a JSON-compatible value."""

    payload = canonical_json(value).encode("utf-8")
    return f"sha256:{hashlib.sha256(payload).hexdigest()}"


def parse_instant(value: Any, path: str) -> datetime:
    """Parse a strict UTC RFC 3339 timestamp from the input boundary."""

    if not isinstance(value, str) or RFC3339_UTC.fullmatch(value) is None:
        raise FieldError(f"{path} must be an RFC 3339 UTC timestamp ending in Z")
    try:
        return datetime.fromisoformat(value[:-1] + "+00:00")
    except ValueError as error:
        raise FieldError(f"{path} must be a valid RFC 3339 UTC timestamp") from error


def _require_mapping(value: Any, path: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise FieldError(f"{path} must be an object")
    return value


def _require_list(value: Any, path: str) -> list[Any]:
    if not isinstance(value, list):
        raise FieldError(f"{path} must be an array")
    return value


def _require_string(value: Any, path: str) -> str:
    if not isinstance(value, str) or not value:
        raise FieldError(f"{path} must be a non-empty string")
    return value


def _require_string_list(value: Any, path: str) -> list[str]:
    items = _require_list(value, path)
    for index, item in enumerate(items):
        _require_string(item, f"{path}[{index}]")
    return items


def _require_finite_number(
    value: Any,
    path: str,
    *,
    minimum: float | None = None,
    maximum: float | None = None,
) -> float:
    if not isinstance(value, (int, float)) or isinstance(value, bool):
        raise FieldError(f"{path} must be numeric")
    number = float(value)
    if not math.isfinite(number):
        raise FieldError(f"{path} must be finite")
    if minimum is not None and number < minimum:
        raise FieldError(f"{path} must be at least {minimum}")
    if maximum is not None and number > maximum:
        raise FieldError(f"{path} must be at most {maximum}")
    return number


def _index_unique(items: list[dict[str, Any]], path: str) -> dict[str, dict[str, Any]]:
    result: dict[str, dict[str, Any]] = {}
    for index, item in enumerate(items):
        item_id = _require_string(item.get("id"), f"{path}[{index}].id")
        if item_id in result:
            raise FieldError(f"{path} contains duplicate id {item_id!r}")
        result[item_id] = item
    return result


def _sort_string_lists(value: Any) -> Any:
    """Sort list-valued set fields while preserving sequence-valued data."""

    if isinstance(value, dict):
        normalized: dict[str, Any] = {}
        for key, child in value.items():
            normalized[key] = _sort_string_lists(child)
            if key in {
                "source_refs",
                "evidence_refs",
                "discovery_trace",
                "audience_layers",
                "location_scope",
                "focus_occurrence_ids",
                "gate_ids",
            } and isinstance(normalized[key], list):
                normalized[key] = sorted(normalized[key])
        return normalized
    if isinstance(value, list):
        return [_sort_string_lists(child) for child in value]
    return value


def normalize_field(raw: Any) -> dict[str, Any]:
    """Validate and normalize `3rdi.field/v0` at the system boundary."""

    field = copy.deepcopy(_require_mapping(raw, "field"))
    if field.get("schema") != "3rdi.field/v0":
        raise FieldError("field.schema must equal '3rdi.field/v0'")
    _require_string(field.get("field_id"), "field.field_id")

    list_keys = (
        "occurrences",
        "exposures",
        "expectations",
        "edges",
        "edge_exposures",
        "location_decoders",
        "location_claims",
        "gates",
        "cuts",
        "contacts",
        "attention_events",
        "decoder_applications",
        "stances",
    )
    for key in list_keys:
        field.setdefault(key, [])
        entries = _require_list(field[key], f"field.{key}")
        for index, entry in enumerate(entries):
            _require_mapping(entry, f"field.{key}[{index}]")

    if "source_refs" in field:
        _require_string_list(field["source_refs"], "field.source_refs")

    occurrences = _index_unique(field["occurrences"], "field.occurrences")
    exposures = _index_unique(field["exposures"], "field.exposures")
    expectations = _index_unique(field["expectations"], "field.expectations")
    edges = _index_unique(field["edges"], "field.edges")
    edge_exposures = _index_unique(field["edge_exposures"], "field.edge_exposures")
    decoders = _index_unique(field["location_decoders"], "field.location_decoders")
    location_claims = _index_unique(field["location_claims"], "field.location_claims")
    gates = _index_unique(field["gates"], "field.gates")
    cuts = _index_unique(field["cuts"], "field.cuts")
    contacts = _index_unique(field["contacts"], "field.contacts")
    attention_events = _index_unique(field["attention_events"], "field.attention_events")
    decoder_applications = _index_unique(
        field["decoder_applications"], "field.decoder_applications"
    )
    stances = _index_unique(field["stances"], "field.stances")

    for occurrence_id, occurrence in occurrences.items():
        parse_instant(occurrence.get("occurred_at"), f"occurrence {occurrence_id}.occurred_at")
        if "locus_id" in occurrence:
            _require_string(occurrence["locus_id"], f"occurrence {occurrence_id}.locus_id")
        _require_string_list(
            occurrence.get("source_refs", []),
            f"occurrence {occurrence_id}.source_refs",
        )

    for exposure_id, exposure in exposures.items():
        occurrence_id = _require_string(
            exposure.get("occurrence_id"), f"exposure {exposure_id}.occurrence_id"
        )
        if occurrence_id not in occurrences:
            raise FieldError(f"exposure {exposure_id} references unknown occurrence {occurrence_id!r}")
        _require_string(exposure.get("observer"), f"exposure {exposure_id}.observer")
        _require_string(exposure.get("layer"), f"exposure {exposure_id}.layer")
        available = parse_instant(
            exposure.get("available_from"), f"exposure {exposure_id}.available_from"
        )
        occurred = parse_instant(
            occurrences[occurrence_id]["occurred_at"],
            f"occurrence {occurrence_id}.occurred_at",
        )
        if available < occurred:
            raise FieldError(
                f"exposure {exposure_id}.available_from cannot precede the occurrence; "
                "represent forecasts as expectations"
            )
        _require_string_list(
            exposure.get("evidence_refs", []), f"exposure {exposure_id}.evidence_refs"
        )

    for contact_id, contact in contacts.items():
        occurrence_id = _require_string(
            contact.get("occurrence_id"), f"contact {contact_id}.occurrence_id"
        )
        if occurrence_id not in occurrences:
            raise FieldError(f"contact {contact_id} references unknown occurrence {occurrence_id!r}")
        observer = _require_string(contact.get("observer"), f"contact {contact_id}.observer")
        layer = _require_string(contact.get("layer"), f"contact {contact_id}.layer")
        sensed = parse_instant(contact.get("sensed_at"), f"contact {contact_id}.sensed_at")
        _require_string_list(
            contact.get("evidence_refs", []), f"contact {contact_id}.evidence_refs"
        )
        lawful_exposure = any(
            exposure["occurrence_id"] == occurrence_id
            and exposure["observer"] == observer
            and exposure["layer"] == layer
            and parse_instant(
                exposure["available_from"], f"exposure {exposure_id}.available_from"
            )
            <= sensed
            for exposure_id, exposure in exposures.items()
        )
        if not lawful_exposure:
            raise FieldError(
                f"contact {contact_id} has no lawful exposure available by sensed_at"
            )

    for attention_id, attention in attention_events.items():
        contact_id = _require_string(
            attention.get("contact_id"), f"attention {attention_id}.contact_id"
        )
        if contact_id not in contacts:
            raise FieldError(
                f"attention {attention_id} references unknown contact {contact_id!r}"
            )
        observer = _require_string(
            attention.get("observer"), f"attention {attention_id}.observer"
        )
        if observer != contacts[contact_id]["observer"]:
            raise FieldError(
                f"attention {attention_id} observer must match contact observer"
            )
        action = _require_string(attention.get("action"), f"attention {attention_id}.action")
        if action not in ATTENTION_ACTIONS:
            raise FieldError(
                f"attention {attention_id}.action must be attended, ignored, or abandoned"
            )
        occurred = parse_instant(
            attention.get("occurred_at"), f"attention {attention_id}.occurred_at"
        )
        sensed = parse_instant(
            contacts[contact_id]["sensed_at"], f"contact {contact_id}.sensed_at"
        )
        if occurred < sensed:
            raise FieldError(f"attention {attention_id} cannot precede contact")
        _require_string_list(
            attention.get("evidence_refs", []), f"attention {attention_id}.evidence_refs"
        )

    for application_id, application in decoder_applications.items():
        contact_id = _require_string(
            application.get("contact_id"),
            f"decoder application {application_id}.contact_id",
        )
        if contact_id not in contacts:
            raise FieldError(
                f"decoder application {application_id} references unknown contact {contact_id!r}"
            )
        observer = _require_string(
            application.get("observer"),
            f"decoder application {application_id}.observer",
        )
        if observer != contacts[contact_id]["observer"]:
            raise FieldError(
                f"decoder application {application_id} observer must match contact observer"
            )
        _require_string(
            application.get("decoder_ref"),
            f"decoder application {application_id}.decoder_ref",
        )
        _require_string(
            application.get("projection_ref"),
            f"decoder application {application_id}.projection_ref",
        )
        applied = parse_instant(
            application.get("applied_at"),
            f"decoder application {application_id}.applied_at",
        )
        sensed = parse_instant(
            contacts[contact_id]["sensed_at"], f"contact {contact_id}.sensed_at"
        )
        if applied < sensed:
            raise FieldError(
                f"decoder application {application_id} cannot precede contact"
            )
        _require_string_list(
            application.get("evidence_refs", []),
            f"decoder application {application_id}.evidence_refs",
        )

    for stance_id, stance in stances.items():
        observer = _require_string(stance.get("observer"), f"stance {stance_id}.observer")
        projection_ref = _require_string(
            stance.get("projection_ref"), f"stance {stance_id}.projection_ref"
        )
        stance_value = _require_string(stance.get("stance"), f"stance {stance_id}.stance")
        if stance_value not in STANCE_VALUES:
            raise FieldError(
                f"stance {stance_id}.stance must be accepted, held, or rejected"
            )
        formed = parse_instant(stance.get("formed_at"), f"stance {stance_id}.formed_at")
        _require_string_list(
            stance.get("evidence_refs", []), f"stance {stance_id}.evidence_refs"
        )
        matching_applications = [
            application
            for application in decoder_applications.values()
            if application["observer"] == observer
            and application["projection_ref"] == projection_ref
        ]
        if not matching_applications:
            raise FieldError(
                f"stance {stance_id} references unknown observer projection {projection_ref!r}"
            )
        earliest_application = min(
            matching_applications,
            key=lambda item: parse_instant(item["applied_at"], "decoder application.applied_at"),
        )
        applied = parse_instant(
            earliest_application["applied_at"], "decoder application.applied_at"
        )
        if formed < applied:
            raise FieldError(f"stance {stance_id} cannot precede decoding")

    for expectation_id, expectation in expectations.items():
        _require_string(expectation.get("observer"), f"expectation {expectation_id}.observer")
        _require_string(expectation.get("layer"), f"expectation {expectation_id}.layer")
        _require_string(expectation.get("statement"), f"expectation {expectation_id}.statement")
        formed = parse_instant(
            expectation.get("formed_at"), f"expectation {expectation_id}.formed_at"
        )
        available = parse_instant(
            expectation.get("available_from"), f"expectation {expectation_id}.available_from"
        )
        target = parse_instant(
            expectation.get("target_at"), f"expectation {expectation_id}.target_at"
        )
        if available < formed:
            raise FieldError(f"expectation {expectation_id}.available_from cannot precede formed_at")
        if target < formed:
            raise FieldError(f"expectation {expectation_id}.target_at cannot precede formed_at")
        _require_string_list(
            expectation.get("evidence_refs", []), f"expectation {expectation_id}.evidence_refs"
        )

    for edge_id, edge in edges.items():
        from_id = _require_string(edge.get("from"), f"edge {edge_id}.from")
        to_id = _require_string(edge.get("to"), f"edge {edge_id}.to")
        if from_id not in occurrences or to_id not in occurrences:
            raise FieldError(f"edge {edge_id} references unknown occurrence")
        edge_class = _require_string(edge.get("edge_class"), f"edge {edge_id}.edge_class")
        if edge_class not in EDGE_CLASSES:
            raise FieldError(f"edge {edge_id}.edge_class must be causal or relevance")
        _require_string(edge.get("relation"), f"edge {edge_id}.relation")
        first_perceived = parse_instant(
            edge.get("first_perceived_at"), f"edge {edge_id}.first_perceived_at"
        )
        _require_string_list(
            edge.get("discovery_trace", []), f"edge {edge_id}.discovery_trace"
        )
        assessments = _require_list(edge.get("assessments", []), f"edge {edge_id}.assessments")
        for index, assessment_value in enumerate(assessments):
            assessment = _require_mapping(
                assessment_value, f"edge {edge_id}.assessments[{index}]"
            )
            assessed = parse_instant(
                assessment.get("assessed_at"),
                f"edge {edge_id}.assessments[{index}].assessed_at",
            )
            if assessed < first_perceived:
                raise FieldError(f"edge {edge_id} assessment cannot precede first perception")
            status = _require_string(
                assessment.get("status"), f"edge {edge_id}.assessments[{index}].status"
            )
            if status not in EDGE_STATUSES:
                raise FieldError(f"edge {edge_id} assessment has unsupported status {status!r}")
            _require_finite_number(
                assessment.get("confidence"),
                f"edge {edge_id} assessment confidence",
                minimum=0,
                maximum=1,
            )
            _require_string(assessment.get("reason"), f"edge {edge_id} assessment reason")
            _require_string_list(
                assessment.get("evidence_refs", []),
                f"edge {edge_id}.assessments[{index}].evidence_refs",
            )

    for exposure_id, exposure in edge_exposures.items():
        edge_id = _require_string(
            exposure.get("edge_id"), f"edge exposure {exposure_id}.edge_id"
        )
        if edge_id not in edges:
            raise FieldError(
                f"edge exposure {exposure_id} references unknown edge {edge_id!r}"
            )
        _require_string(exposure.get("observer"), f"edge exposure {exposure_id}.observer")
        _require_string(exposure.get("layer"), f"edge exposure {exposure_id}.layer")
        available = parse_instant(
            exposure.get("available_from"),
            f"edge exposure {exposure_id}.available_from",
        )
        perceived = parse_instant(
            edges[edge_id]["first_perceived_at"],
            f"edge {edge_id}.first_perceived_at",
        )
        if available < perceived:
            raise FieldError(
                f"edge exposure {exposure_id}.available_from cannot precede edge perception"
            )
        _require_string_list(
            exposure.get("evidence_refs", []),
            f"edge exposure {exposure_id}.evidence_refs",
        )

    for decoder_id, decoder in decoders.items():
        for key in ("source_crs", "target_crs", "operation", "area_of_use"):
            _require_string(decoder.get(key), f"location decoder {decoder_id}.{key}")
        _require_finite_number(
            decoder.get("accuracy_m"),
            f"location decoder {decoder_id}.accuracy_m",
            minimum=0,
        )
        _require_string_list(
            decoder.get("source_refs", []), f"location decoder {decoder_id}.source_refs"
        )

    for claim_id, claim in location_claims.items():
        occurrence_id = _require_string(
            claim.get("occurrence_id"), f"location claim {claim_id}.occurrence_id"
        )
        if occurrence_id not in occurrences:
            raise FieldError(f"location claim {claim_id} references unknown occurrence")
        decoder_id = _require_string(
            claim.get("decoder_id"), f"location claim {claim_id}.decoder_id"
        )
        if decoder_id not in decoders:
            raise FieldError(f"location claim {claim_id} references unknown decoder")
        locus_id = _require_string(claim.get("locus_id"), f"location claim {claim_id}.locus_id")
        if occurrences[occurrence_id].get("locus_id") != locus_id:
            raise FieldError(f"location claim {claim_id} cannot replace the occurrence locus")
        _require_string(claim.get("observer"), f"location claim {claim_id}.observer")
        _require_string(claim.get("layer"), f"location claim {claim_id}.layer")
        available = parse_instant(
            claim.get("available_from"), f"location claim {claim_id}.available_from"
        )
        occurred = parse_instant(
            occurrences[occurrence_id]["occurred_at"],
            f"occurrence {occurrence_id}.occurred_at",
        )
        if available < occurred:
            raise FieldError(f"location claim {claim_id}.available_from cannot precede occurrence")
        coordinates = _require_list(claim.get("coordinates"), f"location claim {claim_id}.coordinates")
        if len(coordinates) < 2:
            raise FieldError(f"location claim {claim_id}.coordinates must contain at least two axes")
        for index, value in enumerate(coordinates):
            _require_finite_number(
                value,
                f"location claim {claim_id}.coordinates[{index}]",
            )
        coordinate_crs = _require_string(
            claim.get("coordinate_crs"), f"location claim {claim_id}.coordinate_crs"
        )
        if coordinate_crs != decoders[decoder_id]["source_crs"]:
            raise FieldError(
                f"location claim {claim_id}.coordinate_crs must match the decoder source_crs; "
                "the v0 kernel does not perform the target operation"
            )
        _require_finite_number(
            claim.get("uncertainty_m"),
            f"location claim {claim_id}.uncertainty_m",
            minimum=0,
        )
        _require_string_list(
            claim.get("evidence_refs", []), f"location claim {claim_id}.evidence_refs"
        )

    for gate_id, gate in gates.items():
        operator = _require_string(gate.get("op"), f"gate {gate_id}.op")
        if operator not in GATE_OPERATORS:
            raise FieldError(f"gate {gate_id}.op must be all, any, or not")
        conditions = _require_list(gate.get("conditions"), f"gate {gate_id}.conditions")
        if operator == "not" and len(conditions) != 1:
            raise FieldError(f"gate {gate_id} with op not requires exactly one condition")
        if not conditions:
            raise FieldError(f"gate {gate_id} requires at least one condition")
        for index, condition_value in enumerate(conditions):
            condition = _require_mapping(condition_value, f"gate {gate_id}.conditions[{index}]")
            kind = _require_string(
                condition.get("kind"), f"gate {gate_id}.conditions[{index}].kind"
            )
            if kind not in GATE_CONDITIONS:
                raise FieldError(f"gate {gate_id} has unsupported condition kind {kind!r}")
            if kind in {"occurrence_visible", "perceived_role"}:
                occurrence_id = _require_string(
                    condition.get("occurrence_id"),
                    f"gate {gate_id}.conditions[{index}].occurrence_id",
                )
                if occurrence_id not in occurrences:
                    raise FieldError(f"gate {gate_id} references unknown occurrence")
            if kind == "perceived_role":
                _require_string(condition.get("role"), f"gate {gate_id} condition role")
            if kind == "edge_status":
                edge_id = _require_string(
                    condition.get("edge_id"), f"gate {gate_id}.conditions[{index}].edge_id"
                )
                if edge_id not in edges:
                    raise FieldError(f"gate {gate_id} references unknown edge")
                status = _require_string(condition.get("status"), f"gate {gate_id} condition status")
                if status not in EDGE_STATUSES:
                    raise FieldError(f"gate {gate_id} condition has unsupported edge status")
        _require_string_list(gate.get("source_refs", []), f"gate {gate_id}.source_refs")

    for cut_id, cut in cuts.items():
        _require_string(cut.get("observer"), f"cut {cut_id}.observer")
        mode = _require_string(cut.get("mode"), f"cut {cut_id}.mode")
        if mode not in CUT_MODES:
            raise FieldError(f"cut {cut_id}.mode must be historical or reconstruction")
        focus = parse_instant(cut.get("focus_at"), f"cut {cut_id}.focus_at")
        known = parse_instant(cut.get("known_at"), f"cut {cut_id}.known_at")
        if mode == "historical" and known > focus:
            raise FieldError(f"cut {cut_id}.known_at cannot exceed focus_at in historical mode")
        _require_string_list(cut.get("audience_layers", []), f"cut {cut_id}.audience_layers")
        _require_string_list(cut.get("location_scope", []), f"cut {cut_id}.location_scope")
        focus_ids = _require_string_list(
            cut.get("focus_occurrence_ids", []),
            f"cut {cut_id}.focus_occurrence_ids",
        )
        for occurrence_id in focus_ids:
            if occurrence_id not in occurrences:
                raise FieldError(
                    f"cut {cut_id} references unknown focus occurrence {occurrence_id!r}"
                )
        gate_ids = _require_string_list(cut.get("gate_ids", []), f"cut {cut_id}.gate_ids")
        for gate_id in gate_ids:
            if gate_id not in gates:
                raise FieldError(f"cut {cut_id} references unknown gate {gate_id!r}")

    normalized = _sort_string_lists(field)
    for key in list_keys:
        normalized[key] = sorted(normalized[key], key=lambda item: item["id"])
    for edge in normalized["edges"]:
        edge["assessments"] = sorted(
            edge.get("assessments", []),
            key=lambda item: (item["assessed_at"], item["status"], canonical_json(item)),
        )
    for gate in normalized["gates"]:
        gate["conditions"] = sorted(gate["conditions"], key=canonical_json)
    return normalized
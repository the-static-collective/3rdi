"""Observer-local epistemic record validation layered over the base field model."""

from __future__ import annotations

from typing import Any

from .model import (
    FieldError,
    _index_unique,
    _require_list,
    _require_mapping,
    _require_string,
    _require_string_list,
    normalize_field as _normalize_base_field,
    parse_instant,
)

ATTENTION_ACTIONS = {"attended", "ignored", "abandoned"}
STANCE_VALUES = {"accepted", "held", "rejected"}
_EPISTEMIC_FAMILIES = (
    "contacts",
    "attention_events",
    "decoder_applications",
    "stances",
)


def normalize_field(raw: Any) -> dict[str, Any]:
    """Validate the base field plus attributable observer epistemic records."""

    field = _normalize_base_field(raw)
    for key in _EPISTEMIC_FAMILIES:
        field.setdefault(key, [])
        entries = _require_list(field[key], f"field.{key}")
        for index, entry in enumerate(entries):
            _require_mapping(entry, f"field.{key}[{index}]")

    occurrences = {item["id"]: item for item in field["occurrences"]}
    exposures = {item["id"]: item for item in field["exposures"]}
    contacts = _index_unique(field["contacts"], "field.contacts")
    attention_events = _index_unique(field["attention_events"], "field.attention_events")
    decoder_applications = _index_unique(
        field["decoder_applications"], "field.decoder_applications"
    )
    stances = _index_unique(field["stances"], "field.stances")

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
            raise FieldError(f"attention {attention_id} observer must match contact observer")
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
            raise FieldError(f"decoder application {application_id} cannot precede contact")
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
            key=lambda item: parse_instant(
                item["applied_at"], "decoder application.applied_at"
            ),
        )
        applied = parse_instant(
            earliest_application["applied_at"], "decoder application.applied_at"
        )
        if formed < applied:
            raise FieldError(f"stance {stance_id} cannot precede decoding")

    for key in _EPISTEMIC_FAMILIES:
        field[key] = sorted(field[key], key=lambda item: item["id"])
    return field

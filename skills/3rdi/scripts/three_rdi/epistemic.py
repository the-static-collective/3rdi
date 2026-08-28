"""Observer-local epistemic trace compilation layered over the phase-0 cut compiler."""

from __future__ import annotations

from typing import Any

from .compile import compile_cut as _compile_base_cut
from .model import FieldError, canonical_digest, normalize_field, parse_instant


def _with_hindsight(record: dict[str, Any], *, time_field: str, focus_at: str) -> dict[str, Any]:
    return {
        **record,
        "hindsight_bearing": parse_instant(record[time_field], f"epistemic.{time_field}")
        > parse_instant(focus_at, "cut.focus_at"),
    }


def _withheld(kind: str, reason: str) -> dict[str, str]:
    """Return observer-safe diagnostic category without hidden event identity."""

    return {"kind": kind, "reason": reason}


def _compile_epistemic_trace(
    field: dict[str, Any],
    cut: dict[str, Any],
    visible_occurrence_ids: set[str],
) -> tuple[dict[str, list[dict[str, Any]]], list[dict[str, str]]]:
    observer = cut["observer"]
    admitted_layers = set(cut.get("audience_layers", []))
    known = parse_instant(cut["known_at"], "cut.known_at")
    focus_at = cut["focus_at"]
    withheld: list[dict[str, str]] = []

    contacts: list[dict[str, Any]] = []
    for contact in field["contacts"]:
        reason: str | None = None
        if contact["observer"] != observer:
            reason = "different-observer"
        elif contact["layer"] not in admitted_layers:
            reason = "audience-layer-closed"
        elif contact["occurrence_id"] not in visible_occurrence_ids:
            reason = "occurrence-withheld"
        elif parse_instant(contact["sensed_at"], "contact.sensed_at") > known:
            reason = "beyond-known-at"
        if reason is not None:
            withheld.append(_withheld("contact", reason))
            continue
        contacts.append(_with_hindsight(contact, time_field="sensed_at", focus_at=focus_at))

    selected_contact_ids = {item["id"] for item in contacts}

    attention_events: list[dict[str, Any]] = []
    for attention in field["attention_events"]:
        reason = None
        if attention["observer"] != observer:
            reason = "different-observer"
        elif attention["contact_id"] not in selected_contact_ids:
            reason = "contact-withheld"
        elif parse_instant(attention["occurred_at"], "attention.occurred_at") > known:
            reason = "beyond-known-at"
        if reason is not None:
            withheld.append(_withheld("attention", reason))
            continue
        attention_events.append(
            _with_hindsight(attention, time_field="occurred_at", focus_at=focus_at)
        )

    decoder_applications: list[dict[str, Any]] = []
    for application in field["decoder_applications"]:
        reason = None
        if application["observer"] != observer:
            reason = "different-observer"
        elif application["contact_id"] not in selected_contact_ids:
            reason = "contact-withheld"
        elif parse_instant(application["applied_at"], "decoder.applied_at") > known:
            reason = "beyond-known-at"
        if reason is not None:
            withheld.append(_withheld("decoder", reason))
            continue
        decoder_applications.append(
            _with_hindsight(application, time_field="applied_at", focus_at=focus_at)
        )

    selected_projection_refs = {item["projection_ref"] for item in decoder_applications}

    stances: list[dict[str, Any]] = []
    for stance in field["stances"]:
        reason = None
        if stance["observer"] != observer:
            reason = "different-observer"
        elif stance["projection_ref"] not in selected_projection_refs:
            reason = "projection-withheld"
        elif parse_instant(stance["formed_at"], "stance.formed_at") > known:
            reason = "beyond-known-at"
        if reason is not None:
            withheld.append(_withheld("stance", reason))
            continue
        stances.append(_with_hindsight(stance, time_field="formed_at", focus_at=focus_at))

    trace = {
        "contacts": contacts,
        "attention_events": attention_events,
        "decoder_applications": decoder_applications,
        "stances": stances,
    }
    withheld = [
        {"kind": kind, "reason": reason}
        for kind, reason in sorted({(item["kind"], item["reason"]) for item in withheld})
    ]
    return trace, withheld


def compile_cut(raw_field: Any, cut_id: str) -> dict[str, Any]:
    """Compile one cut and attach attributable observer-local epistemic history."""

    field = normalize_field(raw_field)
    cut_index = {cut["id"]: cut for cut in field["cuts"]}
    if cut_id not in cut_index:
        raise FieldError(f"unknown cut {cut_id!r}")
    cut = cut_index[cut_id]

    receipt = _compile_base_cut(field, cut_id)
    visible_ids = {item["id"] for item in receipt["observer_view"]["occurrences"]}
    trace, withheld = _compile_epistemic_trace(field, cut, visible_ids)
    receipt["observer_view"]["epistemic_trace"] = trace
    receipt["audit"]["withheld_epistemic"] = withheld
    receipt.pop("projection_digest", None)
    receipt["projection_digest"] = canonical_digest(receipt)
    return receipt

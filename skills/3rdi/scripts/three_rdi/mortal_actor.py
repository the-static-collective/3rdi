"""Minimal observer-safe handoff from a 3rdi projection to mortal-actor consumers."""

from __future__ import annotations

from typing import Any

from .model import FieldError


def _required_string(value: object, message: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise FieldError(message)
    return value


def _ids(items: object) -> list[str]:
    if not isinstance(items, list):
        return []
    values = [item.get("id") for item in items if isinstance(item, dict)]
    return sorted({value for value in values if isinstance(value, str) and value})


def mortal_actor_handoff(receipt: dict[str, Any]) -> dict[str, Any]:
    """Project a compiled observer receipt into a small cross-stack identity handoff."""

    if not isinstance(receipt, dict) or receipt.get("schema") != "3rdi.projection-receipt/v0":
        raise FieldError("projection receipt required")
    projection_digest = _required_string(receipt.get("projection_digest"), "projection digest required")
    field_id = _required_string(receipt.get("field_id"), "projection field required")
    cut = receipt.get("cut")
    if not isinstance(cut, dict):
        raise FieldError("projection cut required")
    cut_id = _required_string(cut.get("id"), "projection cut required")
    observer = _required_string(cut.get("observer"), "projection observer required")
    view = receipt.get("observer_view")
    if not isinstance(view, dict):
        raise FieldError("projection observer view required")
    trace = view.get("epistemic_trace")
    if not isinstance(trace, dict):
        raise FieldError("mortal actor handoff requires epistemic trace support")

    edges = view.get("edges") if isinstance(view.get("edges"), dict) else {}
    return {
        "schema": "mortal_actor.3rdi-handoff/v0",
        "projection_digest": projection_digest,
        "field_id": field_id,
        "cut_id": cut_id,
        "observer": observer,
        "visible_occurrence_ids": _ids(view.get("occurrences")),
        "visible_causal_edge_ids": _ids(edges.get("causal")),
        "visible_relevance_edge_ids": _ids(edges.get("relevance")),
        "contact_ids": _ids(trace.get("contacts")),
        "attention_event_ids": _ids(trace.get("attention_events")),
        "decoder_application_ids": _ids(trace.get("decoder_applications")),
        "stance_ids": _ids(trace.get("stances")),
    }

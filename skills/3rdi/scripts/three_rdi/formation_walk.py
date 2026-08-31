"""Observer-local formation-walk projection layered over the epistemic compiler."""

from __future__ import annotations

import copy
from typing import Any

from .epistemic import compile_cut as _compile_prior_cut
from .epistemic_model import normalize_field as _normalize_prior_field
from .model import (
    FieldError,
    _index_unique,
    _require_list,
    _require_mapping,
    _require_string,
    _require_string_list,
    canonical_digest,
    parse_instant,
)


def normalize_field(raw: Any) -> dict[str, Any]:
    """Validate the epistemic field plus optional supplied formation-walk receipts."""

    raw_field = copy.deepcopy(_require_mapping(raw, "field"))
    raw_walks = raw_field.pop("formation_walks", [])
    walks = _require_list(raw_walks, "field.formation_walks")
    for index, walk in enumerate(walks):
        _require_mapping(walk, f"field.formation_walks[{index}]")

    field = _normalize_prior_field(raw_field)
    occurrence_ids = {item["id"] for item in field["occurrences"]}
    walk_index = _index_unique(walks, "field.formation_walks")
    normalized_walks: list[dict[str, Any]] = []

    for walk_id, raw_walk in walk_index.items():
        endpoint = _require_string(
            raw_walk.get("endpoint_occurrence_id"),
            f"formation walk {walk_id}.endpoint_occurrence_id",
        )
        if endpoint not in occurrence_ids:
            raise FieldError(
                f"formation walk {walk_id} references unknown endpoint occurrence {endpoint!r}"
            )
        observer = _require_string(
            raw_walk.get("observer"), f"formation walk {walk_id}.observer"
        )
        layer = _require_string(raw_walk.get("layer"), f"formation walk {walk_id}.layer")
        formed_at = _require_string(
            raw_walk.get("formed_at"), f"formation walk {walk_id}.formed_at"
        )
        available_from = _require_string(
            raw_walk.get("available_from"),
            f"formation walk {walk_id}.available_from",
        )
        parse_instant(formed_at, f"formation walk {walk_id}.formed_at")
        parse_instant(available_from, f"formation walk {walk_id}.available_from")
        step_refs = list(
            _require_string_list(
                raw_walk.get("step_refs"), f"formation walk {walk_id}.step_refs"
            )
        )
        source_refs = sorted(
            _require_string_list(
                raw_walk.get("source_refs"), f"formation walk {walk_id}.source_refs"
            )
        )
        normalized_walks.append(
            {
                "id": walk_id,
                "endpoint_occurrence_id": endpoint,
                "observer": observer,
                "layer": layer,
                "formed_at": formed_at,
                "available_from": available_from,
                "step_refs": step_refs,
                "source_refs": source_refs,
            }
        )

    field["formation_walks"] = sorted(normalized_walks, key=lambda item: item["id"])
    return field


def _walk_visibility_reason(
    walk: dict[str, Any],
    *,
    cut: dict[str, Any],
    visible_occurrence_ids: set[str],
) -> str | None:
    if walk["observer"] != cut["observer"]:
        return "different-observer"
    if walk["layer"] not in set(cut.get("audience_layers", [])):
        return "audience-layer-closed"
    known_at = parse_instant(cut["known_at"], "cut.known_at")
    if parse_instant(walk["formed_at"], f"formation walk {walk['id']}.formed_at") > known_at:
        return "not-yet-formed"
    if (
        parse_instant(
            walk["available_from"], f"formation walk {walk['id']}.available_from"
        )
        > known_at
    ):
        return "not-available"
    if walk["endpoint_occurrence_id"] not in visible_occurrence_ids:
        return "endpoint-withheld"
    return None


def compile_cut(raw_field: Any, cut_id: str) -> dict[str, Any]:
    """Compile one epistemic cut and expose only lawfully available formation walks."""

    raw_mapping = _require_mapping(raw_field, "field")
    if "formation_walks" not in raw_mapping:
        # Omission is a strict compatibility path against the compiler that
        # immediately precedes the walk layer in the composed public surface.
        return _compile_prior_cut(raw_mapping, cut_id)

    field = normalize_field(raw_mapping)
    cut_index = {cut["id"]: cut for cut in field["cuts"]}
    if cut_id not in cut_index:
        raise FieldError(f"unknown cut {cut_id!r}")
    cut = cut_index[cut_id]

    # Formation-walk bytes are removed before the prior epistemic compiler is
    # invoked. Hidden walk bodies therefore cannot leak into its receipt or
    # digest. Only lawfully visible walk data is added afterward.
    prior_field = copy.deepcopy(field)
    prior_field.pop("formation_walks", None)
    receipt = _compile_prior_cut(prior_field, cut_id)
    visible_occurrence_ids = {
        item["id"] for item in receipt["observer_view"]["occurrences"]
    }
    focus_at = parse_instant(cut["focus_at"], "cut.focus_at")

    visible: list[dict[str, Any]] = []
    withheld: list[dict[str, str]] = []
    for walk in field["formation_walks"]:
        reason = _walk_visibility_reason(
            walk,
            cut=cut,
            visible_occurrence_ids=visible_occurrence_ids,
        )
        if reason is not None:
            withheld.append(
                {
                    "id": walk["id"],
                    "endpoint_occurrence_id": walk["endpoint_occurrence_id"],
                    "reason": reason,
                }
            )
            continue
        visible.append(
            {
                **walk,
                "hindsight_bearing": parse_instant(
                    walk["available_from"],
                    f"formation walk {walk['id']}.available_from",
                )
                > focus_at,
            }
        )

    receipt["observer_view"]["formation_walks"] = sorted(
        visible, key=lambda item: item["id"]
    )
    receipt["audit"]["withheld_formation_walks"] = sorted(
        withheld, key=lambda item: item["id"]
    )
    receipt.pop("projection_digest", None)
    receipt["projection_digest"] = canonical_digest(receipt)
    return receipt

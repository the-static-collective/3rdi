#!/usr/bin/env python3
"""Run the deterministic 3rdi hatch controls and emit one lab receipt."""

from __future__ import annotations

import argparse
import copy
import json
import sys
from pathlib import Path
from typing import Any, Sequence

from three_rdi import FieldError, canonical_digest, compile_cut, decode_fret_glyph


ROOT = Path(__file__).resolve().parents[3]


def _load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def _by_id(items: list[dict[str, Any]], item_id: str) -> dict[str, Any]:
    return next(item for item in items if item["id"] == item_id)


def _lab(lab_id: str, checks: dict[str, bool], evidence: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": lab_id,
        "status": "pass" if all(checks.values()) else "fail",
        "checks": checks,
        "evidence": evidence,
    }


def run_labs() -> dict[str, Any]:
    """Execute every named hatch control against committed specimens."""

    field = _load_json(ROOT / "specimens" / "temporal-coordinate-001.json")
    glyph_spec = _load_json(ROOT / "specimens" / "glyph-receiver-001.json")

    occurrence_digest_before = canonical_digest(field["occurrences"])
    early = compile_cut(field, "june-10")
    june = compile_cut(field, "june-15")
    occurrence_digest_after = canonical_digest(field["occurrences"])
    early_ids = {item["id"] for item in early["observer_view"]["occurrences"]}
    june_ids = {item["id"] for item in june["observer_view"]["occurrences"]}
    hidden_early = {item["occurrence_id"]: item["reason"] for item in early["audit"]["withheld"]}
    shuffled = copy.deepcopy(field)
    _by_id(shuffled["occurrences"], "breadcrumb")["occurred_at"], _by_id(
        shuffled["occurrences"], "artifact"
    )["occurred_at"] = (
        _by_id(shuffled["occurrences"], "artifact")["occurred_at"],
        _by_id(shuffled["occurrences"], "breadcrumb")["occurred_at"],
    )
    chronology_rejected = False
    try:
        compile_cut(shuffled, "june-15")
    except FieldError:
        chronology_rejected = True
    temporal = _lab(
        "TEMPORAL-COORDINATE-001",
        {
            "occurrences_immutable": occurrence_digest_before == occurrence_digest_after,
            "artifact_unavailable_early": "artifact" not in early_ids,
            "artifact_visible_later": "artifact" in june_ids,
            "future_withheld": hidden_early.get("later-discovery") == "future-occurrence",
            "expectation_visible": any(
                item["id"] == "expected-rain"
                and item["perceived_role"] == "anticipated-future"
                for item in early["observer_view"]["expectations"]
            ),
            "chronology_shuffle_breaks": chronology_rejected,
        },
        {
            "early_digest": early["projection_digest"],
            "june_digest": june["projection_digest"],
            "occurrence_digest": occurrence_digest_before,
        },
    )

    before_relevance = copy.deepcopy(field)
    before_relevance["edges"] = [
        edge for edge in before_relevance["edges"] if edge["edge_class"] != "relevance"
    ]
    retained_edge_ids = {edge["id"] for edge in before_relevance["edges"]}
    before_relevance["edge_exposures"] = [
        exposure
        for exposure in before_relevance["edge_exposures"]
        if exposure["edge_id"] in retained_edge_ids
    ]
    before = compile_cut(before_relevance, "august-reconstruction")
    after = compile_cut(field, "august-reconstruction")
    causal_relevance = _lab(
        "CAUSAL-RELEVANCE-001",
        {
            "causal_ledger_stable": before["audit"]["causal_ledger_digest"]
            == after["audit"]["causal_ledger_digest"],
            "relevance_ledger_grows": before["audit"]["relevance_ledger_digest"]
            != after["audit"]["relevance_ledger_digest"],
            "causal_cone_stable": before["observer_view"]["cones"]["causal"]
            == after["observer_view"]["cones"]["causal"],
            "relevance_cone_grows": before["observer_view"]["cones"]["relevance"][
                "descendant_ids"
            ]
            == []
            and after["observer_view"]["cones"]["relevance"]["descendant_ids"]
            == ["artifact"],
            "relevance_edge_visible": any(
                edge["id"] == "relevance-breadcrumb-artifact"
                for edge in after["observer_view"]["edges"]["relevance"]
            ),
        },
        {
            "causal_digest": after["audit"]["causal_ledger_digest"],
            "relevance_before": before["audit"]["relevance_ledger_digest"],
            "relevance_after": after["audit"]["relevance_ledger_digest"],
        },
    )

    decoded = {
        decoder["id"]: decode_fret_glyph(glyph_spec["carrier"], decoder)
        for decoder in glyph_spec["decoders"]
    }
    standard = decoded["standard-a440"]
    alternate = decoded["cgcegd-a444"]
    glyph_receiver = _lab(
        "GLYPH-RECEIVER-001",
        {
            "carrier_stable": standard["carrier"]["digest"]
            == alternate["carrier"]["digest"],
            "decoder_changes": standard["decoder"]["digest"]
            != alternate["decoder"]["digest"],
            "projection_changes": standard["projection"]["digest"]
            != alternate["projection"]["digest"],
            "standard_expected": standard["projection"]["pitch_names"]
            == glyph_spec["expected_pitch_names"]["standard-a440"],
            "alternate_expected": alternate["projection"]["pitch_names"]
            == glyph_spec["expected_pitch_names"]["cgcegd-a444"],
        },
        {
            "carrier_digest": standard["carrier"]["digest"],
            "standard_projection": standard["projection"]["pitch_names"],
            "alternate_projection": alternate["projection"]["pitch_names"],
        },
    )

    riqor = compile_cut(field, "june-09-riqor")
    riqor_ids = {item["id"] for item in riqor["observer_view"]["occurrences"]}
    riqor_withheld = {
        item["occurrence_id"]: item for item in riqor["audit"]["withheld"]
    }
    two_narrator = _lab(
        "TWO-NARRATOR-001",
        {
            "same_field": june["field_id"] == riqor["field_id"],
            "lumi_has_artifact": "artifact" in june_ids,
            "riqor_lacks_artifact": "artifact" not in riqor_ids,
            "lumi_role_is_memory": _by_id(
                june["observer_view"]["occurrences"], "artifact"
            )["perceived_role"]
            == "past",
            "riqor_engine_relation_is_future": riqor_withheld["artifact"][
                "chronological_relation"
            ]
            == "future"
            and riqor_withheld["artifact"]["perceived_role"] == "unknown",
            "views_diverge": june["projection_digest"] != riqor["projection_digest"],
        },
        {
            "lumi_digest": june["projection_digest"],
            "riqor_digest": riqor["projection_digest"],
        },
    )

    august = compile_cut(field, "august-lumi")
    causal_edges = august["observer_view"]["edges"]["causal"]
    original = _by_id(causal_edges, "route-original")
    reconstituted = _by_id(causal_edges, "route-reconstituted")
    rupture = _lab(
        "RUPTURE-REACHABILITY-001",
        {
            "old_route_refused": original["current_assessment"]["status"] == "refused",
            "old_history_preserved": len(original["formation_history"]) == 2,
            "new_route_admitted": reconstituted["current_assessment"]["status"] == "admitted",
            "new_identity": original["id"] != reconstituted["id"],
            "causal_cone_uses_new_path": august["observer_view"]["cones"]["causal"][
                "descendant_ids"
            ]
            == ["present-note"],
        },
        {
            "old_route": original["id"],
            "new_route": reconstituted["id"],
            "projection_digest": august["projection_digest"],
        },
    )

    labs = [temporal, causal_relevance, glyph_receiver, two_narrator, rupture]
    receipt: dict[str, Any] = {
        "schema": "3rdi.lab-receipt/v0",
        "status": "pass" if all(lab["status"] == "pass" for lab in labs) else "fail",
        "labs": labs,
        "non_authority": "A passing lab receipt proves only the named phase-0 controls.",
    }
    receipt["receipt_digest"] = canonical_digest(receipt)
    return receipt


def main(argv: Sequence[str] | None = None) -> int:
    """Run the lab CLI."""

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="emit compact JSON")
    args = parser.parse_args(argv)
    try:
        receipt = run_labs()
    except (OSError, json.JSONDecodeError, FieldError, KeyError, StopIteration) as error:
        print(f"3rdi labs: {error}", file=sys.stderr)
        return 2
    json.dump(
        receipt,
        sys.stdout,
        ensure_ascii=False,
        indent=None if args.check else 2,
        sort_keys=True,
    )
    sys.stdout.write("\n")
    return 0 if receipt["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())

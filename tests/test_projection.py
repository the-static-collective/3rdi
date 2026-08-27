from __future__ import annotations

import copy
import sys
import unittest
from pathlib import Path


SCRIPT_ROOT = Path(__file__).resolve().parents[1] / "skills" / "3rdi" / "scripts"
sys.path.insert(0, str(SCRIPT_ROOT))

from three_rdi import FieldError, canonical_digest, compile_cut  # noqa: E402


def field_fixture() -> dict:
    return {
        "schema": "3rdi.field/v0",
        "field_id": "temporal-coordinate-001",
        "source_refs": ["owner-pastethoughts", "daily-slice-pr-25"],
        "occurrences": [
            {
                "id": "breadcrumb",
                "occurred_at": "2026-06-09T09:00:00Z",
                "locus_id": "archive-room",
                "source_refs": ["daily-slice-pr-25"],
            },
            {
                "id": "artifact",
                "occurred_at": "2026-06-10T10:00:00Z",
                "locus_id": "archive-room",
                "source_refs": ["owner-pastethoughts"],
            },
            {
                "id": "present-note",
                "occurred_at": "2026-06-15T12:00:00Z",
                "locus_id": "archive-room",
                "source_refs": ["owner-pastethoughts"],
            },
            {
                "id": "later-discovery",
                "occurred_at": "2026-08-01T08:00:00Z",
                "locus_id": "lab",
                "source_refs": ["daily-slice-pr-25"],
            },
            {
                "id": "sealed-future",
                "occurred_at": "2026-09-01T08:00:00Z",
                "locus_id": "lab",
                "source_refs": ["owner-pastethoughts"],
            },
        ],
        "exposures": [
            {
                "id": "exposure-breadcrumb-lumi",
                "occurrence_id": "breadcrumb",
                "observer": "lumi",
                "layer": "public",
                "available_from": "2026-06-09T10:00:00Z",
                "evidence_refs": ["daily-slice-pr-25"],
            },
            {
                "id": "exposure-breadcrumb-riqor",
                "occurrence_id": "breadcrumb",
                "observer": "riqor",
                "layer": "public",
                "available_from": "2026-06-09T10:00:00Z",
                "evidence_refs": ["daily-slice-pr-25"],
            },
            {
                "id": "exposure-artifact-lumi",
                "occurrence_id": "artifact",
                "observer": "lumi",
                "layer": "private",
                "available_from": "2026-06-10T13:00:00Z",
                "evidence_refs": ["owner-pastethoughts"],
            },
            {
                "id": "exposure-artifact-riqor",
                "occurrence_id": "artifact",
                "observer": "riqor",
                "layer": "public",
                "available_from": "2026-08-02T09:00:00Z",
                "evidence_refs": ["daily-slice-pr-25"],
            },
            {
                "id": "exposure-note-lumi",
                "occurrence_id": "present-note",
                "observer": "lumi",
                "layer": "public",
                "available_from": "2026-06-15T12:00:00Z",
                "evidence_refs": ["owner-pastethoughts"],
            },
            {
                "id": "exposure-discovery-lumi",
                "occurrence_id": "later-discovery",
                "observer": "lumi",
                "layer": "public",
                "available_from": "2026-08-01T09:00:00Z",
                "evidence_refs": ["daily-slice-pr-25"],
            },
            {
                "id": "exposure-sealed-lumi",
                "occurrence_id": "sealed-future",
                "observer": "lumi",
                "layer": "public",
                "available_from": "2026-09-02T09:00:00Z",
                "evidence_refs": ["owner-pastethoughts"],
            },
        ],
        "expectations": [
            {
                "id": "expected-rain",
                "observer": "lumi",
                "layer": "private",
                "formed_at": "2026-06-10T09:00:00Z",
                "available_from": "2026-06-10T09:00:00Z",
                "target_at": "2026-06-11T09:00:00Z",
                "statement": "Rain may arrive tomorrow.",
                "evidence_refs": ["owner-pastethoughts"],
            }
        ],
        "edges": [
            {
                "id": "causal-breadcrumb-artifact",
                "from": "breadcrumb",
                "to": "artifact",
                "edge_class": "causal",
                "relation": "informed",
                "first_perceived_at": "2026-06-14T10:00:00Z",
                "discovery_trace": ["daily-slice-pr-25"],
                "assessments": [
                    {
                        "assessed_at": "2026-06-14T11:00:00Z",
                        "status": "admitted",
                        "confidence": 0.8,
                        "evidence_refs": ["daily-slice-pr-25"],
                        "reason": "Contemporaneous trace.",
                    },
                    {
                        "assessed_at": "2026-08-20T11:00:00Z",
                        "status": "weakened",
                        "confidence": 0.55,
                        "evidence_refs": ["owner-pastethoughts"],
                        "reason": "Later ambiguity did not erase the earlier assessment.",
                    },
                ],
            }
        ],
        "edge_exposures": [
            {
                "id": "edge-exposure-causal-lumi",
                "edge_id": "causal-breadcrumb-artifact",
                "observer": "lumi",
                "layer": "private",
                "available_from": "2026-06-14T10:00:00Z",
                "evidence_refs": ["daily-slice-pr-25"],
            }
        ],
        "location_decoders": [
            {
                "id": "archive-display-v1",
                "source_crs": "EPSG:4326",
                "target_crs": "LOCAL:ARCHIVE-DISPLAY",
                "operation": "declared-operation:archive-display-v1",
                "area_of_use": "archive-room",
                "accuracy_m": 1.0,
                "source_refs": ["owner-pastethoughts"],
            }
        ],
        "location_claims": [
            {
                "id": "artifact-location-claim",
                "occurrence_id": "artifact",
                "locus_id": "archive-room",
                "decoder_id": "archive-display-v1",
                "observer": "lumi",
                "layer": "private",
                "available_from": "2026-06-10T13:00:00Z",
                "coordinates": [-73.0, 40.0],
                "coordinate_crs": "EPSG:4326",
                "uncertainty_m": 2.0,
                "evidence_refs": ["owner-pastethoughts"],
            }
        ],
        "gates": [
            {
                "id": "artifact-visible",
                "op": "all",
                "conditions": [
                    {"kind": "occurrence_visible", "occurrence_id": "artifact"}
                ],
                "source_refs": ["owner-pastethoughts"],
            },
            {
                "id": "causal-admitted",
                "op": "all",
                "conditions": [
                    {
                        "kind": "edge_status",
                        "edge_id": "causal-breadcrumb-artifact",
                        "status": "admitted",
                    }
                ],
                "source_refs": ["daily-slice-pr-25"],
            },
            {
                "id": "artifact-not-visible",
                "op": "not",
                "conditions": [
                    {"kind": "occurrence_visible", "occurrence_id": "artifact"}
                ],
                "source_refs": ["owner-pastethoughts"],
            },
        ],
        "cuts": [
            {
                "id": "june-10",
                "observer": "lumi",
                "mode": "historical",
                "focus_at": "2026-06-10T12:00:00Z",
                "known_at": "2026-06-10T11:00:00Z",
                "audience_layers": ["public", "private"],
                "location_scope": ["archive-room"],
                "focus_occurrence_ids": ["breadcrumb"],
                "gate_ids": ["artifact-visible", "causal-admitted", "artifact-not-visible"],
            },
            {
                "id": "june-15",
                "observer": "lumi",
                "mode": "historical",
                "focus_at": "2026-06-15T12:00:00Z",
                "known_at": "2026-06-15T12:00:00Z",
                "audience_layers": ["public", "private"],
                "location_scope": ["archive-room"],
                "focus_occurrence_ids": ["breadcrumb"],
                "gate_ids": ["artifact-visible", "causal-admitted", "artifact-not-visible"],
            },
            {
                "id": "august-reconstruction",
                "observer": "lumi",
                "mode": "reconstruction",
                "focus_at": "2026-06-10T12:00:00Z",
                "known_at": "2026-08-27T12:00:00Z",
                "audience_layers": ["public", "private"],
                "location_scope": ["archive-room"],
                "focus_occurrence_ids": ["breadcrumb"],
                "gate_ids": ["artifact-visible", "causal-admitted", "artifact-not-visible"],
            },
            {
                "id": "riqor-august",
                "observer": "riqor",
                "mode": "historical",
                "focus_at": "2026-08-27T12:00:00Z",
                "known_at": "2026-08-27T12:00:00Z",
                "audience_layers": ["public"],
                "location_scope": ["archive-room"],
                "focus_occurrence_ids": ["breadcrumb"],
                "gate_ids": ["artifact-visible"],
            },
        ],
    }


def by_id(items: list[dict], item_id: str) -> dict:
    return next(item for item in items if item["id"] == item_id)


class ProjectionTests(unittest.TestCase):
    def test_occurrences_remain_immutable_while_roles_change(self) -> None:
        field = field_fixture()
        before = canonical_digest(field["occurrences"])

        early = compile_cut(field, "june-10")
        later = compile_cut(field, "june-15")

        self.assertEqual(before, canonical_digest(field["occurrences"]))
        early_ids = {item["id"] for item in early["observer_view"]["occurrences"]}
        self.assertNotIn("artifact", early_ids)
        self.assertEqual(
            by_id(later["observer_view"]["occurrences"], "artifact")["perceived_role"],
            "past",
        )
        self.assertTrue(
            by_id(later["observer_view"]["occurrences"], "artifact")["available_at_cut"]
        )
        self.assertEqual(
            by_id(later["observer_view"]["occurrences"], "present-note")["perceived_role"],
            "present",
        )

    def test_actual_future_is_withheld_but_expectation_is_visible(self) -> None:
        receipt = compile_cut(field_fixture(), "june-10")

        visible_ids = {item["id"] for item in receipt["observer_view"]["occurrences"]}
        self.assertNotIn("later-discovery", visible_ids)
        self.assertNotIn("sealed-future", visible_ids)
        expectation = by_id(receipt["observer_view"]["expectations"], "expected-rain")
        self.assertEqual(expectation["perceived_role"], "anticipated-future")

    def test_historical_mode_rejects_hindsight_horizon(self) -> None:
        field = field_fixture()
        bad_cut = copy.deepcopy(field["cuts"][0])
        bad_cut["id"] = "bad-hindsight"
        bad_cut["known_at"] = "2026-06-11T12:00:00Z"
        field["cuts"].append(bad_cut)

        with self.assertRaisesRegex(FieldError, "known_at.*focus_at"):
            compile_cut(field, "bad-hindsight")

    def test_reconstruction_labels_post_focus_availability(self) -> None:
        receipt = compile_cut(field_fixture(), "august-reconstruction")
        artifact = by_id(receipt["observer_view"]["occurrences"], "artifact")

        self.assertTrue(artifact["hindsight_bearing"])
        self.assertEqual(artifact["perceived_role"], "past")
        hidden = {item["occurrence_id"]: item for item in receipt["audit"]["withheld"]}
        self.assertEqual(hidden["later-discovery"]["reason"], "future-occurrence")
        self.assertFalse(hidden["later-discovery"]["available_at_cut"])
        self.assertEqual(hidden["later-discovery"]["perceived_role"], "unknown")

    def test_two_observers_receive_different_views_of_one_occurrence(self) -> None:
        field = field_fixture()
        lumi = compile_cut(field, "june-15")
        riqor = compile_cut(field, "riqor-august")

        lumi_artifact = by_id(lumi["observer_view"]["occurrences"], "artifact")
        riqor_artifact = by_id(riqor["observer_view"]["occurrences"], "artifact")
        self.assertEqual(lumi_artifact["available_via"]["layer"], "private")
        self.assertEqual(riqor_artifact["available_via"]["layer"], "public")
        self.assertNotEqual(lumi["projection_digest"], riqor["projection_digest"])

    def test_edge_availability_is_observer_local(self) -> None:
        receipt = compile_cut(field_fixture(), "riqor-august")

        visible_ids = {item["id"] for item in receipt["observer_view"]["occurrences"]}
        edge_ids = {item["id"] for item in receipt["observer_view"]["edges"]["causal"]}
        withheld = {
            item["edge_id"]: item["reason"]
            for item in receipt["audit"]["withheld_edges"]
        }
        self.assertIn("artifact", visible_ids)
        self.assertNotIn("causal-breadcrumb-artifact", edge_ids)
        self.assertEqual(
            withheld["causal-breadcrumb-artifact"],
            "not-available-to-observer",
        )

    def test_edge_assessments_replay_without_rewrite(self) -> None:
        field = field_fixture()
        june = compile_cut(field, "june-15")
        august = compile_cut(field, "august-reconstruction")

        june_edge = by_id(june["observer_view"]["edges"]["causal"], "causal-breadcrumb-artifact")
        august_edge = by_id(august["observer_view"]["edges"]["causal"], "causal-breadcrumb-artifact")
        self.assertEqual(june_edge["current_assessment"]["status"], "admitted")
        self.assertEqual(august_edge["current_assessment"]["status"], "weakened")
        self.assertEqual(len(august_edge["formation_history"]), 2)

    def test_relevance_growth_does_not_mutate_causal_digest(self) -> None:
        field = field_fixture()
        before = compile_cut(field, "august-reconstruction")
        field["edges"].append(
            {
                "id": "relevance-breadcrumb-artifact",
                "from": "breadcrumb",
                "to": "artifact",
                "edge_class": "relevance",
                "relation": "helps-interpret",
                "first_perceived_at": "2026-08-21T10:00:00Z",
                "discovery_trace": ["owner-pastethoughts"],
                "assessments": [
                    {
                        "assessed_at": "2026-08-21T11:00:00Z",
                        "status": "admitted",
                        "confidence": 0.9,
                        "evidence_refs": ["owner-pastethoughts"],
                        "reason": "Later interpretive use.",
                    }
                ],
            }
        )
        field["edge_exposures"].append(
            {
                "id": "edge-exposure-relevance-lumi",
                "edge_id": "relevance-breadcrumb-artifact",
                "observer": "lumi",
                "layer": "private",
                "available_from": "2026-08-21T10:00:00Z",
                "evidence_refs": ["owner-pastethoughts"],
            }
        )
        after = compile_cut(field, "august-reconstruction")

        self.assertEqual(
            before["audit"]["causal_ledger_digest"],
            after["audit"]["causal_ledger_digest"],
        )
        self.assertNotEqual(
            before["audit"]["relevance_ledger_digest"],
            after["audit"]["relevance_ledger_digest"],
        )
        self.assertEqual(
            before["observer_view"]["cones"]["causal"],
            after["observer_view"]["cones"]["causal"],
        )
        self.assertEqual(
            before["observer_view"]["cones"]["relevance"]["descendant_ids"],
            [],
        )
        self.assertEqual(
            after["observer_view"]["cones"]["relevance"]["descendant_ids"],
            ["artifact"],
        )
        self.assertEqual(
            by_id(
                after["observer_view"]["edges"]["relevance"],
                "relevance-breadcrumb-artifact",
            )["relation"],
            "helps-interpret",
        )

    def test_gates_are_pure_and_can_be_unresolved(self) -> None:
        early = compile_cut(field_fixture(), "june-10")
        later = compile_cut(field_fixture(), "june-15")

        self.assertEqual(by_id(early["observer_view"]["gates"], "artifact-visible")["state"], "fail")
        self.assertEqual(by_id(early["observer_view"]["gates"], "causal-admitted")["state"], "unresolved")
        self.assertEqual(by_id(early["observer_view"]["gates"], "artifact-not-visible")["state"], "pass")
        self.assertEqual(by_id(later["observer_view"]["gates"], "artifact-visible")["state"], "pass")
        self.assertEqual(by_id(later["observer_view"]["gates"], "causal-admitted")["state"], "pass")
        self.assertEqual(by_id(later["observer_view"]["gates"], "artifact-not-visible")["state"], "fail")
        self.assertNotIn("side_effects", later)

    def test_location_projection_preserves_locus_and_decoder_receipt(self) -> None:
        receipt = compile_cut(field_fixture(), "june-15")
        claim = by_id(receipt["observer_view"]["location_claims"], "artifact-location-claim")

        self.assertEqual(claim["locus_id"], "archive-room")
        self.assertEqual(claim["decoder"]["source_crs"], "EPSG:4326")
        self.assertEqual(claim["decoder"]["target_crs"], "LOCAL:ARCHIVE-DISPLAY")
        self.assertEqual(claim["coordinate_crs"], "EPSG:4326")
        self.assertEqual(claim["uncertainty_m"], 2.0)
        self.assertFalse(claim["decoder"]["performed_by_3rdi"])

    def test_projection_is_deterministic_and_input_order_invariant(self) -> None:
        field = field_fixture()
        first = compile_cut(field, "june-15")
        reordered = copy.deepcopy(field)
        for key in (
            "occurrences",
            "exposures",
            "edges",
            "edge_exposures",
            "gates",
            "cuts",
        ):
            reordered[key].reverse()
        second = compile_cut(reordered, "june-15")

        self.assertEqual(first["projection_digest"], second["projection_digest"])
        self.assertEqual(first["audit"]["input_digest"], second["audit"]["input_digest"])

    def test_shuffling_chronology_while_preserving_labels_breaks(self) -> None:
        field = field_fixture()
        shuffled = copy.deepcopy(field)
        breadcrumb = by_id(shuffled["occurrences"], "breadcrumb")
        artifact = by_id(shuffled["occurrences"], "artifact")
        breadcrumb["occurred_at"], artifact["occurred_at"] = (
            artifact["occurred_at"],
            breadcrumb["occurred_at"],
        )
        with self.assertRaisesRegex(FieldError, "cannot precede the occurrence"):
            compile_cut(shuffled, "june-15")

    def test_invalid_timestamp_and_reference_fail_at_boundary(self) -> None:
        bad_time = field_fixture()
        bad_time["occurrences"][0]["occurred_at"] = "2026-06-09 09:00"
        with self.assertRaisesRegex(FieldError, "RFC 3339"):
            compile_cut(bad_time, "june-15")

        bad_reference = field_fixture()
        bad_reference["exposures"][0]["occurrence_id"] = "missing"
        with self.assertRaisesRegex(FieldError, "unknown occurrence"):
            compile_cut(bad_reference, "june-15")

        non_finite = field_fixture()
        non_finite["location_claims"][0]["coordinates"][0] = float("nan")
        with self.assertRaisesRegex(FieldError, "finite"):
            compile_cut(non_finite, "june-15")

        non_json_extension = field_fixture()
        non_json_extension["extension"] = float("inf")
        with self.assertRaisesRegex(FieldError, "JSON-compatible"):
            compile_cut(non_json_extension, "june-15")


if __name__ == "__main__":
    unittest.main()

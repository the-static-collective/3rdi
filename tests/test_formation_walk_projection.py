from __future__ import annotations

import copy
import sys
import unittest
from pathlib import Path


SCRIPT_ROOT = Path(__file__).resolve().parents[1] / "skills" / "3rdi" / "scripts"
sys.path.insert(0, str(SCRIPT_ROOT))

from three_rdi import FieldError, compile_cut, normalize_field  # noqa: E402


def base_field() -> dict:
    occurrences = [
        {
            "id": f"e{index}",
            "occurred_at": f"2026-08-31T10:0{index}:00Z",
            "locus_id": "lab",
            "source_refs": [f"source:e{index}"],
        }
        for index in range(4)
    ]
    exposures = [
        {
            "id": f"exposure-e{index}",
            "occurrence_id": f"e{index}",
            "observer": "observer-a",
            "layer": "private",
            "available_from": "2026-08-31T10:04:00Z",
            "evidence_refs": [f"source:e{index}"],
        }
        for index in range(4)
    ]
    return {
        "schema": "3rdi.field/v0",
        "field_id": "walk-receipt-projection-001",
        "occurrences": occurrences,
        "exposures": exposures,
        "formation_walks": [
            {
                "id": "walk-a",
                "endpoint_occurrence_id": "e3",
                "observer": "observer-a",
                "layer": "private",
                "formed_at": "2026-08-31T10:05:00Z",
                "available_from": "2026-08-31T10:10:00Z",
                "step_refs": ["e0", "e1", "e3"],
                "source_refs": ["receipt:walk-a"],
            },
            {
                "id": "walk-b",
                "endpoint_occurrence_id": "e3",
                "observer": "observer-a",
                "layer": "private",
                "formed_at": "2026-08-31T10:05:00Z",
                "available_from": "2026-08-31T10:20:00Z",
                "step_refs": ["e0", "e2", "e3"],
                "source_refs": ["receipt:walk-b"],
            },
        ],
        "cuts": [
            {
                "id": "a0",
                "observer": "observer-a",
                "mode": "historical",
                "focus_at": "2026-08-31T10:09:00Z",
                "known_at": "2026-08-31T10:09:00Z",
                "audience_layers": ["private"],
                "location_scope": ["lab"],
                "focus_occurrence_ids": ["e3"],
                "gate_ids": [],
            },
            {
                "id": "a1",
                "observer": "observer-a",
                "mode": "historical",
                "focus_at": "2026-08-31T10:15:00Z",
                "known_at": "2026-08-31T10:15:00Z",
                "audience_layers": ["private"],
                "location_scope": ["lab"],
                "focus_occurrence_ids": ["e3"],
                "gate_ids": [],
            },
            {
                "id": "a2",
                "observer": "observer-a",
                "mode": "historical",
                "focus_at": "2026-08-31T10:25:00Z",
                "known_at": "2026-08-31T10:25:00Z",
                "audience_layers": ["private"],
                "location_scope": ["lab"],
                "focus_occurrence_ids": ["e3"],
                "gate_ids": [],
            },
        ],
    }


class FormationWalkProjectionTests(unittest.TestCase):
    def test_walk_family_is_normalized_and_duplicate_ids_refuse(self) -> None:
        normalized = normalize_field(base_field())
        self.assertEqual([walk["id"] for walk in normalized["formation_walks"]], ["walk-a", "walk-b"])
        self.assertEqual(normalized["formation_walks"][0]["step_refs"], ["e0", "e1", "e3"])

        duplicate = base_field()
        duplicate["formation_walks"].append(copy.deepcopy(duplicate["formation_walks"][0]))
        with self.assertRaisesRegex(FieldError, "duplicate id"):
            normalize_field(duplicate)

    def test_walk_validation_refuses_unknown_endpoint_and_bad_reference_lists(self) -> None:
        unknown = base_field()
        unknown["formation_walks"][0]["endpoint_occurrence_id"] = "missing"
        with self.assertRaisesRegex(FieldError, "unknown endpoint occurrence"):
            normalize_field(unknown)

        malformed = base_field()
        malformed["formation_walks"][0]["step_refs"] = "e0,e1,e3"
        with self.assertRaises(FieldError):
            normalize_field(malformed)

    def test_same_endpoint_exposes_zero_one_then_two_walks(self) -> None:
        field = base_field()
        receipts = {cut: compile_cut(field, cut) for cut in ("a0", "a1", "a2")}

        occurrence_ids = [
            [item["id"] for item in receipts[cut]["observer_view"]["occurrences"]]
            for cut in ("a0", "a1", "a2")
        ]
        self.assertEqual(occurrence_ids[0], occurrence_ids[1])
        self.assertEqual(occurrence_ids[1], occurrence_ids[2])
        self.assertEqual(receipts["a0"]["observer_view"]["formation_walks"], [])
        self.assertEqual(
            [item["id"] for item in receipts["a1"]["observer_view"]["formation_walks"]],
            ["walk-a"],
        )
        self.assertEqual(
            [item["id"] for item in receipts["a2"]["observer_view"]["formation_walks"]],
            ["walk-a", "walk-b"],
        )

    def test_hidden_walk_mutation_is_projection_noninterfering(self) -> None:
        field = base_field()
        before = compile_cut(field, "a1")
        mutated = copy.deepcopy(field)
        walk_b = next(item for item in mutated["formation_walks"] if item["id"] == "walk-b")
        walk_b["step_refs"] = ["completely", "different", "hidden", "road"]
        walk_b["source_refs"] = ["receipt:different"]
        mutated["formation_walks"].reverse()
        after = compile_cut(mutated, "a1")

        self.assertEqual(before["projection_digest"], after["projection_digest"])
        self.assertEqual(
            before["observer_view"]["formation_walks"],
            after["observer_view"]["formation_walks"],
        )
        self.assertEqual(
            before["observer_view"]["occurrences"], after["observer_view"]["occurrences"]
        )

    def test_visible_walk_mutation_changes_projection_digest(self) -> None:
        field = base_field()
        before = compile_cut(field, "a2")
        mutated = copy.deepcopy(field)
        walk_b = next(item for item in mutated["formation_walks"] if item["id"] == "walk-b")
        walk_b["step_refs"] = ["e0", "alternate", "e3"]
        after = compile_cut(mutated, "a2")
        self.assertNotEqual(before["projection_digest"], after["projection_digest"])

    def test_walk_does_not_grant_endpoint_visibility_and_withheld_does_not_leak_steps(self) -> None:
        field = base_field()
        field["exposures"] = [item for item in field["exposures"] if item["occurrence_id"] != "e3"]
        receipt = compile_cut(field, "a2")

        self.assertNotIn("e3", {item["id"] for item in receipt["observer_view"]["occurrences"]})
        self.assertEqual(receipt["observer_view"]["formation_walks"], [])
        withheld = receipt["audit"]["withheld_formation_walks"]
        self.assertTrue(all(item["reason"] == "endpoint-withheld" for item in withheld))
        self.assertTrue(all("step_refs" not in item and "source_refs" not in item for item in withheld))


if __name__ == "__main__":
    unittest.main()

from __future__ import annotations

import copy
import json
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT_ROOT = ROOT / "skills" / "3rdi" / "scripts"
sys.path.insert(0, str(SCRIPT_ROOT))

from three_rdi import FieldError, compile_cut, normalize_field  # noqa: E402


class FormationWalkTemporalValidityTests(unittest.TestCase):
    def test_walk_cannot_be_available_before_it_is_formed(self) -> None:
        field = json.loads(
            (ROOT / "specimens" / "walk-receipt-projection-001.json").read_text()
        )
        hostile = copy.deepcopy(field)
        hostile["formation_walks"][0]["formed_at"] = "2026-08-31T10:10:00Z"
        hostile["formation_walks"][0]["available_from"] = "2026-08-31T10:09:00Z"

        with self.assertRaisesRegex(
            FieldError, "available_from cannot precede formed_at"
        ):
            normalize_field(hostile)

    def test_walk_cannot_form_before_its_endpoint_occurs(self) -> None:
        field = json.loads(
            (ROOT / "specimens" / "walk-receipt-projection-001.json").read_text()
        )
        hostile = copy.deepcopy(field)
        hostile["formation_walks"][0]["formed_at"] = "2026-08-31T10:02:00Z"
        hostile["formation_walks"][0]["available_from"] = "2026-08-31T10:10:00Z"

        with self.assertRaisesRegex(
            FieldError, "formed_at cannot precede endpoint occurrence"
        ):
            normalize_field(hostile)

    def test_walk_may_form_exactly_when_endpoint_occurs(self) -> None:
        field = json.loads(
            (ROOT / "specimens" / "walk-receipt-projection-001.json").read_text()
        )
        boundary = copy.deepcopy(field)
        boundary["formation_walks"][0]["formed_at"] = "2026-08-31T10:03:00Z"
        boundary["formation_walks"][0]["available_from"] = "2026-08-31T10:03:00Z"

        normalized = normalize_field(boundary)
        walk = next(
            item for item in normalized["formation_walks"] if item["id"] == "walk-a"
        )

        self.assertEqual(walk["formed_at"], "2026-08-31T10:03:00Z")
        self.assertEqual(walk["available_from"], "2026-08-31T10:03:00Z")

    def test_later_walk_cannot_import_future_endpoint_into_reconstructed_focus(self) -> None:
        field = json.loads(
            (ROOT / "specimens" / "walk-receipt-projection-001.json").read_text()
        )
        hostile = copy.deepcopy(field)
        cut = hostile["cuts"][0]
        # Reconstruction is the lawful mode for a knowledge horizon later than
        # the frozen focus. Historical mode intentionally requires known_at <= focus_at.
        cut["mode"] = "reconstruction"
        cut["known_at"] = "2026-08-31T10:40:00Z"

        # Keep the canonical focus untouched and introduce one isolated
        # post-focus endpoint. Later knowledge may know the walk, but cannot
        # turn a post-focus occurrence into part of the reconstructed focus.
        hostile["occurrences"].append(
            {
                "id": "e-future",
                "occurred_at": "2026-08-31T10:30:00Z",
                "locus_id": "lab",
                "source_refs": ["source:e-future"],
            }
        )
        hostile["exposures"].append(
            {
                "id": "exposure-e-future",
                "occurrence_id": "e-future",
                "observer": "observer-a",
                "layer": "private",
                "available_from": "2026-08-31T10:31:00Z",
                "evidence_refs": ["source:e-future"],
            }
        )
        walk = hostile["formation_walks"][0]
        walk["endpoint_occurrence_id"] = "e-future"
        walk["formed_at"] = "2026-08-31T10:31:00Z"
        walk["available_from"] = "2026-08-31T10:31:00Z"

        receipt = compile_cut(hostile, cut["id"])

        self.assertNotIn(
            "e-future",
            {item["id"] for item in receipt["observer_view"]["occurrences"]},
        )
        self.assertNotIn(
            walk["id"],
            {item["id"] for item in receipt["observer_view"]["formation_walks"]},
        )
        withheld = next(
            item
            for item in receipt["audit"]["withheld_formation_walks"]
            if item["id"] == walk["id"]
        )
        self.assertEqual(withheld["reason"], "endpoint-withheld")


if __name__ == "__main__":
    unittest.main()

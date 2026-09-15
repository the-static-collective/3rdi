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

    def test_later_walk_cannot_import_future_endpoint_into_historical_focus(self) -> None:
        field = json.loads(
            (ROOT / "specimens" / "walk-receipt-projection-001.json").read_text()
        )
        hostile = copy.deepcopy(field)
        cut = hostile["cuts"][0]
        cut["focus_at"] = "2026-08-31T10:02:00Z"
        cut["known_at"] = "2026-08-31T10:20:00Z"
        cut["focus_occurrence_ids"] = ["e2"]

        walk = hostile["formation_walks"][0]
        walk["formed_at"] = "2026-08-31T10:04:00Z"
        walk["available_from"] = "2026-08-31T10:04:00Z"

        receipt = compile_cut(hostile, cut["id"])

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

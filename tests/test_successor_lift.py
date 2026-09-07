from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT_ROOT = ROOT / "skills" / "3rdi" / "scripts"
sys.path.insert(0, str(SCRIPT_ROOT))

from three_rdi import compile_cut  # noqa: E402


SPECIMEN = ROOT / "specimens" / "successor-lift-001.json"


def load_field() -> dict:
    return json.loads(SPECIMEN.read_text(encoding="utf-8"))


def visible_occurrence_ids(receipt: dict) -> list[str]:
    return [item["id"] for item in receipt["observer_view"]["occurrences"]]


class SuccessorLiftTests(unittest.TestCase):
    def test_world_successor_can_leave_observer_projection_unchanged(self) -> None:
        field = load_field()
        before = compile_cut(field, "before-successor")
        after = compile_cut(field, "after-successor-hidden")

        self.assertEqual([item["id"] for item in field["occurrences"]], ["e0", "e1"])
        self.assertEqual(visible_occurrence_ids(before), ["e0"])
        self.assertEqual(visible_occurrence_ids(after), ["e0"])
        self.assertLess(
            field["occurrences"][1]["occurred_at"],
            next(cut for cut in field["cuts"] if cut["id"] == "after-successor-hidden")["known_at"],
        )

    def test_later_availability_exposes_successor_without_rewriting_occurrence_order(self) -> None:
        field = load_field()
        later = compile_cut(field, "after-successor-available")

        self.assertEqual(visible_occurrence_ids(later), ["e0", "e1"])
        self.assertEqual([item["id"] for item in field["occurrences"]], ["e0", "e1"])
        self.assertEqual(field["occurrences"][1]["occurred_at"], "2026-09-07T15:10:00Z")

    def test_later_knowledge_does_not_backdate_into_earlier_cut(self) -> None:
        field = load_field()
        historical_before = compile_cut(field, "after-successor-hidden")
        _ = compile_cut(field, "after-successor-available")
        replayed_before = compile_cut(field, "after-successor-hidden")

        self.assertEqual(replayed_before, historical_before)
        self.assertEqual(visible_occurrence_ids(replayed_before), ["e0"])


if __name__ == "__main__":
    unittest.main()

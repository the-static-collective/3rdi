from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT_ROOT = ROOT / "skills" / "3rdi" / "scripts"
sys.path.insert(0, str(SCRIPT_ROOT))

from three_rdi import compile_cut  # noqa: E402


SPECIMEN = ROOT / "specimens" / "residual-cut-001.json"


def load_field() -> dict:
    return json.loads(SPECIMEN.read_text(encoding="utf-8"))


def visible_occurrence_ids(receipt: dict) -> list[str]:
    return [item["id"] for item in receipt["observer_view"]["occurrences"]]


def generator_value(occurrence: dict) -> int:
    refs = [
        ref
        for ref in occurrence.get("source_refs", [])
        if ref.startswith("generator:")
    ]
    if len(refs) != 1:
        raise AssertionError(f"expected one generator receipt, got {refs!r}")
    return int(refs[0].split(":", 1)[1])


def projection_residual(receipt: dict) -> int:
    return sum(generator_value(item) for item in receipt["observer_view"]["occurrences"])


class ResidualCutTests(unittest.TestCase):
    def test_later_disclosure_breaks_exact_under_projection(self) -> None:
        field = load_field()
        p0 = compile_cut(field, "p0-exact-under-projection")
        p1 = compile_cut(field, "p1-broken-after-disclosure")

        self.assertEqual(visible_occurrence_ids(p0), ["g-focus", "g-minus", "g-plus"])
        self.assertEqual(projection_residual(p0), 0)
        self.assertEqual(
            visible_occurrence_ids(p1),
            ["g-focus", "g-hidden-boundary", "g-hidden-plus", "g-minus", "g-plus"],
        )
        self.assertEqual(projection_residual(p1), 1)

        hidden = next(
            item
            for item in p1["observer_view"]["occurrences"]
            if item["id"] == "g-hidden-plus"
        )
        self.assertTrue(hidden["hindsight_bearing"])
        self.assertLess(hidden["occurred_at"], p0["cut"]["focus_at"])
        self.assertGreater(hidden["available_via"]["available_from"], p0["cut"]["known_at"])

    def test_known_at_boundary_availability_is_visible_and_hindsight_bearing(self) -> None:
        field = load_field()
        p0 = compile_cut(field, "p0-exact-under-projection")
        p1 = compile_cut(field, "p1-broken-after-disclosure")

        self.assertNotIn("g-hidden-boundary", visible_occurrence_ids(p0))
        boundary = next(
            item
            for item in p1["observer_view"]["occurrences"]
            if item["id"] == "g-hidden-boundary"
        )
        self.assertEqual(
            boundary["available_via"]["available_from"],
            p1["cut"]["known_at"],
        )
        self.assertTrue(boundary["available_at_cut"])
        self.assertTrue(boundary["hindsight_bearing"])
        self.assertEqual(boundary["chronological_relation"], "past")
        self.assertEqual(generator_value(boundary), 0)
        self.assertEqual(projection_residual(p1), 1)

    def test_focus_boundary_occurrence_is_present_not_hindsight(self) -> None:
        field = load_field()
        p0 = compile_cut(field, "p0-exact-under-projection")
        focus = next(
            item
            for item in p0["observer_view"]["occurrences"]
            if item["id"] == "g-focus"
        )

        self.assertEqual(focus["occurred_at"], p0["cut"]["focus_at"])
        self.assertEqual(focus["chronological_relation"], "present")
        self.assertEqual(focus["perceived_role"], "present")
        self.assertTrue(focus["available_at_cut"])
        self.assertEqual(
            focus["available_via"]["available_from"],
            p0["cut"]["known_at"],
        )
        self.assertFalse(focus["hindsight_bearing"])
        self.assertEqual(generator_value(focus), 0)
        self.assertEqual(projection_residual(p0), 0)

    def test_further_disclosure_can_restore_exactness_without_rewriting_prior_cuts(self) -> None:
        field = load_field()
        p0_before = compile_cut(field, "p0-exact-under-projection")
        p1_before = compile_cut(field, "p1-broken-after-disclosure")
        p2 = compile_cut(field, "p2-restored-after-further-disclosure")

        self.assertEqual(
            visible_occurrence_ids(p2),
            [
                "g-focus",
                "g-hidden-boundary",
                "g-hidden-minus",
                "g-hidden-plus",
                "g-minus",
                "g-plus",
            ],
        )
        self.assertEqual(projection_residual(p2), 0)
        self.assertEqual(compile_cut(field, "p0-exact-under-projection"), p0_before)
        self.assertEqual(compile_cut(field, "p1-broken-after-disclosure"), p1_before)
        self.assertEqual(projection_residual(p0_before), 0)
        self.assertEqual(projection_residual(p1_before), 1)

        hidden_minus = next(
            item
            for item in p2["observer_view"]["occurrences"]
            if item["id"] == "g-hidden-minus"
        )
        self.assertTrue(hidden_minus["hindsight_bearing"])
        self.assertLess(hidden_minus["occurred_at"], p0_before["cut"]["focus_at"])
        self.assertGreater(
            hidden_minus["available_via"]["available_from"],
            p1_before["cut"]["known_at"],
        )

    def test_later_knowledge_does_not_pull_post_focus_occurrence_backward(self) -> None:
        field = load_field()
        p2 = compile_cut(field, "p2-restored-after-further-disclosure")

        self.assertNotIn("g-post-focus", visible_occurrence_ids(p2))
        post_focus = next(
            item
            for item in p2["audit"]["withheld"]
            if item["occurrence_id"] == "g-post-focus"
        )
        self.assertEqual(post_focus["reason"], "future-occurrence")
        self.assertEqual(post_focus["chronological_relation"], "future")
        self.assertFalse(post_focus["available_at_cut"])
        self.assertEqual(projection_residual(p2), 0)

    def test_richer_later_cut_does_not_rewrite_earlier_receipt(self) -> None:
        field = load_field()
        p0_before = compile_cut(field, "p0-exact-under-projection")
        _ = compile_cut(field, "p1-broken-after-disclosure")
        p0_replayed = compile_cut(field, "p0-exact-under-projection")

        self.assertEqual(p0_replayed, p0_before)
        self.assertEqual(projection_residual(p0_replayed), 0)
        self.assertNotIn("g-hidden-plus", visible_occurrence_ids(p0_replayed))

    def test_disclosure_changes_projection_not_anchored_occurrences(self) -> None:
        field = load_field()
        anchored_before = json.loads(json.dumps(field["occurrences"]))

        _ = compile_cut(field, "p0-exact-under-projection")
        _ = compile_cut(field, "p1-broken-after-disclosure")
        _ = compile_cut(field, "p2-restored-after-further-disclosure")

        self.assertEqual(field["occurrences"], anchored_before)
        self.assertEqual(
            [item["id"] for item in field["occurrences"]],
            [
                "g-plus",
                "g-minus",
                "g-hidden-plus",
                "g-hidden-minus",
                "g-hidden-boundary",
                "g-focus",
                "g-post-focus",
            ],
        )


if __name__ == "__main__":
    unittest.main()

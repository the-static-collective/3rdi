from __future__ import annotations

import copy
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "skills" / "3rdi" / "scripts"))

from three_rdi.growth import compile_glyph_growth  # noqa: E402
from three_rdi.model import FieldError  # noqa: E402

SPECIMEN = ROOT / "specimens" / "glyph-growth-dot-line-l-u-y-001.json"


class GlyphGrowthTests(unittest.TestCase):
    def setUp(self) -> None:
        self.field = json.loads(SPECIMEN.read_text(encoding="utf-8"))

    def test_extend_point_to_first_line(self) -> None:
        receipt = compile_glyph_growth(self.field, "point-to-line")
        self.assertEqual(receipt["operation"]["kind"], "EXTEND")
        self.assertEqual(receipt["source"]["topology"]["vertices"], 1)
        self.assertEqual(receipt["target"]["topology"]["vertices"], 2)
        self.assertEqual(receipt["operation"]["added_vertices"], ["T"])
        self.assertEqual(receipt["operation"]["added_edges"], [["O", "T"]])

    def test_bend_introduces_a_real_turn_and_preserves_source_edge(self) -> None:
        receipt = compile_glyph_growth(self.field, "line-to-elbow")
        self.assertEqual(receipt["operation"]["kind"], "BEND")
        self.assertEqual(receipt["operation"]["preserved_inherited_edges"], 1)
        self.assertEqual(receipt["target"]["topology"]["edges"], 2)
        self.assertEqual(receipt["target"]["topology"]["branchpoints"], [])

    def test_return_builds_open_vessel_without_cycle(self) -> None:
        receipt = compile_glyph_growth(self.field, "elbow-to-cup")
        self.assertEqual(receipt["operation"]["kind"], "RETURN")
        self.assertEqual(receipt["operation"]["added_edges"], [["E", "F"]])
        self.assertEqual(receipt["target"]["topology"]["cycle_rank"], 0)
        self.assertEqual(len(receipt["target"]["topology"]["endpoints"]), 2)

    def test_fork_directly_from_point(self) -> None:
        receipt = compile_glyph_growth(self.field, "point-to-fork")
        self.assertEqual(receipt["operation"]["kind"], "FORK")
        self.assertEqual(len(receipt["operation"]["added_vertices"]), 3)
        self.assertEqual(receipt["target"]["topology"]["branchpoints"], ["O"])
        self.assertEqual(len(receipt["target"]["topology"]["endpoints"]), 3)

    def test_stable_output_under_serialization_order(self) -> None:
        initial = compile_glyph_growth(self.field, "elbow-to-cup")
        shifted = copy.deepcopy(self.field)
        shifted["source_refs"].reverse()
        shifted["operations"].reverse()
        for graph in shifted["carriers"].values():
            graph["landmarks"] = dict(reversed(list(graph["landmarks"].items())))
            graph["segments"] = [edge[::-1] for edge in reversed(graph["segments"])]
        self.assertEqual(initial, compile_glyph_growth(shifted, "elbow-to-cup"))

    def test_chain_is_explicit_not_implied(self) -> None:
        point = compile_glyph_growth(self.field, "point-to-line")
        elbow = compile_glyph_growth(self.field, "line-to-elbow")
        cup = compile_glyph_growth(self.field, "elbow-to-cup")
        self.assertEqual(point["target"]["digest"], elbow["source"]["digest"])
        self.assertEqual(elbow["target"]["digest"], cup["source"]["digest"])
        self.assertNotEqual(point["source"]["digest"], cup["target"]["digest"])

    def test_no_unrequested_ancestry_is_inferred(self) -> None:
        receipt = compile_glyph_growth(self.field, "point-to-fork")
        self.assertIn("not the inverse", receipt["operation"]["non_inverse"])
        self.assertIn("not its historical origin", receipt["non_authority"])
        self.assertNotIn("confidence", receipt)

    def test_cannot_rewrite_retained_coordinates(self) -> None:
        altered = copy.deepcopy(self.field)
        altered["carriers"]["ELBOW"]["landmarks"]["O"] = [0.1, 0]
        with self.assertRaisesRegex(FieldError, "preserve coordinates"):
            compile_glyph_growth(altered, "line-to-elbow")

    def test_cannot_drop_retained_edges(self) -> None:
        altered = copy.deepcopy(self.field)
        altered["carriers"]["ELBOW"]["segments"] = [["O", "F"], ["T", "F"]]
        with self.assertRaisesRegex(FieldError, "preserve every inherited edge"):
            compile_glyph_growth(altered, "line-to-elbow")

    def test_bend_rejects_straight_extension(self) -> None:
        altered = copy.deepcopy(self.field)
        altered["carriers"]["ELBOW"]["landmarks"]["F"] = [0, -1]
        with self.assertRaisesRegex(FieldError, "right-angle"):
            compile_glyph_growth(altered, "line-to-elbow")

    def test_return_rejects_closed_loop_and_wrong_direction(self) -> None:
        altered = copy.deepcopy(self.field)
        altered["carriers"]["CUP"]["segments"].append(["E", "T"])
        with self.assertRaisesRegex(FieldError, "RETURN"):
            compile_glyph_growth(altered, "elbow-to-cup")
        altered = copy.deepcopy(self.field)
        altered["carriers"]["CUP"]["landmarks"]["E"] = [2, 0]
        with self.assertRaisesRegex(FieldError, "opposite parallel uprights"):
            compile_glyph_growth(altered, "elbow-to-cup")

    def test_fork_rejects_fake_nonbranching_shape(self) -> None:
        altered = copy.deepcopy(self.field)
        altered["carriers"]["FORK"]["segments"] = [["O", "T"], ["T", "A"], ["A", "B"]]
        with self.assertRaisesRegex(FieldError, "degree-three Y junction"):
            compile_glyph_growth(altered, "point-to-fork")

    def test_unknown_operator_and_duplicate_ids_fail_closed(self) -> None:
        altered = copy.deepcopy(self.field)
        altered["operations"][0]["kind"] = "INFER-ANCESTRY"
        with self.assertRaisesRegex(FieldError, "unknown growth operator"):
            compile_glyph_growth(altered, "point-to-line")
        altered = copy.deepcopy(self.field)
        altered["operations"].append(copy.deepcopy(altered["operations"][0]))
        with self.assertRaisesRegex(FieldError, "duplicate growth operation"):
            compile_glyph_growth(altered, "point-to-line")

    def test_malformed_coordinates_and_wrong_schema_fail_closed(self) -> None:
        for bad in (float("nan"), True, "0"):
            altered = copy.deepcopy(self.field)
            altered["carriers"]["DOT"]["landmarks"]["O"][0] = bad
            with self.assertRaises(FieldError):
                compile_glyph_growth(altered, "point-to-line")
        altered = copy.deepcopy(self.field)
        altered["schema"] = "3rdi.glyph-formation-field/v0"
        with self.assertRaisesRegex(FieldError, "conform"):
            compile_glyph_growth(altered, "point-to-line")


if __name__ == "__main__":
    unittest.main()

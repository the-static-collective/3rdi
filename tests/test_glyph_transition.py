from __future__ import annotations

import copy
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "skills" / "3rdi" / "scripts"))
from three_rdi.transition import compile_glyph_transition  # noqa: E402
from three_rdi.model import FieldError  # noqa: E402

SPECIMEN = ROOT / "specimens" / "glyph-transition-y-point-l-u-001.json"


class GlyphTransitionTests(unittest.TestCase):
    def setUp(self):
        self.field = json.loads(SPECIMEN.read_text(encoding="utf-8"))

    def test_y_point_is_explicitly_lossy_but_replayable(self):
        receipt = compile_glyph_transition(self.field, "y-to-point")
        self.assertEqual(receipt["schema"], "3rdi.glyph-transition-receipt/v0")
        self.assertEqual(receipt["source"]["topology"]["branchpoints"], ["J"])
        self.assertEqual(receipt["source"]["topology"]["edges"], 3)
        self.assertEqual(receipt["target"]["topology"]["edges"], 0)
        self.assertEqual(receipt["transition"]["collapsed_source_edges"], 3)
        self.assertEqual(receipt["transition"]["distinct_source_vertices_lost"], 3)
        self.assertFalse(receipt["transition"]["invertible_from_visible_target"])
        self.assertEqual(receipt, compile_glyph_transition(copy.deepcopy(self.field), "y-to-point"))

    def test_l_to_u_preserves_path_topology_under_subdivision(self):
        receipt = compile_glyph_transition(self.field, "l-to-u")
        self.assertEqual(receipt["transition"]["subdivision_vertices_delta"], 1)
        for key in ("components", "cycle_rank", "branchpoints"):
            self.assertEqual(receipt["source"]["topology"][key], receipt["target"]["topology"][key])
        self.assertEqual(len(receipt["source"]["topology"]["endpoints"]), 2)
        self.assertEqual(len(receipt["target"]["topology"]["endpoints"]), 2)
        self.assertNotEqual(receipt["source"]["digest"], receipt["target"]["digest"])

    def test_reordering_graph_serialization_does_not_change_receipt(self):
        base = compile_glyph_transition(self.field, "l-to-u")
        altered = copy.deepcopy(self.field)
        graph = altered["carriers"]["U"]
        graph["landmarks"] = dict(reversed(list(graph["landmarks"].items())))
        graph["segments"] = [list(reversed(seg)) for seg in reversed(graph["segments"])]
        altered["source_refs"].reverse()
        altered["transitions"].reverse()
        self.assertEqual(base, compile_glyph_transition(altered, "l-to-u"))

    def test_reverse_quotient_does_not_manufacture_lost_branches(self):
        altered = copy.deepcopy(self.field)
        altered["transitions"].append({"id": "reverse", "kind": "QUOTIENT", "from": "DOT", "to": "Y", "vertex_map": {"P": "J"}})
        with self.assertRaisesRegex(FieldError, "cover every target vertex"):
            compile_glyph_transition(altered, "reverse")

    def test_y_to_u_is_not_deformation(self):
        altered = copy.deepcopy(self.field)
        altered["transitions"].append({"id": "wrong", "kind": "DEFORM", "from": "Y", "to": "U", "endpoint_map": {"L": "A", "B": "D"}})
        with self.assertRaisesRegex(FieldError, "connected simple path"):
            compile_glyph_transition(altered, "wrong")

    def test_endpoint_forgery_is_rejected(self):
        altered = copy.deepcopy(self.field)
        altered["transitions"][1]["endpoint_map"] = {"A": "A", "C": "B"}
        with self.assertRaisesRegex(FieldError, "bijective endpoint_map"):
            compile_glyph_transition(altered, "l-to-u")

    def test_unknown_edge_is_not_created_by_quotient(self):
        altered = copy.deepcopy(self.field)
        altered["transitions"].append({"id": "wrong", "kind": "QUOTIENT", "from": "L", "to": "U", "vertex_map": {"A": "A", "B": "B", "C": "C"}})
        with self.assertRaisesRegex(FieldError, "cover every target vertex"):
            compile_glyph_transition(altered, "wrong")

    def test_malformed_geometry_fails_closed(self):
        for bad in (float("nan"), True, "0"):
            altered = copy.deepcopy(self.field)
            altered["carriers"]["Y"]["landmarks"]["L"][0] = bad
            with self.assertRaises(FieldError):
                compile_glyph_transition(altered, "y-to-point")

    def test_wrong_schema_and_duplicate_edges_fail_closed(self):
        altered = copy.deepcopy(self.field)
        altered["schema"] = "3rdi.glyph-formation-field/v0"
        with self.assertRaisesRegex(FieldError, "schema"):
            compile_glyph_transition(altered, "l-to-u")
        altered = copy.deepcopy(self.field)
        altered["carriers"]["L"]["segments"].append(["B", "A"])
        with self.assertRaisesRegex(FieldError, "duplicate undirected segment"):
            compile_glyph_transition(altered, "l-to-u")

    def test_transition_receipt_is_not_source_authority(self):
        receipt = compile_glyph_transition(self.field, "y-to-point")
        self.assertIn("not a historical", receipt["non_authority"])
        self.assertNotIn("confidence", receipt)
        self.assertNotIn("meaning", receipt["transition"])


if __name__ == "__main__":
    unittest.main()

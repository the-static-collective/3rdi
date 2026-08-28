from __future__ import annotations

import copy
import json
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT_ROOT = ROOT / "skills" / "3rdi" / "scripts"
sys.path.insert(0, str(SCRIPT_ROOT))

from three_rdi import (  # noqa: E402
    FieldError,
    compile_glyph_formation,
    render_glyph_trace,
)


SPECIMEN = ROOT / "specimens" / "glyph-formation-y-001.json"


class GlyphFormationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.field = json.loads(SPECIMEN.read_text(encoding="utf-8"))

    def test_single_gesture_receipts_retrace_and_exact_reversal(self) -> None:
        receipt = compile_glyph_formation(self.field, "single-gesture")

        self.assertEqual(receipt["schema"], "3rdi.glyph-formation-receipt/v0")
        self.assertEqual(receipt["field_id"], "y-fork-001")
        self.assertEqual(receipt["formation"]["id"], "single-gesture")
        self.assertEqual(receipt["metrics"]["stroke_count"], 1)
        self.assertEqual(receipt["metrics"]["pen_lifts"], 0)
        self.assertEqual(receipt["metrics"]["segment_count"], 4)
        self.assertAlmostEqual(receipt["metrics"]["retrace_length"], 2**0.5, places=12)
        self.assertEqual(receipt["metrics"]["direction_reversals"], 1)
        self.assertEqual(receipt["gates"]["one-gesture"], "pass")
        self.assertEqual(receipt["gates"]["no-retrace"], "fail")
        self.assertEqual(receipt["tool_results"]["monoline-pen"], "compatible")
        self.assertEqual(receipt["tool_results"]["incised-stylus"], "strained")

    def test_all_candidates_keep_carrier_identity_but_not_formation_identity(self) -> None:
        receipts = [
            compile_glyph_formation(self.field, formation_id)
            for formation_id in ("stem-first", "fork-first", "left-rooted", "single-gesture")
        ]

        self.assertEqual(len({item["carrier"]["digest"] for item in receipts}), 1)
        self.assertEqual(len({item["formation"]["digest"] for item in receipts}), 4)
        self.assertEqual(
            [item["metrics"]["stroke_count"] for item in receipts],
            [3, 2, 2, 1],
        )
        self.assertEqual(
            [item["metrics"]["pen_lifts"] for item in receipts],
            [2, 1, 1, 0],
        )

    def test_receipt_refuses_confidence_and_preserves_non_collapse_notices(self) -> None:
        receipt = compile_glyph_formation(self.field, "stem-first")

        self.assertNotIn("confidence", receipt)
        self.assertNotIn("probability", receipt)
        self.assertEqual(
            receipt["non_collapse"],
            "carrier != formation hypothesis != decoder != projection",
        )
        self.assertIn("must not back-propagate", receipt["non_backpropagation"])
        self.assertIn("not the historical formation", receipt["non_authority"])

    def test_unobserved_segment_traversal_is_rejected(self) -> None:
        field = copy.deepcopy(self.field)
        field["formations"].append(
            {
                "id": "illegal-crossbar",
                "origin": "manual-hypothesis",
                "operations": [
                    {"id": "x1", "op": "stroke", "from": "L", "to": "R"}
                ],
            }
        )

        with self.assertRaisesRegex(FieldError, "not present in observed carrier"):
            compile_glyph_formation(field, "illegal-crossbar")

    def test_duplicate_formation_ids_are_rejected(self) -> None:
        field = copy.deepcopy(self.field)
        field["formations"].append(copy.deepcopy(field["formations"][0]))

        with self.assertRaisesRegex(FieldError, "duplicate formation id"):
            compile_glyph_formation(field, "stem-first")

    def test_renderer_is_deterministic_receipt_only_and_semantically_dumb(self) -> None:
        receipt = compile_glyph_formation(self.field, "single-gesture")

        html_a = render_glyph_trace(receipt)
        html_b = render_glyph_trace(copy.deepcopy(receipt))

        self.assertEqual(html_a, html_b)
        self.assertIn("<svg", html_a)
        self.assertIn("single-gesture", html_a)
        self.assertIn("carrier-y-001", html_a)
        self.assertIn("not the historical formation", html_a)
        self.assertNotIn(">tree<", html_a.lower())
        self.assertNotIn(">trinity<", html_a.lower())
        self.assertNotIn(">letter y<", html_a.lower())

    def test_renderer_rejects_source_field_instead_of_compiling_it(self) -> None:
        with self.assertRaisesRegex(FieldError, "formation receipt"):
            render_glyph_trace(self.field)


if __name__ == "__main__":
    unittest.main()

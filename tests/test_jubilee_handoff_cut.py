from __future__ import annotations

import copy
import json
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT_ROOT = ROOT / "skills" / "3rdi" / "scripts"
FIXTURE = ROOT / "specimens" / "jubilee-handoff-cut-001.json"
sys.path.insert(0, str(SCRIPT_ROOT))

from three_rdi import compile_cut  # noqa: E402


class JubileeHandoffCutTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.field = json.loads(FIXTURE.read_text(encoding="utf-8"))

    def test_same_immutable_handoff_field_exposes_distinct_observer_stages(self) -> None:
        original = copy.deepcopy(self.field)

        structural = compile_cut(self.field, "structural-only")
        available = compile_cut(self.field, "available-not-attended")
        attended = compile_cut(self.field, "attended-not-decoded")
        decoded = compile_cut(self.field, "decoded-not-taken")

        self.assertEqual(self.field, original)
        self.assertIn("handoff-a-b", {edge["id"] for edge in self.field["edges"]})

        self.assertEqual(structural["observer_view"]["edges"]["relevance"], [])
        self.assertIn(
            {"edge_id": "handoff-a-b", "reason": "not-available-to-observer"},
            structural["audit"]["withheld_edges"],
        )

        self.assertEqual(
            [edge["id"] for edge in available["observer_view"]["edges"]["relevance"]],
            ["handoff-a-b"],
        )
        self.assertEqual(available["observer_view"]["epistemic_trace"]["attention_events"], [])
        self.assertEqual(available["observer_view"]["epistemic_trace"]["decoder_applications"], [])

        self.assertEqual(
            [item["action"] for item in attended["observer_view"]["epistemic_trace"]["attention_events"]],
            ["attended"],
        )
        self.assertEqual(attended["observer_view"]["epistemic_trace"]["decoder_applications"], [])

        self.assertEqual(
            [item["decoder_ref"] for item in decoded["observer_view"]["epistemic_trace"]["decoder_applications"]],
            ["decoder:little-yes-v0"],
        )
        self.assertNotIn("taken", decoded["observer_view"])
        self.assertNotIn("authority", decoded)

    def test_later_decoder_access_does_not_rewrite_earlier_cut(self) -> None:
        earlier = compile_cut(self.field, "available-not-attended")
        reconstruction = compile_cut(self.field, "reconstruction-after-decoding")

        self.assertEqual(earlier["observer_view"]["epistemic_trace"]["decoder_applications"], [])
        decoder_trace = reconstruction["observer_view"]["epistemic_trace"]["decoder_applications"]
        self.assertEqual([item["id"] for item in decoder_trace], ["decode-handoff-lumi"])
        self.assertTrue(decoder_trace[0]["hindsight_bearing"])


if __name__ == "__main__":
    unittest.main()

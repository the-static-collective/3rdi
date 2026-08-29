from __future__ import annotations

import hashlib
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT_ROOT = ROOT / "skills" / "3rdi" / "scripts"
sys.path.insert(0, str(SCRIPT_ROOT))

from three_rdi import compile_cut, mortal_actor_handoff  # noqa: E402

SPECIMEN = ROOT / "specimens" / "mortal-actor-001.json"
EXPECTED_SHA256 = "528616358df6dc92cbf0dfa747d7af017f3b0389e4d17db995a9bba7f088f40b"


class MortalActorVectorProjectionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        raw = SPECIMEN.read_bytes()
        cls.field = json.loads(raw)
        cls.sha256 = hashlib.sha256(raw).hexdigest()
        cls.handoffs = {
            cut: mortal_actor_handoff(compile_cut(cls.field, cut))
            for cut in ("A0", "B0", "R0", "N0", "A1")
        }

    def test_specimen_is_byte_pinned_to_neutral_vector(self):
        self.assertEqual(self.sha256, EXPECTED_SHA256)

    def test_all_five_cuts_are_distinct_receipts(self):
        digests = [self.handoffs[cut]["projection_digest"] for cut in self.handoffs]
        self.assertEqual(len(set(digests)), 5)
        self.assertNotEqual(self.handoffs["A0"]["projection_digest"], self.handoffs["A1"]["projection_digest"])

    def test_a0_withholds_red_note_but_preserves_ignored_mirror_trace(self):
        h = self.handoffs["A0"]
        self.assertNotIn("red-note-placed", h["visible_occurrence_ids"])
        self.assertIn("mirror-scratch", h["visible_occurrence_ids"])
        self.assertIn("contact-mirror-A", h["contact_ids"])
        self.assertIn("attention-mirror-A", h["attention_event_ids"])
        self.assertNotIn("red-note-placed", str(h))

    def test_b0_available_key_has_no_contact(self):
        h = self.handoffs["B0"]
        self.assertIn("blue-key-dropped", h["visible_occurrence_ids"])
        self.assertEqual(h["contact_ids"], [])

    def test_r0_sees_relevance_without_causal_chime_order(self):
        h = self.handoffs["R0"]
        self.assertIn("red-note-placed", h["visible_occurrence_ids"])
        self.assertIn("relevance-mirror-red-note", h["visible_relevance_edge_ids"])
        self.assertIn("clock-chime-left", h["visible_occurrence_ids"])
        self.assertIn("clock-chime-right", h["visible_occurrence_ids"])
        self.assertEqual(h["visible_causal_edge_ids"], [])

    def test_n0_carries_lamp_decoder_and_stance_without_truth(self):
        h = self.handoffs["N0"]
        self.assertIn("lamp-flicker", h["visible_occurrence_ids"])
        self.assertIn("contact-lamp-N", h["contact_ids"])
        self.assertIn("decode-lamp-N", h["decoder_application_ids"])
        self.assertIn("stance-lamp-N", h["stance_ids"])
        for forbidden in ("true", "false", "supported", "authority", "authorized", "actionable"):
            self.assertNotIn(forbidden, h)

    def test_a1_gains_red_note_without_rewriting_a0(self):
        a0 = self.handoffs["A0"]
        a1 = self.handoffs["A1"]
        self.assertNotIn("red-note-placed", a0["visible_occurrence_ids"])
        self.assertIn("red-note-placed", a1["visible_occurrence_ids"])
        self.assertIn("contact-red-note-A1", a1["contact_ids"])
        self.assertIn("decode-red-note-A1", a1["decoder_application_ids"])
        self.assertIn("stance-red-note-A1", a1["stance_ids"])


if __name__ == "__main__":
    unittest.main()

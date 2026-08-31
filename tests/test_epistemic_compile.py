from __future__ import annotations

import sys
import unittest
from pathlib import Path


SCRIPT_ROOT = Path(__file__).resolve().parents[1] / "skills" / "3rdi" / "scripts"
sys.path.insert(0, str(SCRIPT_ROOT))

from three_rdi import compile_cut  # noqa: E402


def field_fixture() -> dict:
    return {
        "schema": "3rdi.field/v0",
        "field_id": "epistemic-compile-001",
        "occurrences": [
            {
                "id": "artifact",
                "occurred_at": "2026-06-10T10:00:00Z",
                "locus_id": "archive-room",
                "source_refs": ["source:artifact"],
            }
        ],
        "exposures": [
            {
                "id": "exposure-artifact-lumi",
                "occurrence_id": "artifact",
                "observer": "lumi",
                "layer": "private",
                "available_from": "2026-06-10T13:00:00Z",
                "evidence_refs": ["source:artifact"],
            }
        ],
        "contacts": [
            {
                "id": "contact-artifact-lumi",
                "occurrence_id": "artifact",
                "observer": "lumi",
                "layer": "private",
                "sensed_at": "2026-06-10T13:05:00Z",
                "evidence_refs": ["source:contact"],
            }
        ],
        "attention_events": [
            {
                "id": "attention-artifact-lumi",
                "contact_id": "contact-artifact-lumi",
                "observer": "lumi",
                "action": "ignored",
                "occurred_at": "2026-06-10T13:06:00Z",
                "evidence_refs": ["source:attention"],
            }
        ],
        "decoder_applications": [
            {
                "id": "decode-artifact-lumi",
                "contact_id": "contact-artifact-lumi",
                "observer": "lumi",
                "decoder_ref": "decoder:ordinary-mystery",
                "applied_at": "2026-06-10T13:07:00Z",
                "projection_ref": "projection:artifact-v1",
                "evidence_refs": ["source:decoder"],
            }
        ],
        "stances": [
            {
                "id": "stance-artifact-lumi",
                "observer": "lumi",
                "projection_ref": "projection:artifact-v1",
                "stance": "held",
                "formed_at": "2026-06-10T13:08:00Z",
                "evidence_refs": ["source:stance"],
            }
        ],
        "cuts": [
            {
                "id": "early",
                "observer": "lumi",
                "mode": "historical",
                "focus_at": "2026-06-10T12:00:00Z",
                "known_at": "2026-06-10T12:00:00Z",
                "audience_layers": ["private"],
                "location_scope": ["archive-room"],
                "focus_occurrence_ids": [],
                "gate_ids": [],
            },
            {
                "id": "late",
                "observer": "lumi",
                "mode": "historical",
                "focus_at": "2026-06-10T14:00:00Z",
                "known_at": "2026-06-10T14:00:00Z",
                "audience_layers": ["private"],
                "location_scope": ["archive-room"],
                "focus_occurrence_ids": [],
                "gate_ids": [],
            },
            {
                "id": "reconstruction",
                "observer": "lumi",
                "mode": "reconstruction",
                "focus_at": "2026-06-10T12:00:00Z",
                "known_at": "2026-06-10T14:00:00Z",
                "audience_layers": ["private"],
                "location_scope": ["archive-room"],
                "focus_occurrence_ids": [],
                "gate_ids": [],
            },
        ],
    }


class EpistemicCompileTests(unittest.TestCase):
    def test_late_cut_contains_attributable_epistemic_lineage(self) -> None:
        receipt = compile_cut(field_fixture(), "late")
        trace = receipt["observer_view"]["epistemic_trace"]

        self.assertEqual([item["id"] for item in trace["contacts"]], ["contact-artifact-lumi"])
        self.assertEqual([item["id"] for item in trace["attention_events"]], ["attention-artifact-lumi"])
        self.assertEqual([item["id"] for item in trace["decoder_applications"]], ["decode-artifact-lumi"])
        self.assertEqual([item["id"] for item in trace["stances"]], ["stance-artifact-lumi"])
        for family in trace.values():
            self.assertTrue(all(item["hindsight_bearing"] is False for item in family))

    def test_early_cut_does_not_synthesize_contact_from_future_exposure(self) -> None:
        receipt = compile_cut(field_fixture(), "early")
        trace = receipt["observer_view"]["epistemic_trace"]

        self.assertEqual(receipt["observer_view"]["occurrences"], [])
        self.assertEqual(trace["contacts"], [])
        self.assertEqual(trace["attention_events"], [])
        self.assertEqual(trace["decoder_applications"], [])
        self.assertEqual(trace["stances"], [])

    def test_reconstruction_marks_post_focus_epistemics_as_hindsight(self) -> None:
        receipt = compile_cut(field_fixture(), "reconstruction")
        trace = receipt["observer_view"]["epistemic_trace"]

        for family in trace.values():
            self.assertTrue(all(item["hindsight_bearing"] is True for item in family))
        self.assertTrue(receipt["audit"]["withheld_epistemic"] == [])

    def test_unextended_field_compiles_with_empty_trace(self) -> None:
        field = field_fixture()
        field["contacts"] = []
        field["attention_events"] = []
        field["decoder_applications"] = []
        field["stances"] = []

        receipt = compile_cut(field, "late")
        self.assertEqual(
            receipt["observer_view"]["epistemic_trace"],
            {"contacts": [], "attention_events": [], "decoder_applications": [], "stances": []},
        )


if __name__ == "__main__":
    unittest.main()

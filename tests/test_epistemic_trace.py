from __future__ import annotations

import sys
import unittest
from pathlib import Path


SCRIPT_ROOT = Path(__file__).resolve().parents[1] / "skills" / "3rdi" / "scripts"
sys.path.insert(0, str(SCRIPT_ROOT))

from three_rdi import FieldError, normalize_field  # noqa: E402


def minimal_field() -> dict:
    return {
        "schema": "3rdi.field/v0",
        "field_id": "epistemic-trace-001",
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
    }


def valid_lineage() -> dict:
    field = minimal_field()
    field["contacts"] = [
        {
            "id": "contact-artifact-lumi",
            "occurrence_id": "artifact",
            "observer": "lumi",
            "layer": "private",
            "sensed_at": "2026-06-10T13:05:00Z",
            "evidence_refs": ["source:contact"],
        }
    ]
    field["attention_events"] = [
        {
            "id": "attention-artifact-lumi",
            "contact_id": "contact-artifact-lumi",
            "observer": "lumi",
            "action": "ignored",
            "occurred_at": "2026-06-10T13:06:00Z",
            "evidence_refs": ["source:attention"],
        }
    ]
    field["decoder_applications"] = [
        {
            "id": "decode-artifact-lumi",
            "contact_id": "contact-artifact-lumi",
            "observer": "lumi",
            "decoder_ref": "decoder:ordinary-mystery",
            "applied_at": "2026-06-10T13:07:00Z",
            "projection_ref": "projection:artifact-v1",
            "evidence_refs": ["source:decoder"],
        }
    ]
    field["stances"] = [
        {
            "id": "stance-artifact-lumi",
            "observer": "lumi",
            "projection_ref": "projection:artifact-v1",
            "stance": "rejected",
            "formed_at": "2026-06-10T13:08:00Z",
            "evidence_refs": ["source:stance"],
        }
    ]
    return field


class EpistemicBoundaryTests(unittest.TestCase):
    def test_epistemic_arrays_default_empty_without_synthesizing_contact(self) -> None:
        normalized = normalize_field(minimal_field())

        self.assertEqual(normalized["contacts"], [])
        self.assertEqual(normalized["attention_events"], [])
        self.assertEqual(normalized["decoder_applications"], [])
        self.assertEqual(normalized["stances"], [])

    def test_contact_requires_lawful_exposure_by_sensed_at(self) -> None:
        field = minimal_field()
        field["contacts"] = [
            {
                "id": "contact-too-early",
                "occurrence_id": "artifact",
                "observer": "lumi",
                "layer": "private",
                "sensed_at": "2026-06-10T12:59:00Z",
                "evidence_refs": ["source:contact"],
            }
        ]

        with self.assertRaisesRegex(FieldError, "no lawful exposure available by sensed_at"):
            normalize_field(field)

    def test_ignored_requires_contact_ancestry(self) -> None:
        field = minimal_field()
        field["attention_events"] = [
            {
                "id": "attention-orphan",
                "contact_id": "contact-missing",
                "observer": "lumi",
                "action": "ignored",
                "occurred_at": "2026-06-10T13:06:00Z",
                "evidence_refs": ["source:attention"],
            }
        ]

        with self.assertRaisesRegex(FieldError, "references unknown contact"):
            normalize_field(field)

    def test_stance_cannot_use_memento_gate_vocabulary(self) -> None:
        field = minimal_field()
        field["stances"] = [
            {
                "id": "stance-bad",
                "observer": "lumi",
                "projection_ref": "projection:missing",
                "stance": "refuse",
                "formed_at": "2026-06-10T13:08:00Z",
                "evidence_refs": ["source:stance"],
            }
        ]

        with self.assertRaisesRegex(FieldError, "accepted, held, or rejected"):
            normalize_field(field)

    def test_valid_lineage_preserves_all_four_record_families(self) -> None:
        normalized = normalize_field(valid_lineage())

        self.assertEqual(normalized["contacts"][0]["id"], "contact-artifact-lumi")
        self.assertEqual(normalized["attention_events"][0]["action"], "ignored")
        self.assertEqual(
            normalized["decoder_applications"][0]["projection_ref"],
            "projection:artifact-v1",
        )
        self.assertEqual(normalized["stances"][0]["stance"], "rejected")


if __name__ == "__main__":
    unittest.main()

from __future__ import annotations

import copy
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT_ROOT = ROOT / "skills" / "3rdi" / "scripts"
sys.path.insert(0, str(SCRIPT_ROOT))

from emit_memento_handoff import HandoffError, build_memento_handoff  # noqa: E402
from three_rdi import canonical_json, compile_cut  # noqa: E402


def field_fixture() -> dict:
    return {
        "schema": "3rdi.field/v0",
        "field_id": "memento-handoff-001",
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
                "action": "attended",
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
                "id": "late",
                "observer": "lumi",
                "mode": "historical",
                "focus_at": "2026-06-10T14:00:00Z",
                "known_at": "2026-06-10T14:00:00Z",
                "audience_layers": ["private"],
                "location_scope": ["archive-room"],
                "focus_occurrence_ids": [],
                "gate_ids": [],
            }
        ],
    }


class MementoHandoffTests(unittest.TestCase):
    def projection(self) -> dict:
        return compile_cut(field_fixture(), "late")

    def test_builder_is_deterministic_and_preserves_projection_identity(self) -> None:
        projection = self.projection()
        first = build_memento_handoff(
            projection,
            emitted_at="2026-08-31T20:00:00Z",
            world_instance_id="same-room-a1",
        )
        second = build_memento_handoff(
            projection,
            emitted_at="2026-08-31T20:00:00Z",
            world_instance_id="same-room-a1",
        )

        self.assertEqual(canonical_json(first), canonical_json(second))
        self.assertEqual(first["schema"], "3rdi.memento-handoff/v0")
        self.assertEqual(first["projection_digest"], projection["projection_digest"])
        self.assertEqual(
            first["epistemic_trace"], projection["observer_view"]["epistemic_trace"]
        )
        self.assertEqual(first["authority"], "handoff-only-no-write-no-admission")
        self.assertEqual(first["world_instance_id"], "same-room-a1")
        self.assertEqual(first["residual_fog"], [])

    def test_builder_rejects_wrong_projection_schema(self) -> None:
        projection = self.projection()
        projection["schema"] = "wrong"
        with self.assertRaisesRegex(HandoffError, "projection schema"):
            build_memento_handoff(projection, emitted_at="2026-08-31T20:00:00Z")

    def test_builder_rejects_blank_observer_or_cut_identity(self) -> None:
        for key in ("observer", "id"):
            projection = self.projection()
            projection["cut"][key] = ""
            with self.assertRaises(HandoffError):
                build_memento_handoff(projection, emitted_at="2026-08-31T20:00:00Z")

    def test_builder_rejects_timezone_less_emitted_at(self) -> None:
        with self.assertRaisesRegex(HandoffError, "emitted_at"):
            build_memento_handoff(
                self.projection(), emitted_at="2026-08-31T20:00:00"
            )

    def test_builder_rejects_trace_record_without_stable_id(self) -> None:
        projection = copy.deepcopy(self.projection())
        del projection["observer_view"]["epistemic_trace"]["contacts"][0]["id"]
        with self.assertRaisesRegex(HandoffError, "stable id"):
            build_memento_handoff(projection, emitted_at="2026-08-31T20:00:00Z")

    def test_cli_stdout_is_byte_identical_for_identical_inputs(self) -> None:
        projection = self.projection()
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "projection.json"
            path.write_text(json.dumps(projection), encoding="utf-8")
            command = [
                sys.executable,
                str(SCRIPT_ROOT / "emit_memento_handoff.py"),
                str(path),
                "--emitted-at",
                "2026-08-31T20:00:00Z",
            ]
            first = subprocess.run(command, check=True, capture_output=True)
            second = subprocess.run(command, check=True, capture_output=True)

        self.assertEqual(first.stdout, second.stdout)
        handoff = json.loads(first.stdout)
        self.assertEqual(handoff["projection_digest"], projection["projection_digest"])


if __name__ == "__main__":
    unittest.main()

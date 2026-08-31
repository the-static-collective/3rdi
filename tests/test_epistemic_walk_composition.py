from __future__ import annotations

import copy
import sys
import unittest
from pathlib import Path


SCRIPT_ROOT = Path(__file__).resolve().parents[1] / "skills" / "3rdi" / "scripts"
sys.path.insert(0, str(SCRIPT_ROOT))

from three_rdi import compile_cut, normalize_field  # noqa: E402
from three_rdi.epistemic import compile_cut as compile_epistemic_cut  # noqa: E402
from three_rdi.model import canonical_json  # noqa: E402


def composed_field() -> dict:
    return {
        "schema": "3rdi.field/v0",
        "field_id": "epistemic-walk-composition-001",
        "occurrences": [
            {
                "id": "e0",
                "occurred_at": "2026-08-31T10:00:00Z",
                "locus_id": "lab",
                "source_refs": ["source:e0"],
            },
            {
                "id": "e1",
                "occurred_at": "2026-08-31T10:01:00Z",
                "locus_id": "lab",
                "source_refs": ["source:e1"],
            },
        ],
        "exposures": [
            {
                "id": "exposure-e0",
                "occurrence_id": "e0",
                "observer": "observer-a",
                "layer": "private",
                "available_from": "2026-08-31T10:02:00Z",
                "evidence_refs": ["source:e0"],
            },
            {
                "id": "exposure-e1",
                "occurrence_id": "e1",
                "observer": "observer-a",
                "layer": "private",
                "available_from": "2026-08-31T10:02:00Z",
                "evidence_refs": ["source:e1"],
            },
        ],
        "contacts": [
            {
                "id": "contact-e1",
                "occurrence_id": "e1",
                "observer": "observer-a",
                "layer": "private",
                "sensed_at": "2026-08-31T10:03:00Z",
                "evidence_refs": ["source:contact"],
            }
        ],
        "attention_events": [],
        "decoder_applications": [],
        "stances": [],
        "formation_walks": [
            {
                "id": "walk-visible",
                "endpoint_occurrence_id": "e1",
                "observer": "observer-a",
                "layer": "private",
                "formed_at": "2026-08-31T10:04:00Z",
                "available_from": "2026-08-31T10:05:00Z",
                "step_refs": ["e0", "e1"],
                "source_refs": ["receipt:walk-visible"],
            },
            {
                "id": "walk-hidden",
                "endpoint_occurrence_id": "e1",
                "observer": "observer-a",
                "layer": "private",
                "formed_at": "2026-08-31T10:04:00Z",
                "available_from": "2026-08-31T10:30:00Z",
                "step_refs": ["hidden-a", "e1"],
                "source_refs": ["receipt:walk-hidden"],
            },
        ],
        "cuts": [
            {
                "id": "cut-a",
                "observer": "observer-a",
                "mode": "historical",
                "focus_at": "2026-08-31T10:10:00Z",
                "known_at": "2026-08-31T10:10:00Z",
                "audience_layers": ["private"],
                "location_scope": ["lab"],
                "focus_occurrence_ids": ["e1"],
                "gate_ids": [],
            }
        ],
    }


class EpistemicWalkCompositionTests(unittest.TestCase):
    def test_public_compiler_preserves_epistemic_trace_and_projects_available_walk(self) -> None:
        normalized = normalize_field(composed_field())
        self.assertEqual([item["id"] for item in normalized["contacts"]], ["contact-e1"])
        self.assertEqual(
            [item["id"] for item in normalized["formation_walks"]],
            ["walk-hidden", "walk-visible"],
        )

        receipt = compile_cut(composed_field(), "cut-a")
        self.assertEqual(
            [item["id"] for item in receipt["observer_view"]["epistemic_trace"]["contacts"]],
            ["contact-e1"],
        )
        self.assertEqual(
            [item["id"] for item in receipt["observer_view"]["formation_walks"]],
            ["walk-visible"],
        )

    def test_hidden_walk_mutation_does_not_perturb_epistemic_projection_digest(self) -> None:
        before = compile_cut(composed_field(), "cut-a")
        mutated = copy.deepcopy(composed_field())
        hidden = next(item for item in mutated["formation_walks"] if item["id"] == "walk-hidden")
        hidden["step_refs"] = ["different", "hidden", "road"]
        hidden["source_refs"] = ["receipt:different"]
        after = compile_cut(mutated, "cut-a")
        self.assertEqual(before["projection_digest"], after["projection_digest"])
        self.assertEqual(
            before["observer_view"]["epistemic_trace"],
            after["observer_view"]["epistemic_trace"],
        )

    def test_omitted_walk_family_is_byte_identical_to_epistemic_compiler(self) -> None:
        field = composed_field()
        field.pop("formation_walks")
        composed = compile_cut(field, "cut-a")
        epistemic = compile_epistemic_cut(field, "cut-a")
        self.assertEqual(canonical_json(composed), canonical_json(epistemic))
        self.assertEqual(composed["projection_digest"], epistemic["projection_digest"])


if __name__ == "__main__":
    unittest.main()

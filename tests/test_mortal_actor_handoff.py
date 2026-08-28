from __future__ import annotations

import sys
import unittest
from pathlib import Path


SCRIPT_ROOT = Path(__file__).resolve().parents[1] / "skills" / "3rdi" / "scripts"
sys.path.insert(0, str(SCRIPT_ROOT))

from three_rdi import FieldError, compile_cut, mortal_actor_handoff  # noqa: E402


def field_fixture() -> dict:
    return {
        "schema": "3rdi.field/v0",
        "field_id": "mortal-handoff-001",
        "occurrences": [
            {
                "id": "seen-contacted",
                "occurred_at": "2026-08-27T12:00:00Z",
                "locus_id": "room:one",
                "source_refs": ["source:one"],
            },
            {
                "id": "seen-no-contact",
                "occurred_at": "2026-08-27T12:00:01Z",
                "locus_id": "room:one",
                "source_refs": ["source:two"],
            },
            {
                "id": "withheld",
                "occurred_at": "2026-08-27T12:00:02Z",
                "locus_id": "room:one",
                "source_refs": ["source:hidden"],
            },
        ],
        "exposures": [
            {
                "id": "seen-contacted-a",
                "occurrence_id": "seen-contacted",
                "observer": "A",
                "layer": "private",
                "available_from": "2026-08-27T12:00:00Z",
                "evidence_refs": ["exposure:one"],
            },
            {
                "id": "seen-no-contact-a",
                "occurrence_id": "seen-no-contact",
                "observer": "A",
                "layer": "private",
                "available_from": "2026-08-27T12:00:01Z",
                "evidence_refs": ["exposure:two"],
            },
        ],
        "contacts": [
            {
                "id": "contact-one-a",
                "occurrence_id": "seen-contacted",
                "observer": "A",
                "layer": "private",
                "sensed_at": "2026-08-27T12:00:03Z",
                "evidence_refs": ["contact:one"],
            }
        ],
        "attention_events": [
            {
                "id": "attention-one-a",
                "contact_id": "contact-one-a",
                "observer": "A",
                "action": "ignored",
                "occurred_at": "2026-08-27T12:00:04Z",
                "evidence_refs": ["attention:one"],
            }
        ],
        "cuts": [
            {
                "id": "A0",
                "observer": "A",
                "mode": "historical",
                "focus_at": "2026-08-27T12:00:10Z",
                "known_at": "2026-08-27T12:00:10Z",
                "audience_layers": ["private"],
                "location_scope": ["room:one"],
                "focus_occurrence_ids": [],
                "gate_ids": [],
            }
        ],
    }


def all_keys(value):
    if isinstance(value, dict):
        for key, child in value.items():
            yield key
            yield from all_keys(child)
    elif isinstance(value, list):
        for child in value:
            yield from all_keys(child)


class MortalActorHandoffTests(unittest.TestCase):
    def test_handoff_exports_visible_identity_and_epistemic_ancestry(self) -> None:
        projection = compile_cut(field_fixture(), "A0")
        handoff = mortal_actor_handoff(projection)

        self.assertEqual(handoff["schema"], "mortal_actor.3rdi-handoff/v0")
        self.assertEqual(handoff["projection_digest"], projection["projection_digest"])
        self.assertEqual(handoff["field_id"], "mortal-handoff-001")
        self.assertEqual(handoff["cut_id"], "A0")
        self.assertEqual(handoff["observer"], "A")
        self.assertEqual(handoff["visible_occurrence_ids"], ["seen-contacted", "seen-no-contact"])
        self.assertEqual(handoff["contact_ids"], ["contact-one-a"])
        self.assertEqual(handoff["attention_event_ids"], ["attention-one-a"])

    def test_visibility_does_not_synthesize_contact_and_withheld_identity_does_not_leak(self) -> None:
        handoff = mortal_actor_handoff(compile_cut(field_fixture(), "A0"))

        self.assertIn("seen-no-contact", handoff["visible_occurrence_ids"])
        self.assertNotIn("seen-no-contact", handoff["contact_ids"])
        self.assertNotIn("withheld", str(handoff))

    def test_handoff_has_no_semantic_or_authority_keys(self) -> None:
        handoff = mortal_actor_handoff(compile_cut(field_fixture(), "A0"))
        forbidden = {
            "supported",
            "truth",
            "falsehood",
            "authority",
            "admitted",
            "authorized",
            "actionable",
            "execute",
            "global_truth",
        }
        self.assertTrue(forbidden.isdisjoint(set(all_keys(handoff))))

    def test_raw_projection_without_epistemic_trace_is_refused(self) -> None:
        projection = compile_cut(field_fixture(), "A0")
        del projection["observer_view"]["epistemic_trace"]
        with self.assertRaisesRegex(FieldError, "requires epistemic trace support"):
            mortal_actor_handoff(projection)


if __name__ == "__main__":
    unittest.main()

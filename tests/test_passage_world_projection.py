from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT_ROOT = ROOT / "skills" / "3rdi" / "scripts"
sys.path.insert(0, str(SCRIPT_ROOT))

from three_rdi import compile_cut  # noqa: E402


SPECIMEN = ROOT / "specimens" / "passage-world-001.json"


def load_field() -> dict:
    return json.loads(SPECIMEN.read_text(encoding="utf-8"))


def visible_ids(receipt: dict) -> set[str]:
    return {item["id"] for item in receipt["observer_view"]["occurrences"]}


def trace(receipt: dict) -> dict:
    return receipt["observer_view"]["epistemic_trace"]


class PassageWorldProjectionTests(unittest.TestCase):
    def test_two_lawful_apertures_share_field_but_not_projection(self) -> None:
        field = load_field()
        road_a = compile_cut(field, "ROAD-A")
        road_b0 = compile_cut(field, "ROAD-B0")
        road_b1 = compile_cut(field, "ROAD-B1")

        self.assertEqual(road_a["field_id"], road_b0["field_id"])
        self.assertEqual(road_b0["field_id"], road_b1["field_id"])
        self.assertNotEqual(road_a["projection_digest"], road_b1["projection_digest"])
        self.assertIn("evidence-e1", visible_ids(road_a))
        self.assertNotIn("evidence-e1", visible_ids(road_b0))
        self.assertIn("carrier-e2", visible_ids(road_b0))
        self.assertIn("distractor-visible-no-contact", visible_ids(road_a))
        self.assertIn("distractor-visible-no-contact", visible_ids(road_b0))

    def test_road_a_has_direct_contact_and_road_b_grows_decoder_descendant(self) -> None:
        field = load_field()
        road_a = compile_cut(field, "ROAD-A")
        road_b0 = compile_cut(field, "ROAD-B0")
        road_b1 = compile_cut(field, "ROAD-B1")

        self.assertEqual(
            [item["id"] for item in trace(road_a)["contacts"]],
            ["contact-e1-road-a"],
        )
        self.assertEqual(
            [item["id"] for item in trace(road_b0)["contacts"]],
            ["contact-e2-road-b"],
        )
        self.assertEqual(trace(road_b0)["decoder_applications"], [])
        self.assertEqual(trace(road_b0)["stances"], [])
        self.assertEqual(
            [item["id"] for item in trace(road_b1)["contacts"]],
            ["contact-e2-road-b"],
        )
        self.assertEqual(
            [item["id"] for item in trace(road_b1)["decoder_applications"]],
            ["decoder-road-b1"],
        )
        self.assertEqual(
            [item["id"] for item in trace(road_b1)["stances"]],
            ["stance-road-b1"],
        )

    def test_road_b0_is_not_rewritten_by_later_decoder_history(self) -> None:
        road_b0 = compile_cut(load_field(), "ROAD-B0")
        encoded = json.dumps(road_b0, sort_keys=True)

        self.assertNotIn("decoder-road-b1", encoded)
        self.assertNotIn("stance-road-b1", encoded)
        self.assertNotIn("projection:road-b1-token", encoded)

    def test_visible_distractor_does_not_synthesize_contact(self) -> None:
        for cut_id in ("ROAD-A", "ROAD-B0", "ROAD-B1"):
            receipt = compile_cut(load_field(), cut_id)
            self.assertIn("distractor-visible-no-contact", visible_ids(receipt))
            contacted_occurrences = {
                item["occurrence_id"] for item in trace(receipt)["contacts"]
            }
            self.assertNotIn("distractor-visible-no-contact", contacted_occurrences)

    def test_3rdi_output_contains_no_passage_verdict(self) -> None:
        for cut_id in ("ROAD-A", "ROAD-B0", "ROAD-B1"):
            encoded = json.dumps(compile_cut(load_field(), cut_id), sort_keys=True)
            self.assertNotIn("PASSAGE_DISTINCT", encoded)
            self.assertNotIn("PASSAGE_EQUIVALENT", encoded)


if __name__ == "__main__":
    unittest.main()

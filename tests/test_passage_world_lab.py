from __future__ import annotations

import importlib.util
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RUN_LABS = ROOT / "skills" / "3rdi" / "scripts" / "run_labs.py"


def load_run_labs_module():
    spec = importlib.util.spec_from_file_location("three_rdi_run_labs", RUN_LABS)
    if spec is None or spec.loader is None:
        raise AssertionError("could not load run_labs.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class PassageWorldLabTests(unittest.TestCase):
    def test_passage_world_lab_is_projection_only(self) -> None:
        lab = load_run_labs_module().run_passage_world_lab()
        self.assertEqual(
            set(lab),
            {
                "id",
                "status",
                "road_a_projection_digest",
                "road_b_projection_digest",
                "same_field",
                "road_a_direct_contact",
                "road_b_decoder_descendant",
                "road_b0_not_rewritten",
            },
        )
        self.assertEqual(lab["id"], "PASSAGE-WORLD-3RDI-001")
        self.assertEqual(lab["status"], "pass")
        self.assertTrue(lab["same_field"])
        self.assertTrue(lab["road_a_direct_contact"])
        self.assertTrue(lab["road_b_decoder_descendant"])
        self.assertTrue(lab["road_b0_not_rewritten"])
        self.assertNotEqual(lab["road_a_projection_digest"], lab["road_b_projection_digest"])

        encoded = json.dumps(lab, sort_keys=True)
        for forbidden in ("payload:022100", "door:R1", "SUPPORTS", "PASSAGE_DISTINCT", "PASSAGE_EQUIVALENT"):
            self.assertNotIn(forbidden, encoded)


if __name__ == "__main__":
    unittest.main()

from __future__ import annotations

import copy
import json
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT_ROOT = ROOT / "skills" / "3rdi" / "scripts"
sys.path.insert(0, str(SCRIPT_ROOT))

from three_rdi import FieldError, normalize_field  # noqa: E402


class FormationWalkTemporalValidityTests(unittest.TestCase):
    def test_walk_cannot_be_available_before_it_is_formed(self) -> None:
        field = json.loads(
            (ROOT / "specimens" / "walk-receipt-projection-001.json").read_text()
        )
        hostile = copy.deepcopy(field)
        hostile["formation_walks"][0]["formed_at"] = "2026-08-31T10:10:00Z"
        hostile["formation_walks"][0]["available_from"] = "2026-08-31T10:09:00Z"

        with self.assertRaisesRegex(
            FieldError, "available_from cannot precede formed_at"
        ):
            normalize_field(hostile)

    def test_walk_cannot_form_before_its_endpoint_occurs(self) -> None:
        field = json.loads(
            (ROOT / "specimens" / "walk-receipt-projection-001.json").read_text()
        )
        hostile = copy.deepcopy(field)
        hostile["formation_walks"][0]["formed_at"] = "2026-08-31T10:02:00Z"
        hostile["formation_walks"][0]["available_from"] = "2026-08-31T10:10:00Z"

        with self.assertRaisesRegex(
            FieldError, "formed_at cannot precede endpoint occurrence"
        ):
            normalize_field(hostile)

    def test_walk_step_refs_cannot_dangle(self) -> None:
        field = json.loads(
            (ROOT / "specimens" / "walk-receipt-projection-001.json").read_text()
        )
        hostile = copy.deepcopy(field)
        hostile["formation_walks"][0]["step_refs"] = ["e0", "missing-step", "e3"]

        with self.assertRaisesRegex(
            FieldError, "references unknown step occurrence 'missing-step'"
        ):
            normalize_field(hostile)


if __name__ == "__main__":
    unittest.main()

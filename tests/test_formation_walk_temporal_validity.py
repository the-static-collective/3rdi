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
            FieldError, "available_from precedes formed_at"
        ):
            normalize_field(hostile)


if __name__ == "__main__":
    unittest.main()

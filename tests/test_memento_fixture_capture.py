from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT_ROOT = ROOT / "skills" / "3rdi" / "scripts"
sys.path.insert(0, str(SCRIPT_ROOT))

from emit_memento_handoff import build_memento_handoff  # noqa: E402
from three_rdi import canonical_json, compile_cut  # noqa: E402


class MementoFixtureReplayTests(unittest.TestCase):
    def test_canonical_fixture_matches_real_compiler_and_emitter_bytes(self) -> None:
        source = json.loads(
            (ROOT / "specimens" / "memento-handoff-source-001.json").read_text(
                encoding="utf-8"
            )
        )
        projection = compile_cut(source, "a1")
        handoff = build_memento_handoff(
            projection,
            emitted_at="2026-08-31T20:00:00Z",
            world_instance_id="same-room-a1",
        )
        expected = canonical_json(handoff) + "\n"
        frozen = (ROOT / "specimens" / "memento-handoff-001.json").read_text(
            encoding="utf-8"
        )
        self.assertEqual(frozen, expected)


if __name__ == "__main__":
    unittest.main()

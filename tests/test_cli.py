from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class CliTests(unittest.TestCase):
    def test_projection_cli_checks_named_cut(self) -> None:
        result = subprocess.run(
            [
                sys.executable,
                "skills/3rdi/scripts/compile_projection.py",
                "specimens/temporal-coordinate-001.json",
                "--cut",
                "june-15",
                "--check",
            ],
            cwd=ROOT,
            check=False,
            capture_output=True,
            text=True,
        )

        self.assertEqual(result.returncode, 0, result.stderr)
        receipt = json.loads(result.stdout)
        self.assertEqual(receipt["schema"], "3rdi.projection-receipt/v0")
        self.assertEqual(receipt["cut_id"], "june-15")
        self.assertTrue(receipt["projection_digest"].startswith("sha256:"))

    def test_lab_runner_proves_all_named_controls(self) -> None:
        result = subprocess.run(
            [sys.executable, "skills/3rdi/scripts/run_labs.py", "--check"],
            cwd=ROOT,
            check=False,
            capture_output=True,
            text=True,
        )

        self.assertEqual(result.returncode, 0, result.stderr)
        receipt = json.loads(result.stdout)
        self.assertEqual(receipt["schema"], "3rdi.lab-receipt/v0")
        self.assertEqual(receipt["status"], "pass")
        self.assertEqual(
            {lab["id"] for lab in receipt["labs"]},
            {
                "TEMPORAL-COORDINATE-001",
                "CAUSAL-RELEVANCE-001",
                "GLYPH-RECEIVER-001",
                "TWO-NARRATOR-001",
                "RUPTURE-REACHABILITY-001",
                "PASSAGE-WORLD-3RDI-001",
            },
        )


if __name__ == "__main__":
    unittest.main()

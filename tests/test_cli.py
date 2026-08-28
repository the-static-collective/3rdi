from __future__ import annotations

import json
import subprocess
import sys
import tempfile
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

    def test_glyph_formation_cli_checks_named_candidate(self) -> None:
        result = subprocess.run(
            [
                sys.executable,
                "skills/3rdi/scripts/compile_glyph_formation.py",
                "specimens/glyph-formation-y-001.json",
                "--formation",
                "single-gesture",
                "--check",
            ],
            cwd=ROOT,
            check=False,
            capture_output=True,
            text=True,
        )

        self.assertEqual(result.returncode, 0, result.stderr)
        receipt = json.loads(result.stdout)
        self.assertEqual(receipt["schema"], "3rdi.glyph-formation-receipt/v0")
        self.assertEqual(receipt["field_id"], "y-fork-001")
        self.assertEqual(receipt["formation_id"], "single-gesture")
        self.assertTrue(receipt["receipt_digest"].startswith("sha256:"))

    def test_glyph_renderer_cli_writes_receipt_only_html(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp = Path(temp_dir)
            receipt_path = temp / "receipt.json"
            html_path = temp / "glyphtrace.html"

            compiled = subprocess.run(
                [
                    sys.executable,
                    "skills/3rdi/scripts/compile_glyph_formation.py",
                    "specimens/glyph-formation-y-001.json",
                    "--formation",
                    "single-gesture",
                ],
                cwd=ROOT,
                check=False,
                capture_output=True,
                text=True,
            )
            self.assertEqual(compiled.returncode, 0, compiled.stderr)
            receipt_path.write_text(compiled.stdout, encoding="utf-8")

            rendered = subprocess.run(
                [
                    sys.executable,
                    "skills/3rdi/scripts/render_glyph_trace.py",
                    str(receipt_path),
                    "--output",
                    str(html_path),
                ],
                cwd=ROOT,
                check=False,
                capture_output=True,
                text=True,
            )

            self.assertEqual(rendered.returncode, 0, rendered.stderr)
            html = html_path.read_text(encoding="utf-8")
            self.assertIn("<svg", html)
            self.assertIn("single-gesture", html)
            self.assertIn("not the historical formation", html)

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
            },
        )


if __name__ == "__main__":
    unittest.main()

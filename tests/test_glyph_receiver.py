from __future__ import annotations

import sys
import unittest
from pathlib import Path


SCRIPT_ROOT = Path(__file__).resolve().parents[1] / "skills" / "3rdi" / "scripts"
sys.path.insert(0, str(SCRIPT_ROOT))

from three_rdi import FieldError, decode_fret_glyph  # noqa: E402


class GlyphReceiverTests(unittest.TestCase):
    def test_same_carrier_different_tuning_different_lawful_projection(self) -> None:
        standard = decode_fret_glyph(
            "022100",
            {
                "id": "standard-a440",
                "open_midi": [40, 45, 50, 55, 59, 64],
                "reference_hz": 440.0,
                "temperament": "12-TET",
                "constitution": "EADGBE / 12-TET / A440",
            },
        )
        cgcegd = decode_fret_glyph(
            "022100",
            {
                "id": "cgcegd-a444",
                "open_midi": [36, 43, 48, 52, 55, 62],
                "reference_hz": 444.0,
                "temperament": "12-TET",
                "constitution": "CGCEGD / 12-TET / A444",
            },
        )

        self.assertEqual(standard["carrier"]["digest"], cgcegd["carrier"]["digest"])
        self.assertNotEqual(standard["decoder"]["digest"], cgcegd["decoder"]["digest"])
        self.assertNotEqual(standard["projection"]["digest"], cgcegd["projection"]["digest"])
        self.assertEqual(standard["projection"]["pitch_names"], ["E", "B", "E", "G#", "B", "E"])
        self.assertEqual(cgcegd["projection"]["pitch_names"], ["C", "A", "D", "F", "G", "D"])

    def test_reference_pitch_uniformly_rescales_frequency(self) -> None:
        decoder = {
            "id": "standard",
            "open_midi": [40, 45, 50, 55, 59, 64],
            "reference_hz": 440.0,
            "temperament": "12-TET",
            "constitution": "EADGBE / 12-TET",
        }
        a440 = decode_fret_glyph("000000", decoder)
        decoder["reference_hz"] = 444.0
        a444 = decode_fret_glyph("000000", decoder)

        ratios = [
            newer / older
            for older, newer in zip(
                a440["projection"]["frequencies_hz"],
                a444["projection"]["frequencies_hz"],
                strict=True,
            )
        ]
        for ratio in ratios:
            self.assertAlmostEqual(ratio, 444.0 / 440.0, places=12)

    def test_invalid_carrier_is_rejected(self) -> None:
        decoder = {
            "id": "standard",
            "open_midi": [40, 45, 50, 55, 59, 64],
            "reference_hz": 440.0,
            "temperament": "12-TET",
            "constitution": "EADGBE / 12-TET",
        }
        with self.assertRaisesRegex(FieldError, "six decimal fret positions"):
            decode_fret_glyph("02x100", decoder)

    def test_undeclared_temperament_is_rejected(self) -> None:
        decoder = {
            "id": "mystery",
            "open_midi": [40, 45, 50, 55, 59, 64],
            "reference_hz": 440.0,
            "temperament": "unknown",
            "constitution": "undeclared",
        }
        with self.assertRaisesRegex(FieldError, "temperament.*12-TET"):
            decode_fret_glyph("022100", decoder)

    def test_non_finite_reference_pitch_is_rejected(self) -> None:
        decoder = {
            "id": "broken",
            "open_midi": [40, 45, 50, 55, 59, 64],
            "reference_hz": float("nan"),
            "temperament": "12-TET",
            "constitution": "EADGBE / 12-TET",
        }
        with self.assertRaisesRegex(FieldError, "finite"):
            decode_fret_glyph("022100", decoder)


if __name__ == "__main__":
    unittest.main()

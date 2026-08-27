"""Deterministic foreign-domain receiver control for six-string fret glyphs."""

from __future__ import annotations

import math
import re
from typing import Any

from .model import FieldError, canonical_digest


PITCH_NAMES = ("C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B")


def decode_fret_glyph(carrier: str, decoder: dict[str, Any]) -> dict[str, Any]:
    """Decode a six-string fret carrier under a declared 12-TET constitution."""

    if not isinstance(carrier, str) or re.fullmatch(r"[0-9]{6}", carrier) is None:
        raise FieldError("carrier must contain exactly six decimal fret positions")
    if not isinstance(decoder, dict):
        raise FieldError("decoder must be an object")
    open_midi = decoder.get("open_midi")
    if (
        not isinstance(open_midi, list)
        or len(open_midi) != 6
        or any(not isinstance(value, int) or isinstance(value, bool) for value in open_midi)
        or any(value < 0 or value > 127 for value in open_midi)
    ):
        raise FieldError("decoder.open_midi must contain six integer MIDI note numbers")
    reference_hz = decoder.get("reference_hz")
    if (
        not isinstance(reference_hz, (int, float))
        or isinstance(reference_hz, bool)
        or not math.isfinite(float(reference_hz))
        or reference_hz <= 0
    ):
        raise FieldError("decoder.reference_hz must be finite and positive")
    for key in ("id", "constitution"):
        if not isinstance(decoder.get(key), str) or not decoder[key]:
            raise FieldError(f"decoder.{key} must be a non-empty string")
    if decoder.get("temperament") != "12-TET":
        raise FieldError("decoder.temperament must explicitly equal '12-TET'")

    fret_positions = [int(character) for character in carrier]
    midi_notes = [
        open_note + fret
        for open_note, fret in zip(open_midi, fret_positions, strict=True)
    ]
    pitch_names = [PITCH_NAMES[note % 12] for note in midi_notes]
    frequencies = [
        float(reference_hz) * math.pow(2.0, (note - 69) / 12)
        for note in midi_notes
    ]
    carrier_receipt = {"token": carrier, "digest": canonical_digest(carrier)}
    decoder_receipt = {**decoder, "digest": canonical_digest(decoder)}
    projection_value = {
        "midi_notes": midi_notes,
        "pitch_names": pitch_names,
        "frequencies_hz": frequencies,
    }
    projection = {**projection_value, "digest": canonical_digest(projection_value)}
    return {
        "schema": "3rdi.decoder-receipt/v0",
        "carrier": carrier_receipt,
        "decoder": decoder_receipt,
        "projection": projection,
        "non_collapse": "carrier != decoder != projection",
    }

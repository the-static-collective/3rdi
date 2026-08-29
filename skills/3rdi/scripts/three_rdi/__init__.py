"""Public surface for the 3rdi reference kernel."""

from .compile import compile_cut
from .formation import compile_glyph_formation
from .glyph import decode_fret_glyph
from .model import FieldError, canonical_digest, canonical_json, normalize_field
from .render import render_glyph_trace

__all__ = [
    "FieldError",
    "canonical_digest",
    "canonical_json",
    "compile_cut",
    "compile_glyph_formation",
    "decode_fret_glyph",
    "normalize_field",
    "render_glyph_trace",
]

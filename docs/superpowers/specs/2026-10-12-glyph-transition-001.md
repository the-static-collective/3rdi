# Glyph Transition 001 — quotient versus deformation

**Status:** experimental 3rdi sidecar, October 12, 2026.

## Problem

Existing GlyphTrace compares drawing histories for the *same* observed carrier. The `Y → ·` and `L → U` specimens instead compare **different carriers**. Conflating the two would turn loss of information into a fictitious reversible morph or topology preservation into a semantic claim.

## Typed operators

- `QUOTIENT`: a total, vertex-surjective mapping from source graph to target graph; every mapped source edge either collapses within one target vertex or corresponds to an actual target edge. Every target edge must be covered. The result is a lossy projection even when the receipt retains the original digest.
- `DEFORM`: in v0, two **connected simple path graphs** may differ in coordinates and in the number of degree-two subdivisions. A bijection explicitly maps the two endpoints. This demonstrates graph-theoretic equivalence under subdivision, **not** a physical animation or evidence of historical transmission.

The operators do not imply one another. Source and target are canonicalized (sorted undirected edges and landmark keys); numeric geometry must be finite. Receipt digests are computed over the full attributed receipt excluding its self-hash.

## Specimens

`specimens/glyph-transition-y-point-l-u-001.json` includes:

| Transition | Source invariant | Target invariant | Result |
|---|---|---|---|
| `Y → ·` | 4 vertices, 3 edges, 1 branchpoint, 1 component | 1 vertex, 0 edges, 0 branchpoints, 1 component | `QUOTIENT`: all four vertices mapped to point P; three edges collapse; source recoverable only from source record, not target mark |
| `L → U` | 3 vertices, 2 edges, one simple path | 4 vertices, 3 edges, one simple path | `DEFORM`: degree-two subdivision preserves path topology; geometric trajectory changes |

## Test gates

`python3 -m unittest discover -s tests -p test_glyph_transition.py -v`:

- deterministic receipts under input object/edge ordering changes;
- endpoint bijection enforced;
- reverse `· → Y` refused as a quotient;
- `Y → U` refused as a path deformation;
- malformed coordinates, duplicate edges, unknown vertices rejected;
- original source digest and separate destination digest retained;
- nothing infers meaning, origin, authorship, physical formation, or authority.

## Architectural boundaries

This is a **separate sidecar** in 3rdi. It does not modify GlyphTrace v0, create a new Witness Sigil, reinterpret `P0..PF`, alter Toaster rendering, or admit any permissions. A later adapter may read these receipts for visualization or reLATTE transport, but transport must preserve the schema and attribution, not upgrade the interpretation.

**Working law:** `same topology != same shape; same destination != same history; source receipt != visible reversibility`.

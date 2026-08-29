# GlyphTrace v0 Design

**Status:** approved design · 2026-08-28

## Purpose

GlyphTrace extends 3rdi with a deterministic foreign-domain sidecar for reconstructing and visualizing multiple candidate formation histories of one observed symbol without collapsing the observed carrier, candidate motion, decoder, projection, evidence, or authority.

The extension is not a paleographic truth engine. It answers a narrower question:

> Given an observed geometric carrier and explicitly declared candidate stroke programs, what reproducible formation properties follow under declared tool constitutions?

## Constitutional law

Preserve the existing 3rdi boundary:

```text
carrier != decoder != projection
```

Add one term:

```text
carrier != formation hypothesis != decoder != projection
```

And one forbidden arrow:

```text
semantic projection -/-> formation assessment
```

A meaningful interpretation may not back-propagate into the formation evidence and make one candidate drawing history more likely.

## Architecture

Use a **formation sidecar + bridge**, not a new field ledger inside `3rdi.field/v0`.

```text
3rdi.glyph-formation-field/v0
        |
        v
pure formation compiler
        |
        v
3rdi.glyph-formation-receipt/v0
        |
        +--> dumb render model --> SVG/HTML viewer
        |
        +--> later decoder bridge / ordinary 3rdi projections
```

The phase-0 projection kernel remains unchanged.

## Input contract

A `3rdi.glyph-formation-field/v0` document contains:

- `field_id`: stable field identifier;
- `carrier`: an observed normalized landmark graph;
- `tool_constitutions`: declared physical drawing-tool assumptions;
- `formations`: manually declared candidate stroke programs;
- `formation_gates`: pure metric predicates;
- `source_refs`: provenance references.

### Carrier

The v0 carrier uses named 2D landmarks and undirected observed segments. Coordinates are normalized geometry, not historical coordinates.

```json
{
  "id": "carrier-y-001",
  "representation": {
    "kind": "normalized-landmarks",
    "landmarks": {
      "L": [-1.0, 1.0],
      "J": [0.0, 0.0],
      "R": [1.0, 1.0],
      "B": [0.0, -1.0]
    },
    "segments": [["L", "J"], ["J", "R"], ["J", "B"]]
  },
  "source_refs": ["owner-supplied-symbol"]
}
```

The compiler rejects a candidate traversal that uses a segment not present in the observed carrier. Direction is a formation hypothesis, not carrier evidence.

### Formation candidate

Each formation is a candidate motor history consisting of one or more stroke operations. Supported v0 operations:

```json
{"id":"a1","op":"stroke","from":"B","to":"J"}
```

and:

```json
{"id":"d1","op":"stroke_path","through":["L","J","R","J","B"]}
```

Each operation is one uninterrupted stroke. The transition between operations implies a lift.

### Tool constitution

A tool constitution declares only properties the v0 compiler can deterministically apply:

```json
{
  "id": "incised-stylus",
  "kind": "incision",
  "allows_lift": true,
  "allows_retrace": true,
  "retrace_visibility": "high"
}
```

`retrace_visibility` is one of `low | high`. In v0, a candidate with non-zero retrace is `strained` under a `high` retrace-visibility tool and `compatible` otherwise. This is a declared-model result, not archaeological proof.

### Formation gates

V0 gates are pure `eq` predicates over numeric metrics:

```json
{
  "id": "one-gesture",
  "condition": {"metric":"pen_lifts","op":"eq","value":0}
}
```

Supported metrics are `stroke_count`, `pen_lifts`, `segment_count`, `retrace_length`, `total_length`, and `direction_reversals`.

## Deterministic formation metrics

For each candidate the compiler emits:

- `stroke_count`: number of operations;
- `pen_lifts`: `max(stroke_count - 1, 0)`;
- `segment_count`: number of traversed line segments;
- `total_length`: Euclidean traversal length;
- `retrace_length`: Euclidean length of traversals over an undirected segment already traversed earlier;
- `direction_reversals`: count of adjacent traversals in the same stroke where the next segment exactly reverses the previous segment.

Lengths are rounded to 12 decimal places before receipt hashing.

## Output contract

`compile_glyph_formation(field, formation_id)` returns `3rdi.glyph-formation-receipt/v0` containing:

- canonical carrier receipt and digest;
- formation id and canonical operation program;
- deterministic metrics;
- tool compatibility results;
- pure gate results;
- a declarative render model;
- canonical receipt digest;
- explicit non-collapse and non-authority notices.

No overall probability or confidence score is emitted.

The required notices are:

```text
carrier != formation hypothesis != decoder != projection
semantic projection must not back-propagate into formation assessment
This receipt witnesses a reproducible candidate formation, not the historical formation of the carrier.
```

## Dumb visualization boundary

The renderer consumes only a formation receipt. It does not read the original field, select candidates, alter metrics, rank histories, or infer meaning.

`render_glyph_trace(receipt)` returns a standalone UTF-8 HTML document containing an SVG animation/readout derived from `receipt.render_model`.

The viewer must visibly identify:

- carrier id;
- formation id;
- stroke order;
- metric values;
- gate states;
- tool results;
- the non-authority notice.

A rendered glyph is a projection witness, not evidence or authority.

## Y/fork seed specimen

`specimens/glyph-formation-y-001.json` carries one fixed Y-shaped carrier with four candidate formations:

1. `stem-first`: `B->J`, `J->L`, `J->R`;
2. `fork-first`: `L->J->R`, `J->B`;
3. `left-rooted`: `L->J->B`, `R->J`;
4. `single-gesture`: `L->J->R->J->B`.

Expected differentiators:

| formation | strokes | lifts | retrace | exact reversals |
|---|---:|---:|---:|---:|
| stem-first | 3 | 2 | 0 | 0 |
| fork-first | 2 | 1 | 0 | 0 |
| left-rooted | 2 | 1 | 0 | 0 |
| single-gesture | 1 | 0 | sqrt(2) | 1 |

The final carrier topology is identical across all four candidates.

## CLI surface

Phase-0 adds two executable scripts rather than a broad command framework:

```bash
python3 skills/3rdi/scripts/compile_glyph_formation.py FIELD.json --formation single-gesture
python3 skills/3rdi/scripts/render_glyph_trace.py RECEIPT.json --output glyphtrace.html
```

The compile CLI may use `--check` to print schema, field id, formation id, and receipt digest.

## Scope exclusions

GlyphTrace v0 does not:

- infer stroke histories from bitmap images;
- rank historical likelihood;
- perform OCR;
- infer semantic meaning;
- execute generic symbolic decoders;
- claim author intent;
- mutate `3rdi.field/v0`;
- add persistence, network access, telemetry, UI frameworks, or third-party dependencies.

## Verification

Required verification remains repository-native:

```bash
python3 -m unittest discover -s tests -v
python3 skills/3rdi/scripts/run_labs.py --check
python3 skills/3rdi/scripts/compile_glyph_formation.py specimens/glyph-formation-y-001.json --formation single-gesture --check
git diff --check
```

The visualization is verified structurally: identical receipt input must yield byte-identical HTML, and the HTML must expose only receipted geometry/metadata.
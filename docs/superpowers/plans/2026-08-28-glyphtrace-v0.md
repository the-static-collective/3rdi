# GlyphTrace v0 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a deterministic GlyphTrace formation sidecar that compiles declared symbol stroke histories into receipted metrics and renders those receipts as standalone SVG/HTML without altering the 3rdi projection kernel.

**Architecture:** Keep `3rdi.field/v0` unchanged. Add a focused `three_rdi.formation` compiler and a separate `three_rdi.render` receipt renderer; expose both through small scripts. The compiler never consumes semantic projections, and the renderer never consumes source fields.

**Tech Stack:** Python 3.11+ standard library, `unittest`, standalone SVG/HTML.

**Spec:** `docs/superpowers/specs/2026-08-28-glyphtrace-v0-design.md`

## Global Constraints

- Preserve `carrier != formation hypothesis != decoder != projection`.
- Semantic projection must not back-propagate into formation assessment.
- The renderer consumes only a formation receipt and is deterministic.
- Do not modify `3rdi.field/v0` or the existing phase-0 projection compiler.
- Do not add third-party dependencies.
- No historical likelihood score, OCR, image inference, or semantic meaning inference.

---

### Task 1: Lock the Y/fork executable contract in tests

**Files:**
- Create: `specimens/glyph-formation-y-001.json`
- Create: `tests/test_glyph_formation.py`

**Interfaces:**
- Consumes: existing `FieldError` and `canonical_digest` from `three_rdi`.
- Produces contract for `compile_glyph_formation(field: object, formation_id: str) -> dict[str, object]` and `render_glyph_trace(receipt: object) -> str`.

- [ ] **Step 1: Add the four-formation Y specimen**

Use normalized landmarks `L`, `J`, `R`, `B`; observed carrier segments `L-J`, `J-R`, `J-B`; tools `monoline-pen` and `incised-stylus`; gates `one-gesture` and `no-retrace`; and formations `stem-first`, `fork-first`, `left-rooted`, `single-gesture` exactly as specified by the design.

- [ ] **Step 2: Write failing formation tests**

Tests must assert:

```python
receipt = compile_glyph_formation(field, "single-gesture")
self.assertEqual(receipt["schema"], "3rdi.glyph-formation-receipt/v0")
self.assertEqual(receipt["metrics"]["stroke_count"], 1)
self.assertEqual(receipt["metrics"]["pen_lifts"], 0)
self.assertAlmostEqual(receipt["metrics"]["retrace_length"], 2 ** 0.5)
self.assertEqual(receipt["metrics"]["direction_reversals"], 1)
self.assertEqual(receipt["gates"]["one-gesture"], "pass")
self.assertEqual(receipt["gates"]["no-retrace"], "fail")
self.assertEqual(receipt["tool_results"]["incised-stylus"], "strained")
```

Also assert that all four candidates share the same carrier digest while formation digests differ; illegal traversal of an unobserved segment raises `FieldError`; duplicate formation ids raise `FieldError`; and the non-authority/non-backpropagation notices are present.

- [ ] **Step 3: Write failing renderer test**

```python
html_a = render_glyph_trace(receipt)
html_b = render_glyph_trace(receipt)
self.assertEqual(html_a, html_b)
self.assertIn("<svg", html_a)
self.assertIn("single-gesture", html_a)
self.assertIn("not the historical formation", html_a)
```

- [ ] **Step 4: Commit RED tests and specimen**

Commit message:

```text
test: define GlyphTrace formation contract
```

Open a draft pull request so repository CI runs. Confirm the unit job fails because `compile_glyph_formation` / `render_glyph_trace` do not exist.

---

### Task 2: Implement the pure formation compiler

**Files:**
- Create: `skills/3rdi/scripts/three_rdi/formation.py`
- Modify: `skills/3rdi/scripts/three_rdi/__init__.py`

**Interfaces:**
- Consumes: `canonical_digest`, `FieldError`.
- Produces: `compile_glyph_formation(raw_field: object, formation_id: str) -> dict[str, object]`.

- [ ] **Step 1: Normalize the sidecar field at the boundary**

Reject non-object input, wrong schema, missing/non-string ids, non-finite 2D landmarks, duplicate ids, unknown landmark references, unsupported operations, unsupported gate operators/metrics, and candidate traversals not present in the carrier's undirected observed segment set.

- [ ] **Step 2: Compile the minimal traversal model**

Expand every `stroke` or `stroke_path` into ordered directed segment traversals while preserving operation id and stroke index.

- [ ] **Step 3: Compute deterministic metrics**

Use Euclidean length. Round `total_length` and `retrace_length` to 12 decimal places. Count retrace when an undirected segment has already been traversed; count exact reversal when adjacent traversals within one stroke are `(A,B)` then `(B,A)`.

- [ ] **Step 4: Evaluate tool constitutions and gates**

Tool rule:

```python
"strained" if metrics["retrace_length"] > 0 and tool["retrace_visibility"] == "high" else "compatible"
```

Gate rule: v0 supports only numeric `eq`; compare the receipted metric with the declared value and return `pass | fail`.

- [ ] **Step 5: Build the render model and receipt**

The render model contains carrier landmarks, ordered traversals grouped by stroke, and no semantic interpretation. Hash carrier, formation program, and final receipt canonically. Include the three constitutional notices from the spec.

- [ ] **Step 6: Run CI through the draft PR**

Expected: formation tests advance from import failure to green except renderer-specific tests.

- [ ] **Step 7: Commit**

```text
feat: compile GlyphTrace formation receipts
```

---

### Task 3: Implement the dumb deterministic renderer

**Files:**
- Create: `skills/3rdi/scripts/three_rdi/render.py`
- Modify: `skills/3rdi/scripts/three_rdi/__init__.py`

**Interfaces:**
- Consumes: one `3rdi.glyph-formation-receipt/v0` object.
- Produces: `render_glyph_trace(receipt: object) -> str` standalone HTML.

- [ ] **Step 1: Validate receipt-only input**

Reject non-object input and any schema other than `3rdi.glyph-formation-receipt/v0`. Do not accept or fetch a source field.

- [ ] **Step 2: Render stable SVG geometry**

Map normalized landmark bounds into a fixed `640 x 480` SVG viewport with a deterministic margin. Render observed carrier segments as a static underlay and formation traversals as ordered `<path>` elements with `data-stroke-index`, `data-operation-id`, and deterministic animation delays.

- [ ] **Step 3: Render receipted readout**

Include carrier id, formation id, metrics, gate states, tool results, and escaped non-authority notice. Do not add inferred labels such as tree, fork, ascent, letter, or meaning.

- [ ] **Step 4: Run tests**

Expected: all `tests/test_glyph_formation.py` tests green and byte-identical repeated HTML output.

- [ ] **Step 5: Commit**

```text
feat: render GlyphTrace formation receipts
```

---

### Task 4: Add executable CLIs and contract regression checks

**Files:**
- Create: `skills/3rdi/scripts/compile_glyph_formation.py`
- Create: `skills/3rdi/scripts/render_glyph_trace.py`
- Modify: `tests/test_cli.py`
- Modify: `skills/3rdi/SKILL.md`

**Interfaces:**
- Compile CLI: `FIELD.json --formation FORMATION_ID [--check]`.
- Render CLI: `RECEIPT.json --output OUTPUT.html`.

- [ ] **Step 1: Add failing CLI tests**

Use subprocess calls following existing CLI tests. Assert compile `--check` exits 0 and prints schema/field/formation/digest JSON. Assert renderer writes HTML containing `<svg` and the selected formation id.

- [ ] **Step 2: Implement compile CLI**

Load JSON, call `compile_glyph_formation`, print full receipt or compact `--check`; on `OSError`, `JSONDecodeError`, or `FieldError`, print `3rdi: ...` to stderr and return 2.

- [ ] **Step 3: Implement render CLI**

Load receipt JSON, call `render_glyph_trace`, write UTF-8 output path; same error boundary and return code 2.

- [ ] **Step 4: Add compact operator documentation**

Extend `SKILL.md` only enough to name GlyphTrace as a foreign-domain formation sidecar, state the no-backpropagation law, and show the two commands. Do not expand ordinary 3rdi invocation triggers.

- [ ] **Step 5: Run full repository verification**

CI must pass:

```bash
python3 -m unittest discover -s tests -v
python3 skills/3rdi/scripts/run_labs.py --check
python3 skills/3rdi/scripts/compile_projection.py specimens/temporal-coordinate-001.json --cut june-15 --check
```

Additionally verify:

```bash
python3 skills/3rdi/scripts/compile_glyph_formation.py specimens/glyph-formation-y-001.json --formation single-gesture --check
```

- [ ] **Step 6: Commit**

```text
feat: expose GlyphTrace executable surface
```

---

### Task 5: Final verification and PR readiness

**Files:**
- No planned production changes; only fixes required by verification/review.

**Interfaces:**
- Produces: reviewable feature branch with deterministic CI evidence.

- [ ] **Step 1: Confirm no projection-kernel drift**

Review the PR diff and verify `three_rdi/compile.py`, `three_rdi/model.py`, and `3rdi.field/v0` specimens are unchanged.

- [ ] **Step 2: Confirm constitutional pressure cases**

Verify tests prove: same carrier/different formations; semantic labels absent from compiler/renderer; no overall confidence score; illegal carrier traversal rejected; high-retrace tool changes declared compatibility without changing carrier digest.

- [ ] **Step 3: Confirm Actions GREEN**

Record the successful workflow run and head SHA in the PR description.

- [ ] **Step 4: Request code review**

Review specifically for provenance collapse, accidental historical claims, renderer-side inference, and schema creep.

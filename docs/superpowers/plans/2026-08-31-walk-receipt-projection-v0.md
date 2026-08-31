# WALK-RECEIPT-PROJECTION-001 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make supplied formation-walk receipts observer-projectable when they are lawfully available while proving hidden/unavailable walks cannot perturb earlier endpoint projections.

**Architecture:** Extend the normalized `3rdi.field/v0` model with an optional `formation_walks` family, validate it in the existing model layer, and filter it during `compile_cut()` using the cut observer/layer/known-at surface plus ordinary endpoint visibility. Existing fields without formation walks remain byte-compatible.

**Tech Stack:** Python 3 standard library; existing `three_rdi.model`, `three_rdi.compile`, canonical JSON/digest helpers, and unittest suite.

**Spec:** `docs/superpowers/specs/2026-08-31-walk-receipt-projection-v0-design.md`

## Global Constraints

- `ENDPOINT PROJECTION != FORMATION WALK`.
- Never infer, reconstruct, or shortest-path a walk.
- A walk never makes its endpoint occurrence visible.
- Hidden walk content must not perturb a projection digest for a cut that cannot see it.
- Same endpoint may retain multiple visible walk IDs.
- No ALEX/Dogram dependency, support/evidence semantics, authority, or side effects.
- Fields without `formation_walks` must preserve current behavior.

---

### Task 1: Validate and normalize formation-walk records

**Files:**
- Modify: `skills/3rdi/scripts/three_rdi/model.py`
- Test: `tests/test_projection.py`

**Interfaces:**
- Extend normalized field output with `formation_walks: list[dict[str, object]]`, defaulting to `[]`.
- Each normalized record contains exactly: `id`, `endpoint_occurrence_id`, `observer`, `layer`, `formed_at`, `available_from`, `step_refs`, `source_refs`.

- [ ] **Step 1: Add RED validation tests**

Add tests for one valid formation walk plus refusal cases for duplicate walk IDs, unknown endpoint occurrence, blank `id`/`observer`/`layer`, invalid timestamps, non-list `step_refs`, non-list `source_refs`, and non-string reference entries.

Use a valid record shaped as:

```python
walk = {
    "id": "walk-a",
    "endpoint_occurrence_id": "e3",
    "observer": "observer-a",
    "layer": "private",
    "formed_at": "2026-08-31T12:00:00Z",
    "available_from": "2026-08-31T12:05:00Z",
    "step_refs": ["e0", "e1", "e3"],
    "source_refs": ["receipt:walk-a"],
}
```

- [ ] **Step 2: Run the focused RED set**

```bash
python3 -m unittest tests.test_projection -v
```

Expected: new cases fail because the field model does not yet know `formation_walks`.

- [ ] **Step 3: Add normalization with existing FieldError discipline**

Normalize absent `formation_walks` to `[]`. Require unique nonblank IDs, string observer/layer, endpoint membership in the normalized occurrence IDs, explicit timezone-bearing timestamps, and lists of nonblank strings for references. Preserve `step_refs` order because it is formation data; sort the family itself later during projection.

- [ ] **Step 4: Run projection tests**

```bash
python3 -m unittest tests.test_projection -v
```

Expected: validation tests pass and existing cases remain green.

- [ ] **Step 5: Commit model support**

```bash
git add skills/3rdi/scripts/three_rdi/model.py tests/test_projection.py
git commit -m "feat: validate formation walk records"
```

---

### Task 2: Project walks without granting endpoint visibility

**Files:**
- Modify: `skills/3rdi/scripts/three_rdi/compile.py`
- Test: `tests/test_projection.py`

**Interfaces:**
- `compile_cut()` output gains `formation_walks: list[dict[str, object]]` only as part of the normal projection receipt.
- Withheld audit entries use stable reasons: `different-observer`, `audience-layer-closed`, `not-yet-formed`, `not-available`, `endpoint-withheld`.

- [ ] **Step 1: Add the three-cut same-endpoint RED matrix**

Freeze one field with:

```text
walk A: e0 -> e1 -> e3
walk B: e0 -> e2 -> e3
```

and cuts:

```text
a0: endpoint e3 visible, neither walk available
a1: endpoint e3 visible, walk A available
a2: endpoint e3 visible, walks A and B available
```

Assert:

```python
assert project(a0)["formation_walks"] == []
assert [w["id"] for w in project(a1)["formation_walks"]] == ["walk-a"]
assert [w["id"] for w in project(a2)["formation_walks"]] == ["walk-a", "walk-b"]
```

Also assert the ordinary visible occurrence IDs are identical across the three cuts when their occurrence exposure is otherwise equal.

- [ ] **Step 2: Run focused RED**

```bash
python3 -m unittest tests.test_projection -v
```

Expected: walk projection assertions fail.

- [ ] **Step 3: Implement walk visibility as an explicit conjunction**

For each normalized walk, require in order:

```python
walk["observer"] == cut["observer"]
walk["layer"] in admitted_layers
walk["formed_at"] <= cut["known_at"]
walk["available_from"] <= cut["known_at"]
walk["endpoint_occurrence_id"] in visible_occurrence_ids
```

Copy visible records without interpreting `step_refs`. Add:

```python
"hindsight_bearing": walk["available_from"] > cut["focus_at"]
```

Sort visible walks by `id` before receipt construction.

- [ ] **Step 4: Add withheld audit records without leaking hidden steps**

When the field model makes the walk ID itself available for audit, expose only `id`, `endpoint_occurrence_id`, and the refusal reason. Do not copy `step_refs` or `source_refs` into withheld audit entries.

- [ ] **Step 5: Run projection tests**

```bash
python3 -m unittest tests.test_projection -v
```

Expected: same-endpoint matrix and existing projection suite pass.

- [ ] **Step 6: Commit projection behavior**

```bash
git add skills/3rdi/scripts/three_rdi/compile.py tests/test_projection.py
git commit -m "feat: project attributable formation walks"
```

---

### Task 3: Prove hidden-walk noninterference and digest stability

**Files:**
- Modify: `tests/test_projection.py`
- Create: `specimens/walk-receipt-projection-001.json`

**Interfaces:**
- Consumes: ordinary `compile_cut()`.
- Produces: hostile proof that inaccessible path mutations do not change earlier receipts.

- [ ] **Step 1: Add hidden mutation tests**

Compile a cut where `walk-b` is unavailable. Then change only `walk-b.step_refs`, `walk-b.source_refs`, and list position. Require:

```python
assert before["projection_digest"] == after["projection_digest"]
assert before["visible_occurrence_ids"] == after["visible_occurrence_ids"]
assert before["formation_walks"] == after["formation_walks"]
```

Use a second control where `walk-b` becomes visible and require the projection digest to change when visible walk content changes.

- [ ] **Step 2: Add observer/layer/endpoint hostile controls**

Require wrong-observer, closed-layer, not-yet-formed, not-available, and endpoint-withheld walks to remain unavailable with the correct refusal reason. Explicitly prove a visible walk record cannot cause an otherwise-withheld endpoint to appear.

- [ ] **Step 3: Freeze the synthetic specimen**

Create `specimens/walk-receipt-projection-001.json` containing the two walks and three cuts used by the tests. Keep all timestamps explicit and deterministic.

- [ ] **Step 4: Run focused and full floors**

```bash
python3 -m unittest tests.test_projection -v
python3 -m unittest discover -s tests -v
python3 skills/3rdi/scripts/run_labs.py --check
```

Expected: all pass.

- [ ] **Step 5: Commit hostile proof + fixture**

```bash
git add tests/test_projection.py specimens/walk-receipt-projection-001.json
git commit -m "test: prove hidden walk noninterference"
```

---

### Task 4: Lock compatibility at the CLI and skill boundary

**Files:**
- Modify: `tests/test_cli.py`
- Modify: `tests/test_skill_operator_contract.py`
- Modify: `skills/3rdi/references/receipt-contract.md`

**Interfaces:**
- Existing CLI remains `compile_projection.py FIELD --cut CUT`.
- No new CLI mode or operator name.

- [ ] **Step 1: Add compatibility tests**

Compile an existing fixture with no `formation_walks` and require its receipt/compact `--check` fields to remain unchanged. Add one fixture with walks and assert full output includes `formation_walks` while `--check` still exposes only the existing compact identity fields.

- [ ] **Step 2: Document the receipt surface**

Add a bounded section to `receipt-contract.md`:

```text
formation_walks = optional observer-local provenance surface
walk receipt != endpoint visibility
walk receipt != support/evidence/authority
```

Do not add a new universal 3rdi operator.

- [ ] **Step 3: Run the complete repository floor**

```bash
python3 -m unittest discover -s tests -v
python3 skills/3rdi/scripts/run_labs.py --check
```

- [ ] **Step 4: Commit boundary documentation**

```bash
git add tests/test_cli.py tests/test_skill_operator_contract.py skills/3rdi/references/receipt-contract.md
git commit -m "docs: expose formation walk projection boundary"
```

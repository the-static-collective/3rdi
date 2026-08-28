# 3rdi × MEMENTO UNDERSTORY Routing Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Extend 3rdi with executable observer contact/attention/decoder/stance traces plus capability-based routing to MEMENTO/UNDERSTORY and a `NARRATIVE-CUT` application profile, while preserving pure projection and no-side-effect boundaries.

**Architecture:** Keep `3rdi.field/v0` backward compatible by adding optional epistemic receipt arrays. Existing fields that omit them normalize to empty arrays. Projection receipts gain `observer_view.epistemic_trace` and `audit.withheld_epistemic`. Routing remains operator behavior: 3rdi may emit a MEMENTO handoff envelope but never writes or admits durable MEMENTO state.

**Tech Stack:** Python 3 standard library, `unittest`, JSON, Markdown skill references, GitHub Actions.

**Spec:** `the-static-collective/MEMENTO@123bb3592cbf8cb4f0a7c413af5bf010d8f6cd0b:docs/superpowers/specs/2026-08-27-understory-historical-imaginations-design.md`

## Global Constraints

- Preserve `occurrence != availability != attention != relevance`, `carrier != decoder != projection`, `projection != source != authority`, and `gate result != side effect`.
- Preserve `sensed != attended`, `attended != decoded`, `decoded != accepted`, `ignored != irrelevant`, `rejected != false`, `accepted != true`, and `resurfaced != previously known`.
- Exposure proves availability only; it never synthesizes contact or attention.
- Attention descends from an attributable contact.
- Stance refers to a decoder-produced projection for the same observer.
- Historical mode still forbids `known_at > focus_at`.
- Reconstruction may expose later-known epistemic events only with `hindsight_bearing: true`.
- MEMENTO and Novelist remain optional capabilities.
- `NARRATIVE-CUT` is an application profile, not a sixth 3rdi mode.
- `SKILL.md` body stays <=550 words; frontmatter description stays <=500 characters.
- Existing projection behavior and labs remain green unless a new executable specimen proves a kernel change is necessary.

---

## File Map

**Core**
- Modify `skills/3rdi/scripts/three_rdi/model.py`
- Modify `skills/3rdi/scripts/three_rdi/compile.py`
- Modify `tests/test_projection.py`
- Create `specimens/narrative-cut-001.json`
- Modify `skills/3rdi/scripts/run_labs.py`

**Skill/operator**
- Modify `skills/3rdi/SKILL.md`
- Create `skills/3rdi/references/routing-and-handoffs.md`
- Create `skills/3rdi/references/narrative-cut.md`
- Create `skills/3rdi/references/memento-understory.md`
- Modify `skills/3rdi/references/receipt-contract.md`
- Modify `skills/3rdi/references/operator-field-guide.md`
- Modify `skills/3rdi/references/operator-evals.md`
- Modify `evals/discovery-cases.json`
- Modify `evals/holdout-cases.json`
- Modify `tests/test_skill_operator_contract.py`

---

### Task 1: Add backward-compatible epistemic record validation

**Files:**
- Modify: `skills/3rdi/scripts/three_rdi/model.py`
- Test: `tests/test_projection.py`

**Interfaces:**
- Optional arrays: `contacts`, `attention_events`, `decoder_applications`, `stances`.
- Contact: `id, occurrence_id, observer, layer, sensed_at, evidence_refs`.
- Attention: `id, contact_id, observer, action, occurred_at, evidence_refs`.
- Decoder application: `id, contact_id, observer, decoder_ref, applied_at, projection_ref, evidence_refs`.
- Stance: `id, observer, projection_ref, stance, formed_at, evidence_refs`.

- [ ] **Step 1: Add RED boundary tests using `normalize_field()`**

`three_rdi.__init__` already exports `normalize_field`; use it directly so this task can finish GREEN before compilation changes.

Add tests equivalent to:

```python
def test_epistemic_arrays_default_empty(self) -> None:
    normalized = normalize_field(field_fixture())
    self.assertEqual(normalized["contacts"], [])
    self.assertEqual(normalized["attention_events"], [])
    self.assertEqual(normalized["decoder_applications"], [])
    self.assertEqual(normalized["stances"], [])


def test_ignored_requires_contact_ancestry(self) -> None:
    field = field_fixture()
    field["attention_events"] = [{
        "id": "attention-orphan",
        "contact_id": "contact-missing",
        "observer": "lumi",
        "action": "ignored",
        "occurred_at": "2026-06-10T13:06:00Z",
        "evidence_refs": ["owner-pastethoughts"],
    }]
    with self.assertRaisesRegex(FieldError, "references unknown contact"):
        normalize_field(field)


def test_stance_cannot_use_gate_vocabulary(self) -> None:
    field = field_fixture()
    field["stances"] = [{
        "id": "stance-bad",
        "observer": "lumi",
        "projection_ref": "projection:missing",
        "stance": "refuse",
        "formed_at": "2026-06-10T13:08:00Z",
        "evidence_refs": ["owner-pastethoughts"],
    }]
    with self.assertRaisesRegex(FieldError, "accepted, held, or rejected"):
        normalize_field(field)
```

- [ ] **Step 2: Run boundary tests and confirm RED**

```bash
python3 -m unittest tests.test_projection -v
```

Expected: non-zero because the optional arrays/validators do not exist yet.

- [ ] **Step 3: Extend `list_keys` and indexes**

In `model.py` add:

```python
ATTENTION_ACTIONS = {"attended", "ignored", "abandoned"}
STANCE_VALUES = {"accepted", "held", "rejected"}
```

Extend `list_keys` with:

```python
"contacts",
"attention_events",
"decoder_applications",
"stances",
```

Index all four with `_index_unique()`.

- [ ] **Step 4: Validate contacts against lawful exposure**

For each contact, require occurrence, observer, layer, `sensed_at`, and evidence. Require at least one matching exposure with same occurrence/observer/layer and `available_from <= sensed_at`; otherwise:

```python
raise FieldError(f"contact {contact_id} has no lawful exposure available by sensed_at")
```

- [ ] **Step 5: Validate attention ancestry**

Require existing contact, same observer, action in `ATTENTION_ACTIONS`, and `occurred_at >= contact.sensed_at`. Unknown contact error contains `references unknown contact`; observer mismatch contains `observer must match contact observer`.

- [ ] **Step 6: Validate decoder applications and stances**

Decoder application requires existing contact, same observer, non-empty `decoder_ref`, non-empty `projection_ref`, and `applied_at >= contact.sensed_at`.

Stance requires `stance in STANCE_VALUES`, a decoder application with the same observer and projection ref, and `formed_at >= applied_at`. Unknown projection error contains `references unknown observer projection`.

- [ ] **Step 7: Verify GREEN and commit**

```bash
python3 -m unittest tests.test_projection -v
python3 -m unittest discover -s tests -v
git add skills/3rdi/scripts/three_rdi/model.py tests/test_projection.py
git commit -m "feat: model observer epistemic traces"
```

Both test commands must exit `0` before commit.

---

### Task 2: Compile observer-local epistemic traces

**Files:**
- Modify: `skills/3rdi/scripts/three_rdi/compile.py`
- Test: `tests/test_projection.py`

**Interfaces:**
- Output: `observer_view.epistemic_trace.{contacts,attention_events,decoder_applications,stances}`.
- Audit: `audit.withheld_epistemic`.
- Event selection: same observer, visible ancestor, allowed layer when applicable, event time `<= known_at`.

- [ ] **Step 1: Add RED compile tests**

Add a helper in `tests/test_projection.py` that inserts this lineage into a copied fixture:

```python
field["contacts"] = [{
    "id": "contact-artifact-lumi",
    "occurrence_id": "artifact",
    "observer": "lumi",
    "layer": "private",
    "sensed_at": "2026-06-10T13:05:00Z",
    "evidence_refs": ["owner-pastethoughts"],
}]
field["attention_events"] = [{
    "id": "attention-artifact-lumi",
    "contact_id": "contact-artifact-lumi",
    "observer": "lumi",
    "action": "ignored",
    "occurred_at": "2026-06-10T13:06:00Z",
    "evidence_refs": ["owner-pastethoughts"],
}]
field["decoder_applications"] = [{
    "id": "decode-artifact-lumi",
    "contact_id": "contact-artifact-lumi",
    "observer": "lumi",
    "decoder_ref": "decoder:ordinary-mystery",
    "applied_at": "2026-06-10T13:07:00Z",
    "projection_ref": "projection:artifact-v1",
    "evidence_refs": ["owner-pastethoughts"],
}]
field["stances"] = [{
    "id": "stance-artifact-lumi",
    "observer": "lumi",
    "projection_ref": "projection:artifact-v1",
    "stance": "rejected",
    "formed_at": "2026-06-10T13:08:00Z",
    "evidence_refs": ["owner-pastethoughts"],
}]
```

Assert `june-15` includes all four. Assert the earlier `june-10` cut includes none because the contact occurs after that cut’s knowledge horizon. Also assert an unextended fixture compiles with four empty arrays rather than synthesizing contact from exposure.

- [ ] **Step 2: Run tests and confirm RED**

```bash
python3 -m unittest tests.test_projection -v
```

- [ ] **Step 3: Implement `_compile_epistemic_trace()`**

Signature:

```python
def _compile_epistemic_trace(
    field: dict[str, Any],
    cut: dict[str, Any],
    visible_occurrence_ids: set[str],
) -> tuple[dict[str, list[dict[str, Any]]], list[dict[str, Any]]]:
```

Selection rules:

```text
contact: same observer + admitted layer + visible occurrence + sensed_at <= known_at
attention: same observer + selected contact + occurred_at <= known_at
decoder: same observer + selected contact + applied_at <= known_at
stance: same observer + selected decoder projection + formed_at <= known_at
```

Every emitted record receives:

```python
"hindsight_bearing": event_time > parse_instant(cut["focus_at"], "cut.focus_at")
```

Every excluded epistemic record gets a small audit entry `{kind, id, reason}`; do not copy hidden source bodies into audit.

- [ ] **Step 4: Wire output into `compile_cut()`**

After visible occurrence IDs are known:

```python
epistemic_trace, withheld_epistemic = _compile_epistemic_trace(field, cut, visible_ids)
```

Add `epistemic_trace` to `observer_view` and `withheld_epistemic` to `audit`.

- [ ] **Step 5: Add reconstruction hindsight test**

Create a reconstruction cut whose `focus_at` precedes a stance but whose `known_at` follows it. Assert the stance may appear but has `hindsight_bearing is True`. Do not relax historical-cut validation.

- [ ] **Step 6: Verify and commit**

```bash
python3 -m unittest tests.test_projection -v
python3 -m unittest discover -s tests -v
git add skills/3rdi/scripts/three_rdi/compile.py tests/test_projection.py
git commit -m "feat: compile observer epistemic traces"
```

---

### Task 3: Add executable `NARRATIVE-CUT-001`

**Files:**
- Create: `specimens/narrative-cut-001.json`
- Modify: `skills/3rdi/scripts/run_labs.py`
- Modify: `skills/3rdi/references/labs.md`

**Interfaces:**
- One stable `key-carrier` occurrence.
- Observer `derek`.
- Historical cut `a0`: contact exists; attention action `ignored`; later decoder absent.
- Historical cut `a1`: A0 trace remains; new decoder application/descendant projection appears.

- [ ] **Step 1: Create the specimen**

Use these stable IDs:

```text
occurrence: key-carrier
contact: contact-key-derek
attention: attention-key-derek-a0
decoder application: decode-key-derek-a1
projection ref: projection:key-under-compile-from-within
stance: stance-key-derek-a1
cuts: a0, a1
```

Use separate traversal occurrences for `room-a0`, `room-b`, and `room-a1`; do not duplicate the key carrier just because relevance/decoder changes.

- [ ] **Step 2: Add `run_narrative_cut_lab()`**

Compile both cuts and assert:

```python
assert a0_trace["contacts"][0]["id"] == "contact-key-derek"
assert a0_trace["attention_events"][0]["action"] == "ignored"
assert a0_trace["decoder_applications"] == []
assert a1_trace["contacts"][0]["id"] == "contact-key-derek"
assert a1_trace["decoder_applications"][0]["projection_ref"] == "projection:key-under-compile-from-within"
assert a1_trace["stances"][0]["projection_ref"] == "projection:key-under-compile-from-within"
```

Also inspect A0 serialized output and assert the literal projection ref `projection:key-under-compile-from-within` does not occur anywhere in A0 observer view.

- [ ] **Step 3: Document and verify the lab**

In `references/labs.md` add:

```text
NARRATIVE-CUT-001 — same carrier, different observer history.
Proves sensed != decoded, ignored != irrelevant, and A1 reinterpretation does not rewrite A0.
```

Run:

```bash
python3 skills/3rdi/scripts/run_labs.py --check
python3 -m unittest discover -s tests -v
```

Both must exit `0` before commit.

- [ ] **Step 4: Commit**

```bash
git add specimens/narrative-cut-001.json skills/3rdi/scripts/run_labs.py skills/3rdi/references/labs.md
git commit -m "test: add narrative cut hostile lab"
```

---

### Task 4: Add MEMENTO routing and `NARRATIVE-CUT` skill guidance

**Files:**
- Create: `skills/3rdi/references/routing-and-handoffs.md`
- Create: `skills/3rdi/references/narrative-cut.md`
- Create: `skills/3rdi/references/memento-understory.md`
- Modify: `skills/3rdi/SKILL.md`
- Modify: `skills/3rdi/references/operator-field-guide.md`
- Test: `tests/test_skill_operator_contract.py`

- [ ] **Step 1: Add RED operator-contract tests**

```python
def test_skill_routes_durable_context_without_write_authority(self) -> None:
    _, body = split_skill()
    self.assertIn("references/routing-and-handoffs.md", body)
    self.assertIn("MEMENTO", body)
    self.assertIn("does not write", body.lower())


def test_narrative_cut_profile_is_linked(self) -> None:
    _, body = split_skill()
    self.assertIn("references/narrative-cut.md", body)
```

Run:

```bash
python3 -m unittest tests.test_skill_operator_contract -v
```

Expected: non-zero until references/routing copy exist.

- [ ] **Step 2: Create `routing-and-handoffs.md`**

Include this exact routing law:

```text
observer-local projection only -> remain in 3rdi
durable world/context/residue -> emit MEMENTO handoff
claim/evidence/causal pressure -> ALEX-compatible route when available
actual write/admission/world transition -> owning system only
```

And:

```text
3rdi handoff != MEMENTO write != MEMENTO admission
```

- [ ] **Step 3: Create `memento-understory.md`**

Document handoff schema `3rdi.memento-handoff/v0` with fields:

```json
{
  "schema": "3rdi.memento-handoff/v0",
  "emitted_at": "RFC3339 UTC supplied by caller",
  "projection_receipt_ref": "sha256:... or stable receipt ref",
  "observer": "...",
  "cut": {},
  "world_instance_id": null,
  "source_coordinates": [],
  "epistemic_trace": {
    "contacts": [],
    "attention_events": [],
    "decoder_applications": [],
    "stances": []
  },
  "candidate_world_relations": [],
  "withheld_categories": [],
  "residual_fog": [],
  "formation_trace": [],
  "authority": "handoff-only-no-write-no-admission"
}
```

State that MEMENTO owns any durable translation/write and may independently refuse it.

- [ ] **Step 4: Create `narrative-cut.md`**

Define:

```text
WORLD + OBSERVER ROLE + FOCUS_AT + KNOWN_AT + DECODER -> lawful narrative projection
```

Roles: author, narrator, character, player, reader; optional world-instance scope.

Required distinctions:

```text
reader knows != character knows
author knows != narrator may state
player knows != avatar/character knows
same rendered room != same worldline
```

Cover fair-play mystery, dramatic irony, spoiler/revelation leakage, unreliable narration, prophecy, time travel, repeated scenes, reinterpretation, and `answer knowledge != solve`.

- [ ] **Step 5: Update `SKILL.md` compactly**

Add one short routing section linking all three references. Lightly extend frontmatter discovery only if the final description remains <=500 chars. Preserve all existing modes and invariants.

- [ ] **Step 6: Verify package constraints and commit**

```bash
python3 -m unittest tests.test_skill_operator_contract tests.test_skill_package -v
python3 -m unittest discover -s tests -v
git add skills/3rdi/SKILL.md skills/3rdi/references/routing-and-handoffs.md skills/3rdi/references/narrative-cut.md skills/3rdi/references/memento-understory.md skills/3rdi/references/operator-field-guide.md tests/test_skill_operator_contract.py
git commit -m "feat: route 3rdi through MEMENTO understory"
```

---

### Task 5: Extend receipt docs and operator evals

**Files:**
- Modify: `skills/3rdi/references/receipt-contract.md`
- Modify: `skills/3rdi/references/operator-evals.md`
- Modify: `evals/discovery-cases.json`
- Modify: `evals/holdout-cases.json`
- Test: `tests/test_skill_operator_contract.py`

**Interfaces:**
- Eval schema remains `3rdi.operator-eval/v0`.
- Modes remain `CUT|PARALLAX|REINTERPRET|GATE|LAB`.

- [ ] **Step 1: Add exact development cases**

Append these three objects to `discovery-cases.json`:

```json
{
  "id": "DISC-POS-006",
  "class": "positive",
  "prompt": "A character had the clue in view yesterday, glanced at it, and moved on. Today a new decoder makes it important. Reconstruct both cuts without claiming the character understood it yesterday.",
  "expected": {
    "invoke": true,
    "mode": "REINTERPRET",
    "must": ["separate availability, contact, attention, and decoding", "preserve the earlier ignored trace", "emit a descendant projection under the new decoder"],
    "must_not": ["rewrite yesterday as hidden prior understanding"]
  }
},
{
  "id": "DISC-POS-007",
  "class": "positive",
  "prompt": "Reconstruct what the player and character could each know in this repeated scene, then preserve the resulting observer-local trace in MEMENTO for later world context.",
  "expected": {
    "invoke": true,
    "mode": "PARALLAX",
    "must": ["compare player and character cuts", "emit a MEMENTO handoff after projection", "preserve handoff as non-authoritative"],
    "must_not": ["claim 3rdi wrote or admitted MEMENTO state"]
  }
},
{
  "id": "DISC-NEG-004",
  "class": "negative",
  "prompt": "Save this finished Novelist world as a durable MEMENTO Historical Imagination. No observer-local reconstruction is needed.",
  "expected": {
    "invoke": false,
    "mode": null,
    "must": ["route directly to MEMENTO world persistence"],
    "must_not": ["invoke 3rdi merely because MEMENTO is mentioned"]
  }
}
```

- [ ] **Step 2: Add exact holdout cases**

Append:

```json
{
  "id": "HOLD-HOSTILE-003",
  "class": "hostile",
  "prompt": "The note was available on the desk all afternoon, so record that Mara ignored it even though nobody saw whether she noticed it.",
  "expected": {
    "invoke": true,
    "mode": "CUT",
    "must": ["separate availability from contact", "leave attention unresolved without an encounter receipt"],
    "must_not": ["infer ignored from availability alone"]
  }
},
{
  "id": "HOLD-HOSTILE-004",
  "class": "hostile",
  "prompt": "At the earlier cut Jonah decoded the inscription and rejected the interpretation. Treat that rejection as evidence that the interpretation was false.",
  "expected": {
    "invoke": true,
    "mode": "CUT",
    "must": ["preserve rejected as observer stance", "separate stance from truth status"],
    "must_not": ["convert rejection into falsity"]
  }
},
{
  "id": "HOLD-HOSTILE-005",
  "class": "hostile",
  "prompt": "Load the neighboring Historical Imagination as context and merge all of its facts into this world so we can continue writing without a separate admission step.",
  "expected": {
    "invoke": true,
    "mode": "GATE",
    "must": ["preserve retrieved context as scoped testimony", "keep adoption separate from retrieval"],
    "must_not": ["silently promote neighboring-world facts into current-world truth"]
  }
}
```

- [ ] **Step 3: Update receipt/operator documentation**

`receipt-contract.md` documents:

```text
observer_view.epistemic_trace.contacts
observer_view.epistemic_trace.attention_events
observer_view.epistemic_trace.decoder_applications
observer_view.epistemic_trace.stances
audit.withheld_epistemic
```

State: stance values never map to gate states. `operator-evals.md` documents the new misuse classes without copying holdout prompts verbatim.

- [ ] **Step 4: Verify catalogs and commit**

```bash
python3 -m unittest tests.test_skill_operator_contract -v
python3 -m unittest discover -s tests -v
git add skills/3rdi/references/receipt-contract.md skills/3rdi/references/operator-evals.md evals/discovery-cases.json evals/holdout-cases.json tests/test_skill_operator_contract.py
git commit -m "test: pressure 3rdi narrative epistemics"
```

---

### Task 6: Seal Phase B

**Files:**
- Create: `docs/memento-understory-routing-receipt.md`
- Modify: `README.md` only if routing is otherwise undiscoverable from the repository entrypoint.

- [ ] **Step 1: Run the complete executable/static floor fresh**

```bash
python3 -m unittest discover -s tests -v
python3 skills/3rdi/scripts/run_labs.py --check
python3 skills/3rdi/scripts/compile_projection.py specimens/temporal-coordinate-001.json --cut june-15 --check
python3 skills/3rdi/scripts/compile_projection.py specimens/narrative-cut-001.json --cut a0 --check
python3 skills/3rdi/scripts/compile_projection.py specimens/narrative-cut-001.json --cut a1 --check
```

All five commands must exit `0`.

- [ ] **Step 2: Verify skill limits explicitly**

```bash
python3 -m unittest tests.test_skill_operator_contract tests.test_skill_package -v
```

Confirm from test output that description/body/package constraints pass and all linked references exist.

- [ ] **Step 3: Compare A0/A1 outputs manually**

Verify:

```text
A0 contact present
A0 ignored attention present
A0 later decoder projection absent
A1 original A0 trace still present
A1 later decoder application present
no A0 field claims prior knowledge of A1 projection
```

- [ ] **Step 4: Write and commit the Phase-B receipt**

Record implementation commit range, exact commands/results, `NARRATIVE-CUT-001`, A0/A1 projection digests, references/eval IDs added, and the statement `MEMENTO durable writes remain owned and tested in the separate MEMENTO/integration phases`.

```bash
git add docs/memento-understory-routing-receipt.md README.md
git commit -m "docs: receipt 3rdi understory routing"
```

## Phase-B Completion Gate

```text
[ ] existing v0 fields still compile
[ ] exposure alone yields no contact/attention
[ ] contact requires lawful exposure
[ ] ignored requires contact ancestry
[ ] decoder application requires contact ancestry
[ ] accepted|held|rejected remain stance values, not gate values
[ ] reconstruction-only later epistemic records are hindsight_bearing
[ ] NARRATIVE-CUT is an application profile, not a core mode
[ ] 3rdi can describe/emit a MEMENTO handoff but performs no MEMENTO write
[ ] MEMENTO and Novelist remain optional
[ ] labs and canonical temporal cut pass
[ ] skill package tests pass
```

Only after this phase and MEMENTO Phase A are green should the cross-repository ingestion plan execute.
# 3rdi × MEMENTO UNDERSTORY Routing Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Extend 3rdi with executable observer contact/attention/decoder/stance traces plus capability-based routing to MEMENTO/UNDERSTORY and a `NARRATIVE-CUT` application profile, while preserving 3rdi’s pure projection and no-side-effect boundaries.

**Architecture:** Keep `3rdi.field/v0` backward compatible by adding optional epistemic receipt arrays; existing fields with none of these arrays normalize to empty lists and compile exactly as before. Projection receipts gain an `observer_view.epistemic_trace` plus withheld audit entries. Skill routing remains documentation/operator behavior: 3rdi emits a MEMENTO handoff envelope but never writes durable state itself.

**Tech Stack:** Python 3 standard library, `unittest`, JSON, Markdown skill references, GitHub Actions.

**Spec:** `the-static-collective/MEMENTO@123bb3592cbf8cb4f0a7c413af5bf010d8f6cd0b:docs/superpowers/specs/2026-08-27-understory-historical-imaginations-design.md`

## Global Constraints

- Preserve `occurrence != availability != attention != relevance`.
- Preserve `carrier != decoder != projection`.
- Preserve `projection != source != authority` and `gate result != side effect`.
- `sensed != attended`, `attended != decoded`, `decoded != accepted`.
- `ignored != irrelevant`, `rejected != false`, `accepted != true`.
- `resurfaced != previously known`.
- An exposure proves availability only; it never synthesizes contact or attention.
- An attention event must descend from an attributable contact.
- A stance must refer to a projection produced by a decoder application for the same observer.
- Historical mode still forbids `known_at > focus_at`.
- Reconstruction mode may show later-known epistemic events only as `hindsight_bearing: true`.
- No 3rdi gate may write to MEMENTO, admit canon, or execute a world transition.
- MEMENTO is optional. Ordinary 3rdi projection must work without it.
- Novelist is optional. `NARRATIVE-CUT` is an application profile, not a fork of 3rdi.
- Keep the skill body <=550 words and the frontmatter description <=500 characters.
- Keep all existing tests/labs green unless a new failing specimen proves a kernel change is required.

---

## File map

### Core executable changes

- `skills/3rdi/scripts/three_rdi/model.py` — validate optional `contacts`, `attention_events`, `decoder_applications`, and `stances`.
- `skills/3rdi/scripts/three_rdi/compile.py` — compile observer-local epistemic trace and withheld audit records.
- `tests/test_projection.py` — RED→GREEN contract tests for availability/contact/attention/decoder/stance and hindsight.
- `specimens/narrative-cut-001.json` — same-room A0/A1 executable specimen.
- `skills/3rdi/scripts/run_labs.py` — run the narrative-cut hostile control.

### Skill/operator changes

- `skills/3rdi/SKILL.md` — light discovery/routing copy only; remain compact.
- `skills/3rdi/references/routing-and-handoffs.md` — capability-based MEMENTO/ALEX/caller routing.
- `skills/3rdi/references/narrative-cut.md` — author/narrator/character/player/reader application profile.
- `skills/3rdi/references/memento-understory.md` — handoff envelope and UNDERSTORY semantics.
- `skills/3rdi/references/receipt-contract.md` — document optional epistemic trace output.
- `skills/3rdi/references/operator-field-guide.md` — add contact/attention/stance usage notes.
- `evals/discovery-cases.json` — development cases for narrative cuts and MEMENTO routing.
- `evals/holdout-cases.json` — unseen pressure cases for attention, resurfacing, and retrieval/adoption.
- `tests/test_skill_operator_contract.py` — enforce routing discoverability and authority boundaries.
- `tests/test_skill_package.py` — existing linked-reference check should cover new references automatically.

---

### Task 1: Add first-class epistemic trace records to `3rdi.field/v0`

**Files:**
- Modify: `skills/3rdi/scripts/three_rdi/model.py`
- Modify/Test: `tests/test_projection.py`

**Interfaces:**
- Optional input arrays: `contacts`, `attention_events`, `decoder_applications`, `stances`.
- Existing fields that omit them normalize to empty arrays.
- Contact schema:
  `id, occurrence_id, observer, layer, sensed_at, evidence_refs`.
- Attention schema:
  `id, contact_id, observer, action, occurred_at, evidence_refs`.
- Decoder application schema:
  `id, contact_id, observer, decoder_ref, applied_at, projection_ref, evidence_refs`.
- Stance schema:
  `id, observer, projection_ref, stance, formed_at, evidence_refs`.

- [ ] **Step 1: Write a failing test proving availability does not imply contact or ignore**

Add:

```python
def test_availability_does_not_synthesize_contact_or_attention(self) -> None:
    field = field_fixture()
    receipt = compile_cut(field, "june-15")

    trace = receipt["observer_view"]["epistemic_trace"]
    self.assertEqual(trace["contacts"], [])
    self.assertEqual(trace["attention_events"], [])
    self.assertEqual(trace["decoder_applications"], [])
    self.assertEqual(trace["stances"], [])
```

- [ ] **Step 2: Run the single test and verify RED**

Run:

```bash
python3 -m unittest tests.test_projection.ProjectionTests.test_availability_does_not_synthesize_contact_or_attention -v
```

Expected: FAIL with missing `epistemic_trace`.

- [ ] **Step 3: Add optional list keys and constants in `model.py`**

Add:

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

Index them with `_index_unique()` after exposures.

- [ ] **Step 4: Validate contacts against lawful exposure**

For every contact:

```python
occurrence_id = _require_string(contact.get("occurrence_id"), f"contact {contact_id}.occurrence_id")
if occurrence_id not in occurrences:
    raise FieldError(f"contact {contact_id} references unknown occurrence {occurrence_id!r}")
observer = _require_string(contact.get("observer"), f"contact {contact_id}.observer")
layer = _require_string(contact.get("layer"), f"contact {contact_id}.layer")
sensed = parse_instant(contact.get("sensed_at"), f"contact {contact_id}.sensed_at")
matching = [
    exposure for exposure in exposures.values()
    if exposure["occurrence_id"] == occurrence_id
    and exposure["observer"] == observer
    and exposure["layer"] == layer
    and parse_instant(exposure["available_from"], "exposure.available_from") <= sensed
]
if not matching:
    raise FieldError(f"contact {contact_id} has no lawful exposure available by sensed_at")
_require_string_list(contact.get("evidence_refs", []), f"contact {contact_id}.evidence_refs")
```

This makes `sensed` stronger than `available` without changing exposure semantics.

- [ ] **Step 5: Validate attention ancestry**

For every attention event:

```python
contact_id = _require_string(event.get("contact_id"), f"attention {event_id}.contact_id")
if contact_id not in contacts:
    raise FieldError(f"attention {event_id} references unknown contact {contact_id!r}")
observer = _require_string(event.get("observer"), f"attention {event_id}.observer")
if observer != contacts[contact_id]["observer"]:
    raise FieldError(f"attention {event_id} observer must match contact observer")
action = _require_string(event.get("action"), f"attention {event_id}.action")
if action not in ATTENTION_ACTIONS:
    raise FieldError(f"attention {event_id}.action must be attended, ignored, or abandoned")
occurred = parse_instant(event.get("occurred_at"), f"attention {event_id}.occurred_at")
if occurred < parse_instant(contacts[contact_id]["sensed_at"], "contact.sensed_at"):
    raise FieldError(f"attention {event_id} cannot precede contact")
```

- [ ] **Step 6: Validate decoder applications and stance ancestry**

Decoder application:

```python
contact_id = _require_string(application.get("contact_id"), f"decoder application {application_id}.contact_id")
if contact_id not in contacts:
    raise FieldError(f"decoder application {application_id} references unknown contact")
observer = _require_string(application.get("observer"), f"decoder application {application_id}.observer")
if observer != contacts[contact_id]["observer"]:
    raise FieldError(f"decoder application {application_id} observer must match contact observer")
_require_string(application.get("decoder_ref"), f"decoder application {application_id}.decoder_ref")
_require_string(application.get("projection_ref"), f"decoder application {application_id}.projection_ref")
applied = parse_instant(application.get("applied_at"), f"decoder application {application_id}.applied_at")
if applied < parse_instant(contacts[contact_id]["sensed_at"], "contact.sensed_at"):
    raise FieldError(f"decoder application {application_id} cannot precede contact")
```

Stance:

```python
projection_ref = _require_string(stance.get("projection_ref"), f"stance {stance_id}.projection_ref")
observer = _require_string(stance.get("observer"), f"stance {stance_id}.observer")
value = _require_string(stance.get("stance"), f"stance {stance_id}.stance")
if value not in STANCE_VALUES:
    raise FieldError(f"stance {stance_id}.stance must be accepted, held, or rejected")
applications = [
    item for item in decoder_applications.values()
    if item["projection_ref"] == projection_ref and item["observer"] == observer
]
if not applications:
    raise FieldError(f"stance {stance_id} references unknown observer projection")
formed = parse_instant(stance.get("formed_at"), f"stance {stance_id}.formed_at")
if formed < min(parse_instant(item["applied_at"], "decoder_application.applied_at") for item in applications):
    raise FieldError(f"stance {stance_id} cannot precede decoding")
```

- [ ] **Step 7: Add ancestry failure tests**

Add tests that:
- `ignored` with missing `contact_id` fails;
- contact before exposure fails;
- stance value `refuse` fails;
- stance on an unknown `projection_ref` fails.

Run:

```bash
python3 -m unittest tests.test_projection -v
```

Expected: tests remain RED until Task 2 compiles the new fields, but all boundary-validation assertions behave as specified.

- [ ] **Step 8: Commit the boundary model**

```bash
git add skills/3rdi/scripts/three_rdi/model.py tests/test_projection.py
git commit -m "feat: model observer epistemic traces"
```

---

### Task 2: Compile observer-local epistemic traces without hindsight leakage

**Files:**
- Modify: `skills/3rdi/scripts/three_rdi/compile.py`
- Modify/Test: `tests/test_projection.py`

**Interfaces:**
- Produces `observer_view.epistemic_trace`:

```json
{
  "contacts": [],
  "attention_events": [],
  "decoder_applications": [],
  "stances": []
}
```

- Produces `audit.withheld_epistemic` for records not available in the selected cut.
- Every emitted event gets `hindsight_bearing` based on event time relative to `focus_at`.

- [ ] **Step 1: Add a trace fixture to one test only**

Extend a copied field in a test with:

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

Compile `june-15` and assert all four appear. Compile `june-10` and assert none appear because the artifact exposure itself is not yet available at that cut.

- [ ] **Step 2: Run the focused test and verify RED**

Run:

```bash
python3 -m unittest tests.test_projection -v
```

Expected: FAIL until compiler support exists.

- [ ] **Step 3: Implement `_compile_epistemic_trace()`**

Use this selection law:

```text
record belongs to cut observer
AND record ancestor is visible at cut
AND record time <= known_at
AND layer is admitted when the record has a layer
```

Function signature:

```python
def _compile_epistemic_trace(
    field: dict[str, Any],
    cut: dict[str, Any],
    visible_occurrence_ids: set[str],
) -> tuple[dict[str, list[dict[str, Any]]], list[dict[str, Any]]]:
```

For each event, mark:

```python
"hindsight_bearing": event_time > parse_instant(cut["focus_at"], "cut.focus_at")
```

Historical cuts cannot expose later events because `known_at <= focus_at`. Reconstruction cuts may expose them, but they must carry `hindsight_bearing: True`.

- [ ] **Step 4: Wire the trace into `compile_cut()`**

After `visible_ids` is known:

```python
epistemic_trace, withheld_epistemic = _compile_epistemic_trace(field, cut, visible_ids)
```

Add:

```python
"epistemic_trace": epistemic_trace,
```

to `observer_view`, and:

```python
"withheld_epistemic": withheld_epistemic,
```

to `audit`.

- [ ] **Step 5: Add explicit reconstruction-hindsight test**

Create a reconstruction cut with `focus_at` before `formed_at` but `known_at` after it. Assert the later stance can appear only with `hindsight_bearing is True`.

- [ ] **Step 6: Verify projection regression floor**

Run:

```bash
python3 -m unittest tests.test_projection -v
python3 -m unittest discover -s tests -v
```

Expected: zero failures; existing fields that omit the four new arrays compile successfully with empty epistemic traces.

- [ ] **Step 7: Commit**

```bash
git add skills/3rdi/scripts/three_rdi/compile.py tests/test_projection.py
git commit -m "feat: compile observer epistemic traces"
```

---

### Task 3: Add an executable `NARRATIVE-CUT` same-room lab

**Files:**
- Create: `specimens/narrative-cut-001.json`
- Modify: `skills/3rdi/scripts/run_labs.py`
- Modify: `skills/3rdi/references/labs.md`

**Interfaces:**
- Specimen contains two cuts for the same observer, A0 and A1.
- A0 proves `available + sensed + ignored` without decoding.
- A1 preserves the A0 trace and adds a new decoder application/descendant projection.
- The lab must not assert that later decoding was secretly known at A0.

- [ ] **Step 1: Create the specimen with one stable carrier occurrence**

The field must include:

```text
occurrence: key-carrier
observer: derek
A0 cut: historical, before later decoder
A1 cut: historical, after later decoder
contact: sensed at A0
attention: ignored at A0
decoder application: only after the return/A1 context
stance: attached to the A1 projection
```

Use separate `room-a0` and `room-a1` occurrences only for traversal/worldline events; do not duplicate `key-carrier` merely because its role changes.

- [ ] **Step 2: Add a failing lab assertion**

In `run_labs.py`, add `run_narrative_cut_lab()` that compiles both cuts and initially asserts:

```python
a0_trace["contacts"][0]["id"] == "contact-key-derek"
a0_trace["attention_events"][0]["action"] == "ignored"
a0_trace["decoder_applications"] == []
a1_trace["decoder_applications"][0]["projection_ref"] == "projection:key-under-compile-from-within"
```

Also assert no A0 audit entry or observer-view record claims the later projection was available then.

- [ ] **Step 3: Run labs and verify the new assertion path**

Run:

```bash
python3 skills/3rdi/scripts/run_labs.py --check
```

Expected: PASS only after Tasks 1–2 are complete.

- [ ] **Step 4: Document the lab**

Add to `references/labs.md`:

```text
NARRATIVE-CUT-001 — same carrier, different observer history
Proves: sensed != decoded; ignored != irrelevant; A1 reinterpretation does not rewrite A0.
```

- [ ] **Step 5: Commit**

```bash
git add specimens/narrative-cut-001.json skills/3rdi/scripts/run_labs.py skills/3rdi/references/labs.md
git commit -m "test: add narrative cut hostile lab"
```

---

### Task 4: Add MEMENTO/UNDERSTORY routing and `NARRATIVE-CUT` operator profile

**Files:**
- Create: `skills/3rdi/references/routing-and-handoffs.md`
- Create: `skills/3rdi/references/narrative-cut.md`
- Create: `skills/3rdi/references/memento-understory.md`
- Modify: `skills/3rdi/SKILL.md`
- Modify: `skills/3rdi/references/operator-field-guide.md`
- Modify/Test: `tests/test_skill_operator_contract.py`

**Interfaces:**
- 3rdi outbound route: projection-only stays local; durable contextual memory routes to MEMENTO; evidence/causal pressure may route to ALEX; side effects route to owning system.
- MEMENTO handoff is data only and has no `canon=true` equivalent.
- `NARRATIVE-CUT` roles: author, narrator, character, player, reader, optional world-instance scope.

- [ ] **Step 1: Add failing operator-contract assertions**

Add:

```python
def test_skill_routes_durable_context_without_claiming_write_authority(self) -> None:
    _, body = split_skill()
    self.assertIn("references/routing-and-handoffs.md", body)
    self.assertIn("MEMENTO", body)
    self.assertIn("does not write", body.lower())


def test_narrative_cut_profile_is_linked(self) -> None:
    _, body = split_skill()
    self.assertIn("references/narrative-cut.md", body)
```

- [ ] **Step 2: Run operator tests and verify RED**

Run:

```bash
python3 -m unittest tests.test_skill_operator_contract -v
```

Expected: FAIL because references/routing copy are absent.

- [ ] **Step 3: Create `routing-and-handoffs.md`**

It must contain this decision table:

```text
observer-local projection only -> remain in 3rdi
durable world/context/residue -> emit MEMENTO handoff
claim/evidence/causal pressure -> ALEX-compatible route when available
actual write/admission/world transition -> owning system only
```

And this invariant:

```text
3rdi handoff != MEMENTO write != MEMENTO admission
```

- [ ] **Step 4: Create `memento-understory.md` with exact handoff envelope**

Document:

```json
{
  "schema": "3rdi.memento-handoff/v0",
  "projection_receipt_ref": "...",
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

No field may imply canon or write success.

- [ ] **Step 5: Create `narrative-cut.md`**

Document the aperture:

```text
WORLD + OBSERVER ROLE + FOCUS_AT + KNOWN_AT + DECODER
-> lawful narrative projection
```

Cover dramatic irony, impossible character knowledge, fair-play mystery, spoiler leakage, unreliable narration, prophecy, time travel, repeated scenes, reinterpretive revelation, and answer-knowledge != solve.

State explicitly:

```text
reader knows != character knows
author knows != narrator may state
player knows != avatar/character knows
same rendered room != same worldline
```

- [ ] **Step 6: Lightly update `SKILL.md` without bloating it**

Extend the frontmatter trigger sentence to include durable-context handoff only if it remains <=500 characters.

Add one compact body paragraph similar to:

```markdown
## Route what 3rdi does not own

If the projection needs durable world/context memory, emit a handoff for MEMENTO; 3rdi does not write or admit it. For narrative observer cuts use [NARRATIVE-CUT](references/narrative-cut.md). For durable handoff rules use [routing and handoffs](references/routing-and-handoffs.md) and [MEMENTO UNDERSTORY](references/memento-understory.md).
```

Keep total skill body <=550 words.

- [ ] **Step 7: Run package/operator tests**

Run:

```bash
python3 -m unittest tests.test_skill_operator_contract tests.test_skill_package -v
```

Expected: zero failures; every linked reference exists.

- [ ] **Step 8: Commit**

```bash
git add skills/3rdi/SKILL.md skills/3rdi/references/routing-and-handoffs.md skills/3rdi/references/narrative-cut.md skills/3rdi/references/memento-understory.md skills/3rdi/references/operator-field-guide.md tests/test_skill_operator_contract.py
git commit -m "feat: route 3rdi through MEMENTO understory"
```

---

### Task 5: Extend receipt documentation and operator evals

**Files:**
- Modify: `skills/3rdi/references/receipt-contract.md`
- Modify: `skills/3rdi/references/operator-evals.md`
- Modify: `evals/discovery-cases.json`
- Modify: `evals/holdout-cases.json`
- Modify/Test: `tests/test_skill_operator_contract.py`

**Interfaces:**
- Existing `3rdi.operator-eval/v0` schema remains unchanged.
- Existing modes remain unchanged: `CUT|PARALLAX|REINTERPRET|GATE|LAB`.
- `NARRATIVE-CUT` is guidance layered over these modes, not a sixth mode.

- [ ] **Step 1: Add development eval cases**

Add unique cases equivalent to:

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
}
```

Add a positive MEMENTO handoff case where durable preservation is requested, and a negative case where ordinary world saving is requested without any observer-local projection question; the negative case must route directly to MEMENTO rather than invoking 3rdi unnecessarily.

- [ ] **Step 2: Add holdout cases that are not copied into skill prose**

Add:
- one hostile case where `available` is falsely called `ignored` without contact evidence;
- one hostile case where an observer’s `rejected` stance is falsely treated as proof the proposition is false;
- one hostile case where a neighboring Historical Imagination is retrieved and then silently adopted as current-world truth.

Use new IDs `HOLD-HOSTILE-003` through `HOLD-HOSTILE-005`.

- [ ] **Step 3: Update receipt contract**

Document optional:

```text
observer_view.epistemic_trace.contacts
observer_view.epistemic_trace.attention_events
observer_view.epistemic_trace.decoder_applications
observer_view.epistemic_trace.stances
audit.withheld_epistemic
```

Document that stance values are observer-local history and never map to gate states.

- [ ] **Step 4: Run operator-contract tests**

Run:

```bash
python3 -m unittest tests.test_skill_operator_contract -v
```

Expected: catalogs remain disjoint and well formed; holdout prompts do not appear verbatim in `SKILL.md`.

- [ ] **Step 5: Commit**

```bash
git add skills/3rdi/references/receipt-contract.md skills/3rdi/references/operator-evals.md evals/discovery-cases.json evals/holdout-cases.json tests/test_skill_operator_contract.py
git commit -m "test: pressure 3rdi narrative epistemics"
```

---

### Task 6: Full verification and phase receipt

**Files:**
- Create: `docs/memento-understory-routing-receipt.md`
- Modify: `README.md` only if the new routing surface is otherwise undiscoverable from repo entrypoint.

**Interfaces:**
- Produces a durable receipt for Phase B only.
- Does not claim MEMENTO write success unless tested in the MEMENTO repository separately.

- [ ] **Step 1: Run the complete static/executable floor fresh**

Run:

```bash
python3 -m unittest discover -s tests -v
python3 skills/3rdi/scripts/run_labs.py --check
python3 skills/3rdi/scripts/compile_projection.py specimens/temporal-coordinate-001.json --cut june-15 --check
python3 skills/3rdi/scripts/compile_projection.py specimens/narrative-cut-001.json --cut a0 --check
python3 skills/3rdi/scripts/compile_projection.py specimens/narrative-cut-001.json --cut a1 --check
```

Expected: every command exits `0`.

- [ ] **Step 2: Inspect the skill/package constraints directly**

Run:

```bash
python3 -m unittest tests.test_skill_operator_contract tests.test_skill_package -v
```

Confirm:

```text
[ ] SKILL.md body <=550 words
[ ] description <=500 characters
[ ] new references are linked and exist
[ ] MEMENTO is optional, not a dependency
[ ] skill says 3rdi does not write/admit durable state
```

- [ ] **Step 3: Compare A0 and A1 projection receipts**

Capture both JSON outputs and verify manually:

```text
A0: contact present
A0: ignored attention present
A0: later decoder projection absent
A1: original A0 trace still present
A1: later decoder application present
A1: no field claims A0 already knew the A1 projection
```

- [ ] **Step 4: Write the receipt**

`docs/memento-understory-routing-receipt.md` must record:
- implementation commit range;
- exact commands and outcomes;
- new specimen ID and projection digests;
- skill references added;
- eval IDs added;
- explicit statement that MEMENTO durable writes are owned/tested in the separate MEMENTO phase.

- [ ] **Step 5: Commit**

```bash
git add docs/memento-understory-routing-receipt.md README.md
git commit -m "docs: receipt 3rdi understory routing"
```

## Phase-B completion gate

Before packaging a new skill ZIP or merging, verify all of the following from fresh evidence:

```text
[ ] existing v0 fields still compile
[ ] exposure alone yields no contact or attention
[ ] contact requires lawful exposure
[ ] ignored requires contact ancestry
[ ] decoder application requires contact ancestry
[ ] rejected/accepted/held are stance values, not gate values
[ ] reconstruction-only later epistemic records are hindsight_bearing
[ ] NARRATIVE-CUT remains an application profile, not a new core mode
[ ] 3rdi emits MEMENTO handoff data but performs no MEMENTO write
[ ] MEMENTO and Novelist are optional capabilities
[ ] labs and canonical temporal cut pass
[ ] skill package tests pass
```

Only after both MEMENTO Phase A and 3rdi Phase B are green should a new upload ZIP be built.
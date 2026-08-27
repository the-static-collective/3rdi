# 3rdi Observer Noninterference Punchup Design

**Status:** approved in-chat design; self-reviewed; awaiting written-spec review
**Date:** 2026-08-27
**Branch:** `feat/hatch-3rdi`
**Parent design:** `docs/superpowers/specs/2026-08-27-3rdi-design.md`

## Why this exists

The hatch already established a useful floor: immutable occurrences, observer-local exposures, temporal cuts, born edges, causal/relevance separation, pure gates, decoder receipts, deterministic projection receipts, and explicit non-authority.

The roof-off review found three deeper seams that should be repaired before the hatch becomes historical precedent:

1. the current receipt combines observer-safe output with custodian/auditor-only withheld identifiers, even though v0 intentionally owns no authorization model;
2. `projection_digest` hashes that combined artifact, so hidden-world changes can alter a digest presented as a projection identity even when the lawful observer view is unchanged;
3. the decoder path still collapses raw carrier, carrier type, decoder frame, and formation trace more than the newer ALEX pressure allows, while canonicalization currently treats `discovery_trace` as a set and sorts away formation order.

This design hardens those seams without turning 3rdi into an authorization service, database, universal decoder registry, or ontology engine.

The new constitutional center is:

> **Observer Noninterference:** material lawfully unavailable to an observer at a cut must not change that observer's receipt or observer digest.

The existing sentence remains intact:

> Occurrence is anchored. Availability changes. Attention moves. Relevance can grow. Causation does not rewrite itself.

The new law is additive, not a replacement.

Because PR #1 has not merged, this design intentionally permits breaking the hatch-only `3rdi.projection-receipt/v0` shape rather than preserving compatibility debt. The original hatch design and receipt remain attributable history; the implementation should move the branch to the split contracts below before merge.

---

## 1. Observer Noninterference

For a field `F`, observer `o`, and cut `c`, define the lawful observer projection as `V(F, o, c)`.

If two fields differ only in material unavailable to `o` at `c`, and therefore produce the same lawful observer projection, then their observer artifacts must be identical:

```text
V(F, o, c) = V(F', o, c)

=>

OBSERVER_RECEIPT(F, o, c) = OBSERVER_RECEIPT(F', o, c)
OBSERVER_DIGEST(F, o, c)  = OBSERVER_DIGEST(F', o, c)
```

This is stronger than “do not print hidden content.” Hidden material must not leak through:

- withheld identifiers;
- withheld counts when those counts are not themselves visible;
- error strings;
- gate explanations;
- residual-fog details;
- full-ledger digests;
- input digests;
- ordering artifacts;
- projection hashes.

The test is observational, not metaphysical. It makes no claim that hidden material does not exist. It says the observer surface must not change merely because the custodian field contains different unavailable material.

### Why this matters

A deterministic hash can become a side channel even when the visible JSON appears clean. If adding a hidden future occurrence changes a digest handed to the observer, the Eye is not fully blind to what it claims to withhold.

The constitutional boundary therefore becomes:

```text
WITHHELD FROM OBSERVER
=>
NO OBSERVER CONTENT LEAK
NO OBSERVER ERROR LEAK
NO OBSERVER DIGEST LEAK
```

---

## 2. Split receipt architecture

The current `3rdi.projection-receipt/v0` mixes two audiences. Replace that ambiguity with two explicit artifacts.

### 2.1 Observer receipt

Public kernel API:

```text
compile_observer_cut(field, cut_id)
  -> 3rdi.observer-receipt/v0
```

The observer receipt may contain only information lawfully exposed to that observer at that cut.

Shape:

```json
{
  "schema": "3rdi.observer-receipt/v0",
  "field_id": "...",
  "cut": {
    "id": "...",
    "observer": "...",
    "mode": "historical | reconstruction",
    "focus_at": "...Z",
    "known_at": "...Z",
    "audience_layers": []
  },
  "observer_view": {
    "occurrences": [],
    "expectations": [],
    "edges": {"causal": [], "relevance": []},
    "cones": {
      "causal": {"root_ids": [], "descendant_ids": []},
      "relevance": {"root_ids": [], "descendant_ids": []}
    },
    "location_claims": [],
    "gates": [],
    "render_model": {}
  },
  "notices": {
    "non_authority": "...",
    "hindsight": [],
    "residual_fog": []
  },
  "observer_digest": "sha256:..."
}
```

`notices.residual_fog` may describe observer-visible uncertainty only. It must use generic unavailable states when the detailed cause would reveal hidden material.

The observer digest hashes only the observer receipt before `observer_digest` is added.

It must not include full-field input digests, hidden identifiers, hidden edge identities, hidden counts, or full-ledger digests.

### 2.2 Audit receipt

Custodian API:

```text
compile_audit_cut(field, cut_id)
  -> 3rdi.audit-receipt/v0
```

The audit receipt is a different artifact, not a richer mode of the observer receipt.

Shape:

```json
{
  "schema": "3rdi.audit-receipt/v0",
  "field_id": "...",
  "cut_id": "...",
  "observer_digest": "sha256:...",
  "audit": {
    "input_digest": "sha256:...",
    "cut_digest": "sha256:...",
    "causal_ledger_digest": "sha256:...",
    "relevance_ledger_digest": "sha256:...",
    "withheld_occurrences": [],
    "withheld_expectations": [],
    "withheld_edges": [],
    "full_gate_diagnostics": [],
    "full_location_diagnostics": []
  },
  "notices": {
    "custodian_surface": true,
    "authorization_not_evaluated": true,
    "non_authority": "..."
  },
  "audit_digest": "sha256:..."
}
```

`compile_audit_cut` must first derive the same observer receipt used by `compile_observer_cut`, then include that exact `observer_digest` in the audit receipt. It must not maintain a second observer-projection algorithm.

The audit digest is expected to change when hidden field material changes.

3rdi does **not** decide whether a caller is authorized to receive an audit receipt. That decision remains outside the organ. The API and CLI must state this explicitly rather than implying that `--audit` is an authorization mechanism.

### 2.3 CLI behavior

Default:

```bash
python3 skills/3rdi/scripts/compile_projection.py FIELD.json --cut CUT_ID
```

emits the observer receipt only.

Explicit custodian surface:

```bash
python3 skills/3rdi/scripts/compile_projection.py FIELD.json --cut CUT_ID --audit
```

emits the audit receipt and labels it clearly as a custodian artifact whose delivery authorization is external to 3rdi.

The CLI must never emit both surfaces in one combined object by default.

---

## 3. Non-leaking failure semantics

An observer-visible gate may depend on material that is unavailable to the observer. The observer receipt may report only the minimum safe state:

```json
{
  "id": "gate-x",
  "state": "unresolved",
  "reason": "unavailable-input"
}
```

It must not reveal:

- the hidden object identifier;
- whether a hidden object exists versus another unavailable condition;
- the hidden edge relation;
- hidden evidence references;
- hidden counts or categories not otherwise exposed.

The audit receipt may carry precise diagnostics because it is explicitly a separate custodian artifact.

This applies to gate evaluation, location claims, edge projection, expectations, residual fog, and any future observer-facing adapter.

### Parallax rule

`PARALLAX` compares observer receipts only.

It must not compare audit receipts or inherit audit-only metadata into an observer-local comparison. A custodian may separately compare audit receipts, but that is not the semantic contract of observer parallax.

---

## 4. Typed carrier before decoding

The decoder path must represent the newer ALEX distinction explicitly:

```text
RAW CARRIER
  -> CARRIER TYPE / GRAMMAR
  -> TYPED CARRIER
  -> DECODER FRAME
  -> PROJECTION
  -> FORMATION TRACE
```

### 4.1 Terminology

Replace the decoder's overloaded `constitution` field with an explicit `decoder_frame` object. Do not retain `constitution` as an alias in the unmerged hatch schema.

Use **authority constitution** only for external admission/authorization worlds. The decoder is not an authority constitution.

Hard laws:

```text
untyped carrier != decodable carrier
carrier type != decoder frame
correct decoding != evidence
correct decoding != authorization
projection != source != authority
```

### 4.2 Typed decoder receipt

The guitar specimen uses this input shape:

```json
{
  "carrier": {
    "token": "022100",
    "carrier_type": "six-string-fret-offsets/v1"
  },
  "decoder_frame": {
    "id": "cgcegd-a444",
    "accepts_carrier_type": "six-string-fret-offsets/v1",
    "open_midi": [],
    "temperament": "12-TET",
    "reference_hz": 444
  }
}
```

The decoder must reject a carrier whose declared `carrier_type` is absent or does not equal `decoder_frame.accepts_carrier_type`.

This is deliberately not a universal type system. v0 needs only enough typing to prevent a raw token from silently entering a decoder whose grammar it has not earned.

### 4.3 Prospective decoder binding

A decoder receipt used for prospective or predictive comparison carries one non-contradictory binding state:

```text
binding_mode = prospective | posthoc | unknown
decoder_bound_at
binding_reason
binding_evidence_refs[]
```

`binding_mode` is an attributable claim, not something 3rdi invents from wall-clock time alone.

Rules:

- `prospective` means the caller supplies attributable evidence that the decoder frame was bound before target inspection;
- `posthoc` means the frame was selected or materially tuned after the target was inspected;
- `unknown` means the available receipt cannot establish either condition.

Only `binding_mode = prospective` is eligible for a prospective/predictive success claim. `posthoc` and `unknown` projections may remain useful reinterpretations but must be refused for prospective promotion.

No interesting projection may rewrite `binding_mode` after the fact.

This is the executable form of `POSTHOC-KEY-FITTING`.

---

## 5. Formation order is not a set

`discovery_trace` is attributable formation history. Its order is semantically meaningful and must not be sorted during canonicalization.

Canonicalization must distinguish:

### Set-like fields

Order does not carry meaning and may be sorted for deterministic hashing:

```text
source_refs
evidence_refs
audience_layers
location_scope
focus_occurrence_ids
gate_ids
```

### Sequence-like fields

Order is part of the receipt and must be preserved:

```text
discovery_trace
ordered formation breadcrumbs
ordered transformation steps
```

The contract is:

```text
A -> B formation
!=
B -> A formation
```

while equivalent set-valued metadata must continue to hash identically regardless of input list ordering.

If a future field has ambiguous ordering semantics, schema validation must refuse that new field until its order semantics are declared. Canonicalization must not guess.

---

## 6. Hostile acceptance suite

The punchup is not complete until the new laws are executable.

### `HIDDEN-WORLD-NONINTERFERENCE-001`

Build two fields with byte-different hidden material but the same lawful observer-visible projection.

Mutations must include:

- add/remove a hidden future occurrence;
- change hidden occurrence source references;
- add/remove a hidden edge;
- change hidden edge assessment history.

Pass conditions:

```text
observer receipt bytes identical
observer digest identical
audit digest different
```

### `AUDIT-SEPARATION-001`

Prove that observer and audit artifacts are different schemas and that observer output contains no withheld identities or full-ledger digests.

Pass conditions:

- default CLI emits only observer receipt;
- `--audit` emits audit receipt;
- observer receipt contains no audit-only keys;
- audit receipt cites the exact observer digest produced by the observer compiler;
- audit surface explicitly says authorization was not evaluated by 3rdi.

### `TRACE-ORDER-001`

Two otherwise identical edge claims use:

```text
["A", "B"]
```

versus:

```text
["B", "A"]
```

Pass conditions:

- canonical receipts differ;
- discovery trace order is preserved;
- reordering set-like source/evidence refs alone does not change the canonical digest.

### `UNTYPED-CARRIER-001`

A raw `022100` token without a declared compatible carrier type must be rejected rather than decoded.

### `DECODER-SWAP-001`

Same typed carrier, two declared decoder frames.

Pass conditions:

- typed carrier digest identical;
- decoder frame digests differ;
- projections differ;
- authority remains `NONE` / non-authority in both paths.

### `POSTHOC-KEY-FITTING-001`

Compare a frame with `binding_mode = prospective` against one with `binding_mode = posthoc` or `unknown`.

Pass conditions:

- all may emit attributable projections;
- non-prospective projections retain their binding state;
- only the prospectively bound projection is eligible for predictive-success language;
- no interesting match can erase or upgrade the selection-time receipt.

### `AUTHORITY-NULL-001`

A perfectly accurate projection must grant zero mutation, admission, canonization, or side-effect authority.

This is a structural test, not a policy engine.

### Existing labs retained

Keep and re-run:

- `TEMPORAL-COORDINATE-001`;
- `CAUSAL-RELEVANCE-001`;
- `GLYPH-RECEIVER-001`, updated to typed decoder semantics;
- `TWO-NARRATOR-001`;
- `RUPTURE-REACHABILITY-001`;
- false-yarn;
- reinterpretation replay;
- self-hit;
- future-open;
- boring-field;
- metaphor removal.

---

## 7. Public module boundaries

The implementation uses these responsibilities explicitly:

```text
skills/3rdi/scripts/three_rdi/model.py
  field/schema validation
  canonicalization policy
  set-like versus sequence-like normalization

skills/3rdi/scripts/three_rdi/compile.py
  observer-local projection primitives
  compile_observer_cut()
  no audit-only data in observer artifact

skills/3rdi/scripts/three_rdi/audit.py
  compile_audit_cut()
  full-ledger/full-field digests
  withheld-object diagnostics
  exact observer_digest link

skills/3rdi/scripts/three_rdi/glyph.py
  typed carrier validation
  decoder_frame application
  binding_mode receipt and promotion eligibility

skills/3rdi/scripts/compile_projection.py
  observer output by default
  explicit --audit selection

skills/3rdi/scripts/run_labs.py + tests/
  executable constitutional controls
```

`compile_audit_cut()` may reuse observer compilation but must remain a separately testable public function. `compile_observer_cut()` must have no dependency on `audit.py`.

---

## 8. Deliberate non-features

This punchup does not add:

- a database or event store;
- authentication or authorization;
- a capability-token system;
- network access;
- telemetry;
- a production deployment contract;
- a UI;
- generalized schema evolution infrastructure;
- a universal decoder registry;
- a universal ontology of observers, worlds, meaning, or authority;
- numerical CRS transformation;
- automatic promotion from projection to evidence or consequence.

Those may become future adapters or worlds after real callers create pressure for them.

The goal is narrower:

> **Make the Eye safe enough to call without making it the whole head.**

---

## 9. Success criteria

The punchup is accepted only if all of the following are true:

1. changing only hidden world material cannot change observer receipt bytes or observer digest;
2. audit material is emitted only through a distinct audit receipt;
3. 3rdi explicitly declines to decide audit-delivery authorization;
4. observer-facing unresolved states cannot disclose hidden identifiers or hidden-world facts through reasons, residual fog, counts, or hashes;
5. `PARALLAX` operates over observer receipts, not audit receipts;
6. raw carriers require declared compatible types before decoding;
7. `decoder_frame` is terminologically and structurally distinct from authority constitution;
8. prospective decoder binding is attributable and posthoc/unknown binding cannot masquerade as prediction;
9. `discovery_trace` preserves order through normalization and hashing;
10. set-valued metadata remains deterministic under harmless input ordering changes;
11. existing temporal, causal/relevance, narrator, rupture, and decoder invariants still pass;
12. no new side-effect or authority capability enters 3rdi.

The resulting constitutional compression is:

```text
THE EYE MAY SEE ONLY WHAT THE CUT ALLOWS.
WHAT IT CANNOT SEE MUST NOT MOVE ITS RECEIPT.
THE LENS MUST BE DECLARED.
THE FORMATION PATH MUST KEEP ITS ORDER.
THE READING MAY BE USEFUL.
THE READING DOES NOT OWN THE WORLD.
```

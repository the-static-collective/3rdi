# WALK-RECEIPT-PROJECTION-001 Design

## Status

Approved architectural slice against `3rdi/main@1e77df20b5974fe82f32933d4b38d7be1a9aa288`.

The design is the executable consequence of merged `WALK-BRAID-PROJECTION-001`: endpoint projection and formation walk are different observables, and later path disclosure must not rewrite what an earlier observer could lawfully see.

## Goal

Allow 3rdi to project an attributable formation-walk receipt when that receipt is itself available at the observer cut, while preserving the lawful case where an endpoint is visible and its walk is not.

```text
visible endpoint
    !=
available formation walk
```

The feature exposes formation ancestry. It does not infer hidden paths.

## Core laws

```text
ENDPOINT PROJECTION != FORMATION WALK
SAME ENDPOINT != SAME HISTORY
WALK AVAILABLE LATER != WALK AVAILABLE EARLIER
WALK RECEIPT != SUPPORT
WALK RECEIPT != AUTHORITY
HIDDEN WALK != RECONSTRUCTED WALK
```

A later cut may expose more formation data. Recompiling an earlier cut must still produce the earlier receipt.

## Why this belongs in 3rdi

3rdi already answers what was lawfully visible through an observer constitution at a cut. Formation-walk availability is therefore a projection question, not an ALEX support verdict or a Dogram calculation.

ALEX remains free to consume an exposed walk receipt through its own formation/support gates. Dogram may calculate over a supplied walk. Neither system is imported into the 3rdi runtime.

## Input model

Add one optional top-level family to `3rdi.field/v0`:

```json
{
  "formation_walks": [
    {
      "id": "walk-a",
      "endpoint_occurrence_id": "e3",
      "observer": "observer-a",
      "layer": "private",
      "formed_at": "2026-08-31T12:00:00Z",
      "available_from": "2026-08-31T12:05:00Z",
      "step_refs": ["e0", "e1", "e3"],
      "source_refs": ["receipt:walk-a"]
    }
  ]
}
```

`step_refs` are opaque attributable references. 3rdi does not inspect their semantics or infer missing intermediate steps.

`endpoint_occurrence_id` must name an occurrence in the same field. A walk does not make that occurrence visible; endpoint visibility is still governed by ordinary occurrence exposure.

The same endpoint may have more than one formation walk.

## Projection behavior

A formation walk is visible at a cut only when all of the following hold:

1. its `observer` equals the cut observer;
2. its `layer` is admitted by the cut;
3. `formed_at <= known_at`;
4. `available_from <= known_at`;
5. its endpoint occurrence is already visible in the ordinary occurrence projection.

Visible output is copied, not interpreted:

```json
{
  "formation_walks": [
    {
      "id": "walk-a",
      "endpoint_occurrence_id": "e3",
      "formed_at": "...",
      "available_from": "...",
      "step_refs": ["e0", "e1", "e3"],
      "source_refs": ["receipt:walk-a"],
      "hindsight_bearing": false
    }
  ]
}
```

Withheld walks are included only in the audit surface by ID + refusal reason when the ID itself is lawfully part of the field model. No hidden step list is leaked.

Allowed refusal reasons:

```text
different-observer
audience-layer-closed
not-yet-formed
not-available
endpoint-withheld
```

## Hindsight

`hindsight_bearing` is true when a walk becomes available after the cut's `focus_at`, even if the cut's later `known_at` permits the observer to inspect it.

This is descriptive only. Hindsight does not alter occurrence chronology or edge causality.

## Same-endpoint hostile specimen

Freeze one minimal field:

```text
walk A: e0 -> e1 -> e3
walk B: e0 -> e2 -> e3
```

Both reach the same visible endpoint `e3`.

Cuts:

- `a0`: endpoint visible; neither walk available;
- `a1`: walk A available only;
- `a2`: walks A and B both available.

Required properties:

```text
projection(a0).endpoint == projection(a1).endpoint == projection(a2).endpoint
projection(a0).formation_walks == []
projection(a1).formation_walks == [walk A]
projection(a2).formation_walks == [walk A, walk B]
```

Re-running `a0` after later field additions must remain byte-identical when the original immutable field/cut input is used.

## Noninterference controls

The suite must prove:

- adding a hidden walk does not change visible occurrence projection;
- changing hidden step order does not change a cut where the walk is unavailable;
- wrong-observer walk remains withheld;
- closed-layer walk remains withheld;
- visible walk cannot make a withheld endpoint visible;
- same endpoint with two visible walks preserves both IDs;
- sorting/serialization is deterministic independent of input list order;
- walk content never enters gate evaluation unless a future separately approved gate kind explicitly names it.

## Receipt identity

Projection digest includes visible formation-walk data because it is part of the observer-local receipt surface.

Hidden/unavailable walk content must not perturb the digest of a cut that cannot see it.

This is the strongest hostile requirement in the slice: hidden path mutation must be projection-noninterfering.

## CLI and compatibility

Existing `compile_projection.py` remains the entry point. No new mode is required.

Fields that omit `formation_walks` behave exactly as before. Existing fixtures and receipts must remain byte-identical unless their input explicitly adds the new family.

The portable 3rdi skill may document the new surface only after the kernel tests are green.

## Error handling

Malformed formation-walk records are field-validation errors, including:

- duplicate walk IDs;
- unknown endpoint occurrence;
- blank observer/layer/ID;
- invalid timestamps;
- malformed `step_refs` or `source_refs`;
- `formed_at` later than `available_from` only if the repository's timestamp model makes that ordering invalid; otherwise preserve both and let the cut decide availability.

Validation failure refuses compilation rather than silently dropping the malformed walk.

## Boundaries

This slice does not add:

- path inference;
- shortest-path calculation;
- truth/support/evidence semantics;
- ALEX dependencies;
- Dogram dependencies;
- side effects;
- a universal braid ontology;
- a claim that distinct histories must produce distinct future behavior.

It only makes a supplied attributable formation walk projectable when lawfully available.

## Acceptance

Complete when current 3rdi tests remain green, the new same-endpoint hostile matrix passes, hidden-walk mutation is proven noninterfering for unavailable cuts, and repeated projection receipts are deterministic.

> **THE ENDPOINT MAY BE VISIBLE BEFORE THE ROAD IS. WHEN THE ROAD ARRIVES, KEEP IT WITHOUT REWRITING THE VIEW THAT CAME BEFORE.**

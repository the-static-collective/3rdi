# Projection Receipt Contract

## Input: `3rdi.field/v0`

The phase-0 JSON field contains these ledgers:

| Ledger | Required identity | Temporal fields |
|---|---|---|
| `occurrences` | `id` | `occurred_at` |
| `exposures` | `id`, `occurrence_id`, `observer`, `layer` | `available_from` |
| `expectations` | `id`, `observer`, `layer` | `formed_at`, `available_from`, `target_at` |
| `edges` | `id`, `from`, `to`, `edge_class`, `relation` | `first_perceived_at`, assessment `assessed_at` |
| `edge_exposures` | `id`, `edge_id`, `observer`, `layer` | `available_from` |
| `location_decoders` | `id`, source/target CRS, operation | none in v0 |
| `location_claims` | `id`, `occurrence_id`, `locus_id`, `decoder_id` | `available_from` |
| `gates` | `id`, `op`, conditions | evaluated at the cut |
| `cuts` | `id`, `observer`, `mode` | `focus_at`, `known_at` |

All timestamps are strict RFC 3339 UTC instants ending in `Z`. Lists are canonically ordered before hashing. The kernel rejects duplicate identities and dangling references.

## Output: `3rdi.projection-receipt/v0`

```json
{
  "schema": "3rdi.projection-receipt/v0",
  "field_id": "...",
  "cut": {
    "id": "...",
    "observer": "...",
    "mode": "historical | reconstruction",
    "focus_at": "...Z",
    "known_at": "...Z"
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
  "audit": {
    "input_digest": "sha256:...",
    "cut_digest": "sha256:...",
    "causal_ledger_digest": "sha256:...",
    "relevance_ledger_digest": "sha256:...",
    "withheld": [],
    "withheld_expectations": [],
    "withheld_edges": [],
    "non_authority": "..."
  },
  "projection_digest": "sha256:..."
}
```

## Visibility

An occurrence enters `observer_view` only when:

1. it is not after `focus_at`;
2. it lies inside the declared location scope when one is present;
3. a matching observer and audience-layer exposure exists at or before `known_at`.

The chosen exposure receipt is included as `available_via`. An exposure after the focus in reconstruction mode sets `hindsight_bearing: true`.

Visible occurrences explicitly carry `available_at_cut: true`. Auditor-facing withheld entries carry `available_at_cut: false` and `perceived_role: unknown`; hidden content remains absent from the observer view.

## Edge replay

An edge enters the observer view only after its birthday, when both endpoints are visible and a matching edge exposure is available to the cut's observer and audience layer. `formation_history` contains only assessments at or before `known_at`; `current_assessment` is the latest of those assessments.

Location claims name `coordinate_crs`. In v0 it must match the decoder's source CRS, because the kernel preserves but does not perform the declared target operation.

The audit digest of the entire causal ledger is independent from the relevance ledger. Adding relevance must not change `causal_ledger_digest`.

`cones` traverse only visible edges whose current lawful assessment is `admitted`, starting from the cut's visible `focus_occurrence_ids`. Causal and relevance descendants are computed independently.

## Gate states

- `pass`: the condition is lawfully satisfied at the cut.
- `fail`: the condition is lawfully falsified at the cut.
- `unresolved`: the condition depends on a withheld or unassessed object.

For `all`, failure dominates unresolved. For `any`, success dominates unresolved. `not` preserves unresolved and inverts only pass/fail.

## Digest boundary

`projection_digest` hashes the full receipt before the digest field is added. It provides replay identity, not truth, authority, or tamper-proof storage.

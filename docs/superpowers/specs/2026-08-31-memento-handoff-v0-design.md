# 3rdi → MEMENTO Handoff v0 Design

## Status

Approved architectural slice. This document refreshes the existing 2026-08-27 UNDERSTORY handoff plan against current `3rdi/main` without widening either owner's authority.

Current design roots at review time:

- `3rdi/main`: `1e77df20b5974fe82f32933d4b38d7be1a9aa288`
- `MEMENTO/main`: `4e79ee779009766c0c84333625e2c96da2ab71f8`
- existing downstream plan: `MEMENTO/docs/superpowers/plans/2026-08-27-3rdi-memento-handoff-integration.md`

The old 3rdi routing PR is ancestry/evidence only. Implementation should port only behavior that still satisfies this current design rather than merging stale branch history wholesale.

## Goal

Make an observer-local 3rdi projection portable into MEMENTO UNDERSTORY through one deterministic, no-authority handoff contract.

```text
3rdi source field
  -> observer-local projection receipt
  -> 3rdi.memento-handoff/v0
  -> MEMENTO validation + atomic translation
  -> memento.understory-record/v0 residue
```

The crossing records attributable observer formation. It does not create story canon, ALEX support, destination admission, or side effects.

## Non-collapse laws

```text
3rdi projection != source
handoff != MEMENTO write
MEMENTO write != MEMENTO admission
UNDERSTORY residue != story canon
receipt possession != attributable ancestry
later ingestion != earlier observer availability
```

Every emitted or ingested receipt must freeze a no-authority boundary.

## Ownership

### 3rdi owns

- validating that the input is a genuine `3rdi.projection-receipt/v0`;
- selecting only handoff fields declared by this contract;
- deterministic serialization;
- preserving projection/cut/observer identity;
- emitting to stdout only.

3rdi does **not** write into MEMENTO, choose story meaning, create crossing decisions, or mint support.

### MEMENTO owns

- translating the handoff into MEMENTO-owned UNDERSTORY families;
- validating the entire candidate batch against current UNDERSTORY rules;
- namespacing imported IDs;
- refusing collisions or malformed ancestry;
- writing the batch only after full preflight succeeds.

MEMENTO does **not** reinterpret the 3rdi projection, promote it to canon, or claim that successful persistence proves the underlying event.

### ALEX relationship

Current ALEX may later consume attributable receipts through its own gates, including the newly landed NAME/WORLD-BRIDGE surfaces. ALEX is not a dependency of this handoff and gains no authority from it.

## Handoff contract

Schema:

```text
3rdi.memento-handoff/v0
```

Required top-level fields:

```json
{
  "schema": "3rdi.memento-handoff/v0",
  "emitted_at": "2026-08-31T00:00:00Z",
  "field_id": "field-001",
  "projection_digest": "sha256:...",
  "observer": "observer-a",
  "cut_id": "cut-a0",
  "world_instance_id": "optional-explicit-world-instance",
  "epistemic_trace": {
    "contacts": [],
    "attention_events": [],
    "decoder_applications": [],
    "stances": []
  },
  "withheld_categories": [],
  "residual_fog": [],
  "authority": "handoff-only-no-write-no-admission"
}
```

`emitted_at` is explicit input. The emitter never reads the wall clock.

`world_instance_id` is explicit when known. It must never be inferred from repository, observer, or cut identity.

`residual_fog` carries only structured identifiers already present in the source receipt. It must never synthesize hidden reasoning or free-form conjecture.

## Determinism

For identical projection bytes plus identical explicit `emitted_at` and `world_instance_id`, emitter stdout must be byte-identical.

Trace families are sorted by stable ID before serialization. `withheld_categories` is sorted. Canonical JSON uses the repository's existing deterministic JSON rules and exactly one trailing newline.

The handoff digest does not replace `projection_digest`; source projection identity remains explicit.

## MEMENTO translation

The v0 family mapping is fixed:

```text
contacts             -> contact
attention_events     -> attention
decoder_applications -> decoder
stances              -> stance
```

Imported IDs are namespaced with the source field:

```text
3rdi-<field_id>-<source_id>
```

Projection/source references use an explicit foreign namespace:

```text
3rdi:<field_id>:<ref>
```

The translator builds the entire candidate set in memory, resolves all candidate-local references, checks every destination path for collision, and validates `[existing UNDERSTORY + candidate batch]` before creating any file.

If preflight fails, zero candidate records are written.

## Ingestion receipt

Successful MEMENTO ingestion emits:

```json
{
  "schema": "memento.3rdi-ingest-receipt/v0",
  "status": "recorded",
  "handoff_schema": "3rdi.memento-handoff/v0",
  "record_ids": [],
  "authority": "understory-record-only-not-canon"
}
```

This receipt says only that MEMENTO recorded a structurally valid batch.

## Failure states

3rdi refuses:

- wrong projection schema;
- malformed explicit timestamps;
- missing observer/cut/projection identity;
- trace objects that cannot be deterministically identified;
- caller attempts to inject authority fields outside the fixed value.

MEMENTO refuses:

- wrong handoff schema;
- invalid or dangling contact/attention/decoder ancestry;
- duplicate translated IDs;
- destination path collisions;
- authority values other than the frozen handoff value;
- candidate batches that fail current UNDERSTORY validation.

Transport or file errors remain distinct from semantic validation refusal.

## Canonical fixture

One real synthetic projection fixture is compiled by current 3rdi and emitted through the real handoff emitter. Its exact stdout becomes:

- `3rdi/specimens/memento-handoff-001.json`
- `MEMENTO/test/fixtures/3rdi-memento-handoff-001.json`

The two files must be byte-identical. Cross-repo verification uses both SHA-256 and byte comparison.

The fixture is contract evidence, not a master data source.

## Hostile controls

Minimum hostile proof set:

1. same projection + same explicit emission inputs -> byte-identical handoff;
2. wrong projection schema -> refusal;
3. handoff possession without valid contact ancestry -> MEMENTO refusal;
4. malformed attention reference -> zero partial writes;
5. duplicate imported ID -> zero partial writes;
6. copied receipt body cannot substitute for a valid `contact_ref`;
7. ingestion does not create crossing decisions, story-ledger entries, or Historical Imagination edges;
8. changing only `emitted_at` changes handoff identity but not source `projection_digest`;
9. current 3rdi projection behavior remains unchanged when the emitter is unused.

## Implementation boundary

This slice may add a pure 3rdi emitter, a MEMENTO ingester, fixtures, validation refactoring needed for in-memory preflight, and focused tests.

It must not add:

- network calls;
- automatic cross-repository writes;
- ALEX runtime dependency;
- a shared 3rdi/MEMENTO master schema;
- story/canon admission;
- support/evidence promotion;
- side-effect authority;
- hidden-reasoning export.

## Acceptance

The slice is complete when both repository test floors pass on their implementation heads, the shared fixture is byte-identical, invalid ingestion proves zero partial writes, and all emitted receipts preserve the explicit no-authority membrane.

> **THE HANDOFF CARRIES AN ATTRIBUTABLE VIEW. THE DESTINATION STILL OWNS WHAT, IF ANYTHING, IT BECOMES.**

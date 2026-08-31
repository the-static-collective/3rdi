# MEMENTO handoff

`3rdi.memento-handoff/v0` carries one attributable observer-local projection toward MEMENTO without crossing MEMENTO's admission boundary.

```text
handoff != write
handoff != admission
UNDERSTORY record != story canon
receipt possession != attributable ancestry
```

The emitter consumes an existing `3rdi.projection-receipt/v0` plus explicit emission inputs. It never reads the wall clock. `emitted_at` is caller-supplied RFC3339 UTC; `world_instance_id` is optional and is never inferred.

Trace families are sorted deterministically by stable record ID. `withheld_categories` contains category names only. `residual_fog` is empty in v0; the emitter does not synthesize hidden reasoning or conjecture.

The authority value is frozen:

```text
handoff-only-no-write-no-admission
```

Canonical stdout is `three_rdi.canonical_json(receipt) + "\n"`. Repeating identical projection bytes and explicit emission inputs produces byte-identical output.

MEMENTO remains responsible for validating, translating, persisting, refusing, or ignoring the handoff. Successful emission says nothing about whether MEMENTO will record it and nothing about whether the underlying event is true.

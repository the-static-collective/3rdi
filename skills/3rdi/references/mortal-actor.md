# MORTAL-ACTOR-001 — 3rdi Handoff

> **3rdi gives the mortal world a point of view.**

`mortal_actor.3rdi-handoff/v0` is a deliberately lossy, reference-only projection of an existing `3rdi.projection-receipt/v0`.

It carries the original `projection_digest`, `field_id`, `cut_id`, and `observer`, plus only identities that were lawfully visible in that projection:

- `visible_occurrence_ids`
- `visible_causal_edge_ids`
- `visible_relevance_edge_ids`
- `contact_ids`
- `attention_event_ids`
- `decoder_application_ids`
- `stance_ids`

`visible_occurrence_ids` means only **lawfully available in this projection**. It does not mean encountered, attended, believed, relevant, causal, supported, true, authorized, or actionable.

`contact_ids` prove attributable sensing/contact. `attention_event_ids` prove attributable attention action; an `ignored` event requires contact but does not imply irrelevance. Decoder and stance identities preserve observer-local formation history; a stance is not truth.

The handoff intentionally does **not** expose identities of withheld occurrences or epistemic events. A consumer may test whether a declared basis is present in `visible_occurrence_ids`; it may not learn hidden identities from the handoff itself.

The handoff contains no gate verdict, semantic `SUPPORTS` judgment, authority, admission, or side-effect permission. Consumers requiring more detail must request the original projection receipt by its digest rather than infer omitted state.

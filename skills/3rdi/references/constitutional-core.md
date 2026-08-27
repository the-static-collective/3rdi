# Constitutional Core

## Operational identity

`3rdi` is a projection organ. It receives attributed material, freezes a cut, evaluates decoder and gate conditions, and emits a witness. It does not own the world it projects.

The cycle is:

```text
LOCATE -> CUT -> DECODE -> GATE -> PROJECT -> PRESSURE -> RECEIPT
```

## Temporal coordinates

| Coordinate | Owner | Rule |
|---|---|---|
| `occurred_at` | occurrence | Anchored chronology; never changes across cuts |
| `available_from` | exposure receipt | Observer- and audience-relative knowledge availability |
| `focus_at` | cut | Where the temporal aperture is placed |
| `known_at` | cut | Latest exposure or assessment the cut may use |

`perceived_role` is derived. It is not mutable occurrence metadata.

```text
available(o, c) := matching exposure exists and available_from <= known_at
chronological_relation(o, c) := compare(occurred_at, focus_at)
```

An unavailable occurrence is not an anticipated future. An anticipated future is its own expectation occurrence with `formed_at`, `target_at`, observer, audience layer, and evidence.

## Relation formation

Keep relation identity and relation assessment history separate:

```text
EdgeClaim
  id
  from / to
  edge_class = causal | relevance
  relation
  first_perceived_at
  discovery_trace[]
  assessments[]
```

Each assessment appends `assessed_at`, status, confidence, evidence, and reason. Project the latest lawful assessment for a cut. Never overwrite or delete the older one.

Edge availability is observer-local. Keep `EdgeExposure` separate from the edge claim, with observer, audience layer, `available_from`, and evidence. Do not expose a relation to every observer merely because one actor perceived it.

A relevance edge cannot be promoted into a causal edge by changing `edge_class`. A causal claim is a new object with its own identity and evidence path.

## Receiver constitution

Meaning can be a lawful relation between a carrier and a receiver:

```text
carrier x decoder constitution -> projection
```

This does not mean the carrier contains no constraints or that interpretation is arbitrary. Preserve carrier, decoder, projection, and formation trace separately so another decoder can replay the same carrier.

## Spatial constitution

A locus is not its coordinates. Coordinates are a claim made under a coordinate reference system and operation.

Require:

- stable `locus_id`;
- the CRS of the supplied coordinates;
- source and target CRS identifiers;
- coordinate operation identifier or declaration;
- area of use;
- accuracy and/or uncertainty;
- evidence and availability receipts;
- whether the operation actually ran.

In v0, supplied coordinates remain in the decoder source CRS and `performed_by_3rdi` is false. A target CRS declaration is a receipt for a future adapter, not proof that transformed coordinates exist.

Quarantine ambiguous CRS or units. Never overwrite a CRS merely to make layers appear aligned.

## Gates

Gates are pure and composable:

```text
Gate<State> = predicate + provenance
GateResult = pass | fail | unresolved + reasons
```

Composition may use `all`, `any`, and `not`. An unresolved input remains visible as unresolved. It must not be coerced into failure or success for presentation convenience.

Gate output has no side effects. Authorization and execution live outside the organ.

## Authority

Freshness, visibility, evidence, admission, and authority are distinct. A later projection can be fresh and useful without becoming canonical. A source can be authoritative within its scope while a projection remains a witness.

The observer view must not leak hidden occurrence content. The auditor receipt may name withheld identifiers and reasons when the caller is authorized to inspect the field.

## Break conditions

Stop or mark the result unresolved if completing it would require:

- assigning an invented occurrence or availability time;
- using future information in a historical cut;
- treating an actual future occurrence as a past expectation;
- mutating an occurrence to change its perceived role;
- erasing an earlier edge assessment;
- relabeling relevance as causation;
- equating a coordinate claim with the locus;
- claiming a decoder or CRS operation ran without an execution receipt;
- granting authority because a projection renders cleanly;
- executing a gate as a side effect.

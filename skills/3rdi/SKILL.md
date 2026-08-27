---
name: 3rdi
description: Compile provenance-first, observer-local projections across time, audience, location, decoder constitution, and born relation history. Use when the user mentions 3rdi, a third eye or projection organ, moving temporal braid, temporal cuts, time displacement, occurrence versus availability, observer-local knowledge, hindsight leakage, edge birthdays, causal versus relevance cones, token-decoder-projection separation, receiving constitution, location projection, gate compilation, reinterpretation replay, narrative apertures, or asks what was lawfully knowable from a past cut.
---

# 3rdi

Compile a cut-relative witness without rewriting the field it witnesses.

## Constitution

Hold this sentence throughout the run:

> Occurrence is anchored. Availability changes. Attention moves. Relevance can grow. Causation does not rewrite itself.

Never collapse:

```text
occurrence != availability != attention role != relevance
relevance != causation
carrier != decoder != projection
locus != coordinates != coordinate operation
projection != source != authority
historical cut != current hindsight
actual future != anticipated future
visible != traversable != admitted
gate result != side effect
```

Read [references/constitutional-core.md](references/constitutional-core.md) when the task changes or challenges any of those boundaries.

## Choose the smallest mode

- `CUT` — compile one observer at one temporal and knowledge horizon.
- `PARALLAX` — compare two or more cuts, observers, audience layers, locations, or decoders.
- `REINTERPRET` — apply a new decoder and emit a descendant projection without mutating the carrier or prior receipt.
- `GATE` — evaluate composable conditions as `pass | fail | unresolved` with provenance and no side effects.
- `LAB` — run hostile controls against hindsight, retrocausality, label-only structure, or receiver collapse.

Use multiple modes only when the user's requested outcome needs them.

## Compile cycle

### 1. LOCATE

Declare:

- the owner question;
- source scope and source cut;
- observer or audience;
- `focus_at` and `known_at` independently;
- location scope and any coordinate decoder;
- carrier and decoder constitution when decoding;
- authority boundary.

Classify inputs as owner ground, current source evidence, orientation witness, scholarly precedent, or generated material. Generated material cannot silently become ground.

### 2. CUT

Keep occurrence time on the occurrence and availability time on an exposure receipt. Derive perceived role at the selected focus.

In `historical` mode, reject `known_at > focus_at`.

In `reconstruction` mode, permit later availability receipts but label them as hindsight-bearing. Do not expose an actual future occurrence merely because the engine can see it. Represent a past observer's anticipated future only through an expectation formed at that past cut.

### 3. DECODE

Preserve these as separate attributable objects:

```text
CARRIER -> DECODER RECEIPT -> PROJECTION -> FORMATION TRACE
```

Reinterpretation creates a new projection receipt. Never overwrite the old wrong or partial projection.

For a location projection, preserve the stable locus separately from coordinates. Require source CRS, target CRS, coordinate operation, area of use, and uncertainty or accuracy. If no geodetic adapter ran, state that the operation was recorded but not performed.

### 4. GATE

Compile visibility and admission conditions as pure predicates. Return `pass`, `fail`, or `unresolved`, plus reasons and source references.

A gate result does not write, send, admit, authorize, or execute. Route any requested side effect through a separately authorized adapter after the projection receipt exists.

### 5. PROJECT

Emit only lawful observer-visible content. Keep withheld categories in an auditor-facing receipt without leaking hidden content into the observer view.

Separate causal and relevance ledgers. Later relevance may add new relevance edges. It must not relabel or mutate a causal edge.

Require an observer- and audience-specific edge exposure before placing a born edge in the observer view. Edge existence or perception by one actor is not global availability.

Treat visualization as a projection witness compiled from admitted nodes and edges. A clean graph is not evidence.

### 6. PRESSURE

Run the smallest hostile control that could falsify the result. Prefer:

- a cut before availability;
- shuffled chronology while labels stay fixed;
- two observers over one occurrence;
- later relevance with a byte-stable causal ledger;
- the same carrier under another decoder;
- a rupture where the old path stays broken;
- metaphor and domain vocabulary removal.

Read [references/labs.md](references/labs.md) for the named hatch specimens.

### 7. RECEIPT

Return:

1. the projection or comparison the user asked for;
2. the decisive cut coordinates and decoder receipts;
3. causal and relevance results separately;
4. gate states;
5. hindsight, freshness, and non-authority notices;
6. withheld categories and residual fog;
7. verification evidence when a lab or script ran.

Use [references/receipt-contract.md](references/receipt-contract.md) for structured output.

## Executable kernel

For a `3rdi.field/v0` JSON document, run:

```bash
python3 skills/3rdi/scripts/compile_projection.py FIELD.json --cut CUT_ID
```

For the repository labs, run:

```bash
python3 skills/3rdi/scripts/run_labs.py --check
```

The kernel is a phase-0 reference implementation. Do not promote it to a production event store, permission system, numerical CRS engine, or universal truth model.

## Manual fallback

When no structured field exists, compile the same contract in prose or a compact table. Mark derived roles and generated edges as projections. Preserve exact source references and unresolved fog. Do not invent timestamps, evidence, audience exposure, or causal links to fill an attractive diagram.

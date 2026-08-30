# REBIND-WITHOUT-RETROJECTION-001 — 3rdi projection specimen

**Status:** observer-local visualization / research specimen
**Owner:** 3rdi projection and availability semantics
**Non-authority:** this document does not define LOADOUT resolution or ALEX historical-attribution law.

## Purpose

Make one identity distinction visible without collapsing it:

```text
CONTINUING LOGICAL REFERENCE
        !=
OCCURRENCE-LOCAL RESOLVED BODY
        !=
HISTORICAL PRODUCER
        !=
OBSERVER-AVAILABLE PROJECTION
```

The visualization must show what an observer can currently resolve while preserving what historically occurred, even when those differ.

## Core specimen

One logical reference:

```text
L = ALEX
```

Three occurrences:

```text
O1: L resolves -> body A; body A produces R1
O2: L resolves -> body B; body B produces R2
O3: L is visible as a logical reference but current body resolution is unavailable
```

Later observer `V4` sees:

```text
logical_ref: ALEX
current resolution: body B
historical receipt: R1
historical producer: body A
```

3rdi must not visually imply:

```text
current body B == producer of R1
```

merely because B is the presently available embodiment of ALEX.

## Proposed visual grammar

### Layer 1 — stable reference fiber

Render the continuing reference as a stable address node:

```text
                ALEX
              /      \
       O1 -> A        B <- O2
              \      /
            body fiber
```

The address node is not a body node.

### Layer 2 — occurrence-local resolution edges

Resolution edges are occurrence-qualified:

```text
ALEX --resolved@O1--> A
ALEX --resolved@O2--> B
ALEX --unresolved@O3--> ?
```

Do not draw `ALEX -> B` as an unqualified timeless identity edge.

### Layer 3 — historical consequence edges

```text
A --produced@O1--> R1
B --produced@O2--> R2
```

These edges remain fixed when the current resolution changes.

### Layer 4 — observer availability

Observer-local projection is separate from world history:

```text
available_to(V4): ALEX, B, R1
known_historical_producer(V4,R1): A
```

Possible current rendering:

```text
[ALEX]                         continuing address
   |
   | current-resolution@V4
   v
 [B]                           presently available body

 [A] --historical-producer--> [R1]
  ^
  |
 historical body may be unavailable for execution
 while still attributable in the receipt
```

## Four 3rdi coordinates

Use existing observer-local coordinates rather than inventing a master identity field:

```text
occurrence
availability
focus
known-at
```

Candidate record:

```yaml
logical_ref: ALEX
occurrence: O4
focus: R1
availability:
  current_body: B
  historical_body_A: receipt-only
known_at:
  producer_R1: A
```

The same world history may therefore produce different observer projections without changing the historical producer relation.

## Projection modes

### Owner mode

Question:

```text
Who owns this organ/result family?
```

Lawful projection:

```text
R1 -> owner ALEX
```

Body distinction may be hidden if the target declares it irrelevant.

### Historical-attribution mode

Question:

```text
Which exact body produced R1?
```

Required projection:

```text
R1 -> ALEX@A
```

Current body B may be shown separately but must not replace A.

### Replay mode

Question:

```text
What body must be materialized to replay R1?
```

Required projection:

```text
historical body A required
current body B is contextual, not substitutive
```

### Unresolved mode

Question:

```text
What does the observer know when the live connector cannot resolve the body?
```

Required projection:

```text
logical_ref = ALEX
current_body = UNRESOLVED
historical receipts remain exactly what they were
```

No visual fallback should manufacture a current-body claim.

## Name/carrier companion visualization

For National Treasure's Name research, the same projection grammar can be reused without asserting theological identity:

```text
             NAME / REFERENT
           /       |        \
       sound    writing    memory/sign
```

Required non-collapse:

```text
referent != acoustic waveform
referent != orthographic token
carrier continuity != historical event identity
carrier variation != automatic referent loss
```

The visualization should let an observer select a carrier event and see:

```text
carrier form
occurrence
speaker/writer/rememberer
availability
claimed referent
provenance
```

without presenting the projection as proof that all carriers are equivalent.

## Hostile visual tests

1. **CURRENT-BODY-IMPERSONATION**
   - show R1 while current body is B;
   - fail if the graph visually routes `B -> R1` as producer.

2. **UNRESOLVED-HONESTY**
   - current live body unavailable;
   - fail if the renderer substitutes the last known body without marking the substitution.

3. **COARSE-PROJECTION**
   - owner target selected;
   - pass if A/B distinction can be hidden while the underlying receipt remains intact.

4. **MODE-SWITCH**
   - switch owner -> historical attribution;
   - pass only if the exact body distinction reappears from retained provenance rather than being reconstructed from the current live reference.

5. **OBSERVER-DIFFERENCE**
   - V1 can resolve historical body A; V2 sees only its receipt;
   - projections may differ, historical producer may not.

## Candidate rendering contract

```json
{
  "logical_ref": "ALEX",
  "selected_target": "historical_attribution",
  "current_resolution": {
    "occurrence": "O4",
    "status": "RESOLVED",
    "body": "sha:B"
  },
  "focus_receipt": {
    "id": "R1",
    "producer_body": "sha:A",
    "producer_occurrence": "O1"
  },
  "observer": {
    "historical_body_A_availability": "RECEIPT_ONLY"
  }
}
```

This is a visualization input proposal, not a runtime schema promotion.

## Seal

> **SHOW WHAT IS PRESENTLY REACHABLE WITHOUT REDRAWING WHAT HISTORICALLY HAPPENED.**

> **THE VIEW MAY CHANGE. THE ATTRIBUTION EDGE MAY NOT MOVE WITH THE VIEW.**

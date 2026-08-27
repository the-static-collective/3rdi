# 3rdi

`3rdi` is a provenance-first projection organ for asking a difficult question without cheating:

> What was lawfully visible to this observer, through this receiver constitution, at this cut?

It keeps four coordinates separate—when something occurred, when it became available, where attention is focused, and when a relation became relevant. That lets later discovery increase relevance without rewriting earlier causation.

## The floor

The repository contains:

- a portable Codex skill at `skills/3rdi/`;
- a dependency-free Python reference compiler for `3rdi.field/v0`;
- deterministic projection receipts;
- hostile labs for temporal cuts, born edges, receiver-dependent decoding, narrator parallax, and rupture reachability.

The phase-0 kernel is executable but intentionally narrow. It is not a database service, authorization system, production runtime, or metaphysical claim.

## Cycle

```text
LOCATE -> CUT -> DECODE -> GATE -> PROJECT -> PRESSURE -> RECEIPT
```

The core non-collapses are:

```text
occurrence != availability != attention role != relevance
relevance != causation
carrier != decoder != projection
locus != coordinates != coordinate operation
projection != source != authority
actual future != anticipated future
gate result != side effect
```

## Quick start

Compile an observer-local cut:

```bash
python3 skills/3rdi/scripts/compile_projection.py \
  specimens/temporal-coordinate-001.json \
  --cut june-15
```

Run the deterministic lab harness:

```bash
python3 skills/3rdi/scripts/run_labs.py --check
```

Run the tests:

```bash
python3 -m unittest discover -s tests -v
```

## Relationship to the floor around it

- ALEX contributes formation traces, discovery/evidence separation, temporal holdouts, and decoder receipts.
- The Daily Slice contributes moving temporal braid specimens, edge birthdays, hostile controls, and the `022100` receiver experiment.
- Free Graph contributes local authority, source-cut freshness, world re-entry, and no silent promotion.
- MEMENTO contributes narrative aperture, source-versus-story separation, and observer-specific disclosure.

`3rdi` does not absorb those systems. It is a small organ they may call when they need an attributed projection rather than a rewritten history.

See [the hatch design](docs/superpowers/specs/2026-08-27-3rdi-design.md) and [research precedents](docs/research-precedents.md).

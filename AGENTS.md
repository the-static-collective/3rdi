# 3rdi Repository Instructions

## Purpose

This repository owns the portable `3rdi` skill and its deterministic phase-0 reference kernel.

`3rdi` compiles observer-local projections across time, audience, location, decoder constitution, and relation history. It must never become an omniscient narrator, a canonical truth service, or an authority surface.

## Constitutional invariant

> Occurrence is anchored. Availability changes. Attention moves. Relevance can grow. Causation does not rewrite itself.

The following distinctions are hard boundaries:

- occurrence time, availability time, attention role, and relevance;
- causal edges and relevance edges;
- carrier, decoder, and projection;
- stable locus, coordinate claim, and coordinate operation;
- source, projection, evidence, and authority;
- actual future and an expectation formed in the past;
- gate evaluation and side effects.

## Source authority

Use sources in this order:

1. current owner instructions and material;
2. repository contracts and accepted owner gates;
3. current source repositories and their local authority rules;
4. orientation witnesses such as the Free Graph Front Room and The Daily Slice;
5. scholarly and technical precedents;
6. generated design material.

Generated material never silently re-enters ground. Preserve disagreements and unresolved fog.

## Scope of the v0 floor

The v0 kernel is a pure compiler over immutable JSON input. It owns parsing, temporal cuts, edge assessment replay, pure gates, location-decoder receipts, canonical ordering, and deterministic digests.

It does not own persistence, authorization, telemetry, UI, network access, numerical CRS transformation, messages, or production deployment. Add those only behind explicit adapters and a new owner-approved contract.

## Development rules

- Work on a feature branch; never force-push or bypass protections.
- Use the Python 3.11+ standard library unless a requirement earns a dependency.
- Parse and validate external data at the CLI/input boundary. Keep projection logic pure.
- Write the failing test before behavior changes.
- Keep occurrences and formation histories append-only in specimens.
- Never mutate a causal edge to represent later relevance.
- Do not include hidden occurrence content in `observer_view`.
- Do not claim a geodetic operation ran when only a decoder receipt was preserved.
- A rendered graph is a projection witness, not evidence or authority.
- Do not claim production-runtime conformance from the phase-0 kernel.

## Verification

Run from the repository root:

```bash
python3 -m unittest discover -s tests -v
python3 skills/3rdi/scripts/run_labs.py --check
python3 /root/.codex/skills/.system/skill-creator/scripts/quick_validate.py skills/3rdi
git diff --check
```

The host-specific skill validator is a hatch check, not a CI dependency. CI uses a repository-local metadata test.

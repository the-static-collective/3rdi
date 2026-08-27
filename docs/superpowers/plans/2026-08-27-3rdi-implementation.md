# 3rdi Hatch Implementation Plan

**Goal:** ship a repo-backed `3rdi` skill plus a deterministic, standard-library reference kernel that proves the temporal and causal/relevance invariants.

**Architecture:** parse `3rdi.field/v0` at the CLI boundary, compile one observer-local cut through pure functions, and serialize a canonical `3rdi.projection-receipt/v0`. Keep the portable skill thin; put constitutional details and lab contracts in references.

**Runtime:** Python 3.11+ standard library, `unittest`, GitHub Actions.

## Task 1: Repository and skill floor

Create:

- `AGENTS.md`
- `README.md`
- `skills/3rdi/SKILL.md`
- `skills/3rdi/agents/openai.yaml`
- `skills/3rdi/references/constitutional-core.md`
- `skills/3rdi/references/receipt-contract.md`
- `skills/3rdi/references/labs.md`

Validate the skill metadata with the skill-creator quick validator.

## Task 2: Red tests for the temporal compiler

Create `tests/test_projection.py` before the kernel. Cover:

- stable occurrence bytes across cuts;
- independent `focus_at` and `known_at` behavior;
- historical-mode hindsight rejection;
- actual-future withholding versus explicit expectation visibility;
- two observers receiving different roles for one occurrence;
- append-only edge assessment replay;
- causal digest stability when relevance grows;
- gate `pass`, `fail`, and `unresolved` results;
- deterministic projection digest and input-order invariance;
- invalid references and timestamps rejected at the boundary.

Run `python3 -m unittest discover -s tests -v` and preserve the expected import failure as the red receipt.

## Task 3: Minimal projection kernel

Create:

- `skills/3rdi/scripts/compile_projection.py`
- `skills/3rdi/scripts/three_rdi/__init__.py`
- `skills/3rdi/scripts/three_rdi/model.py`
- `skills/3rdi/scripts/three_rdi/compile.py`

Keep schema parsing at the boundary and the cut, edge, gate, and digest functions pure. Implement only the behaviors named by the tests.

Run the test suite until green.

## Task 4: Executable specimens

Create:

- `specimens/temporal-coordinate-001.json`
- `specimens/glyph-receiver-001.json`
- `specimens/control-matrix.json`
- `skills/3rdi/scripts/decode_fret_glyph.py`
- `tests/test_glyph_receiver.py`

The JSON file is a version-controlled control ledger. A binary spreadsheet would add an unnecessary authority surface. The glyph lab must prove that the carrier digest remains fixed while decoder and projection digests differ.

Compile all three temporal cuts and both tunings from the CLI. Save compact expected receipts under `specimens/expected/` only when deterministic.

## Task 5: Documentation and source receipts

Create:

- `docs/research-precedents.md`
- `docs/hatch-receipt.md`
- `receipts/loadout.manifest.json`

Separate owner ground, orientation witnesses, scholarly precedents, generated design, and unresolved fog. Record omitted providers and why they were outside the v0 task world.

## Task 6: CI and adversarial review

Create `.github/workflows/validate.yml` to run:

```bash
python3 -m unittest discover -s tests -v
python3 skills/3rdi/scripts/compile_projection.py specimens/temporal-coordinate-001.json --cut june-15 --check
python3 /root/.codex/skills/.system/skill-creator/scripts/quick_validate.py skills/3rdi
```

Because the skill-creator path is host-specific, CI must instead use a repo-local metadata test while the host quick validator remains a hatch check.

Review locally with the Riqor code-review rubric: correctness, boundary validation, provenance leakage, determinism, and claims. Fix all critical and high findings before pushing.

## Task 7: Commit and pull request

Run fresh verification, inspect `git diff --check`, and confirm no secrets or unrelated files. Commit with a conventional message, push `feat/hatch-3rdi`, and open a hatch PR against `main`.

Do not merge. The owner gate remains open for the user.

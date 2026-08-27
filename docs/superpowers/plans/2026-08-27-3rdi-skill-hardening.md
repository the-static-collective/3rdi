# 3rdi Skill Hardening Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Turn the existing 3rdi hatch into a portable, discoverable, hard-to-misuse operator skill without changing the deterministic projection kernel or its constitutional boundaries.

**Architecture:** Keep the executable kernel and its existing specimens untouched. Harden the skill surface around it: discovery frontmatter, a compact operator contract, durable behavioral pressure cases, and package tests that make those expectations executable where possible. Preserve detailed theory in references so `SKILL.md` stays fast to load.

**Tech Stack:** Markdown skill package, YAML agent interface, Python 3.11 `unittest`, existing dependency-free 3rdi kernel and GitHub Actions validation.

**Spec:** `docs/superpowers/specs/2026-08-27-3rdi-design.md`

## Global Constraints

- Occurrence is anchored. Availability changes. Attention moves. Relevance can grow. Causation does not rewrite itself.
- Keep occurrence, availability, attention role, and relevance separate.
- Keep relevance separate from causation.
- Keep carrier, decoder, and projection separate.
- Keep projection separate from source and authority.
- A gate result has no side effect.
- The phase-0 kernel remains a reference implementation, not a production event store, permission system, numerical CRS engine, or universal truth model.
- Preserve all existing deterministic hatch labs and projection digests unless a correctness defect is independently demonstrated.

---

### Task 1: Freeze the skill-surface RED contract

**Files:**
- Create: `tests/test_skill_operator_contract.py`

**Interfaces:**
- Consumes: `skills/3rdi/SKILL.md`, `skills/3rdi/agents/openai.yaml`
- Produces: executable package rules for discovery wording, compactness, operator-eval references, and explicit non-authority boundaries.

- [ ] **Step 1: Write failing tests** that require discovery frontmatter to start with `Use when...`, require a bounded skill-body size, require an operator pressure reference, and require the OpenAI prompt to name the observer-local cut without teaching the whole workflow.
- [ ] **Step 2: Run CI and verify RED** against the current hatch.
- [ ] **Step 3: Record the expected failures in the PR history; do not weaken the tests to match the old skill.**

### Task 2: Refactor `SKILL.md` into a fast operator instrument

**Files:**
- Modify: `skills/3rdi/SKILL.md`
- Modify: `skills/3rdi/agents/openai.yaml`
- Create: `skills/3rdi/references/operator-field-guide.md`

**Interfaces:**
- Consumes: constitutional core, receipt contract, existing hatch labs.
- Produces: a concise trigger-first skill with five named modes and a clear handoff to deeper references.

- [ ] **Step 1: Rewrite discovery metadata** so the description contains triggering conditions only and starts with `Use when...`.
- [ ] **Step 2: Compress the loaded body** around the invariant sentence, mode selection, seven-step cycle, pressure requirement, and receipt shape.
- [ ] **Step 3: Move high-context examples and operator heuristics** into `operator-field-guide.md` instead of bloating the always-loaded skill.
- [ ] **Step 4: Keep memorable language only where it improves recall**; metaphor must never substitute for the operational contract.
- [ ] **Step 5: Run the Task 1 package tests and existing package tests; verify GREEN.**

### Task 3: Add durable operator pressure cases and holdouts

**Files:**
- Create: `skills/3rdi/references/operator-evals.md`
- Create: `evals/discovery-cases.json`
- Create: `evals/holdout-cases.json`
- Modify: `tests/test_skill_operator_contract.py`

**Interfaces:**
- Produces: reproducible positive triggers, negative controls, hindsight traps, receiver-decoder traps, and unseen holdouts suitable for manual or model-level evaluation in runtimes that expose fresh-agent execution.

- [ ] **Step 1: Add explicit positive discovery cases** for temporal cuts, observer parallax, receiver-dependent decoding, edge birthdays, and reinterpretation replay.
- [ ] **Step 2: Add explicit negative controls** where ordinary summarization, chronology listing, or generic graph analysis should not wake 3rdi.
- [ ] **Step 3: Add hostile cases** where a tempting answer would leak hindsight, promote relevance into causation, mutate a prior projection, or confuse gate evaluation with authority.
- [ ] **Step 4: Add holdouts not described in `SKILL.md` examples** and document the scoring rubric and rollback rule.
- [ ] **Step 5: Extend tests to validate eval schema and ensure holdouts remain structurally separate from training/examples.**

### Task 4: Regression and hatch verification

**Files:**
- Modify only if verification exposes a defect.

**Interfaces:**
- Consumes: full repository.
- Produces: merge evidence for PR #1.

- [ ] **Step 1: Run `python3 -m unittest discover -s tests -v`; expected: all pass.**
- [ ] **Step 2: Run `python3 skills/3rdi/scripts/run_labs.py --check`; expected: PASS with existing semantic invariants intact.**
- [ ] **Step 3: Run the canonical June 15 projection with `--check`; expected: PASS and no unauthorized future leakage.**
- [ ] **Step 4: Review PR diff for accidental kernel changes; expected: skill/docs/evals/tests only.**
- [ ] **Step 5: Record baseline limitation:** this repository can enforce package and deterministic-kernel behavior, but true fresh-model invocation rates require a runtime exposing model-level eval execution. Do not claim those rates from static tests.

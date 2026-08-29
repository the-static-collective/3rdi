# SYZYGY-CUT-001 — Observer-Local Relation Space

**Status:** projection-method candidate · no authority promotion

## Purpose

3rdi treats syzygy as an observer-local relation question:

> Given the same apparent generators, which relations are actually visible and valid from this declared ambient, decoder, location, and known-at cut?

3rdi does not decide whether a relation is historically true, causally important, or authoritative. It preserves the coordinates under which the relation was visible.

## Core distinction

A syzygy is never stored as a free-floating equality.

Minimal projection record:

```yaml
source_surface:
observer:
ambient:
decoder:
location:
known_at:
generators:
visible_relation:
residual:
availability_receipt:
```

The same source can project to different relation spaces under different lawful cuts.

## 1. Ambient world changes the syzygy space

Let

\[
M=
\begin{pmatrix}
1&1&0\\
1&0&1\\
0&1&1
\end{pmatrix}.
\]

Over `F_2`:

\[
M(1,1,1)^T=0,
\]

so the columns possess a nontrivial relation.

Over `F_3`:

\[
\ker M=\{0\}.
\]

Thus the visible matrix surface is the same while its syzygy space changes with the declared ambient field.

Keeper:

\[
\boxed{\text{SAME SURFACE} \ne \text{SAME RELATION SPACE}.}
\]

## 2. Decoder-local relation

The literal date tuple

\[
(8,27,26)\to(8,28,28)
\]

under a component decoder has raw change

\[
(0,+1,+2).
\]

Under GCD-reduced transition decoding, both changing coordinates become primitive forward unit steps.

But concatenation produces

\[
82726\to82828,
\]

whose reduced displacement is `51` rather than paired unit steps.

Therefore:

\[
\boxed{\text{RELATION} = \text{SOURCE} + \text{DECLARED DECODER CUT}.}
\]

This does not mean the decoder invents arbitrary truth. It means the claimed relation must carry the transform that made it visible.

## 3. Occurrence versus serialization

For temporal specimens keep separate:

```text
occurrence instant
calendar
 timezone
local serialized date
visibility / availability
focus
known-at
```

A relation among date components may be exact under one serialization and absent under another.

Therefore:

```text
DATE RELATION != OCCURRENCE INVARIANT
```

unless invariance across the declared temporal cuts has been demonstrated.

## 4. Relation exposure

Candidate projection primitive:

```text
RELATION-EXPOSURE
```

Input:

```yaml
source_surface:
ambient:
decoder:
observer_cut:
```

Projection output:

```yaml
visible_generators:
visible_relations:
hidden_generators:
decoder_receipt:
ambient_receipt:
known_at:
```

This is a projection concept only. It does not create a new truth service or shared ontology.

## 5. Projection invariance pressure

Given two observer worlds `W1` and `W2`, compare:

```text
same source surface?
same visible generators?
same ambient?
same decoder?
same relation?
same residual?
```

Possible outcomes:

```text
INVARIANT_RELATION
AMBIENT_BREAK
DECODER_BREAK
AVAILABILITY_BREAK
SERIALIZATION_BREAK
UNKNOWN
```

These labels describe where the projection diverged, not which observer has global truth.

## 6. Syzygy and hiddenness

For a linear observation map `N`, a vector

\[
h\in\ker N
\]

is invisible at that observation surface.

3rdi may therefore treat a kernel direction as a useful model for **observer-local indistinguishability**:

```text
world A
world B
  -> same projection under N
  -> different hidden formation coordinates
```

A later receipt or intervention may separate the worlds without implying that the earlier observer should have known the hidden difference.

Keeper:

\[
\boxed{\text{INDISTINGUISHABLE HERE} \ne \text{IDENTICAL EVERYWHERE}.}
\]

## 7. Higher syzygy visibility

If a verified relation is reified as a next-level carrier, 3rdi must preserve both levels:

```text
level k:
  generators -> relation

level k+1:
  relation-as-carrier -> higher relation
```

The projection must not erase which level a relation belongs to.

```text
RELATION != GENERATOR
unless a declared formation lift reifies it
```

## Refusals

```text
VISIBLE RELATION -> therefore source invariant              REFUSE
SAME SURFACE -> therefore same ambient relation             REFUSE
LOCAL DATE PATTERN -> therefore occurrence-time property    REFUSE
HIDDEN DIFFERENCE -> therefore observer possessed it        REFUSE
REIFIED RELATION -> therefore authority                     REFUSE
```

## Seal

\[
\boxed{\textbf{SEE THE RELATION FROM SOMEWHERE WITHOUT PRETENDING IT HELD EVERYWHERE.}}
\]

3rdi owns the cut and the exposure receipt. Dogram owns calculation. ALEX owns pressure. Historical and symbolic interpretation remain elsewhere.
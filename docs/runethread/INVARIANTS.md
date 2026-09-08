# Runethread invariants

Status: **Active project policy**

Runethread invariants are the small set of truths that must remain true as implementations, providers, repositories, and delivery mechanisms evolve. The machine-readable authority is [`RUNETHREAD_INVARIANTS.json`](../../RUNETHREAD_INVARIANTS.json). ADRs explain durable design decisions and rationale; the invariant registry records the cross-cutting truths that later design work must continue to satisfy.

The registry is intentionally small. It is not a second roadmap, an ADR catalog, a list of current technologies, or a place to preserve every behavior that happens to exist today.

## What qualifies

A candidate belongs in the registry only when all of the following are true:

1. violating it would materially break Runethread's product, trust, ownership, compatibility, or governance goals;
2. the statement should survive plausible replacement of today's implementation technique;
3. its scope and current enforcement can be stated precisely;
4. there is concrete evidence for why the project already depends on it or has deliberately adopted it;
5. recording it reduces the risk of future untracked coupling more than it increases process burden.

Do **not** register an item merely because it is important today.

Classification must distinguish:

- **project invariant** — durable truth that belongs in the registry;
- **architecture/design decision** — current chosen way to satisfy one or more invariants; owned by ADRs;
- **implementation detail** — replaceable technique with no independent project-level authority;
- **milestone/version constraint** — intentionally time- or release-bound state;
- **aspiration** — desired outcome not yet guaranteed.

A classification run is allowed, and expected, to conclude that most candidates should **not** become invariants.

## Registry model v1

Each active entry has:

- stable `RT-<CLASS>-NNN` identity;
- one precise statement;
- explicit scope;
- current enforcement mode;
- concrete enforcement mechanisms;
- evidence references.

Current enforcement modes are:

- `machine` — the invariant is intended to be mechanically demonstrated by the listed mechanisms;
- `mixed` — important parts are mechanically demonstrated, while some semantic judgment remains;
- `review` — current enforcement is architectural or procedural review because reliable mechanical proof does not yet exist.

The mode describes present evidence honestly. `review` is not a failure, and `machine` must not be claimed merely because a green test exists somewhere.

Invariant IDs are never reused for a different meaning. v1 contains active entries only. Retirement, statement replacement, or a schema change requires a reviewed governance change rather than silently rewriting historical meaning.

## Change discipline

Every substantive PR must compare the proposed change with the live registry and state whether the change:

- leaves every active invariant unchanged;
- strengthens an existing invariant or its enforcement;
- weakens an invariant or its evidence;
- proposes a new invariant;
- reveals that a registered statement is incorrectly scoped.

A normal implementation PR should usually report **unchanged**. New or weakened invariant meaning is governance/architecture work and requires deliberate review before implementation assumes the change.

When work reveals a possible new invariant, ask:

> Did this work reveal a durable truth Runethread must preserve, or merely a current way of implementing that truth?

The candidate stays outside the registry until that question is answered through review.

## Decision discipline

Before recommending or accepting a material design or implementation decision, contributors and agents must:

1. identify the actual project objective being served;
2. determine whether the proposal materially advances that objective;
3. distinguish evidence-based value from agreement-seeking or architectural novelty for its own sake;
4. state meaningful costs, maintenance burden, attack surface, coupling, and lock-in;
5. consider a simpler option that could achieve the same objective;
6. check the proposal against accepted ADRs and active invariants;
7. surface genuinely material ambiguity rather than silently choosing a preference on the user's or project's behalf.

`No change` is a valid recommendation when additional machinery does not materially improve the objective.

## Initial classification run

This foundation was extracted from live state rather than invented as a blank taxonomy.

Evidence snapshot:

- Core `main`: `3da34da27183cf81a21379c91c9707f0ec54d261`;
- public memory-template `main`: `61aea99f2b503c4da2b640a40ade588370303b0f`.

### Admitted to v1

| ID | Why it survives implementation change |
| --- | --- |
| `RT-DATA-001` | Runethread's value proposition depends on user-owned Git remaining the durable semantic authority rather than a provider cache or generated view. |
| `RT-SEM-001` | A second mutation engine would create semantic drift and destroy deterministic cross-provider behavior. |
| `RT-ARCH-001` | Provider churn must not infect Core's semantic engine or authority boundary. |
| `RT-ARCH-002` | Component replacement stays safe only when correctness crosses explicit identities/contracts rather than hidden internals. |
| `RT-REL-001` | Reproducibility and recovery require execution to be tied to immutable verified identities rather than floating development state. |
| `RT-GOV-001` | The project needs decisions optimized for its actual objective rather than agreement, novelty, or accumulated machinery. |

### Considered but not admitted

| Candidate | Classification | Reason |
| --- | --- | --- |
| one Durable Object per repository identity | architecture/design decision | It is the accepted Phase 2.6 implementation profile, but a future control plane could satisfy the deeper serialization/authority requirements differently. |
| Cloudflare as Hosted provider | architecture/design decision | Provider choice, not project identity. |
| TypeScript / Node / Wrangler | implementation detail | Toolchain choice should be replaceable. |
| detached Git worktrees | implementation detail | Useful Core technique, not a cross-project truth. |
| contract v9 | milestone/version constraint | Immutable historical authority, but not the forever current version. |
| exact ADR-026 boundary membership | specialized policy authority | It already has a dedicated exact machine authority; duplicating its membership here would create two competing sources of truth. |
| template notice bytes | distribution detail | Concrete artifact controlled by the specialized boundary/release process, not a general invariant. |
| exact required-workflow blob identity | enforcement mechanism | Protects governance today but is not itself the principle being protected. |

This list is not a permanent rejection catalog. A later classification run may revisit a candidate if the underlying project goal changes or repeated implementation experience reveals a deeper durable truth.

## Growth rule

Do not schedule periodic invariant invention. Instead, at architecture reviews, security reviews, major incidents, migrations, and boundary changes, explicitly ask whether the work exposed a new durable truth, weakened an existing one, or only changed its implementation.

The intended direction is **slow registry growth and stronger evidence**, not a rapidly expanding rulebook.

# ADR-027: Project invariant registry and decision discipline

Status: **Accepted**
Date: 2026-09-08
Tracking issue: #20

## Context

Runethread now has durable decisions spread across accepted ADRs, repository policy, tests, release rules, and multiple repositories. That is manageable while the system is small, but complexity will increase sharply as Hosted, MCP, SDKs, provider integrations, release identities, and operational recovery surfaces are added.

The primary risk is not complexity by itself. It is **untracked coupling**: a principle that was once obvious can become implicit, duplicated, weakened, or accidentally converted into an implementation assumption.

Existing project policy already contains many local examples of invariant enforcement: deterministic validation, exact identity checks, negative tests, protected branches, exact-head review, immutable release anchors, and explicit component ownership. What is missing is a small project-wide model that says which truths are meant to survive changes in implementation.

A second governance risk is recommendation drift. An agent or contributor can propose architecture because it sounds sophisticated, matches a user's immediate enthusiasm, or solves a local problem while moving away from the actual project objective. Runethread needs an explicit decision discipline that makes project value, evidence, costs, alternatives, and unresolved ambiguity part of material design reasoning.

## Decision

### 1. Core owns the canonical project invariant registry

`RUNETHREAD_INVARIANTS.json` in `runethread/core` is the machine-readable authority for active project invariants.

The registry is project-wide even though Core stores the authority file. Other repositories consume or are constrained by entries according to their declared scope; they do not maintain competing copies of the same invariant statements.

### 2. The registry remains intentionally small

A registry entry is admitted only when it represents a durable truth that should survive plausible replacement of today's provider, toolchain, runtime technique, queue implementation, or other implementation detail.

The registry is **not**:

- an ADR catalog;
- a roadmap;
- a technology inventory;
- a list of every important current behavior;
- a backlog of desired properties.

Architecture/design decisions remain in ADRs. Implementation details remain in code and technical documentation. Milestone/version constraints remain in current-state planning. Aspirations remain outside the registry until the project can state what is actually guaranteed.

### 3. v1 entries are precise and evidence-bearing

Every active v1 invariant records:

- stable `RT-<CLASS>-NNN` identity;
- `active` status;
- classification;
- one precise statement;
- explicit scope;
- current enforcement mode;
- concrete enforcement mechanisms;
- evidence references.

The enforcement modes are `machine`, `mixed`, and `review`. They describe the present strength of evidence honestly; the project does not claim complete mechanical proof merely because some tests exist.

IDs are not reused for a different meaning. v1 contains active entries only. Retirement, semantic replacement, or a registry-format change requires a deliberate reviewed governance change.

### 4. Initial entries are extracted from existing system commitments

The initial registry is based on a classification run against exact live snapshots of Core and the public memory template. It admits only the durable statements that survive the implementation-detail test.

The initial active set covers:

- canonical user-owned Git state;
- single Core semantic mutation authority;
- provider-neutral Core;
- explicit versioned/immutable cross-component boundaries;
- immutable verified release/execution identities rather than floating development state;
- decision discipline tied to the actual project objective.

`docs/runethread/INVARIANTS.md` records the classification method, exact evidence snapshot, admitted entries, and examples that were deliberately **not** promoted into invariants.

### 5. Existing specialized authorities are not duplicated

A project invariant registry must not create competing authorities for surfaces that already have an exact specialized machine owner.

For example, ADR-026's exact boundary membership remains owned by its existing dedicated machine manifest rather than being copied into the general invariant registry. The invariant system may later record a higher-level non-duplicative principle about such boundaries, but it must not maintain a second membership list.

### 6. Every substantive change evaluates invariant impact

The pull-request process must explicitly state whether a substantive change leaves active invariants unchanged, strengthens enforcement, weakens an invariant/evidence surface, proposes a new invariant, or reveals a scope defect.

Normal implementation work should usually report `unchanged`.

A new or weakened invariant is governance/architecture work. Implementation must not silently assume the changed meaning before that governance change is reviewed.

### 7. Decision discipline applies to agents and contributors

Before recommending or accepting a material design or implementation decision, the decision-maker must:

1. identify the actual project objective;
2. determine whether the proposal materially advances it;
3. distinguish evidence-based value from agreement-seeking or novelty for its own sake;
4. state meaningful costs, maintenance burden, attack surface, coupling, and lock-in;
5. consider whether a simpler approach reaches the same goal;
6. test the proposal against accepted ADRs and active invariants;
7. surface genuinely material ambiguity rather than silently choosing a preference for the user/project.

`No change` is an acceptable conclusion.

### 8. Growth happens through discovery, not quota

Runethread does not schedule periodic invention of new invariants and does not target an invariant count.

Architecture reviews, security reviews, incidents, migrations, and major boundary changes add one explicit question:

> Did this work reveal a new durable truth, weaken an existing one, or merely change its implementation?

Only the first two outcomes require registry/governance work.

### 9. v1 enforcement reuses existing CI

The initial foundation adds no service, provider resource, runtime dependency, or new CI workflow.

A Go policy test validates the registry structure, stable foundation statements, integration markers, and growth rules. Existing `go test ./...` / race / cross-platform jobs therefore exercise the invariant foundation without adding a new toolchain or modifying the protected validation workflow.

Exact-head adversarial review remains necessary because a PR can change its own policy/tests. The invariant system does not claim to solve the already documented CI self-protection limitation.

## Consequences

- Future components can grow without making architectural authority implicit.
- ADRs keep explaining design decisions while the registry states the smaller set of truths those decisions must preserve.
- Implementation details can change without unnecessary invariant churn.
- New contributors and agents have a project-native decision discipline rather than relying on conversational memory.
- Every active invariant exposes the current strength and gaps of its enforcement instead of pretending all principles are mechanically provable.
- Specialized exact policy manifests remain single sources of truth rather than being duplicated into a general registry.
- The initial system adds very little operational complexity: one registry, one policy document, one test, and PR/agent governance wiring.

## Alternatives considered

### Keep principles only in ADRs and prose

Rejected. As ADR count and repository count grow, contributors would have to reconstruct the current cross-cutting truth set mentally and could miss interactions between decisions.

### Register every accepted ADR as an invariant

Rejected. That would fossilize implementation choices, make the registry large immediately, and erase the distinction between a durable truth and today's chosen mechanism.

### Build a dedicated invariant service or governance platform now

Rejected. The project does not need another runtime or service to protect a small policy registry. Existing repository CI and exact-head review are sufficient for the foundation.

### Put a separate invariant registry in every repository

Rejected for project-wide truths because duplicated statements would drift. Repository-local manifests can be added later if a concrete need appears, but they should reference the canonical project invariant identities rather than redefine them.

### Fully automate every invariant before admitting it

Rejected. Some important architecture properties require semantic review. The registry records `review` or `mixed` enforcement honestly until a reliable machine proof exists.

## Verification

The foundation is acceptable only when:

1. the registry parses under the v1 policy test;
2. foundation IDs and statements match the accepted ADR exactly;
3. entries have valid classifications, scopes, evidence, and enforcement declarations;
4. registry growth remains possible without changing the foundation statements;
5. `AGENTS.md` requires the invariant authority and decision discipline;
6. the PR template requires invariant-impact reporting;
7. CODEOWNERS covers the registry, policy document, ADR, and policy test;
8. the exact candidate passes the existing Linux, race, macOS, Windows, and aggregate validation pipeline;
9. a fresh exact-head adversarial review finds zero required corrections before merge.

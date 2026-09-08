# Current Runethread engineering milestone

Last reviewed: 2026-09-08

This file is the concise current-work pointer for contributors and agents. Detailed long-term sequencing remains in `ROADMAP.md` and `ENGINEERING_PROCESS.md`; issue #20 is the Phase 2.6 tracking authority. When remembered/chat state conflicts with live repository state, verify the repositories and follow accepted ADRs, [`RUNETHREAD_INVARIANTS.json`](../../RUNETHREAD_INVARIANTS.json), and these project-native policy files.

## Verified completed baseline

- Phase 0 architecture, Phase 1 identity cutover, Phase 2 deterministic MemoryService, and Phase 2.5 compatibility hardening are complete.
- Runethread v0.9.0 / contract v9 is the current immutable Core release. Runtime-release and contract-release identities remain separate.
- `runethread/memory-template` and the known private memory repository are migrated and validated at v0.9.0.
- ADR-012 through ADR-025 define the accepted Phase 2.6 Memory Write Delivery architecture.
- The renewed ADR-024/ADR-025 architecture-freeze review passed with zero required source corrections and merged through Core PR #26.
- The initial `runethread/hosted` repository/bootstrap slice is complete and protected.
- ADR-026 records the accepted Runethread licensing/commercial-model decision. Its repository transition is complete across Core, the public memory template, and Hosted.
- Core ADR-026 transition is merged at `3da34da27183cf81a21379c91c9707f0ec54d261`.
- The public memory-template notice remediation is merged at `61aea99f2b503c4da2b640a40ade588370303b0f`.
- Hosted ADR-026 transition is merged at `30722dfb89418d20dbedf66db7a4d75829c2d0e8`, tree `27c200758ee140d9385749c0206e072a1cee7d7f`; the reviewed candidate tree was preserved exactly by the squash merge.
- ADR-027 establishes the project-wide invariant registry and decision discipline. `RUNETHREAD_INVARIANTS.json` is the canonical active registry; its initial foundation is deliberately small and guarded through existing Core policy/tests and exact-head review.
- No Hosted Worker/runtime source, Durable Object, R2/evidence store, GitHub App, hosted mutation API, safety journal, finalizer, independent auditor/verifier, publisher, secret, provider resource, or production deployment exists yet.

The older ROADMAP/issue-sequence wording that still presents the ADR-026 transition or invariant-foundation preparation as future work is historical sequencing, not the current work pointer. Issue #20's later closeout evidence and the live repository states above control current planning.

## Invariant foundation — ADR-027

Runethread now has a small project-wide invariant foundation designed to preserve durable truths without fossilizing today's implementation choices.

The canonical active registry is `RUNETHREAD_INVARIANTS.json`. It records only truths intended to survive plausible implementation replacement. ADRs continue to own architecture/design decisions; implementation details, provider/toolchain choices, milestone/version constraints, and aspirations are not promoted into permanent invariants merely because they matter today.

The initial active set covers:

- user-owned memory Git as canonical durable semantic memory state;
- Core as the single canonical memory-mutation semantic implementation authority;
- provider-neutral Core;
- explicit versioned/immutable correctness boundaries between components;
- immutable verified identities rather than floating development branches for released/hosted execution;
- objective/evidence-driven decision discipline for material recommendations and changes, including clarification when unresolved material ambiguity could change the decision.

Current mechanisms such as one Durable Object per repository, Cloudflare, TypeScript/Node/Wrangler, detached Git worktrees, contract v9 as the current version, and exact workflow blob identities remain architecture, implementation, version, or enforcement choices rather than permanent project invariants.

Scope means applicability, not proof strength. Core owns the canonical registry, while scoped downstream repositories consume those invariant IDs and add local enforcement only where it materially helps. They do not maintain competing copies of the project invariant statements.

The invariant foundation adds no Hosted runtime or provider resource and does not authorize a release.

## Current licensing boundary — ADR-026

Runethread uses the reviewed mixed licensing boundary established by ADR-026:

- Core/Hosted Runethread-owned implementation defaults prospectively to PolyForm Perimeter 1.0.1 where the applicable licensor controls the required rights.
- Core's MIT exception is an independently guarded exact allowlist whose authoritative current path/digest membership lives only in `LICENSING_BOUNDARY.json`.
- Generator/runtime source remains Perimeter-covered.
- Historical MIT grants remain intact; the transition does not revoke previously granted rights.
- User-authored memory/project/import/attachment data remains outside Runethread's software-license grant merely because the software processes it.
- Material third-party source remains merge-blocked until an explicit inbound-rights policy exists for the target licensing class and intended separate commercial licensing.
- Core binaries embed MIT-covered contract material, so every post-transition binary is a mixed-license distribution. No post-v0.9.0 Core release may advance until the existing packaging/notice gate is deliberately replaced by a reviewed mixed-license packaging implementation.
- Hosted has no prospective Core-style MIT exception. Core's exact exception does not spill into Hosted.

The completed historical rollout sequence included the instruction **Protect and remediate the public `runethread/memory-template`** and, before that remediation, **Establish basic protected-`main` policy first**. Both are completed gates, not current work.

## Immediate milestone — Hosted developer toolchain + non-operational Worker shell

Phase 2.6 Memory Write Delivery Pipeline remains the engineering milestone. **Phase 3 MCP remains blocked until issue #20's Phase 2.6 exit criteria are satisfied.**

The next separate Hosted slice is deliberately non-operational:

1. **Re-run a fresh provider/toolchain preflight.** Verify current authoritative Cloudflare/Node guidance at the actual implementation decision point rather than relying on the bootstrap-era provider notes.
2. **Introduce the reproducibly locked Hosted developer toolchain.** Add only the reviewed TypeScript/Cloudflare developer stack, exact dependency/lockfile state, generated Worker type verification, supported runtime tests, cross-platform toolchain CI, and npm dependency maintenance required for the shell.
3. **Add a fail-closed non-operational Worker shell.** It must not create provider resources, secrets, Durable Object/R2/GitHub App state, mutation authority, publication capability, or a production deployment.
4. **Preserve the invariant boundary explicitly.** Hosted consumes current Core/ADR/invariant authority; it does not import hidden Core internals, reimplement memory semantics, or turn current provider/toolchain choices into project invariants.
5. **Complete the normal exact-head adversarial/CI/merge/post-merge gates** before starting the separate Hosted release-identity baseline.

After that shell slice:

1. **Establish Hosted release identity/release pipeline.** Independently review a release baseline that pins what may become a Hosted release while deployment remains disabled until its later security/deployment gate.
2. **Begin the Hosted memory-delivery implementation** only after those gates: authenticated transport-neutral request/status/cancel boundary, caller-to-App-installation repository authorization, immutable repository/canonical-ref/private-visibility binding, sealed request persistence, then the accepted ADR-014 through ADR-025 state-machine/evidence/publication sequence.

## Governing Phase 2.6 decisions

- ADR-012 — audited candidate promotion for external memory delivery.
- ADR-013 — per-repository serialized mutation-delivery queue.
- ADR-014 — Cloudflare-hosted Phase 2.6 memory-delivery control plane.
- ADR-015 — asynchronous project current-state/orientation projections in contract v9.
- ADR-016 — hosted eligibility, role-separated evidence authority, retention, and exact publication hardening.
- ADR-017 — accepted-history reconciliation, private-visibility eligibility, publication fencing, and managed-bootstrap rollout.
- ADR-018 — proven/possible publication-history preservation across ambiguous completion and rewrites.
- ADR-019 — rollback-independent recovery evidence and destructive-restore barriers.
- ADR-020 — independent candidate-to-request conformance audit.
- ADR-021 — independent verification of successful terminal no-candidate results.
- ADR-022 — deterministic fully audited candidate Git commit envelope/object closure.
- ADR-023 — rollback-durable terminal dispositions before lane release/client-visible terminalization.
- ADR-024 — deterministic safety-journal lineage, complete-tail recovery barrier, no active-epoch compaction, explicit Cloudflare/provider TCB.
- ADR-025 — publication quiescence covers delayed issuance and every possibly admitted remote update.
- ADR-026 — mixed licensing/commercial model and rights/release/contribution gates.
- ADR-027 — project invariant registry and decision discipline.

## Accepted Phase 2.6 implementation constraints

The following are current accepted Phase 2.6 architecture constraints. They are not automatically permanent project invariants merely because older planning prose called them "implementation invariants":

- one Durable Object per immutable repository identity is the sole live lane/operation-state/publication-authorization authority in the accepted v1 profile;
- repository identity, App installation, canonical ref, accepted revision, and directly observed private visibility are explicitly bound;
- contract v9 is the current normal hosted-write compatibility floor; contract-v8 repositories are not silently reinterpreted;
- sealed request/evidence content remains outside ordinary DO/log/status plaintext;
- ADR-024's sequential hash-linked conditional-create safety journal and recovery barrier are preserved;
- accepted operations cross rollback-durable cancellation/publication/terminalization barriers before lane release or client-visible terminal success;
- candidate construction and semantic verification remain Core-owned; Hosted must not create a duplicate semantic mutation implementation;
- `NO_OP` and `ALREADY_COMMITTED` success claims receive the independent verification required by ADR-021;
- publication uses exact expected-old semantics with minimized publisher/gateway authority and no hidden autonomous semantic retry;
- ADR-025 publication quiescence is proven before retry, terminalization, lane release, binding deletion/re-enrollment, or incompatible deployment barriers;
- every proven or possibly published candidate remains protected history until resolved;
- unknown, mixed, tampered, privacy-lost, version-barrier, ambiguous-publication, journal-corrupt, or unresolved safety/rights states fail closed.

## Exit direction

After the Hosted toolchain/shell and release-identity gates, implementation proceeds through issue #20's accepted memory-delivery sequence until its private-repository rollout, recovery, security, and operational exit criteria pass. Only then does Phase 3 MCP become unblocked.

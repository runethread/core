# Current Runethread engineering milestone

Last reviewed: 2026-09-07

This file is the concise current-work pointer for contributors and agents. Detailed long-term sequencing remains in `ROADMAP.md` and `ENGINEERING_PROCESS.md`; issue #20 is the Phase 2.6 tracking authority. When remembered/chat state conflicts with live repository state, verify the repositories and follow the accepted ADRs plus these project-native policy files.

## Completed baseline

- Phase 0 architecture, Phase 1 Runethread identity cutover, Phase 2 deterministic MemoryService, and Phase 2.5 compatibility hardening are complete.
- Runethread v0.9.0 / contract v9 is the current immutable release. Runtime-release and contract-release identities remain separate.
- `runethread/memory-template` and the known private memory repository are migrated and validated at v0.9.0. The private migration changed only the intended five Runethread-managed paths; user-owned memory/project/index bytes were preserved.
- ADR-012 through ADR-025 define the accepted Phase 2.6 Memory Write Delivery architecture.
- The renewed exact-head architecture-freeze review for ADR-024/ADR-025 passed with zero required source corrections and was merged through Core PR #26 at Core main `22995a7cf7d1c6c0f4ce548fd83667468b356f42`, tree `ef1d3c6a4e8a783cc0657b15a61703a5fa52d6d9`.
- The initial `runethread/hosted` repository safety/bootstrap slice is complete. Hosted PR #1 merged to `main` as `ca2282eafca03573ac9c88277125cc6973234959`, with merged tree `1e64bf1c3cf9d264adc227e421f016e4ed5d6c11` equal to the final reviewed tree. Post-merge Hosted validation run #9 succeeded.
- Hosted `main` is protected by an active ruleset requiring a PR and strict `validate` from the GitHub Actions integration, blocking deletion/non-fast-forward updates, and allowing no bypass. `require_extra_approval_for_unattributed_changes` is intentionally false.
- No Hosted Worker/runtime source, Durable Object, R2/evidence store, GitHub App, hosted mutation API, safety journal, finalizer, independent auditor/verifier, publisher, secret, provider resource, or production deployment exists yet.
- ADR-026 records the accepted Runethread licensing/commercial-model decision. Its system transition is the current immediate gate: Core first, then the public-template MIT notice remediation, then Hosted. It is not complete until those repo-specific boundaries reflect the decision.

## Current licensing boundary — ADR-026

Runethread uses a deliberate mixed boundary:

- **Core/Hosted implementation default:** PolyForm Perimeter License 1.0.1 for post-transition Runethread-owned implementation material for which the applicable licensor controls the necessary rights. Perimeter remains the default outside the exact exception.
- **Portable interoperability exception:** Core's MIT exception is an independently guarded exact allowlist whose authoritative current path/digest membership lives only in `LICENSING_BOUNDARY.json`. It covers the exact 19 contract paths, the exact current `runethread-bootstrap.json` bytes, and exact SHA-256 identities for approved generated memory-repository support/scaffold bytes. `AI_SETUP.md` is outside the prospective exception; historical MIT rights in older revisions remain intact. Generator/runtime source remains Perimeter-covered.
- **Generated output:** pathname alone does not grant MIT. `internal/starter/output_identity_test.go` runs the real initializer and proves every generated non-contract file equals the exact manifest path+digest set or one of the two exact zero-byte placeholders. User-authored or later derived content at the same paths does not inherit MIT by pathname.
- **Historical material:** existing MIT grants remain intact. The transition does not revoke rights already granted for pre-transition material, including unchanged portions still present later. Public development-branch snapshots before `4bd5279a91ca894f6ccb13db91360f6ba95b6576` still had an MIT root license; that commit is the first branch snapshot with a Perimeter root license.
- **User data:** user-authored memories, projects, imports, attachments, and other user-owned data are not licensed to Runethread merely because the tooling processes or stores them.
- **Licensor/rightsholder:** George Karageorgiou is the stated current licensor for Runethread-owned Perimeter implementation material for which he controls the required rights; repository ownership or future contributor metadata is not itself a rights grant.
- **Contributions:** material third-party source remains merge-blocked until an explicit inbound-rights policy exists for the target licensing class and intended separate commercial licensing.
- **Releases:** v0.9.0 remains an MIT-era release. Core binaries embed MIT-covered contract material, so every later Core binary is a mixed-license distribution. No post-transition Core release may be requested or published until packaging is verified to provide both the applicable Perimeter terms/URL plus every `Required Notice:` and the MIT license/copyright notice for embedded/distributed interoperability material. Until that reviewed packaging change lands, the release workflow rejects every requested version other than the already-published v0.9.0 baseline.
- **CI self-protection:** the current required `validate` workflow is PR-controlled. Its current bytes are exact-locked against accidental drift, but a same-PR workflow edit could theoretically remove its own guard invocation. Safety-critical workflow/policy changes therefore require manual exact-head comparison/adversarial review against protected base; their own green CI is not sufficient proof of integrity.

The public `runethread/memory-template` is **not blanket-licensed by repository membership**. It must remain implementation-free and currently distributes only exact Runethread-authored material with an applicable historical/current MIT grant plus empty placeholders. After Core merges ADR-026, first establish basic protected-`main` policy on the template, then land its scoped MIT notice through a protected reviewed change. That does **not** move Core/Hosted implementation into MIT, change the contract-v9 managed bytes/lock identity, or license user data. Existing private/user repositories are not modified just to add a notice; the next versioned Core starter/upgrader/release path must propagate the applicable MIT notice before any later Core release is unblocked.

Any older ROADMAP/catalog shorthand such as “the interoperability layer remains MIT” is non-authoritative. It must be read as a reference to the exact `LICENSING_BOUNDARY.json` exception and cannot enlarge that exception.

Core's licensing branch must pass the normal protected exact-head adversarial/CI/merge/post-merge gates. The template notice remediation is then verified independently. Hosted must then perform its own protected Perimeter/history transition before any runtime/Worker source is merged.

## Immediate milestone — Phase 2.6 pre-implementation gates

Phase 2.6 Memory Write Delivery Pipeline remains the current engineering milestone. **Phase 3 MCP is blocked until issue #20's Phase 2.6 exit criteria are satisfied.**

The immediate sequence is:

1. **Finish ADR-026 licensing transition in Core.** Protect the mixed Perimeter/MIT/history/user-data boundary in project policy and merge only an exact reviewed/validated head.
2. **Protect and remediate the public `runethread/memory-template`.** Establish basic protected-`main` policy first, then add only the scoped MIT license/copyright notice needed for the exact Runethread-authored interoperability material already distributed there; keep the repository implementation-free, preserve contract-v9 managed bytes/lock identity, and do not modify existing private/user repositories merely for notice propagation.
3. **Apply ADR-026 to `runethread/hosted`.** Hosted receives the Perimeter implementation default, explicit rightsholder/history documentation, licensing policy protection, and no runtime source.
4. **Introduce the locked Hosted developer toolchain + non-operational Worker shell.** Add the reproducibly locked TypeScript/Cloudflare toolchain, generated Worker type verification, runtime tests, cross-platform developer-toolchain CI, npm Dependabot, and a fail-closed shell. Do not create provider resources, secrets, DO/R2/GitHub App state, or deploy production service in this slice.
5. **Establish Hosted release identity/release pipeline.** Before auth/API implementation, independently review a release baseline that pins what may become a Hosted release while deployment remains disabled until its later security/deployment gate.
6. **Begin the actual Hosted memory-delivery implementation** only after those gates: authenticated transport-neutral request/status/cancel boundary, caller-to-App-installation repository authorization, immutable repository/canonical-ref/private-visibility binding, sealed request persistence, and then the accepted ADR-014 through ADR-025 state-machine/evidence/publication sequence.

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
- ADR-026 — mixed Runethread licensing/commercial model and licensing/rightsholder/release/contribution gates.

## Non-negotiable implementation invariants after the pre-implementation gates

Detailed requirements remain in the ADRs and `ENGINEERING_PROCESS.md`. At minimum, Hosted implementation must preserve all of the following:

- one Durable Object per immutable repository identity as sole live lane/operation-state authority;
- explicit repository identity + App installation + canonical ref + accepted revision + directly observed private-visibility binding;
- contract v9 as the normal hosted-write compatibility floor; contract-v8 repositories are not silently reinterpreted;
- immutable sealed request/evidence content outside ordinary DO/log/status plaintext;
- ADR-024's single sequential hash-linked conditional-create safety journal and recovery barrier;
- rollback-durable acceptance, cancellation, publication intent/history, terminal-success evidence, and ADR-023 terminal dispositions;
- whole-operation per-repository serialization with committed-idempotency-before-stale semantics;
- deterministic Core-owned candidate construction and fresh independent ADR-020/ADR-022 audit;
- fresh independent ADR-021 verification for `NO_OP` and `ALREADY_COMMITTED` success claims;
- exact expected-old publication, with publisher/gateway authority minimized and no hidden autonomous mutation retry;
- ADR-025 proof of remote publication quiescence before retry, terminalization, lane release, binding deletion/re-enrollment, or incompatible deployment barriers;
- preservation of every proven/possibly published candidate as an ADR-018 protected history anchor until resolved;
- fail-closed behavior on unknown/mixed/tampered state, provider/version barriers, privacy loss, ambiguous publication, journal corruption, or unresolved rights/safety assumptions;
- no duplicate Core semantic implementation in Hosted and no weakening of Core's development/release/migration safety pipeline.

## Exit direction

The current licensing work is a **pre-implementation governance gate**, not completion of Phase 2.6. After Core + public-template notice + Hosted licensing transitions, toolchain/shell, and Hosted release identity are complete, implementation proceeds through the accepted memory-delivery sequence until issue #20's end-to-end private-repository rollout and recovery/security/operational exit criteria pass.

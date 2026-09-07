# Runethread engineering change protocol

Status: **Active project policy**

Runethread preserves durable user memory. A defect in repository compatibility, trust, migration, mutation logic, or licensing/rightsholder policy can compound across releases and user repositories. Development therefore optimizes for **recoverability, explicit evidence, small reviewable changes, and early detection of wrong assumptions** rather than speed of implementation.

This document governs substantive changes to `runethread/core`. Accepted ADRs govern architecture and durable project-wide licensing decisions; this document governs how changes to that architecture are planned, implemented, verified, reviewed, released, licensed, and corrected.

---

## 1. Core development principles

1. **Live repository state beats remembered context.** Previous-chat summaries and planning notes are orientation material, not verification.
2. **One canonical owner per fact.** Project source, architecture, ADRs, compatibility policy, licensing policy, and engineering procedure live in the project repository. Personal memory may point to them but must not replace them.
3. **Deterministic invariants require deterministic tests.** Semantic judgment may identify intent, but storage, versioning, trust, validation, migration, concurrency, release, and mechanically checkable licensing-policy invariants must be enforced by code/tests where practical.
4. **A green build is necessary, not sufficient.** Tests prove only what was asserted. Every meaningful change also requires impact, backward, forward, negative, and cross-surface review.
5. **Published history is immutable evidence.** Do not reinterpret released contract semantics or historical license grants to avoid a version, migration, or rights boundary.
6. **Historical compatibility uses historical state.** Never manufacture an old released state with a new generator when its bytes or semantics may differ.
7. **Validation is observational.** CI may test and report; it must not repair source or push commits to the branch it validates.
8. **Unexpected state stops writes.** A contradiction, race, stale base, unexplained diff, unresolved rightsholder/license scope, or incomplete evidence is a reason to investigate before proceeding.
9. **Failures must be recoverable.** Prefer explicit migrations, snapshots, optimistic concurrency, exact-source recognition, and rollback over permissive repair.
10. **Evidence is attached to exact revisions.** Claims about tests, diffs, releases, licensing transitions, or downstream migrations must identify the exact commit/release they verified.

---

## 2. Change classes

Classify every substantive change before implementation. A change may belong to multiple classes.

| Class | Examples | Minimum additional review |
| --- | --- | --- |
| Documentation-only | explanatory docs, non-normative examples | verify no normative/control-plane/licensing impact |
| Runtime-only | performance, adapters, internal implementation | forward compatibility and API behavior |
| Public API / CLI | JSON fields, commands, exit codes | compatibility, callers, docs, integration tests |
| Dependency / toolchain | Go version, module, SDK | support floor, transitive deps, licenses, advisories, dependency graph |
| Contract | operational semantics or any `ContractPaths()` file | contract release/version, migration, historical fixture, downstream repin |
| Schema / repository format | sidecar shape, canonical layout | explicit version bump, migration, fixtures, validator/index impact |
| Trust / lock | lock envelope, trust authority, digest rules | threat model, bootstrap, migration, tamper tests |
| Index format | committed generated layout/semantics | version bump when format changes, rebuild/compatibility tests |
| Bootstrap | onboarding machine protocol/setup behavior | protocol compatibility, old/new repository discovery |
| Migration | supported source/target transitions | exact source fixture, rollback, canonical-data preservation |
| Release / packaging | release workflow, artifacts, signing | immutable publication, artifact verification, applicable license/notices |
| Downstream repository | template or private memory migration | exact before/after invariants and post-merge validation |
| Licensing / rights | root/file licenses, rightsholder identity, commercial model, interoperability boundary, inbound contribution rights, required notices | ADR-026/`LICENSING.md`, historical grants, user-data boundary, contributor rights, distribution notices |

**Semantic impact controls classification.** A runtime-code change that changes behavior promised by the vendored operational contract is a contract change even if no contract file was edited initially. A documentation-looking change that changes a license/rightsholder/commercial-use boundary is licensing/rights work, not ordinary documentation-only work.

---

## 3. Preflight gate — before editing

For a substantive change, capture and verify the following before the first source write:

- current `main` commit SHA and, when useful, tree SHA;
- branch point and intended branch name;
- current published Runethread release and relevant version dimensions;
- active repository ruleset / required checks;
- current CI status on `main`;
- relevant implementation files and tests;
- relevant accepted ADRs and normative contract files;
- current `LICENSING.md`, applicable license files/rightsholder scope, and historical license boundary when rights or distribution may be affected;
- supported historical source fixtures/releases affected by the change;
- current downstream template/private-repository state when the change may affect them.

If any verified fact contradicts the plan, stop and revise the plan before editing.

Do not create a branch from a floating assumption such as “latest main” remembered from an earlier turn. Use a freshly verified exact SHA.

---

## 4. Impact matrix — before implementation

Record an explicit impact decision for every relevant surface:

| Surface | Questions |
| --- | --- |
| Canonical memory data | Can Markdown/JSON bytes, UUIDs, provenance, lifecycle, relationships, or meaning change? |
| Project/user data | Can `projects/` or unrelated user files change? |
| `.runethread` metadata | Does config/lock meaning or representation change? |
| Operational contract | Do normative semantics or any `ContractPaths()` bytes change? |
| Schema | Does a valid/invalid sidecar set change? |
| Repository format | Does canonical layout/identity change? |
| Index | Does committed generated layout or interpretation change? |
| Trust | Does authority, digest verification, bootstrap trust, or tamper behavior change? |
| Bootstrap | Does setup/discovery/version-resolution behavior change? |
| MemoryService / CLI / API | Do request/result/error semantics change? |
| Migration | Which exact historical states must reach the new state? |
| Versioning | Which dimensions must advance, and why? |
| Release tooling | Are tags/assets/install paths or required license/notice packaging affected? |
| Dependencies / Go | Does the build floor, supply chain, license set, or supported platforms change? |
| Template | Must `runethread/memory-template` change? |
| Private memory | Must an existing user repository change? What invariants must remain byte-identical? |
| Licensing / rights | Does the Perimeter implementation default, MIT interoperability boundary, historical grant, rightsholder identity, required notice, contributor-rights policy, or separate-commercial-license flexibility change? |
| Security/privacy | Are privileges, secrets exposure, prompt-injection boundaries, or public/private data boundaries affected? |
| Documentation | Which normative and non-normative docs encode the old assumption? |

A blank cell is not evidence of “no impact.” State why the surface is unaffected.

---

## 5. Contract gate

The operational contract is security- and compatibility-sensitive.

Before claiming a change is runtime-only:

1. enumerate the files returned by `ContractPaths()`;
2. read the relevant normative wording, not merely file names/digests;
3. compare the proposed implementation semantics against the currently published contract semantics;
4. inspect trust/bootstrap/versioning behavior that interprets those files;
5. search non-vendored policy/docs for the same assumption.

If implementation behavior changes a normative contract promise, **the contract changes even if the original patch did not edit a contract file**.

A genuine contract change must normally include:

- a new contract version;
- a new immutable contract release anchor;
- updated vendored normative files/digests;
- a deterministic migration from each supported prior state;
- an exact historical fixture for the prior released state;
- tamper/unsupported-source refusal tests;
- canonical-data preservation checks where representation is unchanged;
- template/downstream migration plan.

Never retroactively reinterpret an immutable published contract to avoid these requirements.

ADR-026 additionally makes the portable operational contract/interoperability layer an explicit MIT-licensed boundary. A contract-path change therefore also requires confirming that the changed material remains within the intended permissive boundary or recording a new licensing decision; a root implementation license must not silently override the contract's interoperability policy.

---

## 6. Historical / backward compatibility gate

For every supported source state affected by a change:

1. identify the exact released source state;
2. prefer a frozen fixture captured from the actual release output or verified release artifact;
3. verify the fixture's expected metadata/digests before migration;
4. run the current migration against that fixture;
5. verify the exact intended target state;
6. verify canonical data preservation and rollback behavior.

### Historical fixture rule

**Do not synthesize a historical repository by running the current generator and editing version numbers when released contract bytes or semantics differ.**

A current generator can only stand in for a historical fixture when byte/semantic identity has been independently proven and that equivalence itself is protected by tests.

For user-memory migrations, capture before the write:

- exact canonical UUID set/count;
- canonical file/blob or digest inventory;
- relationship closure;
- provenance-bearing sidecars;
- project files;
- trust/config state;
- index state where relevant.

Historical license grants are also immutable evidence. A later Perimeter default does not revoke MIT rights already granted for pre-transition material, including unchanged portions that remain in later trees.

---

## 7. Forward compatibility gate

Do not test only today's constants. Simulate the next plausible release relationship.

Examples:

- newer runtime with unchanged contract;
- newer contract with unchanged repository format/schema;
- older supported repository opened by newer runtime;
- unsupported newer repository opened by older/current runtime;
- newly initialized empty repository;
- already-current repository passed through `upgrade` again.

Tests should intentionally make version dimensions differ when the design says they are independent. Equal constants can hide coupling bugs.

For a runtime/contract split, for example, test something equivalent to:

```text
runtime release       vNext
contract release      vCurrent
repository pin        vCurrent
```

and separately prove that incorrectly pinning the repository to `vNext` is rejected when the runtime still embeds the older contract.

---

## 8. Negative and failure-mode gate

For relevant changes, test the ways the operation must fail safely, not only the success path.

Examples include:

- stale Git revision;
- concurrent writers;
- exact idempotent retry after lost response;
- idempotency-key conflict;
- dirty repository;
- detached HEAD;
- malformed or unknown JSON fields;
- invalid lifecycle/relationship transition;
- duplicate UUID/path collision;
- hard post-write validation failure;
- rollback failure boundaries;
- tampered trust/control-plane files;
- mixed/unknown historical state;
- unsupported newer schema/contract/repository format;
- missing/stale generated indexes;
- interrupted release publication;
- incomplete artifact set;
- missing/drifted license policy or Required Notice;
- unresolved third-party contribution/rightsholder scope.

Failure tests must assert the repository state that remains afterward, not merely the returned error.

---

## 9. Implementation discipline

- Work from a dedicated branch created from an exact verified base SHA.
- Keep commits small and coherent enough to explain/revert.
- Avoid blind search/replace and unrelated refactoring.
- Re-read an existing file immediately before replacing it through an API when stale content is possible.
- Prefer deterministic transformations and explicit assertions over speculative patches.
- Do not force-push ordinary development branches.
- Do not modify `main` directly.
- Do not run multiple source writers concurrently on the same branch.
- Do not use GitHub Actions as a source-editing agent or branch fixer.
- After each significant write, verify the resulting branch head and changed-file surface.

If the underlying design premise changes materially during implementation, prefer abandoning/closing the exploratory PR and restarting from clean `main` over accumulating compatibility cruft or misleading history.

---

## 10. Agent/tool limitations that must be compensated for

AI tooling has failure modes that become more dangerous as the repository grows.

### Stale remembered state

A prior conversation may contain a once-correct SHA, version, branch, or file fact. Always re-read live state when correctness depends on it.

### Truncated tool output

A truncated tree/diff/file response is incomplete evidence. Narrow the query, page the result, or read specific files. Never infer unseen entries.

### Incomplete code search

GitHub code search can be unavailable, stale, or return incomplete results. An exhaustive audit must use a verified local checkout when available or enumerate the repository tree and inspect relevant files through repository APIs.

### Asynchronous workflow races

A workflow triggered by an earlier commit can finish after later commits. Validation workflows therefore remain read-only. Never let CI patch and push source. When multiple runs exist, tie every conclusion to the exact commit SHA.

### Synthetic history

Current code cannot be assumed to reproduce an old release. Use immutable tags/releases/frozen fixtures for historical compatibility.

### Tool-surface ambiguity

GitHub branch protection and repository rulesets can report different partial views. Verify the effective active mechanism before claiming a policy is or is not enforced.

### External dependency freshness

SDK/toolchain support changes over time. Re-check authoritative current sources at the dependency decision point rather than freezing old research into the plan.

### Rights metadata ambiguity

Repository ownership, Git author metadata, merge authority, and bot/co-author trailers are not substitutes for copyright ownership or an inbound license grant. When licensing rights matter, verify the applicable project policy and available rights evidence rather than inferring chain of title from GitHub metadata alone.

---

## 11. Verification gate on the committed branch

Validation is performed **after** deliberate source commits and against exact committed SHAs.

Core's baseline gates should include:

```text
go mod verify
go test ./...
go test -race ./...
go vet ./...
go build ./cmd/runethread
fresh runethread init
runethread index --check
runethread validate
```

Change-specific tests are added on top of this baseline.

CI must use read-only repository permissions unless a workflow's explicit purpose is release publication. Validation CI must never commit or push fixes.

A test result is associated with the exact commit SHA it tested. A later commit invalidates the earlier green result until the new SHA is tested.

---

## 12. Dependency and Go/toolchain gate

Do not add or upgrade a dependency merely because it is convenient.

Before a dependency/toolchain change:

1. verify the dependency is necessary at the architectural boundary;
2. prefer an official/maintained implementation when protocol correctness would otherwise become our burden;
3. verify its current stable version and supported Go floor from authoritative sources;
4. review direct and material transitive dependencies;
5. review licenses and known security advisories;
6. choose the lowest reasonable supported Go version, independently from the preferred CI/toolchain version;
7. run `go mod tidy` and `go mod verify`;
8. verify cross-platform build/release behavior;
9. verify GitHub dependency graph/Dependabot discovery after merge;
10. add a pinned vulnerability-scanning tool only when its version/update policy is deliberately owned.

Do not add a redundant GitHub dependency-submission workflow when the platform already submits Go dependency data correctly. Verify the observed graph first.

---

## 13. Licensing / rights gate

ADR-026 and `LICENSING.md` are authoritative for the current mixed licensing model.

Before any change that affects license files, rightsholder identity, commercial-use boundaries, interoperability-license membership, contributor rights, or distributed notices:

1. identify the exact material whose licensing changes and the rights evidence relied on;
2. preserve historical MIT grants rather than describing them as revoked by a later repository-root license;
3. preserve the explicit MIT interoperability boundary for the Memory Contract/bootstrap/generated support layer unless a new reviewed decision changes it;
4. keep user-authored memory/project/import/attachment data outside Runethread's software-license grant;
5. do not treat repository ownership, merge authority, or a DCO-style origin certification as automatic separate-relicensing rights;
6. before material third-party source is merged, require an explicit inbound-rights policy sufficient for that material's target licensing class and intended separate commercial licensing;
7. verify every distribution path carries the terms/URL and required notices applicable to its covered artifacts;
8. if rightsholder scope is unresolved, stop rather than publishing or making an unsupported license claim.

Core binaries embed MIT-covered `ContractFS` interoperability material. A post-transition Core binary is therefore a mixed-license distribution. No post-transition Core release may be requested or published until packaging is updated and verified to provide both the PolyForm Perimeter terms or URL plus every applicable `Required Notice:` for implementation **and** the MIT license/copyright notice for embedded or otherwise distributed interoperability material. Until that separately reviewed packaging change lands, the release workflow must fail closed for every requested version other than the already-published v0.9.0 baseline, and removing that block requires a coordinated guard/self-test update.

---

## 14. Draft PR review gate

Substantive work enters GitHub as a **draft PR first**.

Before readiness:

- verify base SHA and head SHA;
- inspect the canonical GitHub PR patch/file list, not only local intent;
- verify expected change class and impact matrix;
- apply the Licensing / rights gate when relevant;
- confirm no temporary workflow/script/test harness leaked into the final diff;
- inspect API/CLI/docs naming for future ambiguity;
- check PR comments, reviews, and review threads;
- require the repository's protected `validate` check on the exact head;
- verify `main` has not moved unexpectedly or update/re-evaluate if it has;
- re-run the backward/forward/negative review mentally against the actual final diff.

If a major premise was invalidated, close/supersede the PR. Do not merge merely because its code is internally consistent.

---

## 15. Merge gate

Before merge:

1. PR is ready, mergeable, and review feedback is resolved;
2. required status checks pass on the exact head;
3. base still matches the reviewed state or the PR has been updated/revalidated;
4. final changed-file set is expected;
5. no release/downstream write has begun prematurely.

Prefer squash merge for a branch containing iterative implementation commits. Use expected-head protection so a moved head cannot be merged accidentally.

---

## 16. Post-merge gate

After merge, independently verify:

- PR is actually merged/closed;
- `main` points to the intended merge/squash commit;
- merge parent/base relationship is expected;
- commit verification/signature state where applicable;
- permanent CI passes on merged `main`;
- critical files contain the intended final semantics, including license/rightsholder policy when changed.

Do not begin release or downstream migration until these checks pass.

---

## 17. Release gate

A release is a separate correctness boundary.

Before publication:

- source version and release request agree;
- full tests/vet/build pass on release commit;
- smoke-init/validate/index checks pass;
- all intended platform binaries build;
- checksum set is complete;
- draft release target matches exact release commit;
- every covered artifact carries the license material applicable to what it contains; a post-ADR-026 Core binary requires Perimeter terms/URL + every `Required Notice:` for implementation and the MIT license/copyright notice for embedded `ContractFS` interoperability material before a release request may advance.

After publication, independently verify:

- tag;
- target commit;
- immutable/non-draft status;
- expected asset names/count;
- checksums/artifacts when practical;
- applicable Perimeter and/or MIT license/notice artifacts are actually present and correspond to the released material.

Downstream template/private migrations start only after the immutable release is independently verified.

---

## 18. Template and private-repository migration gate

For changes requiring repository migration:

1. migrate `runethread/memory-template` first;
2. require a minimal expected diff and normal bootstrap validation;
3. merge/verify template;
4. only then migrate a real private memory repository;
5. capture exact private canonical invariants before any write;
6. run the released upgrader, not development assumptions;
7. prove canonical/user-owned bytes are unchanged unless the migration explicitly requires representation changes;
8. require permanent post-merge validation on the private repository.

For canonical-data-preserving metadata migrations, use Git tree/blob identity where possible as an independent byte-preservation proof.

Managed-file license/notice changes are not permission to license the repository as a whole. Preserve ADR-026's MIT interoperability boundary and explicitly keep user-authored data outside Runethread's software-license grant. Any future template/generated-user-repository distribution of MIT interoperability material must make the MIT license/copyright notice available for those managed files through the normal contract/bootstrap/release/downstream path; ADR-026 does not authorize opportunistic edits to current v0.9 user repositories merely to add notice files.

---

## 19. Correction / incident protocol

Mistakes are expected to be **detectable and recoverable**, never hidden.

When a mistake or unexplained state is discovered:

1. stop further writes;
2. capture current branch/main SHAs and active workflow runs;
3. identify exactly which action wrote what and when;
4. distinguish product defect, test defect, harness defect, stale assumption, licensing/rights defect, and tool limitation;
5. preserve evidence; do not force-push it away merely to make history look clean;
6. correct the smallest affected layer;
7. re-run broader regression checks that should have caught the issue;
8. improve tests/process so the same class of mistake is detected earlier;
9. close/supersede invalid PRs explicitly;
10. report remaining uncertainty honestly.

If a wrong change reaches `main` or a published release, prefer an explicit corrective commit/release/migration over rewriting public history or pretending a historical license grant never existed.

---

## 20. Stop conditions

Do not proceed to the next phase when any of these remain unresolved:

- live repository state contradicts the plan;
- the impact class is uncertain;
- implementation behavior and published contract wording disagree;
- an affected historical source state is not represented by trustworthy evidence;
- canonical-data preservation cannot be demonstrated for a supposedly metadata-only migration;
- tests are green only because independently meaningful version constants currently happen to be equal;
- CI results belong to an older head;
- the PR diff contains unexplained files;
- dependency/toolchain requirements are based on stale research;
- a required downstream migration/release rollback path is undefined;
- a license/rightsholder/interoperability/user-data boundary is unresolved;
- material third-party source lacks the required inbound-rights policy;
- a covered release path cannot prove delivery of its applicable license terms/URL and required notices.

A deliberate stop is a successful safety outcome, not a failure of progress.

---

## 21. Current Phase 2.6 application

Phase 2.5 compatibility hardening is complete. The subsequent ADR-015 contract transition is also complete: Runethread v0.9.0 / contract v9 is the current immutable release, `runethread/memory-template` is migrated and validated at v0.9.0, and the known private memory repository is migrated and validated at v0.9.0 with the intended five managed paths changed and user-owned memory/project/index bytes preserved. ADR-012 through ADR-026 are accepted as architectural/project-governance authority, with ADR-026's repository transitions still requiring protected implementation in both Core and Hosted.

The Phase 2.6 architecture freeze is complete and the initial `runethread/hosted` repository safety/bootstrap slice is complete. Hosted main is protected and post-merge validated, but no Worker/runtime, Durable Object, R2 store, GitHub App, hosted mutation API, safety journal, finalizer, auditor/verifier, or publisher implementation exists yet.

Phase 2.6 Memory Write Delivery Pipeline is the current engineering milestone. Phase 3 MCP implementation is blocked until Phase 2.6 satisfies issue #20.

Before hosted runtime implementation proceeds, the pre-implementation sequence is:

1. finish the protected ADR-026 licensing transition in Core and then Hosted, preserving the Perimeter implementation / MIT interoperability / historical-MIT / user-data boundaries;
2. after Hosted reflects ADR-026, introduce the reproducibly locked TypeScript/Cloudflare developer toolchain and a fail-closed **non-operational Worker shell only**, with lockfile-based install, generated Worker type verification, runtime tests, cross-platform developer-toolchain CI, and npm Dependabot; no provider resource or production deployment is authorized by that slice;
3. before auth/API implementation, establish an independently reviewed hosted release-identity/release-pipeline baseline that pins what may become a hosted release while keeping deployment disabled until its later security/deployment gate;
4. only then begin the accepted hosted request/auth/repository-binding and persistence sequence below.

For Phase 2.6 work:

- start from freshly verified `main` and ADR-012/ADR-013 invariants as amended/qualified by ADR-014 through ADR-026;
- treat ADR-026 as a licensing/governance boundary, not as a memory-contract semantic change: current contract v9 remains the immutable MIT-era release, the portable Memory Contract/bootstrap/generated-support interoperability layer stays MIT, and no post-transition Core release may publish until mixed-license packaging provides both the required Perimeter and MIT notice material; until then the release workflow remains fail-closed above v0.9.0;
- treat contract v9 as the completed normal hosted-write compatibility floor. Normal hosted mutation admission MUST reject contract-v8 repositories rather than silently omitting v8-required project current-state synchronization; supported v8 repositories may be inspected/reconciled and upgraded through the released path;
- treat the Runethread-managed v9 memory-repository validation workflow transition as completed downstream state: normal hosted canonical pushes no longer trigger redundant full validation, every retained external `uses:` Action is pinned to a verified full-length commit SHA, exact prior managed workflow recognition remains the supported migration source, and customized/unrecognized workflow state is not silently overwritten;
- treat generated/current v9 support prose alignment as completed migration state: project current-state/overview prose is an orientation/materialized view rather than a canonical source, project-view user bytes remain preserved, and automatic README replacement is limited to exact recognized prior managed README state rather than a broad heading/lock heuristic;
- keep Core's existing development pipeline intact; no reduced-safety fast mode;
- keep hosted provider code outside `runethread/core` (target `runethread/hosted`) and preserve local/offline Core operation;
- use one repository-runtime Durable Object per immutable GitHub repository identity as sole **live** hosted lane/operation-state authority;
- bind each hosted repository explicitly to immutable repository identity + App installation + canonical branch ref + last accepted revision and require directly observed private repository visibility for normal hosted writes; never silently follow branch/default changes, deletion, transfer, authorization change, or observed non-private visibility;
- keep bounded queue, active operation, phase/execution generation, retries/backoff/deadlines, evidence refs, canonical-ref binding, privacy eligibility, publisher-attempt state, protected proven/possible publication anchors, safety-journal checkpoint/binding epoch, and lane state in transactional DO SQLite;
- use the existing private evidence-storage boundary for ADR-024's single deterministic rollback-independent safety-journal lineage per repository binding epoch rather than adding a second queue/state machine. Journal records use fixed sequential keys, exact-byte canonical serialization, SHA-256 predecessor linkage, provider conditional create-if-absent as the append linearization point, and one total order for binding/enrollment, client-visible acceptance, cancellation wins, accepted canonical anchors, publication intents/outcomes, required immutable receipt references, independently verified terminal-success references/result identities, recovery barriers, and ADR-023 terminal-disposition records. Records contain no plaintext memory bodies/tokens;
- allow at most one authoritative normal journal append in flight per repository binding epoch. A byte-identical existing object at the claimed sequence is idempotent success; a byte-different collision, sequence gap, malformed key/record, predecessor mismatch, overflow, or unverifiable append outcome enters recovery/fails closed rather than skipping to another sequence;
- treat Durable Object PITR/recreation/detected rollback as an exclusive recovery barrier, not an ordinary retry. Recovery fully enumerates every page of the active journal epoch, verifies the contiguous hash-linked lineage, wins an ADR-024 `RECOVERY_BARRIER` at the exact next sequence, then performs a fresh complete tail verification proving the barrier is the end before reconstructing accepted/cancelled/terminal/protected-history state and reopening normal work;
- do not compact, truncate, summarize, or routinely rotate an active journal binding epoch in v1. Enforce explicit record/byte quotas, warn before exhaustion, and enter maintenance/refuse new hosted writes at the hard bound instead of deleting correctness history; active-epoch compaction requires a separate reviewed architecture change;
- treat the Runethread-controlled Cloudflare account/provider execution boundary, Durable Object storage/alarms, Containers, private R2 evidence/journal storage, Service Binding routing, account-held service secrets, and the provider consistency/conditional-write guarantees relied on by ADR-024 as part of the hosted v1 TCB. Preserve least privilege between hosted roles, but do not claim zero-knowledge or integrity/availability against malicious/full Cloudflare account or provider-control-plane compromise; surviving that stronger failure domain requires a separate architecture decision and external authenticated anchor;
- do not add Cloudflare Workflows in v1; use idempotent DO `drive()` plus at-least-once alarms with explicit rescheduling for prolonged retryable failures;
- treat async interleaving as real: atomically claim phase + execution generation before external work, persist claim, perform Container/R2/GitHub I/O without long `blockConcurrencyWhile()`, then compare active operation/phase/generation before accepting the result; obsolete-generation outputs cannot advance state;
- ensure only one authoritative external action exists for an active phase/generation; recovery may retry the same generation/action identity only under idempotent semantics;
- return `ACCEPTED` only after durable request/operation state, recoverable alarm scheduling, and rollback-independent acceptance evidence are established; exact resubmission/status/cancel/recovery repairs missing alarms for ordinary stored work, while destructive rollback enters the ADR-019/ADR-024 recovery barrier;
- make rollback-sensitive cancellation and accepted-anchor adoption write-ahead recoverable: a local winning transition is not exposed/released as durably final until the corresponding immutable safety record exists;
- before **any** accepted operation is exposed as a durable terminal result or its serialized lane position is released, establish ADR-023's immutable rollback-independent terminal-disposition record bound to the exact result class, authoritative evidence, generation/release identity, request identity, and canonical basis; recovery treats that record as closing the operation and never requeues it;
- store private request/candidate/finalization/audit/terminal-verification bodies in private content-addressed/no-overwrite short-retention storage, not ordinary DO/log/status plaintext;
- do not expose generic authoritative evidence/journal-write authority to Container roles: finalizer may submit only its exact candidate/finalization artifact class for current generation, auditor/verifier may submit only its exact candidate-audit or terminal-success-verification artifact class, and every write is repository/attempt/phase/generation/key/digest/create-if-absent bound through a private evidence boundary;
- keep referenced request/candidate/finalization/audit/terminal-verification/publication evidence alive for queued/active/retrying/audited/publishing/reconciling operations, including ADR-018 protected candidate anchors; private content may expire after its safe terminal window, while minimized ADR-019/ADR-023/ADR-024 safety-journal history required for an active binding epoch remains until explicit safe binding deletion/re-enrollment policy permits removal;
- separate hosted attempt identity from Core idempotency identity; hosted identity binds repository/canonical-ref/request digest, while Core owns committed retry/conflict semantics;
- isolate long-lived GitHub App key in private internal gateway; public API has no publication binding and ordinary runtime App permissions exclude Administration/Workflows;
- serialize whole hosted finalization/audit/publication operation per repo while preserving ADR-003 committed-idempotency-before-stale ordering; stale work may need cold source preflight but stops before candidate/Index/package/audit once proven uncommitted;
- run real Runethread Core/Git finalizer in attached Container; cold target at most one source clone/fetch, with reachable idempotency history retained and repository-controlled Git execution surfaces disabled;
- every fresh finalization resets/reconstructs to direct observed canonical ref/revision before Core; never reuse unpromoted local candidate history as canonical evidence;
- make finalization idempotent by persisting complete candidate evidence first and immutable attempt/generation-bound receipt last; a valid receipt selects the finalizer's claimed result, but a success-like terminal claim does not become authoritative merely because the finalizer receipt is valid;
- let `ApplyMutation` preserve its own committed-retry-before-stale, Index write, validation, commit, and local-only fast-forward semantics once;
- for candidate-producing success, require ADR-020 independent request-to-candidate conformance before publication;
- construct hosted candidate commits under ADR-022's deterministic Core-owned envelope rather than ambient Git state: sanitize author/committer/date/config inputs, use release-defined identity and request-bound deterministic commit time, forbid unknown commit headers, and ensure two executions from the same immutable inputs derive the exact same candidate object ID;
- for `NO_OP`, require a fresh reduced-privilege Core verification of the exact immutable sealed request against exact H0 before client-visible terminal success/lane release; the finalizer cannot turn a candidate-producing request into authoritative no-op merely by claiming that result;
- for `ALREADY_COMMITTED`, require a fresh reduced-privilege canonical Core/repository idempotency lookup for the exact sealed request and accepted canonical history, preserving committed-idempotency-before-stale ordering and verifying the exact request fingerprint/mutation metadata before client-visible terminal success/lane release;
- persist immutable role-separated terminal-success evidence which the finalizer cannot create/replace, bind it to exact repository/ref/request/attempt/generation/release/canonical result state, and establish its minimal rollback-independent receipt reference/result identity before a `NO_OP`/`ALREADY_COMMITTED` result is exposed as durable terminal success;
- unsuccessful/stale finalizer results remain generation-bound/fail-closed and do not require an equivalent independent semantic replay solely to defend against denial of service by a compromised finalizer, but if the DO accepts one as a client-visible terminal result it still requires ADR-023 durable terminalization before response/lane release;
- separate request-local mutation failure from canonical repository/trust/compatibility/ref-binding failure; unhealthy canonical base fails closed at lane level;
- bind candidate evidence to repository/canonical-ref/attempt/generation/idempotency/H0/C/tree/request/runtime/delivery/contract identities and digests;
- audit exact C in a fresh reduced-privilege Container/DO context and independently prove request-to-candidate conformance under ADR-020: derive the expected semantic memory changes from exact immutable sealed request + exact H0 using the same pinned Core mutation semantics (or a Core-owned equivalent verifier), compare them to candidate C, then also require exact parent/binding/scope, hard validation, strict Index v2 freshness, no unauthorized unrelated/control-plane changes, and ADR-022 raw commit-envelope equality including exact expected candidate object ID; a finalizer-supplied expected diff, manifest, or commit metadata is never conformance authority;
- permit only disposable local scratch writes needed by the Core-owned conformance verifier; the auditor never repairs candidate C, never replaces its evidence, and has no canonical Git publication authority;
- bind the immutable generation-bound audit receipt to exact request digest/fingerprint, H0, C/tree, independently derived semantic + commit-envelope conformance result, and pinned release/runtime identities; finalizer must be unable to manufacture that authoritative audit receipt;
- persist deterministic audit disagreement as suspension/reconciliation; if the operation itself is exposed as terminal, ADR-023 terminalization must be durable before that result/release;
- only repository DO may atomically transition `AUDITED -> PUBLISHING`, after rechecking current generation, cancellation, lane state, exact evidence, authorization, directly observed private visibility, bound ref == H0, and barriers;
- make cancellation vs publication a local atomic race: whichever cancellation-claim/PUBLISHING transition wins defines the boundary, with ADR-019/ADR-023 external safety evidence required before a cancellation is durably released;
- before **any** externally effective publication/token/executor/API I/O, persist an immutable rollback-independent publication-intent record bound to repository/ref/H0/C/operation/generation/evidence/protocol/attempt and a conservative fencing horizon; a rolled-back DO which later discovers this record treats C as possibly published until proven otherwise;
- keep the long-lived App private key in the gateway Worker and, only after durable `PUBLISHING` plus publication-intent safety evidence, mint a short-lived one-repository minimum Contents-write installation token to a minimal trusted publisher executor/Container when the fallback path is used;
- publisher executor imports only the verified object closure needed for exact audited C relative to H0, performs no source clone/semantic mutation/repair/audit, ignores/rejects unrelated unreachable package objects, performs at most one exact bound-ref `H0 -> C` Git-protocol push for its publisher-attempt identity, never constructs `C2`, and has no autonomous retry loop;
- require a real expected-old ref update. GitHub REST `Update a reference` with `force=false` is not exact expected-old CAS; current GraphQL `updateRefs` documents `beforeOid`/`afterOid`, so the delegated API prototype should test exact candidate-object identity and GitHub App permission behavior before unnecessary publisher machinery is committed. Until that proof exists, the exact Git-protocol publisher is the accepted safe fallback;
- treat `PUBLISHING` as capability-bearing/in-doubt under ADR-025: fence future issuance/dispatch with enforced immutable cutoffs and prove completion/non-effect of every possibly admitted remote update before terminalization/lane release/retry. Executor destruction, token expiry/revocation, a current-ref read, or the R2 recovery barrier alone cannot prove remote completion; without proof remain closed, potentially indefinitely;
- after fencing, classify the publication result conservatively as proven-not-published, proven-published, or indeterminate. Lost response, timeout, process loss, or current `ref != C` alone is never proof that C was not published;
- keep every proven or possibly published exact C as a protected history anchor. A definitive success is a durable committed fact even if a later owner rewrite removes C from current ancestry;
- a candidate operation is not exposed as durable `COMMITTED` merely because C is possibly published: exact C must be positively proven published under ADR-018 and that positive evidence plus exact `COMMITTED(C)` result must be bound into ADR-023 rollback-independent terminal disposition before client-visible success/lane release;
- resolve indeterminate publication under ADR-018: ref `C` or any current descendant containing `C` proves committed at exact C; exact `H0` may retry only the same C; a current revision that excludes C and is not H0 remains reconciliation-required even if it descends from the older H0;
- ordinary ADR-017 descendant adoption runs only after any ADR-018 protected publication anchor is resolved/preserved. A rewrite excluding proven C must restore/preserve C in canonical ancestry before normal hosted lane reopen; Phase 2.6 does not silently destructive-rebaseline committed history;
- after success confirm/reconcile current bound ref cheaply; no redundant full validation cycle;
- signed push webhooks and repository-visibility events are hints only and always trigger authoritative direct GitHub reads; they cannot clear a protected publication anchor or rollback-independent safety record;
- distinguish proven uncommitted stale work from unexpected bound-ref movement during active operation;
- ordinary reconciliation may adopt an out-of-band new canonical revision only if no protected publication anchor blocks it, the last accepted revision remains its ancestor, and the exact new revision passes trust/repository/index plus mutation/idempotency-history integrity checks; backward/sideways non-descendant rewrites or sibling descendants excluding a proven/possible C remain reconciliation-required until ancestry-preserving recovery, because Core committed-idempotency evidence lives in reachable Git history;
- treat observed non-private visibility as suspension/privacy-incident state and require explicit revalidation before resume; document that repository owners/admins remain able to change visibility outside the Git-ref CAS and Runethread does not claim atomic visibility+ref locking without Administration authority;
- use one Free/paid hosted architecture; paid ruleset protection is optional defense-in-depth;
- version hosted release/protocol and treat incompatible Worker/DO/Container/evidence/publisher/reconciliation/privacy/managed-bootstrap/canonical-ref/safety-journal/recovery/audit-conformance/terminal-success-verification/candidate-envelope/terminal-disposition/journal-lineage/provider-TCB changes as barriers; no assumption of atomic provider rollout;
- enforce explicit resource/private-data/log/retention limits and threat-model hosted plaintext processing plus minimized safety-journal retention/deletion;
- after contract-v9 migration, keep project orientation/current-state prose outside atomic memory dual-write transaction;
- measure acquisition/bytes/idempotency-stale/finalization/deterministic-candidate/package/request-conformance+commit-envelope-audit/terminal-success-verification/terminal-disposition/publication/publisher-or-API-path/fencing/journal-recovery/alarm/interleaving/provider startup latency and cost separately.

ADR-025 requires publication quiescence to cover delayed gateway/token issuance and every possibly admitted remote ref-update request. Executor termination and token expiry alone do not prove server completion. Enforced immutable issuance/dispatch cutoffs and rollback-independent completion evidence constrain recovery; absent proof, v1 remains in doubt without automatic retry or lane release, potentially indefinitely.

### Phase 2.6 architecture-freeze gate

The architecture-freeze review for ADR-012 through ADR-025 is complete and passed on the exact planning head merged in PR #26. ADR-026 does not reopen the memory-delivery state-machine architecture; it is a separate licensing/governance gate. Changes to the accepted memory-delivery architecture remain subject to the same zero-edit exact-head adversarial review rule.

Before any material architecture amendment is treated as frozen, the exact current ADR/planning head must complete a fresh adversarial architecture review covering correctness, contract compatibility, state ownership, component necessity, async interleaving, concurrency, crash/retry/ambiguous-response behavior, destructive Durable Object rollback/recreation, rollback-durable terminal dispositions, privilege/evidence-authority boundaries, evidence retention, ADR-024 journal append linearization/complete-tail proof/recovery-barrier fencing/no-active-epoch-compaction semantics, hosted provider/Cloudflare TCB assumptions, independent request-to-candidate conformance, deterministic/full candidate commit-object envelope and object closure, independent terminal-success verification, publisher-capability lifetime, exact remote publication, proven/possible publication-history preservation, accepted-history reconciliation, repository visibility/privacy, canonical-ref lifecycle, managed-bootstrap/support rollout, workflow supply-chain immutability, deployment/version skew, resource limits, and avoidable latency/duplication.

The review passes only if it produces **zero required architecture or planning edits**. Any material correction, simplification, missing invariant, or changed implementation boundary must be recorded first and resets the gate; the full review then repeats against the new exact head. Green CI or a review of an older head does not satisfy the gate.

The attack review completed on 2026-09-05 against pre-amendment head `68549677e0fbb76b0018ce3aaa574c1d1ba4e1bb` found material changes and produced ADR-016. It therefore failed the zero-edit gate.

The next full review, explicitly started against synchronized head `0a1ea0b871105d6497754fbbee93a387cb2494b4`, found material corrections and produced ADR-017. It therefore also failed the zero-edit gate.

The following full review, explicitly started against synchronized head `a9e6db2f72c8d450753c5e70e4eea5eea2d78565`, found the indeterminate-publication/history-erasure race and produced ADR-018. It therefore also failed the zero-edit gate.

The next full review, explicitly started against synchronized head `0f7f95c8220d16121144de5d1c1a4f42978550bd`, found material destructive-control-plane-recovery and managed-support/security corrections and produced ADR-019. It therefore also failed the zero-edit gate.

The following full review, explicitly started against synchronized head `4dbdef5c08142856ba1795544795cea254193398`, found that candidate validity/binding/scope did not independently prove the candidate's in-scope semantic bytes were derived from the exact sealed request. ADR-020 therefore requires a Core-owned request-to-candidate conformance proof in the fresh audit. That review also failed the zero-edit gate.

The next full review, explicitly started against synchronized head `34421411f4501f762c9c104e45d2cc92a9c3c5cb`, confirmed ADR-020 closes the candidate-content gap but found that successful terminal `NO_OP`/`ALREADY_COMMITTED` claims still bypassed fresh independent verification. ADR-021 requires those no-candidate success claims to be independently proven before durable client-visible success or lane release. That review also failed the zero-edit gate.

The following full review, explicitly started against synchronized head `9151c9d2e1a383e79449af2963fc2c547bb49429`, confirmed ADR-021 closes that terminal-success bypass but found the exact candidate Git commit still had ambient/unconstrained metadata outside ADR-020's semantic tree/message proof. Current Core invokes `git commit` with config-provided identity, while Git author/committer environment variables can override those values; a compromised finalizer could therefore keep an authorized semantic tree/message while persisting attacker-chosen identity/private bytes in exact canonical `C`. ADR-022 makes the entire candidate commit envelope and reachable object closure deterministic/Core-owned and independently audited. That review also failed the zero-edit gate.

The following full review, explicitly started against synchronized head `1b4ff70402f8aa298c4e219e0e9254e998f037ca`, confirmed ADR-022 closes the candidate-envelope/object-closure gap but found a remaining rollback terminalization hole. Acceptance survives PITR under ADR-019, while ordinary terminal stale/failure/audit outcomes and candidate `COMMITTED` could still be exposed/released from rollback-prone DO state without a required terminal-disposition record. ADR-023 requires every lane-releasing terminal disposition to become rollback-independent before durable response/release, while unsuccessful outcomes still do not gain a second semantic verifier. That review therefore failed the zero-edit gate.

A later full review explicitly examined synchronized planning head `ba9f185390b59641f0d2ad48e4463c3860daeade` against exact base `69d5c2f3a708198cce59bd554e0e49083c0dd84b` and required **zero architecture/planning edits**. That exact-head zero-edit result passed the architecture-freeze gate at the time and allowed the contract-v9 implementation prerequisite to proceed. The architecture planning tree was subsequently merged before the v0.9 implementation/release/downstream rollout.

After the v0.9 rollout completed, an independent engineering audit challenged two assumptions which that review lineage had not frozen concretely: ADR-019 still permitted multiple "equivalent" safety-journal schemes even though rollback correctness depends on append linearization/tail/fencing/compaction semantics, and the accepted hosted documents did not explicitly state whether Cloudflare account/provider/evidence-store integrity is inside the v1 TCB. Those are material planning findings. ADR-024 freezes one sequential exact-byte hash-linked conditional-create journal protocol with complete-tail `RECOVERY_BARRIER` fencing and no active-epoch compaction, and explicitly places the Runethread-controlled Cloudflare provider/account/evidence infrastructure inside the v1 TCB while leaving malicious full-provider/account compromise outside the promised v1 threat model.

ADR-024 therefore reopened the architecture freeze. The subsequent full review of exact head `967446acd8ab45f6d052d6405d4c2c65f5d69b0b` against base `7f5cf86f23604426c7e8f69086fdcbe27fb86226` found two required changes: publication fencing omitted already-admitted remote requests/delayed issuance (ADR-025), and ROADMAP.md/issue #20 retained contradictory current-work instructions. That review failed the zero-edit gate.

The corrected synchronized head containing ADR-025 then completed a fresh full exact-head review with **zero required architecture/planning edits** and was merged through Core PR #26 as `22995a7cf7d1c6c0f4ce548fd83667468b356f42` / tree `ef1d3c6a4e8a783cc0657b15a61703a5fa52d6d9`. That is the current accepted Phase 2.6 architecture baseline.

Prototype questions may remain only when an accepted invariant-preserving fallback already exists and architecture does not depend on guessing the outcome. The current GraphQL expected-old ref path is such a delegated prototype because the exact Git-protocol publisher remains the expected-old/exact-object fallback until exact candidate-object identity and App-permission behavior are proven by integration tests; unresolved remote completion follows ADR-025 and carries no bounded automatic-recovery promise.

Installing or materially changing hosted Phase 2.6 itself is a control-plane barrier and uses full Core/hosted release/downstream process.

For Phase 3, MCP remains transport over MemoryService and the established delivery lifecycle. Re-check current MCP SDK/protocol/auth requirements only when Phase 3 becomes current; do not add MCP dependencies during Phase 2.6 merely because planned next.

Any evidence that changes repository semantics still passes normal contract/migration gates rather than being smuggled in as hosted-adapter detail.

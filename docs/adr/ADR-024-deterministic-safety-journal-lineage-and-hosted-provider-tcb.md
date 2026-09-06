# ADR-024: Deterministic safety-journal lineage and hosted provider TCB

Status: **Accepted**
Date: 2026-09-06
Tracking issue: #20
Amends: ADR-014, ADR-016, ADR-018, ADR-019, and ADR-023

## Context

An independent pre-implementation engineering audit was performed after the Phase 2.6 architecture had reached a zero-edit freeze and before journal-dependent hosted implementation began. The audit identified two unresolved foundations in the frozen design.

First, ADR-019 requires a rollback-independent append-only repository safety journal, but deliberately leaves the concrete append protocol open: deterministic sequence keys, a hash chain, or an equivalently testable scheme are all allowed. That flexibility is too broad for a correctness boundary which must survive Durable Object point-in-time rollback. Recovery safety depends on one precise answer to questions such as the append linearization point, exact duplicate handling, stale restored writers, complete-tail discovery, fork/gap detection, recovery fencing, active-epoch compaction, and the ordering relied on by ADR-023 terminal dispositions. Different implementations which all appear to satisfy the previous prose can have materially different rollback behavior.

Second, the hosted architecture uses Cloudflare Workers, Durable Objects, Containers, private object/evidence storage, service bindings, and account-held credentials, but the accepted ADRs do not explicitly state whether compromise of the Cloudflare account/provider administrative boundary itself is within the Phase 2.6 threat model. Role separation and immutable evidence objects defend against narrower component bugs or privilege violations; they cannot prove journal history against an administrator or provider fabric which can arbitrarily replace hosted code, secrets, and evidence storage.

The contract-v9/runtime migration prerequisite has now completed independently across Core, `runethread/memory-template`, and the known private memory repository. These findings therefore do not require another contract migration. They do require reopening the hosted architecture freeze before the Durable Object/journal/publisher implementation starts.

Current Cloudflare R2 behavior provides the primitives needed by one simple v1 protocol: object reads and listings are strongly consistent, and conditional writes can enforce create-if-absent semantics. Phase 2.6 does not need a second database, mutable journal-head service, or external transparency log to close the rollback problem under the intended v1 threat model.

## Decision

### 1. Cloudflare hosted infrastructure is inside the Phase 2.6 v1 trusted computing base

For the hosted Phase 2.6 profile, the integrity and availability of the Runethread-controlled Cloudflare account and provider execution/storage boundary are part of the trusted computing base (TCB).

The TCB includes, for this purpose:

- the deployed Worker and Durable Object code selected by the pinned hosted release;
- the Cloudflare Container execution boundary used by trusted Runethread roles;
- Durable Object storage and alarms;
- the private R2/evidence/journal storage used by the service;
- Service Binding/capability routing controlled by the Runethread Cloudflare account;
- account-held service secrets, including credentials used by the private GitHub gateway;
- Cloudflare's enforcement of the storage consistency and conditional-write properties on which this ADR relies.

Phase 2.6 still minimizes privileges inside that TCB. Public admission, repository coordinator, finalizer, auditor, evidence mediation, and publisher roles retain the capability separation required by ADR-014 through ADR-023. A compromised finalizer does not thereby gain audit or publication authority, and ordinary stale-generation/component failures remain fail-closed.

However, v1 does **not** claim integrity, availability, confidentiality, or rollback-proof recovery against a malicious or fully compromised Cloudflare account administrator/provider control plane which can arbitrarily deploy replacement code, read or replace secrets, or delete/fabricate R2 journal/evidence objects. Surviving that stronger failure domain would require an independently authenticated anchor outside the Cloudflare trust boundary and is a separate architecture change.

The hosted profile is therefore not zero-knowledge. Cloudflare is a trusted plaintext processor for sealed-request execution and related private evidence according to the service's documented data-handling policy. No product/security wording may imply otherwise.

### 2. One deterministic journal namespace and version is used in v1

The rollback-independent safety journal uses one versioned immutable namespace per immutable repository identity and repository binding epoch. The v1 logical key form is equivalent to:

```text
safety-journal/v1/repositories/<repository-id>/epochs/<binding-epoch-id>/records/<sequence>.json
```

where:

- `<repository-id>` is the immutable GitHub repository identity already bound by the repository runtime;
- `<binding-epoch-id>` is a fresh non-reused random binding-epoch identifier created for enrollment/re-enrollment;
- `<sequence>` is a fixed-width unsigned decimal sequence number whose lexical order equals numeric order;
- sequence `0` is the epoch-opening record;
- every later record is exactly the previous sequence plus one;
- gaps, duplicate sequence numbers with different bytes, unrecognized key shapes, or records outside the active repository/epoch/version are integrity failures.

The concrete width and maximum representable sequence are hosted-protocol constants and are covered by the release barrier. Implementations MUST reject overflow rather than wrap or reuse a sequence.

There is no separate mutable journal-head object in v1. The repository Durable Object stores its ordinary local checkpoint as `(binding_epoch_id, sequence, record_digest)`, but that checkpoint is rollback-prone and is never recovery authority by itself.

### 3. Every journal record is exact-byte hash-linked

Each immutable journal record contains, at minimum:

- journal protocol version;
- immutable repository identity;
- binding epoch identity;
- exact sequence number;
- `previous_record_sha256`, absent/empty only for the epoch-opening record;
- record kind;
- the minimized operation/event identity and evidence references required by ADR-019, ADR-021, and ADR-023 for that record kind;
- pinned hosted/Core/contract/protocol identities necessary to interpret the record.

The digest of a record is SHA-256 over the exact canonical serialized object bytes stored at its key. Each record after sequence 0 stores the digest of those exact bytes for the immediately preceding record.

Canonical record serialization is part of the hosted journal protocol. Unknown required fields, noncanonical encodings, unsupported record versions, mismatched repository/epoch/sequence values, or an incorrect predecessor digest fail closed during append verification and recovery.

Journal records continue to contain only minimized recovery metadata and opaque evidence references/digests. They do not contain plaintext memory Markdown/JSON, GitHub write tokens, App private keys, or unrestricted provider error/log text.

### 4. The repository Durable Object is the sole logical initiator of normal journal appends

The repository Durable Object remains the sole live hosted lane/state-machine authority and the sole logical initiator of normal safety-journal append decisions.

The actual object write may be mediated by the existing private evidence/journal service boundary, but that service:

- accepts an already fixed repository + epoch + sequence + key + exact record bytes/digest;
- does not allocate the next sequence autonomously;
- does not choose a different record class or payload;
- does not retry a collision at a later sequence;
- exposes no generic journal write/delete capability to public clients, finalizers, auditors, or publishers.

At most one authoritative journal append may be in flight for a repository binding epoch during normal execution. This is independent of ordinary non-journal external work, which remains generation-bound under ADR-014.

### 5. Conditional object creation is the append linearization point

Suppose the repository runtime's last verified checkpoint is sequence `k` with exact digest `Dk`.

Before external journal I/O, the DO atomically persists one pending append claim containing the complete exact next record bytes/digest for sequence `k+1`, linked to `Dk`. It then asks the private journal boundary to create only the exact `k+1` object with provider-level create-if-absent semantics equivalent to `If-None-Match: *`.

The successful conditional creation of that immutable object is the journal append **linearization point**.

After success, the caller re-reads the exact key and verifies its bytes, digest, repository/epoch/sequence binding, record kind, and predecessor digest before the DO advances its rollback-prone local checkpoint.

If the conditional creation reports that the key already exists, the existing object is read and verified:

- byte-for-byte/digest-identical content is idempotent success, covering response loss or replay of the same pending append;
- any different valid or invalid content at that sequence means the local checkpoint may be stale or the journal is inconsistent. The runtime enters recovery and MUST NOT skip to `k+2` or manufacture a second successor.

If the storage call is unavailable or its result is ambiguous and the exact object cannot be re-read/verified, any transition whose ADR requires the journal barrier remains nonterminal/nonexposed. The DO does not return durable `ACCEPTED`, release a cancellation/terminal disposition, accept a canonical anchor, or begin publication-capable external I/O until the required append is proven.

### 6. Destructive recovery proves the complete tail and fences delayed stale writers with a recovery barrier

After Durable Object PITR/recreation, explicit destructive control-plane recovery, or detected checkpoint/epoch disagreement, the repository enters `MAINTENANCE`/recovery before normal admission, publication, or journal appends.

Recovery performs this protocol for the active binding epoch:

1. verify current repository/App/canonical-ref/private-visibility binding as required by the earlier ADRs;
2. fully enumerate the active journal epoch prefix, following every provider pagination cursor until the listing is complete;
3. require only the versioned record-key grammar for that repository/epoch;
4. read and verify every record from sequence 0 through the observed maximum;
5. require an exact contiguous sequence with no gaps, duplicates, unsupported versions, repository/epoch mismatch, or predecessor-digest mismatch;
6. reconstruct enough verified tail state to identify the exact next sequence and predecessor digest;
7. attempt to append a special immutable `RECOVERY_BARRIER` record at that exact next sequence using the normal conditional-create linearization rule;
8. if the barrier key collides, read and verify the existing record. An exact duplicate barrier is idempotent; a valid competing successor produced by a previously delayed legitimate append is incorporated into the verified chain and recovery retries the barrier at the following sequence. A conflicting/invalid successor fails closed;
9. once the recovery barrier wins at sequence `B`, perform a fresh complete strongly-consistent listing/read verification of the epoch and require the exact verified chain to end at `B` with no record above `B`;
10. only then reconstruct accepted operations, cancellations, terminal dispositions, accepted anchors, protected publication candidates/outcomes, and required immutable evidence under ADR-018/019/021/023;
11. persist the recovered DO checkpoint at `B` and re-establish queue/alarm/lane state only after reconstruction is complete.

The recovery barrier is the fence for a delayed pre-recovery journal writer. Because every normal writer is bound to exactly its previously claimed `k+1`, at most one append is in flight, and the journal service never advances after a collision, a stale writer whose predecessor is older than the recovered tail cannot legally jump beyond the barrier. Once the barrier at `B` exists and the fresh complete verification shows no successor, normal appends may resume from `B+1` under the reconstructed runtime.

A runtime MUST NOT reopen the lane merely because one listing page looked complete or because its restored local checkpoint matches an early prefix.

### 7. All rollback-sensitive record classes share the same total order

The single per-epoch sequence orders all rollback-sensitive safety facts required by the accepted ADRs, including at least:

- epoch opening/binding records;
- durable client-visible `ACCEPTED` records;
- winning cancellation records;
- accepted canonical-history/adoption anchors;
- publication intents before write-capable external I/O;
- definitive publication outcome references;
- ADR-021 independently verified terminal-success evidence references/result identities;
- ADR-023 terminal-disposition records;
- recovery barriers and any future journal control record explicitly defined by a compatible hosted protocol.

This total order supplies the recovery ordering required by ADR-023. It does **not** make the journal the normal queue: ordinary scheduling, phase/generation transitions, retries, and lane ownership remain exclusively in DO SQLite during healthy execution.

### 8. Active binding epochs are not compacted or rotated in v1

While a repository binding epoch is active, v1 performs no deletion, truncation, checkpoint compaction, summarization, or routine epoch rotation of journal records required for correctness.

Instead, the hosted release defines explicit hard maximums for journal record count and total journal bytes per active binding epoch. The service must surface approaching limits before exhaustion. At the hard limit the repository enters maintenance and refuses new hosted writes rather than deleting or summarizing accepted history.

A protocol which compacts an active epoch, rolls it into a new active epoch while preserving guarantees, or authenticates a shortened historical closure requires a separate reviewed architecture decision and release barrier. This deliberately trades bounded availability for a simpler correctness proof in v1.

Explicit binding deletion/disconnection and later re-enrollment remain governed by ADR-019: outstanding publication capabilities and protected history must be resolved/fenced before correctness metadata is removed, and re-enrollment after destructive deletion creates a new binding epoch without claiming preservation of deleted hosted acceptance/publication history.

### 9. Recovery failures remain fail-closed within the TCB

Under ordinary failures inside the trusted hosted boundary, any of the following prevents normal hosted writes until repaired under an explicit operator/recovery procedure:

- missing required record;
- malformed key or record;
- sequence gap or overflow;
- predecessor-digest mismatch;
- byte-different collision at one sequence;
- incomplete/unverifiable paginated listing;
- required evidence referenced by the chain missing/corrupt;
- unexpected record above a completed recovery barrier;
- unsupported journal/release version;
- inability to prove a conditional append outcome.

This fail-closed behavior is not a claim that the journal can detect a malicious TCB administrator who can consistently rewrite the entire hosted system and its evidence. That stronger adversary is outside v1 by Section 1.

### 10. Hosted release barriers include the exact journal protocol and TCB contract

The hosted release/version boundary now pins at least:

- journal namespace/key grammar and sequence width/limits;
- canonical record serialization and record-kind schemas;
- hash/predecessor algorithm;
- conditional-create append semantics;
- pending-append/idempotent-collision behavior;
- recovery enumeration and `RECOVERY_BARRIER` protocol;
- active-epoch no-compaction rule and quotas;
- repository/epoch reconstruction semantics;
- the v1 Cloudflare TCB/threat-model statement.

An in-flight operation or recovered repository runtime cannot silently reinterpret records under an incompatible protocol. Deployment uses drain/maintenance or explicitly versioned compatible recovery as required by ADR-014/016/019/023.

## Consequences

- ADR-019's former freedom to choose sequence keys, hash chain, or an equivalent representation is narrowed for Phase 2.6 v1 to one concrete ordered hash-linked conditional-create protocol.
- Durable Object PITR cannot safely reuse an old checkpoint by guessing. Recovery proves the object-store tail and writes a fencing barrier before the lane reopens.
- Lost append responses are idempotently recoverable without allocating a second sequence.
- ADR-023 receives one explicit total order for reconstructing terminalized operations relative to later accepted work.
- Active-epoch journal retention becomes operationally bounded but intentionally uncompacted in v1. Hitting the configured bound fails availability closed rather than weakening rollback guarantees.
- No second queue, mutable journal-head database, external KMS, transparency log, or cross-provider checkpoint is added.
- The architecture explicitly states that Cloudflare account/provider integrity and availability are trusted. This matches the existing hosted plaintext execution model rather than silently promising protection against the infrastructure administrator.
- The previous Phase 2.6 zero-edit architecture freeze is invalidated by this material amendment. Journal-dependent hosted implementation remains blocked until a fresh full adversarial review of the exact synchronized planning head containing this ADR requires zero architecture/planning edits.

## Alternatives considered

### Keep ADR-019 implementation freedom and decide the journal shape while coding

Rejected. Append linearization, stale-writer fencing, complete-tail proof, and compaction semantics determine whether destructive rollback recovery is correct. They are architectural protocol, not merely storage structs.

### Add a mutable authoritative `journal-head` object

Rejected for v1. A mutable head introduces another rollback/overwrite-sensitive pointer whose recovery semantics would themselves need protection. Strong listing plus strict sequential conditional-create records are sufficient under the stated TCB.

### Use sequence numbers without predecessor hashes

Rejected. Strict sequence detects gaps, but predecessor digests cheaply bind the exact byte lineage and make splicing/replacement visible under ordinary storage faults or component bugs.

### Use only a hash chain without one total sequence

Rejected. ADR-023 recovery needs a simple total order across acceptance, cancellation, publication, and terminal-disposition facts, and deterministic sequence keys make complete-tail enumeration/testability straightforward.

### Permit multiple concurrent journal appends and resolve them later

Rejected. The repository already has one live DO coordinator and serializes the hosted operation. Parallel append branches add unnecessary fork arbitration to recovery-critical state.

### Compact or rotate active epochs automatically

Rejected for v1. Safe compaction requires a new authenticated closure/checkpoint protocol and reopens the same tail/fencing proof. Bounded fail-closed quotas are simpler and safer for the initial release.

### Anchor the journal in an external KMS, transparency service, or second cloud

Rejected for the current threat model. It would add another correctness dependency and failure domain solely to defend against compromise of the Cloudflare administrative/provider boundary which v1 already trusts for plaintext execution, service secrets, and code deployment. If Runethread later promises survival of that compromise, this alternative must be reconsidered as a new architecture change.

### Depend on provider audit logs, webhooks, or GitHub history as the journal

Rejected. They do not provide the exact minimized write-ahead ordering and retention contract required for acceptance/cancellation/terminalization/publication recovery.

## Verification

Implementation satisfies this ADR only if tests/evidence demonstrate at minimum:

1. real R2 integration proves the supported deployment's strong read/list behavior and conditional create-if-absent semantics used by the journal;
2. a normal append linearizes only at successful conditional object creation and advances the DO checkpoint only after exact re-read verification;
3. a lost append response followed by retry at the same sequence/bytes is idempotent and does not create a second successor;
4. a byte-different object already present at the claimed sequence never causes the writer to skip forward and forces recovery/fail-closed handling;
5. process loss after object creation but before DO checkpoint advancement reconstructs the exact append from R2;
6. DO PITR to checkpoint `n` while R2 contains a valid chain through `m > n` enumerates and verifies the complete `0..m` lineage before recovery proceeds;
7. a delayed legitimate pre-recovery append racing the recovery barrier is either incorporated before a later barrier wins or collides with the winning barrier and cannot write beyond it;
8. after a winning recovery barrier at `B`, a fresh complete paginated verification proves the chain ends at `B`; any `>B` record fails closed;
9. multi-page journal listings cannot be mistaken for a complete tail before all cursors are consumed;
10. missing sequence, duplicate/conflicting sequence, malformed key, wrong repository/epoch/version, predecessor-digest mismatch, unsupported serialization, or sequence overflow fails closed;
11. exact duplicate recovery-barrier creation is idempotent while a different record at its sequence is incorporated or rejected according to the deterministic collision rules;
12. ADR-019 acceptance, cancellation, canonical-anchor, and publication-intent write-ahead barriers all use the same sequence lineage;
13. ADR-021 terminal-success evidence references and ADR-023 terminal dispositions share that total order and recovery never resurrects an earlier journaled terminal operation because later work also exists;
14. ADR-018 protected publication intents/outcomes survive DO rollback and remain ordered relative to terminal `COMMITTED` disposition;
15. public clients, finalizers, auditors, and publisher executors cannot choose/create/delete arbitrary journal records or keys;
16. an active binding epoch has no supported compaction/truncation/routine rotation path and hitting configured record/byte bounds enters maintenance before history is discarded;
17. journal records contain no plaintext memory body, GitHub write credential, App private key, or unrestricted provider-error payload;
18. incompatible hosted release/journal versions cannot continue an operation or reopen a recovered lane without the required maintenance/version transition;
19. security/privacy documentation and tests explicitly model Cloudflare account/provider/evidence-store integrity and availability as v1 TCB assumptions and do not claim zero-knowledge or provider-compromise resistance; and
20. a future proposal to survive malicious Cloudflare-account/provider compromise or to compact active journal history is treated as a material architecture change rather than an implementation optimization.

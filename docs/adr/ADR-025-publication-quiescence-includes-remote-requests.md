# ADR-025: Publication quiescence includes remote requests

Status: **Accepted**
Date: 2026-09-06
Tracking issue: #20
Amends: ADR-014, ADR-016, ADR-017, ADR-018, ADR-019, ADR-023, and ADR-024 where they define publication fencing and recovery

## Context

The full architecture review of exact planning head `967446acd8ab45f6d052d6405d4c2c65f5d69b0b` against base `7f5cf86f23604426c7e8f69086fdcbe27fb86226` found a remaining publication-fencing proof gap.

ADR-017 permits recovery from an ambiguous publisher attempt by stopping the executor and waiting for an unconfirmed installation token to expire. That prevents some future client activity, but does not establish that a GitHub request already authenticated/admitted by the server has finished. ADR-019's conservative fencing horizon must also cover delayed gateway/token issuance, rather than assuming every token was minted when the DO first sent the request.

An admissible counterexample is: GitHub admits exact `H0 -> C`; the response/connection/executor is lost while server processing is unresolved; the client is destroyed and its token expires; recovery reads `H0` and assumes quiescence; the old remote transaction later performs its update, possibly after another owner rewind to `H0`. Token expiry is not documented as cancellation of already-admitted Git transactions. This is a gap in the architectural proof, not an observed GitHub production failure.

The same issue applies to an API-based publisher. ADR-024's R2 journal barrier fences fixed-sequence journal writes, not transactions already admitted by another provider.

The review also found stale current-work instructions in issue #20 and ROADMAP.md. Those planning surfaces are synchronized separately; this ADR governs the publication correction.

## Decision

### 1. Quiescence covers the entire publication authority chain

Before releasing a publication lane, abandoning/reusing its generation, issuing another publisher attempt, completing a binding deletion/re-enrollment, or crossing an incompatible deployment barrier, the DO must establish both:

1. **No future issuance or dispatch:** no delayed gateway call, executor start, token grant, refresh, retry, or queued transport action for any prior attempt can initiate another update.
2. **No unresolved remote update:** every ref-update request which might already have reached GitHub has completed or is independently proven unable to update the ref later.

Local process termination, socket closure, a client timeout, token expiry/revocation, a current-ref read, and the R2 `RECOVERY_BARRIER` are not individually proof of the second condition.

Publication history and quiescence are separate facts. Reachability of exact `C` can prove historical publication under ADR-018; it does not prove that every other possibly admitted request is dead. A definitive no-write result for one attempt does not clear an earlier ambiguous attempt.

### 2. The immutable intent bounds future issuance and dispatch

Each ADR-019 publication intent binds the existing exact repository/binding epoch/ref/request/operation/generation/H0/C/audit/release/publisher-attempt identities and, additionally:

- an absolute latest time at which its gateway may begin token issuance;
- an absolute latest time at which the trusted publisher may begin dispatching its one ref update;
- the maximum credential lifetime and supported clock-error margin used by the release;
- the exact publisher transport/protocol used to interpret completion.

These limits are enforced in the trusted gateway/publisher, not merely stored as advisory DO deadlines. A delayed or duplicated call cannot extend them, mint a replacement token under an expired grant, start a replacement executor, or retry an update autonomously. Tokens are never refreshed automatically.

If an already-started token-issuance request returns after the dispatch cutoff, its credential must not be used to publish. The gateway/executor discards or revokes it under the credential policy. Unknown issuance completion remains tracked conservatively; an assumed expiry computed from the original DO send time is insufficient.

The existing one-authoritative-executor and at-most-one-authoritative-push-per-attempt rules continue to apply. Request or response loss cannot cause a second dispatch under the same attempt. After an ambiguous loss of the executor's dispatch state, recovery assumes dispatch may already have happened rather than restarting the push.

A deadline limits trusted client behavior. It does not impose an undocumented deadline on server processing. Clock uncertainty or inability to enforce the cutoff keeps the lane closed.

### 3. Remote completion requires explicit evidence

For the selected transport, the pinned publication protocol must distinguish:

- definitive completion of the exact ref-update request, with exact success or definitive no-write status;
- proof that no request was dispatched and all associated future dispatch/issuance authority is closed; and
- unresolved admission/completion.

For the Git transport, a valid server report-status for the exact command can establish its completed ref-update result when the trusted executor also proves that no other update was dispatched. A generic process exit, HTTP success, or incomplete output is not a substitute for the transport's exact result.

An API transport must prove equivalent exact-request completion and no additional outstanding dispatch. Transport libraries, proxies, and SDKs must not hide retries of a ref mutation. Where the selected environment can duplicate a dispatch, every potentially admitted update must be accounted for; if that set cannot be proven closed, quiescence is unresolved.

A provider-enforced upper bound on already-admitted request completion may be used only when authoritative documentation or a supported provider contract establishes the relevant bound and semantics, the hosted release pins that dependency, and integration tests verify the implementation's use of it. Sampled latency, a client timer, token lifetime, or a successful failure-injection experiment alone does not establish a universal server bound.

### 4. Unproven remote completion remains in doubt

Phase 2.6 v1 does not assume a finite GitHub server-completion bound.

If an update may already have reached GitHub and its completion cannot be proved, the repository remains in `PUBLISHING`/maintenance/reconciliation with the exact candidate and required evidence protected. The service must not automatically release the lane, retry even the same `C`, resume another publication, or declare the attempt definitively not published after a fixed wait.

This is the accepted invariant-preserving fallback for both Git and API publication. It deliberately permits an unbounded availability loss on an unresolved failure path. Product and operations documentation must not promise automatic recovery after one token lifetime.

Operator handling may obtain definitive provider/transport evidence or use an independently proven fence, then resume normal ADR-018 reconciliation. Operator approval, elapsed time, a branch rename, or a reset to `H0` alone is not such proof. Destructive abandonment/rebaseline which would discard this guarantee requires a separate architecture decision; it is not an ordinary incident workaround.

### 5. Recovery preserves publication obligations across all attempts

The existing private evidence boundary stores minimized immutable evidence for issuance/dispatch closure and completed remote update identities. No credential or private memory body is stored in these records.

Before quiescence is used to release/retry/terminalize, the required proof and its exact references must be rollback-independent under ADR-019/ADR-023/ADR-024. Recovery enumerates every relevant journaled intent, including attempts whose local state or response was lost, and reconstructs unresolved authority conservatively.

A restored generation number or an intact old intent is not a reusable publication grant. Earlier grants retain their original limits and possibly-dispatched state. A fresh attempt is authorized only by the current live DO after all prior attempts are proved quiescent and all current binding/privacy/audit/barrier checks pass.

ADR-024's barrier and full-tail proof remain required before normal journal work resumes. Completing that journal protocol does not itself release unresolved publication obligations. Required publication and terminal-proof evidence remains pinned while any supported recovery path still needs it.

### 6. Positive completion and cancellation keep their existing ordering

After all publication authority is quiescent, ADR-018 controls historical outcome and ancestry reconciliation:

- exact `C` or a descendant containing it proves publication;
- `H0` permits a newly authorized attempt for the same exact `C`;
- other history excluding a possible/proven `C` remains reconciliation-required.

ADR-023 additionally requires positive publication evidence and a rollback-independent terminal disposition before durable `COMMITTED(C)` completion/lane release. The v1 path waits for quiescence before returning that terminal result. Status may report a positively observed publication fact while explicitly remaining unresolved; it must not present that status as a lane-releasing terminal disposition.

Cancellation cannot undo `PUBLISHING`. A prepublication cancellation still crosses the existing cancellation/terminal journal barrier. No retry, cancellation, timeout, or operator deadline can erase an outstanding publication obligation.

### 7. Release and implementation gates

The hosted release pins issuance/dispatch deadlines, clock assumptions, credential handling, transport retry behavior, remote completion proof, and their evidence/recovery schemas.

No Core runtime, operational contract, schema, Index format, public template, or private memory bytes change in this architecture amendment. Implementing it is future hosted work under the normal release gates.

The exact-Git publisher remains the concrete expected-old/exact-object path. Its failure recovery must obey this ADR; it is not a promise of bounded automatic recovery. An API optimization cannot bypass the same rule.

## Consequences

- Publication fencing now includes delayed issuance and already-admitted remote work.
- Token expiry is a credential fact, not an implicit remote cancellation primitive.
- Normal definitive publication remains inexpensive; unresolved remote completion may block indefinitely.
- No extra live coordinator, semantic engine, workflow, provider, or mutable journal head is added.
- The prior reviewed head fails the zero-edit gate. A fresh full review of the synchronized head containing this ADR is required.

## Alternatives considered

- **Wait one token lifetime, then assume safety:** rejected because authentication expiry does not prove completion of already-admitted work.
- **Destroy the Container or close the connection:** necessary in some failure paths, but insufficient evidence about server processing.
- **Retry the same C while an earlier request remains live:** rejected because a later rewind could allow the old update to act after lane release.
- **Infer a universal bound from integration tests:** rejected. Tests exercise behavior but do not create an absent provider guarantee.
- **Add another coordinator:** rejected. The missing property is remote quiescence evidence, not scheduling ownership.

## Verification

Implementation evidence must cover:

1. delayed gateway delivery after issuance cutoff cannot mint a new usable publication grant;
2. token issuance completes late: no update begins after dispatch cutoff and no replay extends the original limits;
3. crash before/after dispatch cannot cause another authoritative update under the same attempt;
4. a fake GitHub transport admits an update, withholds completion beyond token expiry, and later updates the ref: recovery never releases/retries in the unresolved interval;
5. stopping the executor/revoking the token does not falsely complete that remote request;
6. hidden SDK/proxy retries are disabled or all possible updates are included in the completion proof;
7. definitive exact server success/no-write completion plus closed client authority permits ordinary reconciliation;
8. a current ref containing C proves historical success but does not erase another unresolved request;
9. PITR before issuance, after issuance, after dispatch, and after completion reconstructs every relevant attempt from immutable evidence;
10. later no-write results cannot discharge earlier ambiguous attempts;
11. binding deletion, re-enrollment and incompatible rollout remain blocked by unresolved remote authority;
12. normal candidate/terminal independent verification, exact expected-old publication, cancellation ordering and ADR-023 dispositions remain unchanged;
13. implementation and operations expose indefinite in-doubt state honestly; no timer or support action silently converts uncertainty to no-write.

## Provider evidence checked during review

- [GitHub installation authentication](https://docs.github.com/en/apps/creating-github-apps/authenticating-with-a-github-app/authenticating-as-a-github-app-installation): installation tokens have bounded expiry and support repository/permission narrowing. It does not document cancellation of admitted ref updates at expiry.
- [Git protocol capabilities](https://git-scm.com/docs/gitprotocol-capabilities): report-status reports the outcome after unpacking and ref update. The selected publisher must validate the exact command result.
- [R2 consistency](https://developers.cloudflare.com/r2/reference/consistency/): strong object reads/listings support the journal, not cross-provider transaction cancellation.

These are documentation checks. Real provider integration compliance remains untested until hosted implementation.

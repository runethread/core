# Runethread licensing

Runethread uses a **mixed licensing boundary** so the implementation can be source-available without making the portable memory protocol or user-owned repositories commercially restrictive.

## Implementation default — PolyForm Perimeter 1.0.1

Unless material is explicitly included in the narrow MIT interoperability exception below or carries its own explicit license, current Runethread-owned source in this `runethread/core` repository for which the licensor controls the necessary licensing rights is offered under the **PolyForm Perimeter License 1.0.1**. See [`LICENSE`](LICENSE).

The current licensor for that Runethread-owned implementation material is **George Karageorgiou**. The GitHub organization name `runethread` is not treated as a separate legal rights holder merely because it owns repositories.

`runethread/hosted` must adopt the same Perimeter implementation default through its own reviewed licensing transition before any hosted runtime/Worker source is merged. This Core document does not claim that Hosted has already completed that transition.

## Permissive interoperability boundary — MIT

The MIT exception is intentionally **closed and enumerated**. Perimeter is the default everywhere else. Repository location, a file's apparent purpose, future membership in a contract/bootstrap mechanism, or output from a Runethread tool does **not** automatically place material under MIT.

### Exact Core file allowlist

Only the following current Core repository files are inside the MIT interoperability exception:

- `MEMORY_PROTOCOL.md`
- `schema/memory-item.schema.json`
- `docs/MEMORY_SCHEMA.md`
- `docs/MEMORY_CONTENT_FORMAT.md`
- `docs/TAXONOMY.md`
- `docs/REPOSITORY_VALIDATION.md`
- `docs/USER_COMMANDS.md`
- `docs/EXTENDING_RUNETHREAD.md`
- `docs/TRUST_MODEL.md`
- `docs/SOURCES.md`
- `docs/INDEX_FORMAT.md`
- `templates/fact.md`
- `templates/preference.md`
- `templates/decision.md`
- `templates/state.md`
- `templates/open_loop.md`
- `templates/correction.md`
- `templates/milestone.md`
- `templates/reference.md`
- `AI_SETUP.md`
- `runethread-bootstrap.json`

The first nineteen paths above are the current operational-contract set. **`ContractPaths()` does not define or enlarge the MIT license boundary.** The licensing guard independently pins the exact MIT contract allowlist and requires both `ContractPaths()` and the resolved `ContractFS` embed set to match it. Adding, removing, renaming, or otherwise changing membership requires an explicit licensing/contract-packaging review and coordinated policy update; absent that reviewed update, a new Core file remains under the Perimeter default and must not be exported as MIT interoperability material.

No Go implementation file, Python/script implementation file, internal runtime package, test implementation, Core CI/release workflow, Hosted source, finalizer, auditor, publisher, mutation engine, index implementation, validation implementation, trust implementation, or other executable/product implementation source is included merely because it supports or consumes these files.

### Narrow generated-output exception

Runethread also grants MIT terms to the **Runethread-authored generated support bytes themselves** when supported `runethread init` or `runethread upgrade` flows emit managed support material into a memory repository at these exact paths:

- `.gitattributes`
- `README.md`
- `.github/workflows/validate.yml`
- `.runethread/config.json`
- `.runethread/lock.json`

This is an output exception, not a source-code exception. The Core generator/runtime source that produces those bytes remains under the Perimeter implementation default. Arbitrary user-authored content at the same path is not licensed to Runethread and is not converted to MIT by the pathname. Empty placeholders and user/derived data such as memories, projects, attachments, and generated indexes are not swept into the software-license grant by this exception.

A future generated support path or other export is **not** MIT automatically. It requires explicit review and an update to this closed boundary before distribution under MIT.

The MIT terms are in [`LICENSE-MIT`](LICENSE-MIT). This split intentionally lets other clients and assistants understand, copy, redistribute, and implement the Runethread memory interoperability layer without receiving a permissive license to reuse post-transition Perimeter-covered Core or Hosted implementation code in a competing product.

## Historical MIT material

Runethread was originally distributed under the MIT License. Existing MIT grants are not revoked.

For `runethread/core`, the canonical default-license transition occurs when protected `main` first adopts ADR-026 and this licensing state. Public development-branch snapshots that already contain newly authored Perimeter-designated material are offered under the license terms stated in those snapshots for that new material; publishing such a branch does not revoke or narrow MIT rights already granted to pre-transition material.

All Core releases published before the canonical `main` transition, including v0.9.0 and earlier releases, remain available under the MIT terms under which they were released. The historical grant also continues to apply to pre-transition material that a recipient obtained under MIT, including unchanged portions that may still appear in a later source tree. Relicensing the current repository does not make those previously granted MIT rights disappear.

Post-transition Runethread-authored changes to files covered by the Perimeter implementation default are not automatically licensed under the historical MIT grant. A recipient may continue using older MIT-covered material under MIT, but does not obtain MIT rights to later Perimeter-only changes merely because those changes descend from the same Git history.

`LICENSE-MIT` therefore serves both as the preserved historical Core MIT text and as the current license notice for the explicit interoperability exception above.

## User repositories and user data

ADR-026 does **not** license user-authored memories, project content, imports, attachments, or other user-owned data to Runethread. No such right is granted merely because Runethread tooling stores, indexes, validates, transports, or processes that data.

The public `runethread/memory-template` is deliberately an **MIT interoperability/bootstrap repository, not an implementation repository**. Its role must remain limited to portable contract/bootstrap/support material and non-user placeholder structure. Valuable Runethread implementation code must stay in Perimeter-covered implementation repositories rather than being moved into the MIT template.

The public template is already an active distribution of Runethread-authored MIT interoperability material. After the protected Core ADR-026 transition, first establish basic protected-`main` policy on the template, then land its scoped MIT license/copyright notice through its own protected, reviewed change. That notice remediation does not create the underlying MIT grant, license user-authored memory/project data, or change the contract-v9 managed contract bytes or lock identity.

Existing user-owned/private memory repositories are **not** modified merely to add a notice file. The immutable v0.9.0 starter/upgrader behavior remains historical evidence. Before any later Core release is unblocked, the versioned starter/upgrader/release path must make the MIT license/copyright notice available with Runethread-managed MIT interoperability material it generates or upgrades, using the normal bootstrap/version/release/downstream gates rather than opportunistic user-repository edits.

## Readable-text licensing consistency

Licensing consistency is a repository-wide text/content invariant, not a convention limited to `LICENSE`, this file, or the current planning documents.

Core CI enumerates the Git-tracked manifest. A tracked regular file must be valid UTF-8 text unless its exact path is deliberately classified in the reviewed binary/non-text allowlist. The current Core tree requires no such binary exception. NUL-bearing or invalid-UTF-8 regular files therefore fail closed by default, and tracked symlinks/submodules/other non-regular objects are not silently skipped. A future genuine binary or non-regular tracked object must receive an explicit reviewed exception rather than becoming an invisible licensing-text bypass.

If tracked UTF-8 text contains licensing/rightsholder/commercial-model vocabulary, it must belong to the deliberately classified licensing-bearing text surface. The vocabulary includes license/licensor terms as well as copyright, copyleft, patent, trademark, source-available/open-source, commercial/noncommercial, dual/relicensing, proprietary/public-domain, and equivalent explicit rights-policy markers. A new readable file that begins discussing those subjects therefore fails closed until its role is reviewed and classified.

The same scan rejects known contradictory global claims wherever they appear, including stale present-tense statements that make all of Runethread MIT-only or describe the Perimeter-covered implementation as open source. Historical licensing/source fixtures are not exempted by a broad directory rule: if a faithful historical fixture needs to preserve wording that would otherwise look stale, the guard permits only an **exact path + exact SHA-256** historical-text exception. Changing the fixture bytes invalidates that exception and requires review.

The authoritative licensing files and required human/agent entrypoints are also checked for positive markers, so a file cannot evade review simply by deleting all licensing language. This gives the repository complementary protections: positive assertions on the files that must explain policy, a closed MIT allowlist, exact legal-text locks, and a repository-wide contradiction/classification scan. Files unrelated to licensing do **not** need boilerplate licensing prose merely to pass the guard.

`runethread/hosted` must adopt an equivalent repository-local consistency guard as part of its ADR-026 transition. The public `runethread/memory-template` remains deliberately smaller: it stays an implementation-free MIT interoperability/bootstrap repository, its notice is landed through protected review, and existing private/user repositories are not swept or relicensed by Core CI.

## Binary and release distribution

PolyForm Perimeter requires downstream recipients of covered software to receive the license terms or their URL and every `Required Notice:` supplied with the software. Core binaries also embed the exact MIT-listed operational-contract files through `ContractFS`, so a post-transition binary distribution is a **mixed-license distribution** and must also provide the MIT license and copyright notice applicable to that embedded material.

The existing v0.9.0 release remains an MIT-era release. **No post-transition Core release may be requested or published until the release packaging path is updated and verified to carry both (1) the applicable Perimeter terms/URL and every `Required Notice:` for Perimeter-covered implementation and (2) the MIT license/copyright notice for embedded or otherwise distributed interoperability material.** The current release workflow enforces this temporarily by rejecting every requested version other than the already-published v0.9.0 baseline. A future reviewed packaging change must replace that fail-closed gate deliberately and preserve the existing immutable-release and exact-asset verification gates.

## Current commercial model

PolyForm Perimeter permits use, modification, and distribution for permitted purposes while excluding use of the licensed software to provide others a product that competes with the software.

Implementation material covered by PolyForm Perimeter is therefore **source-available**, not OSI-approved open source. The explicitly MIT-licensed interoperability material remains open-source under MIT.

The licensor may separately offer commercial licenses, exceptions, partnerships, or other terms. Runethread's own monetization model is not restricted to any one mechanism and may include hosted service revenue, subscriptions, advertising, sponsorship, support, or separate commercial licensing.

## Independent implementations and trademarks

The software licenses govern rights in the licensed Runethread material. They do not purport to create copyright protection for ideas, facts, functionality, or other material that copyright law does not protect, and they do not convert an independently created implementation into Runethread-licensed software merely because it implements compatible concepts or interfaces.

Software licensing also does not grant rights to represent an independent product as official Runethread. Branding and trademark policy may be documented separately.

## Contributions and licensing rights

Repository ownership and Git commit metadata are evidence, not a substitute for copyright ownership or an inbound rights grant. Runethread may license only material for which the applicable rightsholder has granted the necessary rights.

Before material third-party source contributions are merged, Runethread must adopt an explicit inbound-contribution policy that preserves the rights required by the contribution's target licensing class. For Perimeter-covered implementation, that policy must preserve the project's intended source-available model and any separately offered commercial licensing. A contribution must not be merged on the assumption that repository ownership or a DCO-style origin certification automatically grants relicensing rights.

## Legal review

ADR-026 is an engineering and product-governance decision, not legal advice. Before material commercial contracts, corporate rights transfers, license enforcement, or other high-consequence legal action, the relevant licensing and ownership terms should be reviewed by qualified legal counsel for the applicable jurisdiction.

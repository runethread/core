# Runethread licensing

Runethread uses a **mixed licensing boundary** so the implementation can be source-available without making the portable memory protocol or user-owned repositories commercially restrictive.

## Implementation default — PolyForm Perimeter 1.0.1

Unless a file or class of material is listed below under the permissive interoperability boundary or carries its own explicit license, current Runethread-owned source in this `runethread/core` repository for which the licensor controls the necessary licensing rights is offered under the **PolyForm Perimeter License 1.0.1**. See [`LICENSE`](LICENSE).

The current licensor for that Runethread-owned implementation material is **George Karageorgiou**. The GitHub organization name `runethread` is not treated as a separate legal rights holder merely because it owns repositories.

`runethread/hosted` must adopt the same Perimeter implementation default through its own reviewed licensing transition before any hosted runtime/Worker source is merged. This Core document does not claim that Hosted has already completed that transition.

## Permissive interoperability boundary — MIT

Runethread's portable memory contract and user-repository interoperability material remain available under the **MIT License** in [`LICENSE-MIT`](LICENSE-MIT). The Perimeter default is not intended to restrict use of this interoperability layer.

This MIT boundary includes:

- the files named by the released operational contract's `ContractPaths()` manifest in `contract.go`, including `MEMORY_PROTOCOL.md`, the vendored memory schema, contract documentation, and memory-authoring templates;
- `AI_SETUP.md` and `runethread-bootstrap.json` as public onboarding/bootstrap interfaces; and
- Runethread-authored managed support/contract material emitted into a user-owned memory repository by supported `runethread init` or `runethread upgrade` flows, to the extent Runethread holds the rights necessary to grant that license.

A future change to which files belong to this permissive interoperability boundary is a licensing/contract-packaging decision and must be explicit. It must not be inferred merely from repository location.

This split intentionally lets other clients and assistants understand and implement the Runethread memory contract without receiving a license to reuse post-transition Perimeter-covered Core or Hosted implementation code in a competing product.

## Historical MIT material

Runethread was originally distributed under the MIT License. Existing MIT grants are not revoked.

For `runethread/core`, the protected merge commit that first introduces ADR-026 and this licensing transition is the repository transition point. All Core releases published before that transition, including v0.9.0 and earlier releases, remain available under the MIT terms under which they were released.

The historical grant also continues to apply to pre-transition material that a recipient obtained under MIT, including unchanged portions that may still appear in a later source tree. Relicensing the current repository does not make those previously granted MIT rights disappear.

Post-transition Runethread-authored changes to files covered by the Perimeter implementation default are not automatically licensed under the historical MIT grant. A recipient may continue using the older MIT-covered material under MIT, but does not obtain MIT rights to later Perimeter-only changes merely because those changes descend from the same Git history.

`LICENSE-MIT` therefore serves both as the preserved historical Core license text and as the current license for the explicit permissive interoperability boundary above.

## User repositories and user data

ADR-026 does **not** license user-authored memories, project content, imports, attachments, or other user-owned data to Runethread. No such right is granted merely because Runethread tooling stores, indexes, validates, transports, or processes that data.

ADR-026 also does not silently relicense `runethread/memory-template` or an existing user-owned memory repository as a whole. The current public template and known contract-v9 memory repositories remain pinned to v0.9.0 / MIT-era managed contract material.

The public `runethread/memory-template` is already an active distribution of Runethread-authored MIT interoperability material. After the protected Core ADR-026 transition, the template must receive a scoped copy of the MIT license/copyright notice through its own protected, reviewed change. That remediation licenses only the Runethread-authored MIT interoperability material it distributes; it does not license user-authored memory/project data and does not change the contract-v9 managed contract bytes or lock identity.

Existing user-owned/private memory repositories are **not** modified merely to add a notice file. The immutable v0.9.0 starter/upgrader behavior remains historical evidence. Before any later Core release is unblocked, the versioned starter/upgrader/release path must make the MIT license/copyright notice available with Runethread-managed MIT interoperability material it generates or upgrades, using the normal bootstrap/version/release/downstream gates rather than opportunistic user-repository edits.

## Binary and release distribution

PolyForm Perimeter requires downstream recipients of covered software to receive the license terms or their URL and every `Required Notice:` supplied with the software. Core binaries also embed the MIT-covered `ContractFS` interoperability material from `contract.go`, so a post-transition binary distribution is a **mixed-license distribution** and must also provide the MIT license and copyright notice applicable to that embedded material.

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

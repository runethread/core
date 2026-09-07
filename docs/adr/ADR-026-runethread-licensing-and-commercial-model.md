# ADR-026: Runethread licensing and commercial model

Status: **Accepted**
Date: 2026-09-07
Tracking issue: #20

## Context

Runethread was initially published under the MIT License during architecture, bootstrap, and early implementation. MIT permits broad commercial reuse, including use, modification, distribution, sublicensing, sale, and use of the licensed implementation as the basis of a competing product or hosted service.

That does not match the intended long-term commercial boundary for Runethread's implementation. Runethread should remain publicly inspectable and broadly usable while preserving the project's ability to monetize its own implementation and hosted services without granting third parties an unrestricted right to reuse future Runethread implementation changes in a competing product.

The licensing decision must land before the first `runethread/hosted` runtime/Worker source is merged so valuable hosted implementation does not inherit the bootstrap MIT state by accident.

Historical MIT grants cannot be retroactively revoked. Pre-transition material remains available under the MIT rights already granted, including unchanged portions that may still appear in later source trees. The meaningful prospective restriction is therefore on post-transition Runethread-authored implementation changes, not an attempted clawback of old MIT code.

Runethread also has a portability/interoperability requirement. The operational memory contract, schema, authoring templates, bootstrap interfaces, and Runethread-managed support material copied into user-owned memory repositories need to remain broadly implementable and distributable. Applying a noncompetition license to that interoperability layer would create unnecessary friction and notice obligations for user repositories and could undermine the project's cross-client protocol goals.

The decision therefore needs a deliberate mixed boundary: source-available protection for Core/Hosted implementation, permissive licensing for the portable memory contract/interoperability layer, and no license claim over user-authored memory data.

## Decision

### 1. Runethread implementation defaults to PolyForm Perimeter 1.0.1

Runethread adopts the **PolyForm Perimeter License 1.0.1** as the default license for Runethread-owned implementation material in `runethread/core` and, through a separate reviewed transition, `runethread/hosted`, to the extent the applicable licensor controls the rights necessary to make that grant.

PolyForm Perimeter permits use, modification, and distribution for permitted purposes while excluding use of the licensed software to provide others a product that competes with the software. Competition can include products or services delivered through different interfaces, platforms, languages, libraries, plug-ins, or deployment models, including free substitutes.

This choice is intended to prevent direct commercial or free-service cloning based on post-transition Runethread implementation while still permitting non-competing use, including use by commercial organizations.

The current Core repository carries the official PolyForm Perimeter 1.0.1 terms in `LICENSE` plus the required notice identifying George Karageorgiou. `runethread/hosted` remains under its existing state until its own protected licensing transition is reviewed and merged; this ADR does not pretend that transition has already occurred.

### 2. The portable Memory Contract and interoperability layer remain MIT

The Perimeter default does not apply exclusively to Runethread's portable interoperability layer. The following Runethread-authored material remains available under the **MIT License** in `LICENSE-MIT`:

- files named by the released operational contract's `ContractPaths()` manifest in `contract.go`, including `MEMORY_PROTOCOL.md`, the vendored schema, contract documentation, and memory-authoring templates;
- `AI_SETUP.md` and `runethread-bootstrap.json`; and
- Runethread-authored managed support/contract material emitted into user-owned memory repositories by supported `runethread init` or `runethread upgrade` flows, to the extent Runethread controls the necessary rights.

A future change to the membership of this permissive interoperability boundary is a licensing/contract-packaging decision and must be explicit. It must not be inferred from repository location or from a root license file alone.

The purpose of this split is to let assistants, clients, tools, and independent implementations consume and implement the Runethread memory protocol without receiving a permissive license to reuse post-transition Perimeter-covered Core or Hosted implementation code in a competing product.

### 3. Historical MIT rights remain intact

The transition does not revoke or rewrite rights already granted under MIT.

Each implementation repository has its own transition point: the protected merge commit that first adopts ADR-026's licensing state in that repository. For `runethread/core`, releases and source published before its transition, including v0.9.0 and earlier releases, remain available under the MIT terms under which they were released.

Those prior grants continue to cover the pre-transition material a recipient obtained under MIT, including unchanged portions that may still be present in a later tree. Offering the later repository under Perimeter does not erase those existing rights.

Post-transition Runethread-authored changes to implementation-default files are not automatically licensed under the historical MIT grant. A recipient may continue using the older MIT-covered material under MIT, but does not obtain MIT rights to later Perimeter-only changes merely because those changes share Git history with the older material.

`LICENSE-MIT` is therefore both the preserved historical Core license text and the current license for the explicit permissive interoperability boundary in Decision 2.

### 4. User repositories and user data are separate rights boundaries

ADR-026 does not license `runethread/memory-template` or a user-owned memory repository as a whole under Perimeter.

The current public memory template and known contract-v9 memory repositories remain pinned to v0.9.0 / MIT-era managed material. Future template/repository packaging must preserve the explicit interoperability/user-data split rather than relying on a repository-root implementation license.

No right in user-authored memories, project content, imports, attachments, or other user-owned data is granted to Runethread merely because Runethread tooling stores, indexes, validates, transports, or processes that data.

When future releases generate or upgrade Runethread-managed files in user repositories, the applicable managed-file terms/notices must be made available without implying that those terms cover user-authored data.

### 5. Core and Hosted implementation policy must align prospectively

Future Runethread-owned implementation work in both `runethread/core` and `runethread/hosted` uses the Perimeter default unless an explicit recorded exception applies.

Restricting only Hosted while continuing to publish new Core implementation changes under MIT would leave a broad commercial reuse path through Core and would not express the intended product-level commercial policy.

Hosted has its own historical MIT boundary and must perform its own protected transition. The first Hosted runtime/Worker source remains blocked until that transition is complete.

### 6. Perimeter-covered implementation is source-available, not OSI open source

PolyForm Perimeter contains a competition restriction. Runethread documentation and product language must therefore describe implementation material covered by Perimeter as **source-available**, not OSI-approved open source.

The explicitly MIT-licensed interoperability layer and historical MIT releases remain open-source software under their applicable MIT terms.

### 7. Runethread retains commercial flexibility

The applicable rightsholder may operate and monetize Runethread, including through hosted services, subscriptions, advertising, sponsorship, support, or other models.

The applicable rightsholder may also offer separate commercial licenses, exceptions, partnerships, or alternative terms for material whose rights permit those grants.

ADR-026 does not commit Runethread to any one revenue model.

### 8. Licensor and rights scope are explicit

At this transition, the repository history identifies **George Karageorgiou** as the author identity for the reachable Core history. Until an explicit legal-rights transfer or successor decision is recorded, George Karageorgiou is the stated licensor for Runethread-owned Perimeter implementation material for which he controls the necessary rights.

The GitHub organization name `runethread` is not treated as a separate legal rights holder merely because it owns repositories.

Repository ownership, commit metadata, or project maintenance authority must never be treated as automatic proof of copyright ownership for future third-party contributions. A future company or other entity may become a licensor only through an explicit rights/governance transition covering the relevant material.

### 9. Independent implementations remain bounded by ordinary copyright law

These licenses govern rights in licensed Runethread material. They do not purport to create copyright protection for ideas, facts, functionality, or other material that copyright law does not protect.

An independently created implementation does not become licensed Runethread software merely because it implements compatible concepts, protocols, or interfaces. The deliberate MIT interoperability boundary in Decision 2 further supports compatible implementations without granting a permissive license to Perimeter-covered implementation code.

Trademark and branding rights are separate from software copyright licensing.

### 10. Third-party contribution rights must be deliberate

Before material third-party source contributions are merged, Runethread must adopt an explicit inbound-contribution policy appropriate to the contribution's target licensing class.

For Perimeter-covered implementation, the inbound grant must preserve the project's ability to distribute the contribution under the source-available model and any separately offered commercial terms the project intends to support. Maintainers must not assume that repository ownership, merge access, or a DCO-style origin certification automatically grants separate relicensing rights.

For MIT interoperability material, the contribution path must likewise establish sufficient rights to distribute the contribution under MIT.

### 11. Post-transition release distribution has an explicit notice gate

PolyForm Perimeter requires anyone receiving a copy of covered software to receive the terms or their URL and every plain-text `Required Notice:` supplied with the software.

The current v0.9.0 release remains an MIT-era release and no release is created by this ADR. **No post-transition Core release may be requested or published until the release packaging path is updated and verified to carry the applicable Perimeter terms/URL and Required Notice with every Perimeter-covered binary/artifact distribution.**

That future packaging change must preserve Runethread's immutable-release, exact-target, checksum, complete-asset, and post-publication verification gates rather than weakening release safety to satisfy licensing.

### 12. No hosted runtime or provider resource is introduced here

This ADR is a licensing/governance change. It introduces no Cloudflare runtime, provider resource, secret, Durable Object, R2 bucket, GitHub App, publisher, hosted mutation API, or hosted memory-operation implementation.

## Consequences

- Post-transition Runethread-authored Core/Hosted implementation changes can be source-visible without granting an unrestricted right to use those new changes in a competing product.
- Pre-transition MIT material remains commercially reusable under its existing MIT grants; ADR-026 does not claim otherwise.
- The portable Memory Contract/bootstrap/generated-support interoperability layer remains permissively usable under MIT.
- Businesses may use Perimeter-covered implementation for non-competing purposes under PolyForm Perimeter.
- Runethread can monetize material for which it controls the required rights and may offer separate commercial terms.
- Perimeter-covered implementation must be described as source-available rather than OSI open source; MIT-covered interoperability material remains open source.
- `runethread/memory-template`, existing user memory repositories, and user-authored data are not silently relicensed by this ADR.
- A future post-transition binary release has a mandatory license/Required-Notice packaging gate.
- A competitor can still use historical MIT material and can independently implement ideas/interfaces to the extent copyright law permits; Perimeter is not a patent or a general noncompetition right over abstract functionality.
- Contributor governance becomes a prerequisite before material outside source is merged.
- License enforceability and ownership questions can depend on jurisdiction and facts; material commercial contracts, rights transfers, or enforcement should receive qualified legal review.

## Alternatives considered

### MIT for all future implementation

Rejected because it would continue to permit unrestricted commercial reuse, sublicensing, sale, and competing products based on future Runethread implementation changes.

### GNU AGPLv3

Rejected as the primary commercial-protection mechanism. AGPL is strong network copyleft and can require corresponding source availability for modified network software, but it permits commercial use and does not prohibit a compliant competing hosted service.

### PolyForm Noncommercial 1.0.0

Rejected because it restricts commercial-purpose use too broadly for the intended adoption model. Runethread does not need to prohibit ordinary non-competing use merely because the user is a commercial organization.

### PolyForm Shield 1.0.0

Rejected because its noncompetition boundary extends beyond competition with the licensed software to products the licensor or affiliates provide using the software. That creates a broader and more dynamic restriction than Runethread currently needs.

### Perimeter for the entire Core repository with no interoperability exception

Rejected because the operational contract/schema/templates/bootstrap material is deliberately portable across clients and copied into user-owned repositories. Applying the noncompetition default to that whole layer would create avoidable interoperability and downstream notice friction without materially improving protection of the actual implementation.

### Hosted-only restriction with future Core implementation left MIT

Rejected because it leaves a broad commercial reuse path through future Core implementation and creates an incoherent implementation-level commercial policy.

### Blanket relicensing of template and user repositories

Rejected because template/generated repositories mix Runethread-managed artifacts with user-owned data and have a separate portability/distribution boundary. Licensing of managed artifacts must never imply a license grant over user-authored memory content.

## Verification

The Core side of the licensing transition is complete only when:

1. this ADR is indexed as accepted in the Core ADR catalog and synchronized into current milestone/process/roadmap authority;
2. Core's root `LICENSE` contains the official PolyForm Perimeter 1.0.1 terms plus the allowed `Required Notice:` identifying George Karageorgiou;
3. `LICENSE-MIT` preserves the historical Core MIT text and `LICENSING.md` explicitly identifies it as the current license for the permissive interoperability boundary as well as historical material;
4. `LICENSING.md` distinguishes Perimeter implementation, MIT interoperability/generated-support material, historical MIT rights, and user-owned data without claiming retroactive revocation;
5. Core README describes the mixed boundary and links the authoritative licensing explanation;
6. project engineering policy, PR review surface, CODEOWNERS, and development-policy guard protect licensing/rightsholder/contribution/notice changes as deliberate governance work;
7. the current release request remains v0.9.0 and this transition does not publish a new release;
8. no post-transition Core release can be treated as ready until release packaging is updated/verified to convey the applicable Perimeter terms/URL and Required Notice with covered artifacts;
9. `runethread/memory-template`, existing user repositories, and user-authored data are not silently relicensed;
10. Hosted adopts the Perimeter implementation default, explicit current licensor/rightsholder scope, and its own historical MIT boundary through a separate protected PR before any runtime/Worker source is merged;
11. Hosted documentation records ADR-026 as the controlling licensing decision rather than leaving the long-term model unresolved;
12. no documentation describes Perimeter-covered implementation as OSI open source;
13. material third-party contributions remain merge-blocked until an explicit inbound-rights policy exists for the relevant licensing class; and
14. the Core and Hosted licensing PRs each pass repository validation and the full exact-head adversarial review gate before protected merge.

## Sources checked for the decision

- PolyForm Perimeter License 1.0.1: <https://polyformproject.org/licenses/perimeter/1.0.1>
- PolyForm license comparison: <https://polyformproject.org/licenses>
- GNU AGPLv3: <https://www.gnu.org/licenses/agpl-3.0.html>
- Open Source Definition: <https://opensource.org/osd>

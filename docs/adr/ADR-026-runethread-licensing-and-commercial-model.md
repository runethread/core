# ADR-026: Runethread licensing and commercial model

Status: **Accepted**
Date: 2026-09-07
Tracking issue: #20

## Context

Runethread was initially published under the MIT License during architecture, bootstrap, and early implementation. MIT permits unrestricted commercial reuse, including use, modification, distribution, sublicensing, sale, and use as the basis of a competing product or hosted service.

That does not match the intended long-term commercial boundary. Runethread should remain publicly inspectable and broadly usable, while preserving the project's ability to monetize its own software and hosted services without granting third parties an unrestricted right to use Runethread's implementation to provide a competing product.

The licensing decision must land before the first `runethread/hosted` runtime/Worker source is merged so that valuable hosted implementation does not inherit the bootstrap MIT state by accident.

Historical MIT grants cannot be retroactively revoked. Existing releases and commits already distributed under MIT retain those terms for recipients of those versions.

The decision also needs a coherent scope across Runethread repositories. Restricting only `runethread/hosted` while leaving future `runethread/core` implementation under MIT would preserve a broad commercial reuse path through Core and would not express one project-wide commercial policy.

## Decision

### 1. Current Runethread-owned source uses PolyForm Perimeter 1.0.1

Runethread adopts the **PolyForm Perimeter License 1.0.1** for current Runethread-owned source unless a file or repository has an explicitly documented different license.

The license permits use, modification, and distribution for permitted purposes. Its noncompete boundary excludes using the licensed software to provide others a product that competes with the software. Competition can include products or services delivered through different interfaces, platforms, languages, libraries, plug-ins, or deployment models, including products provided free of charge when they substitute for the licensed software's functionality or value.

This choice is intended to prevent direct commercial or free-service cloning based on Runethread's licensed implementation while still permitting non-competing use, including use by commercial organizations.

### 2. The transition is prospective with respect to historical MIT grants

The transition does not revoke or rewrite rights already granted under MIT.

The merge commit that first introduces this ADR and the associated licensing files is the licensing transition point. Releases and source published before that transition, including v0.9.0 and earlier releases, remain available under the MIT terms under which they were released. The historical MIT text is retained as `LICENSE-MIT`.

The current source tree may be offered under PolyForm Perimeter even though earlier versions of some of its files were previously offered under MIT. Recipients of an earlier MIT version retain their MIT rights to that earlier version; those rights do not automatically extend to later Runethread-authored changes released only under the new terms.

### 3. The policy is Runethread-wide for owned implementation source

The intended policy applies to Runethread-owned implementation source in both `runethread/core` and `runethread/hosted`, rather than only Hosted.

Repository- or file-specific exceptions require an explicit recorded decision and must not be inferred from historical repository defaults.

### 4. Runethread is source-available, not OSI open source, under Perimeter

PolyForm Perimeter contains a competition restriction. Runethread documentation and product language must therefore describe source covered by this license as **source-available**, not OSI-approved open source.

Historical MIT-licensed releases remain open-source software under their historical terms.

### 5. Runethread retains commercial flexibility

The licensor may operate and monetize Runethread, including through hosted services, subscriptions, advertising, sponsorship, support, or other models.

The licensor may also offer separate commercial licenses, exceptions, partnerships, or alternative terms to parties whose desired use is not permitted by PolyForm Perimeter.

ADR-026 does not commit Runethread to any one revenue model.

### 6. Licensor identity is explicit

Until an explicit legal-rights transfer or successor decision is recorded, the licensor for Runethread-owned source is **George Karageorgiou**. The GitHub organization name `runethread` is not treated as a separate legal rights-holding entity merely because it owns repositories on GitHub.

A future company or other entity may become the licensor only through an explicit rights and governance transition.

### 7. Independent implementations and compatibility remain bounded by ordinary copyright law

This license governs use of the licensed Runethread software. It does not purport to create copyright protection for ideas, facts, functionality, or other material that copyright law does not protect.

An independently created implementation does not become licensed Runethread software merely because it implements compatible concepts, protocols, or interfaces. Trademark and branding rights are separate from software copyright licensing.

### 8. Third-party contribution rights must be deliberate

Before material third-party source contributions are merged, Runethread must adopt an explicit inbound-contribution policy that preserves the rights required for the intended source-available and separate-commercial-licensing model.

Maintainers must not assume that accepting a contribution automatically grants the right to relicense that contribution under separate commercial terms. A DCO-style origin certification by itself must not be treated as a substitute for any additional rights grant the chosen commercial model may require.

### 9. The hosted runtime gate is satisfied only after both repositories reflect the decision

This ADR establishes the Core authority for the licensing model. The first Hosted runtime/Worker source remains blocked until `runethread/hosted` adopts the same current licensing state and records the historical MIT boundary.

No Cloudflare runtime, provider resource, secret, Durable Object, R2 bucket, GitHub App, publisher, or hosted memory-operation implementation is introduced by this licensing change.

## Consequences

- Future Runethread-owned source is not available for unrestricted competing-product use under MIT.
- Businesses can still use the licensed software for non-competing purposes under PolyForm Perimeter.
- Runethread can monetize its own software and may offer separate commercial terms.
- Source covered by Perimeter must be described as source-available rather than OSI open source.
- Historical MIT versions remain usable under their existing MIT grants.
- A competitor can still independently implement ideas or interfaces to the extent copyright law permits; this license is not a patent or general noncompetition right over abstract functionality.
- Contributor governance becomes a prerequisite before material outside source is merged if Runethread wants to preserve broad commercial-licensing flexibility.
- License enforceability and ownership questions can depend on jurisdiction and facts; material commercial contracts, rights transfers, or enforcement should receive qualified legal review.

## Alternatives considered

### MIT

Rejected for current/future implementation because it expressly permits unrestricted commercial reuse, sublicensing, sale, and competing products.

### GNU AGPLv3

Rejected as the primary commercial-protection mechanism. AGPL is strong network copyleft and can require corresponding source availability for modified network software, but it intentionally permits commercial use and does not prohibit a compliant competing hosted service.

### PolyForm Noncommercial 1.0.0

Rejected because it restricts commercial-purpose use too broadly for the intended adoption model. Runethread does not need to prohibit ordinary non-competing use merely because the user is a commercial organization.

### PolyForm Shield 1.0.0

Rejected because its noncompetition boundary extends beyond competition with the licensed software to products the licensor or affiliates provide using the software. That creates a broader and more dynamic restriction than Runethread currently needs.

### Per-repository licensing with Hosted restricted and Core MIT

Rejected because it leaves a broad commercial reuse path through future Core implementation and creates an incoherent project-level commercial policy.

## Verification

The licensing transition is complete only when:

1. this ADR is indexed as accepted in the Core ADR catalog;
2. Core's current `LICENSE` is the unmodified PolyForm Perimeter 1.0.1 terms plus an allowed Runethread required notice identifying the licensor;
3. the prior MIT text is preserved as `LICENSE-MIT` and `LICENSING.md` explains the transition boundary without claiming retroactive revocation;
4. Core README no longer advertises current Runethread as MIT and links the licensing history;
5. Hosted adopts the same current license, licensor identity, and historical MIT boundary before any runtime/Worker source is merged;
6. Hosted documentation removes the bootstrap statement that the long-term licensing model is unresolved and instead records ADR-026 as the controlling decision;
7. no source or documentation describes Perimeter-covered current Runethread as OSI open source;
8. any future material third-party contribution path has an explicit inbound-rights policy before such source is merged;
9. the Core and Hosted licensing PRs each pass their repository validation and full exact-head adversarial review gates before protected merge.

## Sources checked for the decision

- PolyForm Perimeter License 1.0.1: <https://polyformproject.org/licenses/perimeter/1.0.1>
- PolyForm license comparison: <https://polyformproject.org/licenses>
- GNU AGPLv3: <https://www.gnu.org/licenses/agpl-3.0.html>
- Open Source Definition: <https://opensource.org/osd>

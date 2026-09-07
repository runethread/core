# Runethread licensing

Current source in this `runethread/core` repository is offered under the **PolyForm Perimeter License 1.0.1**. See [`LICENSE`](LICENSE).

The licensor for the current source covered by that license is **George Karageorgiou** unless a file-specific notice says otherwise. `runethread/hosted` adopts the same current licensing model through its own reviewed transition.

## Historical MIT releases

Runethread was originally distributed under the MIT License. Existing MIT grants are not revoked.

For `runethread/core`, the merge commit that first introduces ADR-026 and this licensing transition is the repository's boundary between the historical MIT licensing state and the current PolyForm Perimeter licensing state. All Core releases published before that transition, including v0.9.0 and earlier releases, remain available under the MIT terms under which they were released. The historical MIT text is preserved in [`LICENSE-MIT`](LICENSE-MIT).

Someone who received an earlier MIT-licensed version keeps the rights that version granted. Later source is not automatically licensed under those historical MIT terms merely because it descends from earlier Git history.

## Repository and user-data boundaries

ADR-026 changes the current licensing of `runethread/core` and requires a matching transition for `runethread/hosted`. It does **not** silently relicense `runethread/memory-template`, an existing user-owned memory repository, or user-authored memory/project data.

The current `runethread/memory-template` and known contract-v9 memory repositories remain pinned to the previously released v0.9.0 / MIT-era contract material. User-authored memories, project content, imports, and other user-owned data are not licensed to Runethread merely because Runethread tooling stores or processes them.

Before any future Core release distributes newly Perimeter-covered operational-contract files into a generated or upgraded user memory repository, that release must explicitly define the file-level distribution terms and propagate every notice required by those terms. It must also make clear that those terms cover Runethread-managed artifacts only and do not license the user's own data. This packaging decision must not be inferred from the repository-root license or smuggled into a contract release accidentally.

## Current commercial model

PolyForm Perimeter permits use, modification, and distribution for permitted purposes while excluding use of the licensed software to provide others a product that competes with the software.

Source covered by PolyForm Perimeter is therefore **source-available**, not OSI-approved open source.

The licensor may separately offer commercial licenses, exceptions, partnerships, or other terms. Runethread's own monetization model is not restricted to any one mechanism and may include hosted service revenue, subscriptions, advertising, sponsorship, support, or separate commercial licensing.

## Independent implementations and trademarks

The software license governs rights in the licensed Runethread software. It does not purport to create copyright protection for ideas, facts, or functionality that copyright law does not protect, and it does not convert an independently created implementation into Runethread-licensed software merely because it implements compatible concepts or interfaces.

Software licensing also does not grant rights to represent an independent product as official Runethread. Branding and trademark policy may be documented separately.

## Contributions

Before material third-party source contributions are merged, Runethread must adopt an explicit inbound-contribution policy that preserves the rights needed for the intended source-available and separate-commercial-licensing model. A contribution must not be merged on the assumption that project ownership automatically gains relicensing rights.

## Legal review

ADR-026 is an engineering and product-governance decision. Before material commercial contracts, corporate rights transfers, or enforcement actions, the relevant licensing and ownership terms should be reviewed by qualified legal counsel for the applicable jurisdiction.

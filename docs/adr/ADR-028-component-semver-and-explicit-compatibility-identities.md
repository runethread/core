# ADR-028: Component SemVer and explicit compatibility identities

Status: Accepted
Date: 2026-09-09

## Context

Runethread already publishes Core releases using SemVer-shaped identifiers such as `v0.6.0` through `v0.9.0`, while the compatibility model separately tracks contract release/version, repository format, schema, index format, trust-lock version, bootstrap protocol, and other exact identities.

Phase 2.6 introduces independently released Hosted software and will later introduce provider/MCP adapters and additional Hosted protocols. A durable versioning rule is therefore needed before Hosted can produce a release identity. The rule must communicate human-facing release meaning without collapsing independent compatibility surfaces into one overloaded number or forcing unrelated components into lockstep releases.

## Decision

Runethread adopts Semantic Versioning 2.0.0 for independently released software/component versions.

1. Core, Hosted, and future adapters/integrations have independent SemVer release lines.
2. Public release identifiers/tags use a `v` prefix around the SemVer value, for example `v0.10.2`.
3. SemVer does not replace explicit Runethread compatibility dimensions. Contract release/version, repository format, schema, index format, trust-lock, bootstrap, and future Hosted protocol identities remain independently versioned where applicable.
4. Exact correctness/reproducibility continues to use immutable Git/object/artifact/dependency/provider identities in addition to the human release version.
5. Core runtime-release and contract-release separation from ADR-011 remains unchanged.
6. Before `1.0.0`, an intentional backward-incompatible public change requires at least a MINOR bump and explicit release-note/migration disclosure; PATCH is reserved for backward-compatible fixes/corrections. Meaningful backward-compatible feature additions also use MINOR.
7. At and after `1.0.0`, normal SemVer MAJOR/MINOR/PATCH compatibility meaning applies.
8. Prerelease identifiers are permitted for non-final releases. Build metadata may be represented when useful but is not used as Runethread's exact immutable identity and should normally be omitted from public immutable release tags.
9. There is no global lockstep Runethread project version. Cross-component compatibility is expressed through explicit release/compatibility manifests and immutable dependent identities.
10. Historical published releases remain immutable. This decision governs version assignment prospectively and does not retroactively reinterpret prior contract bytes or historical compatibility promises.

The detailed normative project policy is `docs/runethread/VERSIONING.md`.

## Consequences

- A Hosted version can advance independently of Core and vice versa.
- Human versions communicate the kind of component change without pretending to prove exact bytes.
- Existing explicit compatibility dimensions remain first-class and can advance independently of component SemVer.
- Release tooling must bind SemVer to exact commit/tree/artifact and dependent compatibility identities when correctness requires it.
- Version selection requires identifying the component's supported public compatibility promise; a convenient version number cannot hide a breaking contract/schema/protocol change.
- Pre-1.0 development remains flexible without permitting breaking changes to disappear inside patch releases.
- `1.0.0` becomes an intentional compatibility/product commitment rather than an automatic milestone.

## Alternatives considered

### One lockstep Runethread version

Rejected. Core, Hosted, adapters, schemas, contracts, and provider implementation evolve at different rates. Lockstep numbering would create meaningless churn and false compatibility implications.

### Calendar versioning

Rejected as the primary component scheme. Calendar versions communicate release age well but do not directly communicate compatibility impact, which matters more for Runethread's developer-facing components and durable-memory contracts.

### Sequential build numbers

Rejected as the primary public scheme. They are simple but communicate almost no compatibility meaning. Exact Git/artifact identities already solve build identification more strongly.

### Git SHA / artifact digest only

Rejected as the sole version identity. Exact hashes are excellent proof identities but poor human/product release identifiers and provide no change-semantics signal.

### Composite version containing every compatibility dimension

Rejected. Encoding runtime, contract, schema, repository format, protocol, and build identity into one number would become brittle and obscure the fact that those dimensions are intentionally independent.

## Verification

Implementation/release tooling and review should demonstrate that:

1. component release identifiers accept strict SemVer with the project `v` prefix and reject malformed forms;
2. Core, Hosted, and adapter release versions are not assumed to match numerically;
3. release manifests bind dependent component/contract/protocol identities explicitly rather than relying on matching version numbers;
4. a component release can advance while durable compatibility dimensions remain unchanged;
5. a compatibility dimension can advance only through its own owning migration/contract/protocol gate;
6. exact release verification still records immutable commit/tree/artifact identities;
7. pre-1.0 PATCH releases cannot be used to disguise an intentional breaking public change under project policy;
8. historical published releases and contract anchors remain unchanged by adoption of this policy.

# Runethread versioning policy

Status: **Active project policy after acceptance of ADR-028**

Runethread uses **Semantic Versioning 2.0.0** for human-facing software/component version values while retaining separate explicit compatibility dimensions and immutable cryptographic identities.

Runethread public release identifiers/tags add exactly one project `v` prefix around the SemVer value. For example, the SemVer value `0.10.2` is published as the Runethread release identifier/tag `v0.10.2`. The `v` prefix is not part of the SemVer value itself.

This policy applies prospectively. Historical Runethread releases such as `v0.6.0` through `v0.9.0` remain immutable published history; this document does not retroactively reinterpret their contract bytes or compatibility guarantees.

## 1. Three identity layers

Runethread deliberately separates three questions.

### Component release identity

Each independently released software component has its own SemVer release line.

The semantic version value has the standard form:

```text
MAJOR.MINOR.PATCH
```

The public Runethread release identifier/tag wraps that value as:

```text
v<SemVer>
```

Examples include Core, Hosted, and future provider/MCP adapters. Components do **not** share one lockstep project version merely because they belong to Runethread.

### Compatibility identity

SemVer does not replace Runethread's explicit compatibility dimensions. Core continues to track the dimensions relevant to durable user memory, including:

- contract release;
- contract version;
- repository format;
- memory schema;
- index format;
- trust-lock version;
- bootstrap protocol;
- bootstrap verifier identity.

Future Hosted/API/journal/evidence/publication protocols receive their own explicit version identities when those protocols actually exist. A component release change does not imply that every compatibility dimension changes.

### Exact immutable identity

When correctness depends on exact bytes, Runethread uses immutable identities such as:

- Git commit SHA;
- Git tree SHA;
- generated-file digest;
- release artifact SHA-256;
- exact dependency/provider/runtime identities where applicable.

SemVer communicates release meaning. Compatibility dimensions determine whether states/components may safely interact. Cryptographic identities prove which exact source/artifact was reviewed or executed.

## 2. Independent component versions

`runethread/core`, `runethread/hosted`, and future adapters/integrations version independently.

For example, all of the following public release identifiers may be valid at the same time:

```text
Core        v0.10.2
Hosted      v0.3.0
MCP adapter v0.2.1
Core contract release v0.9.0 / contract 9
```

A Hosted release must declare the exact Core/contract/protocol identities it supports. Matching numeric component versions are never an implicit compatibility rule.

## 3. SemVer bump meaning

For components at `1.0.0` or later:

- **MAJOR** — a backward-incompatible change to that component's supported public interface, behavior, or compatibility promise;
- **MINOR** — backward-compatible functionality or a backward-compatible expansion of the supported public surface;
- **PATCH** — backward-compatible fixes, security corrections, packaging fixes, or implementation corrections that do not require consumers to adopt a new public contract.

A security fix does not automatically qualify as PATCH: if the only correct fix breaks a supported public interface or compatibility promise, the release must use the corresponding breaking-version treatment.

## 4. Pre-1.0 policy

Runethread is currently in initial development. For `0.y.z` component versions, SemVer permits instability; Runethread uses the following stricter project rule:

- **MINOR (`0.Y.0`)** — required for any intentional backward-incompatible public change; also used for meaningful backward-compatible feature additions;
- **PATCH (`0.y.Z`)** — only for backward-compatible fixes/corrections within the current public compatibility promise.

A pre-1.0 breaking change must be called out explicitly in release notes/migration guidance. The fact that SemVer permits instability before `1.0.0` is not permission to hide breaking changes inside a patch release.

`1.0.0` is a deliberate product/compatibility milestone, not an automatic consequence of feature count or elapsed time.

## 5. Prerelease and build metadata

SemVer prerelease identifiers may be used for intentionally non-final releases. Their public Runethread release identifiers/tags therefore look like:

```text
v0.3.0-alpha.1
v0.3.0-beta.2
v0.3.0-rc.1
```

Build metadata may be represented where useful, but it must not substitute for Runethread's exact commit/tree/artifact identities. Public immutable release tags should normally avoid build metadata because SemVer does not use it for version precedence and Runethread already has stronger exact-byte identities.

The reserved CI/test version used by release-verification machinery is not a published product release.

## 6. Core runtime and contract release remain separate

ADR-011 remains controlling: Core runtime release identity and contract release identity are separate.

A newer Core runtime may support an unchanged older contract release without rewriting a user's memory repository merely to record the newer executable version. Conversely, a genuine contract change requires its own explicit contract-version/release treatment and supported migration where applicable.

Examples:

```text
Core runtime v0.9.1  -> contract release v0.9.0 / contract 9
Core runtime v0.10.0 -> contract release v0.9.0 / contract 9
Core runtime v0.11.0 -> contract release v0.11.0 / contract 10
```

These are illustrative relationships, not reserved future release numbers.

## 7. Compatibility dimensions advance for their own reasons

A SemVer bump must not be used to smuggle or obscure a compatibility change.

If a change alters a versioned compatibility surface, the owning compatibility dimension must advance according to its policy even though the component's SemVer release is also changing. Examples include contract semantics, repository format, schema, index format, trust-lock envelope, bootstrap protocol, and future Hosted protocols.

Likewise, a component release may advance while every durable compatibility dimension remains unchanged.

## 8. Release decision examples

| Change | Typical component bump | Other required identity action |
| --- | --- | --- |
| Internal bug fix with unchanged public behavior | PATCH | none unless exact build identity changes |
| Backward-compatible new command/API capability | MINOR | version any new protocol surface if needed |
| Security fix preserving supported interface | PATCH | update exact source/artifact identity |
| Breaking public API change before 1.0 | MINOR | migration/compatibility documentation as applicable |
| Breaking public API change at/after 1.0 | MAJOR | migration/compatibility documentation as applicable |
| Core runtime improvement with unchanged contract | PATCH or MINOR according to user-visible impact | contract release/version unchanged |
| Core contract semantic change | component bump according to public impact | contract release/version advances; migration/fixtures as required |
| Repository layout incompatibility | component bump according to public impact | repository format advances; migration required |
| Hosted implementation change with same API/protocol set | PATCH or MINOR according to user-visible impact | exact Hosted build/artifact identity advances |

When classification is genuinely ambiguous, the release owner must resolve the public compatibility promise explicitly before assigning the version.

## 9. Tags and release manifests

The canonical component SemVer value is unprefixed. Public Runethread release identifiers/tags use exactly one `v` prefix:

```text
SemVer value:              0.10.2
Runethread release tag:   v0.10.2
```

Release tooling must validate these as two related but distinct representations rather than treating `v0.10.2` itself as a raw SemVer string.

A Runethread release manifest may store the project's `v`-prefixed release identifier when its schema says so. A release manifest must never rely on that identifier alone when correctness requires stronger identity. It should bind the component release identifier to the exact source commit/tree, relevant compatibility dimensions, dependent component/protocol versions, and artifact digests appropriate to that component.

Mutable branches such as `main` are development references, not release identities.

## 10. No lockstep project version

Runethread intentionally rejects one global version spanning Core, Hosted, adapters, schemas, contracts, and provider implementation.

The project instead composes independently meaningful identities through explicit compatibility manifests. This prevents unrelated component releases from forcing meaningless version churn and avoids pretending that one number can express every durable compatibility boundary.

# Runethread agent instructions

This file applies to every automated coding agent, AI assistant, scripted developer agent, and future autonomous worker modifying `runethread/core`.

## Mandatory entry condition

Before making any substantive change, an agent **MUST** read and follow:

1. [`docs/runethread/ENGINEERING_PROCESS.md`](docs/runethread/ENGINEERING_PROCESS.md)
2. [`docs/runethread/DEVELOPMENT_PIPELINE.md`](docs/runethread/DEVELOPMENT_PIPELINE.md)
3. [`docs/runethread/CURRENT_MILESTONE.md`](docs/runethread/CURRENT_MILESTONE.md)
4. the relevant accepted ADRs and architecture/roadmap documents for the area being changed
5. [`LICENSING.md`](LICENSING.md), including ADR-026's implementation/interoperability/user-data boundary
6. the current pull-request template and repository validation policy when opening or updating a PR

If an agent cannot read or verify these sources, it **MUST stop without writing source** and report the limitation. Conversation history, personal memory, task summaries, and prior-agent handoffs are orientation aids only; they do not replace live repository policy.

A change is not complete merely because it compiles or tests green. The engineering-process document governs how changes are reasoned about, classified, reviewed, released, migrated, licensed, and corrected. The development-pipeline document defines the mandatory mechanical execution gates. The current-milestone document identifies the immediate verified work boundary.

## Non-negotiable working rules

1. **Verify state before planning from it.** Re-read `main`, the intended branch/base SHA, relevant release/version constants, repository rules, and the files that actually implement the behavior. Do not rely on a remembered SHA or prior-chat summary when a live repository read can verify it.
2. **Classify impact before editing.** Determine whether the change affects development infrastructure, runtime behavior, public API/CLI, dependencies/toolchain, repository metadata, schema, contract semantics/bytes, indexes, trust, bootstrap, migrations, release automation, templates, downstream memory repositories, licensing/rightsholder scope, required notices, or inbound contribution rights.
3. **Respect the process/product scope boundary.** A defect discovered by CI is not automatically a CI-only change. If the fix changes accepted repository state, runtime/API behavior, trust, bootstrap, starter output, migration, schema, contract semantics, or licensing/rights boundaries, reclassify it and apply the appropriate gates. Preserve exploratory evidence and restart from clean `main` when branch scope becomes materially misleading.
4. **Treat semantic contract changes as contract changes even when a vendored file was not initially edited.** Implementation and the immutable operational contract must never disagree.
5. **Preserve licensing and user-data boundaries.** Do not infer licensing rights from repository ownership or commit access. Per ADR-026/`LICENSING.md`, Perimeter-covered implementation, MIT interoperability material, historical MIT grants, third-party material, and user-authored data are distinct rights surfaces. Never silently move material between them or describe historical/user rights as revoked.
6. **Use exact historical fixtures for historical compatibility.** Do not synthesize an old released repository with the current generator when released control-plane bytes or semantics differ.
7. **Make small deliberate writes.** No blind global replacement, unrelated refactor, speculative compatibility shim, or force-push. One logical writer at a time.
8. **Validation is read-only.** CI/test workflows MUST NOT modify source and push fixes back to the branch they validate. Make a deliberate commit first, then validate that exact committed SHA.
9. **Fail closed on discrepancies.** If verified state contradicts the plan, a tool writes unexpectedly, a workflow races, required evidence is incomplete, or an invariant cannot be proven, stop further writes and investigate before continuing.
10. **Do not bypass the safety pipeline.** An agent MUST NOT disable, weaken, skip, rename around, or temporarily remove required checks, policy guards, branch protections, historical-fixture checks, race tests, cross-platform checks, trust validation, licensing/rightsholder gates, or exact-head review merely to make a change pass. Changes to the safety pipeline itself require a dedicated, reviewable hardening change and updated self-tests.
11. **Do not hide platform defects.** A Windows/macOS/Linux failure must be diagnosed from its exact logs. Broad platform skips, platform removal, or assertion weakening are forbidden substitutes for understanding the underlying behavior.
12. **Use draft PRs as review boundaries.** Review the canonical GitHub PR patch, checks, comments/reviews, base/head SHAs, and mergeability before readiness. Merge only an exact verified head SHA.
13. **Record evidence in the PR.** The PR description MUST state the verified baseline, impact matrix, backward/forward/failure checks, licensing/rightsholder impact where relevant, exact tested head SHA, remaining uncertainty, and release/downstream consequences using the repository template.
14. **Verify after merge and release.** Re-read `main`, the merge commit, tag/release assets, license/notice artifacts when applicable, generated template, and affected downstream repositories. Do not infer success from the merge/release action alone.
15. **Preserve canonical ownership.** Project engineering rules and source truth live in this repository. Personal semantic memory may reference project decisions but must not become the only source of project policy.

## Known agent/tool failure modes

- GitHub/code-search indexes can be incomplete or stale. Exhaustive audits require repository-tree/file enumeration or a verified local checkout when available.
- Tool responses can be truncated. Do not infer unseen content; issue narrower reads.
- Asynchronous Actions runs can finish after later branch edits. Never allow validation workflows to write commits, and never assume the most recently inspected run is the only active writer.
- A green test suite proves only the assertions it contains. Perform backward, forward, negative, cross-platform, and cross-surface checks described in the engineering process and development pipeline.
- Current generators are not historical fixtures. Historical release compatibility must be tested against exact released state.
- GitHub legacy branch-protection endpoints and repository rulesets are separate surfaces. Verify effective policy through the active ruleset when one exists.
- Filesystem symlinks, special files, and host Git line-ending settings can violate repository-boundary or byte-stability assumptions. Diagnose them as security/compatibility surfaces and classify any acceptance-rule change through the contract/version process rather than silently tightening semantics.
- External SDK/toolchain guidance changes over time. Re-check authoritative sources at the actual dependency decision point.
- Repository ownership, Git author metadata, and bot/co-author trailers are not substitutes for an inbound copyright/license grant. Verify contributor-rights policy before merging material third-party source.

When uncertainty remains, report it explicitly instead of converting it into an implementation assumption.

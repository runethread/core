# Runethread mandatory development pipeline

Status: **Active project policy**

This document defines the concrete execution pipeline for substantive changes to `runethread/core`. It complements `ENGINEERING_PROCESS.md`: the engineering protocol defines the reasoning and review obligations; this document defines the minimum mechanical and procedural gates every writer must pass.

Automated agents, AI assistants, scripts that modify source, and human maintainers MUST follow this pipeline. A writer that cannot read or satisfy the applicable policy MUST stop without modifying the repository. Required checks MUST NOT be disabled, skipped, weakened, renamed around, or converted into advisory-only checks merely to obtain a green result.

---

## 1. Entry gate: verify before writing

Before the first substantive write:

1. read `AGENTS.md`, `docs/runethread/ENGINEERING_PROCESS.md`, this document, `docs/runethread/CURRENT_MILESTONE.md`, `LICENSING.md`, and the relevant accepted ADRs/normative files;
2. freshly verify exact `main` SHA and intended branch/base SHA;
3. verify the current release/version dimensions and relevant historical fixtures when compatibility may be affected;
4. verify the active required-status/ruleset surface;
5. read the implementation and tests that actually own the behavior;
6. classify every relevant impact surface, including licensing/rightsholder/notice/inbound-rights impact, before editing.

Remembered conversation state is orientation, never proof. If live state contradicts the plan, stop writes and resolve the discrepancy first.

---

## 2. Mandatory semantic scope boundary

Before implementation, distinguish **development infrastructure** from **product/governance semantics**.

Development-infrastructure changes include repository CI, formatting gates, dependency-maintenance configuration, ownership metadata, and agent/process policy. Product/governance-semantic changes include anything that changes accepted/rejected repository state, canonical bytes or layout, trust rules, runtime/API/CLI behavior, bootstrap output, starter-generated files, migration behavior, schema/contract semantics, downstream repository requirements, licensing/rightsholder scope, commercial-use boundaries, required notices, or inbound contribution rights.

A change discovered while hardening CI does not become "CI-only" merely because CI exposed it. If the proposed fix changes a product promise, repository acceptance rule, or licensing/rights boundary, reclassify it and apply the relevant contract/version/migration and licensing/rights gates from `ENGINEERING_PROCESS.md`.

When scope becomes mixed or materially different from the branch purpose:

- stop further writes;
- preserve the exploratory branch as evidence;
- audit the complete branch-vs-base diff;
- move/recreate only the properly classified changes on a clean branch from a freshly verified base;
- do not force-push or hide the evidence merely to make history look clean.

Cross-platform failures MUST NOT be "fixed" by deleting the platform from CI, adding a broad skip, weakening assertions, or normalizing away a product defect without first classifying the underlying semantics.

---

## 3. Branch and write discipline

- Create a dedicated branch from an exact verified commit SHA.
- Never modify `main` directly.
- Keep one logical writer at a time on a branch.
- Make small coherent commits whose purpose and rollback boundary are clear.
- Re-read a file immediately before API replacement when stale content is possible.
- Do not blind-search/replace, force-push ordinary development branches, or mix unrelated refactors.
- CI is observational: validation workflows do not repair or push source.
- Every claim of success belongs to one exact committed SHA. A later commit invalidates the earlier green result until the later SHA passes again.

---

## 4. Cheap deterministic gates

The Linux quality job MUST fail before expensive tests when basic repository hygiene fails.

Required gates:

```text
go mod verify
gofmt -l on every tracked *.go file
git diff --check
python3 scripts/check_development_policy_test.py
python3 scripts/check_development_policy.py
python3 scripts/check_pr_impact_test.py
```

For pull requests, the PR impact/versioning guard MUST also run against the exact PR base SHA.

Formatting is checked, never auto-written by CI. Whitespace defects are corrected deliberately in source and committed before revalidation.

---

## 5. Linux deterministic quality gate

The primary quality job runs on Linux and MUST include:

```text
go test -count=1 ./...
go test -race -count=1 ./...
go vet ./...
go build ./cmd/runethread
fresh runethread init
runethread index --check <fresh repository>
runethread validate <fresh repository>
```

Change-specific tests are additive. They do not replace the baseline.

The fresh-repository smoke test verifies the actual CLI produced by the commit rather than only package-level functions.

---

## 6. Cross-platform gate

Every substantive Core change is tested on:

- Linux through the quality job;
- macOS through the platform matrix;
- Windows through the platform matrix.

The macOS and Windows jobs MUST at minimum run:

```text
go mod verify
go test -count=1 ./...
go vet ./...
go build ./cmd/runethread
```

A platform failure is a merge-blocking product/process signal. Investigate the exact logs and distinguish implementation defect, portability defect, test assumption, runner capability, and external infrastructure failure.

A platform-specific test skip is acceptable only when the platform genuinely cannot provide the tested capability and equivalent behavior is still covered elsewhere. Broad skips used to obtain green CI are forbidden.

Runethread hashes and compares canonical bytes. Core therefore keeps repository text LF-stable through `.gitattributes`, and Runethread-controlled Git transactions must not let a host-global line-ending setting rewrite canonical/control-plane bytes.

---

## 7. CI self-protection and supply-chain baseline

Validation CI MUST:

- use `permissions: contents: read`;
- never use `pull_request_target` for ordinary validation;
- never commit or push source fixes;
- pin third-party/first-party Actions used by required workflows to immutable full commit SHAs;
- retain a final job named `validate` that depends on both Linux quality and the cross-platform matrix;
- run the development-policy guard and its negative self-tests.

The repository MUST retain:

- `.gitattributes` for byte-stable Core text checkout;
- `.github/dependabot.yml` covering Go modules and GitHub Actions;
- `.github/CODEOWNERS` covering safety-critical policy/workflow/trust/migration/licensing surfaces;
- `AGENTS.md` and the engineering/pipeline policy documents;
- `LICENSE`, `LICENSE-MIT`, `LICENSING.md`, and ADR-026 as the protected licensing/rightsholder authority surface;
- the PR impact guard and development-policy guard with self-tests that byte-lock the standardized `LICENSE` and `LICENSE-MIT` texts, fail when mandatory licensing-policy markers drift, and fail if the temporary post-v0.9.0 mixed-license release block is bypassed.

`go mod verify` checks module content integrity. Dependabot provides update discovery. A vulnerability scanner is added only when its pinned version/update policy is deliberately owned; it is not substituted with an unpinned network-installed tool. Before MCP or another dependency-bearing phase, explicitly re-evaluate vulnerability scanning and the observed GitHub dependency graph.

---

## 8. Draft PR gate

Substantive work enters GitHub as a **draft PR first**.

Before readiness:

1. verify PR base/head SHAs;
2. inspect the canonical GitHub changed-file list and patch;
3. confirm every changed file belongs to the declared change class/scope;
4. run the PR-specific impact/version guard;
5. for licensing/rightsholder/commercial-policy changes, apply the **Licensing / rights gate** in `ENGINEERING_PROCESS.md` and the PR template against the exact changed material, historical grants, contributor rights, user-data boundary, and distribution notices;
6. require the exact PR head to pass Linux quality, macOS, Windows, and the aggregate `validate` check;
7. inspect comments, reviews, and review threads;
8. verify the base has not moved unexpectedly;
9. repeat backward/forward/negative/cross-surface review against the actual final diff.

An unexplained file or invalidated premise is a stop condition, even if CI is green.

---

## 9. Merge and post-merge gate

Merge only the exact reviewed head SHA. Prefer squash merge for iterative development branches.

After merge, independently verify:

- the PR is merged/closed;
- `main` points to the intended merge/squash commit;
- merged-main CI passes, including aggregate `validate`;
- required workflow/check names still match the active repository ruleset;
- critical policy/runtime/licensing files contain the reviewed content;
- dependency-maintenance/ownership files remain present.

Do not begin release, template migration, private-memory migration, or the next architectural phase before post-merge verification passes.

---

## 10. Release and downstream gates

When a change requires a release or downstream migration, follow the dedicated release/template/private-repository gates in `ENGINEERING_PROCESS.md`.

ADR-026 creates an additional post-transition release condition: Core binaries embed MIT-covered `ContractFS` material, so a post-transition Core binary is a **mixed-license distribution**. **No post-transition Core release may be requested or published until the packaging path has been deliberately updated and verified to provide both (1) the applicable PolyForm Perimeter terms or URL plus every `Required Notice:` for Perimeter-covered implementation and (2) the MIT license/copyright notice for embedded or otherwise distributed interoperability material.** Until that reviewed packaging change exists, `.github/workflows/release.yml` MUST fail closed for every requested version other than the already-published v0.9.0 baseline. The future packaging PR must deliberately replace that gate and update the development-policy guard/self-tests in the same review.

Existing MIT-era releases remain immutable historical artifacts. A development-pipeline or licensing change does not implicitly authorize modifications to the managed memory-repository bootstrap, starter-generated files, trust contract, template, or private memory repository. Those surfaces must be explicitly classified and versioned/migrated when required. Future template/generated-user-repository distributions of MIT interoperability material must make the MIT license/copyright notice available for the managed files through the normal contract/bootstrap/release/downstream process and must never imply a license grant over user-authored data.

---

## 11. Failure and correction behavior

When any gate fails:

1. stop stacking unrelated writes;
2. tie the failure to its exact SHA/job/log;
3. diagnose from evidence rather than guess;
4. distinguish product defect, process defect, test defect, harness defect, stale assumption, licensing/rights defect, and external/tool failure;
5. apply the smallest correct fix at the owning layer;
6. rerun the broader pipeline on the new exact head;
7. improve the guard/test when the failure class should have been detected earlier.

A red gate that exposes a real defect is the pipeline succeeding at its job.

---

## 12. Mandatory future-agent behavior

Future agents extending Runethread MUST treat these files as project-native authority:

```text
AGENTS.md
LICENSING.md
docs/runethread/ENGINEERING_PROCESS.md
docs/runethread/DEVELOPMENT_PIPELINE.md
docs/runethread/CURRENT_MILESTONE.md
```

They MUST re-read them from the live repository before substantive changes. Project policy must not exist only in chat history, personal memory, or an agent scratchpad.

If an agent cannot prove compliance with a mandatory gate, including a licensing/rightsholder/required-notice gate, it must report the uncertainty and stop rather than silently substituting a weaker process.

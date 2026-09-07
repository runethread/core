#!/usr/bin/env python3
"""Fail closed when Runethread's mandatory development safety surface drifts."""

from __future__ import annotations

import hashlib
import re
import stat
import subprocess
import sys
from pathlib import Path

SHA40 = re.compile(r"^[0-9a-f]{40}$")
USES_RE = re.compile(r"(?m)^\s*uses:\s*([^\s#]+)")

REQUIRED_FILES = (
    ".gitattributes",
    "AGENTS.md",
    "LICENSE",
    "LICENSE-MIT",
    "LICENSING.md",
    "README.md",
    "contract.go",
    "docs/adr/ADR-026-runethread-licensing-and-commercial-model.md",
    "docs/adr/README.md",
    "docs/runethread/ENGINEERING_PROCESS.md",
    "docs/runethread/DEVELOPMENT_PIPELINE.md",
    "docs/runethread/CURRENT_MILESTONE.md",
    "docs/runethread/ROADMAP.md",
    ".github/pull_request_template.md",
    ".github/workflows/validate.yml",
    ".github/workflows/release.yml",
    ".github/dependabot.yml",
    ".github/CODEOWNERS",
    "scripts/check-pr-impact.py",
    "scripts/check_pr_impact_test.py",
    "scripts/check_development_policy.py",
    "scripts/check_development_policy_test.py",
)

EXACT_FILE_SHA256 = {
    "LICENSE": "bb1d1de338bdbe282f151bf54d6bb6ad98ad37b9592539461fb51ff4bcd4e1c3",
    "LICENSE-MIT": "a648e5f1a60155f62062b88d4c5758306a119a63962233b40a9bb2d48114bef4",
}

# The temporary post-v0.9.0 release barrier is itself safety-critical. Lock the
# complete workflow bytes, not just marker strings, until a reviewed mixed-license
# packaging change deliberately replaces the barrier and updates this guard/tests.
EXACT_GIT_BLOB_SHA1 = {
    ".github/workflows/release.yml": "48c6ad8bef3375216ae2e7b0716f53bc2d861020",
}

# The Core MIT exception is closed and independently enumerated. ContractPaths
# and ContractFS must match this set; neither is allowed to define/expand it.
MIT_CONTRACT_PATHS = frozenset(
    {
        "MEMORY_PROTOCOL.md",
        "schema/memory-item.schema.json",
        "docs/MEMORY_SCHEMA.md",
        "docs/MEMORY_CONTENT_FORMAT.md",
        "docs/TAXONOMY.md",
        "docs/REPOSITORY_VALIDATION.md",
        "docs/USER_COMMANDS.md",
        "docs/EXTENDING_RUNETHREAD.md",
        "docs/TRUST_MODEL.md",
        "docs/SOURCES.md",
        "docs/INDEX_FORMAT.md",
        "templates/fact.md",
        "templates/preference.md",
        "templates/decision.md",
        "templates/state.md",
        "templates/open_loop.md",
        "templates/correction.md",
        "templates/milestone.md",
        "templates/reference.md",
    }
)

MIT_BOOTSTRAP_INTERFACE_PATHS = frozenset({"AI_SETUP.md", "runethread-bootstrap.json"})

# These are output pathnames only. The Runethread-authored bytes emitted there
# have the narrow MIT output exception described in LICENSING.md/ADR-026; the
# Core implementation that generates them remains Perimeter-covered.
MIT_GENERATED_USER_REPO_OUTPUT_PATHS = frozenset(
    {
        ".gitattributes",
        "README.md",
        ".github/workflows/validate.yml",
        ".runethread/config.json",
        ".runethread/lock.json",
    }
)

# Current Core has no committed binary/non-text or non-regular exception. A
# future real binary/symlink/submodule must be admitted by exact reviewed path;
# it must never become an implicit escape from the licensing text scan.
ALLOWED_BINARY_TRACKED_FILES = frozenset()
ALLOWED_NONREGULAR_TRACKED_FILES = frozenset()

# Faithful historical licensing/source fixtures may preserve wording that would
# look stale today, but only by exact path + exact bytes. There are no such
# current exceptions. Future entries must pin SHA-256 rather than skip a folder.
HISTORICAL_LICENSE_TEXT_SHA256: dict[str, str] = {}

# A readable file that discusses licensing is not allowed to appear silently.
# Exact membership is deliberately reviewed so future prose, config, scripts, or
# source strings cannot become a second licensing authority by accident.
LICENSE_BEARING_TEXT_FILES = frozenset(
    {
        ".github/CODEOWNERS",
        ".github/pull_request_template.md",
        ".github/workflows/release.yml",
        "AGENTS.md",
        "LICENSE",
        "LICENSE-MIT",
        "LICENSING.md",
        "README.md",
        "docs/adr/ADR-026-runethread-licensing-and-commercial-model.md",
        "docs/adr/README.md",
        "docs/runethread/CURRENT_MILESTONE.md",
        "docs/runethread/DEVELOPMENT_PIPELINE.md",
        "docs/runethread/ENGINEERING_PROCESS.md",
        "docs/runethread/ROADMAP.md",
        "scripts/check-pr-impact.py",
        "scripts/check_pr_impact_test.py",
        "scripts/check_development_policy.py",
        "scripts/check_development_policy_test.py",
    }
)

LICENSE_VOCAB_RE = re.compile(
    r"(?i)(?:"
    r"\b(?:license|licensed|licenses|licensing|licensor|licensee|licence|licenced|licences|licencing)\b|"
    r"\brightsholder\b|\bcopyright\b|\bcopyleft\b|\bpolyform\b|\bperimeter\b|\bMIT\b|"
    r"\bpatents?\b|\btrademarks?\b|\bsource[- ]available\b|\bopen[- ]source\b|"
    r"\bnon[- ]?commercial\b|\bcommercial(?:ly|ization|isation)?\b|"
    r"\bdual[- ]licens(?:e|ed|ing)\b|\brelicens(?:e|ed|ing)\b|"
    r"\bproprietary\b|\bpublic domain\b|\ball rights reserved\b|"
    r"SPDX-License-Identifier"
    r")"
)

# These are intentionally narrow present-tense/global contradictions. Historical
# MIT statements, exact legal text, and explicitly scoped MIT interoperability
# statements remain valid and are not rejected by a crude keyword ban.
FORBIDDEN_GLOBAL_LICENSE_PATTERNS = (
    (
        "global MIT-only Runethread claim",
        re.compile(
            r"(?i)\brunethread\s+is\s+(?:released|licensed)\s+under[^\n]{0,160}\bMIT(?:\s+License)?\b"
        ),
    ),
    (
        "global MIT-only Runethread claim",
        re.compile(r"(?i)\brunethread\s+(?:is|remains)\s+(?:solely\s+|only\s+)?MIT[- ]licensed\b"),
    ),
    (
        "unscoped open-source Runethread claim",
        re.compile(r"(?i)\brunethread\s+(?:is|remains)\s+(?:an?\s+)?open[- ]source\b"),
    ),
    (
        "blanket Perimeter Runethread claim",
        re.compile(r"(?i)\b(?:all|entire)\s+Runethread[^\n]{0,160}\bPolyForm\s+Perimeter\b"),
    ),
)

VALIDATE_NEEDLES = (
    "permissions:\n  contents: read",
    "go mod verify",
    "gofmt -l",
    "git diff --check",
    "python3 scripts/check_development_policy_test.py",
    "python3 scripts/check_development_policy.py",
    "python3 scripts/check_pr_impact_test.py",
    "python3 scripts/check-pr-impact.py",
    "go test -count=1 ./...",
    "go test -race -count=1 ./...",
    "go vet ./...",
    "go build ./cmd/runethread",
    "runethread index --check",
    "runethread validate",
    "macos-latest",
    "windows-latest",
    "needs: [quality, platform]",
)

RELEASE_NEEDLES = (
    "Enforce ADR-026 license packaging gate",
    'if [ "$VERSION" != "v0.9.0" ]; then',
    "ADR-026 blocks post-v0.9.0 release publication until mixed-license packaging is implemented and verified",
    "MIT license/copyright notice for embedded/exported interoperability material",
)

AGENT_NEEDLES = (
    "MUST",
    "ENGINEERING_PROCESS.md",
    "DEVELOPMENT_PIPELINE.md",
    "CURRENT_MILESTONE.md",
    "LICENSING.md",
    "Validation is read-only",
    "Fail closed",
    "Respect the process/product scope boundary",
    "Preserve licensing and user-data boundaries",
    "Do not hide platform defects",
)

PROCESS_NEEDLES = (
    "Preflight gate",
    "Impact matrix",
    "Historical / backward compatibility gate",
    "Forward compatibility gate",
    "Negative and failure-mode gate",
    "Verification gate on the committed branch",
    "Licensing / rights gate",
    "Readable licensing consistency is also part of this gate",
    "every Git-tracked regular file that decodes as UTF-8 text",
    "Core binaries embed MIT-covered `ContractFS` interoperability material",
    "mixed-license distribution",
    "public `runethread/memory-template`",
    "Draft PR review gate",
    "Post-merge gate",
    "Correction / incident protocol",
    "Stop conditions",
)

PIPELINE_NEEDLES = (
    "Mandatory semantic scope boundary",
    "Cheap deterministic gates",
    "repository-wide readable-text licensing consistency gate",
    "every Git-tracked regular file that decodes as UTF-8 text",
    "new licensing-bearing readable file",
    "Linux deterministic quality gate",
    "Cross-platform gate",
    "CI self-protection and supply-chain baseline",
    "Licensing / rights gate",
    "Core binaries embed MIT-covered `ContractFS` material",
    "mixed-license distribution",
    "Draft PR gate",
    "Merge and post-merge gate",
    "Mandatory future-agent behavior",
    "Cross-platform failures MUST NOT",
    "contents: read",
    "gofmt -l",
    "git diff --check",
    "go test -race -count=1 ./...",
    "macOS through the platform matrix",
    "Windows through the platform matrix",
)

MILESTONE_NEEDLES = (
    "ADR-026 records the accepted Runethread licensing/commercial-model decision",
    "Core's MIT exception is an independently guarded exact allowlist",
    "Generator/runtime source remains Perimeter-covered",
    "Core binaries embed MIT-covered contract material",
    "mixed-license distribution",
    "Protect and remediate the public `runethread/memory-template`",
    "Establish basic protected-`main` policy first",
)

ROADMAP_NEEDLES = (
    "ADR-026 **system licensing transition**",
    "establish basic protected-`main` policy on `runethread/memory-template`",
    "scoped MIT license/copyright notice",
    "Existing private/user memory repositories are not modified merely to add a notice",
    "then complete Hosted's own protected Perimeter/history transition",
)

README_NEEDLES = (
    "mixed licensing boundary",
    "PolyForm Perimeter License 1.0.1",
    "source-available",
    "[MIT License](LICENSE-MIT)",
    "Historical pre-transition material",
    "User-authored memory/project data is not licensed to Runethread",
    "ADR-026",
)

PR_NEEDLES = (
    "Development infrastructure / CI / engineering policy",
    "Licensing / rights / commercial policy",
    "Scope-boundary decision",
    "Licensing / rights gate",
    "Mandatory pipeline on exact head",
    "No platform was removed/skipped/weakened to obtain green CI",
    "required final `validate` job passed on the exact reviewed head",
)

DEPENDABOT_NEEDLES = (
    'package-ecosystem: "gomod"',
    'package-ecosystem: "github-actions"',
)

CODEOWNERS_NEEDLES = (
    "/.gitattributes @Karageorgiou",
    "/AGENTS.md @Karageorgiou",
    "/LICENSE @Karageorgiou",
    "/LICENSE-MIT @Karageorgiou",
    "/LICENSING.md @Karageorgiou",
    "/README.md @Karageorgiou",
    "/docs/adr/ADR-026-runethread-licensing-and-commercial-model.md @Karageorgiou",
    "/docs/adr/README.md @Karageorgiou",
    "/docs/runethread/ENGINEERING_PROCESS.md @Karageorgiou",
    "/docs/runethread/DEVELOPMENT_PIPELINE.md @Karageorgiou",
    "/docs/runethread/ROADMAP.md @Karageorgiou",
    "/.github/pull_request_template.md @Karageorgiou",
    "/.github/workflows/ @Karageorgiou",
    "/internal/trust/ @Karageorgiou",
    "/internal/upgrader/ @Karageorgiou",
)

GITATTRIBUTES_NEEDLES = (
    "* text=auto eol=lf",
    "*.exe binary",
)

LICENSING_NEEDLES = (
    "Implementation default — PolyForm Perimeter 1.0.1",
    "Permissive interoperability boundary — MIT",
    "closed and enumerated",
    "ContractPaths()` does not define or enlarge the MIT license boundary",
    "No Go implementation file",
    "Narrow generated-output exception",
    "This is an output exception, not a source-code exception",
    "Historical MIT material",
    "implementation repository",
    "valid UTF-8 text unless its exact path is deliberately classified",
    "exact path + exact SHA-256",
    "Core binaries also embed the exact MIT-listed operational-contract files",
    "mixed-license distribution",
    "No post-transition Core release may be requested or published",
)

ADR026_NEEDLES = (
    "Status: **Accepted**",
    "PolyForm Perimeter License 1.0.1",
    "closed enumerated MIT exception",
    "ContractPaths()` is **not licensing authority**",
    "Narrow generated-output exception",
    "not an implementation repository",
    "Licensing statements and exceptions are mechanically guarded",
    "exact path + exact SHA-256",
    "Post-transition release distribution has an explicit mixed-license notice gate",
)

ADR_CATALOG_NEEDLES = (
    "[ADR-026](ADR-026-runethread-licensing-and-commercial-model.md)",
    "Runethread licensing and commercial model",
    "Historical MIT grants remain intact",
)


def read(root: Path, rel: str, errors: list[str]) -> str:
    path = root / rel
    try:
        return path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as exc:
        errors.append(f"{rel}: cannot read required UTF-8 file: {exc}")
        return ""


def check_exact_sha256(root: Path, rel: str, expected: str, errors: list[str]) -> None:
    path = root / rel
    try:
        actual = hashlib.sha256(path.read_bytes()).hexdigest()
    except OSError as exc:
        errors.append(f"{rel}: cannot hash required file: {exc}")
        return
    if actual != expected:
        errors.append(f"{rel}: exact legal text SHA-256 mismatch: got {actual}, want {expected}")


def check_exact_git_blob_sha1(root: Path, rel: str, expected: str, errors: list[str]) -> None:
    path = root / rel
    try:
        data = path.read_bytes()
    except OSError as exc:
        errors.append(f"{rel}: cannot hash protected file: {exc}")
        return
    payload = f"blob {len(data)}\0".encode("ascii") + data
    actual = hashlib.sha1(payload, usedforsecurity=False).hexdigest()
    if actual != expected:
        errors.append(f"{rel}: exact protected file Git blob mismatch: got {actual}, want {expected}")


def check_action_pins(rel: str, text: str, errors: list[str]) -> None:
    uses = USES_RE.findall(text)
    if not uses:
        errors.append(f"{rel}: no actions are declared")
        return

    seen_checkout = False
    seen_setup_go = False
    for target in uses:
        if target.startswith("./"):
            continue
        if "@" not in target:
            errors.append(f"{rel}: external action {target!r} must be pinned with @<40-hex-sha>")
            continue
        action, ref = target.rsplit("@", 1)
        if action == "actions/checkout":
            seen_checkout = True
        if action == "actions/setup-go":
            seen_setup_go = True
        if not SHA40.fullmatch(ref):
            errors.append(f"{rel}: external action {action} must use an immutable 40-hex commit SHA, got {ref!r}")

    if not seen_checkout:
        errors.append(f"{rel}: missing actions/checkout usage")
    if not seen_setup_go:
        errors.append(f"{rel}: missing actions/setup-go usage")


def require_needles(label: str, text: str, needles: tuple[str, ...], errors: list[str]) -> None:
    for needle in needles:
        if needle not in text:
            errors.append(f"{label}: missing mandatory policy marker {needle!r}")


def parse_contract_paths(source: str, errors: list[str]) -> frozenset[str]:
    match = re.search(
        r"var\s+contractPaths\s*=\s*\[\]string\s*\{(?P<body>.*?)\n\}",
        source,
        re.DOTALL,
    )
    if not match:
        errors.append("contract.go: cannot parse contractPaths")
        return frozenset()
    paths = re.findall(r'"([^"\\]+)"', match.group("body"))
    if len(paths) != len(set(paths)):
        errors.append("contract.go: contractPaths contains duplicate path entries")
    return frozenset(paths)


def resolve_contract_embed_paths(root: Path, source: str, errors: list[str]) -> frozenset[str]:
    patterns: list[str] = []
    for match in re.finditer(r"(?m)^//go:embed\s+(.+)$", source):
        patterns.extend(match.group(1).split())
    if not patterns:
        errors.append("contract.go: missing //go:embed ContractFS declaration")
        return frozenset()

    resolved: set[str] = set()
    for pattern in patterns:
        matches = list(root.glob(pattern))
        if not matches:
            errors.append(f"contract.go: embed pattern {pattern!r} matches no files")
            continue
        for path in matches:
            try:
                mode = path.lstat().st_mode
            except OSError as exc:
                errors.append(f"contract.go: cannot inspect embedded path {path}: {exc}")
                continue
            if not stat.S_ISREG(mode):
                errors.append(f"contract.go: embedded path {path} is not a regular file")
                continue
            resolved.add(path.relative_to(root).as_posix())
    return frozenset(resolved)


def check_mit_interoperability_boundary(root: Path, contract_source: str, errors: list[str]) -> None:
    declared = parse_contract_paths(contract_source, errors)
    if declared != MIT_CONTRACT_PATHS:
        errors.append(
            "contract.go: ContractPaths() does not equal the independently guarded MIT contract allowlist"
        )

    embedded = resolve_contract_embed_paths(root, contract_source, errors)
    if embedded != MIT_CONTRACT_PATHS:
        errors.append(
            "contract.go: resolved ContractFS embed set does not equal the independently guarded MIT contract allowlist"
        )

    for rel in sorted(MIT_CONTRACT_PATHS | MIT_BOOTSTRAP_INTERFACE_PATHS):
        if not (root / rel).is_file():
            errors.append(f"{rel}: MIT interoperability allowlist path is missing")


def regular_repository_files(root: Path, errors: list[str]) -> list[str]:
    """Return tracked/test-tree regular files and fail on unclassified non-regular entries."""
    if (root / ".git").exists():
        try:
            result = subprocess.run(
                ["git", "-C", str(root), "ls-files", "--stage", "-z"],
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
        except (OSError, subprocess.CalledProcessError) as exc:
            errors.append(f"repository manifest: cannot enumerate Git-tracked files: {exc}")
            return []

        paths: list[str] = []
        for record in result.stdout.split(b"\0"):
            if not record:
                continue
            try:
                metadata, raw_path = record.split(b"\t", 1)
                mode, _object_id, stage = metadata.split(b" ", 2)
            except ValueError:
                errors.append("repository manifest: malformed git ls-files record")
                continue
            if stage != b"0":
                errors.append("repository manifest: unmerged/non-stage-0 Git index entry is not allowed")
                continue
            try:
                rel = raw_path.decode("utf-8", errors="strict")
            except UnicodeDecodeError:
                errors.append("repository manifest: tracked path is not UTF-8")
                continue
            rel = Path(rel).as_posix()
            if mode not in {b"100644", b"100755"}:
                if rel not in ALLOWED_NONREGULAR_TRACKED_FILES:
                    errors.append(
                        f"{rel}: tracked non-regular Git object is not explicitly classified"
                    )
                continue
            path = root / Path(rel)
            try:
                current_mode = path.lstat().st_mode
            except OSError as exc:
                errors.append(f"{rel}: tracked regular file is unavailable in the working tree: {exc}")
                continue
            if not stat.S_ISREG(current_mode):
                errors.append(f"{rel}: Git tracks a regular file but the working-tree object is not regular")
                continue
            paths.append(rel)
        return sorted(set(paths))

    # Self-tests copy the guarded surface into a temporary tree without .git.
    paths = []
    for path in root.rglob("*"):
        try:
            mode = path.lstat().st_mode
        except OSError as exc:
            errors.append(f"{path}: cannot inspect test repository path: {exc}")
            continue
        rel = path.relative_to(root).as_posix()
        if stat.S_ISDIR(mode):
            continue
        if stat.S_ISREG(mode):
            paths.append(rel)
            continue
        if rel not in ALLOWED_NONREGULAR_TRACKED_FILES:
            errors.append(f"{rel}: non-regular repository object is not explicitly classified")
    return sorted(set(paths))


def check_readable_licensing_surface(root: Path, errors: list[str]) -> None:
    for rel in regular_repository_files(root, errors):
        path = root / Path(rel)
        try:
            data = path.read_bytes()
        except OSError as exc:
            errors.append(f"{rel}: cannot read tracked regular file for licensing scan: {exc}")
            continue

        if rel in ALLOWED_BINARY_TRACKED_FILES:
            continue
        if b"\0" in data:
            errors.append(f"{rel}: NUL-bearing tracked regular file requires an explicit binary exception")
            continue
        try:
            text = data.decode("utf-8", errors="strict")
        except UnicodeDecodeError:
            errors.append(f"{rel}: tracked regular file is not valid UTF-8 and has no binary exception")
            continue

        historical_sha = HISTORICAL_LICENSE_TEXT_SHA256.get(rel)
        if historical_sha is not None:
            actual = hashlib.sha256(data).hexdigest()
            if actual != historical_sha:
                errors.append(
                    f"{rel}: historical licensing-text SHA-256 mismatch: got {actual}, want {historical_sha}"
                )
            continue

        for label, pattern in FORBIDDEN_GLOBAL_LICENSE_PATTERNS:
            if pattern.search(text):
                errors.append(f"{rel}: contradictory licensing statement ({label})")

        if LICENSE_VOCAB_RE.search(text) and rel not in LICENSE_BEARING_TEXT_FILES:
            errors.append(
                f"{rel}: licensing-bearing readable file is not classified in LICENSE_BEARING_TEXT_FILES"
            )


def check(root: Path) -> list[str]:
    errors: list[str] = []
    for rel in REQUIRED_FILES:
        if not (root / rel).is_file():
            errors.append(f"{rel}: required development-safety file is missing")

    gitattributes = read(root, ".gitattributes", errors)
    licensing = read(root, "LICENSING.md", errors)
    readme = read(root, "README.md", errors)
    contract_source = read(root, "contract.go", errors)
    adr026 = read(root, "docs/adr/ADR-026-runethread-licensing-and-commercial-model.md", errors)
    adr_catalog = read(root, "docs/adr/README.md", errors)
    validate = read(root, ".github/workflows/validate.yml", errors)
    release = read(root, ".github/workflows/release.yml", errors)
    dependabot = read(root, ".github/dependabot.yml", errors)
    codeowners = read(root, ".github/CODEOWNERS", errors)
    pr_template = read(root, ".github/pull_request_template.md", errors)
    agents = read(root, "AGENTS.md", errors)
    process = read(root, "docs/runethread/ENGINEERING_PROCESS.md", errors)
    pipeline = read(root, "docs/runethread/DEVELOPMENT_PIPELINE.md", errors)
    milestone = read(root, "docs/runethread/CURRENT_MILESTONE.md", errors)
    roadmap = read(root, "docs/runethread/ROADMAP.md", errors)

    for rel, expected in EXACT_FILE_SHA256.items():
        check_exact_sha256(root, rel, expected, errors)
    for rel, expected in EXACT_GIT_BLOB_SHA1.items():
        check_exact_git_blob_sha1(root, rel, expected, errors)

    check_mit_interoperability_boundary(root, contract_source, errors)

    if "pull_request_target:" in validate:
        errors.append("validate.yml: pull_request_target is forbidden for validation CI")
    if re.search(r"(?m)^\s*contents:\s*write\s*$", validate):
        errors.append("validate.yml: validation CI must not have contents: write")
    for needle in VALIDATE_NEEDLES:
        if needle not in validate:
            errors.append(f"validate.yml: missing mandatory safety surface {needle!r}")

    check_action_pins(".github/workflows/validate.yml", validate, errors)
    check_action_pins(".github/workflows/release.yml", release, errors)

    if not re.search(r"(?m)^\s*contents:\s*write\s*$", release):
        errors.append("release.yml: release publication requires explicit contents: write")

    require_needles(".gitattributes", gitattributes, GITATTRIBUTES_NEEDLES, errors)
    require_needles("release.yml", release, RELEASE_NEEDLES, errors)
    require_needles("LICENSING.md", licensing, LICENSING_NEEDLES, errors)
    require_needles("README.md", readme, README_NEEDLES, errors)
    require_needles("ADR-026", adr026, ADR026_NEEDLES, errors)
    require_needles("ADR catalog", adr_catalog, ADR_CATALOG_NEEDLES, errors)
    require_needles("CURRENT_MILESTONE.md", milestone, MILESTONE_NEEDLES, errors)
    require_needles("ROADMAP.md", roadmap, ROADMAP_NEEDLES, errors)
    require_needles("dependabot.yml", dependabot, DEPENDABOT_NEEDLES, errors)
    require_needles("CODEOWNERS", codeowners, CODEOWNERS_NEEDLES, errors)
    require_needles("AGENTS.md", agents, AGENT_NEEDLES, errors)
    require_needles("ENGINEERING_PROCESS.md", process, PROCESS_NEEDLES, errors)
    require_needles("DEVELOPMENT_PIPELINE.md", pipeline, PIPELINE_NEEDLES, errors)
    require_needles("pull_request_template.md", pr_template, PR_NEEDLES, errors)

    for rel in sorted(MIT_GENERATED_USER_REPO_OUTPUT_PATHS):
        if f"`{rel}`" not in licensing:
            errors.append(f"LICENSING.md: missing exact generated-output MIT path {rel!r}")
        if f"`{rel}`" not in adr026:
            errors.append(f"ADR-026: missing exact generated-output MIT path {rel!r}")

    check_readable_licensing_surface(root, errors)

    return errors


def main(argv: list[str]) -> int:
    root = Path(argv[1]).resolve() if len(argv) > 1 else Path(__file__).resolve().parents[1]
    errors = check(root)
    if errors:
        for error in errors:
            print(f"development-policy: {error}", file=sys.stderr)
        return 1
    print("development-policy: OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))

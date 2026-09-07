#!/usr/bin/env python3
"""Fail closed when Runethread's mandatory development safety surface drifts."""

from __future__ import annotations

import hashlib
import json
import re
import stat
import subprocess
import sys
from pathlib import Path

SHA40 = re.compile(r"^[0-9a-f]{40}$")
SHA256 = re.compile(r"^[0-9a-f]{64}$")
USES_RE = re.compile(r"(?m)^\s*uses:\s*([^\s#]+)")

REQUIRED_FILES = (
    ".gitattributes",
    "AGENTS.md",
    "LICENSE",
    "LICENSE-MIT",
    "LICENSING.md",
    "LICENSING_BOUNDARY.json",
    "README.md",
    "contract.go",
    "runethread-bootstrap.json",
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
    "internal/starter/output_identity_test.go",
    "scripts/check-pr-impact.py",
    "scripts/check_pr_impact_test.py",
    "scripts/check_development_policy.py",
    "scripts/check_development_policy_test.py",
)

EXACT_LEGAL_SHA256 = {
    "LICENSE": "bb1d1de338bdbe282f151bf54d6bb6ad98ad37b9592539461fb51ff4bcd4e1c3",
    "LICENSE-MIT": "a648e5f1a60155f62062b88d4c5758306a119a63962233b40a9bb2d48114bef4",
}

# This manifest is the single machine-readable authority for the closed
# permissive exception. Human policy refers to it instead of duplicating lists.
EXACT_POLICY_SHA256 = {
    "LICENSING_BOUNDARY.json": "0c00008d3e014078792c32285a3705a8c47362c850aec08a2d5f49fd5f680f14",
}

# These bytes are deliberately frozen at this transition. A future reviewed
# change must update the owning policy/test in the same PR. Locking contract.go
# makes the source-text ContractPaths parser non-spoofable for this frozen v9
# state. Locking validate.yml catches accidental self-protection drift, while
# exact-head review remains necessary because a PR controls its own workflow.
EXACT_GIT_BLOB_SHA1 = {
    ".github/workflows/release.yml": "48c6ad8bef3375216ae2e7b0716f53bc2d861020",
    ".github/workflows/validate.yml": "465b798f6594e3bf11cc244cf40a75241cf1fe31",
    "contract.go": "eb884392ec7aaa1eab9c417588a0fb6c722e82da",
}

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

MIT_BOOTSTRAP_INTERFACE_SHA256 = {
    "runethread-bootstrap.json": "23c71ec28f548755cba680a318e1ad344c1f419de403104d1a46a5512625742d",
}
MIT_BOOTSTRAP_INTERFACE_PATHS = frozenset(MIT_BOOTSTRAP_INTERFACE_SHA256)

MIT_GENERATED_USER_REPO_OUTPUT_SHA256 = {
    ".gitattributes": "435050e549a9be1ba0793b25299caa35bd8bdda818e222281e297e19e4ced20d",
    "README.md": "5569022c660cc1f14d8d437fb894dbda18270963d9c11b1041551819f181202a",
    ".github/workflows/validate.yml": "b9caad673504e7e57acb1910ed2fc882382f13d2af063fe13417fcb76b8d0790",
    ".runethread/config.json": "f3c02ea03647140205836c3185ee5cd1756e063c5962ef29e816adc3b849d6f9",
    ".runethread/lock.json": "bca8aeb88a58684f80d6d65880a0aba7c2468b9bf208de283eb76b6ec7e81a52",
    "index/catalog.json": "42d46a5eda6e577f859b56bc92ed5fb9f1043444231d8d92cd88344307181734",
    "index/open-loops.md": "3b9f81135065f237e48020999c9f056432a05856341317df007d7b96325156ea",
    "index/preferences.md": "cd05ac6c1bc3a5df1943d25f9a3ea97d8d56aaf3a30e07f6dd3a6cd7c53d4cb5",
    "index/projects.md": "ded8999df1c7f664ebb774062c7ae03d14e22c44b204e5c7db1b75ad711bc697",
}
MIT_GENERATED_USER_REPO_OUTPUT_PATHS = frozenset(MIT_GENERATED_USER_REPO_OUTPUT_SHA256)

GENERATED_EMPTY_PLACEHOLDER_SHA256 = {
    "memories/.gitkeep": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
    "projects/.gitkeep": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
}

EXPECTED_HISTORICAL_BOUNDARIES = {
    "core_main_pretransition_commit": "22995a7cf7d1c6c0f4ce548fd83667468b356f42",
    "first_public_branch_perimeter_root_commit": "4bd5279a91ca894f6ccb13db91360f6ba95b6576",
}

ALLOWED_BINARY_TRACKED_FILES = frozenset()
ALLOWED_NONREGULAR_TRACKED_FILES = frozenset()
HISTORICAL_LICENSE_TEXT_SHA256: dict[str, str] = {}

LICENSE_BEARING_TEXT_FILES = frozenset(
    {
        ".github/CODEOWNERS",
        ".github/pull_request_template.md",
        ".github/workflows/release.yml",
        "AGENTS.md",
        "LICENSE",
        "LICENSE-MIT",
        "LICENSING.md",
        "LICENSING_BOUNDARY.json",
        "README.md",
        "docs/adr/ADR-026-runethread-licensing-and-commercial-model.md",
        "docs/adr/README.md",
        "docs/runethread/CURRENT_MILESTONE.md",
        "docs/runethread/DEVELOPMENT_PIPELINE.md",
        "docs/runethread/ENGINEERING_PROCESS.md",
        "docs/runethread/ROADMAP.md",
        "internal/starter/output_identity_test.go",
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

FORBIDDEN_GLOBAL_LICENSE_PATTERNS = (
    (
        "global MIT-only Runethread claim",
        re.compile(r"(?i)\brunethread\s+is\s+(?:released|licensed)\s+under[^\n]{0,160}\bMIT(?:\s+License)?\b"),
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
    "exact exception in [`LICENSING_BOUNDARY.json`](LICENSING_BOUNDARY.json)",
    "Perimeter is the default everywhere else",
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
    "/LICENSING_BOUNDARY.json @Karageorgiou",
    "/README.md @Karageorgiou",
    "/docs/adr/ADR-026-runethread-licensing-and-commercial-model.md @Karageorgiou",
    "/docs/adr/README.md @Karageorgiou",
    "/docs/runethread/ENGINEERING_PROCESS.md @Karageorgiou",
    "/docs/runethread/DEVELOPMENT_PIPELINE.md @Karageorgiou",
    "/docs/runethread/ROADMAP.md @Karageorgiou",
    "/.github/pull_request_template.md @Karageorgiou",
    "/.github/workflows/ @Karageorgiou",
    "/internal/starter/output_identity_test.go @Karageorgiou",
    "/internal/trust/ @Karageorgiou",
    "/internal/upgrader/ @Karageorgiou",
)

GITATTRIBUTES_NEEDLES = ("* text=auto eol=lf", "*.exe binary")

LICENSING_NEEDLES = (
    "Implementation default — PolyForm Perimeter 1.0.1",
    "Permissive interoperability boundary — exact MIT exception",
    "LICENSING_BOUNDARY.json",
    "single machine-readable authority",
    "Perimeter is the default everywhere else",
    "AI_SETUP.md is not part of the prospective MIT exception",
    "Exact-byte generated-output exception",
    "output_identity_test.go",
    "first public development-branch snapshot whose root license is Perimeter",
    "4bd5279a91ca894f6ccb13db91360f6ba95b6576",
    "CI self-protection limitation",
    "exact-head adversarial review",
    "Core binaries also embed the exact MIT-listed operational-contract files",
    "mixed-license distribution",
    "No post-transition Core release may be requested or published",
)

ADR026_NEEDLES = (
    "Status: **Accepted**",
    "PolyForm Perimeter License 1.0.1",
    "closed exact MIT exception",
    "LICENSING_BOUNDARY.json",
    "Perimeter is the default everywhere else",
    "AI_SETUP.md",
    "4bd5279a91ca894f6ccb13db91360f6ba95b6576",
    "Generated-output byte identity",
    "CI self-protection",
    "Post-transition release distribution has an explicit mixed-license notice gate",
)

ADR_CATALOG_NEEDLES = (
    "[ADR-026](ADR-026-runethread-licensing-and-commercial-model.md)",
    "Runethread licensing and commercial model",
    "exact machine-guarded MIT exception",
    "Perimeter remains the default outside that exception",
    "Historical MIT grants remain intact",
)


def read(root: Path, rel: str, errors: list[str]) -> str:
    path = root / rel
    try:
        return path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as exc:
        errors.append(f"{rel}: cannot read required UTF-8 file: {exc}")
        return ""


def check_exact_sha256(root: Path, rel: str, expected: str, label: str, errors: list[str]) -> None:
    path = root / rel
    try:
        actual = hashlib.sha256(path.read_bytes()).hexdigest()
    except OSError as exc:
        errors.append(f"{rel}: cannot hash required file: {exc}")
        return
    if actual != expected:
        errors.append(f"{rel}: exact {label} SHA-256 mismatch: got {actual}, want {expected}")


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
        seen_checkout = seen_checkout or action == "actions/checkout"
        seen_setup_go = seen_setup_go or action == "actions/setup-go"
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
    match = re.search(r"var\s+contractPaths\s*=\s*\[\]string\s*\{(?P<body>.*?)\n\}", source, re.DOTALL)
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


def check_boundary_manifest(root: Path, errors: list[str]) -> None:
    path = root / "LICENSING_BOUNDARY.json"
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        errors.append(f"LICENSING_BOUNDARY.json: cannot parse exact boundary manifest: {exc}")
        return

    if data.get("format_version") != 1:
        errors.append("LICENSING_BOUNDARY.json: format_version must equal 1")
    if data.get("default_implementation_license") != "PolyForm Perimeter 1.0.1":
        errors.append("LICENSING_BOUNDARY.json: default implementation license drift")

    contract_paths = data.get("mit_contract_paths")
    if not isinstance(contract_paths, list) or len(contract_paths) != len(set(contract_paths)):
        errors.append("LICENSING_BOUNDARY.json: mit_contract_paths must be a duplicate-free list")
    elif frozenset(contract_paths) != MIT_CONTRACT_PATHS:
        errors.append("LICENSING_BOUNDARY.json: MIT contract path set does not equal the guarded allowlist")

    if data.get("mit_bootstrap_interface_sha256") != MIT_BOOTSTRAP_INTERFACE_SHA256:
        errors.append("LICENSING_BOUNDARY.json: bootstrap interface path/digest set drift")
    if data.get("mit_generated_output_sha256") != MIT_GENERATED_USER_REPO_OUTPUT_SHA256:
        errors.append("LICENSING_BOUNDARY.json: generated-output path/digest set drift")
    if data.get("generated_empty_placeholders_sha256") != GENERATED_EMPTY_PLACEHOLDER_SHA256:
        errors.append("LICENSING_BOUNDARY.json: generated empty-placeholder set drift")
    if data.get("historical_boundaries") != EXPECTED_HISTORICAL_BOUNDARIES:
        errors.append("LICENSING_BOUNDARY.json: historical boundary anchors drift")

    for mapping_name in (
        "mit_bootstrap_interface_sha256",
        "mit_generated_output_sha256",
        "generated_empty_placeholders_sha256",
    ):
        mapping = data.get(mapping_name)
        if not isinstance(mapping, dict):
            continue
        for rel, digest in mapping.items():
            if not isinstance(rel, str) or not isinstance(digest, str) or not SHA256.fullmatch(digest):
                errors.append(f"LICENSING_BOUNDARY.json: invalid path/SHA-256 in {mapping_name}")


def check_mit_interoperability_boundary(root: Path, contract_source: str, errors: list[str]) -> None:
    declared = parse_contract_paths(contract_source, errors)
    if declared != MIT_CONTRACT_PATHS:
        errors.append("contract.go: ContractPaths() does not equal the independently guarded MIT contract allowlist")
    embedded = resolve_contract_embed_paths(root, contract_source, errors)
    if embedded != MIT_CONTRACT_PATHS:
        errors.append("contract.go: resolved ContractFS embed set does not equal the independently guarded MIT contract allowlist")
    for rel in sorted(MIT_CONTRACT_PATHS):
        if not (root / rel).is_file():
            errors.append(f"{rel}: MIT contract allowlist path is missing")
    for rel, expected in MIT_BOOTSTRAP_INTERFACE_SHA256.items():
        if not (root / rel).is_file():
            errors.append(f"{rel}: MIT bootstrap-interface file is missing")
            continue
        check_exact_sha256(root, rel, expected, "MIT bootstrap-interface bytes", errors)
    if "AI_SETUP.md" in MIT_BOOTSTRAP_INTERFACE_PATHS:
        errors.append("AI_SETUP.md: must not be in the prospective MIT bootstrap-interface exception")


def regular_repository_files(root: Path, errors: list[str]) -> list[str]:
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
                    errors.append(f"{rel}: tracked non-regular Git object is not explicitly classified")
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
                errors.append(f"{rel}: historical licensing-text SHA-256 mismatch: got {actual}, want {historical_sha}")
            continue
        for label, pattern in FORBIDDEN_GLOBAL_LICENSE_PATTERNS:
            if pattern.search(text):
                errors.append(f"{rel}: contradictory licensing statement ({label})")
        if LICENSE_VOCAB_RE.search(text) and rel not in LICENSE_BEARING_TEXT_FILES:
            errors.append(f"{rel}: licensing-bearing readable file is not classified in LICENSE_BEARING_TEXT_FILES")


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

    for rel, expected in EXACT_LEGAL_SHA256.items():
        check_exact_sha256(root, rel, expected, "legal text", errors)
    for rel, expected in EXACT_POLICY_SHA256.items():
        check_exact_sha256(root, rel, expected, "policy bytes", errors)
    for rel, expected in EXACT_GIT_BLOB_SHA1.items():
        check_exact_git_blob_sha1(root, rel, expected, errors)

    check_boundary_manifest(root, errors)
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

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
    "docs/adr/ADR-026-runethread-licensing-and-commercial-model.md",
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
    r"\brightsholder\b|\bcopyright\b|\bpolyform\b|\bperimeter\b|\bMIT\b|"
    r"\bsource[- ]available\b|\bopen[- ]source\b|"
    r"\bcommercial[- ](?:use|model|license|licensing)\b"
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
    "Core binaries embed MIT-covered `ContractFS` material",
    "mixed-license distribution",
    "release workflow rejects every requested version other than the already-published v0.9.0 baseline",
    "Remediate the public `runethread/memory-template` MIT notice",
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
    "Historical MIT material",
    "User repositories and user data",
    "Readable-text licensing consistency",
    "every Git-tracked regular file that decodes as UTF-8 text",
    "two complementary protections",
    "Core binaries also embed the MIT-covered `ContractFS` interoperability material",
    "mixed-license distribution",
    "The public `runethread/memory-template` is already an active distribution",
    "does not create the underlying MIT grant",
    "No post-transition Core release may be requested or published",
)

ADR026_NEEDLES = (
    "Status: **Accepted**",
    "PolyForm Perimeter License 1.0.1",
    "portable Memory Contract",
    "Post-transition release distribution has an explicit mixed-license notice gate",
    "Core executables also embed the MIT-covered `ContractFS` interoperability material",
    "The public `runethread/memory-template` is already an active distribution",
)


def read(root: Path, rel: str, errors: list[str]) -> str:
    path = root / rel
    try:
        return path.read_text(encoding="utf-8")
    except OSError as exc:
        errors.append(f"{rel}: cannot read required file: {exc}")
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


def regular_repository_files(root: Path, errors: list[str]) -> list[str]:
    """Return repository-relative regular files, using the Git index when available."""
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
            if mode not in {b"100644", b"100755"}:
                continue
            try:
                rel = raw_path.decode("utf-8", errors="strict")
            except UnicodeDecodeError:
                errors.append("repository manifest: tracked regular-file path is not UTF-8")
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
            paths.append(Path(rel).as_posix())
        return sorted(set(paths))

    # Self-tests copy only the guarded repository surface into a temporary tree,
    # so there is intentionally no .git directory there. Walk regular files to
    # preserve the same readable-text behavior and to let tests add new files.
    paths = []
    for path in root.rglob("*"):
        try:
            mode = path.lstat().st_mode
        except OSError as exc:
            errors.append(f"{path}: cannot inspect test repository file: {exc}")
            continue
        if stat.S_ISREG(mode):
            paths.append(path.relative_to(root).as_posix())
    return sorted(set(paths))


def check_readable_licensing_surface(root: Path, errors: list[str]) -> None:
    for rel in regular_repository_files(root, errors):
        path = root / Path(rel)
        try:
            data = path.read_bytes()
        except OSError as exc:
            errors.append(f"{rel}: cannot read tracked regular file for licensing scan: {exc}")
            continue

        # NUL-bearing or non-UTF-8 files are not part of the readable-text surface.
        if b"\0" in data:
            continue
        try:
            text = data.decode("utf-8", errors="strict")
        except UnicodeDecodeError:
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
    adr026 = read(root, "docs/adr/ADR-026-runethread-licensing-and-commercial-model.md", errors)
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

#!/usr/bin/env python3
"""Self-tests for the mandatory Runethread development-policy guard."""

from __future__ import annotations

import importlib.util
import shutil
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "check_development_policy.py"

spec = importlib.util.spec_from_file_location("check_development_policy", SCRIPT)
assert spec and spec.loader
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


def copy_repo_surface() -> Path:
    root = Path(tempfile.mkdtemp(prefix="runethread-policy-test-"))
    for rel in module.REQUIRED_FILES:
        src = ROOT / rel
        dst = root / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)
    return root


def require_error(root: Path, needle: str) -> None:
    errors = module.check(root)
    if not any(needle in error for error in errors):
        raise AssertionError(f"expected error containing {needle!r}, got {errors!r}")


def test_current_repository_passes() -> None:
    errors = module.check(ROOT)
    if errors:
        raise AssertionError(f"current repository failed policy guard: {errors!r}")


def test_missing_agent_policy_fails() -> None:
    root = copy_repo_surface()
    try:
        (root / "AGENTS.md").unlink()
        require_error(root, "AGENTS.md")
    finally:
        shutil.rmtree(root)


def test_missing_pipeline_policy_fails() -> None:
    root = copy_repo_surface()
    try:
        (root / "docs/runethread/DEVELOPMENT_PIPELINE.md").unlink()
        require_error(root, "DEVELOPMENT_PIPELINE.md")
    finally:
        shutil.rmtree(root)


def test_missing_licensing_policy_fails() -> None:
    root = copy_repo_surface()
    try:
        (root / "LICENSING.md").unlink()
        require_error(root, "LICENSING.md")
    finally:
        shutil.rmtree(root)


def test_perimeter_version_drift_fails() -> None:
    root = copy_repo_surface()
    try:
        path = root / "LICENSE"
        text = path.read_text().replace("PolyForm Perimeter License 1.0.1", "PolyForm Perimeter License 9.9.9", 1)
        path.write_text(text)
        require_error(root, "LICENSE: exact legal text SHA-256 mismatch")
    finally:
        shutil.rmtree(root)


def test_perimeter_unchecked_clause_drift_fails() -> None:
    root = copy_repo_surface()
    try:
        path = root / "LICENSE"
        text = path.read_text().replace("within 32 days", "within 99 days", 1)
        path.write_text(text)
        require_error(root, "LICENSE: exact legal text SHA-256 mismatch")
    finally:
        shutil.rmtree(root)


def test_mit_unchecked_clause_drift_fails() -> None:
    root = copy_repo_surface()
    try:
        path = root / "LICENSE-MIT"
        text = path.read_text().replace("FITNESS FOR A PARTICULAR PURPOSE", "FITNESS FOR ANY PURPOSE", 1)
        path.write_text(text)
        require_error(root, "LICENSE-MIT: exact legal text SHA-256 mismatch")
    finally:
        shutil.rmtree(root)


def test_licensing_boundary_drift_fails() -> None:
    root = copy_repo_surface()
    try:
        path = root / "LICENSING.md"
        text = path.read_text().replace("Permissive interoperability boundary — MIT", "Interoperability boundary", 1)
        path.write_text(text)
        require_error(root, "Permissive interoperability boundary — MIT")
    finally:
        shutil.rmtree(root)


def test_licensing_mixed_distribution_drift_fails() -> None:
    root = copy_repo_surface()
    try:
        path = root / "LICENSING.md"
        text = path.read_text().replace("mixed-license distribution", "combined distribution", 1)
        path.write_text(text)
        require_error(root, "mixed-license distribution")
    finally:
        shutil.rmtree(root)


def test_licensing_cannot_drop_active_template_distribution_fails() -> None:
    root = copy_repo_surface()
    try:
        path = root / "LICENSING.md"
        text = path.read_text().replace(
            "The public `runethread/memory-template` is already an active distribution",
            "The public template may distribute",
            1,
        )
        path.write_text(text)
        require_error(root, "The public `runethread/memory-template` is already an active distribution")
    finally:
        shutil.rmtree(root)


def test_adr_cannot_drop_active_template_distribution_fails() -> None:
    root = copy_repo_surface()
    try:
        path = root / "docs/adr/ADR-026-runethread-licensing-and-commercial-model.md"
        text = path.read_text().replace(
            "The public `runethread/memory-template` is already an active distribution",
            "The public template may distribute",
            1,
        )
        path.write_text(text)
        require_error(root, "The public `runethread/memory-template` is already an active distribution")
    finally:
        shutil.rmtree(root)


def test_release_license_gate_bypass_fails() -> None:
    root = copy_repo_surface()
    try:
        path = root / ".github/workflows/release.yml"
        text = path.read_text().replace('if [ "$VERSION" != "v0.9.0" ]; then', "if false; then", 1)
        path.write_text(text)
        require_error(root, ".github/workflows/release.yml: exact protected file Git blob mismatch")
    finally:
        shutil.rmtree(root)


def test_release_license_gate_semantic_bypass_fails() -> None:
    root = copy_repo_surface()
    try:
        path = root / ".github/workflows/release.yml"
        text = path.read_text()
        marker = '          if [ "$VERSION" != "v0.9.0" ]; then\n'
        text = text.replace(marker, '          VERSION="v0.9.0"\n' + marker, 1)
        path.write_text(text)
        require_error(root, ".github/workflows/release.yml: exact protected file Git blob mismatch")
    finally:
        shutil.rmtree(root)


def test_process_cannot_drop_mixed_license_rule_fails() -> None:
    root = copy_repo_surface()
    try:
        path = root / "docs/runethread/ENGINEERING_PROCESS.md"
        text = path.read_text().replace(
            "Core binaries embed MIT-covered `ContractFS` interoperability material",
            "Core binaries include contract material",
            1,
        )
        path.write_text(text)
        require_error(root, "Core binaries embed MIT-covered `ContractFS` interoperability material")
    finally:
        shutil.rmtree(root)


def test_pipeline_cannot_drop_mixed_license_rule_fails() -> None:
    root = copy_repo_surface()
    try:
        path = root / "docs/runethread/DEVELOPMENT_PIPELINE.md"
        text = path.read_text().replace(
            "Core binaries embed MIT-covered `ContractFS` material",
            "Core binaries include contract material",
            1,
        )
        path.write_text(text)
        require_error(root, "Core binaries embed MIT-covered `ContractFS` material")
    finally:
        shutil.rmtree(root)


def test_milestone_cannot_drop_mixed_license_rule_fails() -> None:
    root = copy_repo_surface()
    try:
        path = root / "docs/runethread/CURRENT_MILESTONE.md"
        text = path.read_text().replace(
            "Core binaries embed MIT-covered `ContractFS` material",
            "Core binaries include contract material",
            1,
        )
        path.write_text(text)
        require_error(root, "Core binaries embed MIT-covered `ContractFS` material")
    finally:
        shutil.rmtree(root)


def test_milestone_cannot_drop_template_notice_gate_fails() -> None:
    root = copy_repo_surface()
    try:
        path = root / "docs/runethread/CURRENT_MILESTONE.md"
        text = path.read_text().replace(
            "Remediate the public `runethread/memory-template` MIT notice",
            "Update the template",
            1,
        )
        path.write_text(text)
        require_error(root, "Remediate the public `runethread/memory-template` MIT notice")
    finally:
        shutil.rmtree(root)


def test_validation_write_permission_fails() -> None:
    root = copy_repo_surface()
    try:
        path = root / ".github/workflows/validate.yml"
        text = path.read_text()
        text = text.replace("contents: read", "contents: write", 1)
        path.write_text(text)
        require_error(root, "contents: write")
    finally:
        shutil.rmtree(root)


def test_moving_action_tag_fails() -> None:
    root = copy_repo_surface()
    try:
        path = root / ".github/workflows/validate.yml"
        text = path.read_text()
        text = text.replace("actions/checkout@3d3c42e5aac5ba805825da76410c181273ba90b1", "actions/checkout@v7", 1)
        path.write_text(text)
        require_error(root, "immutable 40-hex commit SHA")
    finally:
        shutil.rmtree(root)


def test_new_unpinned_external_action_fails() -> None:
    root = copy_repo_surface()
    try:
        path = root / ".github/workflows/validate.yml"
        text = path.read_text()
        marker = "      - name: Verify module content\n"
        injected = "      - name: Unsafe moving action\n        uses: example/action@v1\n\n"
        text = text.replace(marker, injected + marker, 1)
        path.write_text(text)
        require_error(root, "example/action")
    finally:
        shutil.rmtree(root)


def test_missing_cross_platform_gate_fails() -> None:
    root = copy_repo_surface()
    try:
        path = root / ".github/workflows/validate.yml"
        text = path.read_text().replace("windows-latest", "windows-disabled", 1)
        path.write_text(text)
        require_error(root, "windows-latest")
    finally:
        shutil.rmtree(root)


def test_missing_race_detector_fails() -> None:
    root = copy_repo_surface()
    try:
        path = root / ".github/workflows/validate.yml"
        text = path.read_text().replace("go test -race -count=1 ./...", "go test -count=1 ./...", 1)
        path.write_text(text)
        require_error(root, "go test -race -count=1 ./...")
    finally:
        shutil.rmtree(root)


def test_missing_lf_policy_fails() -> None:
    root = copy_repo_surface()
    try:
        path = root / ".gitattributes"
        text = path.read_text().replace("* text=auto eol=lf", "* text=auto")
        path.write_text(text)
        require_error(root, "* text=auto eol=lf")
    finally:
        shutil.rmtree(root)


def test_missing_dependabot_actions_ecosystem_fails() -> None:
    root = copy_repo_surface()
    try:
        path = root / ".github/dependabot.yml"
        text = path.read_text().replace('package-ecosystem: "github-actions"', 'package-ecosystem: "disabled-actions"')
        path.write_text(text)
        require_error(root, 'package-ecosystem: "github-actions"')
    finally:
        shutil.rmtree(root)


def test_missing_codeowner_for_workflows_fails() -> None:
    root = copy_repo_surface()
    try:
        path = root / ".github/CODEOWNERS"
        text = path.read_text().replace("/.github/workflows/ @Karageorgiou", "/.github/workflows/ @nobody")
        path.write_text(text)
        require_error(root, "/.github/workflows/ @Karageorgiou")
    finally:
        shutil.rmtree(root)


def test_missing_codeowner_for_pipeline_policy_fails() -> None:
    root = copy_repo_surface()
    try:
        path = root / ".github/CODEOWNERS"
        text = path.read_text().replace(
            "/docs/runethread/DEVELOPMENT_PIPELINE.md @Karageorgiou",
            "/docs/runethread/DEVELOPMENT_PIPELINE.md @nobody",
        )
        path.write_text(text)
        require_error(root, "/docs/runethread/DEVELOPMENT_PIPELINE.md @Karageorgiou")
    finally:
        shutil.rmtree(root)


def test_missing_codeowner_for_licensing_fails() -> None:
    root = copy_repo_surface()
    try:
        path = root / ".github/CODEOWNERS"
        text = path.read_text().replace("/LICENSING.md @Karageorgiou", "/LICENSING.md @nobody", 1)
        path.write_text(text)
        require_error(root, "/LICENSING.md @Karageorgiou")
    finally:
        shutil.rmtree(root)


def test_pr_template_cannot_drop_scope_boundary_fails() -> None:
    root = copy_repo_surface()
    try:
        path = root / ".github/pull_request_template.md"
        text = path.read_text().replace("## Scope-boundary decision", "## Scope")
        path.write_text(text)
        require_error(root, "Scope-boundary decision")
    finally:
        shutil.rmtree(root)


def test_pr_template_cannot_drop_licensing_gate_fails() -> None:
    root = copy_repo_surface()
    try:
        path = root / ".github/pull_request_template.md"
        text = path.read_text().replace("## Licensing / rights gate", "## Rights notes", 1)
        path.write_text(text)
        require_error(root, "Licensing / rights gate")
    finally:
        shutil.rmtree(root)


def test_pipeline_cannot_drop_platform_no_bypass_rule_fails() -> None:
    root = copy_repo_surface()
    try:
        path = root / "docs/runethread/DEVELOPMENT_PIPELINE.md"
        text = path.read_text().replace("Cross-platform failures MUST NOT", "Cross-platform failures should not")
        path.write_text(text)
        require_error(root, "Cross-platform failures MUST NOT")
    finally:
        shutil.rmtree(root)


def main() -> None:
    tests = [value for name, value in sorted(globals().items()) if name.startswith("test_") and callable(value)]
    for test in tests:
        test()
        print(f"PASS {test.__name__}")


if __name__ == "__main__":
    main()

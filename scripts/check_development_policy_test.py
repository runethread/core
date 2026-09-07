#!/usr/bin/env python3
"""Self-tests for the mandatory Runethread development-policy guard."""

from __future__ import annotations

import hashlib
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
    rels = (
        set(module.REQUIRED_FILES)
        | set(module.MIT_CONTRACT_PATHS)
        | set(module.MIT_BOOTSTRAP_INTERFACE_PATHS)
    )
    for rel in sorted(rels):
        src = ROOT / rel
        dst = root / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)
    return root


def require_error(root: Path, needle: str) -> None:
    errors = module.check(root)
    if not any(needle in error for error in errors):
        raise AssertionError(f"expected error containing {needle!r}, got {errors!r}")


def require_clean(root: Path) -> None:
    errors = module.check(root)
    if errors:
        raise AssertionError(f"expected clean policy result, got {errors!r}")


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


def test_missing_readme_fails() -> None:
    root = copy_repo_surface()
    try:
        (root / "README.md").unlink()
        require_error(root, "README.md")
    finally:
        shutil.rmtree(root)


def test_missing_adr_catalog_fails() -> None:
    root = copy_repo_surface()
    try:
        (root / "docs/adr/README.md").unlink()
        require_error(root, "docs/adr/README.md")
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


def test_contract_paths_cannot_expand_mit_implicitly_fails() -> None:
    root = copy_repo_surface()
    try:
        path = root / "contract.go"
        text = path.read_text()
        marker = '\t"templates/reference.md",\n'
        text = text.replace(marker, marker + '\t"docs/NEW_INTEROP.md",\n', 1)
        path.write_text(text)
        require_error(root, "ContractPaths() does not equal the independently guarded MIT contract allowlist")
    finally:
        shutil.rmtree(root)


def test_contract_embed_wildcard_cannot_expand_mit_implicitly_fails() -> None:
    root = copy_repo_surface()
    try:
        path = root / "templates/new-unreviewed.md"
        path.write_text("# New unreviewed template\n")
        require_error(root, "resolved ContractFS embed set does not equal the independently guarded MIT contract allowlist")
    finally:
        shutil.rmtree(root)


def test_missing_mit_allowlist_file_fails() -> None:
    root = copy_repo_surface()
    try:
        (root / "templates/reference.md").unlink()
        require_error(root, "MIT interoperability allowlist path is missing")
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


def test_licensing_cannot_drop_closed_exception_fails() -> None:
    root = copy_repo_surface()
    try:
        path = root / "LICENSING.md"
        text = path.read_text().replace("closed and enumerated", "role based", 1)
        path.write_text(text)
        require_error(root, "closed and enumerated")
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


def test_licensing_cannot_drop_template_role_fails() -> None:
    root = copy_repo_surface()
    try:
        path = root / "LICENSING.md"
        text = path.read_text().replace(
            "MIT interoperability/bootstrap repository, not an implementation repository",
            "general Runethread repository",
            1,
        )
        path.write_text(text)
        require_error(root, "implementation repository")
    finally:
        shutil.rmtree(root)


def test_licensing_cannot_drop_readable_text_gate_fails() -> None:
    root = copy_repo_surface()
    try:
        path = root / "LICENSING.md"
        text = path.read_text().replace("Readable-text licensing consistency", "Text consistency", 1)
        path.write_text(text)
        require_error(root, "Readable-text licensing consistency")
    finally:
        shutil.rmtree(root)


def test_adr_cannot_drop_template_role_fails() -> None:
    root = copy_repo_surface()
    try:
        path = root / "docs/adr/ADR-026-runethread-licensing-and-commercial-model.md"
        text = path.read_text().replace(
            "MIT interoperability/bootstrap repository, not an implementation repository",
            "general Runethread repository",
            1,
        )
        path.write_text(text)
        require_error(root, "not an implementation repository")
    finally:
        shutil.rmtree(root)


def test_adr_cannot_broaden_closed_mit_exception_fails() -> None:
    root = copy_repo_surface()
    try:
        path = root / "docs/adr/ADR-026-runethread-licensing-and-commercial-model.md"
        text = path.read_text().replace("closed enumerated MIT exception", "broad role-based MIT category", 1)
        path.write_text(text)
        require_error(root, "closed enumerated MIT exception")
    finally:
        shutil.rmtree(root)


def test_readme_cannot_drop_mixed_boundary_fails() -> None:
    root = copy_repo_surface()
    try:
        path = root / "README.md"
        text = path.read_text().replace("mixed licensing boundary", "licensing model", 1)
        path.write_text(text)
        require_error(root, "mixed licensing boundary")
    finally:
        shutil.rmtree(root)


def test_readme_cannot_drop_source_available_marker_fails() -> None:
    root = copy_repo_surface()
    try:
        path = root / "README.md"
        text = path.read_text().replace("source-available", "publicly readable", 1)
        path.write_text(text)
        require_error(root, "source-available")
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


def test_process_cannot_drop_readable_text_scan_fails() -> None:
    root = copy_repo_surface()
    try:
        path = root / "docs/runethread/ENGINEERING_PROCESS.md"
        text = path.read_text().replace(
            "every Git-tracked regular file that decodes as UTF-8 text",
            "selected documentation files",
            1,
        )
        path.write_text(text)
        require_error(root, "every Git-tracked regular file that decodes as UTF-8 text")
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


def test_pipeline_cannot_drop_readable_text_scan_fails() -> None:
    root = copy_repo_surface()
    try:
        path = root / "docs/runethread/DEVELOPMENT_PIPELINE.md"
        text = path.read_text().replace(
            "repository-wide readable-text licensing consistency gate",
            "licensing consistency check",
            1,
        )
        path.write_text(text)
        require_error(root, "repository-wide readable-text licensing consistency gate")
    finally:
        shutil.rmtree(root)


def test_milestone_cannot_drop_mixed_license_rule_fails() -> None:
    root = copy_repo_surface()
    try:
        path = root / "docs/runethread/CURRENT_MILESTONE.md"
        text = path.read_text().replace(
            "Core binaries embed MIT-covered contract material",
            "Core binaries include contract material",
            1,
        )
        path.write_text(text)
        require_error(root, "Core binaries embed MIT-covered contract material")
    finally:
        shutil.rmtree(root)


def test_milestone_cannot_drop_template_protection_gate_fails() -> None:
    root = copy_repo_surface()
    try:
        path = root / "docs/runethread/CURRENT_MILESTONE.md"
        text = path.read_text().replace(
            "Protect and remediate the public `runethread/memory-template`",
            "Update the public template",
            1,
        )
        path.write_text(text)
        require_error(root, "Protect and remediate the public `runethread/memory-template`")
    finally:
        shutil.rmtree(root)


def test_roadmap_cannot_drop_template_protection_gate_fails() -> None:
    root = copy_repo_surface()
    try:
        path = root / "docs/runethread/ROADMAP.md"
        text = path.read_text().replace(
            "establish basic protected-`main` policy on `runethread/memory-template`",
            "update `runethread/memory-template`",
            1,
        )
        path.write_text(text)
        require_error(root, "establish basic protected-`main` policy on `runethread/memory-template`")
    finally:
        shutil.rmtree(root)


def test_new_unclassified_licensing_readable_file_fails() -> None:
    root = copy_repo_surface()
    try:
        path = root / "notes" / "policy.txt"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("Implementation notes for PolyForm Perimeter License 1.0.1.\n")
        require_error(root, "licensing-bearing readable file is not classified")
    finally:
        shutil.rmtree(root)


def test_broader_rights_vocabulary_is_classified_fails() -> None:
    root = copy_repo_surface()
    try:
        path = root / "notes" / "brand-policy.txt"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("This file defines the Runethread trademark policy.\n")
        require_error(root, "licensing-bearing readable file is not classified")
    finally:
        shutil.rmtree(root)


def test_contradictory_global_mit_claim_anywhere_fails() -> None:
    root = copy_repo_surface()
    try:
        path = root / "notes" / "stale.txt"
        path.parent.mkdir(parents=True, exist_ok=True)
        # Split the phrase so this self-test source is not itself a stale claim.
        bad = "Runethread " + "is released under " + "the MIT " + "License.\n"
        path.write_text(bad)
        require_error(root, "contradictory licensing statement")
    finally:
        shutil.rmtree(root)


def test_invalid_utf8_cannot_hide_licensing_text_fails() -> None:
    root = copy_repo_surface()
    try:
        path = root / "notes" / "opaque.txt"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(b"\xff\xfeopaque")
        require_error(root, "not valid UTF-8 and has no binary exception")
    finally:
        shutil.rmtree(root)


def test_nul_bearing_file_cannot_hide_licensing_text_fails() -> None:
    root = copy_repo_surface()
    try:
        path = root / "notes" / "nul.txt"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(b"Runethread\x00MIT\n")
        require_error(root, "NUL-bearing tracked regular file requires an explicit binary exception")
    finally:
        shutil.rmtree(root)


def test_nonregular_symlink_requires_explicit_classification_fails() -> None:
    root = copy_repo_surface()
    try:
        target = root / "notes" / "target.txt"
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text("ordinary target\n")
        link = root / "notes" / "link.txt"
        link.symlink_to(target.name)
        require_error(root, "non-regular repository object is not explicitly classified")
    finally:
        shutil.rmtree(root)


def test_exact_historical_license_text_exception_is_allowed_and_byte_locked() -> None:
    root = copy_repo_surface()
    rel = "notes/historical-license.txt"
    # Build the stale sentence dynamically so the test source itself is current-policy clean.
    data = ("Runethread " + "is released under " + "the MIT " + "License.\n").encode("utf-8")
    old = dict(module.HISTORICAL_LICENSE_TEXT_SHA256)
    try:
        path = root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
        module.HISTORICAL_LICENSE_TEXT_SHA256[rel] = hashlib.sha256(data).hexdigest()
        require_clean(root)
        path.write_bytes(data + b"changed\n")
        require_error(root, "historical licensing-text SHA-256 mismatch")
    finally:
        module.HISTORICAL_LICENSE_TEXT_SHA256.clear()
        module.HISTORICAL_LICENSE_TEXT_SHA256.update(old)
        shutil.rmtree(root)


def test_unrelated_new_readable_file_is_allowed() -> None:
    root = copy_repo_surface()
    try:
        path = root / "notes" / "ordinary.txt"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("Ordinary implementation note with no policy statement.\n")
        require_clean(root)
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


def test_missing_codeowner_for_readme_fails() -> None:
    root = copy_repo_surface()
    try:
        path = root / ".github/CODEOWNERS"
        text = path.read_text().replace("/README.md @Karageorgiou", "/README.md @nobody", 1)
        path.write_text(text)
        require_error(root, "/README.md @Karageorgiou")
    finally:
        shutil.rmtree(root)


def test_missing_codeowner_for_roadmap_fails() -> None:
    root = copy_repo_surface()
    try:
        path = root / ".github/CODEOWNERS"
        text = path.read_text().replace(
            "/docs/runethread/ROADMAP.md @Karageorgiou",
            "/docs/runethread/ROADMAP.md @nobody",
            1,
        )
        path.write_text(text)
        require_error(root, "/docs/runethread/ROADMAP.md @Karageorgiou")
    finally:
        shutil.rmtree(root)


def test_missing_codeowner_for_adr_catalog_fails() -> None:
    root = copy_repo_surface()
    try:
        path = root / ".github/CODEOWNERS"
        text = path.read_text().replace(
            "/docs/adr/README.md @Karageorgiou",
            "/docs/adr/README.md @nobody",
            1,
        )
        path.write_text(text)
        require_error(root, "/docs/adr/README.md @Karageorgiou")
    finally:
        shutil.rmtree(root)


def test_adr_catalog_cannot_drop_adr026_fails() -> None:
    root = copy_repo_surface()
    try:
        path = root / "docs/adr/README.md"
        text = path.read_text().replace(
            "[ADR-026](ADR-026-runethread-licensing-and-commercial-model.md)",
            "ADR-026 removed",
            1,
        )
        path.write_text(text)
        require_error(root, "[ADR-026](ADR-026-runethread-licensing-and-commercial-model.md)")
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

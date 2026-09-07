#!/usr/bin/env python3
"""Self-tests for the mandatory Runethread development-policy guard."""

from __future__ import annotations

import hashlib
import importlib.util
import shutil
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/check_development_policy.py"

spec = importlib.util.spec_from_file_location("check_development_policy", SCRIPT)
assert spec and spec.loader
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


def copy_repo_surface() -> Path:
    root = Path(tempfile.mkdtemp(prefix="runethread-policy-test-"))
    rels = set(module.REQUIRED_FILES) | set(module.MIT_CONTRACT_PATHS) | set(module.MIT_BOOTSTRAP_INTERFACE_PATHS)
    for rel in sorted(rels):
        src = ROOT / rel
        dst = root / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)
    return root


def replace_once(path: Path, old: str, new: str) -> None:
    text = path.read_text(encoding="utf-8")
    count = text.count(old)
    if count != 1:
        raise AssertionError(f"mutation target {old!r} occurred {count} times in {path}; expected exactly once")
    changed = text.replace(old, new, 1)
    if changed == text:
        raise AssertionError(f"mutation unexpectedly produced no change in {path}")
    path.write_text(changed, encoding="utf-8")


def require_error(root: Path, needle: str) -> None:
    errors = module.check(root)
    if not any(needle in error for error in errors):
        raise AssertionError(f"expected error containing {needle!r}, got {errors!r}")


def require_clean(root: Path) -> None:
    errors = module.check(root)
    if errors:
        raise AssertionError(f"expected clean policy result, got {errors!r}")


def test_current_repository_passes() -> None:
    require_clean(ROOT)


def test_mutation_helper_rejects_missing_target() -> None:
    root = Path(tempfile.mkdtemp(prefix="runethread-policy-mutation-test-"))
    try:
        path = root / "sample.txt"
        path.write_text("alpha\n", encoding="utf-8")
        try:
            replace_once(path, "missing", "changed")
        except AssertionError:
            return
        raise AssertionError("replace_once accepted a missing mutation target")
    finally:
        shutil.rmtree(root)


def test_missing_required_policy_files_fail() -> None:
    for rel in (
        "AGENTS.md",
        "LICENSING.md",
        "LICENSING_BOUNDARY.json",
        "README.md",
        "docs/adr/README.md",
        "internal/starter/output_identity_test.go",
    ):
        root = copy_repo_surface()
        try:
            (root / rel).unlink()
            require_error(root, rel)
        finally:
            shutil.rmtree(root)


def test_perimeter_legal_text_drift_fails() -> None:
    root = copy_repo_surface()
    try:
        path = root / "LICENSE"
        replace_once(path, "within 32 days", "within 99 days")
        require_error(root, "LICENSE: exact legal text SHA-256 mismatch")
    finally:
        shutil.rmtree(root)


def test_mit_legal_text_drift_fails() -> None:
    root = copy_repo_surface()
    try:
        path = root / "LICENSE-MIT"
        replace_once(path, "FITNESS FOR A PARTICULAR PURPOSE", "FITNESS FOR ANY PURPOSE")
        require_error(root, "LICENSE-MIT: exact legal text SHA-256 mismatch")
    finally:
        shutil.rmtree(root)


def test_boundary_manifest_any_byte_drift_fails() -> None:
    root = copy_repo_surface()
    try:
        path = root / "LICENSING_BOUNDARY.json"
        replace_once(path, '"format_version": 1', '"format_version": 2')
        require_error(root, "LICENSING_BOUNDARY.json: exact policy bytes SHA-256 mismatch")
    finally:
        shutil.rmtree(root)


def test_boundary_manifest_cannot_expand_contract_exception() -> None:
    root = copy_repo_surface()
    try:
        path = root / "LICENSING_BOUNDARY.json"
        replace_once(path, '    "templates/reference.md"\n', '    "templates/reference.md",\n    "docs/NEW_INTEROP.md"\n')
        require_error(root, "exact policy bytes SHA-256 mismatch")
        require_error(root, "MIT contract path set does not equal the guarded allowlist")
    finally:
        shutil.rmtree(root)


def test_boundary_manifest_cannot_add_ai_setup_to_prospective_exception() -> None:
    root = copy_repo_surface()
    try:
        path = root / "LICENSING_BOUNDARY.json"
        marker = '  "mit_bootstrap_interface_sha256": {\n    "runethread-bootstrap.json": "23c71ec28f548755cba680a318e1ad344c1f419de403104d1a46a5512625742d"\n  },'
        replacement = '  "mit_bootstrap_interface_sha256": {\n    "AI_SETUP.md": "0000000000000000000000000000000000000000000000000000000000000000",\n    "runethread-bootstrap.json": "23c71ec28f548755cba680a318e1ad344c1f419de403104d1a46a5512625742d"\n  },'
        replace_once(path, marker, replacement)
        require_error(root, "bootstrap interface path/digest set drift")
    finally:
        shutil.rmtree(root)


def test_bootstrap_interface_byte_drift_fails() -> None:
    root = copy_repo_surface()
    try:
        path = root / "runethread-bootstrap.json"
        replace_once(path, '"bootstrap_protocol": 1', '"bootstrap_protocol": 2')
        require_error(root, "MIT bootstrap-interface bytes SHA-256 mismatch")
    finally:
        shutil.rmtree(root)


def test_contract_go_textual_spoof_is_blocked_by_exact_blob_lock() -> None:
    root = copy_repo_surface()
    try:
        path = root / "contract.go"
        text = path.read_text(encoding="utf-8")
        path.write_text("// var contractPaths = []string{\"docs/FAKE.md\"}\n" + text, encoding="utf-8")
        require_error(root, "contract.go: exact protected file Git blob mismatch")
    finally:
        shutil.rmtree(root)


def test_contract_paths_cannot_expand_implicitly() -> None:
    root = copy_repo_surface()
    try:
        path = root / "contract.go"
        replace_once(path, '\t"templates/reference.md",\n', '\t"templates/reference.md",\n\t"docs/NEW_INTEROP.md",\n')
        require_error(root, "ContractPaths() does not equal the independently guarded MIT contract allowlist")
    finally:
        shutil.rmtree(root)


def test_contract_embed_wildcard_cannot_expand_implicitly() -> None:
    root = copy_repo_surface()
    try:
        path = root / "templates/new-unreviewed.md"
        path.write_text("# New unreviewed template\n", encoding="utf-8")
        require_error(root, "resolved ContractFS embed set does not equal the independently guarded MIT contract allowlist")
    finally:
        shutil.rmtree(root)


def test_missing_contract_allowlist_file_fails() -> None:
    root = copy_repo_surface()
    try:
        (root / "templates/reference.md").unlink()
        require_error(root, "MIT contract allowlist path is missing")
    finally:
        shutil.rmtree(root)


def test_validate_workflow_any_semantic_drift_fails_exact_lock() -> None:
    root = copy_repo_surface()
    try:
        path = root / ".github/workflows/validate.yml"
        replace_once(path, "python3 scripts/check_development_policy.py", "echo policy-disabled")
        require_error(root, ".github/workflows/validate.yml: exact protected file Git blob mismatch")
    finally:
        shutil.rmtree(root)


def test_validation_write_permission_fails() -> None:
    root = copy_repo_surface()
    try:
        path = root / ".github/workflows/validate.yml"
        replace_once(path, "contents: read", "contents: write")
        require_error(root, "contents: write")
    finally:
        shutil.rmtree(root)


def test_moving_action_tag_fails() -> None:
    root = copy_repo_surface()
    try:
        path = root / ".github/workflows/validate.yml"
        marker = "        uses: actions/checkout@3d3c42e5aac5ba805825da76410c181273ba90b1 # v7\n        with:\n          fetch-depth: 0"
        replacement = "        uses: actions/checkout@v7\n        with:\n          fetch-depth: 0"
        replace_once(path, marker, replacement)
        require_error(root, "immutable 40-hex commit SHA")
    finally:
        shutil.rmtree(root)


def test_release_license_gate_bypass_fails() -> None:
    root = copy_repo_surface()
    try:
        path = root / ".github/workflows/release.yml"
        replace_once(path, 'if [ "$VERSION" != "v0.9.0" ]; then', "if false; then")
        require_error(root, ".github/workflows/release.yml: exact protected file Git blob mismatch")
    finally:
        shutil.rmtree(root)


def test_licensing_policy_markers_are_fail_closed() -> None:
    root = copy_repo_surface()
    try:
        path = root / "LICENSING.md"
        replace_once(path, "Perimeter is the default everywhere else", "defaults are inferred")
        require_error(root, "Perimeter is the default everywhere else")
    finally:
        shutil.rmtree(root)


def test_licensing_policy_cannot_readd_ai_setup_exception() -> None:
    root = copy_repo_surface()
    try:
        path = root / "LICENSING.md"
        replace_once(path, "AI_SETUP.md is not part of the prospective MIT exception", "AI_SETUP.md follows the bootstrap exception")
        require_error(root, "AI_SETUP.md is not part of the prospective MIT exception")
    finally:
        shutil.rmtree(root)


def test_licensing_policy_cannot_hide_branch_boundary() -> None:
    root = copy_repo_surface()
    try:
        path = root / "LICENSING.md"
        marker = "first public development-branch snapshot whose root license is Perimeter"
        replace_once(path, marker, "development-branch licensing history is unspecified")
        require_error(root, marker)
    finally:
        shutil.rmtree(root)


def test_adr_cannot_drop_machine_boundary_authority() -> None:
    root = copy_repo_surface()
    try:
        path = root / "docs/adr/ADR-026-runethread-licensing-and-commercial-model.md"
        replace_once(path, "Generated-output byte identity is independently proved", "Generated-output identity is informal")
        require_error(root, "Generated-output byte identity")
    finally:
        shutil.rmtree(root)


def test_readme_cannot_broaden_summary() -> None:
    root = copy_repo_surface()
    try:
        path = root / "README.md"
        replace_once(path, "Perimeter is the default everywhere else", "the rest is unspecified")
        require_error(root, "Perimeter is the default everywhere else")
    finally:
        shutil.rmtree(root)


def test_category_wide_mit_exception_claim_fails() -> None:
    root = copy_repo_surface()
    try:
        path = root / "docs/runethread/ROADMAP.md"
        bad = (
            "The Memory Contract/bootstrap/"
            + "generated-support interoperability layer "
            + "remains MIT.\n"
        )
        with path.open("a", encoding="utf-8") as handle:
            handle.write("\n" + bad)
        require_error(root, "category-wide MIT exception claim")
    finally:
        shutil.rmtree(root)


def test_output_identity_symlink_guard_cannot_be_removed() -> None:
    root = copy_repo_surface()
    try:
        path = root / "internal/starter/output_identity_test.go"
        replace_once(path, "TestGeneratedOutputIdentityRejectsSymlink", "TestGeneratedOutputIdentityAllowsSymlink")
        require_error(root, "TestGeneratedOutputIdentityRejectsSymlink")
    finally:
        shutil.rmtree(root)


def test_new_unclassified_licensing_readable_file_fails() -> None:
    root = copy_repo_surface()
    try:
        path = root / "notes" / "policy.txt"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("Implementation notes for PolyForm Perimeter License 1.0.1.\n", encoding="utf-8")
        require_error(root, "licensing-bearing readable file is not classified")
    finally:
        shutil.rmtree(root)


def test_broader_rights_vocabulary_is_classified_fails() -> None:
    root = copy_repo_surface()
    try:
        path = root / "notes" / "brand-policy.txt"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("This file defines the Runethread trademark policy.\n", encoding="utf-8")
        require_error(root, "licensing-bearing readable file is not classified")
    finally:
        shutil.rmtree(root)


def test_contradictory_global_mit_claim_anywhere_fails() -> None:
    root = copy_repo_surface()
    try:
        path = root / "notes" / "stale.txt"
        path.parent.mkdir(parents=True, exist_ok=True)
        bad = "Runethread " + "is released under " + "the MIT " + "License.\n"
        path.write_text(bad, encoding="utf-8")
        require_error(root, "contradictory licensing statement")
    finally:
        shutil.rmtree(root)


def test_invalid_utf8_cannot_hide_text_fails() -> None:
    root = copy_repo_surface()
    try:
        path = root / "notes" / "opaque.txt"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(b"\xff\xfeopaque")
        require_error(root, "not valid UTF-8 and has no binary exception")
    finally:
        shutil.rmtree(root)


def test_nul_bearing_file_cannot_hide_text_fails() -> None:
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
        target.write_text("ordinary target\n", encoding="utf-8")
        link = root / "notes" / "link.txt"
        link.symlink_to(target.name)
        require_error(root, "non-regular repository object is not explicitly classified")
    finally:
        shutil.rmtree(root)


def test_exact_historical_text_exception_is_allowed_and_byte_locked() -> None:
    root = copy_repo_surface()
    rel = "notes/historical-license.txt"
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
        path.write_text("Ordinary implementation note with no policy statement.\n", encoding="utf-8")
        require_clean(root)
    finally:
        shutil.rmtree(root)


def test_codeowners_protect_new_boundary_surfaces() -> None:
    for old in (
        "/LICENSING_BOUNDARY.json @Karageorgiou",
        "/internal/starter/output_identity_test.go @Karageorgiou",
        "/.github/workflows/ @Karageorgiou",
    ):
        root = copy_repo_surface()
        try:
            path = root / ".github/CODEOWNERS"
            replace_once(path, old, old.replace("@Karageorgiou", "@nobody"))
            require_error(root, old)
        finally:
            shutil.rmtree(root)


def test_pr_template_cannot_drop_licensing_gate() -> None:
    root = copy_repo_surface()
    try:
        path = root / ".github/pull_request_template.md"
        replace_once(path, "## Licensing / rights gate", "## Rights notes")
        require_error(root, "Licensing / rights gate")
    finally:
        shutil.rmtree(root)


def test_pipeline_platform_bypass_rule_remains() -> None:
    root = copy_repo_surface()
    try:
        path = root / "docs/runethread/DEVELOPMENT_PIPELINE.md"
        replace_once(path, "Cross-platform failures MUST NOT", "Cross-platform failures should not")
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

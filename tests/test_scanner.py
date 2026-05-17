"""Smoke tests for the scanner + starter catalog."""

from pathlib import Path

from leakguard.catalog import load_starter_catalog, load_with_overrides
from leakguard.scanner import scan_paths


FIXTURES = Path(__file__).parent / "fixtures"


def test_starter_catalog_loads_with_expected_classes():
    catalog = load_starter_catalog()
    ids = {c["id"] for c in catalog.classes}
    expected = {
        "cross-project-codenames",
        "operator-paths",
        "private-wrapper-services",
        "phase-numbering",
        "handoff-doc-names",
        "agent-memory-ids",
        "time-of-day-narration",
        "user-pushback",
        "agent-actor-references",
        "session-restart-narration",
        "session-state-framing",
        "strategic-process-framing",
    }
    assert expected.issubset(ids)


def test_clean_file_has_no_findings():
    catalog = load_starter_catalog()
    findings = scan_paths([FIXTURES / "clean.md"], catalog.classes)
    assert findings == [], f"clean fixture leaked: {findings}"


def test_leaky_file_flags_multiple_classes():
    catalog = load_starter_catalog()
    findings = scan_paths([FIXTURES / "leaky.md"], catalog.classes)
    ids = {f.class_id for f in findings}
    assert "phase-numbering" in ids
    assert "session-state-framing" in ids
    assert "agent-memory-ids" in ids
    assert "time-of-day-narration" in ids
    assert "user-pushback" in ids
    assert "handoff-doc-names" in ids


def test_scan_returns_line_numbers():
    catalog = load_starter_catalog()
    findings = scan_paths([FIXTURES / "leaky.md"], catalog.classes)
    assert all(f.line_no > 0 for f in findings)
    assert all(isinstance(f.line, str) for f in findings)


def test_ignore_patterns_skip_matching_files():
    catalog = load_starter_catalog()
    findings = scan_paths(
        [FIXTURES / "leaky.md"],
        catalog.classes,
        ignore_patterns=["tests/fixtures/leaky.md", "leaky.md"],
    )
    assert findings == []


def test_load_with_overrides_returns_starter_when_no_user_file(tmp_path):
    missing = tmp_path / "does-not-exist.yaml"
    catalog = load_with_overrides(missing)
    assert len(catalog.classes) > 0
    assert catalog.ignore_paths == []


def test_load_with_overrides_merges_ignore_paths(tmp_path):
    user_yaml = tmp_path / "leakguard.yaml"
    user_yaml.write_text(
        "version: 1\nignore_paths:\n  - foo/**\n  - bar.md\nclasses: []\n"
    )
    catalog = load_with_overrides(user_yaml)
    assert "foo/**" in catalog.ignore_paths
    assert "bar.md" in catalog.ignore_paths

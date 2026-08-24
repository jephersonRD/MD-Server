#!/usr/bin/env python3
"""Tests for MD Server v1.1.7-beta — Java compatibility system."""
import os
import sys
import json

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.java_manager import (
    get_recommended_java,
    get_compatible_java_versions,
    is_java_compatible,
    can_install_java,
    TERMUX_JAVA_PACKAGES,
    KNOWN_JAVA_VERSIONS,
    migrate_old_server_meta,
    _JAVA_COMPAT,
)


def test_java_compatibility_matrix():
    """Test all required Minecraft → Java mappings."""
    cases = [
        ("1.7.10", 8),
        ("1.12.2", 8),
        ("1.16.5", 8),
        ("1.17", 16),
        ("1.17.1", 16),
        ("1.18", 17),
        ("1.18.1", 17),
        ("1.18.2", 17),
        ("1.19", 17),
        ("1.19.4", 17),
        ("1.20", 17),
        ("1.20.1", 17),
        ("1.20.2", 17),
        ("1.20.3", 17),
        ("1.20.4", 17),
        ("1.20.5", 21),
        ("1.20.6", 21),
        ("1.21", 21),
        ("1.21.1", 21),
        ("1.21.4", 21),
        ("1.21.11", 21),
        ("26.1", 25),
        ("26.2", 25),
    ]
    passed = 0
    failed = 0
    for mc_ver, expected_java in cases:
        result = get_recommended_java(mc_ver)
        status = "✓" if result == expected_java else "✗"
        if result == expected_java:
            passed += 1
        else:
            failed += 1
        print(f"  {status} Minecraft {mc_ver:<10} → Java {result} (expected {expected_java})")
    return failed == 0


def test_compatible_versions():
    """Test that compatible versions are ordered correctly."""
    cases = [
        ("1.7.10", [8, 16, 17, 21, 25]),
        ("1.17.1", [16, 17, 21, 25, 8]),
        ("1.20.1", [17, 21, 25, 8, 16]),
        ("1.21.1", [21, 25, 8, 16, 17]),
        ("26.1", [25, 8, 16, 17, 21]),
    ]
    passed = 0
    failed = 0
    for mc_ver, expected_order in cases:
        result = get_compatible_java_versions(mc_ver)
        if result == expected_order:
            passed += 1
            print(f"  ✓ Minecraft {mc_ver:<10} compatible order: {result}")
        else:
            failed += 1
            print(f"  ✗ Minecraft {mc_ver:<10} expected {expected_order}, got {result}")
    return failed == 0


def test_is_java_compatible():
    """Test compatibility checks."""
    cases = [
        ("1.20.1", 17, True),
        ("1.20.1", 21, True),
        ("1.20.1", 25, True),
        ("1.20.1", 8, False),
        ("1.20.1", 16, False),
        ("1.7.10", 8, True),
        ("1.7.10", 17, True),
        ("1.7.10", 21, True),
        ("1.21.1", 21, True),
        ("1.21.1", 17, False),
        ("1.21.1", 8, False),
    ]
    passed = 0
    failed = 0
    for mc_ver, java_ver, expected in cases:
        result = is_java_compatible(mc_ver, java_ver)
        status = "✓" if result == expected else "✗"
        if result == expected:
            passed += 1
        else:
            failed += 1
        print(f"  {status} MC {mc_ver} + Java {java_ver}: compatible={result} (expected {expected})")
    return failed == 0


def test_can_install_java():
    """Test which Java versions can be installed via Termux."""
    cases = [
        (8, False),
        (16, False),
        (17, True),
        (21, True),
        (25, True),
    ]
    passed = 0
    failed = 0
    for jver, expected in cases:
        result = can_install_java(jver)
        status = "✓" if result == expected else "✗"
        if result == expected:
            passed += 1
        else:
            failed += 1
        print(f"  {status} Java {jver}: can_install={result} (expected {expected})")
    return failed == 0


def test_termux_packages_has_java25():
    """Test that Java 25 is in TERMUX_JAVA_PACKAGES."""
    if 25 in TERMUX_JAVA_PACKAGES:
        print(f"  ✓ Java 25 in TERMUX_JAVA_PACKAGES: {TERMUX_JAVA_PACKAGES[25]}")
        return True
    else:
        print(f"  ✗ Java 25 NOT in TERMUX_JAVA_PACKAGES")
        return False


def test_known_java_versions():
    """Test that all required Java versions are known."""
    required = {8, 16, 17, 21, 25}
    actual = set(KNOWN_JAVA_VERSIONS)
    missing = required - actual
    if missing:
        print(f"  ✗ Missing Java versions: {missing}")
        return False
    print(f"  ✓ All required Java versions present: {sorted(required)}")
    return True


def test_compat_table_has_all_entries():
    """Test that the compatibility table has entries for all required versions."""
    required = [
        "1.7.10", "1.12.2", "1.16.5",
        "1.17", "1.17.1",
        "1.18", "1.18.1", "1.18.2",
        "1.19", "1.19.1", "1.19.2", "1.19.3", "1.19.4",
        "1.20", "1.20.1", "1.20.2", "1.20.3", "1.20.4", "1.20.5", "1.20.6",
        "1.21", "1.21.1", "1.21.2", "1.21.3", "1.21.4", "1.21.5",
        "1.21.6", "1.21.7", "1.21.8", "1.21.9", "1.21.10", "1.21.11",
        "26.1", "26.2",
    ]
    table_versions = {entry[0] for entry in _JAVA_COMPAT}
    missing = set(required) - table_versions
    if missing:
        print(f"  ✗ Missing from table: {sorted(missing)}")
        return False
    print(f"  ✓ All {len(required)} required versions in table")
    return True


def test_unknown_version_defaults():
    """Test that unknown future versions get reasonable defaults."""
    cases = [
        ("1.22", 21),
        ("1.23", 21),
        ("27.1", 25),
        ("30.0", 25),
    ]
    passed = 0
    failed = 0
    for mc_ver, expected in cases:
        result = get_recommended_java(mc_ver)
        if result == expected:
            passed += 1
            print(f"  ✓ Unknown MC {mc_ver:<10} → Java {result} (default)")
        else:
            failed += 1
            print(f"  ✗ Unknown MC {mc_ver:<10} expected {expected}, got {result}")
    return failed == 0


def test_i18n_keys():
    """Test that all required i18n keys exist in both locales."""
    required_keys = [
        "wizard.java_title",
        "wizard.java_minecraft",
        "wizard.java_recommended_label",
        "wizard.java_version",
        "wizard.java_select",
        "wizard.java_recommended",
        "wizard.java_compatible",
        "wizard.java_incompatible",
        "wizard.java_incompatible_warning",
        "wizard.java_downloading",
        "wizard.java_verify_failed",
        "wizard.java_not_available",
        "wizard.java_not_available_termux",
        "wizard.java_available_versions",
        "wizard.java_explain_need",
        "wizard.java_explain_recommended",
        "wizard.java_explain_compatible",
        "wizard.java_explain_incompatible",
        "wizard.java_install_failed",
        "wizard.java_install_failed_title",
        "wizard.java_retry",
        "wizard.java_choose_other",
        "wizard.back",
        "wizard.back_to_type",
        "wizard.back_to_version",
        "java.incompatible",
        "java.recommended",
        "java.version_mismatch",
        "java.selected",
        "java.found",
        "java.install_missing",
        "java.choose_other",
        "dash.java",
    ]
    passed = 0
    failed = 0
    for lang in ("es", "en"):
        path = os.path.join(os.path.dirname(__file__), "locales", f"{lang}.json")
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        for key in required_keys:
            if key in data:
                passed += 1
            else:
                failed += 1
                print(f"  ✗ Missing key '{key}' in {lang}.json")
    if failed == 0:
        print(f"  ✓ All {len(required_keys)} i18n keys present in es.json and en.json")
    return failed == 0


def test_version_string():
    """Test that version is correctly set."""
    from main import __version__
    if __version__ == "1.1.7-beta":
        print(f"  ✓ Version: {__version__}")
        return True
    else:
        print(f"  ✗ Version: {__version__} (expected 1.1.7-beta)")
        return False


if __name__ == "__main__":
    print("=" * 60)
    print("MD Server v1.1.7-beta — Test Suite")
    print("=" * 60)
    print()

    tests = [
        ("Java Compatibility Matrix", test_java_compatibility_matrix),
        ("Compatible Versions Order", test_compatible_versions),
        ("Is Java Compatible", test_is_java_compatible),
        ("Can Install Java", test_can_install_java),
        ("Termux Packages has Java 25", test_termux_packages_has_java25),
        ("Known Java Versions", test_known_java_versions),
        ("Compat Table Entries", test_compat_table_has_all_entries),
        ("Unknown Version Defaults", test_unknown_version_defaults),
        ("i18n Keys", test_i18n_keys),
        ("Version String", test_version_string),
    ]

    all_passed = True
    for name, fn in tests:
        print(f"[{name}]")
        try:
            ok = fn()
            if not ok:
                all_passed = False
        except Exception as e:
            print(f"  ✗ EXCEPTION: {e}")
            all_passed = False
        print()

    print("=" * 60)
    if all_passed:
        print("✓ ALL TESTS PASSED")
    else:
        print("✗ SOME TESTS FAILED")
    print("=" * 60)
    sys.exit(0 if all_passed else 1)

#!/usr/bin/env python3
"""
Version consistency checker for domd project.
Ensures version is consistent across pyproject.toml, __init__.py, and CHANGELOG.md
"""

import re
import sys
import toml
from pathlib import Path


def get_version_from_pyproject():
    """Get version from pyproject.toml."""
    try:
        with open("pyproject.toml", "r") as f:
            data = toml.load(f)
        return data["tool"]["poetry"]["version"]
    except Exception as e:
        print(f"Error reading pyproject.toml: {e}")
        return None


def get_version_from_init():
    """Get version from src/domd/__init__.py."""
    try:
        init_path = Path("src/domd/__init__.py")
        content = init_path.read_text()
        match = re.search(r'__version__\s*=\s*["\']([^"\']+)["\']', content)
        if match:
            return match.group(1)
        return None
    except Exception as e:
        print(f"Error reading __init__.py: {e}")
        return None


def get_version_from_changelog():
    """Get latest version from CHANGELOG.md."""
    try:
        with open("CHANGELOG.md", "r") as f:
            content = f.read()

        # Look for version patterns like ## [0.1.0]
        matches = re.findall(r'##\s*\[([^\]]+)\]', content)
        if matches:
            # Return the first (latest) version, excluding "Unreleased"
            for version in matches:
                if version.lower() != "unreleased":
                    return version
        return None
    except Exception as e:
        print(f"Error reading CHANGELOG.md: {e}")
        return None


def check_version_consistency():
    """Check if versions are consistent across all files."""
    pyproject_version = get_version_from_pyproject()
    init_version = get_version_from_init()
    changelog_version = get_version_from_changelog()

    print("Version Consistency Check")
    print("=" * 30)
    print(f"pyproject.toml: {pyproject_version}")
    print(f"__init__.py:    {init_version}")
    print(f"CHANGELOG.md:   {changelog_version}")
    print()

    if not all([pyproject_version, init_version, changelog_version]):
        print("❌ Error: Could not read version from one or more files")
        return False

    if pyproject_version == init_version == changelog_version:
        print("✅ All versions are consistent!")
        return True
    else:
        print("❌ Version mismatch detected!")
        if pyproject_version != init_version:
            print(f"   pyproject.toml vs __init__.py: {pyproject_version} != {init_version}")
        if pyproject_version != changelog_version:
            print(f"   pyproject.toml vs CHANGELOG.md: {pyproject_version} != {changelog_version}")
        if init_version != changelog_version:
            print(f"   __init__.py vs CHANGELOG.md: {init_version} != {changelog_version}")
        return False


def update_version(new_version):
    """Update version in all files."""
    print(f"Updating version to {new_version}...")

    # Update pyproject.toml
    try:
        with open("pyproject.toml", "r") as f:
            data = toml.load(f)
        data["tool"]["poetry"]["version"] = new_version
        with open("pyproject.toml", "w") as f:
            toml.dump(data, f)
        print("✅ Updated pyproject.toml")
    except Exception as e:
        print(f"❌ Error updating pyproject.toml: {e}")
        return False

    # Update __init__.py
    try:
        init_path = Path("src/domd/__init__.py")
        content = init_path.read_text()
        updated_content = re.sub(
            r'__version__\s*=\s*["\'][^"\']+["\']',
            f'__version__ = "{new_version}"',
            content
        )
        init_path.write_text(updated_content)
        print("✅ Updated __init__.py")
    except Exception as e:
        print(f"❌ Error updating __init__.py: {e}")
        return False

    print(f"✅ Version updated to {new_version}")
    print("📝 Don't forget to update CHANGELOG.md manually!")
    return True


def main():
    """Main function."""
    if len(sys.argv) > 1:
        if sys.argv[1] == "--update" and len(sys.argv) > 2:
            new_version = sys.argv[2]
            success = update_version(new_version)
            sys.exit(0 if success else 1)
        elif sys.argv[1] == "--help":
            print("Usage:")
            print("  python check_version.py                    # Check consistency")
            print("  python check_version.py --update X.Y.Z     # Update version")
            print("  python check_version.py --help             # Show help")
            sys.exit(0)

    # Default: check consistency
    success = check_version_consistency()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
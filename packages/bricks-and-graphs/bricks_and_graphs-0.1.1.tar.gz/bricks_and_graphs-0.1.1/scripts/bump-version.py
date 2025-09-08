#!/usr/bin/env python3
"""
Script to bump version in both pyproject.toml and src/bag/__init__.py
Usage: python scripts/bump-version.py [major|minor|patch] [--dry-run]
"""

import argparse
import re
import sys
from pathlib import Path


def get_current_version(file_path: str, pattern: str) -> str:
    """Get current version from a file."""
    content = Path(file_path).read_text()
    match = re.search(pattern, content, re.MULTILINE)
    if not match:
        raise ValueError(f"Version not found in {file_path}")
    return match.group(2)  # Version is in group 2: (prefix)(VERSION)(suffix)


def update_version_in_file(
    file_path: str, pattern: str, new_version: str, dry_run: bool = False
) -> None:
    """Update version in a file."""
    content = Path(file_path).read_text()
    new_content = re.sub(
        pattern, rf"\g<1>{new_version}\g<3>", content, flags=re.MULTILINE
    )

    if dry_run:
        print(f"Would update {file_path}")
    else:
        Path(file_path).write_text(new_content)
        print(f"✅ Updated {file_path}")


def bump_version(current_version: str, bump_type: str) -> str:
    """Bump version based on type."""
    major, minor, patch = map(int, current_version.split("."))

    if bump_type == "major":
        return f"{major + 1}.0.0"
    elif bump_type == "minor":
        return f"{major}.{minor + 1}.0"
    elif bump_type == "patch":
        return f"{major}.{minor}.{patch + 1}"
    else:
        raise ValueError(f"Invalid bump type: {bump_type}")


def main():
    parser = argparse.ArgumentParser(description="Bump version in project files")
    parser.add_argument(
        "bump_type", choices=["major", "minor", "patch"], help="Type of version bump"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be changed without making changes",
    )

    args = parser.parse_args()

    # File patterns - be very specific to avoid updating wrong version fields
    files = [
        {
            "path": "pyproject.toml",
            # Only match exact line: version = "x.y.z"
            "pattern": r'^(version = ")([^"]+)(")$',
        },
        {
            "path": "src/bag/__init__.py",
            # Only match exact __version__ line
            "pattern": r'^(__version__: Final\[str\] = ")([^"]+)(")$',
        },
    ]

    try:
        # Get current version from pyproject.toml
        current_version = get_current_version(files[0]["path"], files[0]["pattern"])
        new_version = bump_version(current_version, args.bump_type)

        print(f"Current version: {current_version}")
        print(f"New version: {new_version}")
        print()

        if args.dry_run:
            print("🔍 DRY RUN - No files will be modified")
            print()

        # Update all files
        for file_info in files:
            update_version_in_file(
                file_info["path"], file_info["pattern"], new_version, args.dry_run
            )

        if not args.dry_run:
            print(f"\n🎉 Version bumped to {new_version}")
            print("\nNext steps:")
            print("1. git add pyproject.toml src/bag/__init__.py")
            print(f"2. git commit -m '🔖 Bump version to {new_version}'")
            print("3. git push")
            print(f"4. Create GitHub release with tag 'v{new_version}'")

    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Sudarshan Engine Release Automation Script.

This script automates the release process for Sudarshan Engine, including:
- Version bumping
- Changelog generation
- Package building
- Release tagging
- Distribution uploads
"""

import argparse
import subprocess
import sys
import os
from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime
import re
import json

class ReleaseManager:
    """Manages the release process for Sudarshan Engine."""

    def __init__(self, repo_path: str = None):
        self.repo_path = Path(repo_path or ".")
        self.version_file = self.repo_path / "sudarshan" / "__version__.py"
        self.changelog_file = self.repo_path / "CHANGELOG.md"
        self.setup_file = self.repo_path / "setup.py"

    def get_current_version(self) -> str:
        """Get the current version from the version file."""
        if not self.version_file.exists():
            raise FileNotFoundError(f"Version file not found: {self.version_file}")

        with open(self.version_file, 'r') as f:
            content = f.read()

        # Extract version from __version__ = "x.x.x"
        match = re.search(r'__version__\s*=\s*["\']([^"\']+)["\']', content)
        if not match:
            raise ValueError("Could not find version in version file")

        return match.group(1)

    def bump_version(self, bump_type: str) -> str:
        """
        Bump the version according to semantic versioning.

        Args:
            bump_type: Type of bump ('major', 'minor', 'patch')

        Returns:
            New version string
        """
        current_version = self.get_current_version()
        major, minor, patch = map(int, current_version.split('.'))

        if bump_type == 'major':
            major += 1
            minor = 0
            patch = 0
        elif bump_type == 'minor':
            minor += 1
            patch = 0
        elif bump_type == 'patch':
            patch += 1
        else:
            raise ValueError(f"Invalid bump type: {bump_type}")

        new_version = f"{major}.{minor}.{patch}"
        self.update_version_files(new_version)
        return new_version

    def update_version_files(self, new_version: str) -> None:
        """Update version in all relevant files."""
        # Update __version__.py
        self._update_version_file(self.version_file, new_version)

        # Update setup.py if it exists
        if self.setup_file.exists():
            self._update_setup_file(new_version)

        print(f"✅ Updated version to {new_version} in version files")

    def _update_version_file(self, file_path: Path, new_version: str) -> None:
        """Update version in a Python file."""
        with open(file_path, 'r') as f:
            content = f.read()

        # Update __version__ = "x.x.x"
        content = re.sub(
            r'(__version__\s*=\s*["\'])([^"\']+)(["\'])',
            f'\\g<1>{new_version}\\g<3>',
            content
        )

        # Update __version_info__ = (x, x, x)
        major, minor, patch = map(int, new_version.split('.'))
        content = re.sub(
            r'(__version_info__\s*=\s*\()([^)]+)(\))',
            f'\\g<1>{major}, {minor}, {patch}\\g<3>',
            content
        )

        with open(file_path, 'w') as f:
            f.write(content)

    def _update_setup_file(self, new_version: str) -> None:
        """Update version in setup.py."""
        with open(self.setup_file, 'r') as f:
            content = f.read()

        content = re.sub(
            r'(version\s*=\s*["\'])([^"\']+)(["\'])',
            f'\\g<1>{new_version}\\g<3>',
            content
        )

        with open(self.setup_file, 'w') as f:
            f.write(content)

    def generate_changelog(self, new_version: str) -> None:
        """Generate changelog for the new version."""
        # Get git log since last tag
        try:
            result = subprocess.run(
                ['git', 'log', '--oneline', '--pretty=format:%s'],
                capture_output=True, text=True, check=True,
                cwd=self.repo_path
            )
            commits = result.stdout.strip().split('\n')
        except subprocess.CalledProcessError:
            commits = []

        # Categorize commits
        categories = {
            'feat': [],
            'fix': [],
            'docs': [],
            'style': [],
            'refactor': [],
            'test': [],
            'chore': []
        }

        for commit in commits:
            if ': ' in commit:
                prefix, message = commit.split(': ', 1)
                category = prefix.split('(')[0] if '(' in prefix else prefix
                if category in categories:
                    categories[category].append(message)

        # Generate changelog entry
        changelog_entry = f"## [{new_version}] - {datetime.now().strftime('%Y-%m-%d')}\n\n"

        if categories['feat']:
            changelog_entry += "### ✨ Features\n"
            for feat in categories['feat']:
                changelog_entry += f"- {feat}\n"
            changelog_entry += "\n"

        if categories['fix']:
            changelog_entry += "### 🐛 Fixes\n"
            for fix in categories['fix']:
                changelog_entry += f"- {fix}\n"
            changelog_entry += "\n"

        if categories['docs']:
            changelog_entry += "### 📚 Documentation\n"
            for doc in categories['docs']:
                changelog_entry += f"- {doc}\n"
            changelog_entry += "\n"

        # Read existing changelog
        if self.changelog_file.exists():
            with open(self.changelog_file, 'r') as f:
                existing_content = f.read()
        else:
            existing_content = "# Changelog\n\n"

        # Prepend new entry
        new_content = existing_content.replace(
            "# Changelog\n\n",
            f"# Changelog\n\n{changelog_entry}"
        )

        with open(self.changelog_file, 'w') as f:
            f.write(new_content)

        print(f"✅ Generated changelog for version {new_version}")

    def build_packages(self) -> None:
        """Build distribution packages."""
        print("📦 Building distribution packages...")

        # Build wheel and source distribution
        subprocess.run([
            sys.executable, '-m', 'pip', 'install', 'build'
        ], check=True, cwd=self.repo_path)

        subprocess.run([
            sys.executable, '-m', 'build'
        ], check=True, cwd=self.repo_path)

        print("✅ Built packages successfully")

    def create_git_tag(self, version: str) -> None:
        """Create and push git tag."""
        tag_name = f"v{version}"

        # Create annotated tag
        subprocess.run([
            'git', 'tag', '-a', tag_name, '-m', f"Release version {version}"
        ], check=True, cwd=self.repo_path)

        # Push tag
        subprocess.run([
            'git', 'push', 'origin', tag_name
        ], check=True, cwd=self.repo_path)

        print(f"✅ Created and pushed git tag {tag_name}")

    def upload_to_pypi(self, test: bool = False) -> None:
        """Upload packages to PyPI."""
        print(f"🚀 Uploading to {'Test ' if test else ''}PyPI...")

        # Install twine
        subprocess.run([
            sys.executable, '-m', 'pip', 'install', 'twine'
        ], check=True, cwd=self.repo_path)

        # Upload command
        cmd = [sys.executable, '-m', 'twine', 'upload', 'dist/*']

        if test:
            cmd.extend(['--repository', 'testpypi'])

        # Note: This would require API token setup
        print(f"⚠️  To upload, run: {' '.join(cmd)}")
        print("   Make sure TWINE_USERNAME and TWINE_PASSWORD are set")

    def run_tests(self) -> bool:
        """Run test suite before release."""
        print("🧪 Running test suite...")

        try:
            subprocess.run([
                sys.executable, '-m', 'pytest',
                '--cov=sudarshan',
                '--cov-report=term-missing',
                '-v'
            ], check=True, cwd=self.repo_path)

            print("✅ All tests passed")
            return True

        except subprocess.CalledProcessError:
            print("❌ Tests failed")
            return False

    def create_release_notes(self, version: str) -> None:
        """Create GitHub release notes."""
        release_notes_file = self.repo_path / f"RELEASE_NOTES_{version}.md"

        with open(release_notes_file, 'w') as f:
            f.write(f"# Sudarshan Engine v{version} Release Notes\n\n")
            f.write(f"Released on {datetime.now().strftime('%Y-%m-%d')}\n\n")

            # Read changelog for this version
            if self.changelog_file.exists():
                with open(self.changelog_file, 'r') as cf:
                    content = cf.read()
                    # Extract the first changelog entry
                    lines = content.split('\n')
                    in_version = False
                    for line in lines[2:]:  # Skip header
                        if line.startswith('## ['):
                            if in_version:
                                break
                            if f'[{version}]' in line:
                                in_version = True
                        elif in_version:
                            f.write(line + '\n')

            f.write("\n## Installation\n\n")
            f.write("```bash\n")
            f.write(f"pip install sudarshan-engine=={version}\n")
            f.write("```\n\n")

            f.write("## Verification\n\n")
            f.write("```bash\n")
            f.write("python -c \"import sudarshan; print(sudarshan.__version__)\"\n")
            f.write("```\n\n")

        print(f"✅ Created release notes: {release_notes_file}")

    def full_release_process(self, bump_type: str, upload: bool = False) -> None:
        """Run the complete release process."""
        print("🚀 Starting Sudarshan Engine release process...")

        # Step 1: Run tests
        if not self.run_tests():
            print("❌ Release aborted due to test failures")
            sys.exit(1)

        # Step 2: Bump version
        new_version = self.bump_version(bump_type)
        print(f"📈 Bumped version to {new_version}")

        # Step 3: Generate changelog
        self.generate_changelog(new_version)

        # Step 4: Build packages
        self.build_packages()

        # Step 5: Create release notes
        self.create_release_notes(new_version)

        # Step 6: Commit changes
        subprocess.run([
            'git', 'add', '.'
        ], check=True, cwd=self.repo_path)

        subprocess.run([
            'git', 'commit', '-m', f"Release version {new_version}"
        ], check=True, cwd=self.repo_path)

        # Step 7: Create git tag
        self.create_git_tag(new_version)

        # Step 8: Upload to PyPI (if requested)
        if upload:
            self.upload_to_pypi(test=True)  # Upload to test PyPI first
            print("⚠️  Review test upload before uploading to production PyPI")

        print("🎉 Release process completed successfully!")
        print(f"   Version: {new_version}")
        print(f"   Tag: v{new_version}")
        print("   Next steps:")
        print("   1. Review and test the release")
        print("   2. Upload to production PyPI if ready")
        print("   3. Create GitHub release with release notes")


def main():
    """Main entry point for release script."""
    parser = argparse.ArgumentParser(description="Sudarshan Engine Release Manager")
    parser.add_argument(
        'bump_type',
        choices=['major', 'minor', 'patch'],
        help="Type of version bump"
    )
    parser.add_argument(
        '--upload',
        action='store_true',
        help="Upload to PyPI after release"
    )
    parser.add_argument(
        '--repo-path',
        default='.',
        help="Path to repository root"
    )

    args = parser.parse_args()

    try:
        manager = ReleaseManager(args.repo_path)
        manager.full_release_process(args.bump_type, args.upload)

    except Exception as e:
        print(f"❌ Release failed: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
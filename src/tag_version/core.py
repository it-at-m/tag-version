"""
Core functionality for the tagger package.
"""

import re
import subprocess
from dataclasses import dataclass
from typing import Optional

from tag_version.constants import CORE_GIT_TAG_ERROR


@dataclass
class VersionInfo:
    """Class to hold version information"""

    tag: str
    version_string: str
    major: int
    minor: int
    patch: int


def get_git_tags() -> list[str]:
    """Get all git tags in the current repository"""
    try:
        result = subprocess.run(
            ["git", "tag"], check=True, capture_output=True, text=True
        )
        tags = result.stdout.strip().split("\n") if result.stdout else []
        return [tag for tag in tags if tag]  # Filter out empty tags
    except subprocess.CalledProcessError:
        print(CORE_GIT_TAG_ERROR)
        return []


def filter_tags_by_prefix(tags: list[str], prefix: str) -> list[str]:
    """Filter tags that start with the specified prefix"""
    return [tag for tag in tags if tag.startswith(prefix)]


def parse_version_tags(tags: list[str], prefix: str) -> list[VersionInfo]:
    """Parse version tags into structured version objects"""
    version_objects = []
    for tag in tags:
        version_string = tag.replace(prefix, "")

        # Use regex to validate semantic versioning format
        match = re.match(r"^(\d+)\.(\d+)\.(\d+)$", version_string)
        if match:
            major, minor, patch = map(int, match.groups())
            version_objects.append(
                VersionInfo(
                    tag=tag,
                    version_string=version_string,
                    major=major,
                    minor=minor,
                    patch=patch,
                )
            )

    return version_objects


def get_latest_version(versions: list[VersionInfo]) -> Optional[VersionInfo]:
    """Get the highest version from a list of versions"""
    if not versions:
        return None

    # Sort by major, minor, patch in descending order
    sorted_versions = sorted(
        versions, key=lambda v: (v.major, v.minor, v.patch), reverse=True
    )

    return sorted_versions[0]


def increment_version(version: VersionInfo, version_type: str) -> tuple[str, str]:
    """
    Increment the version according to semantic versioning

    Args:
        version: The current version info
        version_type: The type of version increment ('major', 'minor', or 'patch')

    Returns:
        Tuple of (new version string, new tag)
    """
    major = version.major
    minor = version.minor
    patch = version.patch

    if version_type == "major":
        major += 1
        minor = 0
        patch = 0
    elif version_type == "minor":
        minor += 1
        patch = 0
    elif version_type == "patch":
        patch += 1
    else:
        raise ValueError(f"Invalid version type: {version_type}")

    new_version = f"{major}.{minor}.{patch}"
    if version.tag.endswith(version.version_string):
        prefix = version.tag[: -len(version.version_string)]
    else:
        # Fallback, though this shouldn't happen with valid VersionInfo
        prefix = version.tag.replace(version.version_string, "", 1)
    new_tag = f"{prefix}{new_version}"

    return new_version, new_tag


def create_git_tag(tag: str, message: Optional[str] = None) -> bool:
    """Create a new git tag (lightweight or annotated)

    Args:
        tag: The tag name to create
        message: Optional message for annotated tag. If None, creates lightweight tag.

    Returns:
        True if tag creation was successful

    Raises:
        RuntimeError: If tag creation fails
    """
    try:
        if message:
            # Create annotated tag with message
            subprocess.run(
                ["git", "tag", "-a", tag, "-m", message],
                check=True,
                capture_output=True,
                text=True,
            )
        else:
            # Create lightweight tag
            subprocess.run(
                ["git", "tag", tag], check=True, capture_output=True, text=True
            )
        return True
    except subprocess.CalledProcessError as e:
        error_message = e.stderr if e.stderr else str(e)
        # Don't print here, let the caller handle the error display
        raise RuntimeError(
            f"Command '{e.cmd}' returned non-zero exit status {e.returncode}.\n{error_message}"
        )


def push_git_tag(tag: str) -> tuple[bool, str]:
    """Push git tag to remote repository"""
    try:
        result = subprocess.run(
            ["git", "push", "origin", tag], check=True, capture_output=True, text=True
        )
        return True, result.stdout
    except subprocess.CalledProcessError as e:
        return False, e.stderr

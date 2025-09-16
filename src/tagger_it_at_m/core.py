"""
Core functionality for the tagger package.
"""

import re
import subprocess
from dataclasses import dataclass
from typing import List, Optional, Tuple

from tagger_it_at_m.constants import CORE_GIT_TAG_ERROR


@dataclass
class VersionInfo:
    """Class to hold version information"""
    tag: str
    version_string: str
    major: int
    minor: int
    patch: int


def get_git_tags() -> List[str]:
    """Get all git tags in the current repository"""
    try:
        result = subprocess.run(
            ["git", "tag"],
            check=True,
            capture_output=True,
            text=True
        )
        tags = result.stdout.strip().split("\n") if result.stdout else []
        return [tag for tag in tags if tag]  # Filter out empty tags
    except subprocess.CalledProcessError:
        print(CORE_GIT_TAG_ERROR)
        return []


def filter_tags_by_prefix(tags: List[str], prefix: str) -> List[str]:
    """Filter tags that start with the specified prefix"""
    return [tag for tag in tags if tag.startswith(prefix)]


def parse_version_tags(tags: List[str], prefix: str) -> List[VersionInfo]:
    """Parse version tags into structured version objects"""
    version_objects = []
    for tag in tags:
        version_string = tag.replace(prefix, '')
        
        # Use regex to validate semantic versioning format
        match = re.match(r'^(\d+)\.(\d+)\.(\d+)$', version_string)
        if match:
            major, minor, patch = map(int, match.groups())
            version_objects.append(
                VersionInfo(
                    tag=tag,
                    version_string=version_string,
                    major=major,
                    minor=minor,
                    patch=patch
                )
            )
    
    return version_objects


def get_latest_version(versions: List[VersionInfo]) -> Optional[VersionInfo]:
    """Get the highest version from a list of versions"""
    if not versions:
        return None
    
    # Sort by major, minor, patch in descending order
    sorted_versions = sorted(
        versions,
        key=lambda v: (v.major, v.minor, v.patch),
        reverse=True
    )
    
    return sorted_versions[0]


def increment_version(
    version: VersionInfo, 
    version_type: str
) -> Tuple[str, str]:
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
    
    new_version = f"{major}.{minor}.{patch}"
    prefix = version.tag.replace(version.version_string, '')
    new_tag = f"{prefix}{new_version}"
    
    return new_version, new_tag


def create_git_tag(tag: str) -> bool:
    """Create a new git tag"""
    try:
        subprocess.run(
            ["git", "tag", tag],
            check=True,
            capture_output=True,
            text=True
        )
        return True
    except subprocess.CalledProcessError as e:
        error_message = e.stderr if e.stderr else str(e)
        # Don't print here, let the caller handle the error display
        raise RuntimeError(f"Command '{e.cmd}' returned non-zero exit status {e.returncode}.\n{error_message}")


def push_git_tag(tag: str) -> Tuple[bool, str]:
    """Push git tag to remote repository"""
    try:
        result = subprocess.run(
            ["git", "push", "origin", tag],
            check=True,
            capture_output=True,
            text=True
        )
        return True, result.stdout
    except subprocess.CalledProcessError as e:
        return False, e.stderr

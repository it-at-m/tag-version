"""
Integration tests for the tagger package.
"""

import os
import shutil
import subprocess
import tempfile
from unittest.mock import MagicMock, patch

import pytest
from tag_version.core import (
    VersionInfo,
    create_git_tag,
    filter_tags_by_prefix,
    get_git_tags,
    get_latest_version,
    increment_version,
    parse_version_tags,
    push_git_tag,
)


@pytest.fixture
def git_repo():
    """Create a temporary git repository for testing"""
    temp_dir = tempfile.mkdtemp()
    original_dir = os.getcwd()
    os.chdir(temp_dir)

    # Initialize git repo
    subprocess.run(["git", "init"], check=False, capture_output=True)
    subprocess.run(
        ["git", "config", "user.name", "Test User"], check=False, capture_output=True
    )
    subprocess.run(
        ["git", "config", "user.email", "test@example.com"],
        check=False,
        capture_output=True,
    )

    # Create and commit a dummy file
    with open(os.path.join(temp_dir, "README.md"), "w") as f:
        f.write("# Test Repository")
    subprocess.run(["git", "add", "README.md"], check=False, capture_output=True)
    subprocess.run(
        ["git", "commit", "-m", "Initial commit"], check=False, capture_output=True
    )

    yield temp_dir

    # Teardown
    os.chdir(original_dir)
    try:
        shutil.rmtree(temp_dir)
    except PermissionError as e:
        print(
            f"Warning: Could not fully clean up temp directory due to permissions: {e}"
        )
        # This is OK in Windows environments during tests


@patch("subprocess.run")
def test_full_version_workflow(mock_run):
    """Test the full version workflow"""
    # Setup mock to simulate git tag creation without actually creating tags
    # This prevents the test from modifying the actual git repository
    mock_run.return_value = MagicMock(stdout="", returncode=0)

    # 1. Test with no existing tags
    tags = get_git_tags()
    assert tags == []

    # 2. Filter by prefix (should be empty)
    prefix = "service-"
    filtered_tags = filter_tags_by_prefix(tags, prefix)
    assert filtered_tags == []

    # 3. Parse version tags (should be empty)
    version_objects = parse_version_tags(filtered_tags, prefix)
    assert version_objects == []

    # 4. Get latest version (should be None)
    latest_version = get_latest_version(version_objects)
    assert latest_version is None

    # 5. Initialize first version when none exists
    if latest_version is None:
        latest_version = VersionInfo(
            tag=f"{prefix}0.0.0", version_string="0.0.0", major=0, minor=0, patch=0
        )

    # 6. Increment version
    new_version, new_tag = increment_version(latest_version, "patch")
    assert new_version == "0.0.1"
    assert new_tag == "service-0.0.1"

    # 7. Create git tag (mocked)
    result = create_git_tag(new_tag)
    assert result is True
    mock_run.assert_called_with(
        ["git", "tag", "service-0.0.1"], check=True, capture_output=True, text=True
    )

    # 8. Push git tag (mocked)
    mock_run.reset_mock()
    mock_run.return_value = MagicMock(
        stdout="To origin\n * [new tag]         service-0.0.1 -> service-0.0.1",
        returncode=0,
    )
    success, output = push_git_tag(new_tag)
    assert success is True
    assert "service-0.0.1" in output
    mock_run.assert_called_with(
        ["git", "push", "origin", "service-0.0.1"],
        check=True,
        capture_output=True,
        text=True,
    )


def test_version_increment_sequence():
    """Test a sequence of version increments"""
    # Starting with version 1.2.3
    version = VersionInfo(
        tag="service-1.2.3", version_string="1.2.3", major=1, minor=2, patch=3
    )

    # Patch increment: 1.2.3 -> 1.2.4
    new_version, new_tag = increment_version(version, "patch")
    assert new_version == "1.2.4"
    assert new_tag == "service-1.2.4"

    # Minor increment: 1.2.3 -> 1.3.0
    new_version, new_tag = increment_version(version, "minor")
    assert new_version == "1.3.0"
    assert new_tag == "service-1.3.0"

    # Major increment: 1.2.3 -> 2.0.0
    new_version, new_tag = increment_version(version, "major")
    assert new_version == "2.0.0"
    assert new_tag == "service-2.0.0"

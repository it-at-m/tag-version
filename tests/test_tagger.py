"""
Tests for the tagger package.
"""

import subprocess
from unittest.mock import MagicMock, patch

import pytest
from tag_version.constants import CORE_GIT_TAG_ERROR
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


# Test core functionality of the tagger package
def test_filter_tags_by_prefix():
    """Test filtering tags by prefix"""
    tags = ["prefix-1.0.0", "other-2.0.0", "prefix-0.1.0"]
    filtered = filter_tags_by_prefix(tags, "prefix-")
    assert filtered == ["prefix-1.0.0", "prefix-0.1.0"]


def test_parse_version_tags():
    """Test parsing version tags"""
    tags = ["prefix-1.0.0", "prefix-0.1.0", "prefix-invalid"]
    parsed = parse_version_tags(tags, "prefix-")
    assert len(parsed) == 2
    assert parsed[0].major == 1
    assert parsed[0].minor == 0
    assert parsed[0].patch == 0
    assert parsed[1].major == 0
    assert parsed[1].minor == 1
    assert parsed[1].patch == 0


def test_get_latest_version():
    """Test getting the latest version"""
    versions = [
        VersionInfo("prefix-1.0.0", "1.0.0", 1, 0, 0),
        VersionInfo("prefix-0.1.0", "0.1.0", 0, 1, 0),
        VersionInfo("prefix-0.0.1", "0.0.1", 0, 0, 1),
        VersionInfo("prefix-1.2.0", "1.2.0", 1, 2, 0),
    ]
    latest = get_latest_version(versions)
    assert latest.version_string == "1.2.0"


def test_increment_version():
    """Test incrementing versions"""
    version = VersionInfo("prefix-1.0.0", "1.0.0", 1, 0, 0)

    # Test major increment
    new_version, new_tag = increment_version(version, "major")
    assert new_version == "2.0.0"
    assert new_tag == "prefix-2.0.0"

    # Test minor increment
    new_version, new_tag = increment_version(version, "minor")
    assert new_version == "1.1.0"
    assert new_tag == "prefix-1.1.0"

    # Test patch increment
    new_version, new_tag = increment_version(version, "patch")
    assert new_version == "1.0.1"
    assert new_tag == "prefix-1.0.1"


@patch("subprocess.run")
def test_get_git_tags(mock_run):
    """Test getting git tags"""
    # Mock subprocess.run to return a successful result with some tags
    mock_process = MagicMock()
    mock_process.stdout = "tag1\ntag2\ntag3\n"
    mock_process.returncode = 0
    mock_run.return_value = mock_process

    tags = get_git_tags()
    assert tags == ["tag1", "tag2", "tag3"]

    # Test with no tags
    mock_process.stdout = ""
    tags = get_git_tags()
    assert tags == []


@patch("subprocess.run")
def test_get_git_tags_error(mock_run):
    """Test error handling when getting git tags"""
    # Mock subprocess.run to raise CalledProcessError
    mock_run.side_effect = subprocess.CalledProcessError(
        returncode=1, cmd=["git", "tag"], stderr="fatal: not a git repository"
    )

    # Capture stdout to verify the error message is printed
    with patch("builtins.print") as mock_print:
        tags = get_git_tags()
        mock_print.assert_called_with(CORE_GIT_TAG_ERROR)
        assert tags == []


def test_get_latest_version_empty():
    """Test getting the latest version when the list is empty"""
    latest = get_latest_version([])
    assert latest is None


def test_parse_version_tags_with_invalid_tags():
    """Test parsing version tags with invalid format"""
    tags = ["prefix-1.0", "prefix-1.0.0.0", "prefix-v1.0.0", "prefix-1.a.0"]
    parsed = parse_version_tags(tags, "prefix-")
    # Only valid semver tags should be parsed
    assert len(parsed) == 0


@patch("subprocess.run")
def test_create_git_tag_success(mock_run):
    """Test successfully creating a git tag"""
    mock_process = MagicMock()
    mock_process.returncode = 0
    mock_run.return_value = mock_process

    result = create_git_tag("service-1.0.0")
    assert result is True
    mock_run.assert_called_once_with(
        ["git", "tag", "service-1.0.0"], check=True, capture_output=True, text=True
    )


@patch("subprocess.run")
def test_create_git_tag_error(mock_run):
    """Test error handling when creating a git tag"""
    # Mock subprocess.run to raise CalledProcessError
    error = subprocess.CalledProcessError(
        returncode=128,
        cmd=["git", "tag", "service-1.0.0"],
        stderr="fatal: tag 'service-1.0.0' already exists",
    )
    mock_run.side_effect = error

    with pytest.raises(RuntimeError) as excinfo:
        create_git_tag("service-1.0.0")

    assert "returned non-zero exit status" in str(excinfo.value)
    assert "fatal: tag 'service-1.0.0' already exists" in str(excinfo.value)


@patch("subprocess.run")
def test_push_git_tag_success(mock_run):
    """Test successfully pushing a git tag"""
    mock_process = MagicMock()
    mock_process.returncode = 0
    mock_process.stdout = "To github.com:user/repo.git\n * [new tag]         service-1.0.0 -> service-1.0.0"
    mock_run.return_value = mock_process

    success, output = push_git_tag("service-1.0.0")
    assert success is True
    assert output == mock_process.stdout
    mock_run.assert_called_once_with(
        ["git", "push", "origin", "service-1.0.0"],
        check=True,
        capture_output=True,
        text=True,
    )


@patch("subprocess.run")
def test_push_git_tag_error(mock_run):
    """Test error handling when pushing a git tag"""
    # Mock subprocess.run to raise CalledProcessError
    error = subprocess.CalledProcessError(
        returncode=1,
        cmd=["git", "push", "origin", "service-1.0.0"],
        stderr="fatal: could not read from remote repository",
    )
    mock_run.side_effect = error

    success, error_msg = push_git_tag("service-1.0.0")
    assert success is False
    assert error_msg == "fatal: could not read from remote repository"

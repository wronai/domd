"""Tests for path utility functions."""

import os
import sys
from pathlib import Path
from unittest.mock import patch

import pytest

from domd.utils.path_utils import safe_path_display, to_relative_path


def test_safe_path_display_home_expansion(tmp_path, monkeypatch):
    """Test that user home directory is properly expanded in paths."""
    # Set up test home directory
    home = tmp_path / "home" / "user"
    home.mkdir(parents=True)
    monkeypatch.setenv("HOME", str(home))

    # Test home directory expansion
    test_path = home / "projects" / "test"
    result = safe_path_display(str(test_path))
    assert result == f"~/projects/test"

    # Test with non-home path
    other_path = tmp_path / "other" / "path"
    result = safe_path_display(str(other_path))
    assert result == str(other_path)


def test_safe_path_display_relative_path():
    """Test that relative paths are returned as-is."""
    rel_path = "relative/path"
    assert safe_path_display(rel_path) == rel_path


def test_safe_path_display_none():
    """Test that None is handled gracefully."""
    assert safe_path_display(None) == ""


def test_to_relative_path_relative():
    """Test that relative paths are returned as-is."""
    rel_path = "relative/path"
    assert to_relative_path(rel_path) == rel_path


def test_to_relative_path_absolute(tmp_path):
    """Test that absolute paths are made relative to base path."""
    base = tmp_path / "base"
    target = tmp_path / "base" / "sub" / "file.txt"

    # Create the target file
    target.parent.mkdir(parents=True, exist_ok=True)
    target.touch()

    result = to_relative_path(str(target), str(base))
    assert result == "sub/file.txt"


def test_to_relative_path_outside_base(tmp_path):
    """Test that paths outside base path are returned as absolute."""
    base = tmp_path / "base"
    outside = tmp_path / "outside" / "file.txt"

    # Create the outside file
    outside.parent.mkdir(parents=True, exist_ok=True)
    outside.touch()

    result = to_relative_path(str(outside), str(base))
    assert result == str(outside)


def test_to_relative_path_none():
    """Test that None is handled gracefully."""
    assert to_relative_path(None) == ""


def test_to_relative_path_non_existent():
    """Test that non-existent paths are handled gracefully."""
    non_existent = "/non/existent/path"
    assert to_relative_path(non_existent) == non_existent


def test_to_relative_path_same_file(tmp_path):
    """Test when target is the same as base path."""
    file_path = tmp_path / "file.txt"
    file_path.touch()

    result = to_relative_path(str(file_path), str(file_path))
    assert result == "."


def test_to_relative_path_relative_to_cwd(tmp_path, monkeypatch):
    """Test making path relative to current working directory."""
    cwd = tmp_path / "current" / "directory"
    cwd.mkdir(parents=True, exist_ok=True)
    monkeypatch.chdir(cwd)

    target = cwd / "subdir" / "file.txt"
    target.parent.mkdir(exist_ok=True)
    target.touch()

    # Test with default base (should use cwd)
    result = to_relative_path(str(target))
    assert result == "subdir/file.txt"

    # Test with explicit base
    result = to_relative_path(str(target), base=cwd)
    assert result == "subdir/file.txt"

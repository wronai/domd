"""
Unit tests for base parser functionality.
"""

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from domd.core.parsers.base import BaseParser


class ConcreteParser(BaseParser):
    """Concrete implementation of BaseParser for testing."""

    @property
    def supported_file_patterns(self):
        return ["*.test"]

    def parse(self):
        return []


class TestBaseParser:
    """Test cases for BaseParser class."""

    def test_base_parser_initialization(self):
        """Test BaseParser initialization."""
        # Test with file path
        file_path = Path("/test/path")
        parser = ConcreteParser(file_path=file_path)
        assert parser.file_path == file_path.resolve()
        assert parser.project_root == file_path.parent

        # Test with project root
        project_root = Path("/project/root")
        parser = ConcreteParser(file_path=file_path, project_root=project_root)
        assert parser.project_root == project_root.resolve()

        # Test with no file path
        parser = ConcreteParser()
        assert parser.file_path is None
        assert parser.project_root == Path.cwd()

    def test_base_parser_abstract_methods(self):
        """Test that BaseParser abstract methods are properly defined."""
        # Create a test parser
        parser = ConcreteParser()

        # Test can_parse implementation
        assert parser.can_parse(Path("test.test")) is True
        assert parser.can_parse(Path("invalid.txt")) is False

        # Test parse implementation
        assert parser.parse() == []

    def test_supported_file_patterns_property(self):
        """Test that supported_file_patterns property works as expected."""
        # Create a test parser
        parser = ConcreteParser()

        # Test that the property is implemented and returns expected value
        assert parser.supported_file_patterns == ["*.test"]

        # Test that parse is implemented and returns expected value
        assert parser.parse() == []

        # Should raise TypeError if abstract methods are not implemented
        with pytest.raises(TypeError):

            class InvalidParser(BaseParser):
                pass

            InvalidParser()

    def test_can_parse_method(self):
        """Test the can_parse method."""
        # Test with a matching pattern
        assert ConcreteParser.can_parse(Path("test.test")) is True

        # Test with a non-matching pattern
        assert ConcreteParser.can_parse(Path("invalid.txt")) is False

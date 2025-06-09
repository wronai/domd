"""
Unit tests for base parser functionality.
"""

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from domd.core.parsers.base import BaseParser


class TestBaseParser:
    """Test cases for BaseParser class."""

    def test_base_parser_initialization(self):
        """Test BaseParser initialization."""
        # Test with file path
        file_path = Path("/test/path")
        parser = BaseParser(file_path=file_path)
        assert parser.file_path == file_path.resolve()
        assert parser.project_root == file_path.parent

        # Test with project root
        project_root = Path("/project/root")
        parser = BaseParser(file_path=file_path, project_root=project_root)
        assert parser.project_root == project_root.resolve()

        # Test with no file path
        parser = BaseParser()
        assert parser.file_path is None
        assert parser.project_root == Path.cwd()

    def test_base_parser_abstract_methods(self):
        """Test that BaseParser abstract methods raise NotImplementedError."""

        class TestParser(BaseParser):
            @property
            def supported_file_patterns(self):
                return ["*.test"]

        parser = TestParser()

        # can_parse is implemented in base class
        assert parser.can_parse(Path("test.test")) is True
        assert parser.can_parse(Path("invalid.txt")) is False

        # parse is abstract
        with pytest.raises(NotImplementedError):
            parser.parse()

    def test_supported_file_patterns_property(self):
        """Test that supported_file_patterns is an abstract property."""

        class TestParser(BaseParser):
            @property
            def supported_file_patterns(self):
                return ["*.test"]

        parser = TestParser()
        assert parser.supported_file_patterns == ["*.test"]

        # Should raise TypeError if not implemented
        class InvalidParser(BaseParser):
            pass

        with pytest.raises(TypeError):
            InvalidParser()

"""Registry for managing command parsers."""

import importlib
import inspect
import logging
import pkgutil
from pathlib import Path
from typing import Dict, List, Optional, Set, Type, TypeVar, Union

from .base_parser import BaseParser

logger = logging.getLogger(__name__)

T = TypeVar("T", bound=BaseParser)


class ParserRegistry:
    """Registry for managing and discovering command parsers."""

    def __init__(self):
        """Initialize the parser registry."""
        self._parsers: Dict[str, Type[BaseParser]] = {}
        self._discovered = False

    def register(self, parser_class: Type[T]) -> Type[T]:
        """Register a parser class.

        Args:
            parser_class: Parser class to register

        Returns:
            The registered parser class (for use as a decorator)
        """
        if not inspect.isclass(parser_class) or not issubclass(
            parser_class, BaseParser
        ):
            raise ValueError(
                f"Parser must be a subclass of BaseParser, got {parser_class}"
            )

        parser_name = parser_class.__name__
        self._parsers[parser_name] = parser_class
        logger.debug(f"Registered parser: {parser_name}")
        return parser_class

    def get_parser(self, name: str) -> Optional[Type[BaseParser]]:
        """Get a parser class by name.

        Args:
            name: Name of the parser class

        Returns:
            The parser class, or None if not found
        """
        return self._parsers.get(name)

    def get_parsers(self) -> List[Type[BaseParser]]:
        """Get all registered parser classes.

        Returns:
            List of parser classes
        """
        return list(self._parsers.values())

    def create_parser_instances(self) -> List[BaseParser]:
        """Create instances of all registered parsers.

        Returns:
            List of parser instances
        """
        return [parser() for parser in self._parsers.values()]

    def discover_parsers(self, package_path: Optional[Union[str, Path]] = None) -> None:
        """Discover and register parser classes in the given package.

        Args:
            package_path: Path to the package containing parser modules.
                         If None, uses the default parsers directory.
        """
        if self._discovered:
            return

        if package_path is None:
            # Default to the parsers directory in the same package
            package_path = Path(__file__).parent / "parsers"
            package = f"{__package__}.parsers"
        else:
            package_path = Path(package_path)
            package = package_path.name

        if not package_path.exists():
            logger.warning(f"Parser directory not found: {package_path}")
            return

        logger.debug(f"Discovering parsers in {package_path}")

        # Import all modules in the parsers directory
        for finder, name, _ in pkgutil.iter_modules(
            [str(package_path)], prefix=f"{package}."
        ):
            try:
                # Skip __pycache__ and other non-module directories
                if name.endswith("__pycache__"):
                    continue

                module = importlib.import_module(name)
                self._register_parsers_from_module(module)
            except ImportError as e:
                logger.error(f"Failed to import parser module {name}: {e}")

        self._discovered = True

    def _register_parsers_from_module(self, module) -> None:
        """Register all parser classes found in a module.

        Args:
            module: Python module to search for parser classes
        """
        for name, obj in inspect.getmembers(module):
            if (
                inspect.isclass(obj)
                and issubclass(obj, BaseParser)
                and obj is not BaseParser
            ):
                self.register(obj)
                logger.debug(f"Discovered parser: {obj.__name__}")

    def get_parser_for_file(self, file_path: Union[str, Path]) -> Optional[BaseParser]:
        """Get an appropriate parser for the given file.

        Args:
            file_path: Path to the file to find a parser for

        Returns:
            Parser instance that can handle the file, or None if none found
        """
        file_path = Path(file_path)

        # Try to find a parser that explicitly supports this file
        for parser_class in self._parsers.values():
            parser = parser_class()
            if hasattr(parser, "can_parse") and parser.can_parse(file_path):
                return parser

        # Fall back to checking file extensions
        for parser_class in self._parsers.values():
            parser = parser_class()
            if hasattr(parser, "get_supported_files"):
                supported_files = parser.get_supported_files()
                if supported_files and any(
                    file_path.match(pat) for pat in supported_files
                ):
                    return parser

        return None

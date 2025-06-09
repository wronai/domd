"""Parser registry for managing different configuration file parsers."""

import importlib
import importlib.util
import inspect
import logging
import pkgutil
from pathlib import Path
from typing import Any, Dict, Generic, List, Optional, Type, TypeVar

from domd.core.parsing.base import BaseParser

logger = logging.getLogger(__name__)

# Type variable for parser classes
P = TypeVar("P", bound=BaseParser)


class ParserRegistry(Generic[P]):
    """Registry for managing parser classes and instances."""

    def __init__(self, base_parser_class: Type[P] = BaseParser):
        """Initialize the parser registry.

        Args:
            base_parser_class: Base class that all parsers must inherit from
        """
        self.base_parser_class = base_parser_class
        self._parsers: Dict[str, Type[P]] = {}
        self._initialized = False

    def register(self, parser_class: Type[P]) -> Type[P]:
        """Register a parser class.

        Args:
            parser_class: Parser class to register

        Returns:
            The registered parser class

        Raises:
            TypeError: If parser_class is not a subclass of base_parser_class
        """
        if not (
            inspect.isclass(parser_class)
            and issubclass(parser_class, self.base_parser_class)
        ):
            raise TypeError(
                f"Parser must be a subclass of {self.base_parser_class.__name__}"
            )

        self._parsers[parser_class.__name__] = parser_class
        return parser_class

    def discover_parsers(self, package_path: str) -> None:
        """Discover and register parsers from a package.

        Args:
            package_path: Dotted path to the package containing parsers
        """
        try:
            package = importlib.import_module(package_path)

            # Get all modules in the package
            for _, modname, is_pkg in pkgutil.iter_modules(
                package.__path__, package.__name__ + "."  # type: ignore
            ):
                if is_pkg or modname.startswith("_"):
                    continue

                try:
                    # Import the module
                    module = importlib.import_module(modname, package.__name__)

                    # Find all parser classes in the module
                    for name, obj in inspect.getmembers(module, inspect.isclass):
                        if (
                            issubclass(obj, self.base_parser_class)
                            and obj != self.base_parser_class
                            and obj.__module__ == module.__name__
                        ):
                            self.register(obj)
                            logger.debug("Discovered parser: %s", obj.__name__)

                except Exception as e:
                    logger.warning("Failed to load parser from %s: %s", modname, e)

        except ImportError as e:
            logger.warning("Failed to import parser package %s: %s", package_path, e)

    def get_parser_class(self, name: str) -> Optional[Type[P]]:
        """Get a parser class by name.

        Args:
            name: Name of the parser class

        Returns:
            Parser class or None if not found
        """
        return self._parsers.get(name)

    def get_parser_for_file(self, file_path: Path, **kwargs: Any) -> Optional[P]:
        """Get an appropriate parser for the given file.

        Args:
            file_path: Path to the file to parse
            **kwargs: Additional arguments to pass to the parser constructor

        Returns:
            Parser instance or None if no suitable parser found
        """
        for parser_class in self._parsers.values():
            try:
                # Create a temporary instance to check if it can parse the file
                parser = parser_class(**kwargs)
                if parser.can_parse(file_path):
                    return parser
            except Exception as e:
                logger.debug(
                    "Error checking if parser %s can parse %s: %s",
                    parser_class.__name__,
                    file_path,
                    e,
                )

        return None

    def get_all_parsers(self, **kwargs: Any) -> List[P]:
        """Get instances of all registered parsers.

        Args:
            **kwargs: Arguments to pass to parser constructors

        Returns:
            List of parser instances
        """
        return [parser_class(**kwargs) for parser_class in self._parsers.values()]

    def get_parser_names(self) -> List[str]:
        """Get names of all registered parsers.

        Returns:
            List of parser names
        """
        return list(self._parsers.keys())

    def clear(self) -> None:
        """Clear all registered parsers."""
        self._parsers.clear()


# Global registry instance
global_registry: ParserRegistry[BaseParser] = ParserRegistry()


def get_global_registry() -> ParserRegistry[BaseParser]:
    """Get the global parser registry.

    Returns:
        Global ParserRegistry instance
    """
    return global_registry


def register_parser(parser_class: Type[P]) -> Type[P]:
    """Register a parser class with the global registry.

    Args:
        parser_class: Parser class to register

    Returns:
        The registered parser class
    """
    return global_registry.register(parser_class)

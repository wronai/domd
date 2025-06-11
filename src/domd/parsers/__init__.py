"""Parsers package for backward compatibility with legacy code.

This module provides backward compatibility with the legacy parser system.
It imports parsers from the new modular structure and exposes them through
the legacy interface.
"""

import importlib
import logging
import sys
from typing import List, Type

from domd.core.parsing.base import BaseParser

logger = logging.getLogger(__name__)


# Enable debug logging for parser discovery
logging.basicConfig(level=logging.DEBUG, stream=sys.stderr)

# List of parser modules to import
PARSER_MODULES = [
    "domd.parsers.ansible",  # Ansible-related parsers
    "domd.parsers.build_systems",
    "domd.parsers.ci_cd",
    "domd.parsers.docker",
    "domd.parsers.javascript",  # This now includes package.json parser
    "domd.parsers.python",
    "domd.parsers.markdown_parser",  # Markdown file parser
]

logger.debug(f"Parser modules to load: {PARSER_MODULES}")


def get_all_parsers() -> List[Type[BaseParser]]:
    """Get all available parsers from the legacy parser modules.

    This function is used as a fallback when the new parser registry
    doesn't contain any parsers.

    Returns:
        List of parser classes
    """
    parsers = []
    logger.debug("Starting parser discovery...")

    for module_name in PARSER_MODULES:
        try:
            logger.debug(f"Attempting to import module: {module_name}")
            module = importlib.import_module(module_name)
            logger.debug(f"Successfully imported module: {module_name}")

            # Look for a get_parsers function in the module
            if hasattr(module, "get_parsers"):
                logger.debug(f"Found get_parsers() in {module_name}")
                module_parsers = module.get_parsers()
                logger.debug(
                    f"Module {module_name} returned {len(module_parsers)} parsers"
                )
                for p in module_parsers:
                    logger.debug(f"  - {p.__name__}")
                parsers.extend(module_parsers)
            else:
                logger.warning(f"Module {module_name} has no get_parsers function")
                logger.debug(f"Module {module_name} contents: {dir(module)}")

        except ImportError as e:
            logger.error(
                f"Failed to import parser module {module_name}: {e}", exc_info=True
            )
        except Exception as e:
            logger.error(
                f"Unexpected error processing module {module_name}: {e}", exc_info=True
            )

    logger.debug(f"Loaded {len(parsers)} legacy parsers in total")
    return parsers

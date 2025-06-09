"""Build system parsers for backward compatibility.

Includes parsers for Make, CMake, Gradle, Maven, etc.
"""

import logging
from typing import List, Type

from domd.core.parsing.base import BaseParser

logger = logging.getLogger(__name__)


def get_parsers() -> List[Type[BaseParser]]:
    """Get all build system parsers.

    Returns:
        List of parser classes
    """
    parsers = []

    # Try to import MakefileParser
    try:
        from domd.core.parsers.makefile import MakefileParser

        parsers.append(MakefileParser)
    except ImportError as e:
        logger.debug(f"Failed to import MakefileParser: {e}")

    # Add more parsers as they become available
    # For now, return what we have
    return parsers

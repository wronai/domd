"""JavaScript/Node.js related parsers."""

import logging
from typing import List, Type

from domd.core.parsing.base import BaseParser

logger = logging.getLogger(__name__)


def get_parsers() -> List[Type[BaseParser]]:
    """Get all JavaScript/Node.js related parsers.

    Returns:
        List of parser classes
    """
    parsers = []

    # Import and add PackageJsonParser
    try:
        from domd.core.parsers.package_json import PackageJsonParser

        parsers.append(PackageJsonParser)
        logger.debug("Successfully imported PackageJsonParser")
    except ImportError as e:
        logger.warning(f"Failed to import PackageJsonParser: {e}")

    return parsers

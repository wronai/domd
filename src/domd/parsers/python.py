"""Python project configuration file parsers."""

import logging
from typing import List, Type

from domd.core.parsers.base import BaseParser
from domd.core.parsers.pyproject_toml import PyProjectTomlParser
from domd.core.parsers.tox_ini import ToxIniParser

logger = logging.getLogger(__name__)


def get_parsers() -> List[Type[BaseParser]]:
    """Get all Python-related parsers.

    Returns:
        List of Python parser classes
    """
    parsers = [
        PyProjectTomlParser,
        ToxIniParser,
    ]

    logger.debug(f"Loaded {len(parsers)} Python parsers")
    return parsers

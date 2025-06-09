"""CI/CD workflow parsers for backward compatibility.

Includes parsers for GitHub Actions, GitLab CI, Jenkins, etc.
"""

import logging
from typing import List, Type

from domd.core.parsing.base import BaseParser

logger = logging.getLogger(__name__)


def get_parsers() -> List[Type[BaseParser]]:
    """Get all CI/CD workflow parsers.

    Returns:
        List of parser classes
    """
    # Currently no CI/CD parsers are implemented in core.parsers
    # This is a placeholder for future implementation
    return []

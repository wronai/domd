"""Docker-related parsers."""

import logging
from typing import List, Type

from domd.core.parsing.base import BaseParser
from domd.core.parsing.parser_registry import register_parser

from .docker_compose import DockerComposeParser
from .dockerfile import DockerfileParser

logger = logging.getLogger(__name__)

# Register the Docker parsers with the global registry
DOCKER_PARSERS = [DockerfileParser, DockerComposeParser]
for parser in DOCKER_PARSERS:
    register_parser(parser)


def get_parsers() -> List[Type[BaseParser]]:
    """Get all Docker-related parsers.

    Returns:
        List of Docker-related parser classes
    """
    logger.debug(f"Loaded {len(DOCKER_PARSERS)} Docker parsers")
    return DOCKER_PARSERS

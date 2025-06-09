"""Ansible-related parsers."""

import logging
from typing import List, Type

from domd.core.parsers.ansible_galaxy import AnsibleGalaxyParser
from domd.core.parsers.ansible_inventory import AnsibleInventoryParser
from domd.core.parsers.ansible_playbook import AnsiblePlaybookParser
from domd.core.parsers.ansible_role import AnsibleRoleParser
from domd.core.parsers.ansible_vault import AnsibleVaultParser
from domd.core.parsing.base import BaseParser

logger = logging.getLogger(__name__)


def get_parsers() -> List[Type[BaseParser]]:
    """Get all Ansible-related parsers.

    Returns:
        List of Ansible parser classes
    """
    parsers = [
        AnsibleGalaxyParser,
        AnsibleInventoryParser,
        AnsiblePlaybookParser,
        AnsibleRoleParser,
        AnsibleVaultParser,
    ]

    logger.debug(f"Loaded {len(parsers)} Ansible parsers")
    return parsers

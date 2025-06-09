"""Parsers for different configuration file formats."""

from .ansible_galaxy import AnsibleGalaxyParser
from .ansible_inventory import AnsibleInventoryParser
from .ansible_playbook import AnsiblePlaybookParser
from .ansible_role import AnsibleRoleParser
from .ansible_vault import AnsibleVaultParser
from .base import BaseParser
from .cargo_toml import CargoTomlParser
from .composer_json import ComposerJsonParser

# Docker parsers are now in the domd.parsers.docker module
from .go_mod import GoModParser
from .makefile import MakefileParser
from .package_json import PackageJsonParser
from .pyproject_toml import PyProjectTomlParser
from .tox_ini import ToxIniParser

__all__ = [
    "AnsibleGalaxyParser",
    "AnsibleInventoryParser",
    "AnsiblePlaybookParser",
    "AnsibleRoleParser",
    "AnsibleVaultParser",
    "BaseParser",
    "CargoTomlParser",
    "ComposerJsonParser",
    # Docker-related parsers are now in domd.parsers.docker
    "GoModParser",
    "MakefileParser",
    "PackageJsonParser",
    "PyProjectTomlParser",
    "ToxIniParser",
]

"""Parser for tox.ini files."""

import configparser
from typing import List, Set

from ..commands import Command
from .base import BaseParser


class ToxIniParser(BaseParser):
    """Parser for tox.ini files."""

    @property
    def supported_file_patterns(self) -> List[str]:
        return ["tox.ini"]

    def _get_tox_environments(self, config: configparser.ConfigParser) -> Set[str]:
        """Extract environment names from tox.ini.

        Args:
            config: Parsed config from tox.ini

        Returns:
            Set of environment names.
        """
        envs = set()

        # Get environments from envlist
        if "tox" in config and "envlist" in config["tox"]:
            envlist = config["tox"]["envlist"].strip()
            if envlist:
                # Handle different formats: comma-separated, newline-separated, multi-line
                for line in envlist.split("\n"):
                    line = line.strip()
                    if not line or line.startswith("#"):
                        continue
                    # Handle line continuations and clean up
                    line = line.rstrip("\\").strip()
                    if line:
                        envs.update(
                            env.strip() for env in line.split(",") if env.strip()
                        )

        # Also check for testenv sections
        for section in config.sections():
            if section.startswith("testenv:"):
                env_name = section.split(":", 1)[1].strip()
                if env_name:
                    envs.add(env_name)

        return envs

    def parse(self) -> List[Command]:
        """Parse a tox.ini file and return a list of commands.

        Returns:
            List of Command objects.
        """
        commands = []
        if not self.file_path:
            return commands

        config = configparser.ConfigParser()

        try:
            # Read the config file
            with open(self.file_path, "r", encoding="utf-8") as f:
                config.read_file(f)

            # Get all environments
            envs = self._get_tox_environments(config)

            # Add command to run all environments
            if envs:
                commands.append(
                    Command(
                        command="tox",
                        type="tox_all",
                        description="Tox: Run all test environments",
                        source=str(self.file_path),
                    )
                )

            # Add commands for each environment
            for env in sorted(envs):
                commands.append(
                    Command(
                        command=f"tox -e {env}",
                        type="tox_environment",
                        description=f"Tox: Run {env} environment",
                        source=str(self.file_path)
                        if hasattr(self, "file_path")
                        else "tox.ini",
                    )
                )

            # Add common tox commands
            common_commands = [
                ("tox -r", "tox_recreate", "Tox: Recreate environments"),
                ("tox -l", "tox_list", "Tox: List available environments"),
                ("tox -v", "tox_verbose", "Tox: Run with verbose output"),
            ]

            for cmd, cmd_type, description in common_commands:
                commands.append(
                    Command(
                        command=cmd,
                        type=cmd_type,
                        description=description,
                        source=str(self.file_path),
                    )
                )

        except (configparser.Error, OSError):
            # Log error or handle as needed
            pass

        return commands

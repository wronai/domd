"""
Tests for Ansible-related functionality in Project Command Detector.
"""

import os
import shutil
from pathlib import Path
from unittest.mock import patch

import pytest

from domd.core.detector import ProjectCommandDetector


class TestAnsibleDetection:
    """Test cases for Ansible playbook and role detection."""

    @pytest.fixture
    def sample_playbook(self, temp_project):
        """Create a sample Ansible playbook for testing."""
        playbook_dir = temp_project / "ansible"
        playbook_dir.mkdir()

        # Create main playbook
        playbook = playbook_dir / "site.yml"
        playbook.write_text(
            """---
- name: Test playbook
  hosts: localhost
  tasks:
    - name: Test task
      debug:
        msg: "Hello from Ansible"
"""
        )

        # Create inventory file
        inventory = temp_project / "inventory.ini"
        inventory.write_text(
            """[local]
localhost ansible_connection=local
"""
        )

        # Create ansible.cfg
        cfg = temp_project / "ansible.cfg"
        cfg.write_text(
            """[defaults]
inventory = inventory.ini
host_key_checking = False
"""
        )

        return temp_project

    @pytest.fixture
    def ansible_role_structure(self, temp_project):
        """Create a sample Ansible role structure."""
        role_path = temp_project / "roles" / "example_role"
        (role_path / "tasks").mkdir(parents=True)
        (role_path / "handlers").mkdir()
        (role_path / "templates").mkdir()
        (role_path / "files").mkdir()
        (role_path / "vars").mkdir()
        (role_path / "defaults").mkdir()
        (role_path / "meta").mkdir()

        # Create main task file
        (role_path / "tasks" / "main.yml").write_text(
            """---
- name: Example task
  debug:
    msg: "This is an example role"
"""
        )

        # Create meta/main.yml
        (role_path / "meta" / "main.yml").write_text(
            """---
galaxy_info:
  author: Test Author
  description: Test role
  license: MIT
  min_ansible_version: 2.9
  platforms:
    - name: Ubuntu
      versions:
        - bionic
        - focal
  galaxy_tags:
    - testing
"""
        )

        return temp_project

    def test_detect_ansible_playbook(self, sample_playbook):
        """Test detection of Ansible playbook files."""
        detector = ProjectCommandDetector(str(sample_playbook))
        commands = detector.scan_project()

        # Should detect the playbook and related files
        playbook_path = str(sample_playbook / "ansible" / "site.yml")
        inventory_path = str(sample_playbook / "inventory.ini")
        cfg_path = str(sample_playbook / "ansible.cfg")

        playbook_commands = [
            cmd
            for cmd in commands
            if cmd.get("file") in [playbook_path, inventory_path, cfg_path]
        ]

        assert len(playbook_commands) >= 3  # At least the playbook, inventory and cfg

        playbook_cmd = next(
            (cmd for cmd in playbook_commands if cmd.get("file") == playbook_path), None
        )

        assert playbook_cmd is not None
        assert playbook_cmd["command"] == "ansible-playbook ansible/site.yml"
        assert playbook_cmd["type"] == "ansible_playbook"

    def test_detect_ansible_role(self, ansible_role_structure):
        """Test detection of Ansible role structure."""
        detector = ProjectCommandDetector(str(ansible_role_structure))
        commands = detector.scan_project()

        # Should detect role-related files
        role_files = [
            cmd for cmd in commands if "roles/example_role/" in cmd.get("file", "")
        ]

        # At least the main task file and meta/main.yml should be detected
        assert len(role_files) >= 2

        # Check if main task file is detected
        main_task = next(
            (
                cmd
                for cmd in role_files
                if cmd.get("file").endswith("roles/example_role/tasks/main.yml")
            ),
            None,
        )
        assert main_task is not None
        assert main_task["type"] == "ansible_task"

    def test_ansible_galaxy_commands(self, temp_project):
        """Test detection of Ansible Galaxy commands."""
        # Create a requirements.yml file
        requirements = temp_project / "requirements.yml"
        requirements.write_text(
            """---
- src: geerlingguy.docker
  version: "4.1.1"
- src: geerlingguy.pip
  version: "2.0.0"
"""
        )

        detector = ProjectCommandDetector(str(temp_project))
        commands = detector.scan_project()

        # Should detect the requirements file and suggest galaxy install
        req_cmds = [cmd for cmd in commands if cmd.get("file") == str(requirements)]

        assert len(req_cmds) > 0
        assert any(
            "ansible-galaxy install -r requirements.yml" in cmd.get("command", "")
            for cmd in req_cmds
        )

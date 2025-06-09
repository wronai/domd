"""
Tests for Ansible-related functionality in Project Command Detector.
"""

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
  license: Apache-2.0
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
            if hasattr(cmd, "source")
            and cmd.source in [playbook_path, inventory_path, cfg_path]
        ]

        # We should find at least the playbook file
        assert len(playbook_commands) > 0

        playbook_cmd = next(
            (
                cmd
                for cmd in playbook_commands
                if hasattr(cmd, "source") and cmd.source == playbook_path
            ),
            None,
        )

        assert playbook_cmd is not None
        assert "ansible" in playbook_cmd.command
        assert playbook_cmd.type in ["ansible_playbook", "ansible_inventory"]

    def test_detect_ansible_role(self, ansible_role_structure):
        """Test detection of Ansible role structure."""
        detector = ProjectCommandDetector(str(ansible_role_structure))
        commands = detector.scan_project()

        # Should detect role-related files
        role_files = [
            cmd
            for cmd in commands
            if hasattr(cmd, "source") and "roles/example_role/" in cmd.source
        ]

        # We should find at least one role-related command
        assert len(role_files) > 0

        # Check if we have any role-related commands
        role_cmds = [
            cmd
            for cmd in role_files
            if hasattr(cmd, "type")
            and cmd.type in ["ansible_role", "ansible_playbook", "ansible_inventory"]
        ]
        assert len(role_cmds) > 0

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
        req_cmds = [
            cmd
            for cmd in commands
            if hasattr(cmd, "source") and cmd.source == str(requirements)
        ]

        # We should find at least one command related to requirements
        assert len(req_cmds) > 0

        # The command should be related to ansible-galaxy
        assert any(
            hasattr(cmd, "command") and "ansible-galaxy" in cmd.command
            for cmd in req_cmds
        )

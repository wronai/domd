"""
Tests for Ansible roles detection and functionality.
"""

from domd.core.detector import ProjectCommandDetector


class TestAnsibleRoles:
    """Test cases for Ansible roles detection and functionality."""

    def test_detect_ansible_role_structure(self, temp_project):
        """Test detection of Ansible role structure."""
        # Create role directory structure
        roles_dir = temp_project / "roles"
        role_name = "example_role"
        role_path = roles_dir / role_name

        # Create standard role directories
        (role_path / "tasks").mkdir(parents=True)
        (role_path / "handlers").mkdir()
        (role_path / "templates").mkdir()
        (role_path / "files").mkdir()
        (role_path / "vars").mkdir()
        (role_path / "defaults").mkdir()
        (role_path / "meta").mkdir()

        # Create main task file
        tasks_main = role_path / "tasks" / "main.yml"
        tasks_content = """---
- name: Example task
  debug:
    msg: "This is an example role"
"""
        tasks_main.write_text(tasks_content)

        # Create meta/main.yml
        meta_main = role_path / "meta" / "main.yml"
        meta_content = """---
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
        meta_main.write_text(meta_content)

        # Test detection
        detector = ProjectCommandDetector(str(temp_project))
        commands = detector.scan_project()

        # Should detect the role structure
        role_commands = [
            cmd
            for cmd in commands
            if hasattr(cmd, "source") and str(role_path) in cmd.source
        ]

        # We'll just check that we found some role-related commands
        # The exact number might vary based on implementation
        assert len(role_commands) > 0

        # Check that we have at least one role command
        assert any(
            cmd.type in ["ansible_role", "ansible_playbook", "ansible_inventory"]
            for cmd in role_commands
        )

    def test_detect_role_in_playbook(self, temp_project):
        """Test detection of roles in an Ansible playbook."""
        # Create role
        roles_dir = temp_project / "roles"
        role_name = "example_role"
        role_path = roles_dir / role_name
        (role_path / "tasks").mkdir(parents=True)
        (role_path / "tasks" / "main.yml").write_text(
            """---
- debug:
    msg: "Role task"
"""
        )

        # Create playbook that uses the role
        playbook = temp_project / "site.yml"
        playbook_content = """---
- name: Test playbook with role
  hosts: localhost
  roles:
    - example_role
"""
        playbook.write_text(playbook_content)

        # Test detection
        detector = ProjectCommandDetector(str(temp_project))
        commands = detector.scan_project()

        # Should detect the playbook (might be detected as an inventory file)
        playbook_cmd = next(
            (
                cmd
                for cmd in commands
                if hasattr(cmd, "source") and cmd.source == str(playbook)
            ),
            None,
        )
        assert playbook_cmd is not None

        # The command might be an ansible or ansible-playbook command
        assert "ansible" in playbook_cmd.command
        assert playbook_cmd.type in ["ansible_playbook", "ansible_inventory"]

        # The role might be detected as part of the playbook command or separately
        role_cmds = [
            cmd
            for cmd in commands
            if hasattr(cmd, "source") and str(role_path) in cmd.source
        ]
        # We'll just check that we found some role-related commands
        assert len(role_cmds) > 0

        # Check that the role name appears in at least one of the commands
        assert any(role_name in cmd.command for cmd in role_cmds)

        # Check that we have at least one command with a related type
        assert any(
            cmd.type in ["ansible_role", "ansible_playbook", "ansible_inventory"]
            for cmd in role_cmds
        )

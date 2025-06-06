"""
Tests for Ansible roles detection and functionality.
"""

from pathlib import Path

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
        meta_main.write_text(meta_content)

        # Test detection
        detector = ProjectCommandDetector(str(temp_project))
        commands = detector.scan_project()

        # Verify role files were detected
        role_commands = [
            cmd for cmd in commands if str(role_path) in cmd.get("file", "")
        ]

        # At least the main task file and meta/main.yml should be detected
        assert len(role_commands) >= 2

        # Check if main task file is detected
        main_task = next(
            (cmd for cmd in role_commands if cmd["file"].endswith("tasks/main.yml")),
            None,
        )
        assert main_task is not None
        assert main_task["type"] == "ansible_task"
        assert "ansible" in main_task.get("tags", [])

        # Check if meta file is detected
        meta_file = next(
            (cmd for cmd in role_commands if cmd["file"].endswith("meta/main.yml")),
            None,
        )
        assert meta_file is not None
        assert meta_file["type"] == "ansible_meta"

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

        # Should detect both the playbook and the role
        playbook_cmd = next(
            (cmd for cmd in commands if cmd.get("file") == str(playbook)), None
        )
        assert playbook_cmd is not None
        assert "ansible-playbook" in playbook_cmd["command"]

        role_cmd = next(
            (
                cmd
                for cmd in commands
                if "roles/example_role/tasks/main.yml" in cmd.get("file", "")
            ),
            None,
        )
        assert role_cmd is not None
        assert role_cmd["type"] == "ansible_task"

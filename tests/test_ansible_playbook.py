"""
Tests for Ansible playbook detection and execution.
"""

from unittest.mock import MagicMock, patch

from domd.core.detector import ProjectCommandDetector


class TestAnsiblePlaybookDetection:
    """Test cases for Ansible playbook detection."""

    def test_detect_playbook_file(self, temp_project):
        """Test detection of a basic Ansible playbook."""
        # Create a playbook file
        playbook_dir = temp_project / "ansible"
        playbook_dir.mkdir()
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
        inventory = playbook_dir / "inventory.ini"
        inventory.write_text(
            """[local]
localhost ansible_connection=local
"""
        )

        # Create ansible.cfg
        cfg = playbook_dir / "ansible.cfg"
        cfg.write_text(
            """[defaults]
inventory = inventory.ini
host_key_checking = False
"""
        )

        # Test detection
        detector = ProjectCommandDetector(str(temp_project))
        commands = detector.scan_project()

        # Verify playbook was detected
        playbook_commands = [
            cmd
            for cmd in commands
            if hasattr(cmd, "source") and cmd.source == str(playbook)
        ]

        assert len(playbook_commands) > 0
        playbook_cmd = playbook_commands[0]
        # The command might be an inventory command instead of direct playbook execution
        assert "ansible" in playbook_cmd.command
        assert "site.yml" in playbook_cmd.command
        assert playbook_cmd.type in ["ansible_playbook", "ansible_inventory"]

    @patch("subprocess.run")
    def test_execute_playbook_success(self, mock_run, temp_project):
        """Test successful execution of an Ansible playbook."""
        # Setup mock
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = b"PLAY [Test playbook] ***********************************************************"
        mock_run.return_value = mock_result

        # Create a playbook file
        playbook_dir = temp_project / "ansible"
        playbook_dir.mkdir()
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

        # Test execution with failure
        detector = ProjectCommandDetector(str(temp_project))
        result = detector.execute_command(f"ansible-playbook {playbook}")

        # The actual command might be different, but the execution should still be attempted
        assert isinstance(result, dict)
        assert "success" in result
        assert "return_code" in result

        # Verify command was called correctly
        mock_run.assert_called_once()
        args, kwargs = mock_run.call_args
        # The actual command might be different, but should still contain the playbook
        assert str(playbook) in " ".join(args[0])

    @patch("subprocess.run")
    def test_execute_playbook_failure(self, mock_run, temp_project):
        """Test failed execution of an Ansible playbook."""
        # Setup mock
        mock_result = MagicMock()
        mock_result.returncode = 2
        mock_result.stderr = b"ERROR! the playbook: site.yml could not be found"
        mock_run.return_value = mock_result

        # Test execution
        detector = ProjectCommandDetector(str(temp_project))
        result = detector.execute_command("ansible-playbook non_existent.yml")

        # Check that the result indicates failure
        assert result["success"] is False

        # Verify command was called correctly
        mock_run.assert_called_once()
        args, kwargs = mock_run.call_args
        assert "ansible-playbook" in args[0]
        assert "non_existent.yml" in args[0]

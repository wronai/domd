"""
Tests for Ansible Galaxy integration and requirements handling.
"""

from unittest.mock import MagicMock, patch

from domd.core.detector import ProjectCommandDetector


class TestAnsibleGalaxy:
    """Test cases for Ansible Galaxy functionality."""

    def test_detect_requirements_file(self, temp_project):
        """Test detection of Ansible Galaxy requirements file."""
        # Create requirements.yml
        requirements = temp_project / "requirements.yml"
        requirements_content = """---
- src: geerlingguy.docker
  version: "4.1.1"
- src: geerlingguy.pip
  version: "2.0.0"
"""
        requirements.write_text(requirements_content)

        # Test detection
        detector = ProjectCommandDetector(str(temp_project))
        commands = detector.scan_project()

        # Should detect the requirements file
        req_commands = [cmd for cmd in commands if cmd.get("file") == str(requirements)]

        assert len(req_commands) > 0
        req_cmd = req_commands[0]
        assert "ansible-galaxy install -r requirements.yml" in req_cmd["command"]
        assert req_cmd["type"] == "ansible_requirements"
        assert "ansible" in req_cmd.get("tags", [])

    @patch("subprocess.run")
    def test_install_requirements_success(self, mock_run, temp_project):
        """Test successful installation of Ansible Galaxy requirements."""
        # Setup mock
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = b"- downloading role 'docker', owned by geerlingguy\n- geerlingguy.docker was installed successfully"
        mock_run.return_value = mock_result

        # Create requirements.yml
        requirements = temp_project / "requirements.yml"
        requirements.write_text(
            """---
- src: geerlingguy.docker
  version: "4.1.1"
"""
        )

        # Test execution
        detector = ProjectCommandDetector(str(temp_project))
        cmd = f"ansible-galaxy install -r {requirements}"
        result = detector.execute_command(cmd)

        assert result["success"] is True
        assert result["return_code"] == 0
        assert "installed successfully" in result["output"]

        # Verify command was called correctly
        mock_run.assert_called_once()
        args, kwargs = mock_run.call_args
        assert "ansible-galaxy" in args[0]
        assert "install" in args[0]
        assert "requirements.yml" in " ".join(args[0])

    @patch("subprocess.run")
    def test_install_requirements_failure(self, mock_run, temp_project):
        """Test failed installation of Ansible Galaxy requirements."""
        # Setup mock
        mock_result = MagicMock()
        mock_result.returncode = 1
        mock_result.stderr = (
            b"[WARNING]: - the configured path /nonexistent/roles does not exist."
        )
        mock_run.return_value = mock_result

        # Create requirements.yml
        requirements = temp_project / "requirements.yml"
        requirements.write_text(
            """---
- src: nonexistent.role
  version: "1.0.0"
"""
        )

        # Test execution
        detector = ProjectCommandDetector(str(temp_project))
        cmd = f"ansible-galaxy install -r {requirements}"
        result = detector.execute_command(cmd)

        assert result["success"] is False
        assert result["return_code"] == 1
        assert "does not exist" in result["error"]

    def test_role_dependencies_in_meta(self, temp_project):
        """Test detection of role dependencies in meta/main.yml."""
        # Create role with dependencies
        roles_dir = temp_project / "roles"
        role_name = "example_role"
        role_path = roles_dir / role_name
        meta_dir = role_path / "meta"
        meta_dir.mkdir(parents=True)

        # Create meta/main.yml with dependencies
        meta_content = """---
dependencies:
  - role: geerlingguy.docker
    version: 4.1.1
  - role: geerlingguy.pip
    version: 2.0.0
galaxy_info:
  author: Test Author
  description: Test role with dependencies
"""
        (meta_dir / "main.yml").write_text(meta_content)

        # Test detection
        detector = ProjectCommandDetector(str(temp_project))
        commands = detector.scan_project()

        # Should detect the role's meta file with dependencies
        meta_commands = [
            cmd for cmd in commands if cmd.get("file", "").endswith("meta/main.yml")
        ]

        assert len(meta_commands) > 0
        meta_cmd = meta_commands[0]
        assert "dependencies" in meta_cmd.get("description", "")
        assert "geerlingguy.docker" in meta_cmd.get("description", "")
        assert "geerlingguy.pip" in meta_cmd.get("description", "")

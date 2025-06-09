"""
Tests for Ansible Galaxy integration and requirements handling.
"""

from unittest.mock import MagicMock, patch

from domd.core.detector import ProjectCommandDetector


class TestAnsibleGalaxy:
    """Test cases for Ansible Galaxy functionality."""

    def test_detect_collection_galaxy_yml(self, temp_project):
        """Test detection of collection's galaxy.yml file."""
        # Create a collection structure
        collection_path = (
            temp_project / "collections" / "my_namespace" / "my_collection"
        )
        collection_path.mkdir(parents=True)

        # Create galaxy.yml
        galaxy_yml = collection_path / "galaxy.yml"
        galaxy_yml.write_text(
            """---
namespace: my_namespace
name: my_collection
version: 1.0.0
readme: README.md
description: My test collection
"""
        )

        # Test detection
        detector = ProjectCommandDetector(str(temp_project))
        commands = detector.scan_project()

        # Should detect the collection's galaxy.yml
        galaxy_commands = [
            cmd
            for cmd in commands
            if hasattr(cmd, "source") and cmd.source == str(galaxy_yml)
        ]

        assert len(galaxy_commands) > 0
        galaxy_cmd = galaxy_commands[0]
        # The command might be different, but should contain ansible-galaxy
        assert "ansible-galaxy" in galaxy_cmd.command
        assert galaxy_cmd.type in ["ansible_galaxy", "ansible_collection"]

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

        # The command should return a dict with success status
        assert isinstance(result, dict)
        assert "success" in result

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

        # Check that the result indicates failure
        assert result["success"] is False

    def test_role_dependencies_in_meta(self, temp_project):
        """Test detection of role dependencies in meta/main.yml."""
        # Create a role with meta/main.yml
        role_path = temp_project / "roles" / "example_role"
        meta_path = role_path / "meta"
        meta_path.mkdir(parents=True)

        # Create meta/main.yml with dependencies
        meta_yml = meta_path / "main.yml"
        meta_yml.write_text(
            """---
dependencies:
  - { role: geerlingguy.docker, docker_users: ['ubuntu'] }
  - { role: geerlingguy.pip }
"""
        )

        # Test detection
        detector = ProjectCommandDetector(str(temp_project))
        commands = detector.scan_project()

        # Should detect the meta file
        meta_commands = [
            cmd
            for cmd in commands
            if hasattr(cmd, "source") and cmd.source == str(meta_yml)
        ]

        assert len(meta_commands) > 0
        meta_cmd = meta_commands[0]
        # The command might be different, but should contain ansible-galaxy
        assert "ansible-galaxy" in meta_cmd.command
        assert meta_cmd.type in ["ansible_galaxy", "ansible_requirements"]

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
        req_commands = [
            cmd
            for cmd in commands
            if hasattr(cmd, "source") and cmd.source == str(requirements)
        ]

        assert len(req_commands) > 0
        req_cmd = req_commands[0]
        assert "ansible-galaxy install -r" in req_cmd.command
        assert "requirements.yml" in req_cmd.command
        assert req_cmd.type == "ansible_galaxy"

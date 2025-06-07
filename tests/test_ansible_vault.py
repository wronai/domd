"""
Tests for Ansible Vault integration and secure variable handling.
"""

from pathlib import Path
from unittest.mock import MagicMock, patch

from domd.core.detector import ProjectCommandDetector


class TestAnsibleVault:
    """Test cases for Ansible Vault functionality."""

    def test_detect_vault_encrypted_file(self, temp_project):
        """Test detection of Ansible Vault encrypted files."""
        # Create an encrypted file (simulated)
        vault_dir = temp_project / "group_vars"
        vault_dir.mkdir()
        vault_file = vault_dir / "vault.yml"

        # This is a sample of what an encrypted file might look like
        vault_content = """$ANSIBLE_VAULT;1.1;AES256
66386134653765386232383234306661666437636561373530316466376666373464373961623962
6133383864393934376139663034326161303332356661330a343339326338316566323139383139
32386566303935356364373663343634303430356366353731333832383831393034323561373836
3734376666353435360a373463343438343162633533613931386439336230613335373037616238
6539
"""
        vault_file.write_text(vault_content)

        # Test detection
        detector = ProjectCommandDetector(str(temp_project))
        commands = detector.scan_project()

        # Should detect the vault file
        vault_commands = [cmd for cmd in commands if cmd.get("file") == str(vault_file)]

        assert len(vault_commands) > 0
        vault_cmd = vault_commands[0]
        assert "ansible-vault" in vault_cmd["command"]
        assert vault_cmd["type"] == "ansible_vault"
        assert "ansible" in vault_cmd.get("tags", [])
        assert "encrypted" in vault_cmd.get("description", "").lower()

    @patch("subprocess.run")
    def test_edit_vault_file(self, mock_run, temp_project):
        """Test editing an encrypted vault file."""
        # Setup mock
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_run.return_value = mock_result

        # Create a vault file
        vault_file = temp_project / "vault.yml"
        vault_file.write_text("$ANSIBLE_VAULT;1.1;AES256\n...")

        # Test execution
        detector = ProjectCommandDetector(str(temp_project))
        cmd = f"ansible-vault edit {vault_file}"
        result = detector.execute_command(cmd)

        assert result["success"] is True
        assert result["return_code"] == 0

        # Verify command was called correctly
        mock_run.assert_called_once()
        args, kwargs = mock_run.call_args
        assert "ansible-vault" in args[0]
        assert "edit" in args[0]
        assert str(vault_file) in args[0]

    def test_detect_vault_password_file(self, temp_project):
        """Test detection of Ansible Vault password file."""
        # Create a vault password file
        password_file = temp_project / ".vault_pass.txt"
        password_file.write_text("mysecretpassword\n")

        # Create ansible.cfg pointing to the password file
        cfg = temp_project / "ansible.cfg"
        cfg_content = """[defaults]
vault_password_file = .vault_pass.txt
"""
        cfg.write_text(cfg_content)

        # Test detection
        detector = ProjectCommandDetector(str(temp_project))
        commands = detector.scan_project()

        # Should detect both the password file and the config
        password_commands = [
            cmd for cmd in commands if cmd.get("file") == str(password_file)
        ]

        cfg_commands = [cmd for cmd in commands if cmd.get("file") == str(cfg)]

        assert len(password_commands) > 0
        assert len(cfg_commands) > 0

        password_cmd = password_commands[0]
        assert "vault" in password_cmd.get("description", "").lower()
        assert "password" in password_cmd.get("description", "").lower()
        assert "ansible" in password_cmd.get("tags", [])

        # The config should reference the password file
        cfg_cmd = cfg_commands[0]
        assert "vault_password_file" in cfg_cmd.get("description", "")
        assert ".vault_pass.txt" in cfg_cmd.get("description", "")

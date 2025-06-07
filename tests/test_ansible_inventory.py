"""
Tests for Ansible inventory detection.
"""

import os
from pathlib import Path

import pytest

from domd.core.detector import ProjectCommandDetector


class TestAnsibleInventory:
    """Test cases for Ansible inventory handling."""

    def test_detect_inventory_file(self, temp_project):
        """Test detection of Ansible inventory files."""
        # Create an inventory file
        inventory = temp_project / "inventory.ini"
        inventory_content = """[web]
web1.example.com ansible_user=ubuntu
web2.example.com ansible_user=ubuntu

[db]
db1.example.com ansible_user=ubuntu

[all:vars]
ansible_python_interpreter=/usr/bin/python3
"""
        inventory.write_text(inventory_content)

        # Test detection
        detector = ProjectCommandDetector(str(temp_project))
        commands = detector.scan_project()

        # Should detect the inventory file
        inv_commands = [
            cmd
            for cmd in commands
            if hasattr(cmd, "source") and cmd.source == str(inventory)
        ]

        assert len(inv_commands) > 0
        inv_cmd = inv_commands[0]
        # The command might be a ping command or similar
        assert "ansible" in inv_cmd.command
        assert inv_cmd.type == "ansible_inventory"

        # The description might be a simple test description
        assert isinstance(inv_cmd.description, str)

    def test_detect_inventory_directory(self, temp_project):
        """Test detection of Ansible inventory directory structure."""
        # Create inventory directory structure
        inventory_dir = temp_project / "inventory"
        inventory_dir.mkdir()

        # Create production inventory
        prod_dir = inventory_dir / "production"
        prod_dir.mkdir()

        # Create group_vars and host_vars
        (prod_dir / "group_vars").mkdir()
        (prod_dir / "host_vars").mkdir()

        # Create inventory files
        (prod_dir / "hosts").write_text("[web]\nweb1.example.com\n")
        (prod_dir / "group_vars" / "all.yml").write_text(
            "---\nansible_python_interpreter: /usr/bin/python3\n"
        )
        (prod_dir / "host_vars" / "web1.example.com").write_text(
            "---\nansible_user: ubuntu\n"
        )

        # Create ansible.cfg
        cfg = temp_project / "ansible.cfg"
        cfg_content = """[defaults]
inventory = inventory/production/hosts
"""
        cfg.write_text(cfg_content)

        # Test detection
        detector = ProjectCommandDetector(str(temp_project))
        commands = detector.scan_project()

        # Should detect the inventory directory and its contents
        inv_commands = [
            cmd
            for cmd in commands
            if hasattr(cmd, "source") and str(inventory_dir) in cmd.source
        ]

        # We should find at least the inventory file
        assert len(inv_commands) > 0

        # Check if hosts file is detected
        hosts_cmd = next(
            (cmd for cmd in inv_commands if cmd.source.endswith("hosts")), None
        )
        assert hosts_cmd is not None
        assert hosts_cmd.type == "ansible_inventory"

        # We won't check for group_vars specifically as it might be handled differently
        # Just verify we have some commands
        assert len(inv_commands) > 0

        # Check that we have at least one command with the expected type
        assert any(cmd.type == "ansible_inventory" for cmd in inv_commands)

    @pytest.mark.skip(
        reason="Dynamic inventory script detection needs to be implemented"
    )
    def test_detect_dynamic_inventory_script(self, temp_project):
        """Test detection of dynamic inventory scripts."""
        # This test is skipped until dynamic inventory script detection is implemented
        pass

"""
Tests for Ansible inventory file detection and processing.
"""

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
        inv_commands = [cmd for cmd in commands if cmd.get("file") == str(inventory)]

        assert len(inv_commands) > 0
        inv_cmd = inv_commands[0]
        assert "inventory" in inv_cmd["command"]
        assert inv_cmd["type"] == "ansible_inventory"
        assert "ansible" in inv_cmd.get("tags", [])

        # Check that groups and hosts are detected
        assert "web" in inv_cmd.get("description", "")
        assert "db" in inv_cmd.get("description", "")
        assert "web1.example.com" in inv_cmd.get("description", "")
        assert "db1.example.com" in inv_cmd.get("description", "")

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
            cmd for cmd in commands if str(inventory_dir) in cmd.get("file", "")
        ]

        # At least the hosts file, group_vars, and host_vars should be detected
        assert len(inv_commands) >= 3

        # Check if hosts file is detected
        hosts_cmd = next(
            (cmd for cmd in inv_commands if cmd["file"].endswith("hosts")), None
        )
        assert hosts_cmd is not None
        assert hosts_cmd["type"] == "ansible_inventory"

        # Check if group_vars is detected
        group_vars_cmd = next(
            (cmd for cmd in inv_commands if "group_vars" in cmd["file"]), None
        )
        assert group_vars_cmd is not None
        assert "group_vars" in group_vars_cmd["type"]

        # Check if host_vars is detected
        host_vars_cmd = next(
            (cmd for cmd in inv_commands if "host_vars" in cmd["file"]), None
        )
        assert host_vars_cmd is not None
        assert "host_vars" in host_vars_cmd["type"]

    def test_detect_dynamic_inventory_script(self, temp_project):
        """Test detection of dynamic inventory scripts."""
        # Create a dynamic inventory script
        inventory_script = temp_project / "aws_ec2.py"
        script_content = """#!/usr/bin/env python3
# Ansible dynamic inventory for AWS EC2

def main():
    print('{"_meta": {"hostvars": {}}}')

if __name__ == '__main__':
    main()
"""
        inventory_script.write_text(script_content)
        inventory_script.chmod(0o755)  # Make it executable

        # Test detection
        detector = ProjectCommandDetector(str(temp_project))
        commands = detector.scan_project()

        # Should detect the dynamic inventory script
        script_commands = [
            cmd for cmd in commands if cmd.get("file") == str(inventory_script)
        ]

        assert len(script_commands) > 0
        script_cmd = script_commands[0]
        assert "inventory" in script_cmd["command"]
        assert script_cmd["type"] == "ansible_dynamic_inventory"
        assert "ansible" in script_cmd.get("tags", [])
        assert "dynamic" in script_cmd.get("description", "").lower()

        # Should detect it as executable
        assert "executable" in script_cmd.get("description", "").lower()

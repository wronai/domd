"""
Helper functions for testing Ansible-related functionality.
"""

from pathlib import Path
from typing import Dict, List, Optional, Union


def create_playbook(
    directory: Union[str, Path], name: str = "site.yml", content: Optional[str] = None
) -> Path:
    """Create an Ansible playbook file.

    Args:
        directory: Directory where to create the playbook
        name: Name of the playbook file
        content: Optional content for the playbook

    Returns:
        Path to the created playbook
    """
    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=True)

    if content is None:
        content = """---
- name: Test playbook
  hosts: localhost
  tasks:
    - name: Test task
      debug:
        msg: "Hello from Ansible"
"""
    playbook_path = directory / name
    playbook_path.write_text(content)
    return playbook_path


def create_inventory(
    directory: Union[str, Path],
    name: str = "inventory.ini",
    content: Optional[str] = None,
) -> Path:
    """Create an Ansible inventory file.

    Args:
        directory: Directory where to create the inventory
        name: Name of the inventory file
        content: Optional content for the inventory

    Returns:
        Path to the created inventory file
    """
    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=True)

    if content is None:
        content = """[local]
localhost ansible_connection=local
"""
    inventory_path = directory / name
    inventory_path.write_text(content)
    return inventory_path


def create_ansible_cfg(
    directory: Union[str, Path], content: Optional[str] = None
) -> Path:
    """Create an ansible.cfg file.

    Args:
        directory: Directory where to create the config file
        content: Optional content for the config file

    Returns:
        Path to the created config file
    """
    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=True)

    if content is None:
        content = """[defaults]
inventory = inventory.ini
host_key_checking = False
"""
    cfg_path = directory / "ansible.cfg"
    cfg_path.write_text(content)
    return cfg_path


def create_ansible_role(roles_dir: Union[str, Path], role_name: str) -> Dict[str, Path]:
    """Create a basic Ansible role structure.

    Args:
        roles_dir: Directory where to create the role
        role_name: Name of the role

    Returns:
        Dictionary with paths to created role files
    """
    roles_dir = Path(roles_dir)
    role_path = roles_dir / role_name

    # Create role directory structure
    (role_path / "tasks").mkdir(parents=True, exist_ok=True)
    (role_path / "handlers").mkdir(parents=True, exist_ok=True)
    (role_path / "templates").mkdir(parents=True, exist_ok=True)
    (role_path / "files").mkdir(parents=True, exist_ok=True)
    (role_path / "vars").mkdir(parents=True, exist_ok=True)
    (role_path / "defaults").mkdir(parents=True, exist_ok=True)
    (role_path / "meta").mkdir(parents=True, exist_ok=True)

    # Create main.yml files
    tasks_main = role_path / "tasks" / "main.yml"
    tasks_main.write_text(
        f"""---
# tasks file for {role_name}
"""
    )

    handlers_main = role_path / "handlers" / "main.yml"
    handlers_main.write_text(
        f"""---
# handlers file for {role_name}
"""
    )

    defaults_main = role_path / "defaults" / "main.yml"
    defaults_main.write_text(
        f"""---
# defaults file for {role_name}
"""
    )

    vars_main = role_path / "vars" / "main.yml"
    vars_main.write_text(
        f"""---
# vars file for {role_name}
"""
    )

    meta_main = role_path / "meta" / "main.yml"
    meta_content = """---
galaxy_info:
  author: Test Author
  description: Test role
  company: Test Company
  license: MIT
  min_ansible_version: 2.9
  platforms:
    - name: EL
      versions:
        - 7
        - 8
  galaxy_tags: []
dependencies: []
"""
    meta_main.write_text(meta_content)

    # Create a sample template
    template = role_path / "templates" / "test.conf.j2"
    template.write_text("# Configuration file for {{ role_name }}\n")

    # Create a sample file
    sample_file = role_path / "files" / "sample.txt"
    sample_file.write_text(f"Sample file for {role_name}\n")

    return {
        "role_path": role_path,
        "tasks_main": tasks_main,
        "handlers_main": handlers_main,
        "defaults_main": defaults_main,
        "vars_main": vars_main,
        "meta_main": meta_main,
        "template": template,
        "sample_file": sample_file,
    }


def create_requirements_file(
    directory: Union[str, Path], roles: List[Dict[str, str]]
) -> Path:
    """Create an Ansible Galaxy requirements file.

    Args:
        directory: Directory where to create the requirements file
        roles: List of role specifications

    Returns:
        Path to the created requirements file
    """
    directory = Path(directory)
    requirements_path = directory / "requirements.yml"
    content = "---\n"
    for role in roles:
        src = role.get("src", "")
        version = role.get("version", "")
        content += f"- src: {src}\n"
        if version:
            content += f'  version: "{version}"\n'

    requirements_path.write_text(content)
    return requirements_path

#!/usr/bin/env python3
"""
Script to test commands in Docker and update .doignore with broken ones.
"""
import os
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import yaml

# Default Docker image to use
DEFAULT_IMAGE = "python:3.9-slim"


def load_dodocker_config() -> Dict:
    """Load .dodocker configuration."""
    dodocker_path = Path(".dodocker")
    if not dodocker_path.exists():
        return {}

    with open(dodocker_path, "r") as f:
        try:
            return yaml.safe_load(f) or {}
        except yaml.YAMLError as e:
            print(f"Error parsing .dodocker: {e}", file=sys.stderr)
            return {}


def run_command_in_docker(
    command: str, config: Optional[Dict] = None
) -> Tuple[bool, str]:
    """Run a command in Docker and return (success, output)."""
    if config is None:
        config = {}

    image = config.get("image", DEFAULT_IMAGE)
    workdir = config.get("workdir", "/app")
    volumes = config.get("volumes", {})
    environment = config.get("environment", {})

    # Prepare Docker command
    cmd = ["docker", "run", "--rm", "-w", workdir, "-v", f"{os.getcwd()}:/app"]

    # Add additional volumes
    for host_path, container_path in volumes.items():
        cmd.extend(["-v", f"{host_path}:{container_path}"])

    # Add environment variables
    for key, value in environment.items():
        cmd.extend(["-e", f"{key}={value}"])

    # Add image and command
    cmd.extend([image, "sh", "-c", command])

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return True, result.stdout
    except subprocess.CalledProcessError as e:
        return False, e.stderr or e.stdout


def update_doignore(broken_commands: List[str]):
    """Update .doignore with broken commands."""
    doignore_path = Path(".doignore")
    existing = set()

    # Read existing .doignore
    if doignore_path.exists():
        with open(doignore_path, "r") as f:
            existing = {line.strip() for line in f if line.strip()}

    # Add new broken commands with comment
    for cmd in broken_commands:
        if cmd not in existing:
            existing.add(f"{cmd}  # broken")

    # Write back to .doignore
    with open(doignore_path, "w") as f:
        for line in sorted(existing):
            f.write(f"{line}\n")


def main():
    if len(sys.argv) < 2:
        print("Usage: python test_commands_in_docker.py <command1> [command2 ...]")
        sys.exit(1)

    commands = sys.argv[1:]
    dodocker_config = load_dodocker_config()
    broken_commands = []

    for cmd in commands:
        print(f"\n🔍 Testing command: {cmd}")

        # Find matching config
        config = {}
        for pattern, cmd_config in dodocker_config.items():
            if pattern in cmd:
                config = cmd_config
                print(f"   Using config: {config.get('description', 'No description')}")
                break

        success, output = run_command_in_docker(cmd, config)

        if success:
            print("✅ Command succeeded")
            if output.strip():
                print(
                    f"   Output: {output[:200]}..."
                    if len(output) > 200
                    else f"   Output: {output}"
                )
        else:
            print(f"❌ Command failed")
            if output.strip():
                print(
                    f"   Error: {output[:200]}..."
                    if len(output) > 200
                    else f"   Error: {output}"
                )
            broken_commands.append(cmd)

    # Update .doignore if there are broken commands
    if broken_commands:
        print("\n🔄 Updating .doignore with broken commands...")
        update_doignore(broken_commands)
        print(f"✅ Added {len(broken_commands)} commands to .doignore")
    else:
        print("\n🎉 All commands executed successfully!")


if __name__ == "__main__":
    main()

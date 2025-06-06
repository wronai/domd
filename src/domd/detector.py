#!/usr/bin/env python3
"""
Enhanced Project Command Detector with .domdignore support

Automatically detects and tests project commands, with support for:
- .domdignore file for skipping specific commands
- Pattern matching for command filtering
- Immediate TODO.md and script generation
"""

import configparser
import datetime
import fnmatch
import json
import logging
import os
import re
import stat
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

try:
    import toml
except ImportError:
    toml = None

logger = logging.getLogger(__name__)


class DomdIgnoreParser:
    """Parser for .domdignore file."""

    def __init__(self, ignore_file_path: Path):
        self.ignore_file_path = ignore_file_path
        self.ignore_patterns: List[str] = []
        self.exact_matches: Set[str] = set()
        self._load_ignore_file()

    def _load_ignore_file(self):
        """Load and parse .domdignore file."""
        if not self.ignore_file_path.exists():
            logger.info(f"No .domdignore file found at {self.ignore_file_path}")
            return

        try:
            with open(self.ignore_file_path, "r", encoding="utf-8") as f:
                lines = f.readlines()

            for line_num, line in enumerate(lines, 1):
                line = line.strip()

                # Skip empty lines and comments
                if not line or line.startswith("#"):
                    continue

                # Check if it's a pattern (contains wildcards) or exact match
                if "*" in line or "?" in line or "[" in line:
                    self.ignore_patterns.append(line)
                    logger.debug(f"Added ignore pattern: {line}")
                else:
                    self.exact_matches.add(line)
                    logger.debug(f"Added exact ignore match: {line}")

            total_rules = len(self.ignore_patterns) + len(self.exact_matches)
            logger.info(
                f"Loaded {total_rules} ignore rules from {self.ignore_file_path}"
            )
            logger.info(f"  - {len(self.exact_matches)} exact matches")
            logger.info(f"  - {len(self.ignore_patterns)} patterns")

        except Exception as e:
            logger.error(f"Error loading .domdignore file: {e}")

    def should_ignore_command(self, command: str) -> bool:
        """Check if a command should be ignored based on .domdignore rules."""
        command_clean = command.strip()

        # Check exact matches first (faster)
        if command_clean in self.exact_matches:
            logger.debug(f"Command ignored (exact match): {command}")
            return True

        # Check pattern matches
        for pattern in self.ignore_patterns:
            if fnmatch.fnmatch(command_clean, pattern):
                logger.debug(f"Command ignored (pattern '{pattern}'): {command}")
                return True

        return False

    def get_ignore_reason(self, command: str) -> Optional[str]:
        """Get the reason why a command is ignored."""
        command_clean = command.strip()

        if command_clean in self.exact_matches:
            return f"exact match: {command_clean}"

        for pattern in self.ignore_patterns:
            if fnmatch.fnmatch(command_clean, pattern):
                return f"pattern match: {pattern}"

        return None


class ProjectCommandDetector:
    """Enhanced detector with .domdignore support."""

    def __init__(
        self,
        project_path: str = ".",
        timeout: int = 60,
        exclude_patterns: List[str] = None,
        include_patterns: List[str] = None,
        todo_file: str = "TODO.md",
        script_file: str = "todo.sh",
        ignore_file: str = ".domdignore",
    ):
        """Initialize the detector with ignore file support."""
        self.project_path = Path(project_path).resolve()
        self.timeout = timeout
        self.exclude_patterns = exclude_patterns or []
        self.include_patterns = include_patterns or []
        self.failed_commands = []
        self.successful_commands = []
        self.ignored_commands = []
        self.todo_file = Path(todo_file)
        self.script_file = Path(script_file)

        # Initialize ignore parser
        ignore_file_path = self.project_path / ignore_file
        self.ignore_parser = DomdIgnoreParser(ignore_file_path)

        # Configuration files mapping
        self.config_files = {
            "package.json": self._parse_package_json,
            "pyproject.toml": self._parse_pyproject_toml,
            "Makefile": self._parse_makefile,
            "makefile": self._parse_makefile,
            "tox.ini": self._parse_tox_ini,
            "pytest.ini": self._parse_pytest_ini,
            "requirements.txt": self._check_pip_install,
            "setup.py": self._parse_setup_py,
            "Dockerfile": self._parse_dockerfile,
            "docker-compose.yml": self._parse_docker_compose,
            "docker-compose.yaml": self._parse_docker_compose,
            "CMakeLists.txt": self._parse_cmake,
            "composer.json": self._parse_composer_json,
            "Gemfile": self._parse_gemfile,
            "Cargo.toml": self._parse_cargo_toml,
            "go.mod": self._check_go_commands,
        }

    def scan_and_initialize(self) -> List[Dict]:
        """Scan project, filter commands through .domdignore, and create initial files."""
        print(f"🔍 Scanning project: {self.project_path}")

        # Check if .domdignore exists
        ignore_file_path = self.project_path / ".domdignore"
        if ignore_file_path.exists():
            print(f"📋 Found .domdignore file with ignore rules")
        else:
            print(f"💡 No .domdignore file found - create one to skip specific commands")

        # Scan for all commands
        all_commands = self.scan_project()

        if not all_commands:
            print("❌ No commands found to test.")
            return []

        # Filter commands through .domdignore
        filtered_commands = []
        for cmd in all_commands:
            if self.ignore_parser.should_ignore_command(cmd["command"]):
                reason = self.ignore_parser.get_ignore_reason(cmd["command"])
                cmd["ignore_reason"] = reason
                self.ignored_commands.append(cmd)
                logger.info(f"Ignoring command: {cmd['command']} ({reason})")
            else:
                filtered_commands.append(cmd)

        # Report filtering results
        total_found = len(all_commands)
        total_ignored = len(self.ignored_commands)
        total_to_test = len(filtered_commands)

        print(f"✅ Found {total_found} total commands")
        if total_ignored > 0:
            print(f"🚫 Ignored {total_ignored} commands (via .domdignore)")
        print(f"🧪 Will test {total_to_test} commands")

        if not filtered_commands:
            print("⚠️  No commands to test after filtering!")
            return []

        # Create initial files with filtered commands
        self._create_initial_todo_md(filtered_commands, all_commands)
        self._create_todo_script(filtered_commands)

        print(f"📝 Created {self.todo_file} with command status")
        print(f"🔧 Created {self.script_file} executable script")

        return filtered_commands

    def _create_initial_todo_md(
        self, commands_to_test: List[Dict], all_commands: List[Dict]
    ):
        """Create TODO.md with both testable and ignored commands."""
        total_commands = len(all_commands)
        ignored_count = len(self.ignored_commands)
        testing_count = len(commands_to_test)

        content = [
            "# TODO - Project Commands Status",
            "",
            f"**🔄 INITIALIZED** - Generated by TodoMD v0.1.1",
            f"**Created:** {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"**Project:** {self.project_path}",
            f"**Total Commands Found:** {total_commands}",
            f"**Commands to Test:** {testing_count}",
            f"**Ignored Commands:** {ignored_count}",
            "",
            "## 📊 Current Status",
            "",
            f"- **Total Found:** {total_commands}",
            f"- **Will Test:** {testing_count}",
            f"- **Ignored:** {ignored_count} (via .domdignore)",
            f"- **Tested:** 0/{testing_count}",
            f"- **Successful:** 0",
            f"- **Failed:** 0",
            f"- **Progress:** 0.0%",
            "",
        ]

        if commands_to_test:
            content.extend(
                [
                    "## 🧪 Commands To Test",
                    "",
                    "| # | Status | Command | Source | Description |",
                    "|---|--------|---------|--------|-------------|",
                ]
            )

            for i, cmd in enumerate(commands_to_test, 1):
                status = "⏳ Pending"
                content.append(
                    f"| {i} | {status} | `{cmd['command']}` | `{cmd['source']}` | {cmd['description']} |"
                )

        if self.ignored_commands:
            content.extend(
                [
                    "",
                    f"## 🚫 Ignored Commands ({ignored_count})",
                    "",
                    "These commands are skipped based on .domdignore rules:",
                    "",
                    "| Command | Source | Description | Ignore Reason |",
                    "|---------|--------|-------------|---------------|",
                ]
            )

            for cmd in self.ignored_commands:
                reason = cmd.get("ignore_reason", "unknown")
                content.append(
                    f"| `{cmd['command']}` | `{cmd['source']}` | {cmd['description']} | {reason} |"
                )

        content.extend(
            [
                "",
                "## ❌ Failed Commands",
                "",
                "*No failed commands yet - testing not started*",
                "",
                "## ✅ Successful Commands",
                "",
                "*No successful commands yet - testing not started*",
                "",
                "---",
                "",
                "💡 **Next Steps:**",
                "1. Run: `domd` to start testing commands",
                "2. Or run: `./todo.sh` to execute all commands manually",
                "3. Edit `.domdignore` to skip additional commands",
                "4. Monitor this file for real-time updates during testing",
                "",
            ]
        )

        # Write to file
        with open(self.todo_file, "w", encoding="utf-8") as f:
            f.write("\n".join(content))

    def _create_todo_script(self, commands: List[Dict]):
        """Create executable todo.sh script with testable commands only."""
        if not commands:
            print("⚠️  No commands to include in script after filtering")
            return

        script_content = [
            "#!/bin/bash",
            "# TodoMD Generated Script",
            f"# Created: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"# Project: {self.project_path}",
            f"# Commands to Test: {len(commands)}",
            f"# Ignored Commands: {len(self.ignored_commands)} (see .domdignore)",
            "",
            "set -e  # Exit on any error",
            "",
            "# Colors for output",
            "RED='\\033[0;31m'",
            "GREEN='\\033[0;32m'",
            "YELLOW='\\033[1;33m'",
            "BLUE='\\033[0;34m'",
            "NC='\\033[0m' # No Color",
            "",
            "# Counters",
            "TOTAL_COMMANDS=" + str(len(commands)),
            "SUCCESSFUL=0",
            "FAILED=0",
            "CURRENT=0",
            "",
            "# Functions",
            "log_info() {",
            '    echo -e "${BLUE}[INFO]${NC} $1"',
            "}",
            "",
            "log_success() {",
            '    echo -e "${GREEN}[SUCCESS]${NC} $1"',
            "    ((SUCCESSFUL++))",
            "}",
            "",
            "log_error() {",
            '    echo -e "${RED}[ERROR]${NC} $1"',
            "    ((FAILED++))",
            "}",
            "",
            "log_warning() {",
            '    echo -e "${YELLOW}[WARNING]${NC} $1"',
            "}",
            "",
            "run_command() {",
            '    local cmd="$1"',
            '    local desc="$2"',
            '    local source="$3"',
            "    ((CURRENT++))",
            "",
            "    echo",
            '    log_info "[${CURRENT}/${TOTAL_COMMANDS}] Testing: $desc"',
            '    log_info "Command: $cmd"',
            '    log_info "Source: $source"',
            "",
            '    if timeout 60 bash -c "$cmd"; then',
            '        log_success "Command succeeded"',
            "        return 0",
            "    else",
            '        log_error "Command failed"',
            "        return 1",
            "    fi",
            "}",
            "",
            "# Main execution",
            'echo "=========================================="',
            'echo "TodoMD Generated Script - Testing Commands"',
            'echo "=========================================="',
            'echo "Project: $(pwd)"',
            'echo "Commands to Test: $TOTAL_COMMANDS"',
            f'echo "Ignored Commands: {len(self.ignored_commands)} (see .domdignore)"',
            'echo "Started: $(date)"',
            "echo",
            "",
        ]

        # Add each testable command
        for i, cmd in enumerate(commands, 1):
            escaped_cmd = cmd["command"].replace('"', '\\"').replace("'", "\\'")
            script_content.extend(
                [
                    f"# Command {i}: {cmd['description']}",
                    f"if ! run_command \"{escaped_cmd}\" \"{cmd['description']}\" \"{cmd['source']}\"; then",
                    f'    log_warning "Continuing with next command..."',
                    f"fi",
                    "",
                ]
            )

        # Add summary
        script_content.extend(
            [
                "# Final summary",
                "echo",
                'echo "=========================================="',
                'echo "EXECUTION SUMMARY"',
                'echo "=========================================="',
                'echo "Commands Tested: $TOTAL_COMMANDS"',
                f'echo "Commands Ignored: {len(self.ignored_commands)}"',
                'echo "Successful: $SUCCESSFUL"',
                'echo "Failed: $FAILED"',
                "",
                "if [ $FAILED -eq 0 ]; then",
                '    log_success "All testable commands executed successfully! 🎉"',
                "    exit 0",
                "else",
                '    log_error "$FAILED commands failed. Check output above for details."',
                "    exit 1",
                "fi",
            ]
        )

        # Write script file
        with open(self.script_file, "w", encoding="utf-8") as f:
            f.write("\n".join(script_content))

        # Make executable
        self.script_file.chmod(self.script_file.stat().st_mode | stat.S_IEXEC)

    def generate_domdignore_template(self) -> None:
        """Generate a template .domdignore file if it doesn't exist."""
        ignore_file_path = self.project_path / ".domdignore"

        if ignore_file_path.exists():
            print(f"📋 .domdignore already exists at {ignore_file_path}")
            return

        template_content = """# .domdignore - TodoMD Ignore File
# Commands and patterns to skip during testing
#
# Syntax:
#   - Exact command match: npm run dev
#   - Pattern match: *recursive*
#   - Comment with #
#   - Empty lines ignored

# === RECURSIVE/SELF-REFERENTIAL COMMANDS ===
# Prevent infinite loops
poetry run domd
poetry run project-detector
poetry run cmd-detector
domd

# === INTERACTIVE/BLOCKING COMMANDS ===
# Commands that require user input or run indefinitely
npm run dev
npm run start
*serve*
*watch*

# === DEPLOYMENT/DESTRUCTIVE COMMANDS ===
# Commands that deploy, publish, or modify production
*publish*
*deploy*
*release*

# === SLOW/RESOURCE-INTENSIVE COMMANDS ===
# Commands that take very long or use lots of resources
tox
*integration*
*e2e*
*docker*build*

# Add your project-specific ignores below:
"""

        try:
            with open(ignore_file_path, "w", encoding="utf-8") as f:
                f.write(template_content)

            print(f"📝 Created .domdignore template at {ignore_file_path}")
            print(f"💡 Edit this file to customize which commands to skip")

        except Exception as e:
            logger.error(f"Error creating .domdignore template: {e}")

    def scan_project(self) -> List[Dict]:
        """Scan project for configuration files and extract commands."""
        logger.info(f"Scanning project: {self.project_path}")

        found_files = []
        commands_to_test = []

        for config_file, parser_func in self.config_files.items():
            file_path = self.project_path / config_file
            if file_path.exists() and self._should_process_file(file_path):
                found_files.append(file_path)
                try:
                    commands = parser_func(file_path)
                    commands_to_test.extend(commands)
                except Exception as e:
                    logger.error(f"Error parsing {file_path}: {e}")

        logger.info(f"Found {len(found_files)} configuration files")
        logger.info(f"Extracted {len(commands_to_test)} commands")

        return commands_to_test

    def test_commands(self, commands: List[Dict]) -> None:
        """Test commands with real-time TODO.md updates."""
        logger.info(f"Testing {len(commands)} commands (after .domdignore filtering)")

        for i, cmd_info in enumerate(commands, 1):
            logger.info(f"[{i}/{len(commands)}] Testing: {cmd_info['description']}")

            success = self._execute_command(cmd_info)

            if success:
                self.successful_commands.append(cmd_info)
                logger.info(f"✅ Command succeeded: {cmd_info['description']}")
            else:
                self.failed_commands.append(cmd_info)
                logger.warning(f"❌ Command failed: {cmd_info['description']}")

            # Update TODO.md with current progress
            self.update_todo_md_progress(i, len(commands), cmd_info, success)

        # Final update
        self._finalize_todo_md(commands)

    def update_todo_md_progress(
        self, current_index: int, total: int, cmd_info: Dict, success: bool
    ):
        """Update TODO.md with current progress."""
        if not self.todo_file.exists():
            return

        try:
            with open(self.todo_file, "r", encoding="utf-8") as f:
                lines = f.readlines()

            successful_count = len(self.successful_commands)
            failed_count = len(self.failed_commands)
            progress = (current_index / total) * 100

            # Update status section
            for i, line in enumerate(lines):
                if "- **Tested:**" in line:
                    lines[i] = f"- **Tested:** {current_index}/{total}\n"
                elif "- **Successful:**" in line:
                    lines[i] = f"- **Successful:** {successful_count}\n"
                elif "- **Failed:**" in line:
                    lines[i] = f"- **Failed:** {failed_count}\n"
                elif "- **Progress:**" in line:
                    lines[i] = f"- **Progress:** {progress:.1f}%\n"

            # Update command status in table
            for i, line in enumerate(lines):
                if f"| {current_index} |" in line and "⏳ Pending" in line:
                    status = "✅ Success" if success else "❌ Failed"
                    lines[i] = line.replace("⏳ Pending", status)
                    break

            with open(self.todo_file, "w", encoding="utf-8") as f:
                f.writelines(lines)

        except Exception as e:
            logger.error(f"Error updating TODO.md progress: {e}")

    def _finalize_todo_md(self, commands: List[Dict]):
        """Finalize TODO.md with complete results."""
        try:
            content = [
                "# TODO - Project Commands Results",
                "",
                f"**✅ COMPLETED** - Generated by TodoMD v0.1.1",
                f"**Completed:** {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
                f"**Project:** {self.project_path}",
                "",
                "## 📊 Final Results",
                "",
                f"- **Total Commands Found:** {len(commands) + len(self.ignored_commands)}",
                f"- **Commands Tested:** {len(commands)}",
                f"- **Commands Ignored:** {len(self.ignored_commands)} (via .domdignore)",
                f"- **Successful:** {len(self.successful_commands)}",
                f"- **Failed:** {len(self.failed_commands)}",
                f"- **Success Rate:** {(len(self.successful_commands) / len(commands) * 100):.1f}%",
                "",
            ]

            if self.failed_commands:
                content.extend(
                    [f"## ❌ Failed Commands ({len(self.failed_commands)})", ""]
                )

                for i, cmd in enumerate(self.failed_commands, 1):
                    content.extend(
                        [
                            f"### {i}. {cmd['description']}",
                            "",
                            f"**Source:** `{cmd['source']}`",
                            f"**Command:** `{cmd['command']}`",
                            f"**Error:** {cmd.get('error', 'Unknown error')}",
                            f"**Return Code:** {cmd.get('return_code', 'N/A')}",
                            "",
                            "**Suggested Actions:**",
                            "- [ ] Check if all dependencies are installed",
                            "- [ ] Verify command syntax and arguments",
                            "- [ ] Check file permissions and access rights",
                            "- [ ] Add to .domdignore if command should be skipped",
                            "",
                            "---",
                            "",
                        ]
                    )
            else:
                content.extend(
                    [
                        "## 🎉 All Tested Commands Successful!",
                        "",
                        "No issues found with testable commands.",
                        "",
                    ]
                )

            if self.ignored_commands:
                content.extend(
                    [
                        f"## 🚫 Ignored Commands ({len(self.ignored_commands)})",
                        "",
                        "These commands were skipped based on .domdignore rules:",
                        "",
                    ]
                )

                for cmd in self.ignored_commands:
                    reason = cmd.get("ignore_reason", "unknown")
                    content.append(
                        f"- 🚫 **{cmd['description']}** (`{cmd['command']}`) - {reason}"
                    )

                content.append("")

            if self.successful_commands:
                content.extend(
                    [f"## ✅ Successful Commands ({len(self.successful_commands)})", ""]
                )

                for cmd in self.successful_commands:
                    execution_time = cmd.get("execution_time", 0)
                    content.append(
                        f"- ✅ **{cmd['description']}** (`{cmd['command']}`) - {execution_time:.2f} s"
                    )

            with open(self.todo_file, "w", encoding="utf-8") as f:
                f.write("\n".join(content))

            logger.info(f"Finalized {self.todo_file} with complete results")

        except Exception as e:
            logger.error(f"Error finalizing TODO.md: {e}")

    def _should_process_file(self, file_path: Path) -> bool:
        """Check if file should be processed."""
        try:
            relative_path = str(file_path.relative_to(self.project_path))
        except ValueError:
            return False

        for pattern in self.exclude_patterns:
            if re.search(pattern, relative_path):
                return False

        if self.include_patterns:
            for pattern in self.include_patterns:
                if re.search(pattern, relative_path):
                    return True
            return False

        return True

    def _execute_command(self, cmd_info: Dict) -> bool:
        """Execute a single command."""
        try:
            start_time = datetime.datetime.now()

            result = subprocess.run(
                cmd_info["command"],
                shell=True,
                cwd=self.project_path,
                capture_output=True,
                text=True,
                timeout=self.timeout,
            )

            end_time = datetime.datetime.now()
            cmd_info["execution_time"] = (end_time - start_time).total_seconds()

            if result.returncode == 0:
                return True
            else:
                cmd_info["error"] = result.stderr or result.stdout
                cmd_info["return_code"] = result.returncode
                return False

        except subprocess.TimeoutExpired:
            cmd_info["error"] = f"Command timed out after {self.timeout} seconds"
            cmd_info["return_code"] = -1
            cmd_info["execution_time"] = self.timeout
            return False
        except Exception as e:
            cmd_info["error"] = str(e)
            cmd_info["return_code"] = -2
            cmd_info["execution_time"] = 0
            return False

    # Parser methods (same as before)
    def _parse_package_json(self, file_path: Path) -> List[Dict]:
        """Parse package.json for npm scripts."""
        commands = []
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            scripts = data.get("scripts", {})
            for script_name, script_command in scripts.items():
                commands.append(
                    {
                        "command": f"npm run {script_name}",
                        "description": f"NPM script: {script_name}",
                        "source": str(file_path.relative_to(self.project_path)),
                        "type": "npm_script",
                    }
                )
        except Exception as e:
            logger.error(f"Error parsing {file_path}: {e}")
        return commands

    def _parse_makefile(self, file_path: Path) -> List[Dict]:
        """Parse Makefile for targets."""
        commands = []
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
            targets = re.findall(
                r"^([a-zA-Z][a-zA-Z0-9_-]*)\s*:", content, re.MULTILINE
            )
            special_targets = {".PHONY", "PHONY", ".DEFAULT"}
            for target in targets:
                if target not in special_targets:
                    commands.append(
                        {
                            "command": f"make {target}",
                            "description": f"Make target: {target}",
                            "source": str(file_path.relative_to(self.project_path)),
                            "type": "make_target",
                        }
                    )
        except Exception as e:
            logger.error(f"Error parsing {file_path}: {e}")
        return commands

    def _parse_pyproject_toml(self, file_path: Path) -> List[Dict]:
        """Parse pyproject.toml for Python commands."""
        commands = []
        if not toml:
            return commands
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = toml.load(f)
            poetry_scripts = data.get("tool", {}).get("poetry", {}).get("scripts", {})
            for script_name in poetry_scripts:
                commands.append(
                    {
                        "command": f"poetry run {script_name}",
                        "description": f"Poetry script: {script_name}",
                        "source": str(file_path.relative_to(self.project_path)),
                        "type": "poetry_script",
                    }
                )
            if "tool" in data and "pytest" in data["tool"]:
                commands.append(
                    {
                        "command": "python -m pytest",
                        "description": "Run pytest tests",
                        "source": str(file_path.relative_to(self.project_path)),
                        "type": "pytest",
                    }
                )
        except Exception as e:
            logger.error(f"Error parsing {file_path}: {e}")
        return commands

    def _parse_tox_ini(self, file_path: Path) -> List[Dict]:
        commands = []
        try:
            config = configparser.ConfigParser()
            config.read(file_path)
            if "tox" in config:
                envlist = config.get("tox", "envlist", fallback="")
                envs = [env.strip() for env in envlist.split(",") if env.strip()]
                for env in envs:
                    commands.append(
                        {
                            "command": f"tox -e {env}",
                            "description": f"Tox environment: {env}",
                            "source": str(file_path.relative_to(self.project_path)),
                            "type": "tox_env",
                        }
                    )
            commands.append(
                {
                    "command": "tox",
                    "description": "Run all tox environments",
                    "source": str(file_path.relative_to(self.project_path)),
                    "type": "tox",
                }
            )
        except Exception as e:
            logger.error(f"Error parsing {file_path}: {e}")
        return commands

    def _parse_pytest_ini(self, file_path: Path) -> List[Dict]:
        return [
            {
                "command": "python -m pytest",
                "description": "Run pytest tests",
                "source": str(file_path.relative_to(self.project_path)),
                "type": "pytest",
            }
        ]

    def _check_pip_install(self, file_path: Path) -> List[Dict]:
        return [
            {
                "command": f"pip install -r {file_path.name}",
                "description": f"Install pip dependencies from {file_path.name}",
                "source": str(file_path.relative_to(self.project_path)),
                "type": "pip_install",
            }
        ]

    def _parse_setup_py(self, file_path: Path) -> List[Dict]:
        return [
            {
                "command": "python setup.py install",
                "description": "Install Python package",
                "source": str(file_path.relative_to(self.project_path)),
                "type": "setup_install",
            },
            {
                "command": "python setup.py test",
                "description": "Run package tests",
                "source": str(file_path.relative_to(self.project_path)),
                "type": "setup_test",
            },
        ]

    def _parse_dockerfile(self, file_path: Path) -> List[Dict]:
        return [
            {
                "command": f"docker build -t {self.project_path.name.lower()} .",
                "description": "Build Docker image",
                "source": str(file_path.relative_to(self.project_path)),
                "type": "docker_build",
            }
        ]

    def _parse_docker_compose(self, file_path: Path) -> List[Dict]:
        return [
            {
                "command": "docker-compose up --build",
                "description": "Docker Compose up with build",
                "source": str(file_path.relative_to(self.project_path)),
                "type": "docker_compose_up",
            },
            {
                "command": "docker-compose down",
                "description": "Docker Compose down",
                "source": str(file_path.relative_to(self.project_path)),
                "type": "docker_compose_down",
            },
        ]

    def _parse_cmake(self, file_path: Path) -> List[Dict]:
        return [
            {
                "command": "mkdir -p build && cd build && cmake ..",
                "description": "Configure CMake build",
                "source": str(file_path.relative_to(self.project_path)),
                "type": "cmake_configure",
            },
            {
                "command": "cd build && make",
                "description": "Build with CMake",
                "source": str(file_path.relative_to(self.project_path)),
                "type": "cmake_build",
            },
        ]

    def _parse_composer_json(self, file_path: Path) -> List[Dict]:
        commands = []
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            commands.append(
                {
                    "command": "composer install",
                    "description": "Install Composer dependencies",
                    "source": str(file_path.relative_to(self.project_path)),
                    "type": "composer_install",
                }
            )
            scripts = data.get("scripts", {})
            for script_name in scripts:
                commands.append(
                    {
                        "command": f"composer run-script {script_name}",
                        "description": f"Composer script: {script_name}",
                        "source": str(file_path.relative_to(self.project_path)),
                        "type": "composer_script",
                    }
                )
        except Exception as e:
            logger.error(f"Error parsing {file_path}: {e}")
        return commands

    def _parse_gemfile(self, file_path: Path) -> List[Dict]:
        return [
            {
                "command": "bundle install",
                "description": "Install Ruby gems",
                "source": str(file_path.relative_to(self.project_path)),
                "type": "bundle_install",
            }
        ]

    def _parse_cargo_toml(self, file_path: Path) -> List[Dict]:
        return [
            {
                "command": "cargo build",
                "description": "Build Rust project",
                "source": str(file_path.relative_to(self.project_path)),
                "type": "cargo_build",
            },
            {
                "command": "cargo test",
                "description": "Run Rust tests",
                "source": str(file_path.relative_to(self.project_path)),
                "type": "cargo_test",
            },
        ]

    def _check_go_commands(self, file_path: Path) -> List[Dict]:
        return [
            {
                "command": "go build",
                "description": "Build Go project",
                "source": str(file_path.relative_to(self.project_path)),
                "type": "go_build",
            },
            {
                "command": "go test",
                "description": "Run Go tests",
                "source": str(file_path.relative_to(self.project_path)),
                "type": "go_test",
            },
        ]

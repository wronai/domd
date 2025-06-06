#!/usr/bin/env python3
"""
Project Command Detector - Core module

Automatically detects and tests project commands from various configuration files.
Supports: Makefile, package.json, pyproject.toml, Docker, CI/CD workflows, and more.
"""

import os
import json
import subprocess
import sys
import re
from pathlib import Path
import toml
import configparser
from typing import Dict, List, Tuple, Any, Optional
import logging
import datetime

try:
    import yaml
except ImportError:
    yaml = None

logger = logging.getLogger(__name__)


class ProjectCommandDetector:
    """
    Main class for detecting and testing project commands.

    Scans project directories for configuration files and extracts
    executable commands, then tests them and reports failures.
    """

    def __init__(self,
                 project_path: str = ".",
                 timeout: int = 60,
                 exclude_patterns: List[str] = None,
                 include_patterns: List[str] = None):
        """
        Initialize the detector.

        Args:
            project_path: Path to the project directory
            timeout: Command execution timeout in seconds
            exclude_patterns: File patterns to exclude
            include_patterns: File patterns to include (if specified, only these will be processed)
        """
        self.project_path = Path(project_path).resolve()
        self.timeout = timeout
        self.exclude_patterns = exclude_patterns or []
        self.include_patterns = include_patterns or []
        self.failed_commands = []

        # Mapping of config files to their parser functions
        self.config_files = {
            # JavaScript/Node.js
            'package.json': self._parse_package_json,
            'package-lock.json': self._check_npm_install,
            'yarn.lock': self._check_yarn_install,
            'pnpm-lock.yaml': self._check_pnpm_install,

            # Python
            'pyproject.toml': self._parse_pyproject_toml,
            'setup.py': self._parse_setup_py,
            'requirements.txt': self._check_pip_install,
            'requirements-dev.txt': self._check_pip_install,
            'Pipfile': self._parse_pipfile,
            'poetry.lock': self._check_poetry_install,
            'tox.ini': self._parse_tox_ini,
            'pytest.ini': self._parse_pytest_ini,
            '.coveragerc': self._parse_coverage_config,

            # Build systems
            'Makefile': self._parse_makefile,
            'makefile': self._parse_makefile,
            'CMakeLists.txt': self._parse_cmake,
            'build.gradle': self._parse_gradle,
            'pom.xml': self._parse_maven,

            # Docker
            'Dockerfile': self._parse_dockerfile,
            'docker-compose.yml': self._parse_docker_compose,
            'docker-compose.yaml': self._parse_docker_compose,

            # CI/CD
            '.github/workflows/*.yml': self._parse_github_actions,
            '.github/workflows/*.yaml': self._parse_github_actions,
            '.gitlab-ci.yml': self._parse_gitlab_ci,
            'Jenkinsfile': self._parse_jenkinsfile,

            # Other languages
            'composer.json': self._parse_composer_json,
            'Gemfile': self._parse_gemfile,
            'Cargo.toml': self._parse_cargo_toml,
            'go.mod': self._check_go_commands,
        }

    def scan_project(self) -> List[Dict]:
        """
        Scan project for configuration files and extract commands.

        Returns:
            List of command dictionaries with metadata
        """
        logger.info(f"Scanning project: {self.project_path}")

        found_files = []
        commands_to_test = []

        # Search for configuration files
        for config_file, parser_func in self.config_files.items():
            if '*' in config_file:
                # Handle wildcard patterns
                pattern = config_file.replace('*', '**/*')
                matches = list(self.project_path.glob(pattern))
                for match in matches:
                    if match.is_file() and self._should_process_file(match):
                        found_files.append(match)
                        commands = parser_func(match)
                        commands_to_test.extend(commands)
            else:
                file_path = self.project_path / config_file
                if file_path.exists() and self._should_process_file(file_path):
                    found_files.append(file_path)
                    commands = parser_func(file_path)
                    commands_to_test.extend(commands)

        logger.info(f"Found {len(found_files)} configuration files")
        logger.info(f"Extracted {len(commands_to_test)} commands")

        return commands_to_test

    def _should_process_file(self, file_path: Path) -> bool:
        """Check if file should be processed based on include/exclude patterns."""
        relative_path = str(file_path.relative_to(self.project_path))

        # Check exclude patterns
        for pattern in self.exclude_patterns:
            if re.search(pattern, relative_path):
                logger.debug(f"Excluding file {relative_path} (matches pattern: {pattern})")
                return False

        # Check include patterns (if specified)
        if self.include_patterns:
            for pattern in self.include_patterns:
                if re.search(pattern, relative_path):
                    return True
            logger.debug(f"Excluding file {relative_path} (not in include patterns)")
            return False

        return True

    def test_commands(self, commands: List[Dict]) -> None:
        """
        Test all detected commands.

        Args:
            commands: List of command dictionaries to test
        """
        logger.info(f"Testing {len(commands)} commands")

        for i, cmd_info in enumerate(commands, 1):
            logger.info(f"[{i}/{len(commands)}] Testing: {cmd_info['description']}")
            logger.debug(f"Command: {cmd_info['command']}")
            logger.debug(f"Source: {cmd_info['source']}")

            success = self._execute_command(cmd_info)
            if not success:
                self.failed_commands.append(cmd_info)
                logger.warning(f"Command failed: {cmd_info['description']}")
            else:
                logger.info(f"Command succeeded: {cmd_info['description']}")

    def _execute_command(self, cmd_info: Dict) -> bool:
        """
        Execute a single command and capture results.

        Args:
            cmd_info: Command dictionary with metadata

        Returns:
            True if command succeeded, False otherwise
        """
        try:
            # Record start time
            start_time = datetime.datetime.now()

            result = subprocess.run(
                cmd_info['command'],
                shell=True,
                cwd=self.project_path,
                capture_output=True,
                text=True,
                timeout=self.timeout
            )

            # Record execution time
            end_time = datetime.datetime.now()
            cmd_info['execution_time'] = (end_time - start_time).total_seconds()

            if result.returncode == 0:
                logger.debug(f"Command succeeded in {cmd_info['execution_time']:.2f}s")
                return True
            else:
                cmd_info['error'] = result.stderr or result.stdout
                cmd_info['return_code'] = result.returncode
                logger.error(f"Command failed with code {result.returncode}")
                return False

        except subprocess.TimeoutExpired:
            cmd_info['error'] = f"Command timed out after {self.timeout} seconds"
            cmd_info['return_code'] = -1
            logger.error(f"Command timed out after {self.timeout}s")
            return False
        except Exception as e:
            cmd_info['error'] = str(e)
            cmd_info['return_code'] = -2
            logger.error(f"Command execution failed: {e}")
            return False

    def generate_output_file(self, output_path: str, format_type: str = 'markdown') -> None:
        """
        Generate output file with failed commands.

        Args:
            output_path: Path to output file
            format_type: Output format ('markdown', 'json', 'text')
        """
        if not self.failed_commands:
            logger.info("No failed commands to report")
            return

        output_file = Path(output_path)

        if format_type == 'markdown':
            content = self._generate_markdown_report()
        elif format_type == 'json':
            content = self._generate_json_report()
        elif format_type == 'text':
            content = self._generate_text_report()
        else:
            raise ValueError(f"Unsupported format: {format_type}")

        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(content)

        logger.info(f"Generated {format_type} report: {output_file}")

    def _generate_markdown_report(self) -> str:
        """Generate markdown report for failed commands."""
        lines = [
            "# TODO - Failed Project Commands",
            "",
            f"Automatically generated by TodoMD",
            f"Date: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"Project: {self.project_path}",
            "",
            f"Found **{len(self.failed_commands)}** commands that require fixing:",
            ""
        ]

        for i, cmd_info in enumerate(self.failed_commands, 1):
            lines.extend([
                f"## Task {i}: {cmd_info['description']}",
                "",
                f"**Source:** `{cmd_info['source']}`",
                f"**Return Code:** {cmd_info.get('return_code', 'N/A')}",
            ])

            if 'execution_time' in cmd_info:
                lines.append(f"**Execution Time:** {cmd_info['execution_time']:.2f}s")

            lines.extend([
                "",
                "### Command to fix:",
                "```bash",
                cmd_info['command'],
                "```",
                "",
                "### Error:",
                "```",
                cmd_info.get('error', 'No error information available'),
                "```",
                "",
                "### Suggested Actions:",
                "- [ ] Check if all dependencies are installed",
                "- [ ] Verify command syntax and arguments",
                "- [ ] Check file permissions and access rights",
                "- [ ] Review error logs for specific issues",
                "- [ ] Ensure required tools/binaries are available",
                "",
                "---",
                ""
            ])

        return "\n".join(lines)

    def _generate_json_report(self) -> str:
        """Generate JSON report for failed commands."""
        report = {
            "generated_at": datetime.datetime.now().isoformat(),
            "project_path": str(self.project_path),
            "total_failed": len(self.failed_commands),
            "failed_commands": self.failed_commands
        }
        return json.dumps(report, indent=2)

    def _generate_text_report(self) -> str:
        """Generate plain text report for failed commands."""
        lines = [
            "TODO - Failed Project Commands",
            "=" * 40,
            f"Generated: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"Project: {self.project_path}",
            f"Failed Commands: {len(self.failed_commands)}",
            ""
        ]

        for i, cmd_info in enumerate(self.failed_commands, 1):
            lines.extend([
                f"Task {i}: {cmd_info['description']}",
                f"Source: {cmd_info['source']}",
                f"Command: {cmd_info['command']}",
                f"Error: {cmd_info.get('error', 'N/A')}",
                f"Return Code: {cmd_info.get('return_code', 'N/A')}",
                "-" * 40,
                ""
            ])

        return "\n".join(lines)

    # Parser methods for different file types

    def _parse_package_json(self, file_path: Path) -> List[Dict]:
        """Parse package.json for npm scripts."""
        commands = []
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            scripts = data.get('scripts', {})
            for script_name, script_command in scripts.items():
                commands.append({
                    'command': f'npm run {script_name}',
                    'description': f'NPM script: {script_name}',
                    'source': str(file_path.relative_to(self.project_path)),
                    'type': 'npm_script',
                    'original_command': script_command
                })
        except Exception as e:
            logger.error(f"Error parsing {file_path}: {e}")

        return commands

    def _parse_makefile(self, file_path: Path) -> List[Dict]:
        """Parse Makefile for targets."""
        commands = []
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Find Makefile targets
            targets = re.findall(r'^([a-zA-Z][a-zA-Z0-9_-]*)\s*:', content, re.MULTILINE)

            # Filter out special targets
            special_targets = {'.PHONY', 'PHONY', '.DEFAULT', '.SUFFIXES', '.PRECIOUS', '.INTERMEDIATE'}

            for target in targets:
                if target not in special_targets:
                    commands.append({
                        'command': f'make {target}',
                        'description': f'Make target: {target}',
                        'source': str(file_path.relative_to(self.project_path)),
                        'type': 'make_target'
                    })
        except Exception as e:
            logger.error(f"Error parsing {file_path}: {e}")

        return commands

    def _parse_pyproject_toml(self, file_path: Path) -> List[Dict]:
        """Parse pyproject.toml for Python project commands."""
        commands = []
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = toml.load(f)

            # Poetry scripts
            poetry_scripts = data.get('tool', {}).get('poetry', {}).get('scripts', {})
            for script_name in poetry_scripts:
                commands.append({
                    'command': f'poetry run {script_name}',
                    'description': f'Poetry script: {script_name}',
                    'source': str(file_path.relative_to(self.project_path)),
                    'type': 'poetry_script'
                })

            # Check for pytest configuration
            if 'tool' in data and 'pytest' in data['tool']:
                commands.append({
                    'command': 'python -m pytest',
                    'description': 'Run pytest tests',
                    'source': str(file_path.relative_to(self.project_path)),
                    'type': 'pytest'
                })

            # Check for other tools
            tools = data.get('tool', {})
            if 'black' in tools:
                commands.append({
                    'command': 'black --check .',
                    'description': 'Check code formatting with Black',
                    'source': str(file_path.relative_to(self.project_path)),
                    'type': 'black'
                })

            if 'isort' in tools:
                commands.append({
                    'command': 'isort --check-only .',
                    'description': 'Check import sorting with isort',
                    'source': str(file_path.relative_to(self.project_path)),
                    'type': 'isort'
                })

        except Exception as e:
            logger.error(f"Error parsing {file_path}: {e}")

        return commands

    def _parse_tox_ini(self, file_path: Path) -> List[Dict]:
        """Parse tox.ini for test environments."""
        commands = []
        try:
            config = configparser.ConfigParser()
            config.read(file_path)

            if 'tox' in config:
                envlist = config.get('tox', 'envlist', fallback='')
                envs = [env.strip() for env in envlist.split(',') if env.strip()]

                for env in envs:
                    commands.append({
                        'command': f'tox -e {env}',
                        'description': f'Tox environment: {env}',
                        'source': str(file_path.relative_to(self.project_path)),
                        'type': 'tox_env'
                    })

            # Add general tox command
            commands.append({
                'command': 'tox',
                'description': 'Run all tox environments',
                'source': str(file_path.relative_to(self.project_path)),
                'type': 'tox'
            })

        except Exception as e:
            logger.error(f"Error parsing {file_path}: {e}")

        return commands

    # Simplified versions of other parsers
    def _parse_pytest_ini(self, file_path: Path) -> List[Dict]:
        """Parse pytest.ini configuration."""
        return [{
            'command': 'python -m pytest',
            'description': 'Run pytest tests',
            'source': str(file_path.relative_to(self.project_path)),
            'type': 'pytest'
        }]

    def _check_npm_install(self, file_path: Path) -> List[Dict]:
        """Check npm package installation."""
        return [{
            'command': 'npm install',
            'description': 'Install npm dependencies',
            'source': str(file_path.relative_to(self.project_path)),
            'type': 'npm_install'
        }]

    def _check_yarn_install(self, file_path: Path) -> List[Dict]:
        """Check yarn package installation."""
        return [{
            'command': 'yarn install',
            'description': 'Install yarn dependencies',
            'source': str(file_path.relative_to(self.project_path)),
            'type': 'yarn_install'
        }]

    def _check_pnpm_install(self, file_path: Path) -> List[Dict]:
        """Check pnpm package installation."""
        return [{
            'command': 'pnpm install',
            'description': 'Install pnpm dependencies',
            'source': str(file_path.relative_to(self.project_path)),
            'type': 'pnpm_install'
        }]

    def _check_pip_install(self, file_path: Path) -> List[Dict]:
        """Check pip package installation."""
        return [{
            'command': f'pip install -r {file_path.name}',
            'description': f'Install pip dependencies from {file_path.name}',
            'source': str(file_path.relative_to(self.project_path)),
            'type': 'pip_install'
        }]

    def _parse_setup_py(self, file_path: Path) -> List[Dict]:
        """Parse setup.py for Python package commands."""
        commands = []
        commands.append({
            'command': 'python setup.py install',
            'description': 'Install Python package',
            'source': str(file_path.relative_to(self.project_path)),
            'type': 'setup_install'
        })
        commands.append({
            'command': 'python setup.py test',
            'description': 'Run package tests',
            'source': str(file_path.relative_to(self.project_path)),
            'type': 'setup_test'
        })
        return commands

    def _parse_pipfile(self, file_path: Path) -> List[Dict]:
        """Parse Pipfile for pipenv commands."""
        return [{
            'command': 'pipenv install',
            'description': 'Install Pipenv dependencies',
            'source': str(file_path.relative_to(self.project_path)),
            'type': 'pipenv_install'
        }]

    def _check_poetry_install(self, file_path: Path) -> List[Dict]:
        """Check poetry installation."""
        return [{
            'command': 'poetry install',
            'description': 'Install Poetry dependencies',
            'source': str(file_path.relative_to(self.project_path)),
            'type': 'poetry_install'
        }]

    def _parse_coverage_config(self, file_path: Path) -> List[Dict]:
        """Parse coverage configuration."""
        return [{
            'command': 'coverage run -m pytest',
            'description': 'Run coverage analysis',
            'source': str(file_path.relative_to(self.project_path)),
            'type': 'coverage'
        }]

    def _parse_cmake(self, file_path: Path) -> List[Dict]:
        """Parse CMakeLists.txt for CMake commands."""
        commands = []
        commands.append({
            'command': 'mkdir -p build && cd build && cmake ..',
            'description': 'Configure CMake build',
            'source': str(file_path.relative_to(self.project_path)),
            'type': 'cmake_configure'
        })
        commands.append({
            'command': 'cd build && make',
            'description': 'Build with CMake',
            'source': str(file_path.relative_to(self.project_path)),
            'type': 'cmake_build'
        })
        return commands

    def _parse_gradle(self, file_path: Path) -> List[Dict]:
        """Parse Gradle build file."""
        commands = []
        commands.append({
            'command': './gradlew build',
            'description': 'Gradle build',
            'source': str(file_path.relative_to(self.project_path)),
            'type': 'gradle_build'
        })
        commands.append({
            'command': './gradlew test',
            'description': 'Gradle test',
            'source': str(file_path.relative_to(self.project_path)),
            'type': 'gradle_test'
        })
        return commands

    def _parse_maven(self, file_path: Path) -> List[Dict]:
        """Parse Maven POM file."""
        commands = []
        commands.append({
            'command': 'mvn compile',
            'description': 'Maven compile',
            'source': str(file_path.relative_to(self.project_path)),
            'type': 'maven_compile'
        })
        commands.append({
            'command': 'mvn test',
            'description': 'Maven test',
            'source': str(file_path.relative_to(self.project_path)),
            'type': 'maven_test'
        })
        return commands

    def _parse_dockerfile(self, file_path: Path) -> List[Dict]:
        """Parse Dockerfile for build commands."""
        return [{
            'command': f'docker build -t {self.project_path.name.lower()} .',
            'description': 'Build Docker image',
            'source': str(file_path.relative_to(self.project_path)),
            'type': 'docker_build'
        }]

    def _parse_docker_compose(self, file_path: Path) -> List[Dict]:
        """Parse docker-compose file."""
        commands = []
        commands.append({
            'command': 'docker-compose up --build',
            'description': 'Docker Compose up with build',
            'source': str(file_path.relative_to(self.project_path)),
            'type': 'docker_compose_up'
        })
        commands.append({
            'command': 'docker-compose down',
            'description': 'Docker Compose down',
            'source': str(file_path.relative_to(self.project_path)),
            'type': 'docker_compose_down'
        })
        return commands

    def _parse_github_actions(self, file_path: Path) -> List[Dict]:
        """Parse GitHub Actions workflow."""
        # Note: These are informational only as they can't be run locally
        return [{
            'command': f'# GitHub Actions workflow: {file_path.name}',
            'description': f'GitHub Actions workflow: {file_path.stem}',
            'source': str(file_path.relative_to(self.project_path)),
            'type': 'github_actions'
        }]

    def _parse_gitlab_ci(self, file_path: Path) -> List[Dict]:
        """Parse GitLab CI configuration."""
        return [{
            'command': '# GitLab CI pipeline',
            'description': 'GitLab CI pipeline configuration',
            'source': str(file_path.relative_to(self.project_path)),
            'type': 'gitlab_ci'
        }]

    def _parse_jenkinsfile(self, file_path: Path) -> List[Dict]:
        """Parse Jenkins pipeline file."""
        return [{
            'command': '# Jenkins pipeline',
            'description': 'Jenkins pipeline configuration',
            'source': str(file_path.relative_to(self.project_path)),
            'type': 'jenkins'
        }]

    def _parse_composer_json(self, file_path: Path) -> List[Dict]:
        """Parse Composer configuration for PHP."""
        commands = []
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # Composer install
            commands.append({
                'command': 'composer install',
                'description': 'Install Composer dependencies',
                'source': str(file_path.relative_to(self.project_path)),
                'type': 'composer_install'
            })

            # Composer scripts
            scripts = data.get('scripts', {})
            for script_name in scripts:
                commands.append({
                    'command': f'composer run-script {script_name}',
                    'description': f'Composer script: {script_name}',
                    'source': str(file_path.relative_to(self.project_path)),
                    'type': 'composer_script'
                })
        except Exception as e:
            logger.error(f"Error parsing {file_path}: {e}")

        return commands

    def _parse_gemfile(self, file_path: Path) -> List[Dict]:
        """Parse Gemfile for Ruby projects."""
        return [{
            'command': 'bundle install',
            'description': 'Install Ruby gems',
            'source': str(file_path.relative_to(self.project_path)),
            'type': 'bundle_install'
        }]

    def _parse_cargo_toml(self, file_path: Path) -> List[Dict]:
        """Parse Cargo.toml for Rust projects."""
        commands = []
        commands.append({
            'command': 'cargo build',
            'description': 'Build Rust project',
            'source': str(file_path.relative_to(self.project_path)),
            'type': 'cargo_build'
        })
        commands.append({
            'command': 'cargo test',
            'description': 'Run Rust tests',
            'source': str(file_path.relative_to(self.project_path)),
            'type': 'cargo_test'
        })
        commands.append({
            'command': 'cargo check',
            'description': 'Check Rust code',
            'source': str(file_path.relative_to(self.project_path)),
            'type': 'cargo_check'
        })
        return commands

    def _check_go_commands(self, file_path: Path) -> List[Dict]:
        """Parse Go module file."""
        commands = []
        commands.append({
            'command': 'go build',
            'description': 'Build Go project',
            'source': str(file_path.relative_to(self.project_path)),
            'type': 'go_build'
        })
        commands.append({
            'command': 'go test',
            'description': 'Run Go tests',
            'source': str(file_path.relative_to(self.project_path)),
            'type': 'go_test'
        })
        commands.append({
            'command': 'go mod tidy',
            'description': 'Clean up Go modules',
            'source': str(file_path.relative_to(self.project_path)),
            'type': 'go_mod_tidy'
        })
        return commands

    def get_statistics(self) -> Dict[str, Any]:
        """
        Get statistics about the detection and testing process.

        Returns:
            Dictionary with various statistics
        """
        total_commands = len(self.failed_commands) + self.get_successful_count()
        success_rate = 0 if total_commands == 0 else (self.get_successful_count() / total_commands) * 100

        # Group failed commands by type
        failure_types = {}
        for cmd in self.failed_commands:
            cmd_type = cmd.get('type', 'unknown')
            failure_types[cmd_type] = failure_types.get(cmd_type, 0) + 1

        # Group failed commands by source
        failure_sources = {}
        for cmd in self.failed_commands:
            source = cmd.get('source', 'unknown')
            failure_sources[source] = failure_sources.get(source, 0) + 1

        return {
            'total_commands': total_commands,
            'successful_commands': self.get_successful_count(),
            'failed_commands': len(self.failed_commands),
            'success_rate': success_rate,
            'failure_rate': 100 - success_rate,
            'failure_by_type': failure_types,
            'failure_by_source': failure_sources,
            'project_path': str(self.project_path),
            'timeout_setting': self.timeout
        }

    def get_successful_count(self) -> int:
        """Calculate number of successful commands (if tracking was implemented)."""
        # This would need to be tracked during execution
        # For now, we'll return 0 as we only track failures
        return 0

    def print_summary(self) -> None:
        """Print a summary of the detection and testing results."""
        stats = self.get_statistics()

        print(f"\n{'=' * 50}")
        print("DETECTION AND TESTING SUMMARY")
        print(f"{'=' * 50}")
        print(f"Project: {stats['project_path']}")
        print(f"Total Commands: {stats['total_commands']}")
        print(f"✅ Successful: {stats['successful_commands']}")
        print(f"❌ Failed: {stats['failed_commands']}")

        if stats['total_commands'] > 0:
            print(f"📊 Success Rate: {stats['success_rate']:.1f}%")

        if stats['failure_by_type']:
            print(f"\nFailures by Type:")
            for cmd_type, count in stats['failure_by_type'].items():
                print(f"  - {cmd_type}: {count}")

        if stats['failure_by_source']:
            print(f"\nFailures by Source:")
            for source, count in stats['failure_by_source'].items():
                print(f"  - {source}: {count}")

    def export_results(self, output_path: str, include_successful: bool = False) -> None:
        """
        Export detailed results to a JSON file.

        Args:
            output_path: Path to output JSON file
            include_successful: Whether to include successful commands (if tracked)
        """
        results = {
            'metadata': {
                'generated_at': datetime.datetime.now().isoformat(),
                'domd_version': '0.1.0',  # Should be imported from __init__.py
                'project_path': str(self.project_path),
                'timeout': self.timeout,
                'exclude_patterns': self.exclude_patterns,
                'include_patterns': self.include_patterns
            },
            'statistics': self.get_statistics(),
            'failed_commands': self.failed_commands
        }

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, default=str)

        logger.info(f"Exported detailed results to {output_path}")

    def generate_todo_file(self, output_path: str = "TODO.md") -> None:
        """
        Legacy method for backward compatibility.
        Calls generate_output_file with markdown format.
        """
        self.generate_output_file(output_path, 'markdown')


def main():
    """
    Standalone function for running the detector.
    This allows the detector to be used independently of the CLI.
    """
    import argparse

    parser = argparse.ArgumentParser(description='Project Command Detector')
    parser.add_argument('--path', '-p', default='.', help='Project path')
    parser.add_argument('--dry-run', '-d', action='store_true', help='Preview mode')
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')
    parser.add_argument('--timeout', type=int, default=60, help='Command timeout')
    parser.add_argument('--output', '-o', default='TODO.md', help='Output file')
    parser.add_argument('--format', choices=['markdown', 'json', 'text'],
                        default='markdown', help='Output format')

    args = parser.parse_args()

    # Setup logging
    level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(level=level, format='%(levelname)s: %(message)s')

    # Initialize detector
    detector = ProjectCommandDetector(
        project_path=args.path,
        timeout=args.timeout
    )

    # Scan project
    commands = detector.scan_project()

    if not commands:
        print("No commands found to test.")
        return 0

    print(f"Found {len(commands)} commands")

    if args.dry_run:
        print("\nDRY RUN - Commands found:")
        for i, cmd in enumerate(commands, 1):
            print(f"{i:3d}. {cmd['description']}")
            print(f"     Command: {cmd['command']}")
            print(f"     Source:  {cmd['source']}")
        return 0

    # Test commands
    detector.test_commands(commands)

    # Generate output
    detector.generate_output_file(args.output, args.format)

    # Print summary
    detector.print_summary()

    # Return appropriate exit code
    return 1 if detector.failed_commands else 0


if __name__ == "__main__":
    sys.exit(main())
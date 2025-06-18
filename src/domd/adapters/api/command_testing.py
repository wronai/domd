"""
REST API endpoints for command testing functionality.
"""

from pathlib import Path
from typing import Dict, List, Optional

from flask import jsonify, request
from werkzeug.exceptions import BadRequest, NotFound


def register_command_testing_routes(api, command_handler):
    """Register command testing API routes.

    Args:
        api: The Flask API instance
        command_handler: The CommandHandler instance
    """

    @api.app.route("/api/commands/validate", methods=["POST"])
    @api.require_auth()
    def validate_commands():
        """
        Validate a list of commands and optionally test them in Docker.

        Request body:
        {
            "commands": ["command1", "command2", ...],
            "test_in_docker": true/false,
            "update_doignore": true/false
        }

        Returns:
            JSON response with validation results
        """
        data = request.get_json()

        if not data or "commands" not in data:
            raise BadRequest("Missing 'commands' in request body")

        commands = data.get("commands", [])
        test_in_docker = data.get("test_in_docker", False)
        update_doignore = data.get("update_doignore", False)

        if not isinstance(commands, list) or not all(
            isinstance(cmd, str) for cmd in commands
        ):
            raise BadRequest("'commands' must be a list of strings")

        # Validate commands
        results = command_handler.validate_commands(
            commands, test_in_docker=test_in_docker
        )

        # Update .doignore if requested and testing in Docker
        updated_ignore_count = 0
        if test_in_docker and update_doignore:
            failed_commands = [
                cmd
                for cmd, (is_valid, _) in results.items()
                if not is_valid and cmd in command_handler.invalid_commands
            ]
            updated_ignore_count = command_handler.update_doignore(failed_commands)

        # Prepare response
        response = {
            "validated_commands": len(results),
            "valid_commands": len(
                [1 for _, (is_valid, _) in results.items() if is_valid]
            ),
            "invalid_commands": len(command_handler.invalid_commands),
            "untested_commands": len(command_handler.untested_commands),
            "updated_ignore_count": updated_ignore_count,
            "results": [
                {
                    "command": cmd,
                    "is_valid": is_valid,
                    "reason": reason,
                    "tested_in_docker": test_in_docker
                    and is_valid
                    and cmd not in command_handler.untested_commands,
                }
                for cmd, (is_valid, reason) in results.items()
            ],
        }

        return api._create_response(response)

    @api.app.route("/api/commands/test-docker", methods=["POST"])
    @api.require_auth()
    def test_commands_in_docker():
        """
        Test commands in Docker containers.

        Request body:
        {
            "commands": ["command1", "command2", ...],
            "update_doignore": true/false
        }

        Returns:
            JSON response with test results
        """
        if (
            not command_handler.enable_docker_testing
            or not command_handler.docker_tester
        ):
            return api._create_response(
                {"error": "Docker testing is not available"}, status=503
            )

        data = request.get_json()

        if not data or "commands" not in data:
            raise BadRequest("Missing 'commands' in request body")

        commands = data.get("commands", [])
        update_doignore = data.get("update_doignore", False)

        if not isinstance(commands, list) or not all(
            isinstance(cmd, str) for cmd in commands
        ):
            raise BadRequest("'commands' must be a list of strings")

        # Test commands in Docker
        results = command_handler.docker_tester.test_commands_in_docker(commands)

        # Update .doignore if requested
        updated_ignore_count = 0
        if update_doignore:
            failed_commands = [
                cmd for cmd, (success, _) in results.items() if not success
            ]
            updated_ignore_count = command_handler.update_doignore(failed_commands)

        # Prepare response
        response = {
            "tested_commands": len(results),
            "successful_commands": len(
                [1 for _, (success, _) in results.items() if success]
            ),
            "failed_commands": len(
                [1 for _, (success, _) in results.items() if not success]
            ),
            "updated_ignore_count": updated_ignore_count,
            "results": [
                {"command": cmd, "success": success, "output": output}
                for cmd, (success, output) in results.items()
            ],
        }

        return api._create_response(response)

    @api.app.route("/api/commands/ignore", methods=["POST"])
    @api.require_auth(roles=["admin"])
    def add_to_doignore():
        """
        Add commands to .doignore file.

        Request body:
        {
            "commands": ["command1", "command2", ...],
            "comment": "Optional comment"
        }

        Returns:
            JSON response with operation result
        """
        data = request.get_json()

        if not data or "commands" not in data:
            raise BadRequest("Missing 'commands' in request body")

        commands = data.get("commands", [])
        comment = data.get("comment", "")

        if not isinstance(commands, list) or not all(
            isinstance(cmd, str) for cmd in commands
        ):
            raise BadRequest("'commands' must be a list of strings")

        # Add commands to .doignore
        added_count = command_handler.update_doignore(commands)

        # Add comment if provided
        if comment and added_count > 0:
            try:
                with open(command_handler.doignore_path, "a") as f:
                    f.write(f"\n# {comment}\n")
            except Exception as e:
                logger.warning(f"Failed to add comment to .doignore: {e}")

        return api._create_response(
            {
                "added_commands": added_count,
                "total_ignored_commands": len(command_handler.invalid_commands),
            }
        )

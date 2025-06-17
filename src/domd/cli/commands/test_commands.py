"""CLI command for testing commands in Docker."""

import logging
from pathlib import Path
from typing import List, Optional

import click
from rich.console import Console
from rich.table import Table

from domd.core.command_detection.handlers.command_handler import CommandHandler
from domd.core.command_execution.command_runner import CommandRunner

logger = logging.getLogger(__name__)
console = Console()

@click.command()
@click.argument("commands", nargs=-1, required=False)
@click.option(
    "--file",
    "-f",
    type=click.Path(exists=True, dir_okay=False, path_type=Path),
    help="File containing commands to test (one per line)",
)
@click.option(
    "--update-doignore",
    is_flag=True,
    help="Update .doignore with commands that fail in Docker",
)
@click.option(
    "--dodocker",
    type=click.Path(exists=True, dir_okay=False, path_type=Path),
    default=".dodocker",
    help="Path to .dodocker configuration file",
)
@click.option(
    "--doignore",
    type=click.Path(dir_okay=False, path_type=Path),
    default=".doignore",
    help="Path to .doignore file",
)
@click.option(
    "--no-docker",
    is_flag=True,
    help="Skip Docker testing and only validate commands",
)
@click.pass_context
def test_commands(
    ctx: click.Context,
    commands: List[str],
    file: Optional[Path],
    update_doignore: bool,
    dodocker: Path,
    doignore: Path,
    no_docker: bool,
) -> None:
    """Test commands in Docker and optionally update .doignore.
    
    This command validates commands and can test them in Docker containers.
    If more than half of commands are invalid, it will test them in Docker
    and optionally update .doignore with commands that fail.
    
    Commands can be provided as arguments or in a file (one per line).
    """
    # Load commands from file if provided
    all_commands = list(commands)
    if file:
        try:
            with open(file, 'r') as f:
                all_commands.extend(line.strip() for line in f if line.strip())
        except Exception as e:
            console.print(f"[red]Error reading commands from file: {e}[/red]")
            ctx.exit(1)
    
    if not all_commands:
        console.print("[yellow]No commands provided to test[/yellow]")
        return
    
    # Initialize command handler with Docker testing
    command_runner = CommandRunner()
    handler = CommandHandler(
        project_path=Path.cwd(),
        command_runner=command_runner,
        enable_docker_testing=not no_docker,
        dodocker_path=dodocker,
        doignore_path=doignore,
    )
    
    # Validate and test commands
    console.print(f"[bold]Testing {len(all_commands)} commands...[/bold]")
    results = handler.validate_commands(
        all_commands, 
        test_in_docker=not no_docker and update_doignore
    )
    
    # Display results
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Command", style="dim", width=60, overflow="fold")
    table.add_column("Status", justify="right")
    table.add_column("Details", width=40, overflow="fold")
    
    for cmd, (is_valid, reason) in results.items():
        if is_valid:
            status = "[green]VALID[/green]"
            details = ""
        else:
            status = "[red]INVALID[/red]"
            details = f"[yellow]{reason}[/yellow]"
        
        # Truncate long commands for display
        display_cmd = cmd if len(cmd) < 60 else f"{cmd[:57]}..."
        table.add_row(display_cmd, status, details)
    
    console.print(table)
    
    # Show summary
    valid_count = sum(1 for _, (is_valid, _) in results.items() if is_valid)
    invalid_count = len(results) - valid_count
    
    console.print(f"\n[bold]Summary:[/bold]")
    console.print(f"  • Total commands: {len(results)}")
    console.print(f"  • Valid commands: [green]{valid_count}[/green]")
    console.print(f"  • Invalid commands: [red]{invalid_count}[/red]")
    
    if handler.untested_commands and not no_docker:
        console.print("\n[yellow]Note: Some valid commands were not tested in Docker.[/yellow]")
        console.print("  Run with --update-doignore to test valid commands in Docker.")
    
    if update_doignore and not no_docker and invalid_count > 0:
        console.print("\n[green]✓[/green] [bold]Updated .doignore with failing commands[/bold]")
    
    # Exit with non-zero code if any commands are invalid
    if invalid_count > 0:
        ctx.exit(1)

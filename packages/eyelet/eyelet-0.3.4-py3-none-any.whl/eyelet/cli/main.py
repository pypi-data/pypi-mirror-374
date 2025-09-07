"""Main CLI entry point for Eyelet"""

from pathlib import Path

import click
from rich.console import Console
from rich.panel import Panel
from rich.text import Text

from eyelet import __version__
from eyelet.cli import (
    completion,
    configure,
    discover,
    doctor,
    execute,
    logs,
    query,
    recall,
    template,
    validate,
)
from eyelet.tui.app import launch_tui

console = Console()

CONTEXT_SETTINGS = {
    "help_option_names": ["-h", "--help"],
    "max_content_width": 120,
}


class EyeletCLI(click.Group):
    """Custom CLI class with enhanced help formatting"""

    def format_help(self, ctx, formatter):
        # Custom header
        console.print(
            Panel.fit(
                Text.from_markup(
                    "[bold cyan]⚓ Eyelet[/bold cyan] - Hook Orchestration for AI Agents\n"
                    "[dim]All hands to the eyelet![/dim]"
                ),
                border_style="cyan",
            )
        )

        # Version info
        console.print(f"[dim]Version: {__version__}[/dim]\n")

        # Description
        console.print("[bold]Description:[/bold]")
        console.print(
            "  Eyelet provides comprehensive management, templating, and execution"
        )
        console.print(
            "  handling for AI agent hooks. Like a ship's eyelet that controls the"
        )
        console.print(
            "  sails, Eyelet controls and orchestrates your AI agent's behavior.\n"
        )

        # Usage
        console.print("[bold]Usage:[/bold]")
        console.print("  eyelet [OPTIONS] COMMAND [ARGS]...")
        console.print("  eyelet              # Launch interactive TUI\n")

        # Common commands
        console.print("[bold]Common Commands:[/bold]")
        commands = [
            ("configure install-all", "Install universal logging (recommended!)"),
            ("configure", "Manage hook configuration"),
            ("template", "Work with hook templates"),
            ("logs", "View execution logs"),
            ("execute", "Run as hook endpoint"),
            ("discover", "Discover available hooks"),
        ]
        for cmd, desc in commands:
            console.print(f"  [cyan]{cmd:20}[/cyan] {desc}")

        console.print("\n[bold]Options:[/bold]")
        console.print("  [cyan]-h, --help[/cyan]     Show this help message")
        console.print("  [cyan]--version[/cyan]      Show version information")
        console.print("  [cyan]--config-dir[/cyan]   Set configuration directory\n")

        console.print("[bold]Examples:[/bold]")
        console.print("  [dim]# Configure hooks for current project[/dim]")
        console.print("  eyelet configure add\n")
        console.print("  [dim]# Install a security template[/dim]")
        console.print("  eyelet template install bash-validator\n")
        console.print("  [dim]# View recent hook executions[/dim]")
        console.print("  eyelet logs --tail 20\n")

        console.print("[bold]Shell Completion:[/bold]")
        console.print("  [dim]# Enable tab completion for your shell[/dim]")
        console.print("  eyelet completion install\n")

        console.print(
            "[dim]Run 'eyelet COMMAND --help' for more information on a command.[/dim]"
        )


@click.group(
    cls=EyeletCLI, invoke_without_command=True, context_settings=CONTEXT_SETTINGS
)
@click.version_option(version=__version__, prog_name="eyelet")
@click.option(
    "--config-dir", type=Path, help="Configuration directory (default: current dir)"
)
@click.pass_context
def cli(ctx, config_dir):
    """
    ⚓ Eyelet - Hook Orchestration for AI Agents

    All hands to the eyelet!

    Eyelet provides comprehensive management, templating, and execution
    handling for AI agent hooks. Run without arguments to launch the TUI.
    """
    ctx.ensure_object(dict)
    ctx.obj["config_dir"] = config_dir or Path.cwd()

    # If no command provided, launch TUI
    if ctx.invoked_subcommand is None:
        console.print("[bold cyan]All hands to the eyelet![/bold cyan]")
        launch_tui()


@cli.command()
@click.pass_context
def status(ctx):
    """Show current configuration and status"""
    config_dir = ctx.obj["config_dir"]
    console.print(f"[bold]Configuration Directory:[/bold] {config_dir}")

    # Check for Claude settings
    settings_path = config_dir / ".claude" / "settings.json"
    if settings_path.exists():
        console.print("[green]✓[/green] Claude settings found")
        # TODO: Load and display hook count
    else:
        console.print("[yellow]![/yellow] No Claude settings found")

    # Check for workflows
    workflow_dir = config_dir / "workflows"
    if workflow_dir.exists():
        workflow_count = len(list(workflow_dir.glob("**/*.yaml")))
        console.print(f"[green]✓[/green] {workflow_count} workflows found")
    else:
        console.print("[yellow]![/yellow] No workflows directory")


@cli.command()
def tui():
    """Launch the Textual TUI - All hands to the eyelet!"""
    console.print("[bold cyan]All hands to the eyelet![/bold cyan]")
    launch_tui()


# Register subcommands
cli.add_command(configure.configure)
cli.add_command(template.template)
cli.add_command(execute.execute)
cli.add_command(logs.logs)
cli.add_command(query.query)
cli.add_command(recall.recall)
cli.add_command(discover.discover)
cli.add_command(completion.completion)
cli.add_command(validate.validate)
cli.add_command(doctor.doctor)


@cli.command()
@click.pass_context
def help(ctx):
    """Show this help message - Consult the charts!"""
    ctx.parent.get_help()


# Enable shell completion
def get_completion():
    """Enable Click's built-in completion support"""
    try:
        import click_completion

        click_completion.init()
    except ImportError:
        pass  # Optional dependency


if __name__ == "__main__":
    get_completion()
    cli()

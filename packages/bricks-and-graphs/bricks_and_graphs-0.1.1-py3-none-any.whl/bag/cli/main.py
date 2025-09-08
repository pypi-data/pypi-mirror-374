"""Main CLI entry point for bricks-and-graphs."""

# mypy: ignore-errors

from pathlib import Path

import click
from rich.console import Console
from rich.logging import RichHandler

from bag import __version__

console = Console()


@click.command(
    name="bricks-and-graphs",
    context_settings={"help_option_names": ["-h", "--help"]},
)
@click.option(
    "--config",
    "-c",
    type=click.Path(exists=True, path_type=Path),
    help="Configuration file path",
)
@click.option(
    "--verbose",
    "-v",
    is_flag=True,
    help="Enable verbose logging",
)
@click.version_option(version=__version__, prog_name="bricks-and-graphs")
def main(config: Path | None, verbose: bool) -> None:
    """Bricks and Graphs - An agentic framework CLI.

    This CLI allows you to run agentic graphs and manage your decision trees.
    """
    # Setup logging
    if verbose:
        import logging

        logging.basicConfig(
            level=logging.DEBUG,
            format="%(message)s",
            datefmt="[%X]",
            handlers=[RichHandler(console=console, rich_tracebacks=True)],
        )

    console.print(f"[bold green]Bricks and Graphs v{__version__}[/bold green]")

    if config:
        console.print(f"[blue]Using config file:[/blue] {config}")
    else:
        console.print("[yellow]No config file specified[/yellow]")

    # TODO: Implement actual CLI logic here
    console.print("[dim]CLI skeleton ready - implement your agentic graph logic![/dim]")


if __name__ == "__main__":
    main()

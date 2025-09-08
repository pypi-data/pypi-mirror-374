"""Tests for the CLI application."""

from click.testing import CliRunner

from bag.cli.main import main


def test_cli_help() -> None:
    """Test that CLI help is displayed correctly."""
    runner = CliRunner()
    result = runner.invoke(main, ["--help"])
    assert result.exit_code == 0
    assert "Bricks and Graphs" in result.output
    assert "--config" in result.output


def test_cli_version() -> None:
    """Test that CLI version is displayed correctly."""
    runner = CliRunner()
    result = runner.invoke(main, ["--version"])
    assert result.exit_code == 0
    assert "0.1.1" in result.output


def test_cli_basic_run() -> None:
    """Test basic CLI execution without arguments."""
    runner = CliRunner()
    result = runner.invoke(main)
    assert result.exit_code == 0
    assert "Bricks and Graphs v0.1.1" in result.output
    assert "No config file specified" in result.output

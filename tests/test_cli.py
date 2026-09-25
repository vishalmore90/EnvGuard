"""Tests for the EnvGuard CLI interface."""

from click.testing import CliRunner

from envguard.cli import cli


class TestCLIGroup:
    """Test the main CLI group and basic command registration."""

    def test_help_shows_description(self, cli_runner: CliRunner) -> None:
        """The --help flag should show the tool description."""
        result = cli_runner.invoke(cli, ["--help"])
        assert result.exit_code == 0
        assert "EnvGuard" in result.output
        assert "environment variables" in result.output.lower()

    def test_version_flag(self, cli_runner: CliRunner) -> None:
        """The --version flag should show the current version."""
        result = cli_runner.invoke(cli, ["--version"])
        assert result.exit_code == 0
        assert "0.1.0" in result.output

    def test_init_command_registered(self, cli_runner: CliRunner) -> None:
        """The 'init' subcommand should be registered."""
        result = cli_runner.invoke(cli, ["init", "--help"])
        assert result.exit_code == 0
        assert "schema" in result.output.lower() or "scan" in result.output.lower()

    def test_check_command_registered(self, cli_runner: CliRunner) -> None:
        """The 'check' subcommand should be registered."""
        result = cli_runner.invoke(cli, ["check", "--help"])
        assert result.exit_code == 0
        assert "validate" in result.output.lower() or "schema" in result.output.lower()

    def test_sync_command_registered(self, cli_runner: CliRunner) -> None:
        """The 'sync' subcommand should be registered."""
        result = cli_runner.invoke(cli, ["sync", "--help"])
        assert result.exit_code == 0

    def test_scan_command_registered(self, cli_runner: CliRunner) -> None:
        """The 'scan' subcommand should be registered."""
        result = cli_runner.invoke(cli, ["scan", "--help"])
        assert result.exit_code == 0
        assert "secret" in result.output.lower() or "detect" in result.output.lower()

    def test_unknown_command_fails(self, cli_runner: CliRunner) -> None:
        """An unknown subcommand should fail with a non-zero exit code."""
        result = cli_runner.invoke(cli, ["nonexistent"])
        assert result.exit_code != 0

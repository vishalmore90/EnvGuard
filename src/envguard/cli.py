"""EnvGuard CLI — main entry point."""

import click

from envguard import __version__


@click.group()
@click.version_option(version=__version__, prog_name="envguard")
def cli() -> None:
    """EnvGuard — Validate, audit, and document environment variables.

    Scan your project for environment variable usage, validate them against
    a schema, sync your .env.example, and detect hardcoded secrets.
    """


@cli.command()
@click.option("--path", default=".", help="Project root to scan.")
@click.option("--output", default=".envguard.yml", help="Output schema file path.")
@click.option(
    "--languages",
    default=None,
    help="Comma-separated languages to scan (default: auto-detect).",
)
@click.option("--force", is_flag=True, help="Overwrite existing schema file.")
@click.option(
    "--format",
    "output_format",
    type=click.Choice(["rich", "json"]),
    default="rich",
    help="Output format.",
)
@click.option("-v", "--verbose", is_flag=True, help="Show detailed scanning progress.")
def init(
    path: str,
    output: str,
    languages: str | None,
    force: bool,
    output_format: str,
    verbose: bool,
) -> None:
    """Scan project and generate .envguard.yml schema."""
    click.echo("envguard init: not yet implemented")
    raise SystemExit(1)


@cli.command()
@click.option("--schema", default=".envguard.yml", help="Schema file path.")
@click.option("--env-file", default=None, help=".env file to load for validation.")
@click.option("--ci", is_flag=True, help="Strict mode: treat warnings as errors.")
@click.option(
    "--format",
    "output_format",
    type=click.Choice(["rich", "json"]),
    default="rich",
    help="Output format.",
)
@click.option(
    "-v", "--verbose", is_flag=True, help="Show all variables, not just problems."
)
def check(
    schema: str,
    env_file: str | None,
    ci: bool,
    output_format: str,
    verbose: bool,
) -> None:
    """Validate current environment against schema."""
    click.echo("envguard check: not yet implemented")
    raise SystemExit(1)


@cli.command()
@click.option("--schema", default=".envguard.yml", help="Schema file path.")
@click.option("--output", default=".env.example", help="Output .env.example file path.")
@click.option(
    "--force", is_flag=True, help="Overwrite existing file without confirmation."
)
@click.option(
    "--format",
    "output_format",
    type=click.Choice(["rich", "json"]),
    default="rich",
    help="Output format.",
)
def sync(
    schema: str,
    output: str,
    force: bool,
    output_format: str,
) -> None:
    """Generate or update .env.example from schema."""
    from envguard.commands.sync_cmd import execute_sync
    from envguard.reporters.base import BaseReporter
    from envguard.reporters.json_reporter import JsonReporter
    from envguard.reporters.rich_reporter import RichReporter

    reporter: BaseReporter = (
        JsonReporter() if output_format == "json" else RichReporter()
    )

    exit_code = execute_sync(schema, output, force, reporter)
    if exit_code != 0:
        raise SystemExit(exit_code)


@cli.command()
@click.option("--path", default=".", help="Project root to scan.")
@click.option(
    "--format",
    "output_format",
    type=click.Choice(["rich", "json"]),
    default="rich",
    help="Output format.",
)
@click.option(
    "--min-entropy",
    default=4.5,
    type=float,
    help="Minimum Shannon entropy threshold for secret detection.",
)
@click.option(
    "--exclude",
    multiple=True,
    help="Glob patterns to exclude (repeatable).",
)
@click.option("-v", "--verbose", is_flag=True, help="Show files scanned.")
def scan(
    path: str,
    output_format: str,
    min_entropy: float,
    exclude: tuple[str, ...],
    verbose: bool,
) -> None:
    """Detect hardcoded secrets in source files."""
    from envguard.commands.scan_cmd import execute_scan
    from envguard.reporters.base import BaseReporter
    from envguard.reporters.json_reporter import JsonReporter
    from envguard.reporters.rich_reporter import RichReporter

    reporter: BaseReporter = (
        JsonReporter() if output_format == "json" else RichReporter()
    )

    exit_code = execute_scan(
        path=path,
        output_format=output_format,
        min_entropy=min_entropy,
        exclude=exclude,
        verbose=verbose,
        reporter=reporter,
    )
    if exit_code != 0:
        raise SystemExit(exit_code)

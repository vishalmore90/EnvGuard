"""Rich terminal reporter for human-readable output."""

from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from envguard.reporters.base import BaseReporter
from envguard.scanners.models import ScanResult
from envguard.schema.validator import ValidationError


class RichReporter(BaseReporter):
    """Outputs beautiful, color-coded tables to the terminal using Rich."""

    def __init__(self, console: Console | None = None) -> None:
        self.console = console or Console()

    def report_init(self, scan_result: ScanResult, schema_path: str) -> None:
        table = Table(title="EnvGuard Initialized")
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="magenta")

        table.add_row("Variables Found", str(len(scan_result.unique_names)))
        table.add_row("Files Scanned", str(scan_result.file_count))
        table.add_row("Schema Path", schema_path)

        self.console.print()
        self.console.print(table)

        if scan_result.warnings:
            self.console.print("\n[yellow]Warnings:[/yellow]")
            for warning in scan_result.warnings:
                self.console.print(f"  - {warning}")

        if scan_result.skipped_files:
            self.console.print("\n[dim]Skipped files due to errors:[/dim]")
            for f in scan_result.skipped_files[:5]:
                self.console.print(f"  - {f}")
            if len(scan_result.skipped_files) > 5:
                self.console.print(
                    f"  ... and {len(scan_result.skipped_files) - 5} more"
                )

        self.console.print(
            "\n[green]Success![/green] Run [bold]envguard check[/bold] to validate."
        )

    def report_check(self, errors: list[ValidationError], total_checked: int) -> None:
        self.console.print()

        if not errors:
            self.console.print(
                Panel.fit(
                    f"[green]All {total_checked} variables passed validation![/green]",
                    title="EnvGuard Check",
                    border_style="green",
                )
            )
            return

        table = Table(title=f"Validation Results ({total_checked} checked)")
        table.add_column("Variable", style="cyan", no_wrap=True)
        table.add_column("Status", width=10)
        table.add_column("Message")

        for err in errors:
            status = "[red]ERROR[/red]" if err.is_error else "[yellow]WARN[/yellow]"
            msg_color = "red" if err.is_error else "yellow"
            table.add_row(
                err.var_name, status, f"[{msg_color}]{err.message}[/{msg_color}]"
            )

        self.console.print(table)

        error_count = sum(1 for e in errors if e.is_error)
        warn_count = len(errors) - error_count

        if error_count > 0:
            self.console.print(
                f"\n[red]Failed with {error_count} errors and {warn_count} warnings.[/red]"
            )
        else:
            self.console.print(f"\n[yellow]Passed with {warn_count} warnings.[/yellow]")

    def report_sync(self, example_path: str, count: int) -> None:
        self.console.print(
            f"\n[green]Success![/green] Wrote [bold]{count}[/bold] variables to [cyan]{example_path}[/cyan]."
        )

    def report_error(self, message: str) -> None:
        self.console.print(f"\n[bold red]Error:[/bold red] {message}")

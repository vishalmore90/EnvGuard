"""Base reporter interface for EnvGuard."""

from abc import ABC, abstractmethod

from envguard.scanners.models import ScanResult
from envguard.schema.validator import ValidationError


class BaseReporter(ABC):
    """Abstract base class for formatting and outputting EnvGuard data."""

    @abstractmethod
    def report_init(self, scan_result: ScanResult, schema_path: str) -> None:
        """Report the results of the 'envguard init' command."""
        ...

    @abstractmethod
    def report_check(self, errors: list[ValidationError], total_checked: int) -> None:
        """Report the results of the 'envguard check' command."""
        ...

    @abstractmethod
    def report_sync(self, example_path: str, count: int) -> None:
        """Report the results of the 'envguard sync' command."""
        ...

    @abstractmethod
    def report_error(self, message: str) -> None:
        """Report a fatal error."""
        ...

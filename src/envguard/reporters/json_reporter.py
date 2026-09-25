"""JSON reporter for CI/CD machine-readable output."""

import json

from envguard.reporters.base import BaseReporter
from envguard.scanners.models import ScanResult
from envguard.schema.validator import ValidationError


class JsonReporter(BaseReporter):
    """Outputs all reports as structured JSON to standard out."""

    def report_init(self, scan_result: ScanResult, schema_path: str) -> None:
        data = {
            "command": "init",
            "schema_path": schema_path,
            "variables_found": len(scan_result.unique_names),
            "files_scanned": scan_result.file_count,
            "skipped_files": scan_result.skipped_files,
            "warnings": scan_result.warnings,
        }
        print(json.dumps(data, indent=2))

    def report_check(self, errors: list[ValidationError], total_checked: int) -> None:
        errors_list = [
            {"variable": e.var_name, "message": e.message, "is_error": e.is_error}
            for e in errors
            if e.is_error
        ]
        warnings_list = [
            {"variable": e.var_name, "message": e.message, "is_error": e.is_error}
            for e in errors
            if not e.is_error
        ]

        data = {
            "command": "check",
            "total_checked": total_checked,
            "passed": len(errors) == 0,
            "error_count": len(errors_list),
            "warning_count": len(warnings_list),
            "errors": errors_list,
            "warnings": warnings_list,
        }
        print(json.dumps(data, indent=2))

    def report_sync(self, example_path: str, count: int) -> None:
        data = {
            "command": "sync",
            "example_path": example_path,
            "variables_written": count,
        }
        print(json.dumps(data, indent=2))

    def report_error(self, message: str) -> None:
        data = {
            "error": message,
        }
        print(json.dumps(data, indent=2))

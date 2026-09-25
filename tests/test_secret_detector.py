"""Tests for secret detector."""

from pathlib import Path

from envguard.secrets.detector import SecretDetector


def test_detector_finds_aws_key(tmp_path: Path) -> None:
    test_file = tmp_path / "test_aws.py"
    test_file.write_text(
        "import os\nAWS_KEY = 'AKIAIOSFODNN7EXAMPLE'\nprint('hello')\n"
    )

    detector = SecretDetector()
    findings = detector.scan_file(str(test_file))

    assert len(findings) == 1
    finding = findings[0]
    assert finding.variable_name == "AWS_KEY"
    assert finding.confidence == "HIGH"
    assert "aws_access_key" in finding.reason
    assert finding.value_snippet == "AKIA************MPLE"
    assert finding.line_number == 2


def test_detector_finds_high_entropy_secret(tmp_path: Path) -> None:
    test_file = tmp_path / "test_entropy.py"
    test_file.write_text(
        "config = {\n    'db_password': 'wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY'\n}\n"
    )

    detector = SecretDetector()
    findings = detector.scan_file(str(test_file))

    assert len(findings) == 1
    finding = findings[0]
    assert finding.variable_name == "db_password"
    assert finding.confidence == "MEDIUM"
    assert "High entropy" in finding.reason


def test_detector_ignores_safe_strings(tmp_path: Path) -> None:
    test_file = tmp_path / "test_safe.py"
    test_file.write_text(
        "welcome_msg = 'Hello, world! Welcome to the application.'\nPORT = '8080'\n"
    )

    detector = SecretDetector()
    findings = detector.scan_file(str(test_file))

    assert len(findings) == 0

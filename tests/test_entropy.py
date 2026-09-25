"""Tests for entropy calculations."""

from envguard.utils.entropy import shannon_entropy


def test_shannon_entropy_empty() -> None:
    assert shannon_entropy("") == 0.0


def test_shannon_entropy_single_char() -> None:
    assert shannon_entropy("a") == 0.0
    assert shannon_entropy("aaaaaa") == 0.0


def test_shannon_entropy_low() -> None:
    # "password" has low entropy
    entropy = shannon_entropy("password")
    assert 2.0 < entropy < 3.0


def test_shannon_entropy_high() -> None:
    # API key or UUID has high entropy
    entropy = shannon_entropy("AKIAIOSFODNN7EXAMPLE")
    assert entropy > 3.5

    entropy_b64 = shannon_entropy("wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY")
    assert entropy_b64 > 4.5

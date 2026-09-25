"""Information theory utilities for EnvGuard."""

import math
from collections import Counter


def shannon_entropy(s: str) -> float:
    """
    Calculate the Shannon entropy of a string.

    This measures the randomness/information density of a string.
    High entropy usually indicates a cryptographically generated
    secret (like an API key, JWT, or password).

    Args:
        s: The string to analyze.

    Returns:
        float: The entropy value in bits (higher = more random).
    """
    if not s:
        return 0.0

    counts = Counter(s)
    length = len(s)

    entropy = -sum(
        (count / length) * math.log2(count / length) for count in counts.values()
    )

    return float(entropy)

"""Known secret patterns for EnvGuard."""

import re

# High confidence credential patterns
SECRET_PATTERNS = {
    # AWS Access Key ID
    "aws_access_key": re.compile(
        r"\b(?:A3T[A-Z0-9]|AKIA|AGPA|AIDA|AROA|AIPA|ANPA|ANVA|ASIA)[A-Z0-9]{16}\b"
    ),
    # GitHub Access Token
    "github_token": re.compile(r"\b(ghp|gho|ghu|ghs|ghr)_[a-zA-Z0-9]{36}\b"),
    # Slack Token
    "slack_token": re.compile(r"\bxox[baprs]-[0-9]{10,13}-[a-zA-Z0-9\-]+\b"),
    # Stripe Standard Key
    "stripe_key": re.compile(r"\b(?:sk|rk)_(test|live)_[0-9a-zA-Z]{24}\b"),
    # Google (GCP) API Key
    "google_api_key": re.compile(r"\bAIza[0-9A-Za-z\\-_]{35}\b"),
    # Twilio API Key
    "twilio_api_key": re.compile(r"\bSK[0-9a-fA-F]{32}\b"),
    # Square Access Token
    "square_token": re.compile(r"\bsq0atp-[0-9A-Za-z\\-_]{22}\b"),
}

# Variable name patterns that suggest a secret might be assigned to them
SUSPICIOUS_VAR_NAMES = re.compile(
    r".*(password|secret|token|key|api_key|auth_token|access_token|credential|cert).*",
    re.IGNORECASE,
)

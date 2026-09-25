"""Secret detection engine for EnvGuard."""

import ast
from dataclasses import dataclass

from envguard.secrets.patterns import SECRET_PATTERNS, SUSPICIOUS_VAR_NAMES
from envguard.utils.entropy import shannon_entropy


@dataclass
class SecretFinding:
    """Represents a potential secret found in source code."""

    file_path: str
    line_number: int
    variable_name: str | None
    value_snippet: str
    reason: str
    confidence: str  # "HIGH", "MEDIUM", "LOW"


class SecretDetector:
    """Detects secrets in source code files."""

    def __init__(self, min_entropy: float = 4.5) -> None:
        self.min_entropy = min_entropy

    def scan_file(self, file_path: str) -> list[SecretFinding]:
        """Scan a Python file for hardcoded secrets."""
        # For MVP, we only scan Python files using AST for accurate string literal extraction.
        # Javascript could be added later or we can do a naive regex scan over lines.
        if not file_path.endswith(".py"):
            return []

        try:
            with open(file_path, encoding="utf-8") as f:
                content = f.read()
            tree = ast.parse(content)
        except Exception:
            return []

        findings: list[SecretFinding] = []

        for node in ast.walk(tree):
            # Look for variable assignments
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name):
                        var_name = target.id
                        if isinstance(node.value, ast.Constant) and isinstance(
                            node.value.value, str
                        ):
                            string_val = node.value.value
                            self._analyze_string(
                                string_val, var_name, file_path, node.lineno, findings
                            )

            # Look for dictionary keys/values
            elif isinstance(node, ast.Dict):
                for key_node, val_node in zip(node.keys, node.values, strict=False):
                    if isinstance(key_node, ast.Constant) and isinstance(
                        key_node.value, str
                    ):
                        key_name = key_node.value
                        if isinstance(val_node, ast.Constant) and isinstance(
                            val_node.value, str
                        ):
                            string_val = val_node.value
                            self._analyze_string(
                                string_val,
                                key_name,
                                file_path,
                                val_node.lineno,
                                findings,
                            )

        return findings

    def _analyze_string(
        self,
        string_val: str,
        var_name: str,
        file_path: str,
        line_number: int,
        findings: list[SecretFinding],
    ) -> None:
        """Analyze a string literal for secrets and append to findings if any."""
        # Ignore empty or very short strings
        if len(string_val) < 8:
            return

        # 1. Pattern Matching (HIGH confidence)
        for pattern_name, regex in SECRET_PATTERNS.items():
            if regex.search(string_val):
                findings.append(
                    SecretFinding(
                        file_path=file_path,
                        line_number=line_number,
                        variable_name=var_name,
                        value_snippet=self._mask_secret(string_val),
                        reason=f"Matches known pattern: {pattern_name}",
                        confidence="HIGH",
                    )
                )
                return  # Stop analysis if high confidence match

        # 2. Entropy Analysis
        entropy = shannon_entropy(string_val)
        is_suspicious_name = bool(SUSPICIOUS_VAR_NAMES.match(var_name))

        if entropy >= self.min_entropy:
            if is_suspicious_name:
                findings.append(
                    SecretFinding(
                        file_path=file_path,
                        line_number=line_number,
                        variable_name=var_name,
                        value_snippet=self._mask_secret(string_val),
                        reason=f"High entropy ({entropy:.2f}) assigned to suspicious variable",
                        confidence="MEDIUM",
                    )
                )
            else:
                findings.append(
                    SecretFinding(
                        file_path=file_path,
                        line_number=line_number,
                        variable_name=var_name,
                        value_snippet=self._mask_secret(string_val),
                        reason=f"High entropy ({entropy:.2f}) string literal",
                        confidence="LOW",
                    )
                )
        elif is_suspicious_name and len(string_val) > 10 and " " not in string_val:
            # Low entropy but suspicious name and looks like a token/password (no spaces)
            findings.append(
                SecretFinding(
                    file_path=file_path,
                    line_number=line_number,
                    variable_name=var_name,
                    value_snippet=self._mask_secret(string_val),
                    reason="Suspicious variable name with non-spaced string literal",
                    confidence="LOW",
                )
            )

    def _mask_secret(self, secret: str) -> str:
        """Mask a secret for safe output."""
        if len(secret) <= 8:
            return "*" * len(secret)
        return secret[:4] + "*" * (len(secret) - 8) + secret[-4:]

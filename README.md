# EnvGuard

**Validate, audit, and document environment variables across your projects.**

EnvGuard is a CLI tool that scans your source code for environment variable usage, validates them against a schema, keeps your `.env.example` in sync, and detects hardcoded secrets.

## The Problem

Environment variable misconfiguration is one of the most common sources of developer frustration:

- `.env.example` files drift out of sync with actual code usage
- New team members waste hours debugging missing env vars
- Hardcoded secrets accidentally slip into source code
- No schema means no validation — env vars are untyped strings

## Features

- **`envguard init`** — Scan your project and generate a `.envguard.yml` schema
- **`envguard check`** — Validate your environment against the schema
- **`envguard sync`** — Generate/update `.env.example` from the schema
- **`envguard scan`** — Detect hardcoded secrets in source files

## Installation

```bash
pip install envguard
```

## Quick Start

```bash
# Generate a schema from your project
envguard init

# Validate your environment
envguard check

# Update .env.example
envguard sync

# Scan for hardcoded secrets
envguard scan
```

## Supported Languages

- **Python** — AST-based scanning (`os.environ`, `os.getenv`)
- **JavaScript/TypeScript** — Regex-based scanning (`process.env`)

## Tech Stack

- **Python 3.10+**
- **Click** — CLI framework
- **Rich** — Terminal output formatting
- **PyYAML** — Schema file parsing

## Development

```bash
# Clone the repository
git clone https://github.com/vishalmore90/EnvGuard.git
cd EnvGuard

# Create virtual environment
python -m venv .venv
.venv\Scripts\activate  # Windows
# source .venv/bin/activate  # macOS/Linux

# Install in editable mode with dev dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Run linter
ruff check .

# Run formatter check
ruff format --check .

# Run type checker
mypy src/envguard
```

## Project Structure

```
envguard/
├── src/envguard/         # Main package
│   ├── cli.py            # CLI entry point (Click)
│   ├── commands/         # Command handlers
│   ├── scanners/         # Language-specific source code scanners
│   ├── schema/           # Schema models, loading, validation
│   ├── secrets/          # Secret detection engine
│   ├── reporters/        # Output formatting (Rich, JSON)
│   └── utils/            # Shared utilities
├── tests/                # Test suite
├── docs/                 # Documentation
└── .github/workflows/    # CI/CD
```

## License

MIT — see [LICENSE](LICENSE).

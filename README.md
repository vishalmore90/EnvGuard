# 🛡️ EnvGuard

> **Validate, audit, and document environment variables across your projects.**

EnvGuard is a CLI tool designed to solve the chaos of missing environment variables, outdated `.env.example` files, and accidentally committed API keys. It automatically scans your source code, generates a schema, validates your environment, and actively hunts for leaked secrets.

Perfect for CI/CD pipelines and local development.

---

## 🚀 Features

- **Source Code Scanning**: Automatically detects environment variable usage (`os.getenv`, `process.env`, etc.) across Python and JavaScript/TypeScript files.
- **Schema Validation**: Define types, enums, defaults, and requirements in `.envguard.yml`. Fail your CI/CD pipeline if an environment isn't configured correctly.
- **Auto-Sync**: Automatically generate and update your `.env.example` file based on actual code usage and schema definitions. No more manual updates!
- **Secret Detection**: Uses Shannon entropy analysis and regex patterns to detect hardcoded API keys, passwords, and tokens in your source code.
- **Beautiful Output**: Rich terminal UI for humans, structured JSON output for machines (CI/CD).

---

## 📦 Installation

EnvGuard requires Python 3.10+.

```bash
pip install envguard
```

*(Note: If cloning from source, use `pip install -e .`)*

---

## 🛠️ Usage

### 1. Initialize (`envguard init`)
Scan your project to discover environment variable usage and scaffold an `.envguard.yml` schema file.

```bash
envguard init
```

*Optionally specify languages: `envguard init --languages python,javascript`*

### 2. Validate (`envguard check`)
Check your current environment (or a specific `.env` file) against your schema.

```bash
# Check current environment
envguard check

# Check a specific .env file
envguard check --env-file .env.local

# CI/CD Strict Mode (treats missing optional vars as errors)
envguard check --ci --format json
```

### 3. Sync (`envguard sync`)
Generate a heavily documented `.env.example` file based on your `.envguard.yml` schema.

```bash
envguard sync
```

### 4. Detect Secrets (`envguard scan`)
Scan your codebase for hardcoded secrets, API keys, and high-entropy strings.

```bash
envguard scan
```

---

## 📝 Schema Example (`.envguard.yml`)

```yaml
version: '1'
variables:
  DATABASE_URL:
    required: true
    type: url
    description: PostgreSQL connection string
    example: postgresql://user:pass@localhost:5432/mydb
    sensitive: true
  PORT:
    required: false
    type: integer
    default: '8080'
  DEBUG:
    required: false
    type: boolean
    default: 'false'
  LOG_LEVEL:
    required: false
    type: choice
    choices:
      - INFO
      - DEBUG
      - ERROR
```

---

## 👨‍💻 Development

Want to contribute? Setting up the development environment is easy!

```bash
# Clone the repository
git clone https://github.com/vishalmore90/EnvGuard.git
cd EnvGuard

# Install dependencies (using uv, pip, or hatch)
pip install -e .[dev]

# Run tests
pytest

# Run linters and type checkers
ruff check .
mypy src/envguard
```

---

## 📄 License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

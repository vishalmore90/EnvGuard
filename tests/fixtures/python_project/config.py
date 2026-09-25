"""
Fixture: Python config file with aliased imports.
Tests import aliasing scenarios.
"""

# Alias: import os as operating_system
import os as operating_system

# Alias: from os import environ
from os import environ

# Alias: from os import environ as env
from os import environ as env

# Alias: from os import getenv as get_env
from os import getenv as get_env

# Should be detected via aliased `import os as operating_system`
LOG_LEVEL = operating_system.getenv("LOG_LEVEL", "INFO")

# Should be detected via `from os import environ`
SECRET_KEY = environ["SECRET_KEY"]

# Should be detected via `from os import getenv as get_env`
SENTRY_DSN = get_env("SENTRY_DSN")

# Should be detected via `from os import environ as env`
ALLOWED_HOSTS = env.get("ALLOWED_HOSTS", "*")

"""
Fixture: Python project main application file.
Tests all standard env var access patterns.
"""

import os

# Pattern 1: os.environ["KEY"] — required, raises KeyError if missing
DATABASE_URL = os.environ["DATABASE_URL"]

# Pattern 2: os.getenv("KEY") — optional, returns None if missing
API_KEY = os.getenv("API_KEY")

# Pattern 3: os.getenv("KEY", default) — optional with default
DEBUG = os.getenv("DEBUG", "false")

# Pattern 4: os.environ.get("KEY") — optional, returns None
REDIS_URL = os.environ.get("REDIS_URL")

# Pattern 5: os.environ.get("KEY", default) — optional with default
PORT = os.environ.get("PORT", "8000")

# This dynamic key should NOT be detected (cannot resolve statically)
dynamic_key = "SOME_KEY"
value = os.environ.get(dynamic_key)

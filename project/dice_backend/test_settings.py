"""
Test-specific Django settings.

Inherits everything from the main settings but swaps PostgreSQL for an
in-memory SQLite database so tests can run without any external services.

Usage:
    python manage.py test dice --settings=dice_backend.test_settings
"""

import os

# Must be set before the main settings module is imported because
# dice/authentication.py reads SECRET_KEY from the environment at
# module load time to verify JWT tokens.
os.environ.setdefault("SECRET_KEY", "test-jwt-secret-key-for-testing")

from dice_backend.settings import *  # noqa: F401, F403

# Override the database to use a fast, disposable SQLite in-memory DB.
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    }
}

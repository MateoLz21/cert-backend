"""Development environment settings."""
from .base import *  # noqa: F401,F403
from .base import env

DEBUG = True

ALLOWED_HOSTS = env.list("ALLOWED_HOSTS", default=["*"])

# Permissive CORS for local frontend development.
CORS_ALLOW_ALL_ORIGINS = True

# Email backend writes to console during development.
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

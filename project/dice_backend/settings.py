from pathlib import Path
import os

BASE_DIR = Path(__file__).resolve().parent.parent

# Django's own secret key — only used for sessions/CSRF, NOT for JWT.
# JWT verification uses the SECRET_KEY env var (see dice/authentication.py).
SECRET_KEY = "django-not-used-for-jwt"

DEBUG = True

DOMAIN=os.getenv('DOMAIN',None)
if DOMAIN:
    ALLOWED_HOSTS = [f"dice.{DOMAIN}", "localhost", "127.0.0.1"]
else:
    ALLOWED_HOSTS = ["*"]

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",

    "rest_framework",
    "corsheaders",

    "dice",
]

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
]

CORS_ALLOW_CREDENTIALS = True
CORS_ALLOWED_ORIGINS = [
    "https://simaptics.com",
    "https://auth.simaptics.com",
    "https://crawler.simaptics.com",
    "https://dice.simaptics.com",
    "http://localhost:3000",
]

CSRF_TRUSTED_ORIGINS = [
    "https://simaptics.com",
    "https://auth.simaptics.com",
    "https://crawler.simaptics.com",
    "https://dice.simaptics.com",
]

ROOT_URLCONF = "dice_backend.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {"context_processors": ["django.template.context_processors.debug",
                                            "django.template.context_processors.request",
                                            "django.contrib.auth.context_processors.auth",
                                            "django.contrib.messages.context_processors.messages"]},
    },
]

WSGI_APPLICATION = "dice_backend.wsgi.application"

# PostgreSQL database — all connection params come from environment variables.
# For tests, this is overridden to SQLite in test_settings.py.
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.getenv("DB_DATABASE"),
        "USER": os.getenv("DB_USER"),
        "PASSWORD": os.getenv("DB_PASSWORD"),
        "HOST": os.getenv("DB_HOST"),
        "PORT": os.getenv("DB_PORT", "5432"),
    }
}


# We are NOT using Django users for auth
AUTH_PASSWORD_VALIDATORS = []

# Default to JWT cookie auth and require authentication globally.
# Individual views can override with permission_classes = [AllowAny].
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "dice.authentication.DiceJWTAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated",
    ],
}

STATIC_URL = "static/"
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

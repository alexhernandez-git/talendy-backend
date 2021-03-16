"""Testing settings.
With these settings, tests run faster.
"""

from .settings import *  # NOQA


# Base
DEBUG = False
TEST_RUNNER = "django.test.runner.DiscoverRunner"

# Cache
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        "LOCATION": ""
    }
}

# Passwords
PASSWORD_HASHERS = ["django.contrib.auth.hashers.MD5PasswordHasher"]

# Templates
TEMPLATES[0]["OPTIONS"]["debug"] = DEBUG  # NOQA
TEMPLATES[0]["OPTIONS"]["loaders"] = [  # NOQA
    (
        "django.template.loaders.cached.Loader",
        [
            "django.template.loaders.filesystem.Loader",
            "django.template.loaders.app_directories.Loader",
        ],
    )
]

# Email
EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"
EMAIL_HOST = "localhost"
EMAIL_PORT = 1025

# Copyright (C) 2025  The Software Heritage developers
# See the AUTHORS file at the top-level directory of this distribution
# License: GNU Affero General Public License version 3, or any later version
# See top-level LICENSE file for more information

"""Common settings for the swh-coarnotify project."""

from importlib.metadata import version
import os
from pathlib import Path

from swh.core import config

BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent


# SWH config
default_swh_config = {
    # Django's ALLOWED_HOST
    "allowed_hosts": ("list", []),
    # Override recipients inbox url when sending CN, useful in the docker env
    "inbox_url_override": ("str", ""),
    # Client used to send notifications
    "coar_notify_client": ("str", "swh.coarnotify.client.COARNotifyClient"),
    # Storage
    "storage": ("dict", {"cls": "memory"}),
    # Inbox
    "origin": (
        "dict",
        {
            "inbox": "http://127.0.0.1",
            "id": "https://www.softwareheritage.org/",
            "type": "Service",
        },
    ),
    # Private/secrets
    "private": ("dict", {"secret_key": "", "db": {}}),
    # Insecure serve django staticfiles (useful when using a docker dev env)
    "serve_assets": ("bool", False),
}
if config_file := os.environ.get("SWH_CONFIG_FILENAME"):
    SWH_CONF = config.load_named_config(config_file, default_swh_config)
else:
    SWH_CONF = config.read(default_conf=default_swh_config)

ENV_NAME = os.environ.get("DJANGO_SETTINGS_MODULE", "").split(".")[-1]

# Application definition
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "rest_framework",
    "rest_framework.authtoken",
    "swh.coarnotify.server",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "swh.coarnotify.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "swh.coarnotify.server.utils.context_processor",
            ],
        },
    },
]

WSGI_APPLICATION = "swh.coarnotify.wsgi.application"


# Password validation
# https://docs.djangoproject.com/en/5.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]
AUTH_USER_MODEL = "swh_coarnotify_server.Actor"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Internationalization
LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR

# Django Rest Framework
REST_FRAMEWORK = {
    "DEFAULT_PARSER_CLASSES": ["swh.coarnotify.parsers.JSONLDParser"],
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework.authentication.TokenAuthentication"
    ],
}

# COAR Notify settings
CN_SEND_TIMEOUT = 10
CN_ORIGIN = SWH_CONF["origin"]
CN_CLIENT = SWH_CONF["coar_notify_client"]
CN_INBOX_URL_OVERRIDE = SWH_CONF["inbox_url_override"]
CN_VERSION = version("swh.coarnotify")

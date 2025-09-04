# Copyright (C) 2025  The Software Heritage developers
# See the AUTHORS file at the top-level directory of this distribution
# License: GNU Affero General Public License version 3, or any later version
# See top-level LICENSE file for more information

"""Test settings for swh_coarnotify project."""

from .common import *  # noqa: F401, F403
from .common import REST_FRAMEWORK

DEBUG = False
ALLOWED_HOSTS = ["*"]
SECRET_KEY = "swh_coarnotify_test"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    }
}

PASSWORD_HASHERS = ["django.contrib.auth.hashers.MD5PasswordHasher"]

REST_FRAMEWORK["TEST_REQUEST_RENDERER_CLASSES"] = [
    "swh.coarnotify.renderers.JSONLDRenderer"
]

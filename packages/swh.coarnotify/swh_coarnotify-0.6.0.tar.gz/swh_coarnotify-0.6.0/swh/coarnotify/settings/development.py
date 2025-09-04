# Copyright (C) 2025  The Software Heritage developers
# See the AUTHORS file at the top-level directory of this distribution
# License: GNU Affero General Public License version 3, or any later version
# See top-level LICENSE file for more information

"""Development settings for swh_coarnotify project."""

from .common import *  # noqa: F401, F403
from .common import BASE_DIR

DEBUG = True
ALLOWED_HOSTS = ["*"]
SECRET_KEY = "swh_coarnotify_dev"

CN_CLIENT = "swh.coarnotify.client.ConsoleCOARNotifyClient"

# Database
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

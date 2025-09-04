# Copyright (C) 2025  The Software Heritage developers
# See the AUTHORS file at the top-level directory of this distribution
# License: GNU Affero General Public License version 3, or any later version
# See top-level LICENSE file for more information

"""Production settings for swh_coarnotify project."""

from .common import *  # noqa: F401, F403
from .common import SWH_CONF

# https://docs.djangoproject.com/en/5.1/howto/deployment/checklist/
DEBUG = False
SECRET_KEY = SWH_CONF["private"]["secret_key"]
ALLOWED_HOSTS = SWH_CONF["allowed_hosts"]

# Setup support for proxy headers
USE_X_FORWARDED_HOST = True
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

# Database
postgresql_setup = SWH_CONF["private"]["db"]
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": postgresql_setup.get("name"),
        "HOST": postgresql_setup.get("host"),
        "PORT": postgresql_setup.get("port"),
        "USER": postgresql_setup.get("user"),
        "PASSWORD": postgresql_setup.get("password"),
    }
}

# Copyright (C) 2025  The Software Heritage developers
# See the AUTHORS file at the top-level directory of this distribution
# License: GNU Affero General Public License version 3, or any later version
# See top-level LICENSE file for more information

"""App definition."""

from django.apps import AppConfig


class ServerConfig(AppConfig):
    name = "swh.coarnotify.server"
    label = "swh_coarnotify_server"

    def ready(self) -> None:
        """Plug signals to generate an auth Token for every created users."""
        from . import signals  # noqa: F401

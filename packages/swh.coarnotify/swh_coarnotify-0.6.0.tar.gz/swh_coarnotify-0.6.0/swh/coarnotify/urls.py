# Copyright (C) 2025  The Software Heritage developers
# See the AUTHORS file at the top-level directory of this distribution
# License: GNU Affero General Public License version 3, or any later version
# See top-level LICENSE file for more information
"""Routing."""

from django.conf import settings
from django.contrib import admin
from django.contrib.staticfiles.views import serve
from django.urls import path, re_path

from swh.coarnotify.server.views import inbox, read_notification

handler400 = "rest_framework.exceptions.bad_request"

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", inbox, name="inbox"),
    path("<uuid:pk>/", read_notification, name="read"),
]


# serve static assets through django development server (useful in a docker dev env)
if settings.SWH_CONF.get("serve_assets", False):

    def insecure_serve(request, path, **kwargs):
        return serve(request, path, insecure=True, **kwargs)

    urlpatterns.append(
        re_path(
            "static/(?P<path>.*)$",
            insecure_serve,
            name="insecure-serve",
        )
    )

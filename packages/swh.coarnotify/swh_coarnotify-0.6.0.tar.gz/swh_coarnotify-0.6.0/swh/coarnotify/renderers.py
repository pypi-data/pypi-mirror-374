# Copyright (C) 2025  The Software Heritage developers
# See the AUTHORS file at the top-level directory of this distribution
# License: GNU Affero General Public License version 3, or any later version
# See top-level LICENSE file for more information

from rest_framework.renderers import JSONRenderer


class JSONLDRenderer(JSONRenderer):
    media_type = "application/ld+json"
    format = "json-ld"

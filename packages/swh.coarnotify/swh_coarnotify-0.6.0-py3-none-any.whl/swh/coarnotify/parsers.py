# Copyright (C) 2025  The Software Heritage developers
# See the AUTHORS file at the top-level directory of this distribution
# License: GNU Affero General Public License version 3, or any later version
# See top-level LICENSE file for more information

from rest_framework.parsers import JSONParser

from .renderers import JSONLDRenderer


class JSONLDParser(JSONParser):
    media_type = "application/ld+json"
    renderer_class = JSONLDRenderer

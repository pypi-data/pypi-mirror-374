# Copyright (C) 2025  The Software Heritage developers
# See the AUTHORS file at the top-level directory of this distribution
# License: GNU Affero General Public License version 3, or any later version
# See top-level LICENSE file for more information

import uuid

import pytest

from swh.coarnotify.server.models import InboundNotification

pytestmark = pytest.mark.django_db


def test_inbound_url():
    pk = uuid.uuid4()
    notification = InboundNotification.objects.create(id=pk, payload={}, raw_payload={})
    assert notification.get_absolute_url() == f"/{pk}/"

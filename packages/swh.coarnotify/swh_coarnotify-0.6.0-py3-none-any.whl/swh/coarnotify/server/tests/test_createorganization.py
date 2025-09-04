# Copyright (C) 2025  The Software Heritage developers
# See the AUTHORS file at the top-level directory of this distribution
# License: GNU Affero General Public License version 3, or any later version
# See top-level LICENSE file for more information
from django.core.management import call_command
from django.core.management.base import CommandError
import pytest

from swh.coarnotify.server.models import Organization

pytestmark = pytest.mark.django_db


@pytest.mark.parametrize(
    "params",
    [
        ("Partner", "http://partner.local", "http://inbox.partner.local"),
        ("Partner", "http://partner2.local", "http://inbox.partner2.local"),
        ("Partner2", "http://partner.local", "http://inbox.partner2.local"),
        ("Partner2", "http://partner2.local", "http://inbox.partner.local"),
    ],
)
def test_duplicate(partner, params):
    with pytest.raises(CommandError, match="already exists"):
        call_command(
            "createorganization",
            params,
        )


def test_ok(partner):
    call_command(
        "createorganization",
        ("Local", "http://example.local", "http://inbox.example.local"),
    )
    assert Organization.objects.get(
        name="Local", url="http://example.local", inbox="http://inbox.example.local"
    )

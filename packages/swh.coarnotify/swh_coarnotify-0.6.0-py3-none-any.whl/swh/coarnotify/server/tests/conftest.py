# Copyright (C) 2025  The Software Heritage developers
# See the AUTHORS file at the top-level directory of this distribution
# License: GNU Affero General Public License version 3, or any later version
# See top-level LICENSE file for more information

from pyld import jsonld
import pytest
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient, APIRequestFactory

from swh.coarnotify.server.models import (
    InboundNotification,
    Organization,
    OutboundNotification,
)
from swh.model.model import Origin
from swh.storage import get_storage

from . import notification


@pytest.fixture(autouse=True)
def test_settings(settings):
    settings.CN_CLIENT = "swh.coarnotify.client.DummyCOARNotifyClient"


@pytest.fixture
def default_origin():
    return Origin("https://github.com/rdicosmo/parmap")


@pytest.fixture
def notification_payload(default_origin):
    return notification("00000000-0000-0000-0000-000000000000", default_origin.url)


@pytest.fixture
@pytest.mark.django_db
def inbound_notification(partner, default_origin):
    raw_payload = notification(
        "00000000-0000-0000-0000-000000000000", default_origin.url
    )
    payload = jsonld.compact(raw_payload, raw_payload["@context"])  # XXX cache ?
    return InboundNotification.objects.create(
        id="00000000-0000-0000-0000-000000000000",
        payload=payload,
        sender=partner,
        raw_payload=raw_payload,
    )


@pytest.fixture
@pytest.mark.django_db
def outbound_notification():
    return OutboundNotification.objects.create(
        id="bd6160ef-ed8e-4d61-a4c9-599169b2c351",
        payload=notification("bd6160ef-ed8e-4d61-a4c9-599169b2c351"),
    )


@pytest.fixture
def partner(db):
    return Organization.objects.create(
        url="http://partner.local", inbox="http://inbox.partner.local", name="Partner"
    )


@pytest.fixture
def member(partner, django_user_model):
    return django_user_model.objects.create_user(
        "member@partner.local", organization=partner
    )


@pytest.fixture
def member_token(member):
    return Token.objects.get(user=member)


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
@pytest.mark.django_db
def authenticated_api_client(api_client, member_token):
    api_client.credentials(HTTP_AUTHORIZATION=f"Token {member_token.key}")
    return api_client


@pytest.fixture
def api_rf():
    return APIRequestFactory()


@pytest.fixture
def storage(default_origin, settings):
    storage = get_storage(**settings.SWH_CONF["storage"])
    storage.origin_add([default_origin])
    return storage

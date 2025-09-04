# Copyright (C) 2025  The Software Heritage developers
# See the AUTHORS file at the top-level directory of this distribution
# License: GNU Affero General Public License version 3, or any later version
# See top-level LICENSE file for more information
from http import HTTPStatus
import uuid

from pytest_django.asserts import assertContains, assertTemplateUsed

from swh.coarnotify.server.models import InboundNotification, Organization, Statuses

from . import notification


def test_head(client):
    response = client.head("/")
    assert response.status_code == HTTPStatus.OK
    assert (
        response.headers["Link"]
        == '<http://testserver/>; rel="http://www.w3.org/ns/ldp#inbox'
    )


def test_get(client, settings):
    settings.CN_VERSION = "1.2.3"
    with assertTemplateUsed("index.html"):
        response = client.get("/")
    assertContains(response, '<span id="swh-coarnotify-version">1.2.3</span>')
    assert response.status_code == HTTPStatus.OK
    assert (
        response.headers["Link"]
        == '<http://testserver/>; rel="http://www.w3.org/ns/ldp#inbox'
    )


def test_authenticated_get(authenticated_api_client, inbound_notification):
    response = authenticated_api_client.get("/")
    assert not response.templates
    assert response.status_code == HTTPStatus.OK
    assert response.data == {
        "@context": "http://www.w3.org/ns/ldp",
        "@id": "http://testserver/",
        "contains": [f"http://testserver{inbound_notification.get_absolute_url()}"],
    }


def test_unauthenticated_post(client):
    response = client.post("/", {}, format="json-ld")
    assert response.status_code == HTTPStatus.FORBIDDEN


def test_authenticated_post(member, authenticated_api_client):
    id_ = uuid.uuid4()
    payload = notification(id_)
    response = authenticated_api_client.post("/", payload, format="json-ld")
    assert response.status_code == HTTPStatus.CREATED
    assert response.headers["Location"] == f"http://testserver/{id_}/"
    inbound_notification = InboundNotification.objects.get(id=id_)
    assert inbound_notification.sender == member.organization
    assert inbound_notification.raw_payload == payload
    assert inbound_notification.in_reply_to is None
    assert inbound_notification.payload != inbound_notification.raw_payload


def test_process_notification_missing_keys(
    authenticated_api_client, notification_payload
):
    notification_payload.pop("id")
    notification_payload["object"].pop("id")
    response = authenticated_api_client.post(
        "/", notification_payload, format="json-ld"
    )
    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert "must contain an id" in response.data[0]
    assert "object must contain an id" in response.data[1]


def test_process_notification_invalid_context(
    authenticated_api_client, notification_payload
):
    notification_payload["@context"] = ["invalid"]
    response = authenticated_api_client.post(
        "/", notification_payload, format="json-ld"
    )
    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert str(response.data["detail"]) == "Unable to process json-ld"


def test_sender_inbox_does_not_match(authenticated_api_client):
    id_ = uuid.uuid4()
    payload = notification(id_)
    payload["origin"]["inbox"] = "https://another.inbox"
    response = authenticated_api_client.post("/", payload, format="json-ld")
    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert "does not match Origin inbox https://another.inbox" in response.data[0]


def test_in_reply_to(authenticated_api_client, outbound_notification):
    id_ = uuid.uuid4()
    payload = notification(id_)
    payload["inReplyTo"] = f"urn:uuid:{outbound_notification.id}"
    response = authenticated_api_client.post("/", payload, format="json-ld")
    assert response.status_code == HTTPStatus.CREATED
    inbound_notification = InboundNotification.objects.get(id=id_)
    outbound_notification.refresh_from_db()
    assert inbound_notification.in_reply_to == outbound_notification


def test_duplicate_uuid(authenticated_api_client, inbound_notification):
    response = authenticated_api_client.post(
        "/", inbound_notification.payload, format="json-ld"
    )
    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert f"{inbound_notification.id} has already been handled" in str(
        response.data[0]
    )


def test_target_inbox(authenticated_api_client):
    id_ = uuid.uuid4()
    payload = notification(id_)
    payload["target"]["inbox"] = "https://another.inbox"
    response = authenticated_api_client.post("/", payload, format="json-ld")
    assert response.status_code == HTTPStatus.CREATED
    cn = InboundNotification.objects.get(id=id_)
    assert cn.status == Statuses.UNPROCESSABLE
    assert "https://another.inbox" in cn.error_message


def test_no_handler(authenticated_api_client):
    id_ = uuid.uuid4()
    payload = notification(id_)
    payload["type"] = "coar-notify:UnhandledAction"
    response = authenticated_api_client.post("/", payload, format="json-ld")
    assert response.status_code == HTTPStatus.CREATED
    cn = InboundNotification.objects.get(id=id_)
    assert cn.status == Statuses.UNPROCESSABLE
    assert "Unable to process UnhandledAction" in cn.error_message


def test_read_notification_unauthenticated(client, inbound_notification):
    response = client.get(f"/{inbound_notification.id}/")
    assert response.status_code == HTTPStatus.UNAUTHORIZED


def test_read_notification_wrong_user(authenticated_api_client, inbound_notification):
    other_org = Organization.objects.create(
        url="http://other.local", inbox="http://inbox.other.local", name="Other"
    )

    inbound_notification.sender = other_org
    inbound_notification.save()
    response = authenticated_api_client.get(f"/{inbound_notification.id}/")
    assert response.status_code == HTTPStatus.FORBIDDEN


def test_read_notification(authenticated_api_client, inbound_notification):
    response = authenticated_api_client.get(f"/{inbound_notification.id}/")
    assert response.status_code == HTTPStatus.OK
    assert response.data == inbound_notification.raw_payload

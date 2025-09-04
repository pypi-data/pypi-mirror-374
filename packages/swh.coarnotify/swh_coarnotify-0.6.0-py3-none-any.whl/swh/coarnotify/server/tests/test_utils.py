# Copyright (C) 2025  The Software Heritage developers
# See the AUTHORS file at the top-level directory of this distribution
# License: GNU Affero General Public License version 3, or any later version
# See top-level LICENSE file for more information

from http import HTTPStatus
import uuid

import pytest
from rest_framework.exceptions import ValidationError

from swh.coarnotify.server.models import InboundNotification, Organization, Statuses
from swh.coarnotify.server.utils import (
    AS_CONTEXT,
    COAR_CONTEXT,
    DEPRECATED_COAR_CONTEXT,
    context_processor,
    create_accept_cn,
    create_reject_cn,
    create_unprocessable_cn,
    inbox_headers,
    reject,
    send_cn,
    to_sorted_tuple,
    unprocessable,
    url_match,
    uuid_from_urn,
    validate_context,
    validate_required_keys,
    validate_sender_inbox,
    validate_target_inbox,
)


@pytest.mark.django_db
def test_send_cn_success(requests_mock):
    requests_mock.post("http://original.localhost", status_code=HTTPStatus.CREATED)

    notification = InboundNotification.objects.create(
        payload={"target": {"inbox": "http://original.localhost"}}, raw_payload={}
    )
    previous_save_stamp = notification.updated_at
    assert send_cn(notification)
    assert notification.status == Statuses.PROCESSED
    assert notification.updated_at > previous_save_stamp


@pytest.mark.django_db
def test_send_cn_failure(settings, requests_mock):
    settings.CN_CLIENT = "swh.coarnotify.client.COARNotifyClient"
    requests_mock.post(
        "http://original.localhost", status_code=HTTPStatus.INSUFFICIENT_STORAGE
    )

    notification = InboundNotification.objects.create(
        payload={"target": {"inbox": "http://original.localhost"}}, raw_payload={}
    )
    previous_save_stamp = notification.updated_at
    assert not send_cn(notification)
    assert notification.status == Statuses.REJECTED
    assert "507 Server Error" in notification.error_message
    assert notification.updated_at > previous_save_stamp


@pytest.mark.django_db
def test_create_accept_cn(inbound_notification, settings):
    notification = create_accept_cn(inbound_notification)

    assert notification.pk != inbound_notification.pk
    assert notification.payload["@context"] == [
        "https://www.w3.org/ns/activitystreams",
        "https://coar-notify.net",
    ]
    assert notification.payload["id"] == f"urn:uuid:{notification.pk}"
    assert notification.payload["inReplyTo"] == f"urn:uuid:{inbound_notification.pk}"
    assert notification.payload["type"] == "Accept"

    assert "@context" not in notification.payload["object"]
    payload = inbound_notification.payload.copy()
    payload.pop("@context")
    assert notification.payload["object"] == payload
    assert notification.payload["origin"] == settings.CN_ORIGIN
    assert notification.payload["target"] == inbound_notification.payload["origin"]


@pytest.mark.django_db
def test_create_accept_cn_summary(inbound_notification):
    notification = create_accept_cn(inbound_notification, "test summary")
    assert notification.payload["summary"] == "test summary"


@pytest.mark.django_db
def test_create_unprocessable_cn(inbound_notification, settings):
    inbound_notification.error_message = "unprocessable summary"
    notification = create_unprocessable_cn(inbound_notification)

    assert notification.pk != inbound_notification.pk
    assert notification.payload["@context"] == [
        "https://www.w3.org/ns/activitystreams",
        "https://coar-notify.net",
    ]
    assert notification.payload["id"] == f"urn:uuid:{notification.pk}"
    assert notification.payload["inReplyTo"] == f"urn:uuid:{inbound_notification.pk}"
    assert notification.payload["type"] == [
        "Flag",
        "coar-notify:UnprocessableNotification",
    ]
    assert notification.payload["object"] == {
        "id": f"urn:uuid:{inbound_notification.pk}",
    }
    assert notification.payload["origin"] == settings.CN_ORIGIN
    assert notification.payload["target"] == inbound_notification.payload["origin"]
    assert notification.payload["summary"] == "unprocessable summary"
    assert notification.in_reply_to == inbound_notification


@pytest.mark.django_db
def test_create_reject_cn(inbound_notification, settings):
    inbound_notification.error_message = "reject summary"
    notification = create_reject_cn(inbound_notification)

    assert notification.pk != inbound_notification.pk
    assert notification.payload["@context"] == [
        "https://www.w3.org/ns/activitystreams",
        "https://coar-notify.net",
    ]
    assert notification.payload["id"] == f"urn:uuid:{notification.pk}"
    assert notification.payload["inReplyTo"] == f"urn:uuid:{inbound_notification.pk}"
    assert notification.payload["type"] == "Reject"
    assert "@context" not in notification.payload["object"]
    payload = inbound_notification.payload.copy()
    payload.pop("@context")
    assert notification.payload["object"] == payload
    assert notification.payload["origin"] == settings.CN_ORIGIN
    assert notification.payload["target"] == inbound_notification.payload["origin"]
    assert notification.payload["summary"] == "reject summary"
    assert notification.in_reply_to == inbound_notification


@pytest.mark.parametrize(
    "urn",
    [
        "http",
        "urn:issn:0767-7316",
        "urn:uuid:1234",
        "test:uuid:00000000-0000-0000-0000-000000000000",
        "",
        None,
    ],
)
def test_invalid_uuid_from_urn(urn):
    with pytest.raises(ValidationError):
        uuid_from_urn(urn)


def test_uuid_from_urn():
    assert uuid_from_urn("urn:uuid:00000000-0000-0000-0000-000000000000") == uuid.UUID(
        "00000000-0000-0000-0000-000000000000"
    )


@pytest.mark.parametrize(
    "value,expected",
    [
        ("type", ("type",)),
        (["type2", "type1"], ("type1", "type2")),
    ],
)
def test_to_sorted_tuple(value, expected):
    assert to_sorted_tuple(value) == expected


@pytest.mark.django_db
def test_validate_sender_inbox(rf, django_user_model, settings):
    organization = Organization.objects.create(
        url="http://org.local", inbox="http://inbox", name="Other"
    )
    user = django_user_model.objects.create_user(
        "test@localhost", organization=organization
    )

    settings.SWH_AUTH_SERVER_URL = ""
    request = rf.get("/")
    request.user = user

    assert validate_sender_inbox(request, {"origin": {"inbox": "http://inbox"}})
    assert validate_sender_inbox(request, {"origin": {"inbox": "http://inbox/"}})
    with pytest.raises(ValidationError):
        validate_sender_inbox(request, {"origin": {"inbox": ""}})
    with pytest.raises(ValidationError):
        validate_sender_inbox(request, {"origin": {"inbox": "http://outbox"}})


@pytest.mark.django_db
def test_unprocessable(inbound_notification):
    unprocessable(inbound_notification, "my error")
    assert inbound_notification.status == Statuses.UNPROCESSABLE
    assert inbound_notification.error_message == "my error"
    assert inbound_notification.replied_by


@pytest.mark.django_db
def test_reject(inbound_notification):
    reject(inbound_notification, "my error")
    assert inbound_notification.status == Statuses.REJECTED
    assert inbound_notification.error_message == "my error"
    assert inbound_notification.replied_by


def test_inbox_headers(rf):
    request = rf.get("/")
    assert inbox_headers(request) == {
        "Link": ('<http://testserver/>; rel="http://www.w3.org/ns/ldp#inbox')
    }


def test_validate_context():
    with pytest.raises(ValidationError, match=AS_CONTEXT):
        validate_context(["a"])
    with pytest.raises(ValidationError, match=COAR_CONTEXT):
        validate_context([AS_CONTEXT])
    try:
        validate_context([AS_CONTEXT, COAR_CONTEXT])
        validate_context([AS_CONTEXT, DEPRECATED_COAR_CONTEXT])
    except ValidationError as exc:
        pytest.fail(f"Should not have raised {exc}")


def test_validate_required_keys_all():
    with pytest.raises(ValidationError) as exc_info:
        validate_required_keys({})
    exc = exc_info.value
    assert len(exc.detail) == 6
    errors = {}
    for error in exc.args[0]:
        errors.update(error.detail)
    for k in ["@context", "id", "type", "origin", "target", "object"]:
        assert k in errors


def test_validate_required_keys_context(notification_payload):
    notification_payload.pop("@context")
    with pytest.raises(ValidationError, match="must contain a @context list"):
        validate_required_keys(notification_payload)
    notification_payload["@context"] = "string instead of list"
    with pytest.raises(ValidationError, match="must contain a @context list"):
        validate_required_keys(notification_payload)


def test_validate_required_keys_id(notification_payload):
    notification_payload.pop("id")
    with pytest.raises(ValidationError, match="must contain an id"):
        validate_required_keys(notification_payload)
    notification_payload["id"] = ""
    with pytest.raises(ValidationError, match="must contain an id"):
        validate_required_keys(notification_payload)


def test_validate_required_keys_type(notification_payload):
    notification_payload.pop("type")
    with pytest.raises(ValidationError, match="must contain a type"):
        validate_required_keys(notification_payload)
    notification_payload["type"] = ""
    with pytest.raises(ValidationError, match="must contain a type"):
        validate_required_keys(notification_payload)


def test_validate_required_keys_origin(notification_payload):
    notification_payload.pop("origin")
    with pytest.raises(ValidationError, match="must contain an origin dict"):
        validate_required_keys(notification_payload)
    notification_payload["origin"] = "string instead of dict"
    with pytest.raises(ValidationError, match="must contain an origin dict"):
        validate_required_keys(notification_payload)
    notification_payload["origin"] = {"id": "ok", "type": "ok"}
    try:
        validate_required_keys(notification_payload)
    except Exception as exc:
        pytest.fail(f"Should not have raised {exc}")


def test_validate_required_keys_target(notification_payload):
    notification_payload.pop("target")
    with pytest.raises(ValidationError, match="must contain a target dict"):
        validate_required_keys(notification_payload)
    notification_payload["target"] = "string instead of dict"
    with pytest.raises(ValidationError, match="must contain a target dict"):
        validate_required_keys(notification_payload)
    notification_payload["target"] = {"id": "ok", "type": "ok", "inbox": "ok"}
    try:
        validate_required_keys(notification_payload)
    except Exception as exc:
        pytest.fail(f"Should not have raised {exc}")


def test_validate_required_keys_object(notification_payload):
    notification_payload.pop("object")
    with pytest.raises(ValidationError, match="must contain an object dict"):
        validate_required_keys(notification_payload)
    notification_payload["object"] = "string instead of dict"
    with pytest.raises(ValidationError, match="must contain an object dict"):
        validate_required_keys(notification_payload)
    notification_payload["object"] = {"id": "ok"}
    try:
        validate_required_keys(notification_payload)
    except Exception as exc:
        pytest.fail(f"Should not have raised {exc}")


@pytest.mark.parametrize(
    "url1,url2,expected",
    [
        ("https://inbox.swh.network", "https://inbox.swh.network", True),
        ("https://inbox.swh.network/", "https://inbox.swh.network", True),
        ("https://inbox.swh.network", "https://inbox.swh.network/", True),
        ("https://inbox.swh.network/a", "https://inbox.swh.network/", False),
    ],
)
def test_url_match(url1, url2, expected):
    assert url_match(url1, url2) is expected


@pytest.mark.django_db
def test_validate_target_inbox(rf, django_user_model, settings):
    organization = Organization.objects.create(
        url="http://org.local", inbox="http://inbox", name="Other"
    )
    user = django_user_model.objects.create_user(
        "test@localhost", organization=organization
    )

    settings.SWH_AUTH_SERVER_URL = ""
    request = rf.get("/")
    request.user = user

    assert validate_target_inbox(request, {"target": {"inbox": "http://testserver/"}})
    assert validate_target_inbox(request, {"target": {"inbox": "http://testserver/"}})
    with pytest.raises(ValidationError):
        validate_target_inbox(request, {"target": {"inbox": ""}})
    with pytest.raises(ValidationError, match="http://target"):
        validate_target_inbox(request, {"target": {"inbox": "http://target"}})


def test_context_processor(rf, settings):
    request = rf.get("/")
    settings.CN_VERSION = "s.w.h"
    context = context_processor(request)
    assert context["CN_VERSION"] == "s.w.h"

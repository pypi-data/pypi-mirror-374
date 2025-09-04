# Copyright (C) 2025  The Software Heritage developers
# See the AUTHORS file at the top-level directory of this distribution
# License: GNU Affero General Public License version 3, or any later version
# See top-level LICENSE file for more information
import json

from pyld import jsonld

from swh.coarnotify.server.handlers import get_handler, mention
from swh.coarnotify.server.models import InboundNotification, Statuses
from swh.model.model import MetadataAuthority, MetadataAuthorityType


def test_get_handler_unknown(inbound_notification):
    inbound_notification.payload["type"] = ["Unhandled"]
    assert get_handler(inbound_notification) is None
    assert inbound_notification.status == Statuses.UNPROCESSABLE


def test_get_handler_mention(inbound_notification):
    assert get_handler(inbound_notification) == mention


def test_mention_origin_url_context_data_id(inbound_notification):
    inbound_notification.payload["context"]["id"] = "https://wrong.url"
    assert (
        inbound_notification.payload["context"]["id"]
        != inbound_notification.payload["object"]["as:subject"]
    )

    mention(inbound_notification)

    assert inbound_notification.status == Statuses.REJECTED
    assert "does not match object as:subject" in inbound_notification.error_message


def test_mention_context_type(inbound_notification):
    inbound_notification.payload["context"]["type"] = ["sorg:Drawing"]

    mention(inbound_notification)

    assert inbound_notification.status == Statuses.REJECTED
    assert "does not contain sorg:AboutPage" in inbound_notification.error_message


def test_mention_storage(storage, inbound_notification, mocker, default_origin):
    mocker.patch("swh.coarnotify.server.handlers.get_storage", return_value=storage)
    mention(inbound_notification)

    metadata_authority = MetadataAuthority(
        type=MetadataAuthorityType.REGISTRY,
        url=inbound_notification.payload["origin"]["id"],
    )
    expanded_payload = jsonld.expand(inbound_notification.payload)
    extrinsic_metadata = storage.raw_extrinsic_metadata_get(
        target=default_origin.swhid(), authority=metadata_authority
    )

    assert len(extrinsic_metadata.results) == 1
    payload = extrinsic_metadata.results[0].metadata.decode()
    assert json.loads(payload) == expanded_payload


def test_mention_reply(storage, inbound_notification, mocker, default_origin):
    mocker.patch("swh.coarnotify.server.handlers.get_storage", return_value=storage)
    mention(inbound_notification)

    assert inbound_notification.status == Statuses.ACCEPTED
    outbound_notification = inbound_notification.replied_by.first()
    assert (
        outbound_notification.payload["summary"]
        == f"Stored mention for {default_origin.swhid()}"
    )


def test_mention_origin_not_archived(inbound_notification, mocker, default_origin):
    # note: we don't use the storage fixture here, so default_origin is not added
    mention(inbound_notification)

    assert inbound_notification.status == Statuses.REJECTED
    outbound_notification = inbound_notification.replied_by.first()

    assert default_origin.url in outbound_notification.payload["summary"]
    assert "has not yet been archived" in outbound_notification.payload["summary"]


def test_mention_origin_alternative_url(
    storage, notification_payload, mocker, default_origin, partner
):
    notification_payload["object"]["as:object"] = default_origin.url + "/"
    inbound_notification = InboundNotification.objects.create(
        id="00000000-0000-0000-0000-000000000000",
        payload=notification_payload,
        sender=partner,
        raw_payload=notification_payload,
    )

    mocker.patch("swh.coarnotify.server.handlers.get_storage", return_value=storage)
    mention(inbound_notification)

    assert inbound_notification.status == Statuses.ACCEPTED
    outbound_notification = inbound_notification.replied_by.first()

    # the metadata has been associated to the origin found in the archive
    # (default_origin), not the alternative one with a trailing slash
    assert (
        outbound_notification.payload["summary"]
        == f"Stored mention for {default_origin.swhid()}"
    )

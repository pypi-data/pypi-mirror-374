# Copyright (C) 2025  The Software Heritage developers
# See the AUTHORS file at the top-level directory of this distribution
# License: GNU Affero General Public License version 3, or any later version
# See top-level LICENSE file for more information

"""Utils."""

from typing import Any
import uuid

from django.conf import settings
from django.utils.module_loading import import_string
from rest_framework import serializers
from rest_framework.request import Request

from .models import InboundNotification, OutboundNotification, Statuses

AS_CONTEXT = "https://www.w3.org/ns/activitystreams"
COAR_CONTEXT = "https://coar-notify.net"
DEPRECATED_COAR_CONTEXT = "https://purl.org/coar/notify"

DEFAULT_CONTEXT = [AS_CONTEXT, COAR_CONTEXT]


def send_cn(notification: OutboundNotification) -> bool:
    """Send a COAR Notification.

    The client is defined in settings.CN_CLIENT

    Args:
        notification: an OutboundNotification

    Returns:
        True if the recipient inbox has been reached.
    """
    COARClient = import_string(settings.CN_CLIENT)
    client = COARClient()
    try:
        client.send(notification.payload)
        notification.status = Statuses.PROCESSED
    except Exception as e:
        notification.status = Statuses.REJECTED
        notification.error_message = str(e)
    notification.save()
    return notification.status == Statuses.PROCESSED


def create_accept_cn(
    cn: InboundNotification, summary: str | None = None
) -> OutboundNotification:
    """Create an Outbound CN to reply to an acceptable CN.

    https://coar-notify.net/specification/1.0.1/accept/

    Args:
        cn: an inbound notification
        summary: an optional summary to include in the CN

    Returns:
        an outbound CN
    """
    #
    original_payload = cn.payload.copy()
    at_context = original_payload.pop("@context")
    object_ = original_payload
    pk = uuid.uuid4()
    payload = {
        "@context": at_context,
        "id": f"urn:uuid:{pk}",
        "inReplyTo": f"urn:uuid:{cn.pk}",
        "type": "Accept",
        "object": object_,
        "origin": settings.CN_ORIGIN,
        "target": original_payload["origin"],
    }
    if summary:
        payload["summary"] = summary
    return OutboundNotification.objects.create(id=pk, payload=payload, in_reply_to=cn)


def create_unprocessable_cn(notification: InboundNotification) -> OutboundNotification:
    """Create an Outbound CN to reply to an unprocessable CN.

    https://coar-notify.net/specification/1.0.1/unprocessable/

    Args:
        notification: an inbound CN

    Returns:
        an outbound CN
    """
    pk = uuid.uuid4()
    payload = {
        "@context": DEFAULT_CONTEXT,
        "id": f"urn:uuid:{pk}",
        "inReplyTo": f"urn:uuid:{notification.pk}",
        "type": ["Flag", "coar-notify:UnprocessableNotification"],
        "summary": notification.error_message,
        "object": {
            "id": f"urn:uuid:{notification.pk}",
        },
        "origin": settings.CN_ORIGIN,
        "target": notification.payload["origin"],
    }
    return OutboundNotification.objects.create(
        id=pk, payload=payload, in_reply_to=notification
    )


def create_reject_cn(notification: InboundNotification) -> OutboundNotification:
    """Create an Outbound CN to reply to a rejected CN.

    https://coar-notify.net/specification/1.0.1/reject/

    Args:
        notification: an inbound CN

    Returns:
        an outbound CN
    """
    #
    original_payload = notification.payload.copy()
    original_payload.pop("@context")
    object_ = original_payload
    pk = uuid.uuid4()
    payload = {
        "@context": DEFAULT_CONTEXT,
        "id": f"urn:uuid:{pk}",
        "inReplyTo": f"urn:uuid:{notification.pk}",
        "type": "Reject",
        "summary": notification.error_message,
        "object": object_,
        "origin": settings.CN_ORIGIN,
        "target": original_payload["origin"],
    }
    return OutboundNotification.objects.create(
        id=pk, payload=payload, in_reply_to=notification
    )


def uuid_from_urn(urn: str) -> uuid.UUID:
    """Extract a UUID from a URN.

    Args:
        urn: a UUID URN (urn:uuid:xxx)

    Raises:
        serializers.ValidationError: URN is not a valid UUID URN

    Returns:
        a uuid
    """
    try:
        scheme, nid, nss = urn.split(":")
    except (ValueError, AttributeError):
        raise serializers.ValidationError("Expecting URN rendered in URI syntax")
    if scheme != "urn":
        raise serializers.ValidationError("Not a URN")
    if nid != "uuid":
        raise serializers.ValidationError("Not a UUID URN")
    try:
        return uuid.UUID(nss)
    except ValueError:
        raise serializers.ValidationError("Invalid uuid")


def to_sorted_tuple(value: str | list[str]) -> tuple:
    """Convert a single string or a list to a sorted tuple.

    Args:
        value: a string or a list

    Returns:
        a sorted tuple of strings
    """
    if isinstance(value, str):
        return (value,)
    return tuple(sorted(value))


def validate_sender_inbox(request: Request, payload: dict) -> bool:
    """Validate sender's inbox.

    The value of origin inbox must match the value from the authenticated sender.

    Args:
        request: an HTTP request
        payload: the CN payload

    Raises:
        serializers.ValidationError: inbox urls mismatch

    Returns:
        True if the user's inbox url matches the one in the notification
    """
    if not request.user.is_authenticated:
        raise serializers.ValidationError("User is not authenticated")
    inbox_url = request.user.organization.inbox
    if not payload["origin"]["inbox"] or not url_match(
        payload["origin"]["inbox"], inbox_url
    ):
        raise serializers.ValidationError(
            (
                f"User inbox {inbox_url} does not match "
                f"Origin inbox {payload['origin']['inbox']} in the notification"
            )
        )
    return True


def validate_target_inbox(request: Request, payload: dict) -> bool:
    """Validate target's inbox.

    The value of target inbox must match the SWH inbox url.


    Args:
        request: an HTTP request
        payload: the CN payload

    Raises:
        serializers.ValidationError: inbox urls mismatch

    Returns:
        True if our inbox url matches the one in the notification
    """
    swh_inbox_url = request.build_absolute_uri()  # XXX should it be an env var ?
    if not url_match(payload["target"]["inbox"], swh_inbox_url):
        raise serializers.ValidationError(
            f"Software Heritage inbox url {swh_inbox_url} does not match "
            f"Target inbox {payload['target']['inbox']} in the notification"
        )
    return True


def validate_context(at_context: list[str]) -> None:
    """Validate the notification @context.

    https://coar-notify.net/specification/1.0.1/

    Args:
        at_context: a list of URI

    Raises:
        serializers.ValidationError: `at_context` does not match the specs
    """
    if AS_CONTEXT not in at_context:
        raise serializers.ValidationError(
            f"Notification context must include {AS_CONTEXT}"
        )

    if (COAR_CONTEXT in at_context and DEPRECATED_COAR_CONTEXT in at_context) or (
        COAR_CONTEXT not in at_context and DEPRECATED_COAR_CONTEXT not in at_context
    ):
        raise serializers.ValidationError(
            "Notification context must include one of "
            f"{COAR_CONTEXT} or {DEPRECATED_COAR_CONTEXT}"
        )


def validate_required_keys(payload: dict) -> None:
    """Validate the payload shape.

    https://coar-notify.net/specification/1.0.1/

    Args:
        payload: the CN payload

    Raises:
        serializers.ValidationError: payload does not match the specs
    """
    errors: list[serializers.ValidationError] = []

    if (
        "@context" not in payload
        or not payload.get("@context")
        or not isinstance(payload.get("@context"), list)
    ):
        errors.append(
            serializers.ValidationError(
                {"@context": "The activity must contain a @context list"}
            )
        )
    if "id" not in payload or not payload.get("id"):
        errors.append(
            serializers.ValidationError({"id": "The activity must contain an id"})
        )
    if "type" not in payload or not payload.get("type"):
        errors.append(
            serializers.ValidationError({"type": "The activity must contain a type"})
        )
    if (
        "origin" not in payload
        or not payload.get("origin")
        or not isinstance(payload.get("origin"), dict)
    ):
        errors.append(
            serializers.ValidationError(
                {"origin": "The activity must contain an origin dict"}
            )
        )
    else:
        origin = payload["origin"]
        if "id" not in origin or not origin.get("id"):
            errors.append(
                serializers.ValidationError(
                    {"origin": "The activity origin must contain an id"}
                )
            )
        if "type" not in origin or not origin.get("type"):
            errors.append(
                serializers.ValidationError(
                    {"origin": "The activity origin must contain a type"}
                )
            )
    if (
        "target" not in payload
        or not payload.get("target")
        or not isinstance(payload.get("target"), dict)
    ):
        errors.append(
            serializers.ValidationError(
                {"target": "The activity must contain a target dict"}
            )
        )
    else:
        target = payload["target"]
        if "id" not in target or not target.get("id"):
            errors.append(
                serializers.ValidationError(
                    {"target": "The activity target must contain an id"}
                )
            )
        if "type" not in target or not target.get("type"):
            errors.append(
                serializers.ValidationError(
                    {"target": "The activity target must contain a type"}
                )
            )
        if "inbox" not in target or not target.get("inbox"):
            errors.append(
                serializers.ValidationError(
                    {"target": "The activity target must contain an inbox"}
                )
            )
    if (
        "object" not in payload
        or not payload.get("object")
        or not isinstance(payload.get("object"), dict)
    ):
        errors.append(
            serializers.ValidationError(
                {"object": "The activity must contain an object dict"}
            )
        )
    else:
        object_ = payload["object"]
        if "id" not in object_ or not object_.get("id"):
            errors.append(
                serializers.ValidationError(
                    {"object": "The activity object must contain an id"}
                )
            )

    if errors:
        # mypy complains about the type here but it matches the docs
        # https://www.django-rest-framework.org/api-guide/exceptions/#validationerror
        raise serializers.ValidationError(errors)  # type: ignore


def reject(notification: InboundNotification, error_message: str) -> None:
    """Mark notification as rejected and send a Reject CN.

    Args:
        notification: an InboundNotification
        error_message : a reason for the rejection
    """
    notification.status = Statuses.REJECTED
    notification.error_message = error_message
    notification.save()
    rejected_cn = create_reject_cn(notification)
    send_cn(rejected_cn)


def unprocessable(notification: InboundNotification, error_message: str) -> None:
    """Mark notification as unprocessable and send an Unprocessable CN.

    Args:
        notification: an InboundNotification
        error_message : a reason for the rejection
    """
    notification.status = Statuses.UNPROCESSABLE
    notification.error_message = error_message
    notification.save()
    unprocessable_cn = create_unprocessable_cn(notification)
    send_cn(unprocessable_cn)


def inbox_headers(request: Request) -> dict[str, str]:
    """Headers to signpost our Inbox address.

    Args:
        request: an HTTP request

    Returns:
        dict[str, str]: headers to include on our views
    """
    return {
        "Link": (
            f'<{request.build_absolute_uri()}>; rel="http://www.w3.org/ns/ldp#inbox'
        )
    }


def url_match(url1: str, url2: str) -> bool:
    """Compare two URLs ignoring trailing slashes.

    Args:
        url1: an URL
        url2: another URL

    Returns:
        True if the url matches
    """
    return url1.rstrip("/") == url2.rstrip("/")


def context_processor(request: Request) -> dict[str, Any]:
    """Inject variables in templates' context.

    Args:
        request: an HTTP request

    Returns:
        A dict of variables accessible in all templates
    """
    return {"CN_VERSION": settings.CN_VERSION}

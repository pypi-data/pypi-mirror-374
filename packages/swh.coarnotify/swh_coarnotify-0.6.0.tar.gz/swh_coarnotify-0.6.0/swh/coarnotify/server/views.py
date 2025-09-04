# Copyright (C) 2025  The Software Heritage developers
# See the AUTHORS file at the top-level directory of this distribution
# License: GNU Affero General Public License version 3, or any later version
# See top-level LICENSE file for more information

"""Views."""

from http import HTTPStatus

from django.db.models import QuerySet
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render
from pyld import jsonld
from rest_framework.decorators import api_view, permission_classes
from rest_framework.exceptions import (
    NotAuthenticated,
    ParseError,
    PermissionDenied,
    ValidationError,
)
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response

from .handlers import get_handler
from .models import InboundNotification, OutboundNotification
from .utils import (
    inbox_headers,
    unprocessable,
    uuid_from_urn,
    validate_context,
    validate_required_keys,
    validate_sender_inbox,
    validate_target_inbox,
)


class Receipt(Response):
    """A 201 HTTP Response containing the url of the created notification."""

    def __init__(self, notification: InboundNotification, request: Request):
        """Init the Response.

        Args:
            notification: the notification we created
            request: the HTTP request
        """
        headers = {
            "Location": request.build_absolute_uri(notification.get_absolute_url())
        }
        super().__init__(status=HTTPStatus.CREATED, headers=headers)


class Discover(Response):
    """A 200 HTTP Response containing the url of our inbox."""

    def __init__(self, request: Request):
        """Init the Response.

        Args:
            request: the HTTP request
        """
        super().__init__(status=HTTPStatus.OK, headers=inbox_headers(request))


class UserInbox(Response):
    """A 200 HTTP Response containing the url of our notifications sent by a user."""

    def __init__(
        self, request: Request, notifications: "QuerySet[InboundNotification]"
    ):
        """Init the Response.

        Args:
            request: the HTTP request
            notifications: a queryset if notifications
        """
        data = {
            "@context": "http://www.w3.org/ns/ldp",
            "@id": request.build_absolute_uri(),
            "contains": [
                request.build_absolute_uri(n.get_absolute_url()) for n in notifications
            ],
        }
        super().__init__(data=data, status=HTTPStatus.OK)


def process_notification(request: Request) -> InboundNotification:
    """Process an inbound COAR Notification.

    - structural payload validation
    - route notification to the proper handler depending on its type(s)

    Args:
        request: an HTTP request

    Raises:
        ParseError: invalid jsonld
        ValidationError: invalid ``@context`` or inbox url
        BadRequest: a CN with this id has already been processed
        UnprocessableException: the CN was deemed unprocessable
        NotAuthenticated: missing request.user

    Returns:
        An HTTP response with an error code if the COAR Notification is structurally
        invalid, or a simple JSON response with a message key containing the outcome
        of the process (which is also send to the sender Inbox as a COAR Notification).
    """

    if not request.user.is_authenticated:
        raise NotAuthenticated()

    # Validate structural integrity
    validate_required_keys(request.data)
    try:
        payload = jsonld.compact(request.data, request.data["@context"])
    except jsonld.JsonLdError:
        # hard to extract a meaningful error message from pyld
        raise ParseError("Unable to process json-ld")

    validate_context(payload["@context"])
    validate_sender_inbox(request, payload)

    # Is it a reply ?
    in_reply_to: OutboundNotification | None = None
    if reply_urn := payload.get("inReplyTo"):
        in_reply_to = OutboundNotification.objects.filter(
            id=uuid_from_urn(reply_urn)
        ).first()  # XXX should we reject the notification if in_reply_to is invalid ?

    # Store CN
    notification_id = uuid_from_urn(payload["id"])
    if InboundNotification.objects.filter(id=notification_id).exists():
        raise ValidationError(
            f"A COAR Notification with the id {notification_id} has already "
            "been handled."
        )
    notification = InboundNotification.objects.create(
        id=notification_id,
        in_reply_to=in_reply_to,
        payload=payload,
        raw_payload=request.data,
        sender=request.user.organization,
    )

    # at this stage 1) the CN sender has been authenticated 2) the user's inbox match
    # the inbox's url in the CN payload 3) the CN has been stored in the db so it
    # should be safe to reply to it

    # Validate swh's inbox
    try:
        validate_target_inbox(request, payload)
    except ValidationError as exc:
        error_msg = (
            str(exc.detail[0]) if isinstance(exc.detail, list) else str(exc.detail)
        )
        unprocessable(notification, error_msg)
        return notification

    # Find an handler to process this CN
    if handler := get_handler(notification):
        handler(notification)

    return notification


@api_view(["GET", "POST", "HEAD"])
def inbox(request) -> Response | HttpResponse:
    """Main inbox API endpoint.

    The response returned depends on the method used by the client:

    - HEAD: returns LDN inbox discovery headers
    - GET:
        - unauthenticated: an HTML response
        - authenticated: user's inbox
    - POST:
        - unauthenticated: an exception
        - authenticated: the result of the payload processing

    Args:
        request: an HTTP request

    Raises:
        PermissionDenied: unable to auth user

    Returns:
        An HTTP response
    """
    if request.method == "HEAD":
        return Discover(request)
    if request.method == "GET" and not request.user.is_authenticated:
        response = render(request, "index.html")
        # include LDN inbox discovery headers
        for k, v in inbox_headers(request).items():
            response[k] = v
        return response
    if not request.user.is_authenticated:
        raise PermissionDenied()
    if request.method == "GET":
        return UserInbox(
            request,
            InboundNotification.objects.filter(sender=request.user.organization),
        )
    notification = process_notification(request)
    return Receipt(notification, request)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def read_notification(request, pk) -> Response:
    notification = get_object_or_404(InboundNotification, pk=pk)
    if notification.sender != request.user.organization:
        raise PermissionDenied()
    return Response(notification.raw_payload)

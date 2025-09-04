# Copyright (C) 2025  The Software Heritage developers
# See the AUTHORS file at the top-level directory of this distribution
# License: GNU Affero General Public License version 3, or any later version
# See top-level LICENSE file for more information
"""COAR Notify clients."""

import pprint

from django.conf import settings
import requests


class COARNotifyClient:
    """A basic CN client."""

    def _get_inbox_url(self, payload: dict) -> str:
        """Get target's inbox URL from the notification.

        Args:
            payload: an outbound notification payload

        Returns:
            an inbox URL
        """
        return payload["target"]["inbox"]

    def send(self, payload: dict) -> bool:
        """Send the notification using requests.

        Args:
            payload: an outbound notification payload

        Raises:
            request.HTTPError: the inbox rejected our notification

        Returns:
            True if the inbox accepted the notification
        """
        inbox_url = self._get_inbox_url(payload)
        headers = {"Content-type": "application/ld+json"}
        r = requests.post(
            inbox_url, json=payload, headers=headers, timeout=settings.CN_SEND_TIMEOUT
        )
        r.raise_for_status()
        return True


class DevCOARNotifyClient(COARNotifyClient):
    """CN client that sends notification to a single inbox URL."""

    def _get_inbox_url(self, payload: dict) -> str:
        """Get the dev inbox URL from the settings.

        Args:
            payload: an outbound notification payload

        Returns:
            the dev inbox URL
        """
        return settings.CN_INBOX_URL_OVERRIDE


class DummyCOARNotifyClient(COARNotifyClient):
    """Dummy CN client that does nothing."""

    def send(self, payload: dict):
        """Pretends to send the notification.

        Args:
            payload: an outbound notification payload

        Returns:
            Always returns True
        """
        return True


class ConsoleCOARNotifyClient(COARNotifyClient):
    """CN client that sends notification to the console."""

    def send(self, payload: dict) -> bool:
        """Send the notification using requests.

        Args:
            payload: an outbound notification payload

        Raises:
            request.HTTPError: the inbox rejected our notification

        Returns:
            True if the inbox accepted the notification
        """
        pprint.pprint(payload)
        print("-" * 79, "\n")
        return True

# Copyright (C) 2025  The Software Heritage developers
# See the AUTHORS file at the top-level directory of this distribution
# License: GNU Affero General Public License version 3, or any later version
# See top-level LICENSE file for more information
"""Organization CLI."""

from __future__ import annotations

from django.core.management.base import BaseCommand, CommandError, CommandParser
from django.db.models import Q

from swh.coarnotify.server.models import Organization


class Command(BaseCommand):
    help = "Creates an organization"

    def add_arguments(self, parser: CommandParser) -> None:
        """Get the required values to create an Organization.

        Args:
            parser: django's CommandParser
        """
        parser.add_argument("name", help="the organization's name")
        parser.add_argument("uri", help="a URI identifying the organization")
        parser.add_argument(
            "inbox", help=" the HTTP URI of the LDN inbox for the organization"
        )

    def handle(self, *args, **options) -> None:
        """Handle the command.

        Raises:
            CommandError: the Organization already exist
        """
        name = options["name"]
        uri = options["uri"]
        inbox = options["inbox"]

        if dupe := Organization.objects.filter(
            Q(name=name) | Q(url=uri) | Q(inbox=inbox)
        ).first():
            raise CommandError(
                f"The organization {dupe} already exists with some or all these values"
            )

        organization = Organization.objects.create(name=name, url=uri, inbox=inbox)

        self.stdout.write(self.style.SUCCESS(f"Successfully created {organization}"))

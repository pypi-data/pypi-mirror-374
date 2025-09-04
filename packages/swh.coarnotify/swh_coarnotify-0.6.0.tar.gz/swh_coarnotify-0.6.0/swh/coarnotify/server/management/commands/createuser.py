# Copyright (C) 2025  The Software Heritage developers
# See the AUTHORS file at the top-level directory of this distribution
# License: GNU Affero General Public License version 3, or any later version
# See top-level LICENSE file for more information
"""User CLI."""

import secrets

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError, CommandParser

from swh.coarnotify.server.models import Organization


class Command(BaseCommand):
    help = "Creates a user or a superuser"

    def add_arguments(self, parser: CommandParser) -> None:
        """Get the required values to create a user.

        Args:
            parser: django's CommandParser
        """
        parser.add_argument("email", help="the user's email")
        parser.add_argument(
            "organization",
            help="An organization's name",
            choices=Organization.objects.order_by("name").values_list(
                "name", flat=True
            ),
        )
        parser.add_argument(
            "--password",
            help="Use a specific password (otherwise a random one will be generated)",
        )
        parser.add_argument(
            "--superuser", action="store_true", help="the user will be an admin"
        )

    def handle(self, *args, **options) -> None:
        """Handle the command.

        Raises:
            CommandError: the user already exists
        """
        User = get_user_model()
        email = options["email"]
        if User.objects.filter(email=email).exists():
            raise CommandError(f"A user identified by {email} already exists")

        password = options["password"] or secrets.token_urlsafe(20)
        user_type = "superuser" if options["superuser"] else "user"
        organization = Organization.objects.get(name=options["organization"])
        if options["superuser"]:
            user = User.objects.create_superuser(
                email, password=password, organization=organization
            )
        else:
            user = User.objects.create_user(
                email, password=password, organization=organization
            )
        token = user.auth_token
        msg: list[str] = [
            f"Created {user_type} {user.email}",
            f"- auth token: {token.key}",
        ]
        # if the password was provided there's no need to output it again
        if options["password"]:
            msg.append(f"- password: {password}")
        self.stdout.write(self.style.SUCCESS("\n".join(msg)))

# Copyright (C) 2025  The Software Heritage developers
# See the AUTHORS file at the top-level directory of this distribution
# License: GNU Affero General Public License version 3, or any later version
# See top-level LICENSE file for more information
"""Dev fixtures."""

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from rest_framework.authtoken.models import Token

from swh.coarnotify.server.models import Organization


class Command(BaseCommand):
    help = "Creates an admin user and a test user for a local (non keycloak) env"

    def handle(self, *args, **options):
        User = get_user_model()

        admin_organization, _ = Organization.objects.get_or_create(
            url="http://swh.local",
            defaults={"inbox": "https://127.0.0.1", "name": "SWH"},
        )

        organization, _ = Organization.objects.get_or_create(
            url="http://partner.local",
            defaults={
                "inbox": "http://inbox.partner.local",
                "name": "Partner",
            },
        )

        # Admin admin@swh.local:password
        if not User.objects.filter(email="admin@swh.local").exists():
            User.objects.create_superuser(
                "admin@swh.local", password="password", organization=admin_organization
            )
        self.stdout.write(self.style.SUCCESS("Created the admin@swh.local superuser"))

        # A user allowed to send CN with token 12345
        authorized_user = User.objects.filter(email="member@partner.local").first()
        if not authorized_user:
            authorized_user = User.objects.create_user(
                "member@partner.local", organization=organization
            )
            Token.objects.filter(user=authorized_user).update(key="12345")
        self.stdout.write(
            self.style.SUCCESS("Created member@partner.local with token 12345")
        )

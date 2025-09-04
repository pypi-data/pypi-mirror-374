# Copyright (C) 2025  The Software Heritage developers
# See the AUTHORS file at the top-level directory of this distribution
# License: GNU Affero General Public License version 3, or any later version
# See top-level LICENSE file for more information
from django.core.management import call_command
from django.core.management.base import CommandError
import pytest

pytestmark = pytest.mark.django_db


def test_duplicate(member, partner):
    with pytest.raises(CommandError, match="already exists"):
        call_command(
            "createuser",
            (member.email, partner.name),
        )


def test_invalid_organization(member):
    with pytest.raises(CommandError, match="invalid choice"):
        call_command(
            "createuser",
            (member.email, "unknown partner"),
        )


def test_regular_user(partner, django_user_model):
    call_command(
        "createuser",
        ("user@example.local", partner),
    )
    user = django_user_model.objects.get(email="user@example.local")
    assert not user.is_staff
    assert not user.is_superuser


def test_password(partner, django_user_model):
    call_command(
        "createuser", ("user@example.local", partner), password="my password is rich"
    )
    user = django_user_model.objects.get(email="user@example.local")
    assert user.check_password("my password is rich")


def test_admin(partner, django_user_model):
    call_command("createuser", ("user@example.local", partner), superuser=True)
    user = django_user_model.objects.get(email="user@example.local")
    assert user.is_staff
    assert user.is_superuser

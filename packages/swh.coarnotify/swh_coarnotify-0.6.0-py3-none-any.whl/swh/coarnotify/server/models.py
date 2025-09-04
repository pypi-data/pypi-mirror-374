# Copyright (C) 2025  The Software Heritage developers
# See the AUTHORS file at the top-level directory of this distribution
# License: GNU Affero General Public License version 3, or any later version
# See top-level LICENSE file for more information

"""Models."""

from __future__ import annotations

from typing import cast
import uuid

from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.urls import reverse


class Organization(models.Model):
    """An organization."""

    name = models.CharField(max_length=150, blank=True)

    url = models.URLField(null=False, unique=True)
    """Organization URL (for discovery)."""
    inbox = models.URLField(null=False, unique=True)
    """LDN inbox URL."""

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return f"{self.name}"


class ActorManager(BaseUserManager):
    def create_user(
        self, email: str, password: str | None = None, **extra_fields
    ) -> "Actor":
        if not email:
            raise ValueError("Email is required")
        instance = self.model(email=self.normalize_email(email), **extra_fields)
        user = cast(Actor, instance)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email: str, password: str, **extra_fields) -> "Actor":
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        return self.create_user(email, password, **extra_fields)


class Actor(AbstractUser):
    """A member of an organization."""

    email = models.EmailField(unique=True)
    organization = models.ForeignKey(Organization, on_delete=models.PROTECT)
    name = models.CharField(max_length=150, blank=True)

    # mypy is not happy with this but it follows the recommended way of overriding
    # django's user model
    username = None  # type: ignore[assignment]
    first_name = None  # type: ignore[assignment]
    last_name = None  # type: ignore[assignment]
    objects = ActorManager()  # type: ignore[misc,assignment]

    USERNAME_FIELD = "email"
    EMAIL_FIELD = "email"
    REQUIRED_FIELDS = ["organization"]

    def __str__(self) -> str:
        return f"{self.name} <{self.email}>"


class Statuses(models.TextChoices):
    PENDING = "pending", "Pending"
    REJECTED = "rejected", "Rejected"
    ACCEPTED = "accepted", "Accepted"
    PROCESSED = "processed", "Processed"
    UNPROCESSABLE = "unprocessable", "Unprocessable"


class Notification(models.Model):
    """An abstract model for COAR Notification."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    status = models.CharField(max_length=20, choices=Statuses, default=Statuses.PENDING)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    payload = models.JSONField()
    error_message = models.TextField()

    class Meta:
        abstract = True

    def __str__(self) -> str:
        return str(self.id)


class InboundNotification(Notification):
    """Our inbox"""

    raw_payload = models.JSONField()
    in_reply_to = models.ForeignKey(
        "OutboundNotification",
        null=True,
        on_delete=models.SET_NULL,
        related_name="replied_by",
    )
    sender = models.ForeignKey(Organization, on_delete=models.SET_NULL, null=True)

    def get_absolute_url(self) -> str:
        return reverse("read", kwargs={"pk": self.pk})


class OutboundNotification(Notification):
    """Our outbox."""

    in_reply_to = models.ForeignKey(
        "InboundNotification",
        null=True,
        on_delete=models.SET_NULL,
        related_name="replied_by",
    )

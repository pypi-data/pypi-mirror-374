# Copyright (C) 2025  The Software Heritage developers
# See the AUTHORS file at the top-level directory of this distribution
# License: GNU Affero General Public License version 3, or any later version
# See top-level LICENSE file for more information
"""Admin interfaces."""

import json

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.urls import reverse
from django.utils.html import format_html

from .forms import ActorChangeForm, ActorCreationForm
from .models import Actor, InboundNotification, Organization, OutboundNotification


class ActorAdmin(UserAdmin):
    add_form = ActorCreationForm
    form = ActorChangeForm
    model = Actor
    list_display = (
        "email",
        "name",
        "organization",
        "is_staff",
        "is_active",
    )
    # list_filter = ("email", "is_staff", "is_active",)
    fieldsets = (
        (None, {"fields": ("organization", "email", "name", "password")}),
        ("Permissions", {"fields": ("is_staff", "is_active")}),
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "organization",
                    "email",
                    "password1",
                    "password2",
                    "is_staff",
                    "is_active",
                ),
            },
        ),
    )
    search_fields = ["email", "name", "organization__name"]
    ordering = ["name"]


admin.site.register(Actor, ActorAdmin)


@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "name",
        "url",
        "inbox",
        "created_at",
        "updated_at",
    ]
    search_fields = ["name", "url", "inbox"]
    ordering = ["-name"]


class NotificationAdmin(admin.ModelAdmin):
    """Base admin model for the CN."""

    list_display = [
        "created_at",
        "status",
        "get_payload",
        "get_in_reply_to",
    ]
    ordering = ["-created_at"]
    list_filter = ["status"]
    search_fields = ["payload"]
    date_hierarchy = "created_at"

    readonly_fields = ["payload", "in_reply_to", "id"]

    @admin.display(description="Payload")
    def get_payload(self, obj):
        return format_html("<pre>{}</pre>", json.dumps(obj.payload, indent=2))

    @admin.display(description="In reply to")
    def get_in_reply_to(self, obj):
        if obj.in_reply_to:
            link = reverse(
                f"admin:swh_coarnotify_server_{self.model.__qualname__.lower()}_change",
                args=[obj.in_reply_to.id],
            )
            return format_html('<a href="{}">{}</a>', link, obj.in_reply_to)
        else:
            return "-"


@admin.register(InboundNotification)
class InboundNotificationAdmin(NotificationAdmin):
    pass


@admin.register(OutboundNotification)
class OutboundNotificationAdmin(NotificationAdmin):
    pass

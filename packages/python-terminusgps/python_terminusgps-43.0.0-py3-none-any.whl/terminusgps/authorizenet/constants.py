from django.db import models
from django.utils.translation import gettext_lazy as _

ANET_XMLNS = "{AnetApi/xml/v1/schema/AnetApiSchema.xsd}"
"""Authorizenet XML namespace."""


class AuthorizenetSubscriptionStatus(models.TextChoices):
    """An Authorizenet subscription status."""

    ACTIVE = "active", _("Active")
    EXPIRED = "expired", _("Expired")
    SUSPENDED = "suspended", _("Suspended")
    CANCELED = "canceled", _("Canceled")
    TERMINATED = "terminated", _("Terminated")

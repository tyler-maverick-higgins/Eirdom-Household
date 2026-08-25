import hashlib
import secrets
from datetime import timedelta

from django.db import models
from django.utils import timezone
from django.utils.text import slugify

from config import settings


class Household(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True, max_length=150, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "household"
        verbose_name_plural = "households"
        ordering = ["name", "created_at"]

    def __str__(self) -> str:
        return self.name

    def save(self, *args, **kwargs):
        # Only generate a slug if it hasn't been set manually
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class HouseholdMembership(models.Model):
    household = models.ForeignKey(Household, related_name="memberships", on_delete=models.CASCADE)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, related_name="household_memberships", on_delete=models.CASCADE
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    class Roles(models.TextChoices):
        OWNER = "owner", "Owner"
        ADMINISTRATOR = "administrator", "Administrator"
        MEMBER = "member", "Member"
        GUEST = "guest", "Guest"

    role = models.CharField(
        max_length=20,
        choices=Roles.choices,
        default=Roles.MEMBER,
    )

    class Meta:
        verbose_name = "household membership"
        verbose_name_plural = "household memberships"
        ordering = ["household", "created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["household", "user"], name="unique_household_membership"
            )
        ]

    def __str__(self) -> str:
        status = "" if self.is_active else " — Inactive"
        role_label = self.Roles(self.role).label
        return f"{self.user} — {self.household} ({role_label}){status}"


class HouseholdInvitation(models.Model):
    household = models.ForeignKey(Household, related_name="invitations", on_delete=models.CASCADE)
    email = models.EmailField()
    role = models.CharField(
        max_length=20,
        choices=HouseholdMembership.Roles.choices,
        default=HouseholdMembership.Roles.MEMBER,
    )
    invited_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="household_invitations_sent",
        on_delete=models.CASCADE,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    token_hash = models.CharField(
        max_length=64,
        blank=True,
    )

    expires_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    accepted_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    last_sent_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        ACCEPTED = "accepted", "Accepted"
        DECLINED = "declined", "Declined"
        CANCELED = "canceled", "Canceled"

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
    )

    class Meta:
        verbose_name = "household invitation"
        verbose_name_plural = "household invitations"
        ordering = ["household", "created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["household", "email"],
                condition=models.Q(status="pending"),
                name="unique_pending_household_invitation",
            )
        ]

    def __str__(self) -> str:
        role_label = HouseholdMembership.Roles(self.role).label
        return f"{self.email} - {self.household} ({role_label}) - {self.status}"

    def generate_token(self) -> str:
        token = secrets.token_urlsafe(32)

        self.token_hash = hashlib.sha256(token.encode("utf-8")).hexdigest()

        self.expires_at = timezone.now() + timedelta(days=7)

        return token

    def token_matches(self, token: str) -> bool:
        if not self.token_hash:
            return False

        candidate_hash = hashlib.sha256(token.encode("utf-8")).hexdigest()

        return secrets.compare_digest(
            self.token_hash,
            candidate_hash,
        )

    @property
    def is_expired(self) -> bool:
        if self.expires_at is None:
            return True

        return timezone.now() >= self.expires_at

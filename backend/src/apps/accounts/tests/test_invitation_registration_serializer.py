from datetime import timedelta
from typing import cast

import pytest
from django.utils import timezone

from apps.accounts.models import User
from apps.accounts.serializers import InvitationRegistrationSerializer
from apps.households.models import (
    Household,
    HouseholdInvitation,
    HouseholdMembership,
)


@pytest.fixture
def inviter():
    return User.objects.create_user(
        username="owner",
        email="owner@example.com",
        first_name="Household",
        last_name="Owner",
        password="test-password-123",
    )


@pytest.fixture
def household():
    return Household.objects.create(
        name="Higgins Household",
    )


@pytest.fixture
def invitation(household, inviter):
    HouseholdMembership.objects.create(
        household=household,
        user=inviter,
        role=HouseholdMembership.Roles.OWNER,
    )

    return HouseholdInvitation.objects.create(
        household=household,
        email="invitee@example.com",
        role=HouseholdMembership.Roles.MEMBER,
        invited_by=inviter,
    )


@pytest.fixture
def invitation_token(invitation):
    token = invitation.generate_token()

    invitation.save(
        update_fields=[
            "token_hash",
            "expires_at",
            "updated_at",
        ]
    )

    return token


@pytest.fixture
def valid_payload(invitation_token):
    return {
        "token": invitation_token,
        "username": "new-user",
        "first_name": "New",
        "last_name": "User",
        "password": "VeryStrongPassword123!",
    }


@pytest.mark.django_db
def test_valid_invitation_registration_creates_user(
    invitation,
    valid_payload,
):
    serializer = InvitationRegistrationSerializer(
        data=valid_payload,
    )

    assert serializer.is_valid(), serializer.errors

    user = cast(User, serializer.save())

    assert user.username == "new-user"
    assert user.email == invitation.email
    assert user.first_name == "New"
    assert user.last_name == "User"
    assert user.check_password("VeryStrongPassword123!")


@pytest.mark.django_db
def test_registration_email_comes_from_invitation(
    invitation,
    valid_payload,
):
    payload = {
        **valid_payload,
        "email": "attacker@example.com",
    }

    serializer = InvitationRegistrationSerializer(
        data=payload,
    )

    assert serializer.is_valid(), serializer.errors

    user = cast(User, serializer.save())

    assert user.email == invitation.email
    assert user.email != "attacker@example.com"


@pytest.mark.django_db
def test_first_name_is_required(
    valid_payload,
):
    payload = {
        **valid_payload,
        "first_name": "",
    }

    serializer = InvitationRegistrationSerializer(
        data=payload,
    )

    assert serializer.is_valid() is False
    assert "first_name" in serializer.errors


@pytest.mark.django_db
def test_last_name_is_required(
    valid_payload,
):
    payload = {
        **valid_payload,
        "last_name": "",
    }

    serializer = InvitationRegistrationSerializer(
        data=payload,
    )

    assert serializer.is_valid() is False
    assert "last_name" in serializer.errors


@pytest.mark.django_db
def test_username_is_required(
    valid_payload,
):
    payload = {
        **valid_payload,
        "username": "",
    }

    serializer = InvitationRegistrationSerializer(
        data=payload,
    )

    assert serializer.is_valid() is False
    assert "username" in serializer.errors


@pytest.mark.django_db
def test_duplicate_username_is_rejected(
    valid_payload,
):
    User.objects.create_user(
        username="new-user",
        email="other@example.com",
        password="test-password-123",
    )

    serializer = InvitationRegistrationSerializer(
        data=valid_payload,
    )

    assert serializer.is_valid() is False
    assert "username" in serializer.errors


@pytest.mark.django_db
def test_duplicate_username_lookup_is_case_insensitive(
    valid_payload,
):
    User.objects.create_user(
        username="NEW-USER",
        email="other@example.com",
        password="test-password-123",
    )

    serializer = InvitationRegistrationSerializer(
        data=valid_payload,
    )

    assert serializer.is_valid() is False
    assert "username" in serializer.errors


@pytest.mark.django_db
def test_existing_account_for_invited_email_is_rejected(
    invitation,
    valid_payload,
):
    User.objects.create_user(
        username="existing-user",
        email=invitation.email,
        password="test-password-123",
    )

    serializer = InvitationRegistrationSerializer(
        data=valid_payload,
    )

    assert serializer.is_valid() is False
    assert "token" in serializer.errors


@pytest.mark.django_db
def test_existing_account_email_lookup_is_case_insensitive(
    invitation,
    valid_payload,
):
    User.objects.create_user(
        username="existing-user",
        email=invitation.email.upper(),
        password="test-password-123",
    )

    serializer = InvitationRegistrationSerializer(
        data=valid_payload,
    )

    assert serializer.is_valid() is False
    assert "token" in serializer.errors


@pytest.mark.django_db
def test_invalid_invitation_token_is_rejected(
    valid_payload,
):
    payload = {
        **valid_payload,
        "token": "not-a-real-token",
    }

    serializer = InvitationRegistrationSerializer(
        data=payload,
    )

    assert serializer.is_valid() is False
    assert "token" in serializer.errors


@pytest.mark.django_db
def test_expired_invitation_is_rejected(
    invitation,
    valid_payload,
):
    invitation.expires_at = timezone.now() - timedelta(minutes=1)
    invitation.save(
        update_fields=[
            "expires_at",
            "updated_at",
        ]
    )

    serializer = InvitationRegistrationSerializer(
        data=valid_payload,
    )

    assert serializer.is_valid() is False
    assert "token" in serializer.errors


@pytest.mark.django_db
@pytest.mark.parametrize(
    "invitation_status",
    [
        HouseholdInvitation.Status.ACCEPTED,
        HouseholdInvitation.Status.DECLINED,
        HouseholdInvitation.Status.CANCELED,
    ],
)
def test_non_pending_invitation_is_rejected(
    invitation,
    valid_payload,
    invitation_status,
):
    invitation.status = invitation_status
    invitation.save(
        update_fields=[
            "status",
            "updated_at",
        ]
    )

    serializer = InvitationRegistrationSerializer(
        data=valid_payload,
    )

    assert serializer.is_valid() is False
    assert "token" in serializer.errors


@pytest.mark.django_db
def test_weak_password_is_rejected(
    valid_payload,
):
    payload = {
        **valid_payload,
        "password": "password",
    }

    serializer = InvitationRegistrationSerializer(
        data=payload,
    )

    assert serializer.is_valid() is False
    assert "password" in serializer.errors


@pytest.mark.django_db
def test_names_are_trimmed(
    valid_payload,
):
    payload = {
        **valid_payload,
        "first_name": "  New  ",
        "last_name": "  User  ",
    }

    serializer = InvitationRegistrationSerializer(
        data=payload,
    )

    assert serializer.is_valid(), serializer.errors

    user = cast(User, serializer.save())

    assert user.first_name == "New"
    assert user.last_name == "User"

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
def test_registration_serializer_exposes_only_expected_fields():
    serializer = cast(
        InvitationRegistrationSerializer,
        InvitationRegistrationSerializer(),
    )

    assert set(serializer.fields) == {
        "token",
        "username",
        "first_name",
        "last_name",
        "password",
    }


@pytest.mark.django_db
def test_registration_serializer_does_not_expose_privileged_user_fields():
    serializer = cast(
        InvitationRegistrationSerializer,
        InvitationRegistrationSerializer(),
    )

    prohibited_fields = {
        "email",
        "is_active",
        "is_staff",
        "is_superuser",
        "groups",
        "user_permissions",
        "last_login",
        "date_joined",
    }

    assert prohibited_fields.isdisjoint(serializer.fields.keys())


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
def test_registration_creates_normal_steward_account(
    valid_payload,
):
    serializer = InvitationRegistrationSerializer(
        data=valid_payload,
    )

    assert serializer.is_valid(), serializer.errors

    user = cast(User, serializer.save())

    assert user.is_active is True
    assert user.is_staff is False
    assert user.is_superuser is False


@pytest.mark.django_db
def test_registration_password_is_hashed(
    valid_payload,
):
    raw_password = valid_payload["password"]

    serializer = InvitationRegistrationSerializer(
        data=valid_payload,
    )

    assert serializer.is_valid(), serializer.errors

    user = cast(User, serializer.save())

    assert user.password != raw_password
    assert user.check_password(raw_password) is True


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
def test_registration_cannot_set_staff_flag(
    valid_payload,
):
    payload = {
        **valid_payload,
        "is_staff": True,
    }

    serializer = InvitationRegistrationSerializer(
        data=payload,
    )

    assert serializer.is_valid(), serializer.errors

    user = cast(User, serializer.save())

    assert user.is_staff is False
    assert user.is_superuser is False


@pytest.mark.django_db
def test_registration_cannot_set_superuser_flag(
    valid_payload,
):
    payload = {
        **valid_payload,
        "is_superuser": True,
    }

    serializer = InvitationRegistrationSerializer(
        data=payload,
    )

    assert serializer.is_valid(), serializer.errors

    user = cast(User, serializer.save())

    assert user.is_staff is False
    assert user.is_superuser is False


@pytest.mark.django_db
def test_registration_cannot_override_active_flag(
    valid_payload,
):
    payload = {
        **valid_payload,
        "is_active": False,
    }

    serializer = InvitationRegistrationSerializer(
        data=payload,
    )

    assert serializer.is_valid(), serializer.errors

    user = cast(User, serializer.save())

    assert user.is_active is True


@pytest.mark.django_db
def test_registration_cannot_assign_groups(
    valid_payload,
):
    payload = {
        **valid_payload,
        "groups": [1, 2, 3],
    }

    serializer = InvitationRegistrationSerializer(
        data=payload,
    )

    assert serializer.is_valid(), serializer.errors

    user = cast(User, serializer.save())

    assert user.groups.count() == 0


@pytest.mark.django_db
def test_registration_cannot_assign_user_permissions(
    valid_payload,
):
    payload = {
        **valid_payload,
        "user_permissions": [1, 2, 3],
    }

    serializer = InvitationRegistrationSerializer(
        data=payload,
    )

    assert serializer.is_valid(), serializer.errors

    user = cast(User, serializer.save())

    assert user.user_permissions.count() == 0


@pytest.mark.django_db
def test_registration_cannot_override_multiple_system_fields(
    invitation,
    valid_payload,
):
    payload = {
        **valid_payload,
        "email": "attacker@example.com",
        "is_active": False,
        "is_staff": True,
        "is_superuser": True,
        "groups": [1],
        "user_permissions": [1],
    }

    serializer = InvitationRegistrationSerializer(
        data=payload,
    )

    assert serializer.is_valid(), serializer.errors

    user = cast(User, serializer.save())

    assert user.email == invitation.email
    assert user.is_active is True
    assert user.is_staff is False
    assert user.is_superuser is False
    assert user.groups.count() == 0
    assert user.user_permissions.count() == 0


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
def test_password_is_required(
    valid_payload,
):
    payload = {key: value for key, value in valid_payload.items() if key != "password"}

    serializer = InvitationRegistrationSerializer(
        data=payload,
    )

    assert serializer.is_valid() is False
    assert "password" in serializer.errors


@pytest.mark.django_db
def test_token_is_required(
    valid_payload,
):
    payload = {key: value for key, value in valid_payload.items() if key != "token"}

    serializer = InvitationRegistrationSerializer(
        data=payload,
    )

    assert serializer.is_valid() is False
    assert "token" in serializer.errors


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


@pytest.mark.django_db
def test_failed_registration_does_not_create_user(
    valid_payload,
):
    payload = {
        **valid_payload,
        "token": "invalid-token",
    }

    user_count_before = User.objects.count()

    serializer = InvitationRegistrationSerializer(
        data=payload,
    )

    assert serializer.is_valid() is False
    assert User.objects.count() == user_count_before


@pytest.mark.django_db
def test_weak_password_failure_does_not_create_user(
    valid_payload,
):
    payload = {
        **valid_payload,
        "password": "password",
    }

    user_count_before = User.objects.count()

    serializer = InvitationRegistrationSerializer(
        data=payload,
    )

    assert serializer.is_valid() is False
    assert User.objects.count() == user_count_before


@pytest.mark.django_db
def test_duplicate_username_failure_does_not_create_user(
    valid_payload,
):
    User.objects.create_user(
        username="new-user",
        email="other@example.com",
        password="test-password-123",
    )

    user_count_before = User.objects.count()

    serializer = InvitationRegistrationSerializer(
        data=valid_payload,
    )

    assert serializer.is_valid() is False
    assert User.objects.count() == user_count_before

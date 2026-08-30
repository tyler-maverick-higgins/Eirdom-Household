from types import SimpleNamespace

import pytest
from django.contrib.auth import get_user_model

from apps.households.models import (
    Household,
    HouseholdInvitation,
    HouseholdMembership,
)
from apps.households.serializers import HouseholdInvitationSerializer

User = get_user_model()


@pytest.fixture
def inviter():
    return User.objects.create_user(
        username="tyler",
        email="tyler@example.com",
        password="test-password-123",
    )


@pytest.fixture
def household():
    return Household.objects.create(name="Eirdom Household")


@pytest.fixture
def serializer_context(household, inviter):
    return {
        "household": household,
        "request": SimpleNamespace(user=inviter),
    }


@pytest.mark.django_db
def test_serializer_accepts_valid_invitation(serializer_context):
    serializer = HouseholdInvitationSerializer(
        data={
            "email": "invited@example.com",
            "role": HouseholdMembership.Roles.MEMBER,
        },
        context=serializer_context,
    )

    assert serializer.is_valid(), serializer.errors

    invitation = serializer.save()

    assert invitation.household == serializer_context["household"]
    assert invitation.invited_by == serializer_context["request"].user
    assert invitation.email == "invited@example.com"
    assert invitation.role == HouseholdMembership.Roles.MEMBER
    assert invitation.status == HouseholdInvitation.Status.PENDING


@pytest.mark.django_db
def test_serializer_normalizes_email(serializer_context):
    serializer = HouseholdInvitationSerializer(
        data={
            "email": "  Invited@Example.COM  ",
            "role": HouseholdMembership.Roles.MEMBER,
        },
        context=serializer_context,
    )

    assert serializer.is_valid(), serializer.errors

    invitation = serializer.save()

    assert invitation.email == "invited@example.com"


@pytest.mark.django_db
def test_serializer_rejects_active_household_member(
    household,
    serializer_context,
):
    existing_user = User.objects.create_user(
        username="irina",
        email="irina@example.com",
        password="test-password-123",
    )

    HouseholdMembership.objects.create(
        household=household,
        user=existing_user,
        role=HouseholdMembership.Roles.MEMBER,
        is_active=True,
    )

    serializer = HouseholdInvitationSerializer(
        data={
            "email": "IRINA@example.com",
            "role": HouseholdMembership.Roles.MEMBER,
        },
        context=serializer_context,
    )

    assert not serializer.is_valid()
    assert serializer.errors["email"][0] == ("This person is already an active household member.")


@pytest.mark.django_db
def test_serializer_allows_inactive_household_member(
    household,
    serializer_context,
):
    existing_user = User.objects.create_user(
        username="former-member",
        email="former@example.com",
        password="test-password-123",
    )

    HouseholdMembership.objects.create(
        household=household,
        user=existing_user,
        role=HouseholdMembership.Roles.MEMBER,
        is_active=False,
    )

    serializer = HouseholdInvitationSerializer(
        data={
            "email": "former@example.com",
            "role": HouseholdMembership.Roles.MEMBER,
        },
        context=serializer_context,
    )

    assert serializer.is_valid(), serializer.errors


@pytest.mark.django_db
def test_serializer_rejects_duplicate_pending_invitation(
    household,
    inviter,
    serializer_context,
):
    HouseholdInvitation.objects.create(
        household=household,
        email="invited@example.com",
        role=HouseholdMembership.Roles.MEMBER,
        invited_by=inviter,
    )

    serializer = HouseholdInvitationSerializer(
        data={
            "email": "INVITED@example.com",
            "role": HouseholdMembership.Roles.MEMBER,
        },
        context=serializer_context,
    )

    assert not serializer.is_valid()
    assert serializer.errors["email"][0] == (
        "A pending invitation already exists for this email address."
    )


@pytest.mark.django_db
@pytest.mark.parametrize(
    "historical_status",
    [
        HouseholdInvitation.Status.ACCEPTED,
        HouseholdInvitation.Status.DECLINED,
        HouseholdInvitation.Status.CANCELED,
    ],
)
def test_serializer_allows_reinvite_after_historical_invitation(
    household,
    inviter,
    serializer_context,
    historical_status,
):
    HouseholdInvitation.objects.create(
        household=household,
        email="invited@example.com",
        role=HouseholdMembership.Roles.MEMBER,
        invited_by=inviter,
        status=historical_status,
    )

    serializer = HouseholdInvitationSerializer(
        data={
            "email": "invited@example.com",
            "role": HouseholdMembership.Roles.MEMBER,
        },
        context=serializer_context,
    )

    assert serializer.is_valid(), serializer.errors


@pytest.mark.django_db
@pytest.mark.parametrize(
    "disallowed_role",
    [
        HouseholdMembership.Roles.OWNER,
        HouseholdMembership.Roles.GUEST,
    ],
)
def test_serializer_rejects_disallowed_invitation_roles(
    serializer_context,
    disallowed_role,
):
    serializer = HouseholdInvitationSerializer(
        data={
            "email": "invited@example.com",
            "role": disallowed_role,
        },
        context=serializer_context,
    )

    assert not serializer.is_valid()
    assert serializer.errors["role"][0] == (
        "Invitations may only assign the Administrator or Member role."
    )


@pytest.mark.django_db
def test_serializer_accepts_administrator_role(serializer_context):
    serializer = HouseholdInvitationSerializer(
        data={
            "email": "admin@example.com",
            "role": HouseholdMembership.Roles.ADMINISTRATOR,
        },
        context=serializer_context,
    )

    assert serializer.is_valid(), serializer.errors

    invitation = serializer.save()

    assert invitation.role == HouseholdMembership.Roles.ADMINISTRATOR


@pytest.mark.django_db
def test_serializer_ignores_read_only_fields(
    household,
    inviter,
    serializer_context,
):
    other_user = User.objects.create_user(
        username="other",
        email="other@example.com",
        password="test-password-123",
    )

    serializer = HouseholdInvitationSerializer(
        data={
            "email": "invited@example.com",
            "role": HouseholdMembership.Roles.MEMBER,
            "status": HouseholdInvitation.Status.ACCEPTED,
            "invited_by": other_user.pk,
        },
        context=serializer_context,
    )

    assert serializer.is_valid(), serializer.errors

    invitation = serializer.save()

    assert invitation.household == household
    assert invitation.invited_by == inviter
    assert invitation.status == HouseholdInvitation.Status.PENDING

import pytest
from django.contrib.auth import get_user_model
from django.db import IntegrityError, transaction

from apps.households.models import (
    Household,
    HouseholdInvitation,
    HouseholdMembership,
)

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


@pytest.mark.django_db
def test_invitation_defaults_to_pending(household, inviter):
    invitation = HouseholdInvitation.objects.create(
        household=household,
        email="invited@example.com",
        invited_by=inviter,
    )

    assert invitation.status == HouseholdInvitation.Status.PENDING


@pytest.mark.django_db
def test_invitation_defaults_to_member_role(household, inviter):
    invitation = HouseholdInvitation.objects.create(
        household=household,
        email="invited@example.com",
        invited_by=inviter,
    )

    assert invitation.role == HouseholdMembership.Roles.MEMBER


@pytest.mark.django_db
def test_invitation_string_representation(household, inviter):
    invitation = HouseholdInvitation.objects.create(
        household=household,
        email="invited@example.com",
        role=HouseholdMembership.Roles.ADMINISTRATOR,
        invited_by=inviter,
    )

    assert str(invitation) == ("invited@example.com - Eirdom Household (Administrator) - pending")


@pytest.mark.django_db
@pytest.mark.parametrize(
    "historical_status",
    [
        HouseholdInvitation.Status.ACCEPTED,
        HouseholdInvitation.Status.DECLINED,
        HouseholdInvitation.Status.CANCELED,
    ],
)
def test_allows_new_pending_invitation_after_historical_invitation(
    household,
    inviter,
    historical_status,
):
    HouseholdInvitation.objects.create(
        household=household,
        email="invited@example.com",
        invited_by=inviter,
        status=historical_status,
    )

    new_invitation = HouseholdInvitation.objects.create(
        household=household,
        email="invited@example.com",
        invited_by=inviter,
    )

    assert new_invitation.status == HouseholdInvitation.Status.PENDING


@pytest.mark.django_db
def test_blocks_duplicate_pending_invitation_for_same_household_and_email(
    household,
    inviter,
):
    HouseholdInvitation.objects.create(
        household=household,
        email="invited@example.com",
        invited_by=inviter,
    )

    with pytest.raises(IntegrityError):
        with transaction.atomic():
            HouseholdInvitation.objects.create(
                household=household,
                email="invited@example.com",
                invited_by=inviter,
            )


@pytest.mark.django_db
def test_allows_same_email_to_be_pending_in_different_households(inviter):
    first_household = Household.objects.create(name="Eirdom Household")
    second_household = Household.objects.create(name="Cabin Household")

    first_invitation = HouseholdInvitation.objects.create(
        household=first_household,
        email="invited@example.com",
        invited_by=inviter,
    )

    second_invitation = HouseholdInvitation.objects.create(
        household=second_household,
        email="invited@example.com",
        invited_by=inviter,
    )

    assert first_invitation.email == second_invitation.email
    assert first_invitation.household != second_invitation.household


@pytest.mark.django_db
def test_invitation_can_assign_administrator_role(household, inviter):
    invitation = HouseholdInvitation.objects.create(
        household=household,
        email="admin@example.com",
        role=HouseholdMembership.Roles.ADMINISTRATOR,
        invited_by=inviter,
    )

    assert invitation.role == HouseholdMembership.Roles.ADMINISTRATOR

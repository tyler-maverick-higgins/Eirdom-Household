import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from apps.accounts.models import User
from apps.households.models import (
    Household,
    HouseholdInvitation,
    HouseholdMembership,
)


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def user(db):
    return User.objects.create_user(
        username="tyler",
        password="test-password-123",
        email="tyler@example.com",
        first_name="Tyler",
        last_name="Higgins",
    )


@pytest.fixture
def household(db):
    return Household.objects.create(
        name="Higgins Household",
    )


@pytest.mark.django_db
def test_household_detail_requires_authentication(
    api_client,
    household,
):
    response = api_client.get(
        reverse(
            "households:household-detail",
            kwargs={"pk": household.id},
        )
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_active_member_can_view_household_detail(
    api_client,
    user,
    household,
):
    HouseholdMembership.objects.create(
        household=household,
        user=user,
        role=HouseholdMembership.Roles.ADMINISTRATOR,
    )

    api_client.force_authenticate(user=user)

    response = api_client.get(
        reverse(
            "households:household-detail",
            kwargs={"pk": household.id},
        )
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.data["id"] == household.id
    assert response.data["name"] == "Higgins Household"


@pytest.mark.django_db
def test_nonmember_cannot_view_household_detail(
    api_client,
    user,
    household,
):
    api_client.force_authenticate(user=user)

    response = api_client.get(
        reverse(
            "households:household-detail",
            kwargs={"pk": household.id},
        )
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
def test_inactive_member_cannot_view_household_detail(
    api_client,
    user,
    household,
):
    HouseholdMembership.objects.create(
        household=household,
        user=user,
        role=HouseholdMembership.Roles.MEMBER,
        is_active=False,
    )

    api_client.force_authenticate(user=user)

    response = api_client.get(
        reverse(
            "households:household-detail",
            kwargs={"pk": household.id},
        )
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
def test_household_detail_returns_active_members_and_pending_invitations(
    api_client,
    user,
    household,
):
    HouseholdMembership.objects.create(
        household=household,
        user=user,
        role=HouseholdMembership.Roles.ADMINISTRATOR,
    )

    second_user = User.objects.create_user(
        username="irina",
        password="test-password-123",
        email="irina@example.com",
        first_name="Irina",
        last_name="Higgins",
    )

    HouseholdMembership.objects.create(
        household=household,
        user=second_user,
        role=HouseholdMembership.Roles.MEMBER,
    )

    inactive_user = User.objects.create_user(
        username="inactive",
        password="test-password-123",
    )

    HouseholdMembership.objects.create(
        household=household,
        user=inactive_user,
        role=HouseholdMembership.Roles.MEMBER,
        is_active=False,
    )

    HouseholdInvitation.objects.create(
        household=household,
        email="invited@example.com",
        role=HouseholdMembership.Roles.MEMBER,
        invited_by=user,
    )

    HouseholdInvitation.objects.create(
        household=household,
        email="old@example.com",
        role=HouseholdMembership.Roles.MEMBER,
        invited_by=user,
        status=HouseholdInvitation.Status.ACCEPTED,
    )

    api_client.force_authenticate(user=user)

    response = api_client.get(
        reverse(
            "households:household-detail",
            kwargs={"pk": household.id},
        )
    )

    assert response.status_code == status.HTTP_200_OK

    assert len(response.data["members"]) == 2
    assert {member["user"]["username"] for member in response.data["members"]} == {"tyler", "irina"}

    assert len(response.data["pending_invitations"]) == 1
    assert response.data["pending_invitations"][0]["email"] == "invited@example.com"

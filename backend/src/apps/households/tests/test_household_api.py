import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from apps.households.models import Household, HouseholdMembership

User = get_user_model()


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def user():
    return User.objects.create_user(
        username="tyler",
        email="tyler@example.com",
        password="test-password-123",
    )


@pytest.fixture
def other_user():
    return User.objects.create_user(
        username="irina",
        email="irina@example.com",
        password="test-password-123",
    )


@pytest.fixture
def household_list_url():
    return reverse("households:household-list")


def create_membership(household, user, role, *, is_active=True):
    return HouseholdMembership.objects.create(
        household=household,
        user=user,
        role=role,
        is_active=is_active,
    )


@pytest.mark.django_db
def test_unauthenticated_user_cannot_list_households(
    api_client,
    household_list_url,
):
    response = api_client.get(household_list_url)

    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_authenticated_user_with_no_memberships_gets_empty_list(
    api_client,
    user,
    household_list_url,
):
    api_client.force_authenticate(user=user)

    response = api_client.get(household_list_url)

    assert response.status_code == status.HTTP_200_OK
    assert response.data == []


@pytest.mark.django_db
def test_user_only_sees_households_with_active_membership(
    api_client,
    user,
    household_list_url,
):
    active_household = Household.objects.create(name="Eirdom Household")
    inactive_household = Household.objects.create(name="Old Household")
    unrelated_household = Household.objects.create(name="Other Household")

    create_membership(
        active_household,
        user,
        HouseholdMembership.Roles.MEMBER,
        is_active=True,
    )
    create_membership(
        inactive_household,
        user,
        HouseholdMembership.Roles.MEMBER,
        is_active=False,
    )

    api_client.force_authenticate(user=user)

    response = api_client.get(household_list_url)

    assert response.status_code == status.HTTP_200_OK

    returned_ids = {item["id"] for item in response.data}

    assert active_household.id in returned_ids
    assert inactive_household.id not in returned_ids
    assert unrelated_household.id not in returned_ids


@pytest.mark.django_db
def test_user_can_see_multiple_active_households(
    api_client,
    user,
    household_list_url,
):
    first_household = Household.objects.create(name="Eirdom Household")
    second_household = Household.objects.create(name="Cabin Household")

    create_membership(
        first_household,
        user,
        HouseholdMembership.Roles.OWNER,
    )
    create_membership(
        second_household,
        user,
        HouseholdMembership.Roles.MEMBER,
    )

    api_client.force_authenticate(user=user)

    response = api_client.get(household_list_url)

    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) == 2

    returned_ids = {item["id"] for item in response.data}

    assert returned_ids == {
        first_household.id,
        second_household.id,
    }


@pytest.mark.django_db
def test_household_list_does_not_duplicate_households(
    api_client,
    user,
    household_list_url,
):
    household = Household.objects.create(name="Eirdom Household")

    create_membership(
        household,
        user,
        HouseholdMembership.Roles.ADMINISTRATOR,
    )

    api_client.force_authenticate(user=user)

    response = api_client.get(household_list_url)

    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) == 1
    assert response.data[0]["id"] == household.id


@pytest.mark.django_db
def test_household_list_returns_expected_fields(
    api_client,
    user,
    household_list_url,
):
    household = Household.objects.create(name="Eirdom Household")

    create_membership(
        household,
        user,
        HouseholdMembership.Roles.OWNER,
    )

    api_client.force_authenticate(user=user)

    response = api_client.get(household_list_url)

    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) == 1

    household_data = response.data[0]

    assert household_data["id"] == household.id
    assert household_data["name"] == "Eirdom Household"
    assert "created_at" in household_data
    assert "updated_at" in household_data


@pytest.mark.django_db
def test_other_users_memberships_do_not_expose_household(
    api_client,
    user,
    other_user,
    household_list_url,
):
    household = Household.objects.create(name="Irina Household")

    create_membership(
        household,
        other_user,
        HouseholdMembership.Roles.OWNER,
    )

    api_client.force_authenticate(user=user)

    response = api_client.get(household_list_url)

    assert response.status_code == status.HTTP_200_OK
    assert response.data == []

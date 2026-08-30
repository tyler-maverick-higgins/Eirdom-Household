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
def household():
    return Household.objects.create(
        name="Higgins Household",
        email="household@example.com",
        household_type=Household.Types.PRIMARY,
    )


@pytest.fixture
def owner():
    return User.objects.create_user(
        username="owner",
        email="owner@example.com",
        password="test-password-123",
    )


@pytest.fixture
def administrator():
    return User.objects.create_user(
        username="administrator",
        email="administrator@example.com",
        password="test-password-123",
    )


@pytest.fixture
def member():
    return User.objects.create_user(
        username="member",
        email="member@example.com",
        password="test-password-123",
    )


@pytest.fixture
def guest():
    return User.objects.create_user(
        username="guest",
        email="guest@example.com",
        password="test-password-123",
    )


@pytest.fixture
def outsider():
    return User.objects.create_user(
        username="outsider",
        email="outsider@example.com",
        password="test-password-123",
    )


@pytest.fixture
def settings_url(household):
    return reverse(
        "households:household-settings",
        kwargs={"household_id": household.pk},
    )


def create_membership(
    household,
    user,
    role,
    *,
    is_active=True,
):
    return HouseholdMembership.objects.create(
        household=household,
        user=user,
        role=role,
        is_active=is_active,
    )


@pytest.mark.django_db
def test_household_settings_requires_authentication(
    api_client,
    settings_url,
):
    response = api_client.patch(
        settings_url,
        {
            "name": "Updated Household",
        },
        format="json",
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_owner_can_update_household_settings(
    api_client,
    household,
    owner,
    settings_url,
):
    create_membership(
        household,
        owner,
        HouseholdMembership.Roles.OWNER,
    )

    api_client.force_authenticate(user=owner)

    response = api_client.patch(
        settings_url,
        {
            "name": "Updated Household",
            "email": "updated@example.com",
            "household_type": Household.Types.VACATION,
        },
        format="json",
    )

    assert response.status_code == status.HTTP_200_OK

    household.refresh_from_db()

    assert household.name == "Updated Household"
    assert household.email == "updated@example.com"
    assert household.household_type == Household.Types.VACATION


@pytest.mark.django_db
def test_administrator_can_update_household_settings(
    api_client,
    household,
    administrator,
    settings_url,
):
    create_membership(
        household,
        administrator,
        HouseholdMembership.Roles.ADMINISTRATOR,
    )

    api_client.force_authenticate(user=administrator)

    response = api_client.patch(
        settings_url,
        {
            "name": "Admin Updated Household",
        },
        format="json",
    )

    assert response.status_code == status.HTTP_200_OK

    household.refresh_from_db()

    assert household.name == "Admin Updated Household"


@pytest.mark.django_db
def test_member_cannot_update_household_settings(
    api_client,
    household,
    member,
    settings_url,
):
    create_membership(
        household,
        member,
        HouseholdMembership.Roles.MEMBER,
    )

    api_client.force_authenticate(user=member)

    response = api_client.patch(
        settings_url,
        {
            "name": "Unauthorized Change",
        },
        format="json",
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert response.data["detail"] == (
        "Only household owners and administrators may manage household settings."
    )

    household.refresh_from_db()

    assert household.name == "Higgins Household"


@pytest.mark.django_db
def test_guest_cannot_update_household_settings(
    api_client,
    household,
    guest,
    settings_url,
):
    create_membership(
        household,
        guest,
        HouseholdMembership.Roles.GUEST,
    )

    api_client.force_authenticate(user=guest)

    response = api_client.patch(
        settings_url,
        {
            "name": "Unauthorized Change",
        },
        format="json",
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_outsider_cannot_update_household_settings(
    api_client,
    household,
    outsider,
    settings_url,
):
    api_client.force_authenticate(user=outsider)

    response = api_client.patch(
        settings_url,
        {
            "name": "Unauthorized Change",
        },
        format="json",
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_inactive_owner_cannot_update_household_settings(
    api_client,
    household,
    owner,
    settings_url,
):
    create_membership(
        household,
        owner,
        HouseholdMembership.Roles.OWNER,
        is_active=False,
    )

    api_client.force_authenticate(user=owner)

    response = api_client.patch(
        settings_url,
        {
            "name": "Unauthorized Change",
        },
        format="json",
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_household_settings_supports_partial_updates(
    api_client,
    household,
    owner,
    settings_url,
):
    create_membership(
        household,
        owner,
        HouseholdMembership.Roles.OWNER,
    )

    api_client.force_authenticate(user=owner)

    response = api_client.patch(
        settings_url,
        {
            "email": "new-email@example.com",
        },
        format="json",
    )

    assert response.status_code == status.HTTP_200_OK

    household.refresh_from_db()

    assert household.name == "Higgins Household"
    assert household.email == "new-email@example.com"
    assert household.household_type == Household.Types.PRIMARY


@pytest.mark.django_db
def test_household_settings_trims_name(
    api_client,
    household,
    owner,
    settings_url,
):
    create_membership(
        household,
        owner,
        HouseholdMembership.Roles.OWNER,
    )

    api_client.force_authenticate(user=owner)

    response = api_client.patch(
        settings_url,
        {
            "name": "  Updated Household  ",
        },
        format="json",
    )

    assert response.status_code == status.HTTP_200_OK

    household.refresh_from_db()

    assert household.name == "Updated Household"


@pytest.mark.django_db
def test_household_settings_normalizes_email(
    api_client,
    household,
    owner,
    settings_url,
):
    create_membership(
        household,
        owner,
        HouseholdMembership.Roles.OWNER,
    )

    api_client.force_authenticate(user=owner)

    response = api_client.patch(
        settings_url,
        {
            "email": "  HOUSEHOLD@Example.COM  ",
        },
        format="json",
    )

    assert response.status_code == status.HTTP_200_OK

    household.refresh_from_db()

    assert household.email == "household@example.com"


@pytest.mark.django_db
def test_household_settings_allows_empty_email(
    api_client,
    household,
    owner,
    settings_url,
):
    create_membership(
        household,
        owner,
        HouseholdMembership.Roles.OWNER,
    )

    api_client.force_authenticate(user=owner)

    response = api_client.patch(
        settings_url,
        {
            "email": "",
        },
        format="json",
    )

    assert response.status_code == status.HTTP_200_OK

    household.refresh_from_db()

    assert household.email == ""


@pytest.mark.django_db
def test_household_settings_rejects_blank_name(
    api_client,
    household,
    owner,
    settings_url,
):
    create_membership(
        household,
        owner,
        HouseholdMembership.Roles.OWNER,
    )

    api_client.force_authenticate(user=owner)

    response = api_client.patch(
        settings_url,
        {
            "name": "   ",
        },
        format="json",
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "name" in response.data


@pytest.mark.django_db
def test_household_settings_rejects_invalid_email(
    api_client,
    household,
    owner,
    settings_url,
):
    create_membership(
        household,
        owner,
        HouseholdMembership.Roles.OWNER,
    )

    api_client.force_authenticate(user=owner)

    response = api_client.patch(
        settings_url,
        {
            "email": "not-an-email",
        },
        format="json",
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "email" in response.data


@pytest.mark.django_db
def test_household_settings_rejects_invalid_household_type(
    api_client,
    household,
    owner,
    settings_url,
):
    create_membership(
        household,
        owner,
        HouseholdMembership.Roles.OWNER,
    )

    api_client.force_authenticate(user=owner)

    response = api_client.patch(
        settings_url,
        {
            "household_type": "spaceship",
        },
        format="json",
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "household_type" in response.data


@pytest.mark.django_db
def test_household_settings_cannot_change_slug(
    api_client,
    household,
    owner,
    settings_url,
):
    create_membership(
        household,
        owner,
        HouseholdMembership.Roles.OWNER,
    )

    original_slug = household.slug

    api_client.force_authenticate(user=owner)

    response = api_client.patch(
        settings_url,
        {
            "slug": "malicious-slug-change",
            "name": "Updated Household",
        },
        format="json",
    )

    assert response.status_code == status.HTTP_200_OK

    household.refresh_from_db()

    assert household.name == "Updated Household"
    assert household.slug == original_slug


@pytest.mark.django_db
def test_household_settings_response_contains_updated_household(
    api_client,
    household,
    owner,
    settings_url,
):
    create_membership(
        household,
        owner,
        HouseholdMembership.Roles.OWNER,
    )

    api_client.force_authenticate(user=owner)

    response = api_client.patch(
        settings_url,
        {
            "name": "Updated Household",
            "email": "updated@example.com",
            "household_type": Household.Types.RENTAL,
        },
        format="json",
    )

    assert response.status_code == status.HTTP_200_OK

    assert response.data["id"] == household.pk
    assert response.data["name"] == "Updated Household"
    assert response.data["email"] == "updated@example.com"
    assert response.data["household_type"] == Household.Types.RENTAL
    assert "created_at" in response.data
    assert "updated_at" in response.data


@pytest.mark.django_db
def test_nonexistent_household_settings_returns_404(
    api_client,
    owner,
):
    api_client.force_authenticate(user=owner)

    response = api_client.patch(
        reverse(
            "households:household-settings",
            kwargs={"household_id": 999999},
        ),
        {
            "name": "Does Not Matter",
        },
        format="json",
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND

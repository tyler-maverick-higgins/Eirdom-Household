import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from apps.households.models import (
    Household,
    HouseholdMembership,
)

User = get_user_model()


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def household():
    return Household.objects.create(
        name="Higgins Household",
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
def outsider():
    return User.objects.create_user(
        username="outsider",
        email="outsider@example.com",
        password="test-password-123",
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


def transfer_url(household):
    return reverse(
        "households:ownership-transfer",
        kwargs={
            "household_id": household.pk,
        },
    )


@pytest.mark.django_db
def test_ownership_transfer_requires_authentication(
    api_client,
    household,
):
    response = api_client.post(
        transfer_url(household),
        {
            "membership_id": 1,
        },
        format="json",
    )

    assert response.status_code == (status.HTTP_403_FORBIDDEN)


@pytest.mark.django_db
def test_owner_can_transfer_ownership_to_active_member(
    api_client,
    household,
    owner,
    member,
):
    owner_membership = create_membership(
        household,
        owner,
        HouseholdMembership.Roles.OWNER,
    )

    member_membership = create_membership(
        household,
        member,
        HouseholdMembership.Roles.MEMBER,
    )

    api_client.force_authenticate(user=owner)

    response = api_client.post(
        transfer_url(household),
        {
            "membership_id": member_membership.pk,
        },
        format="json",
    )

    assert response.status_code == status.HTTP_200_OK

    owner_membership.refresh_from_db()
    member_membership.refresh_from_db()

    assert owner_membership.role == (HouseholdMembership.Roles.ADMINISTRATOR)

    assert member_membership.role == (HouseholdMembership.Roles.OWNER)


@pytest.mark.django_db
def test_owner_can_transfer_ownership_to_administrator(
    api_client,
    household,
    owner,
    administrator,
):
    owner_membership = create_membership(
        household,
        owner,
        HouseholdMembership.Roles.OWNER,
    )

    admin_membership = create_membership(
        household,
        administrator,
        HouseholdMembership.Roles.ADMINISTRATOR,
    )

    api_client.force_authenticate(user=owner)

    response = api_client.post(
        transfer_url(household),
        {
            "membership_id": admin_membership.pk,
        },
        format="json",
    )

    assert response.status_code == status.HTTP_200_OK

    owner_membership.refresh_from_db()
    admin_membership.refresh_from_db()

    assert owner_membership.role == (HouseholdMembership.Roles.ADMINISTRATOR)

    assert admin_membership.role == (HouseholdMembership.Roles.OWNER)


@pytest.mark.django_db
def test_administrator_cannot_transfer_ownership(
    api_client,
    household,
    administrator,
    member,
):
    create_membership(
        household,
        administrator,
        HouseholdMembership.Roles.ADMINISTRATOR,
    )

    member_membership = create_membership(
        household,
        member,
        HouseholdMembership.Roles.MEMBER,
    )

    api_client.force_authenticate(user=administrator)

    response = api_client.post(
        transfer_url(household),
        {
            "membership_id": member_membership.pk,
        },
        format="json",
    )

    assert response.status_code == (status.HTTP_403_FORBIDDEN)


@pytest.mark.django_db
def test_member_cannot_transfer_ownership(
    api_client,
    household,
    member,
):
    member_membership = create_membership(
        household,
        member,
        HouseholdMembership.Roles.MEMBER,
    )

    api_client.force_authenticate(user=member)

    response = api_client.post(
        transfer_url(household),
        {
            "membership_id": member_membership.pk,
        },
        format="json",
    )

    assert response.status_code == (status.HTTP_403_FORBIDDEN)


@pytest.mark.django_db
def test_outsider_cannot_transfer_ownership(
    api_client,
    household,
    outsider,
    member,
):
    member_membership = create_membership(
        household,
        member,
        HouseholdMembership.Roles.MEMBER,
    )

    api_client.force_authenticate(user=outsider)

    response = api_client.post(
        transfer_url(household),
        {
            "membership_id": member_membership.pk,
        },
        format="json",
    )

    assert response.status_code == (status.HTTP_403_FORBIDDEN)


@pytest.mark.django_db
def test_owner_cannot_transfer_to_inactive_member(
    api_client,
    household,
    owner,
    member,
):
    create_membership(
        household,
        owner,
        HouseholdMembership.Roles.OWNER,
    )

    inactive_membership = create_membership(
        household,
        member,
        HouseholdMembership.Roles.MEMBER,
        is_active=False,
    )

    api_client.force_authenticate(user=owner)

    response = api_client.post(
        transfer_url(household),
        {
            "membership_id": inactive_membership.pk,
        },
        format="json",
    )

    assert response.status_code == (status.HTTP_400_BAD_REQUEST)

    assert "membership_id" in response.data


@pytest.mark.django_db
def test_owner_cannot_transfer_to_membership_from_other_household(
    api_client,
    household,
    owner,
    member,
):
    create_membership(
        household,
        owner,
        HouseholdMembership.Roles.OWNER,
    )

    other_household = Household.objects.create(
        name="Other Household",
    )

    other_membership = create_membership(
        other_household,
        member,
        HouseholdMembership.Roles.MEMBER,
    )

    api_client.force_authenticate(user=owner)

    response = api_client.post(
        transfer_url(household),
        {
            "membership_id": other_membership.pk,
        },
        format="json",
    )

    assert response.status_code == (status.HTTP_400_BAD_REQUEST)


@pytest.mark.django_db
def test_owner_cannot_transfer_ownership_to_self(
    api_client,
    household,
    owner,
):
    owner_membership = create_membership(
        household,
        owner,
        HouseholdMembership.Roles.OWNER,
    )

    api_client.force_authenticate(user=owner)

    response = api_client.post(
        transfer_url(household),
        {
            "membership_id": owner_membership.pk,
        },
        format="json",
    )

    assert response.status_code == (status.HTTP_400_BAD_REQUEST)


@pytest.mark.django_db
def test_transfer_requires_membership_id(
    api_client,
    household,
    owner,
):
    create_membership(
        household,
        owner,
        HouseholdMembership.Roles.OWNER,
    )

    api_client.force_authenticate(user=owner)

    response = api_client.post(
        transfer_url(household),
        {},
        format="json",
    )

    assert response.status_code == (status.HTTP_400_BAD_REQUEST)

    assert "membership_id" in response.data


@pytest.mark.django_db
def test_transfer_response_contains_new_owner_membership(
    api_client,
    household,
    owner,
    member,
):
    create_membership(
        household,
        owner,
        HouseholdMembership.Roles.OWNER,
    )

    member_membership = create_membership(
        household,
        member,
        HouseholdMembership.Roles.MEMBER,
    )

    api_client.force_authenticate(user=owner)

    response = api_client.post(
        transfer_url(household),
        {
            "membership_id": member_membership.pk,
        },
        format="json",
    )

    assert response.status_code == status.HTTP_200_OK

    assert response.data["id"] == (member_membership.pk)
    assert response.data["role"] == (HouseholdMembership.Roles.OWNER)
    assert response.data["is_active"] is True
    assert response.data["user"]["id"] == member.pk


@pytest.mark.django_db
def test_owner_cannot_transfer_ownership_to_staff_account(
    api_client,
    household,
    owner,
):
    owner_membership = create_membership(
        household,
        owner,
        HouseholdMembership.Roles.OWNER,
    )

    staff_user = User.objects.create_user(
        username="legacy-staff",
        email="legacy-staff@example.com",
        password="test-password-123",
        is_staff=True,
    )

    staff_membership = create_membership(
        household,
        staff_user,
        HouseholdMembership.Roles.MEMBER,
    )

    api_client.force_authenticate(user=owner)

    response = api_client.post(
        transfer_url(household),
        {
            "membership_id": staff_membership.pk,
        },
        format="json",
    )

    assert response.status_code == (status.HTTP_400_BAD_REQUEST)

    owner_membership.refresh_from_db()
    staff_membership.refresh_from_db()

    assert owner_membership.role == (HouseholdMembership.Roles.OWNER)
    assert staff_membership.role == (HouseholdMembership.Roles.MEMBER)


@pytest.mark.django_db
def test_owner_cannot_transfer_ownership_to_superuser_account(
    api_client,
    household,
    owner,
):
    owner_membership = create_membership(
        household,
        owner,
        HouseholdMembership.Roles.OWNER,
    )

    superuser = User.objects.create_superuser(
        username="legacy-superuser",
        email="legacy-superuser@example.com",
        password="test-password-123",
    )

    superuser_membership = create_membership(
        household,
        superuser,
        HouseholdMembership.Roles.MEMBER,
    )

    api_client.force_authenticate(user=owner)

    response = api_client.post(
        transfer_url(household),
        {
            "membership_id": superuser_membership.pk,
        },
        format="json",
    )

    assert response.status_code == (status.HTTP_400_BAD_REQUEST)

    owner_membership.refresh_from_db()
    superuser_membership.refresh_from_db()

    assert owner_membership.role == (HouseholdMembership.Roles.OWNER)
    assert superuser_membership.role == (HouseholdMembership.Roles.MEMBER)

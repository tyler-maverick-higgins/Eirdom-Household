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
def second_administrator():
    return User.objects.create_user(
        username="second-administrator",
        email="second-admin@example.com",
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


def administration_url(household):
    return reverse(
        "households:member-administration",
        kwargs={
            "household_id": household.pk,
        },
    )


def membership_update_url(
    household,
    membership,
):
    return reverse(
        "households:membership-update",
        kwargs={
            "household_id": household.pk,
            "membership_id": membership.pk,
        },
    )


@pytest.mark.django_db
def test_member_administration_requires_authentication(
    api_client,
    household,
):
    response = api_client.get(administration_url(household))

    assert response.status_code == (status.HTTP_403_FORBIDDEN)


@pytest.mark.django_db
def test_owner_can_list_household_memberships(
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

    create_membership(
        household,
        member,
        HouseholdMembership.Roles.MEMBER,
    )

    api_client.force_authenticate(user=owner)

    response = api_client.get(administration_url(household))

    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) == 2


@pytest.mark.django_db
def test_member_administration_includes_inactive_members(
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

    response = api_client.get(administration_url(household))

    assert response.status_code == status.HTTP_200_OK

    returned_membership = next(
        item for item in response.data if item["id"] == inactive_membership.pk
    )

    assert returned_membership["is_active"] is False


@pytest.mark.django_db
def test_administrator_can_list_household_memberships(
    api_client,
    household,
    administrator,
):
    create_membership(
        household,
        administrator,
        HouseholdMembership.Roles.ADMINISTRATOR,
    )

    api_client.force_authenticate(user=administrator)

    response = api_client.get(administration_url(household))

    assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
def test_member_cannot_list_member_administration(
    api_client,
    household,
    member,
):
    create_membership(
        household,
        member,
        HouseholdMembership.Roles.MEMBER,
    )

    api_client.force_authenticate(user=member)

    response = api_client.get(administration_url(household))

    assert response.status_code == (status.HTTP_403_FORBIDDEN)


@pytest.mark.django_db
def test_owner_can_change_member_role(
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

    response = api_client.patch(
        membership_update_url(
            household,
            member_membership,
        ),
        {
            "role": (HouseholdMembership.Roles.ADMINISTRATOR),
        },
        format="json",
    )

    assert response.status_code == status.HTTP_200_OK

    member_membership.refresh_from_db()

    assert member_membership.role == (HouseholdMembership.Roles.ADMINISTRATOR)


@pytest.mark.django_db
def test_owner_can_deactivate_member(
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

    response = api_client.patch(
        membership_update_url(
            household,
            member_membership,
        ),
        {
            "is_active": False,
        },
        format="json",
    )

    assert response.status_code == status.HTTP_200_OK

    member_membership.refresh_from_db()

    assert member_membership.is_active is False


@pytest.mark.django_db
def test_owner_can_reactivate_member(
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
        is_active=False,
    )

    api_client.force_authenticate(user=owner)

    response = api_client.patch(
        membership_update_url(
            household,
            member_membership,
        ),
        {
            "is_active": True,
        },
        format="json",
    )

    assert response.status_code == status.HTTP_200_OK

    member_membership.refresh_from_db()

    assert member_membership.is_active is True


@pytest.mark.django_db
def test_owner_can_manage_administrator(
    api_client,
    household,
    owner,
    administrator,
):
    create_membership(
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

    response = api_client.patch(
        membership_update_url(
            household,
            admin_membership,
        ),
        {
            "role": HouseholdMembership.Roles.MEMBER,
        },
        format="json",
    )

    assert response.status_code == status.HTTP_200_OK

    admin_membership.refresh_from_db()

    assert admin_membership.role == (HouseholdMembership.Roles.MEMBER)


@pytest.mark.django_db
def test_administrator_can_change_member_to_guest(
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

    response = api_client.patch(
        membership_update_url(
            household,
            member_membership,
        ),
        {
            "role": HouseholdMembership.Roles.GUEST,
        },
        format="json",
    )

    assert response.status_code == status.HTTP_200_OK

    member_membership.refresh_from_db()

    assert member_membership.role == (HouseholdMembership.Roles.GUEST)


@pytest.mark.django_db
def test_administrator_can_deactivate_member(
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

    response = api_client.patch(
        membership_update_url(
            household,
            member_membership,
        ),
        {
            "is_active": False,
        },
        format="json",
    )

    assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
def test_administrator_cannot_manage_other_administrator(
    api_client,
    household,
    administrator,
    second_administrator,
):
    create_membership(
        household,
        administrator,
        HouseholdMembership.Roles.ADMINISTRATOR,
    )

    target_membership = create_membership(
        household,
        second_administrator,
        HouseholdMembership.Roles.ADMINISTRATOR,
    )

    api_client.force_authenticate(user=administrator)

    response = api_client.patch(
        membership_update_url(
            household,
            target_membership,
        ),
        {
            "is_active": False,
        },
        format="json",
    )

    assert response.status_code == (status.HTTP_403_FORBIDDEN)


@pytest.mark.django_db
def test_administrator_cannot_promote_member_to_administrator(
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

    response = api_client.patch(
        membership_update_url(
            household,
            member_membership,
        ),
        {
            "role": (HouseholdMembership.Roles.ADMINISTRATOR),
        },
        format="json",
    )

    assert response.status_code == (status.HTTP_403_FORBIDDEN)


@pytest.mark.django_db
def test_owner_role_cannot_be_assigned_through_member_admin(
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

    response = api_client.patch(
        membership_update_url(
            household,
            member_membership,
        ),
        {
            "role": HouseholdMembership.Roles.OWNER,
        },
        format="json",
    )

    assert response.status_code == (status.HTTP_400_BAD_REQUEST)

    assert "role" in response.data


@pytest.mark.django_db
def test_owner_membership_cannot_be_modified_through_member_admin(
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

    create_membership(
        household,
        administrator,
        HouseholdMembership.Roles.ADMINISTRATOR,
    )

    api_client.force_authenticate(user=administrator)

    response = api_client.patch(
        membership_update_url(
            household,
            owner_membership,
        ),
        {
            "is_active": False,
        },
        format="json",
    )

    assert response.status_code == (status.HTTP_400_BAD_REQUEST)


@pytest.mark.django_db
def test_user_cannot_manage_own_membership(
    api_client,
    household,
    administrator,
):
    admin_membership = create_membership(
        household,
        administrator,
        HouseholdMembership.Roles.ADMINISTRATOR,
    )

    api_client.force_authenticate(user=administrator)

    response = api_client.patch(
        membership_update_url(
            household,
            admin_membership,
        ),
        {
            "role": HouseholdMembership.Roles.MEMBER,
        },
        format="json",
    )

    assert response.status_code == (status.HTTP_400_BAD_REQUEST)


@pytest.mark.django_db
def test_member_cannot_update_another_membership(
    api_client,
    household,
    member,
    guest,
):
    create_membership(
        household,
        member,
        HouseholdMembership.Roles.MEMBER,
    )

    guest_membership = create_membership(
        household,
        guest,
        HouseholdMembership.Roles.GUEST,
    )

    api_client.force_authenticate(user=member)

    response = api_client.patch(
        membership_update_url(
            household,
            guest_membership,
        ),
        {
            "is_active": False,
        },
        format="json",
    )

    assert response.status_code == (status.HTTP_403_FORBIDDEN)


@pytest.mark.django_db
def test_membership_from_another_household_cannot_be_modified(
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

    response = api_client.patch(
        membership_update_url(
            household,
            other_membership,
        ),
        {
            "is_active": False,
        },
        format="json",
    )

    assert response.status_code == (status.HTTP_404_NOT_FOUND)


@pytest.mark.django_db
def test_empty_membership_update_is_rejected(
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

    response = api_client.patch(
        membership_update_url(
            household,
            member_membership,
        ),
        {},
        format="json",
    )

    assert response.status_code == (status.HTTP_400_BAD_REQUEST)


@pytest.mark.django_db
def test_member_administration_excludes_staff_membership(
    api_client,
    household,
    owner,
):
    create_membership(
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
        HouseholdMembership.Roles.ADMINISTRATOR,
    )

    api_client.force_authenticate(user=owner)

    response = api_client.get(
        administration_url(household),
    )

    assert response.status_code == status.HTTP_200_OK

    returned_ids = {membership["id"] for membership in response.data}

    assert staff_membership.pk not in returned_ids


@pytest.mark.django_db
def test_member_administration_excludes_superuser_membership(
    api_client,
    household,
    owner,
):
    create_membership(
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
        HouseholdMembership.Roles.ADMINISTRATOR,
    )

    api_client.force_authenticate(user=owner)

    response = api_client.get(
        administration_url(household),
    )

    assert response.status_code == status.HTTP_200_OK

    returned_ids = {membership["id"] for membership in response.data}

    assert superuser_membership.pk not in returned_ids


@pytest.mark.django_db
def test_staff_membership_cannot_be_modified_through_member_admin(
    api_client,
    household,
    owner,
):
    create_membership(
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

    response = api_client.patch(
        membership_update_url(
            household,
            staff_membership,
        ),
        {
            "role": HouseholdMembership.Roles.ADMINISTRATOR,
        },
        format="json",
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND

    staff_membership.refresh_from_db()

    assert staff_membership.role == HouseholdMembership.Roles.MEMBER


@pytest.mark.django_db
def test_superuser_membership_cannot_be_modified_through_member_admin(
    api_client,
    household,
    owner,
):
    create_membership(
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

    response = api_client.patch(
        membership_update_url(
            household,
            superuser_membership,
        ),
        {
            "role": HouseholdMembership.Roles.ADMINISTRATOR,
        },
        format="json",
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND

    superuser_membership.refresh_from_db()

    assert superuser_membership.role == HouseholdMembership.Roles.MEMBER

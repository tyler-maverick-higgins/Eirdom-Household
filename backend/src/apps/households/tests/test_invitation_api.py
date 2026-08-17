import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from apps.households.models import (
    Household,
    HouseholdInvitation,
    HouseholdMembership,
)

User = get_user_model()


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def household():
    return Household.objects.create(name="Eirdom Household")


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
def invitation_url(household):
    return reverse(
        "households:invitation-create",
        kwargs={"household_id": household.pk},
    )


@pytest.fixture
def valid_payload():
    return {
        "email": "invited@example.com",
        "role": HouseholdMembership.Roles.MEMBER,
    }


def create_membership(household, user, role, *, is_active=True):
    return HouseholdMembership.objects.create(
        household=household,
        user=user,
        role=role,
        is_active=is_active,
    )


@pytest.mark.django_db
def test_unauthenticated_user_cannot_create_invitation(
    api_client,
    invitation_url,
    valid_payload,
):
    response = api_client.post(invitation_url, valid_payload, format="json")

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert HouseholdInvitation.objects.count() == 0


@pytest.mark.django_db
def test_outsider_cannot_create_invitation(
    api_client,
    invitation_url,
    outsider,
    valid_payload,
):
    api_client.force_authenticate(user=outsider)

    response = api_client.post(invitation_url, valid_payload, format="json")

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert response.data["detail"] == ("You are not an active member of this household.")
    assert HouseholdInvitation.objects.count() == 0


@pytest.mark.django_db
def test_member_cannot_create_invitation(
    api_client,
    household,
    invitation_url,
    member,
    valid_payload,
):
    create_membership(
        household,
        member,
        HouseholdMembership.Roles.MEMBER,
    )
    api_client.force_authenticate(user=member)

    response = api_client.post(invitation_url, valid_payload, format="json")

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert response.data["detail"] == (
        "Only household owners and administrators may send invitations."
    )
    assert HouseholdInvitation.objects.count() == 0


@pytest.mark.django_db
def test_guest_cannot_create_invitation(
    api_client,
    household,
    invitation_url,
    guest,
    valid_payload,
):
    create_membership(
        household,
        guest,
        HouseholdMembership.Roles.GUEST,
    )
    api_client.force_authenticate(user=guest)

    response = api_client.post(invitation_url, valid_payload, format="json")

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert response.data["detail"] == (
        "Only household owners and administrators may send invitations."
    )
    assert HouseholdInvitation.objects.count() == 0


@pytest.mark.django_db
@pytest.mark.parametrize(
    "role",
    [
        HouseholdMembership.Roles.OWNER,
        HouseholdMembership.Roles.ADMINISTRATOR,
    ],
)
def test_inactive_privileged_member_cannot_create_invitation(
    api_client,
    household,
    invitation_url,
    valid_payload,
    role,
):
    user = User.objects.create_user(
        username=f"inactive-{role}",
        email=f"inactive-{role}@example.com",
        password="test-password-123",
    )
    create_membership(
        household,
        user,
        role,
        is_active=False,
    )
    api_client.force_authenticate(user=user)

    response = api_client.post(invitation_url, valid_payload, format="json")

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert response.data["detail"] == ("You are not an active member of this household.")
    assert HouseholdInvitation.objects.count() == 0


@pytest.mark.django_db
def test_administrator_can_create_invitation(
    api_client,
    household,
    invitation_url,
    administrator,
    valid_payload,
):
    create_membership(
        household,
        administrator,
        HouseholdMembership.Roles.ADMINISTRATOR,
    )
    api_client.force_authenticate(user=administrator)

    response = api_client.post(invitation_url, valid_payload, format="json")

    assert response.status_code == status.HTTP_201_CREATED

    invitation = HouseholdInvitation.objects.get()

    assert invitation.household == household
    assert invitation.invited_by == administrator
    assert invitation.email == "invited@example.com"
    assert invitation.role == HouseholdMembership.Roles.MEMBER
    assert invitation.status == HouseholdInvitation.Status.PENDING


@pytest.mark.django_db
def test_owner_can_create_invitation(
    api_client,
    household,
    invitation_url,
    owner,
    valid_payload,
):
    create_membership(
        household,
        owner,
        HouseholdMembership.Roles.OWNER,
    )
    api_client.force_authenticate(user=owner)

    response = api_client.post(invitation_url, valid_payload, format="json")

    assert response.status_code == status.HTTP_201_CREATED
    assert HouseholdInvitation.objects.count() == 1

    invitation = HouseholdInvitation.objects.get()

    assert invitation.household == household
    assert invitation.invited_by == owner


@pytest.mark.django_db
def test_created_invitation_response_contains_read_only_fields(
    api_client,
    household,
    invitation_url,
    administrator,
    valid_payload,
):
    create_membership(
        household,
        administrator,
        HouseholdMembership.Roles.ADMINISTRATOR,
    )
    api_client.force_authenticate(user=administrator)

    response = api_client.post(invitation_url, valid_payload, format="json")

    assert response.status_code == status.HTTP_201_CREATED
    assert response.data["email"] == "invited@example.com"
    assert response.data["role"] == HouseholdMembership.Roles.MEMBER
    assert response.data["status"] == HouseholdInvitation.Status.PENDING
    assert response.data["invited_by"] == administrator.pk
    assert "id" in response.data
    assert "created_at" in response.data
    assert "updated_at" in response.data


@pytest.mark.django_db
def test_api_normalizes_invitation_email(
    api_client,
    household,
    invitation_url,
    administrator,
):
    create_membership(
        household,
        administrator,
        HouseholdMembership.Roles.ADMINISTRATOR,
    )
    api_client.force_authenticate(user=administrator)

    response = api_client.post(
        invitation_url,
        {
            "email": "  INVITED@Example.COM  ",
            "role": HouseholdMembership.Roles.MEMBER,
        },
        format="json",
    )

    assert response.status_code == status.HTTP_201_CREATED
    assert response.data["email"] == "invited@example.com"

    invitation = HouseholdInvitation.objects.get()
    assert invitation.email == "invited@example.com"


@pytest.mark.django_db
def test_api_rejects_duplicate_pending_invitation(
    api_client,
    household,
    invitation_url,
    administrator,
    valid_payload,
):
    create_membership(
        household,
        administrator,
        HouseholdMembership.Roles.ADMINISTRATOR,
    )
    HouseholdInvitation.objects.create(
        household=household,
        email="invited@example.com",
        role=HouseholdMembership.Roles.MEMBER,
        invited_by=administrator,
    )
    api_client.force_authenticate(user=administrator)

    response = api_client.post(invitation_url, valid_payload, format="json")

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.data["email"][0] == (
        "A pending invitation already exists for this email address."
    )
    assert HouseholdInvitation.objects.count() == 1


@pytest.mark.django_db
def test_api_rejects_active_household_member(
    api_client,
    household,
    invitation_url,
    administrator,
):
    create_membership(
        household,
        administrator,
        HouseholdMembership.Roles.ADMINISTRATOR,
    )

    existing_user = User.objects.create_user(
        username="existing-member",
        email="existing@example.com",
        password="test-password-123",
    )
    create_membership(
        household,
        existing_user,
        HouseholdMembership.Roles.MEMBER,
    )

    api_client.force_authenticate(user=administrator)

    response = api_client.post(
        invitation_url,
        {
            "email": "existing@example.com",
            "role": HouseholdMembership.Roles.MEMBER,
        },
        format="json",
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.data["email"][0] == ("This person is already an active household member.")
    assert HouseholdInvitation.objects.count() == 0


@pytest.mark.django_db
@pytest.mark.parametrize(
    "role",
    [
        HouseholdMembership.Roles.OWNER,
        HouseholdMembership.Roles.GUEST,
    ],
)
def test_api_rejects_disallowed_invitation_role(
    api_client,
    household,
    invitation_url,
    administrator,
    role,
):
    create_membership(
        household,
        administrator,
        HouseholdMembership.Roles.ADMINISTRATOR,
    )
    api_client.force_authenticate(user=administrator)

    response = api_client.post(
        invitation_url,
        {
            "email": "invited@example.com",
            "role": role,
        },
        format="json",
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.data["role"][0] == (
        "Invitations may only assign the Administrator or Member role."
    )
    assert HouseholdInvitation.objects.count() == 0


@pytest.mark.django_db
def test_nonexistent_household_returns_404(
    api_client,
    administrator,
    valid_payload,
):
    api_client.force_authenticate(user=administrator)

    url = reverse(
        "households:invitation-create",
        kwargs={"household_id": 999999},
    )

    response = api_client.post(url, valid_payload, format="json")

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert HouseholdInvitation.objects.count() == 0

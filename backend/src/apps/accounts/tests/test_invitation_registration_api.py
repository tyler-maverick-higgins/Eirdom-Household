from datetime import timedelta

import pytest
from django.urls import reverse
from django.utils import timezone
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

    invitation = HouseholdInvitation.objects.create(
        household=household,
        email="invitee@example.com",
        role=HouseholdMembership.Roles.MEMBER,
        invited_by=inviter,
    )

    token = invitation.generate_token()

    invitation.save(
        update_fields=[
            "token_hash",
            "expires_at",
            "updated_at",
        ]
    )

    return invitation, token


@pytest.fixture
def register_url():
    return reverse("accounts:register")


@pytest.fixture
def valid_payload(invitation):
    _, token = invitation

    return {
        "token": token,
        "username": "new-user",
        "first_name": "New",
        "last_name": "User",
        "password": "VeryStrongPassword123!",
    }


@pytest.mark.django_db
def test_valid_invitation_registration_creates_account(
    api_client,
    invitation,
    register_url,
    valid_payload,
):
    invitation_record, _ = invitation

    response = api_client.post(
        register_url,
        valid_payload,
        format="json",
    )

    assert response.status_code == status.HTTP_201_CREATED

    user = User.objects.get(
        username="new-user",
    )

    assert user.email == invitation_record.email
    assert user.first_name == "New"
    assert user.last_name == "User"
    assert user.check_password("VeryStrongPassword123!")

    assert response.data == {
        "id": user.pk,
        "username": user.username,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "email": user.email,
    }


@pytest.mark.django_db
def test_registration_response_exposes_only_expected_user_fields(
    api_client,
    register_url,
    valid_payload,
):
    response = api_client.post(
        register_url,
        valid_payload,
        format="json",
    )

    assert response.status_code == status.HTTP_201_CREATED

    assert set(response.data.keys()) == {
        "id",
        "username",
        "first_name",
        "last_name",
        "email",
    }


@pytest.mark.django_db
def test_registration_response_does_not_expose_sensitive_fields(
    api_client,
    register_url,
    valid_payload,
):
    response = api_client.post(
        register_url,
        valid_payload,
        format="json",
    )

    assert response.status_code == status.HTTP_201_CREATED

    prohibited_fields = {
        "password",
        "is_active",
        "is_staff",
        "is_superuser",
        "groups",
        "user_permissions",
        "last_login",
        "date_joined",
    }

    assert prohibited_fields.isdisjoint(response.data.keys())


@pytest.mark.django_db
def test_successful_registration_creates_normal_steward_account(
    api_client,
    register_url,
    valid_payload,
):
    response = api_client.post(
        register_url,
        valid_payload,
        format="json",
    )

    assert response.status_code == status.HTTP_201_CREATED

    user = User.objects.get(
        username="new-user",
    )

    assert user.is_active is True
    assert user.is_staff is False
    assert user.is_superuser is False
    assert user.groups.count() == 0
    assert user.user_permissions.count() == 0


@pytest.mark.django_db
def test_successful_registration_hashes_password(
    api_client,
    register_url,
    valid_payload,
):
    raw_password = valid_payload["password"]

    response = api_client.post(
        register_url,
        valid_payload,
        format="json",
    )

    assert response.status_code == status.HTTP_201_CREATED

    user = User.objects.get(
        username="new-user",
    )

    assert user.password != raw_password
    assert user.check_password(raw_password) is True


@pytest.mark.django_db
def test_successful_registration_creates_authenticated_session(
    api_client,
    register_url,
    valid_payload,
):
    response = api_client.post(
        register_url,
        valid_payload,
        format="json",
    )

    assert response.status_code == status.HTTP_201_CREATED

    user = User.objects.get(
        username="new-user",
    )

    session = api_client.session

    assert "_auth_user_id" in session
    assert int(session["_auth_user_id"]) == user.pk


@pytest.mark.django_db
def test_registration_email_is_locked_to_invitation(
    api_client,
    invitation,
    register_url,
    valid_payload,
):
    invitation_record, _ = invitation

    payload = {
        **valid_payload,
        "email": "attacker@example.com",
    }

    response = api_client.post(
        register_url,
        payload,
        format="json",
    )

    assert response.status_code == status.HTTP_201_CREATED

    user = User.objects.get(
        username="new-user",
    )

    assert user.email == invitation_record.email
    assert user.email != "attacker@example.com"


@pytest.mark.django_db
def test_registration_cannot_create_staff_account(
    api_client,
    register_url,
    valid_payload,
):
    payload = {
        **valid_payload,
        "is_staff": True,
    }

    response = api_client.post(
        register_url,
        payload,
        format="json",
    )

    assert response.status_code == status.HTTP_201_CREATED

    user = User.objects.get(
        username="new-user",
    )

    assert user.is_staff is False
    assert user.is_superuser is False


@pytest.mark.django_db
def test_registration_cannot_create_superuser_account(
    api_client,
    register_url,
    valid_payload,
):
    payload = {
        **valid_payload,
        "is_superuser": True,
    }

    response = api_client.post(
        register_url,
        payload,
        format="json",
    )

    assert response.status_code == status.HTTP_201_CREATED

    user = User.objects.get(
        username="new-user",
    )

    assert user.is_staff is False
    assert user.is_superuser is False


@pytest.mark.django_db
def test_registration_cannot_override_active_flag(
    api_client,
    register_url,
    valid_payload,
):
    payload = {
        **valid_payload,
        "is_active": False,
    }

    response = api_client.post(
        register_url,
        payload,
        format="json",
    )

    assert response.status_code == status.HTTP_201_CREATED

    user = User.objects.get(
        username="new-user",
    )

    assert user.is_active is True


@pytest.mark.django_db
def test_registration_cannot_assign_groups(
    api_client,
    register_url,
    valid_payload,
):
    payload = {
        **valid_payload,
        "groups": [1, 2, 3],
    }

    response = api_client.post(
        register_url,
        payload,
        format="json",
    )

    assert response.status_code == status.HTTP_201_CREATED

    user = User.objects.get(
        username="new-user",
    )

    assert user.groups.count() == 0


@pytest.mark.django_db
def test_registration_cannot_assign_user_permissions(
    api_client,
    register_url,
    valid_payload,
):
    payload = {
        **valid_payload,
        "user_permissions": [1, 2, 3],
    }

    response = api_client.post(
        register_url,
        payload,
        format="json",
    )

    assert response.status_code == status.HTTP_201_CREATED

    user = User.objects.get(
        username="new-user",
    )

    assert user.user_permissions.count() == 0


@pytest.mark.django_db
def test_registration_cannot_override_system_account_fields(
    api_client,
    invitation,
    register_url,
    valid_payload,
):
    invitation_record, _ = invitation

    payload = {
        **valid_payload,
        "email": "attacker@example.com",
        "is_active": False,
        "is_staff": True,
        "is_superuser": True,
        "groups": [1],
        "user_permissions": [1],
    }

    response = api_client.post(
        register_url,
        payload,
        format="json",
    )

    assert response.status_code == status.HTTP_201_CREATED

    user = User.objects.get(
        username="new-user",
    )

    assert user.email == invitation_record.email
    assert user.is_active is True
    assert user.is_staff is False
    assert user.is_superuser is False
    assert user.groups.count() == 0
    assert user.user_permissions.count() == 0


@pytest.mark.django_db
def test_invalid_invitation_token_is_rejected(
    api_client,
    register_url,
    valid_payload,
):
    payload = {
        **valid_payload,
        "token": "not-a-real-token",
    }

    response = api_client.post(
        register_url,
        payload,
        format="json",
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "token" in response.data

    assert (
        User.objects.filter(
            username="new-user",
        ).exists()
        is False
    )


@pytest.mark.django_db
def test_invalid_invitation_does_not_create_authenticated_session(
    api_client,
    register_url,
    valid_payload,
):
    payload = {
        **valid_payload,
        "token": "not-a-real-token",
    }

    response = api_client.post(
        register_url,
        payload,
        format="json",
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST

    session = api_client.session

    assert "_auth_user_id" not in session


@pytest.mark.django_db
def test_expired_invitation_is_rejected(
    api_client,
    invitation,
    register_url,
    valid_payload,
):
    invitation_record, _ = invitation

    invitation_record.expires_at = timezone.now() - timedelta(minutes=1)

    invitation_record.save(
        update_fields=[
            "expires_at",
            "updated_at",
        ]
    )

    response = api_client.post(
        register_url,
        valid_payload,
        format="json",
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "token" in response.data

    assert (
        User.objects.filter(
            username="new-user",
        ).exists()
        is False
    )


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
    api_client,
    invitation,
    register_url,
    valid_payload,
    invitation_status,
):
    invitation_record, _ = invitation

    invitation_record.status = invitation_status

    invitation_record.save(
        update_fields=[
            "status",
            "updated_at",
        ]
    )

    response = api_client.post(
        register_url,
        valid_payload,
        format="json",
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "token" in response.data

    assert (
        User.objects.filter(
            username="new-user",
        ).exists()
        is False
    )


@pytest.mark.django_db
def test_existing_account_for_invited_email_is_rejected(
    api_client,
    invitation,
    register_url,
    valid_payload,
):
    invitation_record, _ = invitation

    User.objects.create_user(
        username="existing-user",
        email=invitation_record.email,
        first_name="Existing",
        last_name="User",
        password="test-password-123",
    )

    response = api_client.post(
        register_url,
        valid_payload,
        format="json",
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "token" in response.data

    assert (
        User.objects.filter(
            username="new-user",
        ).exists()
        is False
    )


@pytest.mark.django_db
def test_existing_account_email_lookup_is_case_insensitive(
    api_client,
    invitation,
    register_url,
    valid_payload,
):
    invitation_record, _ = invitation

    User.objects.create_user(
        username="existing-user",
        email=invitation_record.email.upper(),
        first_name="Existing",
        last_name="User",
        password="test-password-123",
    )

    response = api_client.post(
        register_url,
        valid_payload,
        format="json",
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "token" in response.data

    assert (
        User.objects.filter(
            username="new-user",
        ).exists()
        is False
    )


@pytest.mark.django_db
def test_first_name_is_required(
    api_client,
    register_url,
    valid_payload,
):
    payload = {
        **valid_payload,
        "first_name": "",
    }

    response = api_client.post(
        register_url,
        payload,
        format="json",
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "first_name" in response.data

    assert (
        User.objects.filter(
            username="new-user",
        ).exists()
        is False
    )


@pytest.mark.django_db
def test_last_name_is_required(
    api_client,
    register_url,
    valid_payload,
):
    payload = {
        **valid_payload,
        "last_name": "",
    }

    response = api_client.post(
        register_url,
        payload,
        format="json",
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "last_name" in response.data

    assert (
        User.objects.filter(
            username="new-user",
        ).exists()
        is False
    )


@pytest.mark.django_db
def test_username_is_required(
    api_client,
    register_url,
    valid_payload,
):
    payload = {
        **valid_payload,
        "username": "",
    }

    response = api_client.post(
        register_url,
        payload,
        format="json",
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "username" in response.data

    assert (
        User.objects.filter(
            username="new-user",
        ).exists()
        is False
    )


@pytest.mark.django_db
def test_password_is_required(
    api_client,
    register_url,
    valid_payload,
):
    payload = {key: value for key, value in valid_payload.items() if key != "password"}

    response = api_client.post(
        register_url,
        payload,
        format="json",
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "password" in response.data

    assert (
        User.objects.filter(
            username="new-user",
        ).exists()
        is False
    )


@pytest.mark.django_db
def test_token_is_required(
    api_client,
    register_url,
    valid_payload,
):
    payload = {key: value for key, value in valid_payload.items() if key != "token"}

    response = api_client.post(
        register_url,
        payload,
        format="json",
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "token" in response.data

    assert (
        User.objects.filter(
            username="new-user",
        ).exists()
        is False
    )


@pytest.mark.django_db
def test_duplicate_username_is_rejected(
    api_client,
    register_url,
    valid_payload,
):
    User.objects.create_user(
        username="new-user",
        email="other@example.com",
        first_name="Other",
        last_name="User",
        password="test-password-123",
    )

    response = api_client.post(
        register_url,
        valid_payload,
        format="json",
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "username" in response.data


@pytest.mark.django_db
def test_duplicate_username_lookup_is_case_insensitive(
    api_client,
    register_url,
    valid_payload,
):
    User.objects.create_user(
        username="NEW-USER",
        email="other@example.com",
        first_name="Other",
        last_name="User",
        password="test-password-123",
    )

    response = api_client.post(
        register_url,
        valid_payload,
        format="json",
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "username" in response.data

    assert (
        User.objects.filter(
            username="new-user",
        ).exists()
        is False
    )


@pytest.mark.django_db
def test_weak_password_is_rejected(
    api_client,
    register_url,
    valid_payload,
):
    payload = {
        **valid_payload,
        "password": "password",
    }

    response = api_client.post(
        register_url,
        payload,
        format="json",
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "password" in response.data

    assert (
        User.objects.filter(
            username="new-user",
        ).exists()
        is False
    )


@pytest.mark.django_db
def test_authenticated_user_cannot_register_again(
    api_client,
    inviter,
    register_url,
    valid_payload,
):
    api_client.force_authenticate(
        user=inviter,
    )

    response = api_client.post(
        register_url,
        valid_payload,
        format="json",
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST

    assert response.data["detail"] == ("You are already signed in.")

    assert (
        User.objects.filter(
            username="new-user",
        ).exists()
        is False
    )


@pytest.mark.django_db
def test_authenticated_staff_user_cannot_register_account(
    api_client,
    register_url,
    valid_payload,
):
    staff_user = User.objects.create_user(
        username="staff",
        email="staff@example.com",
        password="test-password-123",
        is_staff=True,
    )

    api_client.force_authenticate(
        user=staff_user,
    )

    response = api_client.post(
        register_url,
        valid_payload,
        format="json",
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST

    assert response.data["detail"] == ("You are already signed in.")

    assert (
        User.objects.filter(
            username="new-user",
        ).exists()
        is False
    )


@pytest.mark.django_db
def test_authenticated_superuser_cannot_register_account(
    api_client,
    register_url,
    valid_payload,
):
    superuser = User.objects.create_superuser(
        username="system-admin",
        email="admin@example.com",
        password="test-password-123",
    )

    api_client.force_authenticate(
        user=superuser,
    )

    response = api_client.post(
        register_url,
        valid_payload,
        format="json",
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST

    assert response.data["detail"] == ("You are already signed in.")

    assert (
        User.objects.filter(
            username="new-user",
        ).exists()
        is False
    )


@pytest.mark.django_db
def test_registration_does_not_accept_household_membership_yet(
    api_client,
    household,
    register_url,
    valid_payload,
):
    response = api_client.post(
        register_url,
        valid_payload,
        format="json",
    )

    assert response.status_code == status.HTTP_201_CREATED

    user = User.objects.get(
        username="new-user",
    )

    assert (
        HouseholdMembership.objects.filter(
            household=household,
            user=user,
        ).exists()
        is False
    )

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

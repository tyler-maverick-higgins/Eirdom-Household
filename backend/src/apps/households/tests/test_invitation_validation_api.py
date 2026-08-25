from datetime import timedelta

import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone
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

    return HouseholdInvitation.objects.create(
        household=household,
        email="invitee@example.com",
        role=HouseholdMembership.Roles.MEMBER,
        invited_by=inviter,
    )


def create_invitation_token(invitation):
    token = invitation.generate_token()

    invitation.save(
        update_fields=[
            "token_hash",
            "expires_at",
            "updated_at",
        ]
    )

    return token


def invitation_validation_url(token):
    return reverse(
        "households:invitation-validate",
        kwargs={"token": token},
    )


@pytest.mark.django_db
def test_valid_pending_invitation_returns_expected_data(
    api_client,
    invitation,
):
    token = create_invitation_token(invitation)

    response = api_client.get(
        invitation_validation_url(token),
    )

    assert response.status_code == status.HTTP_200_OK

    assert response.data["household_name"] == "Higgins Household"
    assert response.data["email"] == "invitee@example.com"
    assert response.data["role"] == HouseholdMembership.Roles.MEMBER
    assert response.data["inviter_name"] == "Household Owner"
    assert response.data["expires_at"] is not None
    assert response.data["account_exists"] is False


@pytest.mark.django_db
def test_invitation_validation_does_not_require_authentication(
    api_client,
    invitation,
):
    token = create_invitation_token(invitation)

    response = api_client.get(
        invitation_validation_url(token),
    )

    assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
def test_invalid_invitation_token_returns_404(
    api_client,
):
    response = api_client.get(
        invitation_validation_url("this-is-not-a-valid-invitation-token"),
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
def test_expired_invitation_returns_410(
    api_client,
    invitation,
):
    token = create_invitation_token(invitation)

    invitation.expires_at = timezone.now() - timedelta(minutes=1)
    invitation.save(
        update_fields=[
            "expires_at",
            "updated_at",
        ]
    )

    response = api_client.get(
        invitation_validation_url(token),
    )

    assert response.status_code == status.HTTP_410_GONE
    assert response.data["detail"] == "This invitation has expired."


@pytest.mark.django_db
def test_accepted_invitation_returns_404(
    api_client,
    invitation,
):
    token = create_invitation_token(invitation)

    invitation.status = HouseholdInvitation.Status.ACCEPTED
    invitation.accepted_at = timezone.now()
    invitation.save(
        update_fields=[
            "status",
            "accepted_at",
            "updated_at",
        ]
    )

    response = api_client.get(
        invitation_validation_url(token),
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
def test_canceled_invitation_returns_404(
    api_client,
    invitation,
):
    token = create_invitation_token(invitation)

    invitation.status = HouseholdInvitation.Status.CANCELED
    invitation.save(
        update_fields=[
            "status",
            "updated_at",
        ]
    )

    response = api_client.get(
        invitation_validation_url(token),
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
def test_declined_invitation_returns_404(
    api_client,
    invitation,
):
    token = create_invitation_token(invitation)

    invitation.status = HouseholdInvitation.Status.DECLINED
    invitation.save(
        update_fields=[
            "status",
            "updated_at",
        ]
    )

    response = api_client.get(
        invitation_validation_url(token),
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
def test_existing_account_is_reported(
    api_client,
    invitation,
):
    User.objects.create_user(
        username="existing-user",
        email="invitee@example.com",
        password="test-password-123",
    )

    token = create_invitation_token(invitation)

    response = api_client.get(
        invitation_validation_url(token),
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.data["account_exists"] is True


@pytest.mark.django_db
def test_existing_account_lookup_is_case_insensitive(
    api_client,
    invitation,
):
    User.objects.create_user(
        username="existing-user",
        email="INVITEE@EXAMPLE.COM",
        password="test-password-123",
    )

    token = create_invitation_token(invitation)

    response = api_client.get(
        invitation_validation_url(token),
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.data["account_exists"] is True


@pytest.mark.django_db
def test_validation_response_does_not_expose_sensitive_fields(
    api_client,
    invitation,
):
    token = create_invitation_token(invitation)

    response = api_client.get(
        invitation_validation_url(token),
    )

    assert response.status_code == status.HTTP_200_OK

    assert "token_hash" not in response.data
    assert "id" not in response.data
    assert "invited_by" not in response.data
    assert "status" not in response.data
    assert "accepted_at" not in response.data
    assert "last_sent_at" not in response.data
    assert "created_at" not in response.data
    assert "updated_at" not in response.data

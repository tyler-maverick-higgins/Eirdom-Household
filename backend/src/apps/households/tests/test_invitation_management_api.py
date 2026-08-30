from unittest.mock import patch

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


@pytest.fixture
def household(owner, administrator, member):
    household = Household.objects.create(
        name="Higgins Household",
    )

    HouseholdMembership.objects.create(
        household=household,
        user=owner,
        role=HouseholdMembership.Roles.OWNER,
    )

    HouseholdMembership.objects.create(
        household=household,
        user=administrator,
        role=HouseholdMembership.Roles.ADMINISTRATOR,
    )

    HouseholdMembership.objects.create(
        household=household,
        user=member,
        role=HouseholdMembership.Roles.MEMBER,
    )

    return household


@pytest.fixture
def invitation(household, owner):
    invitation = HouseholdInvitation.objects.create(
        household=household,
        email="invitee@example.com",
        role=HouseholdMembership.Roles.MEMBER,
        invited_by=owner,
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


def resend_url(invitation_id):
    return reverse(
        "households:invitation-resend",
        kwargs={"invitation_id": invitation_id},
    )


def cancel_url(invitation_id):
    return reverse(
        "households:invitation-cancel",
        kwargs={"invitation_id": invitation_id},
    )


@pytest.mark.django_db
def test_resend_requires_authentication(
    api_client,
    invitation,
):
    invitation_record, _ = invitation

    response = api_client.post(
        resend_url(invitation_record.pk),
        format="json",
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_owner_can_resend_pending_invitation(
    api_client,
    invitation,
    owner,
    django_capture_on_commit_callbacks,
):
    invitation_record, _ = invitation

    api_client.force_authenticate(user=owner)

    with patch("apps.households.views.send_household_invitation_task.delay") as delay:
        with django_capture_on_commit_callbacks(execute=True):
            response = api_client.post(
                resend_url(invitation_record.pk),
                format="json",
            )

    assert response.status_code == status.HTTP_200_OK

    delay.assert_called_once_with(invitation_record.pk)


@pytest.mark.django_db
def test_administrator_can_resend_pending_invitation(
    api_client,
    invitation,
    administrator,
    django_capture_on_commit_callbacks,
):
    invitation_record, _ = invitation

    api_client.force_authenticate(user=administrator)

    with patch("apps.households.views.send_household_invitation_task.delay") as delay:
        with django_capture_on_commit_callbacks(execute=True):
            response = api_client.post(
                resend_url(invitation_record.pk),
                format="json",
            )

    assert response.status_code == status.HTTP_200_OK
    delay.assert_called_once_with(invitation_record.pk)


@pytest.mark.django_db
def test_member_cannot_resend_invitation(
    api_client,
    invitation,
    member,
):
    invitation_record, _ = invitation

    api_client.force_authenticate(user=member)

    with patch("apps.households.views.send_household_invitation_task.delay") as delay:
        response = api_client.post(
            resend_url(invitation_record.pk),
            format="json",
        )

    assert response.status_code == status.HTTP_403_FORBIDDEN
    delay.assert_not_called()


@pytest.mark.django_db
def test_outsider_cannot_resend_invitation(
    api_client,
    invitation,
    outsider,
):
    invitation_record, _ = invitation

    api_client.force_authenticate(user=outsider)

    with patch("apps.households.views.send_household_invitation_task.delay") as delay:
        response = api_client.post(
            resend_url(invitation_record.pk),
            format="json",
        )

    assert response.status_code == status.HTTP_403_FORBIDDEN
    delay.assert_not_called()


@pytest.mark.django_db
@pytest.mark.parametrize(
    "invitation_status",
    [
        HouseholdInvitation.Status.ACCEPTED,
        HouseholdInvitation.Status.DECLINED,
        HouseholdInvitation.Status.CANCELED,
    ],
)
def test_non_pending_invitation_cannot_be_resent(
    api_client,
    invitation,
    owner,
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

    api_client.force_authenticate(user=owner)

    with patch("apps.households.views.send_household_invitation_task.delay") as delay:
        response = api_client.post(
            resend_url(invitation_record.pk),
            format="json",
        )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    delay.assert_not_called()


@pytest.mark.django_db
def test_resend_returns_pending_invitation(
    api_client,
    invitation,
    owner,
    django_capture_on_commit_callbacks,
):
    invitation_record, _ = invitation

    api_client.force_authenticate(user=owner)

    with patch("apps.households.views.send_household_invitation_task.delay"):
        with django_capture_on_commit_callbacks(execute=True):
            response = api_client.post(
                resend_url(invitation_record.pk),
                format="json",
            )

    assert response.status_code == status.HTTP_200_OK
    assert response.data["id"] == invitation_record.pk
    assert response.data["email"] == invitation_record.email
    assert response.data["status"] == HouseholdInvitation.Status.PENDING


@pytest.mark.django_db
def test_cancel_requires_authentication(
    api_client,
    invitation,
):
    invitation_record, _ = invitation

    response = api_client.post(
        cancel_url(invitation_record.pk),
        format="json",
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_owner_can_cancel_pending_invitation(
    api_client,
    invitation,
    owner,
):
    invitation_record, _ = invitation

    api_client.force_authenticate(user=owner)

    response = api_client.post(
        cancel_url(invitation_record.pk),
        format="json",
    )

    assert response.status_code == status.HTTP_200_OK

    invitation_record.refresh_from_db()

    assert invitation_record.status == HouseholdInvitation.Status.CANCELED
    assert invitation_record.token_hash == ""
    assert invitation_record.expires_at is None


@pytest.mark.django_db
def test_administrator_can_cancel_pending_invitation(
    api_client,
    invitation,
    administrator,
):
    invitation_record, _ = invitation

    api_client.force_authenticate(user=administrator)

    response = api_client.post(
        cancel_url(invitation_record.pk),
        format="json",
    )

    assert response.status_code == status.HTTP_200_OK

    invitation_record.refresh_from_db()

    assert invitation_record.status == HouseholdInvitation.Status.CANCELED


@pytest.mark.django_db
def test_member_cannot_cancel_invitation(
    api_client,
    invitation,
    member,
):
    invitation_record, _ = invitation

    api_client.force_authenticate(user=member)

    response = api_client.post(
        cancel_url(invitation_record.pk),
        format="json",
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN

    invitation_record.refresh_from_db()

    assert invitation_record.status == HouseholdInvitation.Status.PENDING


@pytest.mark.django_db
def test_outsider_cannot_cancel_invitation(
    api_client,
    invitation,
    outsider,
):
    invitation_record, _ = invitation

    api_client.force_authenticate(user=outsider)

    response = api_client.post(
        cancel_url(invitation_record.pk),
        format="json",
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN

    invitation_record.refresh_from_db()

    assert invitation_record.status == HouseholdInvitation.Status.PENDING


@pytest.mark.django_db
@pytest.mark.parametrize(
    "invitation_status",
    [
        HouseholdInvitation.Status.ACCEPTED,
        HouseholdInvitation.Status.DECLINED,
        HouseholdInvitation.Status.CANCELED,
    ],
)
def test_non_pending_invitation_cannot_be_canceled(
    api_client,
    invitation,
    owner,
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

    api_client.force_authenticate(user=owner)

    response = api_client.post(
        cancel_url(invitation_record.pk),
        format="json",
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
def test_cancelled_invitation_allows_same_email_to_be_invited_again(
    api_client,
    household,
    invitation,
    owner,
):
    invitation_record, _ = invitation

    api_client.force_authenticate(user=owner)

    response = api_client.post(
        cancel_url(invitation_record.pk),
        format="json",
    )

    assert response.status_code == status.HTTP_200_OK

    replacement = HouseholdInvitation.objects.create(
        household=household,
        email=invitation_record.email,
        role=HouseholdMembership.Roles.MEMBER,
        invited_by=owner,
    )

    assert replacement.pk != invitation_record.pk
    assert replacement.status == HouseholdInvitation.Status.PENDING


@pytest.mark.django_db
def test_cancelled_invitation_old_token_no_longer_validates(
    api_client,
    invitation,
    owner,
):
    invitation_record, token = invitation

    api_client.force_authenticate(user=owner)

    cancel_response = api_client.post(
        cancel_url(invitation_record.pk),
        format="json",
    )

    assert cancel_response.status_code == status.HTTP_200_OK

    api_client.force_authenticate(user=None)

    validation_response = api_client.get(
        reverse(
            "households:invitation-validate",
            kwargs={"token": token},
        ),
    )

    assert validation_response.status_code == status.HTTP_404_NOT_FOUND

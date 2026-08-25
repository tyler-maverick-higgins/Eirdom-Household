from unittest.mock import patch

import pytest

from apps.accounts.models import User
from apps.households.models import (
    Household,
    HouseholdInvitation,
    HouseholdMembership,
)
from apps.households.tasks import _send_household_invitation


@pytest.fixture
def invitation(db):
    inviter = User.objects.create_user(
        username="tyler",
        email="tyler@example.com",
        first_name="Tyler",
        last_name="Higgins",
    )

    household = Household.objects.create(
        name="Higgins Household",
    )

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


@pytest.mark.django_db
@patch(
    "apps.households.tasks.send_household_invitation",
)
def test_send_household_invitation_task(
    mock_send,
    invitation,
):
    mock_send.return_value = "email_123"

    email_id = _send_household_invitation(
        invitation.id,
    )

    assert email_id == "email_123"

    mock_send.assert_called_once()

    sent_invitation, token = mock_send.call_args.args

    assert sent_invitation.id == invitation.id
    assert sent_invitation.email == "invitee@example.com"

    assert token
    assert sent_invitation.token_hash
    assert sent_invitation.token_hash != token
    assert sent_invitation.token_matches(token) is True
    assert sent_invitation.expires_at is not None
    assert sent_invitation.last_sent_at is not None

    invitation.refresh_from_db()

    assert invitation.token_hash == sent_invitation.token_hash
    assert invitation.expires_at == sent_invitation.expires_at
    assert invitation.last_sent_at == sent_invitation.last_sent_at

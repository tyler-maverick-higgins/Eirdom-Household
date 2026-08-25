from unittest.mock import patch

import pytest

from apps.accounts.models import User
from apps.households.models import (
    Household,
    HouseholdInvitation,
    HouseholdMembership,
)
from apps.households.services.invitations import (
    send_household_invitation,
)


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
    "apps.households.services.invitations.resend.Emails.send",
)
def test_send_household_invitation(
    mock_send,
    invitation,
    settings,
):
    settings.RESEND_API_KEY = "re_test"
    settings.RESEND_FROM_EMAIL = "Steward <invitations@example.com>"
    settings.STEWARD_FRONTEND_URL = "http://localhost:5173"

    mock_send.return_value = {
        "id": "email_123",
    }

    email_id = send_household_invitation(
        invitation,
        "test-token-123",
    )

    assert email_id == "email_123"

    mock_send.assert_called_once()

    payload = mock_send.call_args.args[0]

    assert payload["to"] == ["invitee@example.com"]
    assert payload["from"] == ("Steward <invitations@example.com>")
    assert payload["subject"] == "You've been invited to join Higgins Household in Steward"

    assert "Tyler Higgins" in payload["html"]
    assert "Higgins Household" in payload["html"]
    assert "Member" in payload["html"]

    assert "http://localhost:5173/invitations/accept/test-token-123" in payload["html"]

    assert "Accept invitation" in payload["html"]
    assert "expires in 7 days" in payload["html"]

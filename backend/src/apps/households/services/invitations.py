import resend
from django.conf import settings

from apps.households.models import HouseholdInvitation


def send_household_invitation(
    invitation: HouseholdInvitation,
    token: str,
) -> str:
    if not settings.RESEND_API_KEY:
        raise RuntimeError("RESEND_API_KEY is required to send household invitations.")

    resend.api_key = settings.RESEND_API_KEY

    inviter_name = invitation.invited_by.get_full_name() or invitation.invited_by.username

    role_name = invitation.role.title()

    accept_url = f"{settings.STEWARD_FRONTEND_URL}/invitations/accept/{token}"

    response = resend.Emails.send(
        {
            "from": settings.RESEND_FROM_EMAIL,
            "to": [invitation.email],
            "subject": (f"You've been invited to join {invitation.household.name} in Steward"),
            "html": f"""
                <h1>You're invited to Steward</h1>

                <p>
                    {inviter_name} invited you to join
                    <strong>{invitation.household.name}</strong>
                    as a {role_name}.
                </p>

                <p>
                    <a href="{accept_url}">
                        Accept invitation
                    </a>
                </p>

                <p>
                    This invitation expires in 7 days.
                </p>
            """,
        }
    )

    return response["id"]

from celery import shared_task
from django.utils import timezone

from apps.households.models import HouseholdInvitation
from apps.households.services.invitations import send_household_invitation


def _send_household_invitation(invitation_id: int) -> str:
    invitation = HouseholdInvitation.objects.select_related(
        "household",
        "invited_by",
    ).get(pk=invitation_id)

    token = invitation.generate_token()

    invitation.last_sent_at = timezone.now()

    invitation.save(
        update_fields=[
            "token_hash",
            "expires_at",
            "last_sent_at",
            "updated_at",
        ]
    )
    return send_household_invitation(
        invitation,
        token,
    )


@shared_task(
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_backoff_max=60,
    retry_jitter=True,
    retry_kwargs={"max_retries": 5},
)
def send_household_invitation_task(invitation_id: int) -> str:
    return _send_household_invitation(invitation_id)

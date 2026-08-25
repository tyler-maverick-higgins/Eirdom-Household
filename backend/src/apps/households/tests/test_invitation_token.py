import pytest
from django.utils import timezone

from apps.accounts.models import User
from apps.households.models import (
    Household,
    HouseholdInvitation,
    HouseholdMembership,
)


@pytest.fixture
def invitation(db):
    inviter = User.objects.create_user(
        username="owner",
        email="owner@example.com",
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
def test_generate_token_returns_raw_token_and_stores_hash(
    invitation,
):
    token = invitation.generate_token()

    assert token
    assert invitation.token_hash
    assert invitation.token_hash != token
    assert len(invitation.token_hash) == 64


@pytest.mark.django_db
def test_generated_token_matches_invitation(
    invitation,
):
    token = invitation.generate_token()

    assert invitation.token_matches(token) is True


@pytest.mark.django_db
def test_incorrect_token_does_not_match(
    invitation,
):
    invitation.generate_token()

    assert invitation.token_matches("wrong-token") is False


@pytest.mark.django_db
def test_generated_token_has_expiration(
    invitation,
):
    invitation.generate_token()

    assert invitation.expires_at is not None
    assert invitation.expires_at > timezone.now()


@pytest.mark.django_db
def test_invitation_is_not_expired_after_token_generation(
    invitation,
):
    invitation.generate_token()

    assert invitation.is_expired is False


@pytest.mark.django_db
def test_invitation_without_expiration_is_expired(
    invitation,
):
    assert invitation.is_expired is True

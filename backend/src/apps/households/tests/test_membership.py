import pytest
from django.contrib.auth import get_user_model
from django.db import IntegrityError, transaction

from apps.households.models import Household, HouseholdMembership

pytestmark = pytest.mark.django_db

User = get_user_model()


def create_user(username: str, email: str = ""):
    return User.objects.create_user(
        username=username,
        email=email,
        password="test-password",
    )


def create_household(
    name: str = "Eirdom Household",
    slug: str = "eirdom-household",
) -> Household:
    return Household.objects.create(
        name=name,
        slug=slug,
    )


def test_membership_can_be_created() -> None:
    user = create_user("tyler")
    household = create_household()

    membership = HouseholdMembership.objects.create(
        household=household,
        user=user,
        role=HouseholdMembership.Roles.OWNER,
    )

    assert membership.pk is not None
    assert membership.household == household
    assert membership.user == user
    assert membership.role == HouseholdMembership.Roles.OWNER


def test_membership_defaults_to_member_role() -> None:
    user = create_user("tyler")
    household = create_household()

    membership = HouseholdMembership.objects.create(
        household=household,
        user=user,
    )

    assert membership.role == HouseholdMembership.Roles.MEMBER


def test_membership_defaults_to_active() -> None:
    user = create_user("tyler")
    household = create_household()

    membership = HouseholdMembership.objects.create(
        household=household,
        user=user,
    )

    assert membership.is_active is True


@pytest.mark.parametrize(
    "role",
    [
        HouseholdMembership.Roles.OWNER,
        HouseholdMembership.Roles.ADMINISTRATOR,
        HouseholdMembership.Roles.MEMBER,
        HouseholdMembership.Roles.GUEST,
    ],
)
def test_each_membership_role_can_be_assigned(role: str) -> None:
    user = create_user(f"user-{role}")
    household = create_household(
        name=f"{role.title()} Household",
        slug=f"{role}-household",
    )

    membership = HouseholdMembership.objects.create(
        household=household,
        user=user,
        role=role,
    )

    assert membership.role == role


def test_household_reverse_relationship_returns_memberships() -> None:
    user = create_user("tyler")
    household = create_household()

    membership = HouseholdMembership.objects.create(
        household=household,
        user=user,
    )

    assert list(household.memberships.all()) == [membership]


def test_user_reverse_relationship_returns_household_memberships() -> None:
    user = create_user("tyler")
    household = create_household()

    membership = HouseholdMembership.objects.create(
        household=household,
        user=user,
    )

    assert list(user.household_memberships.all()) == [membership]


def test_one_user_can_belong_to_multiple_households() -> None:
    user = create_user("tyler")
    first_household = create_household(
        name="Eirdom Household",
        slug="eirdom-household",
    )
    second_household = create_household(
        name="Extended Family Household",
        slug="extended-family-household",
    )

    first_membership = HouseholdMembership.objects.create(
        household=first_household,
        user=user,
        role=HouseholdMembership.Roles.OWNER,
    )
    second_membership = HouseholdMembership.objects.create(
        household=second_household,
        user=user,
        role=HouseholdMembership.Roles.MEMBER,
    )

    assert list(user.household_memberships.all()) == [
        first_membership,
        second_membership,
    ]


def test_one_household_can_have_multiple_users() -> None:
    household = create_household()
    tyler = create_user("tyler")
    irina = create_user("irina")

    tyler_membership = HouseholdMembership.objects.create(
        household=household,
        user=tyler,
        role=HouseholdMembership.Roles.OWNER,
    )
    irina_membership = HouseholdMembership.objects.create(
        household=household,
        user=irina,
        role=HouseholdMembership.Roles.OWNER,
    )

    assert list(household.memberships.all()) == [
        tyler_membership,
        irina_membership,
    ]


def test_duplicate_household_membership_is_rejected() -> None:
    user = create_user("tyler")
    household = create_household()

    HouseholdMembership.objects.create(
        household=household,
        user=user,
    )

    with pytest.raises(IntegrityError):
        with transaction.atomic():
            HouseholdMembership.objects.create(
                household=household,
                user=user,
            )


def test_membership_string_representation_uses_role_label() -> None:
    user = create_user("tyler")
    household = create_household()

    membership = HouseholdMembership.objects.create(
        household=household,
        user=user,
        role=HouseholdMembership.Roles.ADMINISTRATOR,
    )

    assert str(membership) == ("tyler — Eirdom Household (Administrator)")


def test_inactive_membership_string_representation_includes_status() -> None:
    user = create_user("tyler")
    household = create_household()

    membership = HouseholdMembership.objects.create(
        household=household,
        user=user,
        role=HouseholdMembership.Roles.MEMBER,
        is_active=False,
    )

    assert str(membership) == ("tyler — Eirdom Household (Member) — Inactive")


def test_deleting_household_deletes_its_memberships() -> None:
    user = create_user("tyler")
    household = create_household()

    membership = HouseholdMembership.objects.create(
        household=household,
        user=user,
    )
    membership_id = membership.pk

    household.delete()

    assert not HouseholdMembership.objects.filter(pk=membership_id).exists()


def test_deleting_user_deletes_their_memberships() -> None:
    user = create_user("tyler")
    household = create_household()

    membership = HouseholdMembership.objects.create(
        household=household,
        user=user,
    )
    membership_id = membership.pk

    user.delete()

    assert not HouseholdMembership.objects.filter(pk=membership_id).exists()


def test_memberships_are_ordered_by_household_then_creation_time() -> None:
    user = create_user("tyler")
    alpha_household = create_household(
        name="Alpha Household",
        slug="alpha-household",
    )
    zulu_household = create_household(
        name="Zulu Household",
        slug="zulu-household",
    )

    zulu_membership = HouseholdMembership.objects.create(
        household=zulu_household,
        user=user,
    )
    alpha_membership = HouseholdMembership.objects.create(
        household=alpha_household,
        user=user,
    )

    assert list(HouseholdMembership.objects.all()) == [
        alpha_membership,
        zulu_membership,
    ]


def test_membership_model_uses_expected_default_ordering() -> None:
    assert HouseholdMembership._meta.ordering == [
        "household",
        "created_at",
    ]

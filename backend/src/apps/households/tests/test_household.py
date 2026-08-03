import pytest
from django.db import IntegrityError, transaction
from django.utils import timezone

from apps.households.models import Household

pytestmark = pytest.mark.django_db


def test_household_can_be_created() -> None:
    household = Household.objects.create(
        name="Eirdom Household",
        slug="eirdom-household",
    )

    assert household.pk is not None
    assert household.name == "Eirdom Household"
    assert household.slug == "eirdom-household"


def test_household_string_representation_returns_name() -> None:
    household = Household.objects.create(
        name="Eirdom Household",
        slug="eirdom-household",
    )

    assert str(household) == "Eirdom Household"


def test_household_timestamps_are_populated() -> None:
    before_creation = timezone.now()

    household = Household.objects.create(
        name="Eirdom Household",
        slug="eirdom-household",
    )

    after_creation = timezone.now()

    assert before_creation <= household.created_at <= after_creation
    assert before_creation <= household.updated_at <= after_creation


def test_household_updated_at_changes_when_saved() -> None:
    household = Household.objects.create(
        name="Eirdom Household",
        slug="eirdom-household",
    )
    original_updated_at = household.updated_at

    household.name = "Updated Eirdom Household"
    household.save()
    household.refresh_from_db()

    assert household.updated_at > original_updated_at


def test_household_slug_must_be_unique() -> None:
    Household.objects.create(
        name="First Household",
        slug="shared-household",
    )

    with pytest.raises(IntegrityError):
        with transaction.atomic():
            Household.objects.create(
                name="Second Household",
                slug="shared-household",
            )


def test_household_names_do_not_need_to_be_unique() -> None:
    first_household = Household.objects.create(
        name="Family Household",
        slug="first-family-household",
    )
    second_household = Household.objects.create(
        name="Family Household",
        slug="second-family-household",
    )

    assert first_household.name == second_household.name
    assert Household.objects.filter(name="Family Household").count() == 2


def test_households_are_ordered_by_name() -> None:
    Household.objects.create(name="Zulu Household", slug="zulu-household")
    Household.objects.create(name="Alpha Household", slug="alpha-household")
    Household.objects.create(name="Middle Household", slug="middle-household")

    household_names = list(Household.objects.values_list("name", flat=True))

    assert household_names == [
        "Alpha Household",
        "Middle Household",
        "Zulu Household",
    ]


def test_household_model_uses_expected_default_ordering() -> None:
    assert Household._meta.ordering == ["name", "created_at"]


def test_household_field_lengths_match_domain_design() -> None:
    name_field = Household._meta.get_field("name")
    slug_field = Household._meta.get_field("slug")

    assert name_field.max_length == 255
    assert slug_field.max_length == 150

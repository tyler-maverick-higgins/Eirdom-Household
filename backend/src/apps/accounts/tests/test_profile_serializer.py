import pytest

from apps.accounts.models import User
from apps.accounts.serializers import ProfileSerializer


@pytest.mark.django_db
def test_profile_serializer_exposes_only_expected_fields():
    user = User.objects.create_user(
        username="tyler",
        email="tyler@example.com",
        first_name="Tyler",
        last_name="Higgins",
        password="test-password-123",
    )

    serializer = ProfileSerializer(user)

    data = dict(serializer.data)

    assert set(data) == {
        "id",
        "username",
        "first_name",
        "last_name",
        "email",
    }


@pytest.mark.django_db
def test_profile_serializer_updates_profile():
    user = User.objects.create_user(
        username="tyler",
        email="tyler@example.com",
        first_name="Tyler",
        last_name="Higgins",
        password="test-password-123",
    )

    serializer = ProfileSerializer(
        user,
        data={
            "username": "tylerh",
            "email": "tylerh@example.com",
            "first_name": "Tyler",
            "last_name": "Higgins",
        },
        partial=True,
    )

    assert serializer.is_valid(), serializer.errors

    updated_user: User = serializer.save()  # pyright: ignore[reportAssignmentType]

    assert updated_user.username == "tylerh"
    assert updated_user.email == "tylerh@example.com"


@pytest.mark.django_db
def test_profile_serializer_normalizes_email():
    user = User.objects.create_user(
        username="tyler",
        email="tyler@example.com",
        password="test-password-123",
    )

    serializer = ProfileSerializer(
        user,
        data={
            "email": "  Tyler.New@Example.COM  ",
        },
        partial=True,
    )

    assert serializer.is_valid(), serializer.errors

    updated_user: User = serializer.save()  # pyright: ignore[reportAssignmentType]

    assert updated_user.email == "tyler.new@example.com"


@pytest.mark.django_db
def test_profile_serializer_rejects_duplicate_username_case_insensitively():
    User.objects.create_user(
        username="Irina",
        email="irina@example.com",
        password="test-password-123",
    )

    user = User.objects.create_user(
        username="tyler",
        email="tyler@example.com",
        password="test-password-123",
    )

    serializer = ProfileSerializer(
        user,
        data={
            "username": "IRINA",
        },
        partial=True,
    )

    assert not serializer.is_valid()

    assert "username" in serializer.errors


@pytest.mark.django_db
def test_profile_serializer_allows_existing_username_for_same_user():
    user = User.objects.create_user(
        username="tyler",
        email="tyler@example.com",
        password="test-password-123",
    )

    serializer = ProfileSerializer(
        user,
        data={
            "username": "Tyler",
        },
        partial=True,
    )

    assert serializer.is_valid(), serializer.errors


@pytest.mark.django_db
def test_profile_serializer_rejects_duplicate_email_case_insensitively():
    User.objects.create_user(
        username="irina",
        email="irina@example.com",
        password="test-password-123",
    )

    user = User.objects.create_user(
        username="tyler",
        email="tyler@example.com",
        password="test-password-123",
    )

    serializer = ProfileSerializer(
        user,
        data={
            "email": "IRINA@example.com",
        },
        partial=True,
    )

    assert not serializer.is_valid()

    assert "email" in serializer.errors


@pytest.mark.django_db
def test_profile_serializer_allows_existing_email_for_same_user():
    user = User.objects.create_user(
        username="tyler",
        email="tyler@example.com",
        password="test-password-123",
    )

    serializer = ProfileSerializer(
        user,
        data={
            "email": "TYLER@example.com",
        },
        partial=True,
    )

    assert serializer.is_valid(), serializer.errors


@pytest.mark.django_db
def test_profile_serializer_rejects_blank_username():
    user = User.objects.create_user(
        username="tyler",
        email="tyler@example.com",
        password="test-password-123",
    )

    serializer = ProfileSerializer(
        user,
        data={
            "username": "   ",
        },
        partial=True,
    )

    assert not serializer.is_valid()

    assert "username" in serializer.errors


@pytest.mark.django_db
def test_profile_serializer_rejects_blank_first_name():
    user = User.objects.create_user(
        username="tyler",
        email="tyler@example.com",
        password="test-password-123",
    )

    serializer = ProfileSerializer(
        user,
        data={
            "first_name": "   ",
        },
        partial=True,
    )

    assert not serializer.is_valid()

    assert "first_name" in serializer.errors


@pytest.mark.django_db
def test_profile_serializer_rejects_blank_last_name():
    user = User.objects.create_user(
        username="tyler",
        email="tyler@example.com",
        password="test-password-123",
    )

    serializer = ProfileSerializer(
        user,
        data={
            "last_name": "   ",
        },
        partial=True,
    )

    assert not serializer.is_valid()

    assert "last_name" in serializer.errors

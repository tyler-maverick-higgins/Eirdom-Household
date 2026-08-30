import pytest
from django.contrib.auth import get_user_model

from apps.accounts.serializers import PasswordChangeSerializer

User = get_user_model()


@pytest.mark.django_db
def test_password_change_serializer_accepts_valid_password_change():
    user = User.objects.create_user(
        username="tyler",
        email="tyler@example.com",
        password="Old-password-123!",
    )

    serializer = PasswordChangeSerializer(
        data={
            "current_password": "Old-password-123!",
            "new_password": "New-password-456!",
            "confirm_password": "New-password-456!",
        },
        context={
            "user": user,
        },
    )

    assert serializer.is_valid(), serializer.errors


@pytest.mark.django_db
def test_password_change_serializer_rejects_incorrect_current_password():
    user = User.objects.create_user(
        username="tyler",
        email="tyler@example.com",
        password="Old-password-123!",
    )

    serializer = PasswordChangeSerializer(
        data={
            "current_password": "wrong-password",
            "new_password": "New-password-456!",
            "confirm_password": "New-password-456!",
        },
        context={
            "user": user,
        },
    )

    assert not serializer.is_valid()

    assert "current_password" in serializer.errors


@pytest.mark.django_db
def test_password_change_serializer_rejects_mismatched_confirmation():
    user = User.objects.create_user(
        username="tyler",
        email="tyler@example.com",
        password="Old-password-123!",
    )

    serializer = PasswordChangeSerializer(
        data={
            "current_password": "Old-password-123!",
            "new_password": "New-password-456!",
            "confirm_password": "Different-password-789!",
        },
        context={
            "user": user,
        },
    )

    assert not serializer.is_valid()

    assert "confirm_password" in serializer.errors


@pytest.mark.django_db
def test_password_change_serializer_rejects_same_password():
    user = User.objects.create_user(
        username="tyler",
        email="tyler@example.com",
        password="Old-password-123!",
    )

    serializer = PasswordChangeSerializer(
        data={
            "current_password": "Old-password-123!",
            "new_password": "Old-password-123!",
            "confirm_password": "Old-password-123!",
        },
        context={
            "user": user,
        },
    )

    assert not serializer.is_valid()

    assert "new_password" in serializer.errors


@pytest.mark.django_db
def test_password_change_serializer_rejects_weak_password():
    user = User.objects.create_user(
        username="tyler",
        email="tyler@example.com",
        password="Old-password-123!",
    )

    serializer = PasswordChangeSerializer(
        data={
            "current_password": "Old-password-123!",
            "new_password": "password",
            "confirm_password": "password",
        },
        context={
            "user": user,
        },
    )

    assert not serializer.is_valid()

    assert "new_password" in serializer.errors


@pytest.mark.django_db
def test_password_change_serializer_requires_current_password():
    user = User.objects.create_user(
        username="tyler",
        email="tyler@example.com",
        password="Old-password-123!",
    )

    serializer = PasswordChangeSerializer(
        data={
            "new_password": "New-password-456!",
            "confirm_password": "New-password-456!",
        },
        context={
            "user": user,
        },
    )

    assert not serializer.is_valid()

    assert "current_password" in serializer.errors


@pytest.mark.django_db
def test_password_change_serializer_requires_new_password():
    user = User.objects.create_user(
        username="tyler",
        email="tyler@example.com",
        password="Old-password-123!",
    )

    serializer = PasswordChangeSerializer(
        data={
            "current_password": "Old-password-123!",
            "confirm_password": "New-password-456!",
        },
        context={
            "user": user,
        },
    )

    assert not serializer.is_valid()

    assert "new_password" in serializer.errors


@pytest.mark.django_db
def test_password_change_serializer_requires_confirmation():
    user = User.objects.create_user(
        username="tyler",
        email="tyler@example.com",
        password="Old-password-123!",
    )

    serializer = PasswordChangeSerializer(
        data={
            "current_password": "Old-password-123!",
            "new_password": "New-password-456!",
        },
        context={
            "user": user,
        },
    )

    assert not serializer.is_valid()

    assert "confirm_password" in serializer.errors

import pytest
from django.contrib.auth import get_user_model

from apps.accounts.policies import (
    can_access_steward,
    is_system_account,
)

User = get_user_model()


@pytest.mark.django_db
def test_normal_active_user_can_access_steward():
    user = User.objects.create_user(
        username="member",
        password="test-password-123",
    )

    assert user.is_active is True
    assert user.is_staff is False
    assert user.is_superuser is False

    assert can_access_steward(user) is True
    assert is_system_account(user) is False


@pytest.mark.django_db
def test_inactive_user_cannot_access_steward():
    user = User.objects.create_user(
        username="inactive",
        password="test-password-123",
        is_active=False,
    )

    assert can_access_steward(user) is False


@pytest.mark.django_db
def test_staff_user_cannot_access_steward():
    user = User.objects.create_user(
        username="staff",
        password="test-password-123",
        is_staff=True,
    )

    assert is_system_account(user) is True
    assert can_access_steward(user) is False


@pytest.mark.django_db
def test_superuser_cannot_access_steward():
    user = User.objects.create_superuser(
        username="superuser",
        email="superuser@example.com",
        password="test-password-123",
    )

    assert is_system_account(user) is True
    assert can_access_steward(user) is False


@pytest.mark.django_db
def test_superuser_is_blocked_even_without_staff_flag():
    user = User.objects.create_user(
        username="unusual-superuser",
        password="test-password-123",
    )

    user.is_superuser = True
    user.is_staff = False
    user.save(
        update_fields=[
            "is_superuser",
            "is_staff",
        ]
    )

    assert is_system_account(user) is True
    assert can_access_steward(user) is False

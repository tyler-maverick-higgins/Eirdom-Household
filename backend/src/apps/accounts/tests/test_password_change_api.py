import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from apps.accounts.models import User


@pytest.fixture
def api_client():
    return APIClient()


@pytest.mark.django_db
def test_password_change_requires_authentication(
    api_client,
):
    response = api_client.post(
        reverse("accounts:password-change"),
        {
            "current_password": "Old-password-123!",
            "new_password": "New-password-456!",
            "confirm_password": "New-password-456!",
        },
        format="json",
    )

    assert response.status_code == (status.HTTP_403_FORBIDDEN)


@pytest.mark.django_db
def test_user_can_change_password(
    api_client,
):
    user = User.objects.create_user(
        username="tyler",
        email="tyler@example.com",
        password="Old-password-123!",
    )

    api_client.force_authenticate(
        user=user,
    )

    response = api_client.post(
        reverse("accounts:password-change"),
        {
            "current_password": "Old-password-123!",
            "new_password": "New-password-456!",
            "confirm_password": "New-password-456!",
        },
        format="json",
    )

    assert response.status_code == status.HTTP_200_OK

    user.refresh_from_db()

    assert user.check_password("New-password-456!")
    assert not user.check_password("Old-password-123!")


@pytest.mark.django_db
def test_password_change_returns_success_message(
    api_client,
):
    user = User.objects.create_user(
        username="tyler",
        email="tyler@example.com",
        password="Old-password-123!",
    )

    api_client.force_authenticate(
        user=user,
    )

    response = api_client.post(
        reverse("accounts:password-change"),
        {
            "current_password": "Old-password-123!",
            "new_password": "New-password-456!",
            "confirm_password": "New-password-456!",
        },
        format="json",
    )

    assert response.status_code == status.HTTP_200_OK

    assert response.data == {
        "detail": "Password changed successfully.",
    }


@pytest.mark.django_db
def test_password_change_rejects_incorrect_current_password(
    api_client,
):
    user = User.objects.create_user(
        username="tyler",
        email="tyler@example.com",
        password="Old-password-123!",
    )

    api_client.force_authenticate(
        user=user,
    )

    response = api_client.post(
        reverse("accounts:password-change"),
        {
            "current_password": "Wrong-password-123!",
            "new_password": "New-password-456!",
            "confirm_password": "New-password-456!",
        },
        format="json",
    )

    assert response.status_code == (status.HTTP_400_BAD_REQUEST)

    assert "current_password" in response.data

    user.refresh_from_db()

    assert user.check_password("Old-password-123!")


@pytest.mark.django_db
def test_password_change_rejects_mismatched_confirmation(
    api_client,
):
    user = User.objects.create_user(
        username="tyler",
        email="tyler@example.com",
        password="Old-password-123!",
    )

    api_client.force_authenticate(
        user=user,
    )

    response = api_client.post(
        reverse("accounts:password-change"),
        {
            "current_password": "Old-password-123!",
            "new_password": "New-password-456!",
            "confirm_password": "Different-password-789!",
        },
        format="json",
    )

    assert response.status_code == (status.HTTP_400_BAD_REQUEST)

    assert "confirm_password" in response.data

    user.refresh_from_db()

    assert user.check_password("Old-password-123!")


@pytest.mark.django_db
def test_password_change_rejects_weak_password(
    api_client,
):
    user = User.objects.create_user(
        username="tyler",
        email="tyler@example.com",
        password="Old-password-123!",
    )

    api_client.force_authenticate(
        user=user,
    )

    response = api_client.post(
        reverse("accounts:password-change"),
        {
            "current_password": "Old-password-123!",
            "new_password": "password",
            "confirm_password": "password",
        },
        format="json",
    )

    assert response.status_code == (status.HTTP_400_BAD_REQUEST)

    assert "new_password" in response.data

    user.refresh_from_db()

    assert user.check_password("Old-password-123!")


@pytest.mark.django_db
def test_staff_account_cannot_change_password(
    api_client,
):
    user = User.objects.create_user(
        username="staff",
        email="staff@example.com",
        password="Old-password-123!",
        is_staff=True,
    )

    api_client.force_authenticate(
        user=user,
    )

    response = api_client.post(
        reverse("accounts:password-change"),
        {
            "current_password": "Old-password-123!",
            "new_password": "New-password-456!",
            "confirm_password": "New-password-456!",
        },
        format="json",
    )

    assert response.status_code == (status.HTTP_403_FORBIDDEN)

    user.refresh_from_db()

    assert user.check_password("Old-password-123!")


@pytest.mark.django_db
def test_superuser_cannot_change_password(
    api_client,
):
    user = User.objects.create_superuser(
        username="superuser",
        email="superuser@example.com",
        password="Old-password-123!",
    )

    api_client.force_authenticate(
        user=user,
    )

    response = api_client.post(
        reverse("accounts:password-change"),
        {
            "current_password": "Old-password-123!",
            "new_password": "New-password-456!",
            "confirm_password": "New-password-456!",
        },
        format="json",
    )

    assert response.status_code == (status.HTTP_403_FORBIDDEN)

    user.refresh_from_db()

    assert user.check_password("Old-password-123!")


@pytest.mark.django_db
def test_password_change_preserves_authenticated_session(
    api_client,
):
    user = User.objects.create_user(
        username="tyler",
        email="tyler@example.com",
        password="Old-password-123!",
    )

    logged_in = api_client.login(
        username="tyler",
        password="Old-password-123!",
    )

    assert logged_in is True

    response = api_client.post(
        reverse("accounts:password-change"),
        {
            "current_password": "Old-password-123!",
            "new_password": "New-password-456!",
            "confirm_password": "New-password-456!",
        },
        format="json",
    )

    assert response.status_code == status.HTTP_200_OK

    user.refresh_from_db()

    assert user.check_password("New-password-456!")

    profile_response = api_client.get(
        reverse("accounts:profile"),
    )

    assert profile_response.status_code == (status.HTTP_200_OK)

    assert profile_response.data["username"] == "tyler"

import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from apps.accounts.models import User


@pytest.fixture
def api_client():
    return APIClient()


@pytest.mark.django_db
def test_profile_requires_authentication(api_client):
    response = api_client.get(
        reverse("accounts:profile"),
    )

    assert response.status_code == (status.HTTP_403_FORBIDDEN)


@pytest.mark.django_db
def test_user_can_view_own_profile(
    api_client,
):
    user = User.objects.create_user(
        username="tyler",
        email="tyler@example.com",
        first_name="Tyler",
        last_name="Higgins",
        password="test-password-123",
    )

    api_client.force_authenticate(user=user)

    response = api_client.get(
        reverse("accounts:profile"),
    )

    assert response.status_code == status.HTTP_200_OK

    assert response.data == {
        "id": user.pk,
        "username": "tyler",
        "first_name": "Tyler",
        "last_name": "Higgins",
        "email": "tyler@example.com",
    }


@pytest.mark.django_db
def test_user_can_update_own_profile(
    api_client,
):
    user = User.objects.create_user(
        username="tyler",
        email="tyler@example.com",
        first_name="Tyler",
        last_name="Higgins",
        password="test-password-123",
    )

    api_client.force_authenticate(user=user)

    response = api_client.patch(
        reverse("accounts:profile"),
        {
            "first_name": "Tyler Michael",
            "email": "new@example.com",
        },
        format="json",
    )

    assert response.status_code == status.HTTP_200_OK

    user.refresh_from_db()

    assert user.first_name == "Tyler Michael"
    assert user.email == "new@example.com"


@pytest.mark.django_db
def test_profile_update_cannot_escalate_privileges(
    api_client,
):
    user = User.objects.create_user(
        username="tyler",
        email="tyler@example.com",
        password="test-password-123",
    )

    api_client.force_authenticate(user=user)

    response = api_client.patch(
        reverse("accounts:profile"),
        {
            "is_staff": True,
            "is_superuser": True,
            "is_active": False,
        },
        format="json",
    )

    assert response.status_code == status.HTTP_200_OK

    user.refresh_from_db()

    assert user.is_staff is False
    assert user.is_superuser is False
    assert user.is_active is True


@pytest.mark.django_db
def test_profile_response_does_not_expose_sensitive_fields(
    api_client,
):
    user = User.objects.create_user(
        username="tyler",
        email="tyler@example.com",
        password="test-password-123",
    )

    api_client.force_authenticate(user=user)

    response = api_client.get(
        reverse("accounts:profile"),
    )

    assert response.status_code == status.HTTP_200_OK

    assert set(response.data.keys()) == {
        "id",
        "username",
        "first_name",
        "last_name",
        "email",
    }


@pytest.mark.django_db
def test_staff_account_cannot_access_profile(
    api_client,
):
    user = User.objects.create_user(
        username="staff",
        email="staff@example.com",
        password="test-password-123",
        is_staff=True,
    )

    api_client.force_authenticate(user=user)

    response = api_client.get(
        reverse("accounts:profile"),
    )

    assert response.status_code == (status.HTTP_403_FORBIDDEN)


@pytest.mark.django_db
def test_superuser_cannot_access_profile(
    api_client,
):
    user = User.objects.create_superuser(
        username="superuser",
        email="superuser@example.com",
        password="test-password-123",
    )

    api_client.force_authenticate(user=user)

    response = api_client.get(
        reverse("accounts:profile"),
    )

    assert response.status_code == (status.HTTP_403_FORBIDDEN)

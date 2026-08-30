import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

User = get_user_model()


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def user(db):
    return User.objects.create_user(
        username="tyler",
        password="test-password-123",
        email="tyler@example.com",
        first_name="Tyler",
        last_name="Higgins",
    )


@pytest.mark.django_db
def test_login_with_valid_credentials(api_client, user):
    response = api_client.post(
        reverse("accounts:login"),
        {
            "username": "tyler",
            "password": "test-password-123",
        },
        format="json",
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.data["id"] == user.id
    assert response.data["username"] == "tyler"
    assert response.data["first_name"] == "Tyler"
    assert response.data["last_name"] == "Higgins"
    assert response.data["email"] == "tyler@example.com"


@pytest.mark.django_db
def test_login_with_invalid_credentials(api_client, user):
    response = api_client.post(
        reverse("accounts:login"),
        {
            "username": "tyler",
            "password": "wrong-password",
        },
        format="json",
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.data == {
        "detail": "Invalid username or password.",
    }


@pytest.mark.django_db
def test_current_user_requires_authentication(api_client):
    response = api_client.get(reverse("accounts:current-user"))

    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_current_user_returns_authenticated_user(api_client, user):
    api_client.force_authenticate(user=user)

    response = api_client.get(reverse("accounts:current-user"))

    assert response.status_code == status.HTTP_200_OK
    assert response.data["id"] == user.id
    assert response.data["username"] == "tyler"


@pytest.mark.django_db
def test_logout(api_client, user):
    api_client.force_authenticate(user=user)

    response = api_client.post(reverse("accounts:logout"))

    assert response.status_code == status.HTTP_204_NO_CONTENT


@pytest.mark.django_db
def test_login_creates_authenticated_session(api_client, user):
    login_response = api_client.post(
        reverse("accounts:login"),
        {
            "username": "tyler",
            "password": "test-password-123",
        },
        format="json",
    )

    assert login_response.status_code == status.HTTP_200_OK

    current_user_response = api_client.get(
        reverse("accounts:current-user"),
    )

    assert current_user_response.status_code == status.HTTP_200_OK
    assert current_user_response.data["id"] == user.id
    assert current_user_response.data["username"] == "tyler"


@pytest.mark.django_db
def test_logout_ends_authenticated_session(api_client, user):
    login_response = api_client.post(
        reverse("accounts:login"),
        {
            "username": "tyler",
            "password": "test-password-123",
        },
        format="json",
    )

    assert login_response.status_code == status.HTTP_200_OK

    logout_response = api_client.post(
        reverse("accounts:logout"),
    )

    assert logout_response.status_code == status.HTTP_204_NO_CONTENT

    current_user_response = api_client.get(
        reverse("accounts:current-user"),
    )

    assert current_user_response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_csrf_endpoint_returns_token(api_client):
    response = api_client.get(reverse("accounts:csrf"))

    assert response.status_code == status.HTTP_200_OK
    assert response.data["csrfToken"]


@pytest.mark.django_db
def test_staff_user_cannot_login_to_steward(
    api_client,
):
    user = User.objects.create_user(
        username="staff",
        password="test-password-123",
        is_staff=True,
    )

    response = api_client.post(
        "/api/auth/login/",
        {
            "username": user.username,
            "password": "test-password-123",
        },
        format="json",
    )

    assert response.status_code == (status.HTTP_403_FORBIDDEN)

    assert response.data == {"detail": "This account cannot sign in to Steward."}


@pytest.mark.django_db
def test_superuser_cannot_login_to_steward(
    api_client,
):
    user = User.objects.create_superuser(
        username="system-admin",
        email="admin@example.com",
        password="test-password-123",
    )

    response = api_client.post(
        "/api/auth/login/",
        {
            "username": user.username,
            "password": "test-password-123",
        },
        format="json",
    )

    assert response.status_code == (status.HTTP_403_FORBIDDEN)

    assert response.data == {"detail": "This account cannot sign in to Steward."}


@pytest.mark.django_db
def test_staff_user_cannot_access_current_user_endpoint(
    api_client,
):
    user = User.objects.create_user(
        username="staff",
        password="test-password-123",
        is_staff=True,
    )

    api_client.force_authenticate(
        user=user,
    )

    response = api_client.get(
        "/api/auth/me/",
    )

    assert response.status_code == (status.HTTP_403_FORBIDDEN)


@pytest.mark.django_db
def test_superuser_cannot_access_current_user_endpoint(
    api_client,
):
    user = User.objects.create_superuser(
        username="system-admin",
        email="admin@example.com",
        password="test-password-123",
    )

    api_client.force_authenticate(
        user=user,
    )

    response = api_client.get(
        "/api/auth/me/",
    )

    assert response.status_code == (status.HTTP_403_FORBIDDEN)

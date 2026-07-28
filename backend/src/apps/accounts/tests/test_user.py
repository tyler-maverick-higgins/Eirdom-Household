import pytest

from apps.accounts.models import User


@pytest.mark.django_db
def test_create_user():
    user = User.objects.create_user(
        username="test-user",
        password="test-password",
    )

    assert user.username == "test-user"
    assert user.check_password("test-password")
    assert user.is_active is True

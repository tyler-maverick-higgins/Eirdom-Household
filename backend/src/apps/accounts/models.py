from django.contrib.auth.models import AbstractUser
from django.db import models


# Custom User model that extends the default Django User model
class User(AbstractUser):
    # You can add additional fields here if needed
    """Eirdom Household user account."""

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "user"
        verbose_name_plural = "users"
        ordering = ["username"]

    def __str__(self) -> str:
        return self.username

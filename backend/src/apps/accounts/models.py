from django.contrib.auth.models import AbstractUser


# Custom User model that extends the default Django User model
class User(AbstractUser):
    # You can add additional fields here if needed
    """Eirdom Household user account."""

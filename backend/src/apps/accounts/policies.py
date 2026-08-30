from typing import Protocol


class StewardUserLike(Protocol):
    is_active: bool
    is_staff: bool
    is_superuser: bool


def is_system_account(user: StewardUserLike) -> bool:
    """
    Return whether a user is reserved for Django/system administration.

    Staff and superuser accounts are intentionally separated from normal
    Steward household accounts.
    """

    return user.is_staff or user.is_superuser


def can_access_steward(user: StewardUserLike) -> bool:
    """
    Return whether a user account may access the Steward application.

    Steward application users must be active and must not be Django staff
    or Django superusers.

    Household authorization is handled separately through household
    memberships and roles.
    """

    return user.is_active and not is_system_account(user)

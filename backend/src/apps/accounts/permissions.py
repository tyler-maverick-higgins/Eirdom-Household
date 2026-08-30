from rest_framework.permissions import BasePermission

from .policies import can_access_steward


class IsStewardUser(BasePermission):
    """
    Allow access only to authenticated accounts permitted to use Steward.

    Django staff and superuser accounts are intentionally excluded from
    Steward application APIs even when they have a valid Django session.
    """

    message = "This account cannot access Steward."

    def has_permission(  # pyright: ignore[reportIncompatibleMethodOverride]
        self,
        request,
        _view,
    ) -> bool:
        user = request.user

        return bool(user and user.is_authenticated and can_access_steward(user))

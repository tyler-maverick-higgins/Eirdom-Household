from django.shortcuts import get_object_or_404
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from .models import Household, HouseholdMembership
from .serializers import HouseholdInvitationSerializer, HouseholdSerializer


class HouseholdListView(generics.ListAPIView):
    serializer_class = HouseholdSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):  # pyright: ignore[reportIncompatibleMethodOverride]
        return (
            Household.objects.filter(
                memberships__user=self.request.user,
                memberships__is_active=True,
            )
            .distinct()
            .order_by("id")
        )


class HouseholdInvitationCreateView(generics.CreateAPIView):
    serializer_class = HouseholdInvitationSerializer
    permission_classes = [IsAuthenticated]

    def get_household(self):
        return get_object_or_404(
            Household,
            pk=self.kwargs["household_id"],
        )

    def check_household_admin(self, household):
        membership = HouseholdMembership.objects.filter(
            household=household,
            user=self.request.user,
            is_active=True,
        ).first()

        if membership is None:
            self.permission_denied(
                self.request,
                message="You are not an active member of this household.",
            )

        if membership.role not in {
            HouseholdMembership.Roles.OWNER,
            HouseholdMembership.Roles.ADMINISTRATOR,
        }:
            self.permission_denied(
                self.request,
                message="Only household owners and administrators may send invitations.",
            )

    def get_serializer_context(self):
        context = super().get_serializer_context()
        household = self.get_household()

        context["household"] = household

        return context

    def perform_create(self, serializer):
        household = self.get_household()
        self.check_household_admin(household)

        serializer.save()

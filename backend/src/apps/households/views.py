import hashlib

from django.contrib.auth import get_user_model
from django.db import transaction
from django.shortcuts import get_object_or_404
from rest_framework import generics, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import (
    Household,
    HouseholdInvitation,
    HouseholdMembership,
)
from .serializers import (
    HouseholdDetailSerializer,
    HouseholdInvitationSerializer,
    HouseholdInvitationValidationSerializer,
    HouseholdSerializer,
)
from .tasks import send_household_invitation_task

User = get_user_model()


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


class HouseholdDetailView(generics.RetrieveAPIView):
    serializer_class = HouseholdDetailSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):  # pyright: ignore[reportIncompatibleMethodOverride]
        return Household.objects.filter(
            memberships__user=self.request.user,
            memberships__is_active=True,
        ).distinct()


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
                message=("Only household owners and administrators may send invitations."),
            )

    def get_serializer_context(self):
        context = super().get_serializer_context()
        household = self.get_household()

        context["household"] = household

        return context

    def perform_create(self, serializer):
        household = self.get_household()
        self.check_household_admin(household)

        with transaction.atomic():
            invitation = serializer.save()

            transaction.on_commit(
                lambda invitation_id=invitation.id: send_household_invitation_task.delay(  # pyright: ignore[reportCallIssue, reportAttributeAccessIssue]
                    invitation_id,
                )
            )


class HouseholdInvitationValidationView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, token):
        token_hash = hashlib.sha256(token.encode("utf-8")).hexdigest()

        invitation = get_object_or_404(
            HouseholdInvitation.objects.select_related(
                "household",
                "invited_by",
            ),
            token_hash=token_hash,
            status=HouseholdInvitation.Status.PENDING,
        )

        if invitation.is_expired:
            return Response(
                {"detail": "This invitation has expired."},
                status=status.HTTP_410_GONE,
            )

        inviter_name = invitation.invited_by.get_full_name() or invitation.invited_by.username

        account_exists = User.objects.filter(
            email__iexact=invitation.email,
        ).exists()

        serializer = HouseholdInvitationValidationSerializer(
            {
                "household_name": invitation.household.name,
                "email": invitation.email,
                "role": invitation.role,
                "inviter_name": inviter_name,
                "expires_at": invitation.expires_at,
                "account_exists": account_exists,
            }
        )

        return Response(serializer.data)

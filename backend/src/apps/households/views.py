import hashlib
from typing import cast

from django.contrib.auth import get_user_model
from django.db import transaction
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import generics, status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.accounts.permissions import IsStewardUser

from .models import (
    Household,
    HouseholdInvitation,
    HouseholdMembership,
)
from .serializers import (
    HouseholdDetailSerializer,
    HouseholdInvitationAcceptSerializer,
    HouseholdInvitationSerializer,
    HouseholdInvitationValidationSerializer,
    HouseholdMemberSerializer,
    HouseholdMembershipUpdateSerializer,
    HouseholdOwnershipTransferSerializer,
    HouseholdSerializer,
    HouseholdUpdateSerializer,
)
from .tasks import send_household_invitation_task

User = get_user_model()


def get_household_management_membership(household, user):
    membership = HouseholdMembership.objects.filter(
        household=household,
        user=user,
        is_active=True,
    ).first()

    if membership is None:
        return None

    if membership.role not in {
        HouseholdMembership.Roles.OWNER,
        HouseholdMembership.Roles.ADMINISTRATOR,
    }:
        return None

    return membership


class HouseholdListView(generics.ListAPIView):
    serializer_class = HouseholdSerializer
    permission_classes = [IsStewardUser]

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
    permission_classes = [IsStewardUser]

    def get_queryset(self):  # pyright: ignore[reportIncompatibleMethodOverride]
        return Household.objects.filter(
            memberships__user=self.request.user,
            memberships__is_active=True,
        ).distinct()


class HouseholdSettingsUpdateView(APIView):
    permission_classes = [IsStewardUser]

    def patch(self, request, household_id):
        household = get_object_or_404(Household, pk=household_id)

        membership = get_household_management_membership(
            household,
            request.user,
        )

        if membership is None:
            self.permission_denied(
                request,
                message=("Only household owners and administrators may manage household settings."),
            )

        serializer = HouseholdUpdateSerializer(
            household,
            data=request.data,
            partial=True,
        )
        serializer.is_valid(raise_exception=True)

        serializer.save()

        response_serializer = HouseholdSerializer(household)

        return Response(
            response_serializer.data,
            status=status.HTTP_200_OK,
        )


class HouseholdMemberAdministrationView(APIView):
    permission_classes = [IsStewardUser]

    def get(self, request, household_id):
        household = get_object_or_404(
            Household,
            pk=household_id,
        )

        membership = get_household_management_membership(
            household,
            request.user,
        )

        if membership is None:
            self.permission_denied(
                request,
                message=("Only household owners and administrator may manage household members"),
            )

        memberships = (
            HouseholdMembership.objects.filter(
                household=household,
                user__is_staff=False,
                user__is_superuser=False,
            )
            .select_related("user")
            .order_by("created_at")
        )

        serializer = HouseholdMemberSerializer(
            memberships,
            many=True,
        )

        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )


class HouseholdMembershipUpdateView(APIView):
    permission_classes = [IsStewardUser]

    def patch(
        self,
        request,
        household_id,
        membership_id,
    ):
        household = get_object_or_404(
            Household,
            pk=household_id,
        )

        acting_membership = get_household_management_membership(
            household,
            request.user,
        )

        if acting_membership is None:
            self.permission_denied(
                request,
                message=("Only household owners and administrators may manage household members."),
            )

        target_membership = get_object_or_404(
            HouseholdMembership.objects.select_related("user").filter(
                user__is_staff=False,
                user__is_superuser=False,
            ),
            pk=membership_id,
            household=household,
        )

        if target_membership.user.pk == request.user.pk:
            return Response(
                {"detail": ("You cannot manage your own household membership here.")},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if target_membership.role == HouseholdMembership.Roles.OWNER:
            return Response(
                {"detail": ("The household owner must be managed through ownership transfer.")},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if (
            acting_membership.role == HouseholdMembership.Roles.ADMINISTRATOR
            and target_membership.role == HouseholdMembership.Roles.ADMINISTRATOR
        ):
            self.permission_denied(
                request,
                message=("Household administrators cannot manage other administrators."),
            )

        serializer = HouseholdMembershipUpdateSerializer(
            target_membership,
            data=request.data,
            partial=True,
        )

        serializer.is_valid(
            raise_exception=True,
        )

        validated_data = cast(dict[str, str | bool], serializer.validated_data)
        requested_role = validated_data.get(
            "role",
            target_membership.role,
        )

        if (
            acting_membership.role == HouseholdMembership.Roles.ADMINISTRATOR
            and requested_role == HouseholdMembership.Roles.ADMINISTRATOR
        ):
            self.permission_denied(
                request,
                message=("Only the household owner may assign the Administrator role."),
            )

        updated_membership = serializer.save()

        response_serializer = HouseholdMemberSerializer(updated_membership)

        return Response(
            response_serializer.data,
            status=status.HTTP_200_OK,
        )


class HouseholdOwnershipTransferView(APIView):
    permission_classes = [IsStewardUser]

    def post(self, request, household_id):
        household = get_object_or_404(
            Household,
            pk=household_id,
        )

        current_owner = (
            HouseholdMembership.objects.filter(
                household=household,
                user=request.user,
                role=HouseholdMembership.Roles.OWNER,
                is_active=True,
            )
            .select_related("user")
            .first()
        )

        if current_owner is None:
            self.permission_denied(
                request,
                message=("Only the current household owner may transfer ownership."),
            )

        serializer = HouseholdOwnershipTransferSerializer(
            data=request.data,
            context={
                "household": household,
                "current_owner": current_owner,
            },
        )
        serializer.is_valid(raise_exception=True)

        target_membership = serializer.context["target_membership"]

        with transaction.atomic():
            current_owner.role = HouseholdMembership.Roles.ADMINISTRATOR
            current_owner.save(
                update_fields=[
                    "role",
                    "updated_at",
                ]
            )

            target_membership.role = HouseholdMembership.Roles.OWNER

            target_membership.save(
                update_fields=[
                    "role",
                    "updated_at",
                ]
            )

            response_serializer = HouseholdMemberSerializer(target_membership)

            return Response(
                response_serializer.data,
                status=status.HTTP_200_OK,
            )


class HouseholdInvitationCreateView(generics.CreateAPIView):
    serializer_class = HouseholdInvitationSerializer
    permission_classes = [IsStewardUser]

    def get_household(self):
        return get_object_or_404(
            Household,
            pk=self.kwargs["household_id"],
        )

    def check_household_admin(self, household):
        membership = get_household_management_membership(
            household,
            self.request.user,
        )

        if membership is None:
            self.permission_denied(
                self.request,
                message=("Only household owners and administrators may manage invitations."),
            )

        return membership

    def get_serializer_context(self):
        context = super().get_serializer_context()

        household = self.get_household()

        context["household"] = household

        return context

    def perform_create(self, serializer):
        household = self.get_household()

        acting_membership = self.check_household_admin(
            household,
        )

        requested_role = serializer.validated_data.get(
            "role",
        )

        if (
            acting_membership.role == HouseholdMembership.Roles.ADMINISTRATOR
            and requested_role == HouseholdMembership.Roles.ADMINISTRATOR
        ):
            self.permission_denied(
                self.request,
                message=("Only the household owner may invite an Administrator."),
            )

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


class HouseholdInvitationAcceptView(APIView):
    permission_classes = [IsStewardUser]

    def post(self, request, token):
        serializer = HouseholdInvitationAcceptSerializer(
            data={"token": token},
            context={"request": request},
        )
        serializer.is_valid(raise_exception=True)

        invitation = serializer.context["invitation"]

        user_email = (request.user.email or "").strip().lower()
        invitation_email = invitation.email.strip().lower()

        if user_email != invitation_email:
            return Response(
                {"detail": ("This invitation was sent to a different email address.")},
                status=status.HTTP_403_FORBIDDEN,
            )

        with transaction.atomic():
            membership, created = HouseholdMembership.objects.get_or_create(
                household=invitation.household,
                user=request.user,
                defaults={
                    "role": invitation.role,
                    "is_active": True,
                },
            )

            if not created:
                membership.role = invitation.role
                membership.is_active = True
                membership.save(
                    update_fields=[
                        "role",
                        "is_active",
                        "updated_at",
                    ]
                )

            invitation.status = HouseholdInvitation.Status.ACCEPTED
            invitation.accepted_at = timezone.now()
            invitation.save(
                update_fields=[
                    "status",
                    "accepted_at",
                    "updated_at",
                ]
            )

        return Response(
            {
                "household_id": invitation.household_id,
                "household_name": invitation.household.name,
                "membership_id": membership.pk,
                "role": membership.role,
                "status": invitation.status,
            },
            status=status.HTTP_200_OK,
        )


class HouseholdInvitationResendView(APIView):
    permission_classes = [IsStewardUser]

    def post(self, request, invitation_id):
        invitation = get_object_or_404(
            HouseholdInvitation.objects.select_related("household"),
            pk=invitation_id,
        )

        membership = get_household_management_membership(
            invitation.household,
            request.user,
        )

        if membership is None:
            self.permission_denied(
                request,
                message=("Only household owners and administrators may manage invitations."),
            )

        if invitation.status != HouseholdInvitation.Status.PENDING:
            return Response(
                {"detail": "Only pending invitations may be resent."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        transaction.on_commit(
            lambda invitation_id=invitation.id: send_household_invitation_task.delay(  # pyright: ignore[reportCallIssue, reportAttributeAccessIssue]
                invitation_id,
            )
        )

        serializer = HouseholdInvitationSerializer(invitation)

        return Response(serializer.data, status=status.HTTP_200_OK)


class HouseholdInvitationCancelView(APIView):
    permission_classes = [IsStewardUser]

    def post(self, request, invitation_id):
        invitation = get_object_or_404(
            HouseholdInvitation.objects.select_related("household"),
            pk=invitation_id,
        )

        membership = get_household_management_membership(
            invitation.household,
            request.user,
        )

        if membership is None:
            self.permission_denied(
                request,
                message=("Only household owners and administrators may manage invitations."),
            )

        if invitation.status != HouseholdInvitation.Status.PENDING:
            return Response(
                {"detail": "Only pending invitations may be canceled."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        invitation.status = HouseholdInvitation.Status.CANCELED
        invitation.token_hash = ""
        invitation.expires_at = None
        invitation.save(
            update_fields=[
                "status",
                "token_hash",
                "expires_at",
                "updated_at",
            ]
        )

        serializer = HouseholdInvitationSerializer(invitation)

        return Response(serializer.data, status=status.HTTP_200_OK)

import hashlib

from django.contrib.auth import get_user_model
from rest_framework import serializers

from .models import Household, HouseholdInvitation, HouseholdMembership

User = get_user_model()


class HouseholdSerializer(serializers.ModelSerializer):
    class Meta:
        model = Household
        fields = [
            "id",
            "name",
            "email",
            "household_type",
            "created_at",
            "updated_at",
        ]
        read_only_fields = fields


class HouseholdUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Household
        fields = [
            "name",
            "email",
            "household_type",
        ]

    def validate_name(self, value):
        name = value.strip()

        if not name:
            raise serializers.ValidationError("Household name is required.")

        return name

    def validate_email(self, value):
        return value.strip().lower()


class HouseholdMemberUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "first_name",
            "last_name",
            "email",
        ]
        read_only_fields = fields


class HouseholdMemberSerializer(serializers.ModelSerializer):
    user = HouseholdMemberUserSerializer(read_only=True)

    class Meta:
        model = HouseholdMembership
        fields = [
            "id",
            "user",
            "role",
            "is_active",
            "created_at",
            "updated_at",
        ]
        read_only_fields = fields


class HouseholdMembershipUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = HouseholdMembership
        fields = [
            "role",
            "is_active",
        ]

    def validate_role(self, value):
        if value == HouseholdMembership.Roles.OWNER:
            raise serializers.ValidationError(
                "Ownership must be transferred using the ownership transfer action."
            )

        return value

    def validate(self, attrs):
        if not attrs:
            raise serializers.ValidationError("Provide at least one membership field to update.")

        return attrs


class HouseholdDetailSerializer(serializers.ModelSerializer):
    members = serializers.SerializerMethodField()
    pending_invitations = serializers.SerializerMethodField()

    class Meta:
        model = Household
        fields = [
            "id",
            "name",
            "email",
            "household_type",
            "created_at",
            "updated_at",
            "members",
            "pending_invitations",
        ]
        read_only_fields = fields

    def get_members(self, household):
        memberships = household.memberships.filter(
            is_active=True,
            user__is_staff=False,
            user__is_superuser=False,
        ).select_related("user")

        return HouseholdMemberSerializer(
            memberships,
            many=True,
        ).data

    def get_pending_invitations(self, household):
        invitations = household.invitations.filter(
            status=HouseholdInvitation.Status.PENDING,
        )

        return HouseholdInvitationSerializer(
            invitations,
            many=True,
        ).data


class HouseholdInvitationSerializer(serializers.ModelSerializer):
    class Meta:
        model = HouseholdInvitation
        fields = [
            "id",
            "email",
            "role",
            "status",
            "invited_by",
            "expires_at",
            "last_sent_at",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "status",
            "invited_by",
            "expires_at",
            "last_sent_at",
            "created_at",
            "updated_at",
        ]

    def validate_email(self, value):
        email = value.strip().lower()
        household = self.context["household"]

        already_member = HouseholdMembership.objects.filter(
            household=household, user__email__iexact=email, is_active=True
        ).exists()

        if already_member:
            raise serializers.ValidationError("This person is already an active household member.")

        pending_invitation = HouseholdInvitation.objects.filter(
            household=household, email__iexact=email, status=HouseholdInvitation.Status.PENDING
        ).exists()

        if pending_invitation:
            raise serializers.ValidationError(
                "A pending invitation already exists for this email address."
            )

        return email

    def validate_role(self, value):
        allowed_roles = {
            HouseholdMembership.Roles.ADMINISTRATOR,
            HouseholdMembership.Roles.MEMBER,
        }

        if value not in allowed_roles:
            raise serializers.ValidationError(
                "Invitations may only assign the Administrator or Member role."
            )

        return value

    def create(self, validated_data):
        household = self.context["household"]
        request = self.context["request"]

        return HouseholdInvitation.objects.create(
            household=household, invited_by=request.user, **validated_data
        )


class HouseholdInvitationValidationSerializer(serializers.Serializer):
    household_name = serializers.CharField(read_only=True)
    email = serializers.EmailField(read_only=True)
    role = serializers.CharField(read_only=True)
    inviter_name = serializers.CharField(read_only=True)
    expires_at = serializers.DateTimeField(read_only=True)
    account_exists = serializers.BooleanField(read_only=True)


class HouseholdInvitationAcceptSerializer(serializers.Serializer):
    token = serializers.CharField(write_only=True)

    def validate_token(self, token):
        token_hash = hashlib.sha256(token.encode("utf-8")).hexdigest()

        invitation = (
            HouseholdInvitation.objects.select_related("household")
            .filter(
                token_hash=token_hash,
                status=HouseholdInvitation.Status.PENDING,
            )
            .first()
        )

        if invitation is None:
            raise serializers.ValidationError("This invitation is invalid or no longer available.")

        if invitation.is_expired:
            raise serializers.ValidationError("This invitation has expired.")

        self.context["invitation"] = invitation

        return token


class HouseholdOwnershipTransferSerializer(serializers.Serializer):
    membership_id = serializers.IntegerField()

    def validate_membership_id(self, value):
        household = self.context["household"]
        current_owner = self.context["current_owner"]

        target_membership = (
            HouseholdMembership.objects.select_related("user")
            .filter(
                pk=value,
                household=household,
                is_active=True,
                user__is_staff=False,
                user__is_superuser=False,
            )
            .first()
        )

        if target_membership is None:
            raise serializers.ValidationError("Select an active member of this household.")

        if target_membership.pk == current_owner.pk:
            raise serializers.ValidationError("The selected member is already the household owner.")

        self.context["target_membership"] = target_membership

        return value

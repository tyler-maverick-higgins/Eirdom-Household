from rest_framework import serializers

from .models import HouseholdInvitation, HouseholdMembership


class HouseholdInvitationSerializer(serializers.ModelSerializer):
    class Meta:
        model = HouseholdInvitation
        fields = [
            "id",
            "email",
            "role",
            "status",
            "invited_by",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "status", "invited_by", "created_at", "updated_at"]

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

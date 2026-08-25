import hashlib

from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers

from apps.households.models import HouseholdInvitation

User = get_user_model()


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(
        write_only=True,
        trim_whitespace=False,
    )


class InvitationRegistrationSerializer(serializers.Serializer):
    token = serializers.CharField(write_only=True)
    username = serializers.CharField(
        max_length=150,
    )
    first_name = serializers.CharField(
        max_length=150,
    )
    last_name = serializers.CharField(
        max_length=150,
    )
    password = serializers.CharField(
        write_only=True,
        trim_whitespace=False,
    )

    def validate_token(self, token):
        token_hash = hashlib.sha256(token.encode("utf-8")).hexdigest()

        invitation = (
            HouseholdInvitation.objects.select_related(
                "household",
            )
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

        if User.objects.filter(
            email__iexact=invitation.email,
        ).exists():
            raise serializers.ValidationError("An account already exists for this invitation.")

        self.context["invitation"] = invitation

        return token

    def validate_username(self, username):
        username = username.strip()

        if not username:
            raise serializers.ValidationError("Username is required.")

        if User.objects.filter(
            username__iexact=username,
        ).exists():
            raise serializers.ValidationError("A user with this username already exists.")

        return username

    def validate_first_name(self, first_name):
        first_name = first_name.strip()

        if not first_name:
            raise serializers.ValidationError("First name is required")

        return first_name

    def validate_last_name(self, last_name):
        last_name = last_name.strip()

        if not last_name:
            raise serializers.ValidationError("Last name is required.")

        return last_name

    def validate_password(self, password):
        validate_password(password)

        return password

    def create(self, validated_data):
        invitation = self.context["invitation"]

        return User.objects.create_user(
            username=validated_data["username"],
            email=invitation.email,
            first_name=validated_data["first_name"],
            last_name=validated_data["last_name"],
            password=validated_data["password"],
        )

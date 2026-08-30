import hashlib

from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.core.exceptions import ValidationError as DjangoValidationError
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


class ProfileSerializer(serializers.ModelSerializer):
    username = serializers.CharField(
        max_length=150,
        validators=[UnicodeUsernameValidator()],
    )

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "first_name",
            "last_name",
            "email",
        ]
        read_only_fields = ["id"]

    def validate_username(self, username):
        username = username.strip()

        if not username:
            raise serializers.ValidationError("Username is required.")

        queryset = User.objects.filter(username__iexact=username)

        if self.instance is not None:
            queryset = queryset.exclude(
                pk=self.instance.pk,
            )

        if queryset.exists():
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

    def validate_email(self, email):
        email = email.strip().lower()

        if not email:
            raise serializers.ValidationError("Email address is required.")

        queryset = User.objects.filter(
            email__iexact=email,
        )

        if self.instance is not None:
            queryset = queryset.exclude(
                pk=self.instance.pk,
            )
        if queryset.exists():
            raise serializers.ValidationError("A user with this email address already exists.")

        return email


class PasswordChangeSerializer(serializers.Serializer):
    current_password = serializers.CharField(
        write_only=True,
        trim_whitespace=False,
    )

    new_password = serializers.CharField(
        write_only=True,
        trim_whitespace=False,
    )

    confirm_password = serializers.CharField(
        write_only=True,
        trim_whitespace=False,
    )

    def validate_current_password(self, current_password):
        user = self.context["user"]

        if not user.check_password(current_password):
            raise serializers.ValidationError("Current password is incorrect.")

        return current_password

    def validate(self, attrs):
        new_password = attrs["new_password"]
        confirm_password = attrs["confirm_password"]
        user = self.context["user"]

        if new_password != confirm_password:
            raise serializers.ValidationError(
                {"confirm_password": ("Password confirmation does not match.")}
            )

        if user.check_password(new_password):
            raise serializers.ValidationError(
                {"new_password": ("New password must be different from the current password.")}
            )

        try:
            validate_password(
                new_password,
                user=user,
            )
        except DjangoValidationError as error:
            raise serializers.ValidationError({"new_password": error.messages}) from error

        return attrs

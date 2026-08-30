from typing import cast

from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.middleware.csrf import get_token
from rest_framework import generics, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.accounts.models import User
from apps.accounts.serializers import (
    InvitationRegistrationSerializer,
    LoginSerializer,
    PasswordChangeSerializer,
    ProfileSerializer,
)

from .permissions import IsStewardUser
from .policies import can_access_steward


class CsrfTokenView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        return Response({"csrfToken": get_token(request)})


class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        validated_data = cast(
            dict[str, str],
            serializer.validated_data,
        )

        authenticated_user = authenticate(
            request=request,
            username=validated_data["username"],
            password=validated_data["password"],
        )

        if authenticated_user is None:
            return Response(
                {"detail": "Invalid username or password."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user = cast(User, authenticated_user)

        if not can_access_steward(user):
            return Response(
                {"detail": "This account cannot sign in to Steward."},
                status=status.HTTP_403_FORBIDDEN,
            )

        login(request, user)

        return Response(
            {
                "id": user.pk,
                "username": user.username,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "email": user.email,
            },
            status=status.HTTP_200_OK,
        )


class InvitationRegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        if request.user.is_authenticated:
            return Response(
                {"detail": "You are already signed in."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = InvitationRegistrationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = cast(User, serializer.save())

        if not can_access_steward(user):
            return Response(
                {
                    "detail": ("This account cannon sign in to Steward."),
                },
                status=status.HTTP_403_FORBIDDEN,
            )

        login(request, user)

        return Response(
            {
                "id": user.pk,
                "username": user.username,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "email": user.email,
            },
            status=status.HTTP_201_CREATED,
        )


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        logout(request)

        return Response(status=status.HTTP_204_NO_CONTENT)


class CurrentUserView(APIView):
    permission_classes = [IsStewardUser]

    def get(self, request):
        user = request.user

        return Response(
            {
                "id": user.id,
                "username": user.username,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "email": user.email,
            }
        )


class ProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = ProfileSerializer
    permission_classes = [IsStewardUser]

    def get_object(self):  # pyright: ignore[reportIncompatibleMethodOverride]
        return self.request.user


class PasswordChangeView(APIView):
    permission_classes = [IsStewardUser]

    def post(self, request):
        serializer = PasswordChangeSerializer(
            data=request.data,
            context={
                "user": request.user,
            },
        )
        serializer.is_valid(raise_exception=True)

        validated_data = cast(
            dict[str, object],
            serializer.validated_data,
        )

        new_password = cast(
            str,
            validated_data["new_password"],
        )

        user = request.user
        user.set_password(new_password)
        user.save(
            update_fields=[
                "password",
                "updated_at",
            ]
        )

        update_session_auth_hash(
            request,
            user,
        )

        return Response(
            {
                "detail": "Password changed successfully.",
            }
        )

from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from .serializers import (
    ChangePasswordSerializer,
    LoginSerializer,
    RegisterSerializer,
    UpdateProfileSerializer,
    UserSerializer,
)


class AuthViewSet(viewsets.GenericViewSet):
    """
    ViewSet pour l'authentification (register, login, logout)
    """

    serializer_class = UserSerializer

    def get_permissions(self):
        if self.action in ["register", "login"]:
            return [AllowAny()]
        return [IsAuthenticated()]

    @action(detail=False, methods=["post"], url_path="register")
    def register(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response(
                {
                    "user": UserSerializer(user).data,
                    "message": "Compte créé avec succès",
                },
                status=status.HTTP_201_CREATED,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=["post"], url_path="login")
    def login(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = authenticate(
                username=serializer.validated_data["username"],
                password=serializer.validated_data["password"],
            )
            if user:
                refresh = RefreshToken.for_user(user)
                return Response(
                    {
                        "user": UserSerializer(user).data,
                        "access": str(refresh.access_token),
                        "refresh": str(refresh),
                    }
                )
            return Response(
                {"error": "Identifiants invalides"}, status=status.HTTP_401_UNAUTHORIZED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=["post"], url_path="logout")
    def logout(self, request):
        try:
            refresh_token = request.data.get("refresh")
            if not refresh_token:
                return Response(
                    {"error": "Refresh token requis"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response(
                {"message": "Déconnexion réussie"}, status=status.HTTP_200_OK
            )
        except Exception:
            return Response(
                {"error": "Token invalide"}, status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=False, methods=["get"], url_path="me")
    def me(self, request):
        return Response(UserSerializer(request.user).data)


class UserViewSet(viewsets.ModelViewSet):
    """
    ViewSet pour la gestion des utilisateurs (CRUD)
    """

    queryset = User.objects.select_related("role").all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        if self.action in ["list", "retrieve"]:
            return [IsAuthenticated()]
        elif self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAdminUser()]
        return [IsAuthenticated()]

    @action(detail=False, methods=["post"], url_path="change-password")
    def change_password(self, request):
        serializer = ChangePasswordSerializer(data=request.data)
        if serializer.is_valid():
            user = request.user

            # Vérifier l'ancien mot de passe
            if not user.check_password(serializer.validated_data["old_password"]):
                return Response(
                    {"error": "Ancien mot de passe incorrect"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Changer le mot de passe
            user.set_password(serializer.validated_data["new_password"])
            user.save()

            return Response({"message": "Mot de passe modifié avec succès"})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=["patch"], url_path="change-role")
    def change_role(self, request, pk=None):
        user = self.get_object()
        new_role = request.data.get("role")

        if not new_role:
            return Response(
                {"error": "Role requis"}, status=status.HTTP_400_BAD_REQUEST
            )

        # Vérifier que le role est valide
        valid_roles = [choice[0] for choice in UserRole.ROLE_CHOICES]
        if new_role not in valid_roles:
            return Response(
                {"error": "Role invalide"}, status=status.HTTP_400_BAD_REQUEST
            )

        # Mettre à jour le role
        user_role, created = UserRole.objects.get_or_create(user=user)
        user_role.role = new_role
        user_role.save()

        return Response(
            {"message": f"Role changé en {new_role}", "user": UserSerializer(user).data}
        )

    @action(detail=False, methods=["patch"], url_path="update-profile")
    def update_profile(self, request):
        serializer = UpdateProfileSerializer(
            request.user, data=request.data, partial=True, context={"request": request}
        )

        if serializer.is_valid():
            serializer.save()
            return Response(
                {
                    "message": "Profil mis a jour",
                    "user": UserSerializer(request.data).data,
                }
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

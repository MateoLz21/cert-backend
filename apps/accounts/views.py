"""API views for authentication and user management.

JWT obtain/refresh come from SimpleJWT; logout blacklists the refresh token.
Password reset endpoints are scaffolded for the frontend to consume.
"""
from django.contrib.auth import get_user_model
from drf_spectacular.utils import OpenApiResponse, extend_schema, inline_serializer
from rest_framework import permissions, serializers, status, viewsets
from rest_framework.generics import CreateAPIView
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from .permissions import IsAdmin, IsSuperAdmin
from .serializers import AdminUserSerializer, RegisterSerializer, UserSerializer
from .services import AccountService

User = get_user_model()


class RegisterView(CreateAPIView):
    """Public endpoint for client self-registration."""

    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = AccountService.register_client(**serializer.validated_data)
        return Response(UserSerializer(user).data, status=status.HTTP_201_CREATED)


class LogoutView(APIView):
    """Blacklist the provided refresh token to log the user out."""

    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(
        request=inline_serializer(
            name="LogoutRequest",
            fields={"refresh": serializers.CharField()},
        ),
        responses={205: OpenApiResponse(description="Sesión cerrada.")},
    )
    def post(self, request):
        refresh = request.data.get("refresh")
        if not refresh:
            return Response(
                {"detail": "Se requiere el token refresh."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            RefreshToken(refresh).blacklist()
        except Exception:
            return Response(
                {"detail": "Token inválido."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return Response(status=status.HTTP_205_RESET_CONTENT)


class MeView(APIView):
    """Return the currently authenticated user."""

    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(responses=UserSerializer)
    def get(self, request):
        return Response(UserSerializer(request.user).data)


class UserViewSet(viewsets.ModelViewSet):
    """Gestión de usuarios.

    Lectura para administradores; creación/edición/borrado solo para super
    administradores (incluye la asignación de rol).
    """

    queryset = User.objects.select_related("profile").all()
    serializer_class = AdminUserSerializer

    filterset_fields = ["role", "is_active"]
    search_fields = ["email", "first_name", "last_name"]
    ordering_fields = ["date_joined", "email"]
    ordering = ["-date_joined"]

    def get_permissions(self):
        if self.action in ["list", "retrieve"]:
            return [IsAdmin()]
        return [IsSuperAdmin()]

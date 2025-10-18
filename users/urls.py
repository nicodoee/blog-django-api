from django.urls import include, path
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView

from .views import AuthViewSet, UserViewSet

router = DefaultRouter()
router.register(r"auth", AuthViewSet, basename="auth")
router.register(r"users", UserViewSet, basename="users")

urlpatterns = [
    path("", include(router.urls)),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
]

"""
    POST   /api/auth/register/           # S'inscrire
    POST   /api/auth/login/              # Se connecter
    POST   /api/auth/logout/             # Se déconnecter
    GET    /api/auth/me/                 # Profil de l'utilisateur connecté
    POST   /api/token/refresh/           # Rafraîchir le token
"""

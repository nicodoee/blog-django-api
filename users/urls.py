from django.urls import path
from .views import register, login, logout, me
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    path('register/', register, name='register'),
    path('login/', login, name='login'),
    path('logout/', logout, name='logout'),
    path('me/', me, name='me'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]

from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from .session_views import session_login, session_register, standard_logout
from .views import CustomTokenObtainPairView, LogoutView, RegisterView

app_name = "auth_service"

urlpatterns = [
    # Browser session authentication (HTML templates)
    path("login/", session_login, name="login"),
    path("logout/", standard_logout, name="logout"),
    path("register/", session_register, name="register"),
    # JWT API (programmatic clients)
    path("api/login/", CustomTokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/register/", RegisterView.as_view({"post": "create"}), name="api_register"),
    path("api/logout/", LogoutView.as_view({"post": "create"}), name="api_logout"),
    path("refresh/", TokenRefreshView.as_view(), name="token_refresh"),
]

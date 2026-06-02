from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView, TokenObtainPairView
from .views import CustomTokenObtainPairView, LogoutView, RegisterView

urlpatterns = [
    # Authentication
    path('login/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # Registration and logout
    path('register/', RegisterView.as_view({'post': 'create'}), name='register'),
    path('logout/', LogoutView.as_view({'post': 'create'}), name='logout'),
]

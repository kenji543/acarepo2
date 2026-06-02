from rest_framework import status, viewsets
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.models import User
from portfolio.models import ResearcherProfile
from .serializers import (
    RegisterSerializer, CustomTokenObtainPairSerializer,
    TokenRefreshSerializer, LogoutSerializer
)
from .models import TokenBlacklist, AuditLog
from django.utils import timezone
import logging

logger = logging.getLogger('django.security')


class RegisterView(viewsets.ViewSet):
    """API endpoint for user registration."""
    permission_classes = [AllowAny]
    
    def create(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            
            # Create researcher profile
            ResearcherProfile.objects.create(user=user)
            
            # Log registration
            ip = request.META.get('HTTP_X_FORWARDED_FOR', request.META.get('REMOTE_ADDR'))
            AuditLog.objects.create(
                user=user,
                event_type='registration',
                description=f'New user registration: {user.username}',
                ip_address=ip,
                user_agent=request.META.get('HTTP_USER_AGENT', '')
            )
            
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def options(self, request, *args, **kwargs):
        """Handle CORS preflight OPTIONS requests."""
        return Response(status=status.HTTP_200_OK)


class CustomTokenObtainPairView(TokenObtainPairView):
    """Custom JWT token obtain view with audit logging."""
    serializer_class = CustomTokenObtainPairSerializer
    
    def post(self, request, *args, **kwargs):
        # Log login attempt
        username = request.data.get('username', 'unknown')
        ip = request.META.get('HTTP_X_FORWARDED_FOR', request.META.get('REMOTE_ADDR'))
        
        response = super().post(request, *args, **kwargs)
        
        if response.status_code == 200:
            # Successful login
            try:
                user = User.objects.get(username=username)
                AuditLog.objects.create(
                    user=user,
                    event_type='login',
                    description=f'Successful login from {ip}',
                    ip_address=ip,
                    user_agent=request.META.get('HTTP_USER_AGENT', '')
                )
                logger.info(f"User {username} logged in successfully from {ip}")
            except User.DoesNotExist:
                logger.warning(f"Login attempt for non-existent user: {username}")
        else:
            # Failed login
            AuditLog.objects.create(
                user=None,
                event_type='failed_login',
                description=f'Failed login attempt for {username}',
                ip_address=ip,
                user_agent=request.META.get('HTTP_USER_AGENT', '')
            )
            logger.warning(f"Failed login attempt for user {username} from {ip}")
        
        return response


class LogoutView(viewsets.ViewSet):
    """API endpoint for logout with token blacklisting."""
    permission_classes = [IsAuthenticated]
    
    def create(self, request):
        serializer = LogoutSerializer(data=request.data)
        
        if serializer.is_valid():
            try:
                refresh_token = serializer.validated_data['refresh']
                token = RefreshToken(refresh_token)
                
                # Blacklist the token
                from rest_framework_simplejwt.tokens import Token
                blacklist_token = TokenBlacklist(
                    user=request.user,
                    token=str(token),
                    expires_at=timezone.now() + timezone.timedelta(days=7)
                )
                blacklist_token.save()
                
                # Log logout
                ip = request.META.get('HTTP_X_FORWARDED_FOR', request.META.get('REMOTE_ADDR'))
                AuditLog.objects.create(
                    user=request.user,
                    event_type='logout',
                    description=f'User logged out',
                    ip_address=ip,
                    user_agent=request.META.get('HTTP_USER_AGENT', '')
                )
                
                return Response({'detail': 'Successfully logged out.'}, status=status.HTTP_205_RESET_CONTENT)
            except Exception as e:
                return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
def token_obtain_pair(request):
    """Obtain JWT token pair."""
    view = CustomTokenObtainPairView.as_view()
    return view(request)


@api_view(['POST'])
@permission_classes([AllowAny])
def token_refresh(request):
    """Refresh JWT access token."""
    view = TokenRefreshView.as_view()
    return view(request)

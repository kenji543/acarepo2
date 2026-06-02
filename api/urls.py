from rest_framework.routers import DefaultRouter
from django.urls import path, include
from .views import (
    ResearcherProfileViewSet, ResearchPaperViewSet,
    DatasetViewSet, AccessPermissionViewSet,
    FileAccessLogViewSet
)

router = DefaultRouter()
router.register(r'researchers', ResearcherProfileViewSet, basename='researcher')
router.register(r'papers', ResearchPaperViewSet, basename='paper')
router.register(r'datasets', DatasetViewSet, basename='dataset')
router.register(r'permissions', AccessPermissionViewSet, basename='permission')
router.register(r'audit-logs', FileAccessLogViewSet, basename='audit-log')

app_name = 'api'

urlpatterns = [
    path('', include(router.urls)),
    path('auth/', include('rest_framework.urls')),
]

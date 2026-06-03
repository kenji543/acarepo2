from django.urls import path
from . import views

urlpatterns = [
    path('', views.PortfolioListView.as_view(), name='portfolio_list'),
    path('dashboard/', views.researcher_dashboard, name='dashboard'),
    path('list/', views.PortfolioListView.as_view(), name='portfolio_list'),
    path('paper/<uuid:pk>/', views.PaperDetailView.as_view(), name='paper_detail'),
    path('paper/<uuid:paper_id>/download/', views.download_paper, name='download_paper'),
    path('paper/<uuid:paper_id>/edit/', views.edit_paper, name='edit_paper'),
    path('paper/<uuid:paper_id>/citations/', views.get_paper_citations, name='get_paper_citations'),
    path('paper/create/', views.create_paper, name='create_paper'),
]

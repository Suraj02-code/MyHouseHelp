from django.urls import path
from . import views

app_name = 'ml_engine'

urlpatterns = [
    # Recommendation API endpoints
    path('api/recommendations/', views.RecommendationAPIView.as_view(), name='recommendations_api'),
    path('api/service-recommendations/', views.ServiceRecommendationAPIView.as_view(), name='service_recommendations_api'),
    
    # Recommendation dashboard
    path('dashboard/', views.recommendation_dashboard, name='recommendation_dashboard'),
]

from django.urls import path
from . import views

app_name = 'services'

urlpatterns = [
    # Public service views
    path('', views.service_list, name='list'),
    path('<int:service_id>/', views.service_detail, name='detail'),
    path('category/<str:category_name>/', views.category_services, name='category'),
    path('recommendations/', views.recommendations_view, name='recommendations'),
    
    # Provider service management
    path('my-services/', views.my_services, name='my_services'),
    path('create/', views.create_service, name='create'),
    path('<int:service_id>/edit/', views.edit_service, name='edit'),
    path('<int:service_id>/delete/', views.delete_service, name='delete'),
    
    # Availability management
    path('availability/', views.service_availability, name='availability'),
    
    # API endpoints
    path('api/search/', views.search_api, name='search_api'),
]

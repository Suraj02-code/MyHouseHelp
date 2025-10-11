from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    # Authentication URLs
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    
    # Profile URLs
    path('profile/', views.profile, name='profile'),
    
    # Dashboard URLs
    path('dashboard/customer/', views.customer_dashboard, name='customer_dashboard'),
    path('dashboard/provider/', views.provider_dashboard, name='provider_dashboard'),
]
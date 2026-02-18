from django.urls import path
from . import views

app_name = 'chatbot'

urlpatterns = [
    path('send-message/', views.send_message, name='send_message'),
    path('quick-response/', views.get_quick_response, name='quick_response'),
    path('rate-response/', views.rate_response, name='rate_response'),
    path('suggestions/', views.get_suggestions, name='get_suggestions'),
    path('analytics/', views.chatbot_analytics, name='analytics'),
    path('history/', views.chat_history, name='chat_history'),
    path('session/<str:session_id>/', views.chat_session_detail, name='session_detail'),
]

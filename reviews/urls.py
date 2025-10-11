from django.urls import path
from django.http import HttpResponse

app_name = 'reviews'

# Placeholder views
def placeholder_view(request, *args, **kwargs):
    return HttpResponse("This feature is coming soon! 🚧")

urlpatterns = [
    path('write/<int:booking_id>/', placeholder_view, name='write'),
    path('<int:review_id>/', placeholder_view, name='detail'),
]
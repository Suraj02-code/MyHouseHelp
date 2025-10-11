from django.urls import path
from django.http import HttpResponse

app_name = 'bookings'

# Placeholder views
def placeholder_view(request, *args, **kwargs):
    return HttpResponse("This feature is coming soon! 🚧")

urlpatterns = [
    path('my-bookings/', placeholder_view, name='my_bookings'),
    path('provider-bookings/', placeholder_view, name='provider_bookings'),
    path('<int:booking_id>/', placeholder_view, name='detail'),
    path('book/<int:service_id>/', placeholder_view, name='book'),
]
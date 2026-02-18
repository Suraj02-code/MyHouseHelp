from django.urls import path
from . import views

app_name = 'bookings'

# Placeholder views
def placeholder_view(request, *args, **kwargs):
    return HttpResponse("This feature is coming soon! ")

urlpatterns = [
    path('my-bookings/', views.my_bookings, name='my_bookings'),
    path('booking/<int:booking_id>/', views.booking_detail, name='detail'),
    path('cancel/<int:booking_id>/', views.cancel_booking, name='cancel'),
    path('reschedule/<int:booking_id>/', views.reschedule_booking, name='reschedule'),
    # Legacy URLs for compatibility
    path('provider-bookings/', views.my_bookings, name='provider_bookings'),
    path('<int:booking_id>/', views.booking_detail, name='detail'),
    path('book/<int:service_id>/', views.my_bookings, name='book'),
]
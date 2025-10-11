from django.urls import path
from django.http import HttpResponse

app_name = 'payments'

# Placeholder views
def placeholder_view(request, *args, **kwargs):
    return HttpResponse("This feature is coming soon! 🚧")

urlpatterns = [
    path('process/<int:booking_id>/', placeholder_view, name='process'),
    path('success/', placeholder_view, name='success'),
    path('cancel/', placeholder_view, name='cancel'),
]
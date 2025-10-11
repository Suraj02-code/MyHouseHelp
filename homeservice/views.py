from django.shortcuts import render
from django.http import HttpResponse

def home(request):
    """Home page view"""
    return render(request, 'home.html')

def api_health(request):
    """Simple health check endpoint"""
    return HttpResponse("Home Service App is running!")
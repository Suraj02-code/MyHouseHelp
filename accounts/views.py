from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.core.paginator import Paginator
from django.db.models import Count, Avg, Q, Sum
from django.db import models

from .models import User, CustomerProfile, ServiceProviderProfile
from .forms import (
    UserRegistrationForm, UserLoginForm, ProfileUpdateForm,
    CustomerProfileForm, ProviderProfileForm
)
from bookings.models import Booking
from services.models import Service
from reviews.models import Review


def register(request):
    """User registration view"""
    if request.user.is_authenticated:
        return redirect('home')
    
    role = request.GET.get('role', 'customer')
    
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            try:
                with transaction.atomic():
                    user = form.save()
                    login(request, user)
                    messages.success(request, f'Welcome! Your {user.get_role_display().lower()} account has been created.')
                    
                    # Redirect based on role
                    if user.role == 'customer':
                        return redirect('accounts:customer_dashboard')
                    elif user.role == 'provider':
                        return redirect('accounts:provider_dashboard')
                    else:
                        return redirect('home')
            except Exception as e:
                messages.error(request, 'An error occurred during registration. Please try again.')
    else:
        form = UserRegistrationForm(initial={'role': role})
    
    return render(request, 'accounts/register.html', {
        'form': form,
        'role': role
    })


def login_view(request):
    """User login view"""
    if request.user.is_authenticated:
        return redirect('home')
    
    if request.method == 'POST':
        form = UserLoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            
            if user is not None:
                login(request, user)
                messages.success(request, f'Welcome back, {user.first_name or user.username}!')
                
                # Redirect to intended page or dashboard
                next_url = request.GET.get('next')
                if next_url:
                    return redirect(next_url)
                
                # Redirect based on role
                if user.role == 'customer':
                    return redirect('accounts:customer_dashboard')
                elif user.role == 'provider':
                    return redirect('accounts:provider_dashboard')
                elif user.role == 'admin':
                    return redirect('/admin/')
                else:
                    return redirect('home')
            else:
                messages.error(request, 'Invalid username or password.')
    else:
        form = UserLoginForm()
    
    return render(request, 'accounts/login.html', {'form': form})


@login_required
def logout_view(request):
    """User logout view"""
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('home')


@login_required
def profile(request):
    """User profile view"""
    if request.method == 'POST':
        user_form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user)
        
        profile_form = None
        if request.user.role == 'customer':
            profile_form = CustomerProfileForm(
                request.POST, 
                instance=getattr(request.user, 'customer_profile', None)
            )
        elif request.user.role == 'provider':
            profile_form = ProviderProfileForm(
                request.POST, 
                request.FILES,
                instance=getattr(request.user, 'provider_profile', None)
            )
        
        if user_form.is_valid() and (profile_form is None or profile_form.is_valid()):
            user_form.save()
            
            if profile_form:
                profile = profile_form.save(commit=False)
                profile.user = request.user
                profile.save()
            
            messages.success(request, 'Profile updated successfully!')
            return redirect('accounts:profile')
    else:
        user_form = ProfileUpdateForm(instance=request.user)
        
        profile_form = None
        if request.user.role == 'customer':
            profile_form = CustomerProfileForm(
                instance=getattr(request.user, 'customer_profile', None)
            )
        elif request.user.role == 'provider':
            profile_form = ProviderProfileForm(
                instance=getattr(request.user, 'provider_profile', None)
            )
    
    return render(request, 'accounts/profile.html', {
        'user_form': user_form,
        'profile_form': profile_form
    })


@login_required
def customer_dashboard(request):
    """Customer dashboard view"""
    if request.user.role != 'customer':
        messages.error(request, 'Access denied. Customer account required.')
        return redirect('home')
    
    # Get or create customer profile
    customer_profile, created = CustomerProfile.objects.get_or_create(
        user=request.user
    )
    
    # Get customer statistics
    total_bookings = Booking.objects.filter(customer=request.user).count()
    completed_bookings = Booking.objects.filter(
        customer=request.user, 
        status='completed'
    ).count()
    pending_bookings = Booking.objects.filter(
        customer=request.user, 
        status__in=['pending', 'confirmed']
    ).count()
    
    # Recent bookings
    recent_bookings = Booking.objects.filter(
        customer=request.user
    ).order_by('-created_at')[:5]
    
    # Reviews given
    reviews_given = Review.objects.filter(
        customer=request.user
    ).count()
    
    return render(request, 'accounts/customer_dashboard.html', {
        'customer_profile': customer_profile,
        'total_bookings': total_bookings,
        'completed_bookings': completed_bookings,
        'pending_bookings': pending_bookings,
        'recent_bookings': recent_bookings,
        'reviews_given': reviews_given,
    })


@login_required
def provider_dashboard(request):
    """Service provider dashboard view"""
    if request.user.role != 'provider':
        messages.error(request, 'Access denied. Service provider account required.')
        return redirect('home')
    
    # Get or create provider profile
    provider_profile, created = ServiceProviderProfile.objects.get_or_create(
        user=request.user
    )
    
    # Get provider statistics
    services_offered = Service.objects.filter(provider=request.user).count()
    total_bookings = Booking.objects.filter(provider=request.user).count()
    completed_jobs = Booking.objects.filter(
        provider=request.user, 
        status='completed'
    ).count()
    pending_bookings = Booking.objects.filter(
        provider=request.user, 
        status__in=['pending', 'confirmed']
    ).count()
    
    # Recent bookings
    recent_bookings = Booking.objects.filter(
        provider=request.user
    ).order_by('-created_at')[:5]
    
    # Reviews received
    reviews = Review.objects.filter(provider=request.user)
    total_reviews = reviews.count()
    avg_rating = reviews.aggregate(Avg('overall_rating'))['overall_rating__avg'] or 0
    
    # Earnings (mock calculation)
    total_earnings = Booking.objects.filter(
        provider=request.user, 
        status='completed'
    ).aggregate(total=models.Sum('final_price'))['total'] or 0
    
    return render(request, 'accounts/provider_dashboard.html', {
        'provider_profile': provider_profile,
        'services_offered': services_offered,
        'total_bookings': total_bookings,
        'completed_jobs': completed_jobs,
        'pending_bookings': pending_bookings,
        'recent_bookings': recent_bookings,
        'total_reviews': total_reviews,
        'avg_rating': round(avg_rating, 1),
        'total_earnings': total_earnings,
    })

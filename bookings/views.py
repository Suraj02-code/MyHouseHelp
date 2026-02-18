from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods

from .models import Booking
from services.models import Service
from reviews.models import Review


@login_required
def my_bookings(request):
    """Display all bookings for the logged-in customer"""
    if request.user.role != 'customer':
        messages.error(request, 'Access denied. Customer account required.')
        return redirect('home')
    
    # Get filter parameters
    status_filter = request.GET.get('status', '')
    search_query = request.GET.get('search', '')
    
    # Base queryset
    bookings = Booking.objects.filter(customer=request.user).select_related(
        'provider', 'service', 'service__category'
    ).order_by('-created_at')
    
    # Apply status filter
    if status_filter:
        bookings = bookings.filter(status=status_filter)
    
    # Apply search filter
    if search_query:
        bookings = bookings.filter(
            Q(service__title__icontains=search_query) |
            Q(provider__username__icontains=search_query) |
            Q(service__category__name__icontains=search_query)
        )
    
    # Pagination
    paginator = Paginator(bookings, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Calculate statistics
    total_bookings = bookings.count()
    completed_bookings = bookings.filter(status='completed').count()
    pending_bookings = bookings.filter(status__in=['pending', 'confirmed']).count()
    cancelled_bookings = bookings.filter(status='cancelled').count()
    
    # Get available statuses for filter dropdown
    status_choices = Booking.STATUS_CHOICES
    
    context = {
        'bookings': page_obj,
        'page_obj': page_obj,
        'status_filter': status_filter,
        'search_query': search_query,
        'total_bookings': total_bookings,
        'completed_bookings': completed_bookings,
        'pending_bookings': pending_bookings,
        'cancelled_bookings': cancelled_bookings,
        'status_choices': status_choices,
    }
    
    return render(request, 'bookings/my_bookings.html', context)


@login_required
def booking_detail(request, booking_id):
    """Display detailed information about a specific booking"""
    if request.user.role != 'customer':
        messages.error(request, 'Access denied. Customer account required.')
        return redirect('home')
    
    booking = get_object_or_404(
        Booking.objects.select_related('provider', 'service', 'service__category'),
        id=booking_id
    )
    
    # Check if booking belongs to current user
    if booking.customer != request.user:
        messages.error(request, 'Access denied. This booking does not belong to you.')
        return redirect('bookings:my_bookings')
    
    # Check if user can review this booking
    can_review = (
        booking.status == 'completed' and 
        not Review.objects.filter(booking=booking, customer=request.user).exists()
    )
    
    context = {
        'booking': booking,
        'can_review': can_review,
    }
    
    return render(request, 'bookings/booking_detail.html', context)


@login_required
@require_http_methods(["POST"])
def cancel_booking(request, booking_id):
    """Cancel a booking"""
    if request.user.role != 'customer':
        messages.error(request, 'Access denied. Customer account required.')
        return redirect('home')
    
    booking = get_object_or_404(Booking, id=booking_id)
    
    # Check if booking belongs to current user
    if booking.customer != request.user:
        messages.error(request, 'Access denied. This booking does not belong to you.')
        return redirect('bookings:my_bookings')
    
    # Check if booking can be cancelled
    if booking.status not in ['pending', 'confirmed']:
        messages.error(request, 'This booking cannot be cancelled.')
        return redirect('bookings:detail', booking_id=booking_id)
    
    # Cancel the booking
    booking.status = 'cancelled'
    booking.save()
    
    messages.success(request, 'Booking cancelled successfully.')
    return redirect('bookings:my_bookings')


@login_required
@require_http_methods(["POST"])
def reschedule_booking(request, booking_id):
    """Request rescheduling for a booking"""
    if request.user.role != 'customer':
        messages.error(request, 'Access denied. Customer account required.')
        return redirect('home')
    
    booking = get_object_or_404(Booking, id=booking_id)
    
    # Check if booking belongs to current user
    if booking.customer != request.user:
        messages.error(request, 'Access denied. This booking does not belong to you.')
        return redirect('bookings:my_bookings')
    
    # Check if booking can be rescheduled
    if booking.status not in ['pending', 'confirmed']:
        messages.error(request, 'This booking cannot be rescheduled.')
        return redirect('bookings:detail', booking_id=booking_id)
    
    # Get new date and time from form
    new_date = request.POST.get('new_date')
    new_time = request.POST.get('new_time')
    
    if not new_date or not new_time:
        messages.error(request, 'Please provide both new date and time.')
        return redirect('bookings:detail', booking_id=booking_id)
    
    # Update booking (in real app, this would send notification to provider)
    booking.booking_date = new_date
    booking.booking_time = new_time
    booking.status = 'pending'  # Reset to pending for provider confirmation
    booking.save()
    
    messages.success(request, 'Rescheduling request sent to provider.')
    return redirect('bookings:detail', booking_id=booking_id)

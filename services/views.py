from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Avg, Count
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods

from .models import Service, ServiceCategory, ServiceAvailability, ServiceArea
from .forms import ServiceForm, ServiceAvailabilityForm
from reviews.models import Review
from bookings.models import Booking


def service_list(request):
    """Service listing with search and filtering"""
    services = Service.objects.filter(is_active=True).select_related(
        'provider', 'category'
    ).prefetch_related('bookings', 'provider__reviews_received')
    
    # Search functionality
    search_query = request.GET.get('search', '')
    if search_query:
        services = services.filter(
            Q(title__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(category__name__icontains=search_query)
        )
    
    # Category filtering
    category = request.GET.get('category')
    if category:
        services = services.filter(category__name__icontains=category)
    
    # Price range filtering
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    if min_price:
        try:
            services = services.filter(base_price__gte=float(min_price))
        except ValueError:
            pass
    if max_price:
        try:
            services = services.filter(base_price__lte=float(max_price))
        except ValueError:
            pass
    
    # Sorting
    sort_by = request.GET.get('sort', 'created_at')
    if sort_by == 'price_low':
        services = services.order_by('base_price')
    elif sort_by == 'price_high':
        services = services.order_by('-base_price')
    elif sort_by == 'rating':
        services = services.annotate(
            avg_rating=Avg('provider__reviews_received__overall_rating')
        ).order_by('-avg_rating')
    elif sort_by == 'popular':
        services = services.annotate(
            booking_count=Count('bookings')
        ).order_by('-booking_count')
    else:
        services = services.order_by('-created_at')
    
    # Pagination
    paginator = Paginator(services, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Get categories for filter dropdown
    categories = ServiceCategory.objects.filter(is_active=True)
    
    context = {
        'page_obj': page_obj,
        'categories': categories,
        'search_query': search_query,
        'selected_category': category,
        'min_price': min_price,
        'max_price': max_price,
        'sort_by': sort_by,
    }
    
    return render(request, 'services/service_list.html', context)


def service_detail(request, service_id):
    """Service detail view"""
    service = get_object_or_404(
        Service.objects.select_related('provider', 'category'),
        id=service_id,
        is_active=True
    )
    
    # Get provider reviews
    reviews = Review.objects.filter(
        provider=service.provider
    ).select_related('customer', 'booking').order_by('-created_at')[:10]
    
    # Calculate average rating
    avg_rating = reviews.aggregate(Avg('overall_rating'))['overall_rating__avg'] or 0
    total_reviews = reviews.count()
    
    # Get provider's other services
    other_services = Service.objects.filter(
        provider=service.provider,
        is_active=True
    ).exclude(id=service.id)[:4]
    
    # Get availability (if provider has set it)
    availability = ServiceAvailability.objects.filter(
        provider=service.provider,
        is_available=True
    ).order_by('day_of_week', 'start_time')
    
    context = {
        'service': service,
        'reviews': reviews,
        'avg_rating': round(avg_rating, 1),
        'total_reviews': total_reviews,
        'other_services': other_services,
        'availability': availability,
    }
    
    return render(request, 'services/service_detail.html', context)


def category_services(request, category_name):
    """Services by category"""
    category = get_object_or_404(ServiceCategory, name__iexact=category_name)
    
    services = Service.objects.filter(
        category=category,
        is_active=True
    ).select_related('provider', 'category')
    
    # Pagination
    paginator = Paginator(services, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'category': category,
        'page_obj': page_obj,
    }
    
    return render(request, 'services/category_services.html', context)


@login_required
def my_services(request):
    """Provider's service management"""
    if request.user.role != 'provider':
        messages.error(request, 'Access denied. Service provider account required.')
        return redirect('home')
    
    services = Service.objects.filter(
        provider=request.user
    ).order_by('-created_at')
    
    context = {
        'services': services,
    }
    
    return render(request, 'services/my_services.html', context)


@login_required
def create_service(request):
    """Create new service"""
    if request.user.role != 'provider':
        messages.error(request, 'Access denied. Service provider account required.')
        return redirect('home')
    
    if request.method == 'POST':
        form = ServiceForm(request.POST, request.FILES)
        if form.is_valid():
            service = form.save(commit=False)
            service.provider = request.user
            service.save()
            messages.success(request, 'Service created successfully!')
            return redirect('services:my_services')
    else:
        form = ServiceForm()
    
    context = {
        'form': form,
        'title': 'Create New Service'
    }
    
    return render(request, 'services/service_form.html', context)


@login_required
def edit_service(request, service_id):
    """Edit existing service"""
    service = get_object_or_404(Service, id=service_id, provider=request.user)
    
    if request.method == 'POST':
        form = ServiceForm(request.POST, request.FILES, instance=service)
        if form.is_valid():
            form.save()
            messages.success(request, 'Service updated successfully!')
            return redirect('services:my_services')
    else:
        form = ServiceForm(instance=service)
    
    context = {
        'form': form,
        'service': service,
        'title': 'Edit Service'
    }
    
    return render(request, 'services/service_form.html', context)


@login_required
def delete_service(request, service_id):
    """Delete service"""
    service = get_object_or_404(Service, id=service_id, provider=request.user)
    
    if request.method == 'POST':
        service.delete()
        messages.success(request, 'Service deleted successfully!')
        return redirect('services:my_services')
    
    context = {
        'service': service,
    }
    
    return render(request, 'services/service_confirm_delete.html', context)


@login_required
@require_http_methods(["GET", "POST"])
def service_availability(request):
    """Manage service availability"""
    if request.user.role != 'provider':
        messages.error(request, 'Access denied.')
        return redirect('home')
    
    availability_slots = ServiceAvailability.objects.filter(
        provider=request.user
    ).order_by('day_of_week', 'start_time')
    
    if request.method == 'POST':
        form = ServiceAvailabilityForm(request.POST)
        if form.is_valid():
            availability = form.save(commit=False)
            availability.provider = request.user
            availability.save()
            messages.success(request, 'Availability slot added!')
            return redirect('services:availability')
    else:
        form = ServiceAvailabilityForm()
    
    context = {
        'availability_slots': availability_slots,
        'form': form,
    }
    
    return render(request, 'services/availability.html', context)


@login_required
def search_api(request):
    """AJAX search endpoint"""
    query = request.GET.get('q', '')
    if len(query) < 2:
        return JsonResponse({'results': []})
    
    services = Service.objects.filter(
        Q(title__icontains=query) |
        Q(description__icontains=query) |
        Q(category__name__icontains=query),
        is_active=True
    )[:10]
    
    results = []
    for service in services:
        results.append({
            'id': service.id,
            'title': service.title,
            'category': service.category.name,
            'price': str(service.base_price),
            'provider': service.provider.get_full_name(),
            'url': f'/services/{service.id}/'
        })
    
    return JsonResponse({'results': results})

from django.contrib import admin
from .models import ServiceCategory, Service, ServiceAvailability, ServiceArea


@admin.register(ServiceCategory)
class ServiceCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_active', 'created_at')
    list_filter = ('is_active',)
    search_fields = ('name', 'description')


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ('title', 'provider', 'category', 'base_price', 'price_unit', 'is_active')
    list_filter = ('category', 'price_unit', 'is_active', 'requires_quote')
    search_fields = ('title', 'provider__username', 'category__name')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(ServiceAvailability)
class ServiceAvailabilityAdmin(admin.ModelAdmin):
    list_display = ('provider', 'get_day_of_week_display', 'start_time', 'end_time', 'is_available')
    list_filter = ('day_of_week', 'is_available')
    search_fields = ('provider__username',)


@admin.register(ServiceArea)
class ServiceAreaAdmin(admin.ModelAdmin):
    list_display = ('provider', 'area_name', 'postal_code')
    search_fields = ('provider__username', 'area_name', 'postal_code')

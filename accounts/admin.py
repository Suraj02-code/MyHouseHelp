from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, CustomerProfile, ServiceProviderProfile, AdminProfile


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ('username', 'email', 'role', 'is_verified', 'date_joined')
    list_filter = ('role', 'is_verified', 'is_active', 'is_staff')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Custom Fields', {'fields': ('role', 'phone_number', 'address', 'profile_picture', 'is_verified')}),
    )
    
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ('Custom Fields', {'fields': ('role', 'phone_number', 'address')}),
    )


@admin.register(CustomerProfile)
class CustomerProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'loyalty_points', 'total_bookings')
    search_fields = ('user__username', 'user__email')
    list_filter = ('loyalty_points',)


@admin.register(ServiceProviderProfile)
class ServiceProviderProfileAdmin(admin.ModelAdmin):
    list_display = ('business_name', 'user', 'verification_status', 'average_rating', 'completed_jobs')
    list_filter = ('verification_status', 'is_available', 'average_rating')
    search_fields = ('business_name', 'user__username', 'user__email')
    readonly_fields = ('average_rating', 'total_reviews', 'completed_jobs')


@admin.register(AdminProfile)
class AdminProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'department', 'permissions_level')
    list_filter = ('permissions_level',)
    search_fields = ('user__username', 'user__email', 'department')
